# MR !570 `ba10c939`: OpenCV 5 `--werror` note

Date: 2026-07-16

## Scope

This records a build-only finding from unmodified MR !570 commit
`ba10c9398fe4542ff6403549884d0c8687182845`. No downstream fix was applied.

## Reproduction

From an exact checkout of the commit on GCC 16.1.1 with OpenCV 5.0.0:

```bash
meson setup build-werror . --werror -Ddrivers=all -Ddoc=false -Dinstalled-tests=false
meson compile -C build-werror
```

## Result

Compilation reaches `libfprint/sigfm/tests.cpp` and fails because warnings are
promoted to errors:

- OpenCV's umbrella header reaches `photo/ccm.hpp`, which emits
  `-Werror=comment` diagnostics for multiline comments;
- `flann/logger.h` emits `-Werror=suggest-attribute=format`;
- the test-local `cv::operator==` has no prior declaration and emits
  `-Werror=missing-declarations`.

The normal Arch package build is unaffected: it compiled successfully, all 122
Meson tests passed, and all 8 SIGFM cases/24 assertions passed. This note is for
the next upstream report and does not claim a runtime defect.
