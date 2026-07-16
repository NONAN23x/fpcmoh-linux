# libfprint-fpcmoh package

- Source: libfprint MR `!570`.
- Commit: `ba10c9398fe4542ff6403549884d0c8687182845`.
- Source archive SHA-256: `77021ac01625cfecba2187d67ab61ad0a23277eebbea41d009df914af6f760e9`.
- Status: experimental; open, conflicted, needs rebase.
- Target: FPC `10a5:9200` and `10a5:9201`.
- Action: replaces `libfprint`; preserves ABI `libfprint-2.so.2`.
- Added dependency: `opencv`.
- API HTML docs: disabled; gtk-doc breaks on whitespace paths and is not runtime data.
- PAM changes: none.
- Candidate package: `1.94.10.fpcmoh.10.gba10c939-1`.
- Source patches: none; the MR now contains the prior OpenCV 5 and device-table
  corrections.
- Offline result: Arch package build, 122 Meson tests, and 8 SIGFM tests passed.
- Audit limitation: a separate `meson setup --werror -Ddrivers=all` build fails
  while compiling `libfprint/sigfm/tests.cpp` against OpenCV 5/GCC 16.
- Candidate `1.94.10.fpcmoh.10.gba10c939-1` is installed; initial genuine
  verification passed. The prior `1.94.10.fpcmoh.10.gaf647965-2` package is
  retained for rollback while broader validation continues.

Build only after review. Do not use `--install`.

```bash
makepkg
```

Installation requires a later reviewed `sudo pacman -U` command.
Rollback is the official signed Arch `libfprint` package.
