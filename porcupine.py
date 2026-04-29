"""Wake word controller interfaces and implementations."""

import io
import wave
from abc import ABC, abstractmethod
import logging

import numpy as np
import sounddevice as sd

LOGGER = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHANNELS = 1


class WakeController(ABC):
    """Wake engine contract."""

    @abstractmethod
    def wait_for_wake(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_segment(self, seconds: int = 7) -> bytes:
        raise NotImplementedError


class KeyboardWakeController(WakeController):
    """Press Enter to wake, then records from the Mac microphone.

    Swap for ESP32WakeController when hardware is ready:
      - wait_for_wake(): block on an HTTP/UDP signal from the board
      - record_segment(): receive audio bytes over the network
    """

    def wait_for_wake(self) -> None:
        input("\n[Jarvis] Press Enter to start recording...")

    def record_segment(self, seconds: int = 7) -> bytes:
        LOGGER.info("Recording %s seconds...", seconds)
        print(f"[Jarvis] Recording for {seconds}s — speak now")

        frames = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )
        sd.wait()
        print("[Jarvis] Done recording")

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(frames.tobytes())

        return buf.getvalue()


class PorcupineWakeController(WakeController):
    """Porcupine-backed wake controller stub.

    TODO: Replace internals with real Porcupine SDK integration.
    """

    def wait_for_wake(self) -> None:
        LOGGER.info("Waiting for wake word (Porcupine stub)...")

    def record_segment(self, seconds: int = 7) -> bytes:
        LOGGER.info("Recording audio segment (stub) for %s seconds", seconds)
        return b""
