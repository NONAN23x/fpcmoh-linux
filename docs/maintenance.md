# Package maintenance and releases

## What happens when official libfprint updates

`libfprint-fpcmoh` is a different package name that provides and conflicts with
`libfprint`. A normal system upgrade therefore does not usually replace it with
the official package. This avoids silently losing device support, but also means
the pinned package can miss upstream security, ABI, dependency, and compatibility
fixes. Treat every official update as a review signal.

The weekly `Watch upstream libfprint` workflow compares:

- the official Arch libfprint version;
- MR !570's head commit, state, and merge status;
- the commit pinned in the PKGBUILD.

It opens one maintenance issue when a recorded signal changes. It never modifies
the PKGBUILD or publishes a package automatically.

## Updating the package safely

1. Check whether `10a5:9200` has entered an official libfprint release. If so,
   A/B test the signed stock package and retire the downstream build if it works.
2. If support remains unmerged, review the new MR !570 head or rebase its FPC
   driver and SIGFM dependency onto the target libfprint release.
3. Update `_commit`, `pkgver`, source SHA-256, and `pkgrel` in the PKGBUILD.
4. Reapply only patches that are still necessary. A patch failing to apply is a
   review event, not permission to bypass it.
5. Build in isolation; run Meson, SIGFM, hwdb, metadata, ABI, dependency, and
   privacy checks.
6. Inspect the package archive and preserve both the installed working package
   and an official signed rollback package.
7. Run the minimum live regression sequence: discovery/open/close, one genuine
   verification, one different-finger control, suspend/resume, then reboot.
8. Only after those gates pass should the updated package replace the working
   installation.

## GitHub Actions package workflow

`Build Arch package` has two activation paths:

- manual dispatch: builds, tests, attests, and stores a workflow artifact;
- a `v*` tag: performs the same build and creates a GitHub Release.

The job builds as an unprivileged user inside an ephemeral Arch container. It
installs build dependencies only in that container, runs the PKGBUILD test suite,
checks expected library/hwdb paths, produces `SHA256SUMS`, and creates a GitHub
artifact-provenance attestation.

Release packages are experimental and unsigned. A checksum and GitHub
attestation improve integrity and provenance, but they are not substitutes for
an Arch packager signature or local review. Arch is rolling, so dependency
versions in future runner images can also change the resulting binary.

Create a release only after a successful manual run and reviewed version bump:

```bash
git tag -s v<version> -m "libfprint-fpcmoh v<version>"
git push origin v<version>
```

Tagging is an external publication action and should be performed deliberately.
