# AGENTS.md

## Objective

Ethically develop reproducible Linux support for the user's Mi NoteBook Ultra
fingerprint reader: `10a5:9200 FPC FPC Sensor Controller`. Prefer reviewable
upstream libfprint work. Do not expose biometric data or weaken other systems.

## User-operated changes

Stop, explain one exact command and expected output, then wait for the user to
run it whenever an operation is interactive, privileged, or changes host/device
state. This includes:

- `pacman`, `yay`, `paru`, `sudo`, `doas`, package or local-driver changes;
- state-changing `systemctl`, module, udev, ACL, permission, group, or USB-reset
  commands;
- USB claims/transfers, capture, enrollment, verification, template deletion;
- usbmon/Wireshark capture, VM passthrough, Windows registry/debugger work;
- firmware, BIOS, PAM, login, lock-screen, `sudo`, or disk-unlock changes.

Never execute these through tools or elevation prompts. Read-only commands that
hit permission barriers must also be handed to the user.

## External-code gate

Before checkout, build, run, install, or test an external driver/fork/patch/MR,
present and obtain approval for:

1. URL and exact branch/commit;
2. upstream/review status;
3. experiment and success/failure evidence;
4. dependencies and disk/state effects;
5. biometric/device/authentication risks;
6. rollback or cleanup.

Public metadata/source review needs no approval. Do not silently cross from
research into build, device access, or execution.

## Allowed workspace work

Without another approval, read files/docs, run non-package-manager read-only
inventory, inspect existing logs, edit workspace docs/parsers/fixtures/scripts,
and statically analyze approved or user-supplied source.

## Research phases

Complete and report each phase before the next experiment:

1. **Inventory:** DMI, OS/kernel, VID:PID/revision, interfaces/endpoints/binding,
   libfprint/fprintd, baseline failure. Redact serials.
2. **Existing support:** supported-device list, issues/MRs, forks/vendors;
   evaluate provenance, maintenance, license, dependencies, protocol and safety.
3. **Experiment:** ask one question; define evidence and rollback; get approval.
4. **Windows oracle, only if needed:** hash package; prefer VM passthrough plus
   host usbmon; identify DriverStore/UMDF/kernel components; do not redistribute.
5. **Protocol:** document requests, endpoints, framing, checksums, states/errors;
   separate TLS, key derivation and images. Never assume Neodyme/Goodix behavior
   applies to FPC1022.
6. **PoC:** offline parsing/synthetic fixtures, then one approved live operation,
   then libfprint integration after repeatability.
7. **Authentication:** keep research separate from PAM. Evaluate genuine and
   impostor trials, replay, spoof/liveness, suspend and reboot before deployment.

## Sensitive data

- Never print raw images, templates, keys, or full serials in chat/normal logs.
- Keep captures, images, templates, Windows binaries, secrets, debugger logs and
  core dumps under ignored `artifacts/private/` paths.
- Publish only sanitized metadata, protocol notes, synthetic fixtures, hashes,
  and non-proprietary code.
- Before publication, audit tracked/ignored files for captures, templates, keys,
  archives, DLLs, serials and private paths.
- Never replace/flush a PSK without an approved backup and tested recovery.

## Evidence and iteration

Keep the experiment log chronological with date, hypothesis, approved command,
environment, result, artifacts and decision. Pin URLs/commits; ignore builds and
private captures; prefer offline regression fixtures; change one variable per
experiment; preserve failures; do not blindly retry device commands.

## Tool priorities

- Visual audit: Chrome skill, browser connector, Computer Use.
- GitHub: `git`, `gh`, GitHub connector. Commit/push/PR only when requested.

## Current posture

`10a5:9200` support remains experimental until upstream review, reproducibility
and larger biometric/security testing. Successful enrollment and KDE unlock are
not production-readiness evidence.
