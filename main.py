"""Main runtime orchestrator for Jarvis dorm MVP."""

from actions import dispatch_intent, parse_deterministic, parse_smart_fallback
from config import USE_SMART_INTENT_FALLBACK, WAKE_RECORD_SECONDS
from lighting import GoveeLightController
from porcupine import PorcupineWakeController
from transcription import transcribe_whisper


def handle_transcript(text: str, lights: GoveeLightController) -> None:
    """Parse transcript into an intent and execute if known."""
    intent = parse_deterministic(text)

    if not intent.known and USE_SMART_INTENT_FALLBACK:
        intent = parse_smart_fallback(text)

    dispatch_intent(intent, lights)


def run_once() -> None:
    """Run a single wake->record->transcribe->parse->execute cycle."""
    wake_engine = PorcupineWakeController()
    lights = GoveeLightController()

    wake_engine.wait_for_wake()
    audio_bytes = wake_engine.record_segment(seconds=WAKE_RECORD_SECONDS)
    transcript = transcribe_whisper(audio_bytes)
    handle_transcript(transcript, lights)


def run_forever() -> None:
    """Continuously run wake cycles."""
    while True:
        run_once()


if __name__ == "__main__":
    run_forever()
