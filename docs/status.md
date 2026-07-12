# Research status

Updated: 2026-07-12

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
- Structured pilot complete: 60 valid trials plus 2 excluded attempts; genuine
  `22/30` accepted and different-finger `30/30` rejected.
- Observed false accepts, protocol errors, and required recoveries: `0`.
- Harness teardown bug: fixed and validated.
- Stock-versus-patched A/B: stock exposed no reader; patched package restored
  the reader, existing enrollment, verification, and KDE unlock.
- linux-hardware.org historical record: no kernel/additional-package driver and
  all 104 listed computer records (107 probes) marked failed when checked.
- [GitHub Release v1.94.10.fpcmoh.10.gaf647965-2](https://github.com/NONAN23x/fpcmoh-linux/releases/tag/v1.94.10.fpcmoh.10.gaf647965-2):
  published with checksums and provenance attestation.

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
- Suspend/resume: KDE unlock passed, but one later verification attempt failed
  with `Cannot run while suspended`; restarting fprintd restored operation.
- KDE lock-screen unlock: passed; enrolled finger accepted, other fingers rejected.
- PAM files changed by project: none.
- Existing KDE vendor policy: `/usr/lib/pam.d/kde-fingerprint` uses `pam_fprintd`.
- Reboot persistence and password fallback: passed.
- SDDM fingerprint login: not configured; KDE lock-screen unlock works.
- Investigate and reproduce the suspend-state failure with focused logs; do not
  treat the daemon restart as a driver fix.
- No more accuracy trials are planned without a new, approved question.
- Keep official `libfprint` as rollback.
