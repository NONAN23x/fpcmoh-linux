#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Resumable 30-trial smoke test for two explicitly selected fprintd templates."""

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
DEFAULT_LEDGER = ROOT / "artifacts/private/reliability/rebase-ba10c939-30.csv"
FIELDS = [
    "attempt", "date", "plan_id", "cohort", "target", "presentation",
    "condition", "expected", "observed", "protocol_error", "recovery", "notes",
]

CONDITION_TEXT = {
    "centered-normal": "centered, normal pressure",
    "clockwise-20deg": "rotated about 20 degrees clockwise, normal pressure",
    "counterclockwise-20deg": "rotated about 20 degrees counterclockwise, normal pressure",
    "fingertip-shift": "shifted toward the fingertip, normal pressure",
    "knuckle-shift": "shifted toward the knuckle, normal pressure",
    "light-pressure": "centered with noticeably lighter pressure",
}

GENUINE = [
    ("right-index", "centered-normal"),
    ("left-middle", "centered-normal"),
    ("right-index", "clockwise-20deg"),
    ("left-middle", "clockwise-20deg"),
    ("right-index", "counterclockwise-20deg"),
    ("left-middle", "counterclockwise-20deg"),
    ("right-index", "fingertip-shift"),
    ("left-middle", "fingertip-shift"),
    ("right-index", "knuckle-shift"),
    ("left-middle", "knuckle-shift"),
    ("right-index", "light-pressure"),
    ("left-middle", "light-pressure"),
    ("right-index", "centered-normal"),
    ("left-middle", "centered-normal"),
    ("right-index", "centered-normal"),
]

CONTROLS = [
    ("left-middle", "right-index"),
    ("right-index", "left-middle"),
    ("right-index", "left-index"),
    ("left-middle", "right-middle"),
    ("right-index", "left-thumb"),
    ("left-middle", "right-thumb"),
    ("right-index", "left-ring"),
    ("left-middle", "right-ring"),
    ("right-index", "left-little"),
    ("left-middle", "right-little"),
    ("right-index", "right-middle"),
    ("left-middle", "left-index"),
    ("right-index", "left-middle"),
    ("left-middle", "right-index"),
    ("right-index", "left-thumb"),
]


def build_plan() -> list[dict[str, str]]:
    plan: list[dict[str, str]] = []
    for index, ((finger, condition), (target, presentation)) in enumerate(
        zip(GENUINE, CONTROLS, strict=True), start=1
    ):
        plan.append({
            "plan_id": f"G{index:02d}", "cohort": "genuine",
            "target": f"{finger}-finger", "presentation": finger,
            "condition": condition, "expected": "match",
        })
        plan.append({
            "plan_id": f"C{index:02d}", "cohort": "different-finger",
            "target": f"{target}-finger", "presentation": presentation,
            "condition": "centered-normal", "expected": "no-match",
        })
    return plan


PLAN = build_plan()


def read_rows(ledger: Path) -> list[dict[str, str]]:
    if not ledger.exists():
        return []
    info = ledger.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f"ledger must be a regular non-symlink file: {ledger}")
    if stat.S_IMODE(info.st_mode) & 0o077:
        raise ValueError(f"ledger permissions must not allow group/other access: {ledger}")
    with ledger.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"unexpected ledger columns: {reader.fieldnames}")
        return list(reader)


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
        csv.DictWriter(stream, fieldnames=FIELDS).writerow(row)
        stream.flush()


def remaining(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    completed = {
        row["plan_id"] for row in rows
        if row["cohort"] in {"genuine", "different-finger"}
    }
    return [entry for entry in PLAN if entry["plan_id"] not in completed]


def instruction(entry: dict[str, str]) -> str:
    return (
        f"Target template: {entry['target'].upper()}\n"
        f"Present: {entry['presentation'].upper()} exactly once, "
        f"{CONDITION_TEXT[entry['condition']]}.\n"
        f"Expected: {entry['expected']}."
    )


def summary(rows: list[dict[str, str]]) -> str:
    valid = [r for r in rows if r["cohort"] in {"genuine", "different-finger"}]
    genuine = [r for r in valid if r["cohort"] == "genuine"]
    controls = [r for r in valid if r["cohort"] == "different-finger"]
    excluded = sum(r["cohort"] == "excluded" for r in rows)
    errors = sum(r["protocol_error"] == "yes" for r in rows)
    recoveries = sum(r["recovery"] == "yes" for r in rows)
    genuine_matches = Counter(r["observed"] for r in genuine)["match"]
    control_rejects = Counter(r["observed"] for r in controls)["no-match"]
    return (
        f"SUMMARY: valid={len(valid)}/30 excluded={excluded} "
        f"genuine_matches={genuine_matches}/{len(genuine)} "
        f"different_finger_rejects={control_rejects}/{len(controls)} "
        f"protocol_errors={errors} recoveries={recoveries}"
    )


def safe_core_limit() -> bool:
    try:
        process = subprocess.run(
            [
                "systemctl", "show", "fprintd.service",
                "--property=LimitCORE", "--value",
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        print(f"SAFETY_CHECK_FAILED: cannot inspect fprintd LimitCORE: {error}")
        return False
    value = process.stdout.strip()
    if process.returncode != 0 or value != "0":
        shown = value or "unavailable"
        print(f"SAFETY_CHECK_FAILED: fprintd LimitCORE={shown}; required=0")
        print("No verification was started. Restore the approved core limit first.")
        return False
    print("SAFETY_CHECK_OK: fprintd LimitCORE=0")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a resumable 30-trial two-template rebase smoke test",
    )
    parser.add_argument(
        "--count", type=int, default=30,
        help="maximum valid trials this run (default: all remaining; max: 30)",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--plan", action="store_true", help="show remaining plan only")
    parser.add_argument("--summary", action="store_true", help="show ledger summary only")
    args = parser.parse_args()
    if not 1 <= args.count <= 30:
        parser.error("--count must be between 1 and 30")

    ledger = args.ledger.expanduser().resolve()
    try:
        rows = read_rows(ledger)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.summary:
        print(summary(rows))
        return 0

    todo = remaining(rows)
    if not todo:
        print("REBASE_SMOKE_COMPLETE")
        print(summary(rows))
        return 0

    todo = todo[:args.count]
    valid_before = sum(r["cohort"] in {"genuine", "different-finger"} for r in rows)
    if args.plan:
        print(f"PLAN: {len(todo)} trials; valid progress {valid_before}/30")
        for index, entry in enumerate(todo, start=1):
            print(f"\n{index}. {entry['plan_id']}\n{instruction(entry)}")
        return 0

    if not safe_core_limit():
        return 2

    next_attempt = max((int(r["attempt"]) for r in rows), default=0) + 1
    valid_this_run = 0
    print(f"SESSION_READY: {len(todo)} trials; valid progress {valid_before}/30")
    print("Pause at each five-trial checkpoint. Never retry within one trial.\n")

    try:
        for index, entry in enumerate(todo, start=1):
            if valid_this_run and valid_this_run % 5 == 0:
                action = input(
                    "CHECKPOINT: wait at least 30 seconds, clean/dry the sensor, "
                    "then type CONTINUE or STOP: "
                ).strip().lower()
                if action != "continue":
                    print(summary(read_rows(ledger)))
                    print("SESSION_STOPPED_SAFELY")
                    return 0
                print()

            print(
                f"Attempt {next_attempt}; planned {entry['plan_id']}; "
                f"valid target {valid_before + valid_this_run + 1}/30"
            )
            print(instruction(entry))
            confirmation = input(
                f"Type {entry['presentation'].upper()} when ready, or SKIP: "
            ).strip().lower()
            if confirmation == "skip":
                print("Skipped; nothing recorded.\n")
                continue
            if confirmation != entry["presentation"]:
                print("Confirmation did not match; nothing recorded.\n")
                continue

            process = subprocess.run(
                ["fprintd-verify", "-f", entry["target"]],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                check=False,
            )
            if "verify-no-match (done)" in process.stdout:
                observed, protocol_error = "no-match", "no"
            elif "verify-match (done)" in process.stdout:
                observed, protocol_error = "match", "no"
            else:
                observed, protocol_error = "error", "yes"
            print(f"VERIFY_RESULT: observed={observed} exit={process.returncode}")

            exact = input(
                "Was only the requested finger presented exactly once? [y/N]: "
            ).strip().lower()
            cohort = entry["cohort"] if exact == "y" else "excluded"
            notes = "one presentation" if exact == "y" else "presentation not confirmed"
            recovery = "no"
            if protocol_error == "yes":
                recovery = (
                    "yes" if input("Was recovery required? [y/N]: ").strip().lower() == "y"
                    else "no"
                )

            append_row(ledger, {
                "attempt": str(next_attempt), "date": date.today().isoformat(),
                "plan_id": entry["plan_id"], "cohort": cohort,
                "target": entry["target"], "presentation": entry["presentation"],
                "condition": entry["condition"], "expected": entry["expected"],
                "observed": observed, "protocol_error": protocol_error,
                "recovery": recovery, "notes": notes,
            })
            next_attempt += 1
            if cohort in {"genuine", "different-finger"}:
                valid_this_run += 1
            print(
                f"RECORDED: expected={entry['expected']} observed={observed} "
                f"cohort={cohort}\n"
            )
    except KeyboardInterrupt:
        print("\nSESSION_STOPPED_SAFELY")
        return 130

    current = read_rows(ledger)
    print(summary(current))
    if not remaining(current):
        print("REBASE_SMOKE_COMPLETE")
    else:
        print("SESSION_COMPLETE: rerun to continue remaining planned trials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
