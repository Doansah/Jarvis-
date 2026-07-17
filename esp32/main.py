"""ESP32 Jarvis Light Controller — main app."""

import time
import network
import ujson
import urequests
from machine import I2C, Pin

import config
import ssd1306

# ── Hardware init ────────────────────────────────────────────────────────────

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400_000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

btn_cycle = Pin(12, Pin.IN, Pin.PULL_UP)  # cycles through presets
btn_power = Pin(14, Pin.IN, Pin.PULL_UP)  # toggles lights on/off

# ── Presets ──────────────────────────────────────────────────────────────────

PRESETS = [
    {"name": "Morning",  "brightness": 100, "r": 255, "g": 255, "b": 200},
    {"name": "Focus",    "brightness": 100, "r": 180, "g": 210, "b": 255},
    {"name": "Relax",    "brightness": 50,  "r": 255, "g": 140, "b": 60},
    {"name": "Warm",     "brightness": 40,  "kelvin": 2700},  # native warm-white, not orange
    {"name": "Movie",    "brightness": 15,  "r": 80,  "g": 0,   "b": 120},
    {"name": "Night",    "brightness": 5,   "r": 255, "g": 40,  "b": 0},
]

state = {"preset": 0, "power": False}

# ── Govee API ────────────────────────────────────────────────────────────────

def _send(capability, value, cap_type=None):
    """Send a single capability command to every configured device."""
    headers = {
        "Govee-API-Key": config.GOVEE_API_KEY,
        "Content-Type": "application/json",
    }
    url = config.GOVEE_BASE_URL + "/router/api/v1/device/control"

    for sku, device_id in config.DEVICES:
        body = ujson.dumps({
            "requestId": "esp32-jarvis",
            "payload": {
                "sku": sku,
                "device": device_id,
                "capability": {
                    "type": cap_type or ("devices.capabilities." + capability),
                    "instance": capability,
                    "value": value,
                },
            },
        })
        try:
            r = urequests.post(url, headers=headers, data=body,
                               timeout=config.REQUEST_TIMEOUT_SEC)
            r.close()
        except Exception as e:
            print("Govee error [%s %s]: %s" % (sku, capability, e))


def _apply_preset(index):
    """Send color (or color temperature) then brightness for the given preset index."""
    p = PRESETS[index]
    if "kelvin" in p:
        _send("colorTemperatureK", p["kelvin"], cap_type="devices.capabilities.color_setting")
    else:
        color_val = (p["r"] << 16) | (p["g"] << 8) | p["b"]
        _send("colorRgb", color_val)
    time.sleep_ms(200)
    _send("brightness", p["brightness"])


# ── Display ──────────────────────────────────────────────────────────────────

def _draw():
    oled.fill(0)
    p = PRESETS[state["preset"]]
    wifi_ok = network.WLAN(network.STA_IF).isconnected()

    # row 0 — header (centred in 16-char field)
    title = "JARVIS LIGHTS"
    oled.text(title, (128 - len(title) * 8) // 2, 0)

    # row 1 — divider
    oled.hline(0, 10, 128, 1)

    # row 3 — preset name with arrow
    oled.text("> " + p["name"], 0, 22)

    # row 4 — position indicator
    pos = "Preset %d/%d" % (state["preset"] + 1, len(PRESETS))
    oled.text(pos, 8, 34)

    # row 5 — divider
    oled.hline(0, 45, 128, 1)

    # row 6 — power state + wifi indicator
    power_str = "Power: ON " if state["power"] else "Power: OFF"
    oled.text(power_str, 0, 52)

    if not wifi_ok:
        oled.text("!", 120, 52)

    oled.show()


def _show_no_wifi():
    oled.fill(0)
    oled.text("JARVIS LIGHTS", 0, 0)
    oled.hline(0, 10, 128, 1)
    oled.text("No WiFi!", 24, 28)
    oled.text("Check config.py", 0, 44)
    oled.show()


# ── Main loop ────────────────────────────────────────────────────────────────

DEBOUNCE_MS = 200

last_cycle = 0
last_power = 0

if not network.WLAN(network.STA_IF).isconnected():
    _show_no_wifi()
else:
    _draw()

while True:
    now = time.ticks_ms()

    if btn_cycle.value() == 0 and time.ticks_diff(now, last_cycle) > DEBOUNCE_MS:
        last_cycle = now
        state["preset"] = (state["preset"] + 1) % len(PRESETS)
        if state["power"]:
            _apply_preset(state["preset"])
        _draw()

    if btn_power.value() == 0 and time.ticks_diff(now, last_power) > DEBOUNCE_MS:
        last_power = now
        state["power"] = not state["power"]
        if state["power"]:
            _send("powerSwitch", 1)
            time.sleep_ms(300)
            _apply_preset(state["preset"])
        else:
            _send("powerSwitch", 0)
        _draw()

    time.sleep_ms(50)
