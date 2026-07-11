# Research status

Updated: 2026-07-11

## Target

- Hardware: Mi NoteBook Ultra, FPC `10a5:9200`.
- Firmware: `11.26.1.44`.
- Driver: libfprint MR `!570`.
- Commit: `af647965253bfcf283474bf6a9dd486f1df553eb`.
- Upstream: open, conflicted, needs rebase.

## Achieved

- Inventory and Windows-driver analysis complete.
- TLS-PSK open/close and native capture complete.
- SIGFM offline scoring complete.
- Five-stage host enrollment complete.
- Private template round-trip validation complete.
- Initial pilot: `5/5` genuine accepted and `5/5` different-finger rejected.
- Structured pilot: 41/60 valid trials complete; genuine `13/21` accepted,
  different-finger `20/20` rejected.
- Protocol errors: `0`.
- Harness teardown bug: fixed and validated.
- Stock-versus-patched A/B: stock exposed no reader; patched package restored
  the reader, existing enrollment, verification, and KDE unlock.
- linux-hardware.org historical record: no kernel/additional-package driver and
  all 104 listed computer records (107 probes) marked failed when checked.

## State

- System libfprint: `libfprint-fpcmoh 1.94.10.fpcmoh.10.gaf647965-2`.
- fprintd: D-Bus activated; one preserved right-index enrollment.
- Project PAM changes: none; existing KDE vendor fingerprint policy is active.
- Readiness: research-only, not production-qualified.

## Next

- Package pkgrel 2: built and inspected; SHA-256 pinned in experiment log.
- Package pkgrel 1: rejected; stale hwdb; must not be installed.
- Package pkgrel 2: installed; byte match and linkage verified.
- fprintd enrollment: right index completed.
- fprintd genuine verification: passed.
- fprintd different-finger rejection: passed.
- Suspend/resume: passed.
- KDE lock-screen unlock: passed; enrolled finger accepted, other fingers rejected.
- PAM files changed by project: none.
- Existing KDE vendor policy: `/usr/lib/pam.d/kde-fingerprint` uses `pam_fprintd`.
- Reboot persistence and password fallback: passed.
- SDDM fingerprint login: not configured; KDE lock-screen unlock works.
- Complete remaining 19 sparse reliability trials after cooldown; avoid rapid
  batches and preserve the current enrollment until the pilot finishes.
- Keep official `libfprint` as rollback.
