# MR !570 rebase audit: `ba10c939`

Date: 2026-07-16

## Scope

- Source: libfprint MR !570 commit
  `ba10c9398fe4542ff6403549884d0c8687182845`.
- Source archive SHA-256:
  `77021ac01625cfecba2187d67ab61ad0a23277eebbea41d009df914af6f760e9`.
- No downstream source patches were applied.
- The offline audit itself performed no package installation, device access,
  enrollment, verification, PAM change, or biometric-data operation. Later
  user-operated live results are recorded separately below.

## Static findings

- The prior OpenCV 5 fallback and supported-device table corrections are present
  in the MR and the local patches are no longer needed.
- TLS PSK decryption now writes into a bounded intermediate buffer before copying
  the validated result into the fixed 32-byte destination.
- Packet offset/length validation avoids wrapping additions by comparing lengths
  against the remaining packet space.

## Build result

- Package: `libfprint-fpcmoh 1.94.10.fpcmoh.10.gba10c939-1`.
- Package SHA-256:
  `118b3568b8a66aeb10a714a4ef9ceb8ceab782d10207a8b0202f2e68fe652441`.
- OpenCV 5.0.0 was selected after the OpenCV 4 probe failed.
- Meson tests: 122 passed, 0 failed.
- SIGFM: 8/8 cases and 24/24 assertions passed.
- Package metadata, ABI library, generated hwdb, metainfo, and OpenCV/OpenSSL
  linkage were inspected.

## Initial live result

- Candidate installed successfully; installed library matched the inspected
  package payload.
- fprintd restarted with `LimitCORE=0`, discovered the FPC MOH device, preserved
  the existing right-index enrollment, and returned `verify-match` for one
  genuine presentation.
- No daemon, protocol, or USB error appeared in the checked service journal.
- Different-finger, enrollment, suspend/resume, and reboot checks remain.

## Extended live result

- New left-middle enrollment and direct verification passed.
- Right index presented against the selected left-middle template returned
  `verify-no-match`, as expected for template-specific verification.
- KDE lock-screen unlock accepted both enrolled fingers.
- A resumable post-reboot smoke test recorded 12/15 genuine matches and 15/15
  different-finger rejections, with 0 protocol errors and 0 recoveries.
- The three genuine misses were placement variants; no false accept was observed.

## Remaining build finding

A separate build using `meson setup --werror -Ddrivers=all` fails while compiling
`libfprint/sigfm/tests.cpp` on GCC 16 with OpenCV 5. The failures are warnings
promoted to errors from OpenCV umbrella-header diagnostics plus a missing prior
declaration for the test-local `cv::operator==`. The normal Arch package build
and its test suite pass. This finding is preserved without a downstream fix in
the [separate `--werror` note](rebase-ba10c939-werror.md).
