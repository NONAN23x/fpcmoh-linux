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
- Hardware-tested commit: `af647965253bfcf283474bf6a9dd486f1df553eb`.
- Rebase candidate: `ba10c9398fe4542ff6403549884d0c8687182845`;
  offline tests and a post-reboot two-template smoke test passed.
- TLS-PSK open/close and native image capture: passed.
- Five-stage match-on-host enrollment: passed.
- Structured reliability pilot: 22/30 genuine matches and 30/30
  different-finger rejections; no observed false accepts or protocol errors.
- Rebase smoke test: 12/15 genuine matches and 15/15 different-finger
  rejections; no protocol errors or required recovery.
- fprintd enrollment and verification: passed.
- KDE lock-screen unlock after suspend: passed.

These small tests demonstrate interoperability, not production biometric error
rates or spoof resistance.

## Repository layout

- `docs/` — sanitized hardware inventory and research results.
- `packaging/libfprint-fpcmoh/` — reproducible Arch package recipe.
- `tools/` — narrow open/close, capture, and offline SIGFM research tools.
- [`CREDITS.md`](CREDITS.md) — upstream authorship and project provenance.
- `.github/workflows/` — pinned package build/release and upstream monitoring.
- `AGENTS.md` — safety and experiment rules.

The [stock-versus-patched A/B report](docs/ab-test.md) isolates the functional
difference to the patched libfprint package while preserving the same fprintd
enrollment and system configuration.

The [rebase audit](docs/rebase-ba10c939-audit.md) records the unmodified MR
candidate build, package inspection, and remaining `--werror` failure.

## Reliability pilot

`tools/reliability-pilot.py` is an interactive aggregate-only runner for sparse
genuine and different-finger trials. The initial 30/30 pilot is complete: it
recorded 22/30 genuine matches and 30/30 different-finger rejections, with two
excluded attempts and no protocol errors or required recovery. It does not
enroll, delete templates, edit PAM, or store fprintd output.

```bash
python3 tools/reliability-pilot.py --plan
```

The default ledger is ignored under `artifacts/private/` and contains only
finger labels, placement categories, expected/observed outcomes, and error flags.

`tools/rebase-smoke-30.py` is the resumable post-reboot check for MR !570 commit
`ba10c939`. It explicitly selects the right-index or left-middle template for
15 genuine and 15 different-finger trials, and pauses after every five valid
trials to reduce rapid-scan failures.

```bash
python3 tools/rebase-smoke-30.py --plan
```

The pilot is too small for FAR/FRR, liveness, or spoof-resistance claims. It
does show placement sensitivity: centered placement was 6/6, while clockwise
rotation was 1/5.

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

MR !570 remains experimental and needs upstream review. The preferred long-term
outcome is a reviewed upstream libfprint driver, not a permanent downstream
package.

## License

LGPL-2.1-or-later. See [`LICENSE`](LICENSE).
