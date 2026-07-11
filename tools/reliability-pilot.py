#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Interactive, resumable aggregate-only fprintd reliability pilot."""

from __future__ import annotations

import argparse
import csv
import os
import stat
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "artifacts/private/reliability/pilot-30x30.csv"
FIELDS = [
    "trial", "date", "cohort", "presentation", "condition", "expected",
    "observed", "protocol_error", "recovery", "notes",
]

GENUINE_COUNTS = {
    "centered-normal": 6,
    "clockwise-20deg": 5,
    "counterclockwise-20deg": 5,
    "fingertip-shift": 5,
    "knuckle-shift": 5,
    "light-pressure": 4,
}
GENUINE_PLAN = [
    ("right-index", condition)
    for round_index in range(max(GENUINE_COUNTS.values()))
    for condition, count in GENUINE_COUNTS.items()
    if round_index < count
]

DIFFERENT_PLAN = (
    [("left-index", "centered-normal")] * 4
    + [("right-middle", "centered-normal")] * 4
    + [("left-thumb", "centered-normal")] * 4
    + [("right-thumb", "centered-normal")] * 3
    + [("left-middle", "centered-normal")] * 3
    + [("right-ring", "centered-normal")] * 3
    + [("right-little", "centered-normal")] * 3
    + [("left-ring", "centered-normal")] * 3
    + [("left-little", "centered-normal")] * 3
)


def read_rows(ledger: Path) -> list[dict[str, str]]:
    if not ledger.exists():
        return []
    info = ledger.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"ledger must be a regular non-symlink file: {ledger}")
    with ledger.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"unexpected ledger columns: {reader.fieldnames}")
        return list(reader)


def remaining(plan: list[tuple[str, str]], cohort: str,
              rows: list[dict[str, str]]) -> list[tuple[str, str]]:
    completed = Counter(
        (row["presentation"], row["condition"])
        for row in rows if row["cohort"] == cohort
    )
    result: list[tuple[str, str]] = []
    for item in plan:
        if completed[item]:
            completed[item] -= 1
        else:
            result.append(item)
    return result


def make_session(rows: list[dict[str, str]], limit: int) -> list[tuple[str, str, str]]:
    genuine = remaining(GENUINE_PLAN, "genuine", rows)
    different = remaining(DIFFERENT_PLAN, "different-finger", rows)
    session: list[tuple[str, str, str]] = []
    prefer_genuine = sum(r["cohort"] == "genuine" for r in rows) <= sum(
        r["cohort"] == "different-finger" for r in rows
    )
    while len(session) < limit and (genuine or different):
        source = genuine if prefer_genuine else different
        cohort = "genuine" if prefer_genuine else "different-finger"
        if not source:
            source = different if prefer_genuine else genuine
            cohort = "different-finger" if prefer_genuine else "genuine"
        presentation, condition = source.pop(0)
        session.append((cohort, presentation, condition))
        prefer_genuine = not prefer_genuine
    return session


def ensure_ledger(ledger: Path) -> None:
    if ledger.exists():
        return
    ledger.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as stream:
        csv.DictWriter(stream, fieldnames=FIELDS).writeheader()


def append_row(ledger: Path, row: dict[str, str]) -> None:
    ensure_ledger(ledger)
    with ledger.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writerow(row)
        stream.flush()


def instruction(presentation: str, condition: str) -> str:
    condition_text = {
        "centered-normal": "centered, normal pressure",
        "clockwise-20deg": "rotated about 20 degrees clockwise, normal pressure",
        "counterclockwise-20deg": "rotated about 20 degrees counterclockwise, normal pressure",
        "fingertip-shift": "shifted toward the fingertip, normal pressure",
        "knuckle-shift": "shifted toward the knuckle, normal pressure",
        "light-pressure": "centered with noticeably lighter pressure",
    }[condition]
    return f"Present {presentation.upper()} exactly once: {condition_text}."


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run sparse, one-shot fprintd verification trials",
    )
    parser.add_argument("--count", type=int, default=1,
                        help="maximum trials this session (default: 1; max: 5)")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER,
                        help="aggregate CSV ledger path")
    parser.add_argument("--plan", action="store_true",
                        help="print the next trials without invoking fprintd")
    args = parser.parse_args()
    if not 1 <= args.count <= 5:
        parser.error("--count must be between 1 and 5")

    ledger = args.ledger.expanduser().resolve()
    try:
        rows = read_rows(ledger)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    session = make_session(rows, args.count)
    if not session:
        print("PILOT_COMPLETE: 30 genuine and 30 different-finger trials recorded")
        return 0

    next_attempt = max((int(r["trial"]) for r in rows), default=0) + 1
    valid_before = sum(r["cohort"] in {"genuine", "different-finger"} for r in rows)

    if args.plan:
        print(f"PLAN: {len(session)} trials; valid pilot progress {valid_before}/60")
        for index, (cohort, presentation, condition) in enumerate(session, start=1):
            expected = "match" if cohort == "genuine" else "no-match"
            print(f"{index}. {instruction(presentation, condition)} Expected: {expected}.")
        return 0

    print(f"SESSION_READY: {len(session)} trials; valid pilot progress {valid_before}/60")
    print("Use sparse sessions, stop if detection degrades, and never retry within a trial.")
    print("Ctrl+C between trials is safe.\n")

    valid_this_session = 0
    for cohort, presentation, condition in session:
        attempt = next_attempt
        expected = "match" if cohort == "genuine" else "no-match"
        print(f"Attempt {attempt}; valid target {valid_before + valid_this_session + 1}/60")
        print(instruction(presentation, condition))
        confirmation = input(f"Type {presentation.upper()} when ready, or SKIP: ").strip().lower()
        if confirmation == "skip":
            print("Skipped; nothing recorded.\n")
            continue
        if confirmation != presentation:
            print("Confirmation did not match; nothing recorded.\n")
            continue

        process = subprocess.run(
            ["fprintd-verify"], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False,
        )
        print(process.stdout, end="" if process.stdout.endswith("\n") else "\n")
        if "verify-no-match (done)" in process.stdout:
            observed, protocol_error = "no-match", "no"
        elif "verify-match (done)" in process.stdout:
            observed, protocol_error = "match", "no"
        else:
            observed, protocol_error = "error", "yes"

        exact = input("Was only the requested finger presented exactly once? [y/N]: ").strip().lower()
        if exact != "y":
            cohort_recorded = "excluded"
            notes = f"intended {presentation}; presentation not confirmed"
        else:
            cohort_recorded = cohort
            notes = "one presentation"

        recovery = "no"
        if protocol_error == "yes":
            recovery = "yes" if input("Was recovery required? [y/N]: ").strip().lower() == "y" else "no"

        append_row(ledger, {
            "trial": str(attempt),
            "date": date.today().isoformat(),
            "cohort": cohort_recorded,
            "presentation": presentation,
            "condition": condition,
            "expected": expected,
            "observed": observed,
            "protocol_error": protocol_error,
            "recovery": recovery,
            "notes": notes,
        })
        next_attempt += 1
        if cohort_recorded in {"genuine", "different-finger"}:
            valid_this_session += 1
        print(f"RECORDED: expected={expected} observed={observed} cohort={cohort_recorded}\n")

    print("SESSION_COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
