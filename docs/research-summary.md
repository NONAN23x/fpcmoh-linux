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
- Genuine research trials: 5/5 accepted.
- Different-finger research trials: 5/5 rejected.
- fprintd enroll/list/verify: passed.
- Suspend/resume and KDE lock-screen unlock: passed.
- Driver/service errors in the final pilot: 0.

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
- Reboot/login-screen behavior is not yet documented here.
- OpenCV 5 package linkage is larger than ideal.

## Safety

No firmware update, PSK replacement, device-template storage, or disk-unlock
integration was performed. Proprietary binaries and biometric artifacts are
not published.
