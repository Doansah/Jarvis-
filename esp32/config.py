"""
ESP32 Jarvis Light Controller — Configuration
Fill in your credentials below, then upload to the ESP32.
Copy device SKUs and IDs from the root Jarvis config.py.
"""

WIFI_SSID = "GoucherGuest"
WIFI_PASSWORD = ""

GOVEE_API_KEY = "your_govee_api_key"
GOVEE_BASE_URL = "https://openapi.api.govee.com"
REQUEST_TIMEOUT_SEC = 10

# List of (sku, device_id) tuples — one entry per Govee device.
# Copy values from GOVEE_DEVICE_SKU_* and GOVEE_DEVICE_ID_* in the root config.py.
DEVICES = [
    ("TALL_LAMP_SKU_HERE",   "TALL_LAMP_DEVICE_ID_HERE"),
    ("SHORT_LAMP_SKU_HERE",  "SHORT_LAMP_DEVICE_ID_HERE"),
    ("RICE_PAPER_SKU_HERE",  "RICE_PAPER_DEVICE_ID_HERE"),
]
