"""Central config for Jarvis dorm MVP."""

import os

from dotenv import load_dotenv

load_dotenv()

# Runtime toggles
USE_SMART_INTENT_FALLBACK = os.getenv("USE_SMART_INTENT_FALLBACK", "true").lower() == "true"
WAKE_RECORD_SECONDS = int(os.getenv("WAKE_RECORD_SECONDS", "7"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "gpt-4o-mini-transcribe")
SMART_INTENT_MODEL = os.getenv("SMART_INTENT_MODEL", "gpt-4.1-mini")

# Govee
GOVEE_API_KEY = os.getenv("GOVEE_API_KEY", "")
GOVEE_BASE_URL = os.getenv("GOVEE_BASE_URL", "https://openapi.api.govee.com")

GOVEE_DEVICE_SKU_TALL_LAMP = os.getenv("GOVEE_DEVICE_SKU_TALL_LAMP", "")
GOVEE_DEVICE_ID_TALL_LAMP = os.getenv("GOVEE_DEVICE_ID_TALL_LAMP", "")
GOVEE_DEVICE_SKU_SHORT_LAMP = os.getenv("GOVEE_DEVICE_SKU_SHORT_LAMP", "")
GOVEE_DEVICE_ID_SHORT_LAMP = os.getenv("GOVEE_DEVICE_ID_SHORT_LAMP", "")
GOVEE_DEVICE_SKU_RICE_PAPER = os.getenv("GOVEE_DEVICE_SKU_RICE_PAPER", "")
GOVEE_DEVICE_ID_RICE_PAPER = os.getenv("GOVEE_DEVICE_ID_RICE_PAPER", "")

REQUEST_TIMEOUT_SEC = int(os.getenv("REQUEST_TIMEOUT_SEC", "10"))
