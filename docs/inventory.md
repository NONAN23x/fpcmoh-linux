# Mi NoteBook Ultra fingerprint research inventory

Inventory date: 2026-07-10 (Asia/Kolkata)

This is the sanitized baseline for interoperability research on the user's own
hardware. USB device serial numbers and biometric contents are intentionally
excluded.

## Executive identification

| Item | Observed value |
|---|---|
| Laptop vendor | TIMI |
| Laptop model | Mi NoteBook Ultra |
| Mainboard | TIMI TM2017 |
| BIOS | TIMI RMATG5B0P0D0D, dated 2021-07-14 |
| Linux distribution | CachyOS (Arch-compatible rolling distribution) |
| Kernel | `7.1.3-2-cachyos`, x86_64 |
| Fingerprint vendor/product | Fingerprint Cards AB (FPC), `10a5:9200` |
| USB product string | `FPC Sensor Controller` |
| Windows package name | FPC Fingerprint Reader (Disum) |
| Likely sensor family | FPC Disum device based on FPC1022 |
| Current Linux result | MR `!570` completes TLS, capture, five-stage enrollment, template persistence, and live verification on this device |

## Verified achievements

- Device identified: FPC Disum/FPC1022, `10a5:9200`, firmware `11.26.1.44`.
- Native Linux TLS-PSK open/close: passed.
- Native image capture: passed; 112x88 source, 224x176 scaled output.
- SIGFM offline matching: passed; placement sensitivity documented.
- Five-stage host enrollment: passed; private template validated byte-for-byte.
- Live pilot: 5/5 genuine accepts, 5/5 different-finger rejects, 0 protocol errors.
- Structured reliability pilot: 41 valid trials so far; 13/21 genuine accepts,
  20/20 different-finger rejects, and no protocol/daemon failure. Rotation,
  light contact, rapid scanning, and sensor cleanliness affect reliability.
- fprintd enrollment and verification: passed.
- KDE lock-screen unlock after suspend and reboot: passed; no project PAM edit required.
- Stock-versus-patched A/B package test: stock exposed no device; restoring the
  pinned patched package immediately restored the reader, saved enrollment, and
  KDE fingerprint unlock.

## Physical USB inventory

Observed through `lsusb`, `lsusb -t`, the USB descriptors, and the boot kernel
log:

| Property | Value |
|---|---|
| USB VID:PID | `10a5:9200` |
| Device revision (`bcdDevice`) | `1.44` |
| Reported sensor firmware | `11.26.1.44` |
| Declared USB version | USB 1.10 |
| Negotiated link | High Speed, 480 Mbit/s |
| Device class | `0xef` miscellaneous device / interface association |
| Power | Bus-powered, 100 mA maximum |
| Wake capability | Remote wakeup |
| Configuration count | 1 |
| Interface count | 2 |
| Current kernel driver | None for either interface |

### Interface map

| Interface | Class | Endpoints | Evidence-backed role |
|---|---|---|---|
| 0 (`MI_00`) | Vendor-specific (`ff/ff/ff`) | Bulk IN `0x82`, 64-byte max packet | Main biometric/UMDF protocol. Xiaomi's INF binds the FPC biometric driver to `USB\\VID_10A5&PID_9200&MI_00`. |
| 1 (`MI_01`) | Vendor-specific (`ff/ff/ff`) | No non-control endpoints declared | Firmware-update/DFU control path. Xiaomi's firmware INF binds its updater to `USB\\VID_10A5&PID_9200&MI_01`. |

The bus/device numbers observed during inventory were `003/004`; these are
ephemeral and must not be used as stable identifiers in scripts.

## Linux software baseline

| Component | Installed/observed value |
|---|---|
| libfprint | `1.94.10-2.1` |
| fprintd | `1.94.5-2.1` |
| libusb | `1.0.30-1.1` |
| usbutils | `019-1.1` |
| Wireshark CLI/GUI | `4.7.1-1` |
| fprintd unit | Static; inactive before probe and D-Bus activated during probe |
| fprintd discovery | `No devices available` |
| libfprint udev support | No `10a5:9200` match in the installed libfprint rules |
| usbmon | Not loaded when inventoried |

The current upstream libfprint supported-device list also omits `10a5:9200`.
Installing another released fprintd package alone will therefore not add
support; the missing piece is a device driver/protocol implementation.

### Public Linux hardware-probe evidence

The [linux-hardware.org record for `10a5:9200`](https://linux-hardware.org/?id=usb:10a5-9200)
identifies the device as `FPC FPC Sensor Controller`, class `ff-ff-ff`. At the
time checked on 2026-07-11, it stated:

- no driver found in Linux kernel versions through 7.0 according to LKDDb;
- no driver found in its known additional packages;
- 107 probes represented by 104 listed computer records across eight pages;
- every listed computer record marked `failed`.

These community-probe results corroborate the historical lack of released
support, but are not the sole proof: database coverage and status can lag new
out-of-tree work. The controlled local A/B package test below directly verifies
the stock-versus-patched behavior on this exact laptop.

### Controlled stock-versus-patched A/B result

The user preserved password access and the existing fprintd enrollment, then
swapped only the pacman-owned libfprint implementation:

1. With official stock libfprint installed, `fprintd-list` reported no device.
2. The user reinstalled the inspected package
   `libfprint-fpcmoh 1.94.10.fpcmoh.10.gaf647965-2`.
3. fprintd immediately listed the FPC MOH reader and the previously enrolled
   right index; KDE lock/unlock authentication worked again.

No enrollment, PAM, firmware, device key, or fprintd-data change was needed.
This isolates the functional difference to the patched libfprint package and
its `fpcmoh`/SIGFM support.

### Experimental driver live baseline

On 2026-07-10, the user ran the reviewed open/close probe against the isolated
MR `!570` build. It discovered the device as `fpcmoh`, reported five enrollment
stages, initialized `MI_00`, retrieved a 121-byte TLS-key packet, verified its
HMAC, decrypted the existing 32-byte PSK in memory, and negotiated TLS 1.2 with
`PSK-AES128-CBC-SHA256`. The probe then closed and released the device normally.

No finger capture, enrollment, key replacement/flush, storage operation, or
firmware-interface access occurred. The reported firmware `11.26.1.44` also
matches the numeric Windows 10 package release (`011.26.1.044`), further tying
the supplied Xiaomi package to the installed hardware.

A subsequent user-executed single-capture probe succeeded. The driver received
one 112x88 raw grayscale frame and produced the configured 2x nearest-neighbor
224x176 image. The saved PGM is structurally valid and shows clear fingerprint
ridge flow without transport corruption. Its 2x2 pixel duplication reconstructs
exactly to the original after 112x88 downsample and 224x176 nearest-neighbor
upsample, confirming the driver's scaling path.

## User-supplied Xiaomi Windows package

The user placed the package at `FingerPrint.zip` and reports downloading it
from Xiaomi's official download centre. The source page URL is not preserved in
the workspace and should be added later for provenance.

| Property | Value |
|---|---|
| File | `FingerPrint.zip` |
| Size | 21,360,534 bytes |
| SHA-256 | `048460fe4506a18a88e75483a21b09fcf80b4f525f5ad208f69acf939e0c1dfb` |
| Archive type | Unencrypted ZIP, 100 entries |
| Platforms | Separate Windows 10 and Windows 11 trees |
| Vendors bundled | Elan, Goodix, and FPC; installer selects by USB hardware ID |
| Target-selection rule | `USB\\VID_10A5&PID_9200` selects the FPC branch |

The archive has only been listed and streamed for static text/string analysis.
No member has been extracted or executed.

### Driver versions

| Package tree | INF driver version |
|---|---|
| Windows 10 | `011.26.1.044`, dated 2021-03-11 |
| Windows 11 | `011.26.1.054`, dated 2021-10-09 |

The two FPC INF files are semantically identical apart from the version/date.
Their binaries are different builds.

### Windows architecture and component roles

The package uses WinUSB plus User-Mode Driver Framework 2.17 rather than a
vendor kernel USB driver.

| Component | Evidenced role |
|---|---|
| `fpc_disum_um_usb.inf` | Binds `MI_00`, registers UMDF service `FpcG2Usb`, sets exclusive access and power policy, and connects the sensor to Windows Biometric Framework. |
| `x64/fpc_disum.dll` | Main UMDF USB transport/protocol driver. Static strings name USB commands/events and TLS/enclave entry points. |
| `x64/FpcDisumEngine.dll` | Windows Biometric Framework engine adapter: enrollment, template loading/commit, image retrieval, and verification. |
| `x64/fpc_enclave.dll` | TLS session, key sealing/HMAC, protected template handling, and image-message processing. |
| `fw_inf/fpc_disum_fw.inf` | Separately binds `MI_01` and the revision-zero DFU identity for firmware-update access. |
| `fw_inf/x64/fpc_disum_fw.dll` | UMDF firmware/update transport, including TLS-key setup support. |
| `SealTlsKey_*` | SGX and non-SGX TLS-key generation/sealing implementations. |

The embedded build paths identify this as Xiaomi A35 customer work under an
FPC `DISUM` project. This is consistent with the exact hardware ID and upstream
driver terminology.

### Protocol facts exposed by static strings

The main UMDF driver names the following operations/events:

- `CMD_TLS_INIT`
- `CMD_TLS_DATA`
- `CMD_GET_TLS_KEY`
- `CMD_SET_TLS_KEY`
- `CMD_REFRESH_SENSOR`
- `EVT_TLS`
- `EVT_TLS_KEY`
- `EVT_REFRESH_SENSOR`
- `EVT_USB_LOGS`

The enclave contains mbedTLS state names and PSK cipher-suite strings. It
explicitly identifies `Disum PSK`, encrypted image messages, dead-pixel data,
key sealing/unsealing, SHA-256/HMAC handling, and protected template HMACs.
This confirms that the TLS/key layer is central to normal capture and that a
passive USB capture alone will not reveal plaintext images.

No key material or biometric data was extracted.

### Critical Windows 11 member hashes

| Archive member | SHA-256 |
|---|---|
| `FPC/fpc_disum_um_usb.inf` | `49fea846a54cb0122f9dd6fde7d6716394e2189ffed197ec11dda093281680f1` |
| `FPC/fpc_disum_um_usb.cat` | `0b49cff6109b18a63a172ee249f1a03afaf881054bb2560f0ceea752ff2eefdc` |
| `FPC/x64/fpc_disum.dll` | `99d72f87fe80338ad243437d602efac2a215f111f9ee654f7d31902bf2ab0d38` |
| `FPC/x64/FpcDisumEngine.dll` | `befb0224c193d2bbc17af56efca714022fdfe82ff6627ee2e6d46f2ae0843f39` |
| `FPC/x64/fpc_enclave.dll` | `1de61453b2436366a455463a19618ccf5fd3e2a1cee36cefce20b3d91fbf47dd` |
| `FPC/fw_inf/fpc_disum_fw.inf` | `a8bfa89d3528496207182fed8802de29965a777eb48417b3bfc1c9fb30c32881` |
| `FPC/fw_inf/x64/fpc_disum_fw.dll` | `60a444707fbd9a722181e3d52be913e721a5297c0a22e4a8672446e0957891ba` |
| `FPC/fw_inf/x64/SealTlsKey_enclave.dll` | `a2cefa98a32817eb391578029b126fd25d448f97b7ab717582473a52a6249bed` |
| `FPC/fw_inf/x64/SealTlsKey_enclave.signed.dll` | `6953d2a2ea529596aca775d43816af100d978b6bcd9eea38a5f6c377a9cdd419` |
| `FPC/fw_inf/x64/SealTlsKey_sgx.dll` | `7fc24b0d3b2a0e263bbd868f030850d0f68308003b11a34a1c4d5e48ec21dd0f` |

## Existing Linux implementation landscape

### 1. Stock libfprint

- Does not support `10a5:9200` in the installed release or current published
  supported-device list.
- This is the safest production baseline, but it cannot currently use the
  sensor.

### 2. Upstream libfprint merge request !570

- Exact target: FPC Disum/FPC1022 USB devices `10a5:9200` and `10a5:9201`.
- Implements host-as-server TLS-PSK transport, 112x88 grayscale capture,
  five-stage image-device enrollment, and SIGFM/SIFT match-on-host verification.
- Reported by its author to work on real `10a5:9200` hardware.
- Still open at `af647965253bfcf283474bf6a9dd486f1df553eb`; conflicted and needs rebasing.
- Depends on still-unmerged SIGFM work in merge request !530.
- Best technical reference and likely best upstream destination, but not yet a
  production-ready package.

### 3. `pakizat/libfprint-fpc9200`

- Experimental exact-device fork published in June 2026.
- Performs single-sample raw-image correlation and warns against PAM/login use.
- Its threshold calibration is based on a small local dataset.
- Useful as corroborating protocol/tooling research, not the preferred security
  or upstream baseline.

## Safety conclusions from the inventory

1. This is a match-on-host design: the host receives fingerprint imagery and
   performs matching, so raw-image and template privacy controls are mandatory.
2. Interface 1 is a firmware-update path. Do not bind, replay, fuzz, or pass it
   through casually while experimenting with interface 0.
3. The normal protocol uses TLS-PSK and protected key storage. Passive USB
   captures are valuable for sequencing and framing, but not sufficient by
   themselves to recover images.
4. The supplied Windows package is a strong reference oracle because it is for
   the exact Xiaomi/FPC Disum device, not merely a similar fingerprint reader.
5. The upstream MR already covers the hard protocol work. Repeating the entire
   reverse-engineering process should be reserved for verifying gaps or fixing
   MR behavior, rather than being the starting point.

## Sources

- [Upstream libfprint supported devices](https://fprint.freedesktop.org/supported-devices.html)
- [libfprint MR !570: FPC Disum/FPC1022 driver](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/570)
- [libfprint MR !530: SIGFM integration](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/530)
- [Experimental `pakizat/libfprint-fpc9200` fork](https://github.com/pakizat/libfprint-fpc9200)
- [Neodyme: Reversing a Fingerprint Reader Protocol](https://neodyme.io/en/blog/fingerprint_reversing/)
- [linux-hardware.org: USB `10a5:9200`](https://linux-hardware.org/?id=usb:10a5-9200)
- Local USB/DMI/kernel observations and the user-supplied `FingerPrint.zip`
