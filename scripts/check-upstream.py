#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compare recorded libfprint state with official Arch and GitLab metadata."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "packaging/upstream-baseline.json"
PKGBUILD_PATH = ROOT / "packaging/libfprint-fpcmoh/PKGBUILD"
ARCH_URL = "https://archlinux.org/packages/extra/x86_64/libfprint/json/"
MR_URL = (
    "https://gitlab.freedesktop.org/api/v4/projects/"
    "libfprint%2Flibfprint/merge_requests/570"
)


def fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "fpcmoh-linux-upstream-watch"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def pinned_commit() -> str:
    match = re.search(
        r"^_commit=([0-9a-f]{40})$",
        PKGBUILD_PATH.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError("could not read _commit from PKGBUILD")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--report", type=Path, default=Path("upstream-report.md"))
    args = parser.parse_args()

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    arch = fetch_json(ARCH_URL)
    mr = fetch_json(MR_URL)
    current = {
        "arch_version": f"{arch['pkgver']}-{arch['pkgrel']}",
        "mr_570_sha": mr["sha"],
        "mr_570_state": mr["state"],
        "mr_570_detailed_merge_status": mr["detailed_merge_status"],
    }
    local_pin = pinned_commit()
    changes = [key for key, value in current.items() if baseline.get(key) != value]
    if local_pin != baseline["mr_570_sha"]:
        changes.append("local_pkgbuild_pin")

    checked = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Upstream libfprint maintenance report",
        "",
        f"Checked: `{checked}`",
        "",
        "| Signal | Recorded baseline | Current |",
        "|---|---|---|",
        f"| Official Arch libfprint | `{baseline['arch_version']}` | `{current['arch_version']}` |",
        f"| MR !570 commit | `{baseline['mr_570_sha']}` | `{current['mr_570_sha']}` |",
        f"| MR !570 state | `{baseline['mr_570_state']}` | `{current['mr_570_state']}` |",
        "| MR !570 merge status | "
        f"`{baseline['mr_570_detailed_merge_status']}` | "
        f"`{current['mr_570_detailed_merge_status']}` |",
        f"| Local PKGBUILD pin | `{baseline['mr_570_sha']}` | `{local_pin}` |",
        "",
    ]
    if changes:
        lines.extend([
            "Changes detected: " + ", ".join(f"`{item}`" for item in changes),
            "",
            "Do not auto-bump the package. Review upstream changes, determine whether "
            "FPC support has merged, reapply only still-needed patches, rebuild and test "
            "offline, and preserve a working rollback before installation.",
        ])
    else:
        lines.append("No recorded upstream signal changed.")

    report = "\n".join(lines) + "\n"
    args.report.write_text(report, encoding="utf-8")
    if args.summary:
        args.summary.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    if args.github_output:
        args.github_output.write_text(
            f"changed={'true' if changes else 'false'}\n"
            f"report_path={args.report.resolve()}\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
