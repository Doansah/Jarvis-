"""Cycle timing and terminal report for Jarvis pipeline steps."""

import logging
import time
from contextlib import contextmanager
from typing import Generator

LOGGER = logging.getLogger(__name__)

_BAR_WIDTH = 40
_COL_LABEL = 12


class CycleTimer:
    """Accumulates per-step durations for one voice command cycle."""

    def __init__(self) -> None:
        self._steps: list[tuple[str, float]] = []

    @contextmanager
    def step(self, label: str) -> Generator[None, None, None]:
        start = time.perf_counter()
        LOGGER.debug("Step start: %s", label)
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._steps.append((label, elapsed_ms))
            LOGGER.debug("Step done:  %s — %.1f ms", label, elapsed_ms)

    def print_report(
        self,
        transcript: str = "",
        action: str = "",
        target: str = "",
        value: int | None = None,
        intent_source: str = "",
        intent_known: bool = False,
    ) -> None:
        total_ms = sum(ms for _, ms in self._steps)
        max_ms = max((ms for _, ms in self._steps), default=1)

        divider = "═" * 57
        thin = "─" * 57

        print(f"\n{divider}")
        print(f"  Jarvis cycle complete  |  total: {total_ms:,.0f} ms")
        print(thin)

        if transcript:
            print(f'  Transcript : "{transcript}"')

        if intent_known:
            value_str = f"  value={value}" if value is not None else ""
            print(f"  Intent     : {action} → {target}{value_str}  [{intent_source}]")
        else:
            print(f"  Intent     : UNKNOWN  [{intent_source}]")

        print(thin)

        for label, ms in self._steps:
            filled = round((ms / max_ms) * _BAR_WIDTH)
            bar = "█" * filled + "░" * (_BAR_WIDTH - filled)
            print(f"  {label:<{_COL_LABEL}} [{ms:>8,.1f} ms]  {bar}")

        print(f"{divider}\n")

        LOGGER.info(
            "Cycle summary — total=%.0f ms steps=%s",
            total_ms,
            {label: f"{ms:.0f}ms" for label, ms in self._steps},
        )
