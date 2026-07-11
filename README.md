# FPC MOH Linux research

Experimental Linux interoperability work for FPC Disum match-on-host
fingerprint sensors, focused on USB device `10a5:9200` in the Mi NoteBook
Ultra.

> [!WARNING]
> This driver is not merged upstream. Do not enable fingerprint authentication
> without preserving password access and a tested package rollback.

## Verified result

- Hardware: FPC `10a5:9200`, firmware `11.26.1.44`.
- Driver base: libfprint MR
  [!570](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/570).
- Pinned commit: `af647965253bfcf283474bf6a9dd486f1df553eb`.
- TLS-PSK open/close and native image capture: passed.
- Five-stage match-on-host enrollment: passed.
- Research pilot: 5/5 genuine accepts and 5/5 different-finger rejects.
- fprintd enrollment and verification: passed.
- KDE lock-screen unlock after suspend: passed.

These small tests demonstrate interoperability, not production biometric error
rates or spoof resistance.

## Repository layout

- `docs/` — sanitized hardware inventory and research results.
- `patches/` — OpenCV 5 and device-table corrections for the pinned MR.
- `packaging/libfprint-fpcmoh/` — reproducible Arch package recipe.
- `tools/` — narrow open/close, capture, and offline SIGFM research tools.
- [`CREDITS.md`](CREDITS.md) — upstream authorship and project provenance.
- `.github/workflows/` — pinned package build/release and upstream monitoring.
- `AGENTS.md` — safety and experiment rules.

The [stock-versus-patched A/B report](docs/ab-test.md) isolates the functional
difference to the patched libfprint package while preserving the same fprintd
enrollment and system configuration.

## Reliability pilot

`tools/reliability-pilot.py` is an interactive aggregate-only runner for sparse
genuine and different-finger trials. It does not enroll, delete templates, edit
PAM, or store fprintd output. Review the next planned trials without touching the
sensor:

```bash
python3 tools/reliability-pilot.py --plan --count 5
```

Run live trials only after reviewing the safety boundary and ensuring password
fallback. Use small sessions separated by normal laptop use:

```bash
python3 tools/reliability-pilot.py --count 1
```

The default ledger is ignored under `artifacts/private/` and contains only
finger labels, placement categories, expected/observed outcomes, and error flags.

## Maintenance and releases

See [package maintenance](docs/maintenance.md) for upstream-update handling,
manual porting gates, GitHub Actions artifacts, tagged Releases, checksums, and
provenance attestations. The workflow never auto-updates the pinned driver.

Fingerprint authentication for sudo has material security and usability risks.
Read the [sudo PAM design and warning](docs/pam-sudo.md) before considering any
host change; this repository does not modify PAM automatically.

## Arch package

Review the source pin, checksums, patches, and
[`PKGBUILD`](packaging/libfprint-fpcmoh/PKGBUILD) before building:

```bash
cd packaging/libfprint-fpcmoh
makepkg
```

The package conflicts with stock `libfprint`. Installation is intentionally
not automated. See the [package notes](packaging/libfprint-fpcmoh/README.md)
for scope and rollback requirements.

## Privacy boundary

The repository excludes fingerprint images, templates, packet captures,
device secrets, core dumps, proprietary Windows binaries, local build trees,
and machine-specific experiment logs. Do not attach such artifacts to issues or
commits.

## Upstream status

MR !570 remains experimental and needs rebase/review. The preferred long-term
outcome is a reviewed upstream libfprint driver, not a permanent downstream
package.

## License

LGPL-2.1-or-later. See [`LICENSE`](LICENSE).
