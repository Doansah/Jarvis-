"""Persisted per-user lighting defaults for Jarvis (calibration)."""

import json
import logging
import time
from pathlib import Path

LOGGER = logging.getLogger(__name__)

_SETTINGS_PATH = Path(__file__).resolve().parent / "user_settings.json"

# Warm *natural* white (~2700K), not the old orange RGB approximation.
# Used until the user calibrates their own default via voice.
FACTORY_DEFAULT: dict = {
    "brightness": 40,
    "mode": "kelvin",
    "kelvin": 2700,
    "rgb": None,
    "captured_from": "",
    "updated_at": "",
}


def load_default() -> dict:
    """Return the user's calibrated default lighting settings.

    Falls back to FACTORY_DEFAULT (warm natural white) if nothing has been
    calibrated yet, or if the settings file is missing/corrupt.
    """
    if not _SETTINGS_PATH.exists():
        return dict(FACTORY_DEFAULT)
    try:
        with _SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if "brightness" not in data or "mode" not in data:
            raise ValueError("settings file missing required keys")
        merged = dict(FACTORY_DEFAULT)
        merged.update(data)
        return merged
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        LOGGER.warning("Failed to read %s (%s); using factory default.", _SETTINGS_PATH, exc)
        return dict(FACTORY_DEFAULT)


def save_default(
    *,
    brightness: int,
    kelvin: int | None = None,
    rgb: tuple[int, int, int] | None = None,
    captured_from: str = "",
) -> dict:
    """Persist the given lighting state as the user's new calibrated default.

    Exactly one of kelvin/rgb should be provided; kelvin takes precedence if
    both are given, since native color temperature reads as true warm/cool
    white rather than an RGB approximation.
    """
    mode = "kelvin" if kelvin is not None else "rgb"
    data = {
        "brightness": max(0, min(100, int(brightness))),
        "mode": mode,
        "kelvin": int(kelvin) if kelvin is not None else None,
        "rgb": list(rgb) if rgb is not None else None,
        "captured_from": captured_from,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    try:
        with _SETTINGS_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        LOGGER.info("Saved new default lighting: %s", data)
    except OSError as exc:
        LOGGER.error("Failed to save default lighting settings: %s", exc)
    return data
