"""Intent schema, parsers, and action dispatcher for Jarvis."""

from dataclasses import dataclass
import logging
import re

from lighting import LightController

LOGGER = logging.getLogger(__name__)


@dataclass
class Intent:
    """Normalized command intent."""

    action: str = "UNKNOWN"
    target: str = "ALL"
    value: int | None = None
    known: bool = False
    source: str = "deterministic"
    raw_text: str = ""


def parse_deterministic(text: str) -> Intent:
    """Deterministic parser for the dorm MVP."""
    normalized = text.lower().strip()
    target = "ALL"

    if "tall lamp" in normalized:
        target = "TALL_LAMP"
    elif "rice paper" in normalized:
        target = "RICE_PAPER"

    if "light" in normalized or "lamp" in normalized:
        if " off" in f" {normalized}" or normalized.startswith("off"):
            return Intent(action="LIGHT_OFF", target=target, known=True, raw_text=text)
        if " on" in f" {normalized}" or normalized.startswith("on"):
            return Intent(action="LIGHT_ON", target=target, known=True, raw_text=text)

    brightness_match = re.search(r"(?:brightness|bright)\D*(\d{1,3})", normalized)
    if brightness_match:
        value = max(0, min(100, int(brightness_match.group(1))))
        return Intent(
            action="SET_BRIGHTNESS",
            target=target,
            value=value,
            known=True,
            raw_text=text,
        )

    return Intent(raw_text=text)


def parse_smart_fallback(text: str) -> Intent:
    """Stub for cheap-model fallback parser in cloud.

    Replace this with an API call that returns normalized JSON.
    """
    LOGGER.info("Smart fallback parser not yet implemented. text=%s", text)
    return Intent(raw_text=text, source="smart_fallback")


def dispatch_intent(intent: Intent, lights: LightController) -> None:
    """Execute known intents through the light controller; otherwise log."""
    if not intent.known:
        LOGGER.info("Unknown intent logged only: %s", intent.raw_text)
        return

    if intent.action == "LIGHT_ON":
        lights.turn_on(intent.target)
        return

    if intent.action == "LIGHT_OFF":
        lights.turn_off(intent.target)
        return

    if intent.action == "SET_BRIGHTNESS" and intent.value is not None:
        lights.set_brightness(intent.target, intent.value)
        return

    LOGGER.info("Unhandled known intent logged only: %s", intent)
