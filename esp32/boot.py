"""Runs automatically on ESP32 startup before main.py — connects to WiFi."""

import network
import time

import config

_TIMEOUT_SEC = 20


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return True

    if config.WIFI_PASSWORD:
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    else:
        wlan.connect(config.WIFI_SSID)

    deadline = time.time() + _TIMEOUT_SEC
    while not wlan.isconnected():
        if time.time() > deadline:
            print("WiFi connection timed out")
            return False
        time.sleep(0.5)

    print("WiFi connected:", wlan.ifconfig()[0])
    return True


connect()
