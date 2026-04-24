"""Whisper transcription wrapper."""

import logging

from config import OPENAI_API_KEY, WHISPER_MODEL

LOGGER = logging.getLogger(__name__)


def transcribe_whisper(audio_bytes: bytes) -> str:
    """Transcribe audio with Whisper.

    This is a stub for now. Replace with OpenAI API call using OPENAI_API_KEY.
    """
    if not OPENAI_API_KEY:
        LOGGER.warning("OPENAI_API_KEY missing in config.py; returning empty transcript.")
        return ""

    LOGGER.info("Whisper stub called with model=%s and bytes=%s", WHISPER_MODEL, len(audio_bytes))
    return ""
