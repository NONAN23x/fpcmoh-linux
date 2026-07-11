# Optional sudo fingerprint authentication

## Security warning

This integration is optional and is not recommended while the driver remains
experimental. The ArchWiki warns that fingerprint authentication for `sudo`,
`su`, or polkit can permit fingerprint hijacking: another process can initiate
authentication and consume a later fingerprint touch. A fingerprint is also not
a secret and cannot replace full-disk or password security.

`pam_fprintd` serializes authentication. It cannot offer password and fingerprint
input simultaneously; password fallback begins only after the fingerprint module
fails or times out.

## Narrow sudo-only design

Do not add the experimental module to global `system-auth`, login, SSH, `su`, or
polkit. If the risk is explicitly accepted, add this line before sudo's existing
`auth include system-auth` line:

```pam
auth sufficient pam_fprintd.so max-tries=1 timeout=10
```

The existing password stack must remain unchanged beneath it:

```pam
#%PAM-1.0
auth sufficient pam_fprintd.so max-tries=1 timeout=10
auth include system-auth
account include system-auth
session include system-auth
```

The change should be made with `sudoedit`, after creating an exact backup and
keeping an authenticated root shell open in a second terminal. Test both one
fingerprint success and password fallback before closing that recovery shell.

Rollback is restoring the backup of `/etc/pam.d/sudo`. Never test a PAM edit by
locking or rebooting first.

Sources:

- [ArchWiki: fprint](https://wiki.archlinux.org/title/Fprint)
- Local `pam_fprintd(8)` manual, including its serialized-authentication limit
