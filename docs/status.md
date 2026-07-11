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
- Genuine tests: `5/5` accepted.
- Different-finger tests: `5/5` rejected.
- Protocol errors: `0`.
- Harness teardown bug: fixed and validated.

## State

- System libfprint: stock.
- fprintd: inactive; no stored prints observed.
- PAM: unchanged; `pam_fprintd` not configured.
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
- Reboot/login/password-fallback tests: pending.
- Test fprintd without PAM.
- Keep official `libfprint` as rollback.
