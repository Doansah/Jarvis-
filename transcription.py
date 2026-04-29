"""Whisper transcription wrapper."""

import io
import logging

import openai

from config import OPENAI_API_KEY, WHISPER_MODEL

LOGGER = logging.getLogger(__name__)


def transcribe_whisper(audio_bytes: bytes) -> str:
    """Transcribe audio bytes with OpenAI Whisper."""
    if not OPENAI_API_KEY:
        LOGGER.warning("OPENAI_API_KEY missing; returning empty transcript.")
        return ""

    if not audio_bytes:
        LOGGER.warning("Empty audio bytes; skipping transcription.")
        return ""

    LOGGER.info("Transcribing with model=%s (%d bytes)", WHISPER_MODEL, len(audio_bytes))

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"

    response = client.audio.transcriptions.create(model=WHISPER_MODEL, file=audio_file)
    transcript = response.text.strip()
    LOGGER.info("Transcript: %r", transcript)
    return transcript
