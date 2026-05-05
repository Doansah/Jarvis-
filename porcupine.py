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

# VAD constants
_VAD_CHUNK = 1600          # 100 ms per chunk at 16 kHz
_SILENCE_RMS = 400         # below this → silence
_SILENCE_SECS = 1.0        # stop after this many consecutive silent seconds
_MIN_SPEECH_SECS = 0.5     # never stop before this many seconds of audio


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
        LOGGER.info("Recording up to %s seconds (VAD enabled)...", seconds)
        print(f"[Jarvis] Recording (up to {seconds}s) — speak now")

        max_chunks = int(seconds * SAMPLE_RATE / _VAD_CHUNK)
        min_chunks = int(_MIN_SPEECH_SECS * SAMPLE_RATE / _VAD_CHUNK)
        silence_chunks_needed = int(_SILENCE_SECS * SAMPLE_RATE / _VAD_CHUNK)

        collected: list[np.ndarray] = []
        silence_run = 0
        speech_detected = False

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16") as stream:
            for _ in range(max_chunks):
                chunk, _ = stream.read(_VAD_CHUNK)
                collected.append(chunk.copy())
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

                if rms > _SILENCE_RMS:
                    speech_detected = True
                    silence_run = 0
                elif speech_detected and len(collected) >= min_chunks:
                    silence_run += 1
                    if silence_run >= silence_chunks_needed:
                        break

        elapsed = len(collected) * _VAD_CHUNK / SAMPLE_RATE
        print(f"[Jarvis] Done recording ({elapsed:.1f}s)")
        LOGGER.info("Recorded %.1fs of audio", elapsed)

        frames = np.concatenate(collected, axis=0)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
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
