"""Intent schema, parsers, and action dispatcher for Jarvis."""

from dataclasses import dataclass
import json
import logging
import re

import openai

from config import OPENAI_API_KEY, SMART_INTENT_MODEL
from lighting import LightController

LOGGER = logging.getLogger(__name__)

_SLEEP_TRIGGERS = {"sleep", "goodbye", "good night", "goodnight", "shut down", "shutdown", "stop listening", "go to sleep"}

COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "red":    (255, 0, 0),
    "green":  (0, 200, 0),
    "blue":   (0, 0, 255),
    "yellow": (255, 220, 0),
    "orange": (255, 100, 0),
    "purple": (128, 0, 255),
    "pink":   (255, 20, 147),
    "white":  (255, 255, 255),
    "cyan":   (0, 200, 200),
    "teal":   (0, 180, 180),
}

PRESETS: dict[str, dict] = {
    "warm":    {"brightness": 40,  "color": (255, 100, 30)},
    "cozy":    {"brightness": 40,  "color": (255, 100, 30)},
    "cold":    {"brightness": 100, "color": (180, 210, 255)},
    "cool":    {"brightness": 100, "color": (180, 210, 255)},
    "focus":   {"brightness": 100, "color": (180, 210, 255)},
    "night":   {"brightness": 5,   "color": (255, 40, 0)},
    "sleep":   {"brightness": 5,   "color": (255, 40, 0)},
    "morning": {"brightness": 100, "color": (255, 255, 200)},
    "movie":   {"brightness": 15,  "color": (80, 0, 120)},
    "cinema":  {"brightness": 15,  "color": (80, 0, 120)},
    "relax":   {"brightness": 50,  "color": (255, 140, 60)},
    "chill":   {"brightness": 50,  "color": (255, 140, 60)},
}

_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client


class SleepRequested(Exception):
    """Raised when the user asks Jarvis to stop listening."""


@dataclass
class Intent:
    """Normalized command intent."""

    action: str = "UNKNOWN"
    target: str = "ALL"
    value: int | None = None
    color: tuple[int, int, int] | None = None
    preset: str | None = None
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

    if any(trigger in normalized for trigger in _SLEEP_TRIGGERS):
        return Intent(action="SLEEP", known=True, raw_text=text)

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

    for preset_name in PRESETS:
        if preset_name in normalized:
            return Intent(action="APPLY_PRESET", target=target, preset=preset_name, known=True, raw_text=text)

    for color_name, rgb in COLOR_MAP.items():
        if color_name in normalized:
            return Intent(action="SET_COLOR", target=target, color=rgb, known=True, raw_text=text)

    return Intent(raw_text=text)


_SYSTEM_PROMPT = """You are a smart home intent parser. Given a voice command, return ONLY a JSON object with these fields:
- action: one of LIGHT_ON, LIGHT_OFF, SET_BRIGHTNESS, SET_COLOR, APPLY_PRESET, SLEEP, UNKNOWN
- target: one of ALL, TALL_LAMP, SHORT_LAMP, RICE_PAPER
- value: integer 0-100 for SET_BRIGHTNESS, otherwise null
- r, g, b: integers 0-255 for SET_COLOR (omit for other actions)
- preset: string for APPLY_PRESET — one of: warm, cozy, cold, cool, focus, night, sleep, morning, movie, cinema, relax, chill (omit for other actions)

Devices: TALL_LAMP is "Dillon's Lamp", SHORT_LAMP is the short bedside lamp, RICE_PAPER is the rice paper lamp.

Examples:
"lights out" -> {"action": "LIGHT_OFF", "target": "ALL", "value": null}
"brighten the tall lamp" -> {"action": "SET_BRIGHTNESS", "target": "TALL_LAMP", "value": 80}
"turn off the short one" -> {"action": "LIGHT_OFF", "target": "SHORT_LAMP", "value": null}
"make it red" -> {"action": "SET_COLOR", "target": "ALL", "r": 255, "g": 0, "b": 0}
"blue light on the tall lamp" -> {"action": "SET_COLOR", "target": "TALL_LAMP", "r": 0, "g": 0, "b": 255}
"warm mode" -> {"action": "APPLY_PRESET", "target": "ALL", "preset": "warm"}
"focus mode" -> {"action": "APPLY_PRESET", "target": "ALL", "preset": "focus"}
"movie time" -> {"action": "APPLY_PRESET", "target": "ALL", "preset": "movie"}
"goodbye jarvis" -> {"action": "SLEEP", "target": "ALL", "value": null}
"go to sleep" -> {"action": "SLEEP", "target": "ALL", "value": null}

Return only the JSON object, no explanation."""


def parse_smart_fallback(text: str) -> Intent:
    """Use gpt-4.1-mini to parse ambiguous commands into a structured Intent."""
    if not OPENAI_API_KEY:
        LOGGER.warning("OPENAI_API_KEY missing; smart fallback unavailable.")
        return Intent(raw_text=text, source="smart_fallback")

    LOGGER.info("Smart fallback parsing: %r", text)
    try:
        client = _get_client()
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
        color = None
        if action == "SET_COLOR" and all(k in data for k in ("r", "g", "b")):
            color = (int(data["r"]), int(data["g"]), int(data["b"]))
        preset = data.get("preset")
        known = action != "UNKNOWN"
        return Intent(action=action, target=target, value=value, color=color, preset=preset, known=known, source="smart_fallback", raw_text=text)
    except Exception as exc:
        LOGGER.warning("Smart fallback failed (%s); returning unknown intent.", exc)
        return Intent(raw_text=text, source="smart_fallback")


def dispatch_intent(intent: Intent, lights: LightController) -> None:
    """Execute known intents through the light controller; otherwise log."""
    if not intent.known:
        LOGGER.info("Unknown intent logged only: %s", intent.raw_text)
        return

    if intent.action == "SLEEP":
        raise SleepRequested

    if intent.action == "LIGHT_ON":
        lights.turn_on(intent.target)
        return

    if intent.action == "LIGHT_OFF":
        lights.turn_off(intent.target)
        return

    if intent.action == "SET_BRIGHTNESS" and intent.value is not None:
        lights.set_brightness(intent.target, intent.value)
        return

    if intent.action == "SET_COLOR" and intent.color is not None:
        r, g, b = intent.color
        lights.set_color(intent.target, r, g, b)
        return

    if intent.action == "APPLY_PRESET" and intent.preset is not None:
        p = PRESETS.get(intent.preset)
        if p:
            lights.set_color(intent.target, *p["color"])
            lights.set_brightness(intent.target, p["brightness"])
        return

    LOGGER.info("Unhandled known intent logged only: %s", intent)
