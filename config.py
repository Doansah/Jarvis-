"""Central config for Jarvis dorm MVP.

Fill in these globals before running against real services.
"""

# Runtime toggles
USE_SMART_INTENT_FALLBACK = True
WAKE_RECORD_SECONDS = 7
LOG_LEVEL = "INFO"

# OpenAI
OPENAI_API_KEY = ""
WHISPER_MODEL = "gpt-4o-mini-transcribe"
SMART_INTENT_MODEL = "gpt-4.1-mini"

# Govee
GOVEE_API_KEY = ""
GOVEE_BASE_URL = "https://openapi.api.govee.com"

GOVEE_DEVICE_SKU_TALL_LAMP = ""
GOVEE_DEVICE_ID_TALL_LAMP = ""
GOVEE_DEVICE_SKU_RICE_PAPER = ""
GOVEE_DEVICE_ID_RICE_PAPER = ""

REQUEST_TIMEOUT_SEC = 10
