"""Intent schema, parsers, and action dispatcher for Jarvis."""

from dataclasses import dataclass
import json
import logging
import re

import openai

from config import OPENAI_API_KEY, SMART_INTENT_MODEL
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
    elif "short lamp" in normalized:
        target = "SHORT_LAMP"
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


_SYSTEM_PROMPT = """You are a smart home intent parser. Given a voice command, return ONLY a JSON object with these fields:
- action: one of LIGHT_ON, LIGHT_OFF, SET_BRIGHTNESS, UNKNOWN
- target: one of ALL, TALL_LAMP, SHORT_LAMP, RICE_PAPER
- value: integer 0-100 for SET_BRIGHTNESS, otherwise null

Devices: TALL_LAMP is "Dillon's Lamp", SHORT_LAMP is the short bedside lamp, RICE_PAPER is the rice paper lamp.

Examples:
"make it cozy" -> {"action": "SET_BRIGHTNESS", "target": "ALL", "value": 30}
"lights out" -> {"action": "LIGHT_OFF", "target": "ALL", "value": null}
"brighten the tall lamp" -> {"action": "SET_BRIGHTNESS", "target": "TALL_LAMP", "value": 80}
"turn off the short one" -> {"action": "LIGHT_OFF", "target": "SHORT_LAMP", "value": null}

Return only the JSON object, no explanation."""


def parse_smart_fallback(text: str) -> Intent:
    """Use gpt-4.1-mini to parse ambiguous commands into a structured Intent."""
    if not OPENAI_API_KEY:
        LOGGER.warning("OPENAI_API_KEY missing; smart fallback unavailable.")
        return Intent(raw_text=text, source="smart_fallback")

    LOGGER.info("Smart fallback parsing: %r", text)
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=SMART_INTENT_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        action = data.get("action", "UNKNOWN").upper()
        target = data.get("target", "ALL").upper()
        value = data.get("value")
        known = action != "UNKNOWN"
        return Intent(action=action, target=target, value=value, known=known, source="smart_fallback", raw_text=text)
    except Exception as exc:
        LOGGER.warning("Smart fallback failed (%s); returning unknown intent.", exc)
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
