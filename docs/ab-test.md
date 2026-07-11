# Stock-versus-patched libfprint A/B test

Test date: 2026-07-11

## Question

Does fingerprint functionality on this Mi NoteBook Ultra come specifically
from the patched libfprint package, rather than an unrelated system change?

## Controlled state

The same laptop, sensor, firmware, fprintd installation, KDE session, PAM
configuration, password fallback, and stored right-index enrollment were used
throughout. Only the pacman-owned libfprint implementation changed.

| Phase | Installed package | Result |
|---|---|---|
| A: official stock | `libfprint 1.94.10-2.1` | Package integrity passed; `fprintd-list` reported `No devices available` |
| B: patched restore | `libfprint-fpcmoh 1.94.10.fpcmoh.10.gaf647965-2` | Reader and existing right-index enrollment returned; verification and KDE unlock passed |

Patched package SHA-256:

```text
d717ffe4bb8343265e1c27a39ea4d1e434d70313213780176d2675fee1a39eef
```

## Procedure

1. Preserve password access and the existing fprintd enrollment.
2. Stop fprintd and replace `libfprint-fpcmoh` with the official signed stock
   package through pacman.
3. Verify stock-package integrity and query the current user's fprintd devices.
4. Stop fprintd and reinstall the exact inspected pkgrel-2 archive.
5. Verify patched-package integrity, list the preserved enrollment, perform one
   genuine verification, and confirm KDE lock-screen unlock.

No template was deleted or recreated. No PAM, firmware, device key, BIOS, or
device-side storage change occurred.

## Conclusion

The official stock library did not expose `10a5:9200` to fprintd. Restoring the
patched library restored the reader and existing authentication state without
any other configuration change. This directly attributes functionality on this
machine to the patched libfprint build containing `fpcmoh` and SIGFM support.

The result proves interoperability on this system. It does not establish
production biometric accuracy, spoof resistance, or upstream readiness.

## Supporting context

The [linux-hardware.org record](https://linux-hardware.org/?id=usb:10a5-9200)
reported no kernel driver through Linux 7.0, no driver in known additional
packages, and every listed computer record as failed when checked. That public
history corroborates the released-support gap; the controlled A/B result above
is the stronger evidence for this exact machine.

Local screenshots were retained outside version control because they expose a
username and full filesystem paths. This report contains the sanitized evidence.
