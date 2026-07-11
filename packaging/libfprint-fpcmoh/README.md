# libfprint-fpcmoh package

- Source: libfprint MR `!570`.
- Commit: `af647965253bfcf283474bf6a9dd486f1df553eb`.
- Source archive SHA-256: `513bc41c95b6d086e8a44c959d0ebe7df80e49544432a62d8c0da9a9467fde4a`.
- Status: experimental; open, conflicted, needs rebase.
- Target: FPC `10a5:9200` and `10a5:9201`.
- Action: replaces `libfprint`; preserves ABI `libfprint-2.so.2`.
- Added dependency: `opencv`.
- API HTML docs: disabled; gtk-doc breaks on whitespace paths and is not runtime data.
- PAM changes: none.
- Valid package revision: `pkgrel=2` or newer.
- Rejected package: `pkgrel=1`; it contains stale hwdb data.

Build only after review. Do not use `--install`.

```bash
makepkg
```

Installation requires a later reviewed `sudo pacman -U` command.
Rollback is the official signed Arch `libfprint` package.
