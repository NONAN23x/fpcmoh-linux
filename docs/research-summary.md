# Research summary

Updated: 2026-07-11

## Target

- Laptop: Mi NoteBook Ultra.
- Sensor: FPC Disum/FPC1022 family.
- USB ID: `10a5:9200`.
- Firmware: `11.26.1.44`.
- Linux base: libfprint MR `!570`, commit
  `af647965253bfcf283474bf6a9dd486f1df553eb`.

## Results

- USB inventory and Xiaomi Windows-package analysis: complete.
- TLS-PSK session establishment: passed.
- Native 112x88 capture and 2x scaling: passed.
- SIGFM extraction/matching: passed.
- Five-stage host template enrollment: passed.
- Initial live pilot: 5/5 genuine accepted and 5/5 different-finger rejected.
- Structured pilot so far: 41 valid trials; 13/21 genuine accepted and 20/20
  different-finger rejected. Centered placement is reliable; rotation, light
  pressure, rapid scanning, and sensor cleanliness reduce capture reliability.
- fprintd enroll/list/verify: passed.
- Suspend/resume, reboot persistence, and KDE lock-screen unlock: passed.
- Stock-versus-patched A/B: stock listed no device; the patched package restored
  the reader, preserved enrollment, and working KDE unlock.
- Protocol crashes, daemon failures, and required recoveries: 0.

## Historical support evidence

The [linux-hardware.org `10a5:9200` record](https://linux-hardware.org/?id=usb:10a5-9200)
reported no kernel driver through Linux 7.0, no known additional-package driver,
and all 104 listed computer records (107 probes) as failed when checked on
2026-07-11. This corroborates the released-support gap; the local A/B test is
the direct proof for this machine.

## Integration finding

KDE already ships a separate vendor PAM service at
`/usr/lib/pam.d/kde-fingerprint`. No project PAM edit was needed. Once fprintd
could access the supported sensor and had an enrolled print, KScreenLocker used
the existing fingerprint authentication path while password authentication
remained available.

## Known limitations

- MR !570 is open, conflicted, and not production-ready.
- The sample count is too small for FAR/FRR claims.
- Liveness and spoof resistance were not evaluated.
- SDDM does not currently offer fingerprint login; KDE session unlock does.
- OpenCV 5 package linkage is larger than ideal.

## Safety

No firmware update, PSK replacement, device-template storage, or disk-unlock
integration was performed. Proprietary binaries and biometric artifacts are
not published.
