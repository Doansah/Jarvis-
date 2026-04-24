"""Wake word controller interfaces and Porcupine stub implementation."""

from abc import ABC, abstractmethod
import logging

LOGGER = logging.getLogger(__name__)


class WakeController(ABC):
    """Wake engine contract."""

    @abstractmethod
    def wait_for_wake(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_segment(self, seconds: int = 7) -> bytes:
        raise NotImplementedError


class PorcupineWakeController(WakeController):
    """Porcupine-backed wake controller stub.

    Replace internals with real ESP32/Porcupine integration.
    """

    def wait_for_wake(self) -> None:
        LOGGER.info("Waiting for wake word (Porcupine stub)...")

    def record_segment(self, seconds: int = 7) -> bytes:
        LOGGER.info("Recording audio segment (stub) for %s seconds", seconds)
        return b""
