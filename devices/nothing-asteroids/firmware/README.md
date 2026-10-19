# Firmware policy for nothing-asteroids (Nothing Phone (3a) Pro)

No proprietary blobs are ever committed to this repository. Firmware is
extracted locally from the device (or its read-only stock backups) at
deploy/build time and verified against the sha256 values below.

## What the device needs

Per the stock Android fstab (`init/fstab.default` in Nothing's asteroid
device trees, cross-checked with on-device `dev.mnt.*` properties of
mb003, 2026-10-19) and the vendor kernel's firmware search paths
(`firmware_class.path` includes `/vendor/firmware_mnt/image`,
`/vendor/bt_firmware`, `/vendor/dsp` — see
`arch/arm64/boot/dts/vendor/qcom/volcano.dtsi` at the pinned commit):

| partition (A/B) | stock mount | contents |
| --- | --- | --- |
| modem_a / modem_b | /vendor/firmware_mnt (vfat) | MPSS modem image set (modem.mbn etc., `*.b00`–`*.bXX` + `.mdt`) |
| dsp_a / dsp_b | /vendor/dsp (ext4) | ADSP/CDSP images |
| bluetooth_a / bluetooth_b | /vendor/bt_firmware (vfat) | Bluetooth controller firmware |
| persist (no slots) | /mnt/vendor/persist (ext4) | WiFi/BT calibration, sensors; must never be flashed |

Extraction (example, on a device running stock with root, or from the
read-only stock backups; never from a dump committed to git):

```sh
mkdir -p firmware-extract/{modem,dsp,bluetooth,persist}
adb pull /vendor/firmware_mnt/image firmware-extract/modem/
adb pull /vendor/dsp firmware-extract/dsp/
adb pull /vendor/bt_firmware firmware-extract/bluetooth/
adb pull /mnt/vendor/persist firmware-extract/persist/
sha256sum firmware-extract/modem/* >> firmware-sha256.txt
```

`persist` holds per-unit calibration; it is never distributed, only
backed up locally for the same physical unit.

## Verified checksums

Stock partition images of the mb003 fleet unit (identical on both
slots; blobs stay in the private read-only backup, only identifiers
here — these are rollback references, not files in git):

| image | sha256 |
| --- | --- |
| boot_a.img = boot_b.img | `197aff11679301ca4a2d6f74dfcb942c3543ac9d41628e4e2116af0bdb706d4d` |
| vendor_boot_a.img = vendor_boot_b.img | `237259404601045205715a71b88016744c73729d4513349cfe90c754b0dc1253` |
| init_boot_a.img = init_boot_b.img | `baa33fd43c3da1d9f3358ced9249c42abecc704fc5707a5241ea69e77c1e3193` |
| dtbo_a.img = dtbo_b.img | `759813dbfd94f4a4124b08afb2c9ef85f1f9afb7cdca9829be2558ffde13c992` |
| vbmeta_a.img = vbmeta_b.img | `cc1926d2aa8e9c12df6a469111bf87f1e61e70022b84626fabcd014ae33cdffe` |
| vbmeta_system_a.img = vbmeta_system_b.img | `e93f42b556c172db6fb001c669099f15b5f2483d06c6802127e3c9816cb4a8d9` |
| vbmeta_vendor_a.img = vbmeta_vendor_b.img | `d8ea3817cb03ab0aa109d574244dede246f1498bf866fa3d36b4f40438287274` |
| recovery_a.img (OrangeFox 6.1) | `0c6767698ebb069064b450b109cde6a1172b478e30000fe852e7d9bc19dbae9e` |
| recovery_b.img (stock) | `6065f68502838b3cb20a51eb6a6aa1b250f3a58553246d9c4259593a3769874b` |

Modem/dsp/bluetooth/persist firmware extracted from the running device
will be recorded here (`firmware-sha256.txt`) once extracted; the files
themselves are never committed.
