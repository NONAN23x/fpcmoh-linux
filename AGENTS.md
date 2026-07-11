# AGENTS.md

## Scope and objective

These instructions apply to the entire workspace.

The project concerns ethical interoperability research on hardware owned by the
user: the fingerprint reader in a Mi NoteBook Ultra. The confirmed USB device is
`10a5:9200 FPC FPC Sensor Controller`. Work should aim for a reproducible,
reviewable Linux implementation, preferably suitable for upstream libfprint,
without weakening unrelated systems or exposing biometric data.

## User controls interactive and state-changing operations

The agent must stop, explain the proposed operation, provide the exact command,
and wait for the user to run it and return the output before continuing whenever
an operation is interactive, privileged, or changes host/device state.

This rule includes, but is not limited to:

- every `pacman`, `yay`, or `paru` command, including package queries;
- `sudo`, `doas`, authentication prompts, and privilege escalation;
- package installation, removal, upgrade, or dependency resolution;
- `systemctl` operations that start, stop, restart, enable, or disable services;
- loading or unloading kernel modules, including `modprobe usbmon`;
- udev rule changes, permission changes, group membership changes, and USB reset;
- commands that claim, detach, reconfigure, write to, or send control/bulk
  transfers to the fingerprint reader;
- Wireshark/usbmon capture, VM USB passthrough, Windows registry changes,
  debugger attachment, firmware operations, and BIOS changes;
- installing a locally built library or driver;
- deleting enrollment records or biometric templates.

Do not attempt these commands through an execution tool or an elevation prompt.
Give the user one small, auditable step at a time, state what output is expected,
and wait for the result before taking the next step.

## Consultation gate for external code and experiments

Before checking out, building, running, installing, or testing an external
driver, fork, patch, pull request, or merge request, the agent must present:

1. the source URL and exact branch/commit;
2. its current upstream/review status;
3. what the experiment will do;
4. required dependencies and expected disk/state changes;
5. biometric, device, and authentication risks;
6. a rollback or cleanup path.

Wait for explicit user approval before proceeding. A build is subject to this
gate even if it is non-interactive, unprivileged, and confined to `/tmp`.

Browsing source code, reading public metadata, and explaining a candidate are
allowed without approval. Do not silently move from research into checkout,
build, device access, or execution.

## Operations allowed without an additional approval

Within the user's stated task, the agent may:

- read workspace files and public documentation;
- run non-interactive, read-only inventory commands that do not use package
  managers or access biometric contents;
- inspect already available logs and metadata;
- create or edit documentation, manifests, parsers, test fixtures, and scripts
  inside this workspace;
- perform static analysis on source already approved or supplied by the user.

If a supposedly read-only operation encounters an access restriction, stop and
ask the user to run the smallest appropriate command. Do not escalate it.

## Required research sequence

Use explicit phase gates. Complete and report one phase before proposing the
next experiment.

1. **Inventory**
   - Record laptop/DMI, kernel, distribution, exact USB VID:PID, revision,
     interfaces, endpoints, current kernel binding, libfprint/fprintd versions,
     and the observed baseline failure.
   - Redact device serial numbers from publishable artifacts.

2. **Existing-support research**
   - Check the current upstream libfprint supported-device list.
   - Check open/closed issues and merge requests for the exact VID:PID.
   - Evaluate forks and vendor offerings for provenance, maintenance, license,
     review state, dependencies, protocol coverage, and authentication safety.
   - Prefer upstream work over a new implementation when technically sound.

3. **Experiment proposal**
   - Present the smallest experiment that answers one question.
   - Define success/failure evidence and rollback before running it.
   - Obtain user approval under the consultation gate.

4. **Known-good Windows observation, if still needed**
   - Preserve the Windows driver package metadata and hashes before analysis.
   - Prefer a Windows VM with explicit USB passthrough and host-side usbmon
     capture so initialization traffic is visible.
   - Locate the exact DriverStore package and determine whether the vendor code
     is UMDF/user-mode or kernel-mode.
   - Correlate driver logs/debug traces with USB packet timing.
   - Do not redistribute proprietary Windows binaries.

5. **Protocol characterization**
   - Document control requests, endpoint direction, message framing, lengths,
     checksums, state transitions, and error behavior before replaying traffic.
   - Build a small Wireshark Lua dissector or offline parser for rapid iteration.
   - Treat TLS records, key derivation, and image encoding as separate layers.
   - Never assume the Goodix protocol, PSK lifecycle, TLS role, or commands from
     the Neodyme article are identical to this FPC1022 device.

6. **PoC before integration**
   - First prove safe enumeration and parsing with recorded/offline data.
   - Then, with approval, prove one narrowly scoped live operation.
   - Only after protocol behavior is repeatable should work move into libfprint.

7. **Authentication evaluation**
   - Keep research verification separate from PAM, login, lock-screen, `sudo`,
     and disk-unlock integration.
   - Do not recommend authentication use until genuine/impostor testing is large
     enough to evaluate false accepts, false rejects, replay resistance, and
     spoof/liveness limitations.

## Biometric and secret-data handling

Fingerprint images and templates are sensitive personal data.

- Never print raw fingerprint bytes, images, templates, keys, or full device
  serials into chat or normal logs.
- Store captures, raw images, templates, Windows binaries, extracted secrets,
  and debugger logs only under a clearly private ignored path such as
  `artifacts/private/`.
- Publish only sanitized metadata, protocol descriptions, synthetic fixtures,
  hashes, and code that contains no biometric material or proprietary binaries.
- Before any commit or publication, inspect tracked files and ignored-file rules
  specifically for `*.pcap`, `*.pcapng`, `*.raw`, `*.bin`, templates, keys,
  driver packages, DLLs, and serial numbers.
- Never overwrite or rotate a device PSK/key without a user-approved backup and
  a tested recovery path.

## Iteration and evidence

- Keep an append-only experiment log with date, hypothesis, exact approved
  command, environment, result, artifacts, and next decision.
- Pin external source URLs and commit hashes.
- Keep generated build trees and private captures out of version control.
- Prefer offline parsers and recorded synthetic fixtures for regression tests.
- Make one protocol change per experiment so results remain attributable.
- Record failures as evidence; do not repeatedly retry device commands blindly.

## Visual audit priority

When a visual audit is required, use this order:

1. Chrome skill
2. Browser connector
3. Computer Use skill

## GitHub workflow priority

Assume GitHub configuration exists but request user approval/elevation when
access requires it. Use this order:

1. `git` command
2. `gh` command
3. GitHub connector skill

Do not commit, push, open a PR, or publish artifacts unless the user explicitly
requests that action.

## Current safety posture

The existing `10a5:9200` libfprint work is experimental until upstream review,
local reproducibility, and biometric error-rate testing establish otherwise.
Do not enable it for PAM/login/unlock merely because enumeration, enrollment,
or a small number of verification attempts succeeds.
