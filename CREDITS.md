# Credits and provenance

This repository packages, tests, and documents work developed in the upstream
libfprint community. It does not claim authorship of the FPC1022 driver or the
SIGFM algorithm.

## Upstream work

- [libfprint](https://gitlab.freedesktop.org/libfprint/libfprint) — the Linux
  fingerprint-reader library maintained by the libfprint project.
- [MR !570](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/570)
  by [Sergey Subbotin (`@ssubbotin`)](https://gitlab.freedesktop.org/ssubbotin)
  — the `fpcmoh` driver for FPC Disum/FPC1022 `10a5:9200` and `10a5:9201`.
- [MR !530](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/530)
  by [`@Tooniis`](https://gitlab.freedesktop.org/Tooniis) — the maintained and
  rebased SIGFM integration used by small-area sensors.
- [MR !418](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/418)
  by [Natasha England-Elbro (`@0x00002a`)](https://gitlab.freedesktop.org/0x00002a)
  — the original SIGFM integration work from which later revisions derive.

## This downstream repository

The work here adds independent `10a5:9200` hardware validation, an Arch package
recipe, an OpenCV 5 dependency fallback, a supported-device table correction,
narrow research tools, privacy controls, and sanitized interoperability results.

The package recipe fetches the pinned upstream source archive directly from
freedesktop.org. Upstream source and local code are distributed under
LGPL-2.1-or-later; see [`LICENSE`](LICENSE).

## Research references

- [Neodyme: Reversing a Fingerprint Reader Protocol](https://neodyme.io/en/blog/fingerprint_reversing/)
  informed the cautious inventory-first research method. Its Goodix-specific
  protocol details were not assumed to apply to FPC hardware.
- [linux-hardware.org device record](https://linux-hardware.org/?id=usb:10a5-9200)
  provides historical community-probe evidence for the released-support gap.
