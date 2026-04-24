"""Lighting interfaces and Govee API adapter for Jarvis."""

from abc import ABC, abstractmethod
import logging

import requests

from config import (
    GOVEE_API_KEY,
    GOVEE_BASE_URL,
    GOVEE_DEVICE_ID_RICE_PAPER,
    GOVEE_DEVICE_ID_TALL_LAMP,
    GOVEE_DEVICE_SKU_RICE_PAPER,
    GOVEE_DEVICE_SKU_TALL_LAMP,
    REQUEST_TIMEOUT_SEC,
)

LOGGER = logging.getLogger(__name__)


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


class GoveeLightController(LightController):
    """Govee OpenAPI implementation."""

    def turn_on(self, target: str) -> bool:
        return self._apply(target, capability="powerSwitch", value=1)

    def turn_off(self, target: str) -> bool:
        return self._apply(target, capability="powerSwitch", value=0)

    def set_brightness(self, target: str, value: int) -> bool:
        brightness = max(0, min(100, value))
        return self._apply(target, capability="brightness", value=brightness)

    def _apply(self, target: str, capability: str, value: int) -> bool:
        devices = self._resolve_targets(target)
        ok = True
        for device in devices:
            ok = self._send_control_command(device["sku"], device["device"], capability, value) and ok
        return ok

    @staticmethod
    def _resolve_targets(target: str) -> list[dict[str, str]]:
        target = target.upper()
        catalog = {
            "TALL_LAMP": {"sku": GOVEE_DEVICE_SKU_TALL_LAMP, "device": GOVEE_DEVICE_ID_TALL_LAMP},
            "RICE_PAPER": {"sku": GOVEE_DEVICE_SKU_RICE_PAPER, "device": GOVEE_DEVICE_ID_RICE_PAPER},
        }
        if target == "ALL":
            return list(catalog.values())
        if target in catalog:
            return [catalog[target]]
        return []

    @staticmethod
    def _send_control_command(sku: str, device_id: str, capability: str, value: int) -> bool:
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
                    "type": "devices.capabilities.%s" % capability,
                    "instance": capability,
                    "value": value,
                },
            },
        }

        url = f"{GOVEE_BASE_URL}/router/api/v1/device/control"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SEC)
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
