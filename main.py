"""Main runtime orchestrator for Jarvis dorm MVP."""

import logging

from actions import dispatch_intent, parse_deterministic, parse_smart_fallback
from config import LOG_LEVEL, USE_SMART_INTENT_FALLBACK, WAKE_RECORD_SECONDS
from lighting import GoveeLightController
from porcupine import KeyboardWakeController
from telemetry import CycleTimer
from transcription import transcribe_whisper

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

LOGGER = logging.getLogger(__name__)


def run_once() -> None:
    """Run a single wake→record→transcribe→parse→dispatch cycle."""
    wake_engine = KeyboardWakeController()
    lights = GoveeLightController()
    timer = CycleTimer()

    wake_engine.wait_for_wake()

    with timer.step("record"):
        audio_bytes = wake_engine.record_segment(seconds=WAKE_RECORD_SECONDS)

    with timer.step("transcribe"):
        transcript = transcribe_whisper(audio_bytes)

    with timer.step("parse"):
        intent = parse_deterministic(transcript)
        LOGGER.info(
            "Deterministic parse: known=%s action=%s target=%s",
            intent.known, intent.action, intent.target,
        )

        if not intent.known and USE_SMART_INTENT_FALLBACK:
            LOGGER.info("Deterministic miss — falling back to smart parser")
            intent = parse_smart_fallback(transcript)
            LOGGER.info(
                "Smart fallback result: known=%s action=%s target=%s value=%s",
                intent.known, intent.action, intent.target, intent.value,
            )

    with timer.step("dispatch"):
        dispatch_intent(intent, lights)

    timer.print_report(
        transcript=transcript,
        action=intent.action,
        target=intent.target,
        value=intent.value,
        intent_source=intent.source,
        intent_known=intent.known,
    )


def run_forever() -> None:
    """Continuously run wake cycles."""
    LOGGER.info("Jarvis started — USE_SMART_INTENT_FALLBACK=%s", USE_SMART_INTENT_FALLBACK)
    while True:
        run_once()


if __name__ == "__main__":
    run_forever()
