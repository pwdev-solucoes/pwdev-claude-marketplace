#!/usr/bin/env python3
"""Observe one live interactive wrapper without inspecting its terminal."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import signal
import sys
import time
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interactive_state

TIMEOUT_SECONDS = 300.0
POLL_SECONDS = 1.0


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _original_parent(pid: int) -> bool:
    return os.getppid() == pid


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def observe(
    member_path: str | os.PathLike[str],
    parent_pid: int,
    *,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    parent_alive: Callable[[int], bool] = _alive,
    parent_is_original: Callable[[int], bool] = _original_parent,
    now: Callable[[], str] = _now,
    cancelled: Callable[[], bool] = lambda: False,
) -> str:
    if parent_pid <= 1:
        return "cancelled"
    member_path = Path(member_path)
    if member_path.is_symlink():
        return "cancelled"
    member_path = member_path.resolve(strict=True)
    started = clock()
    while True:
        if cancelled() or not parent_alive(parent_pid) or not parent_is_original(parent_pid):
            return "cancelled"
        elapsed = clock() - started
        if elapsed >= TIMEOUT_SECONDS:
            # Recheck immediately at the publication boundary. PID reuse or a
            # reparented observer must never mutate member state.
            if cancelled() or not parent_alive(parent_pid) or not parent_is_original(parent_pid):
                return "cancelled"
            try:
                interactive_state.transition(
                    member_path, "running", "awaiting_human",
                    {"next_action": "resume-session"}, now(),
                )
                return "awaiting_human"
            except interactive_state.InteractiveStateError:
                state = interactive_state.load_member(member_path)["interaction"]["state"]
                return "awaiting_human" if state == "awaiting_human" else "cancelled"
        sleep(min(POLL_SECONDS, TIMEOUT_SECONDS - elapsed))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("member_file", type=Path)
    parser.add_argument("parent_pid", type=int)
    args = parser.parse_args()
    stopping = False

    def stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGHUP, stop)
    observe(args.member_file, args.parent_pid, cancelled=lambda: stopping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
