"""Lighting interfaces and Govee API adapter for Jarvis."""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

import requests

from config import (
    GOVEE_API_KEY,
    GOVEE_BASE_URL,
    GOVEE_DEVICE_ID_RICE_PAPER,
    GOVEE_DEVICE_ID_SHORT_LAMP,
    GOVEE_DEVICE_ID_TALL_LAMP,
    GOVEE_DEVICE_SKU_RICE_PAPER,
    GOVEE_DEVICE_SKU_SHORT_LAMP,
    GOVEE_DEVICE_SKU_TALL_LAMP,
    REQUEST_TIMEOUT_SEC,
)

LOGGER = logging.getLogger(__name__)

_session: requests.Session | None = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


class LightController(ABC):
    """Abstract interface for light control providers."""

    @abstractmethod
    def turn_on(self, target: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def turn_off(self, target: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_brightness(self, target: str, value: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_brightness(self, sku: str, device_id: str) -> int | None:
        raise NotImplementedError

    @abstractmethod
    def adjust_brightness(self, target: str, delta: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_color(self, target: str, r: int, g: int, b: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_color_temperature(self, target: str, kelvin: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_full_state(self, sku: str, device_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def capture_current_state(self, target: str) -> dict | None:
        raise NotImplementedError


class GoveeLightController(LightController):
    """Govee OpenAPI implementation."""

    def turn_on(self, target: str) -> bool:
        return self._apply(target, capability="powerSwitch", value=1)

    def turn_off(self, target: str) -> bool:
        return self._apply(target, capability="powerSwitch", value=0)

    def set_brightness(self, target: str, value: int) -> bool:
        brightness = max(0, min(100, value))
        return self._apply(target, capability="brightness", value=brightness)

    def set_color(self, target: str, r: int, g: int, b: int) -> bool:
        color_val = (r << 16) | (g << 8) | b
        return self._apply(target, capability="colorRgb", value=color_val)

    def set_color_temperature(self, target: str, kelvin: int) -> bool:
        # Native warm/cool white. This is a distinct Govee capability type
        # from colorRgb (both live under "color_setting"), so it needs an
        # explicit cap_type override rather than the capability-name default.
        kelvin = max(2000, min(9000, kelvin))
        return self._apply(
            target,
            capability="colorTemperatureK",
            value=kelvin,
            cap_type="devices.capabilities.color_setting",
        )

    def get_full_state(self, sku: str, device_id: str) -> dict | None:
        """Return the live brightness/color state of a single device.

        Result shape: {"brightness": int|None, "mode": "kelvin"|"rgb"|None,
        "kelvin": int|None, "rgb": (r,g,b)|None}. Fields are None when not
        present/parseable in the Govee response, rather than guessed.
        """
        state = self._query_device_state(sku, device_id)
        result: dict = {"brightness": None, "mode": None, "kelvin": None, "rgb": None}
        if state is None:
            return result
        capabilities = state.get("payload", {}).get("capabilities", [])
        for cap in capabilities:
            instance = cap.get("instance")
            value = cap.get("state", {}).get("value")
            if instance == "brightness" and isinstance(value, (int, float)):
                result["brightness"] = int(value)
            elif instance == "colorTemperatureK" and isinstance(value, (int, float)) and value:
                # Govee reports colorTemperatureK == 0 when the bulb is in
                # RGB mode rather than color-temp mode; ignore that case.
                result["kelvin"] = int(value)
                result["mode"] = "kelvin"
            elif instance == "colorRgb" and isinstance(value, (int, float)):
                rgb_int = int(value)
                result["rgb"] = ((rgb_int >> 16) & 255, (rgb_int >> 8) & 255, rgb_int & 255)
                if result["mode"] is None:
                    result["mode"] = "rgb"
        return result

    def capture_current_state(self, target: str) -> dict | None:
        """Snapshot the live state of the first device resolved for `target`.

        Used for calibration — when target is "ALL", the tall lamp (the
        primary device) is used as the reference so a single default profile
        can be replayed across all lamps later.
        """
        devices = self._resolve_targets(target)
        if not devices:
            return None
        d = devices[0]
        return self.get_full_state(d["sku"], d["device"])

    def get_brightness(self, sku: str, device_id: str) -> int | None:
        state = self._query_device_state(sku, device_id)
        if state is None:
            return None
        capabilities = state.get("payload", {}).get("capabilities", [])
        for cap in capabilities:
            if cap.get("instance") == "brightness":
                value = cap.get("state", {}).get("value")
                if isinstance(value, (int, float)):
                    return int(value)
        LOGGER.warning("Brightness not found in Govee state response. device=%s", device_id)
        return None

    def adjust_brightness(self, target: str, delta: int) -> bool:
        devices = self._resolve_targets(target)
        if not devices:
            return True
        if len(devices) == 1:
            d = devices[0]
            return self._adjust_single_brightness(d["sku"], d["device"], delta)
        with ThreadPoolExecutor(max_workers=len(devices)) as executor:
            futures = [
                executor.submit(self._adjust_single_brightness, d["sku"], d["device"], delta)
                for d in devices
            ]
            return all(f.result() for f in as_completed(futures))

    def _adjust_single_brightness(self, sku: str, device_id: str, delta: int) -> bool:
        current = self.get_brightness(sku, device_id)
        if current is None:
            LOGGER.warning(
                "Could not read current brightness; skipping adjustment. device=%s", device_id
            )
            return False
        new_value = max(0, min(100, current + delta))
        return self._send_control_command(sku, device_id, "brightness", new_value)

    def _apply(self, target: str, capability: str, value: int, cap_type: str | None = None) -> bool:
        devices = self._resolve_targets(target)
        if not devices:
            return True
        if len(devices) == 1:
            d = devices[0]
            return self._send_control_command(d["sku"], d["device"], capability, value, cap_type)
        with ThreadPoolExecutor(max_workers=len(devices)) as executor:
            futures = [
                executor.submit(self._send_control_command, d["sku"], d["device"], capability, value, cap_type)
                for d in devices
            ]
            return all(f.result() for f in as_completed(futures))

    @staticmethod
    def _resolve_targets(target: str) -> list[dict[str, str]]:
        target = target.upper()
        catalog = {
            "TALL_LAMP": {"sku": GOVEE_DEVICE_SKU_TALL_LAMP, "device": GOVEE_DEVICE_ID_TALL_LAMP},
            "SHORT_LAMP": {"sku": GOVEE_DEVICE_SKU_SHORT_LAMP, "device": GOVEE_DEVICE_ID_SHORT_LAMP},
            "RICE_PAPER": {"sku": GOVEE_DEVICE_SKU_RICE_PAPER, "device": GOVEE_DEVICE_ID_RICE_PAPER},
        }
        if target == "ALL":
            return list(catalog.values())
        if target in catalog:
            return [catalog[target]]
        return []

    @staticmethod
    def _send_control_command(
        sku: str, device_id: str, capability: str, value: int, cap_type: str | None = None
    ) -> bool:
        if not GOVEE_API_KEY:
            LOGGER.warning("Govee API key missing. Fill GOVEE_API_KEY in config.py")
            return False
        if not sku or not device_id:
            LOGGER.warning("Missing Govee sku/device_id. Fill config.py globals.")
            return False

        headers = {"Govee-API-Key": GOVEE_API_KEY, "Content-Type": "application/json"}
        payload = {
            "requestId": "jarvis-dorm-mvp",
            "payload": {
                "sku": sku,
                "device": device_id,
                "capability": {
                    "type": cap_type or ("devices.capabilities.%s" % capability),
                    "instance": capability,
                    "value": value,
                },
            },
        }

        url = f"{GOVEE_BASE_URL}/router/api/v1/device/control"
        try:
            session = _get_session()
            response = session.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SEC)
            if 200 <= response.status_code < 300:
                LOGGER.info("Govee command success. capability=%s value=%s", capability, value)
                return True
            LOGGER.error(
                "Govee command failed. status=%s body=%s",
                response.status_code,
                response.text,
            )
            return False
        except requests.RequestException as exc:
            LOGGER.exception("Govee command exception: %s", exc)
            return False

    @staticmethod
    def _query_device_state(sku: str, device_id: str) -> dict | None:
        if not GOVEE_API_KEY:
            LOGGER.warning("Govee API key missing. Fill GOVEE_API_KEY in config.py")
            return None
        if not sku or not device_id:
            LOGGER.warning("Missing Govee sku/device_id. Fill config.py globals.")
            return None

        headers = {"Govee-API-Key": GOVEE_API_KEY, "Content-Type": "application/json"}
        payload = {
            "requestId": "jarvis-dorm-mvp",
            "payload": {
                "sku": sku,
                "device": device_id,
            },
        }

        url = f"{GOVEE_BASE_URL}/router/api/v1/device/state"
        try:
            session = _get_session()
            response = session.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SEC)
            if 200 <= response.status_code < 300:
                return response.json()
            LOGGER.error(
                "Govee state query failed. status=%s body=%s",
                response.status_code,
                response.text,
            )
            return None
        except (requests.RequestException, ValueError) as exc:
            LOGGER.exception("Govee state query exception: %s", exc)
            return None
