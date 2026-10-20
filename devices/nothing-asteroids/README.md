# nothing-asteroids (Nothing Phone (3a) Pro)

SM7635/volcano device, A/B slots, Android boot header v4. No **successful Omnipha boot** is established: experimental, authorized boot
attempts returned to fastboot with no observed USB network or SSH. These are
not an installable server image and do not prove that the test kernel ran.
This packaging is based on stock partition layout and read-only firmware
references from a test unit. See [device-specific contributor issues and test reports](https://github.com/omnipha/device-nothing-asteroids),
[the bring-up mission](https://github.com/omnipha/ports/issues/3),
and [the first-boot issue](https://github.com/omnipha/ports/issues/6). Physical
flashing/booting requires an explicit, scoped authorization and a verified
rollback path; do not use the metadata below as a flashing recipe.

- `device.yaml` — machine-readable status. Update it in the same PR as any change.
- `APKBUILD`, `deviceinfo`, `modules-initfs` — device package modeled on
  `xiaomi-laurel`, adapted to A/B (no dedicated recovery/boot-ramdisk
  assumptions): header v4, `fastboot`, pagesize 4096, boot + vendor_boot
  + dtbo partitions, vbmeta (experimental configuration only, not tested installation instructions).
- `APKBUILD.linux-omnipha-nothing-sm7635` — vendor kernel package pinned
  to the immutable NothingOSS commit per
  [omnipha/linux-sm7635](https://github.com/omnipha/linux-sm7635) source
  policy: `d5f5f965fd0b478eaf4eb63fd984c5a4a92135a7`
  (branch `sm7635/v/mr`, kernel 6.1.78). The tree is fetched as a
  tarball of that commit from the NothingOSS repository; no mirror, no
  branch head.
- `config-omnipha-nothing-sm7635.aarch64` — kernel config as built
  (identical to the verified linux-sm7635 baseline config,
  sha256 acee1959e6ab3b4fcdf72ef708d5a13957c714e6b34a3a9ccfc5cb916c04d1cc).
- `0001-build-libbpf-cast-fix-for-host-gcc-15-clang-17.patch` — the one
  host-tool fix the baseline build needs under GCC 15/clang 17 `-Werror`.
- `0002-build-fix-trace-include-paths.patch`,
  `0003-build-quote-local-includes.patch` — build-only fixes needed to
  compile the full module set (not just `Image dtbs`) from the released
  tarball: vendor tracepoint headers use `TRACE_INCLUDE_PATH .`, which
  only resolves when compiling in-tree with the old build system, and two
  files use angled includes for local headers. No functional change.
  With all three patches applied the pinned tree builds
  `Image dtbs modules` cleanly with Ubuntu clang 17.0.6:
  - `Image` sha256 `2463f511c8a08c8fa50fef73a620e94e6bfa816bca5b100d977786081ae024fb`
    (differs from the linux-sm7635 baseline `b289b9f1…` only in the
    embedded version string: the tarball is not a git checkout, so
    `CONFIG_LOCALVERSION_AUTO=y` does not append `-g<commit>-dirty`)
  - `volcano-volcano-qrd-pro-overlay.dtb` sha256 `1c8251e5…`
    and `volcano-qrd-pro-overlay.dtbo` sha256 `f463a7ef…` are
    byte-identical to the baseline artifacts
  - 377 modules build, including `ufs_qcom.ko` /
    `ufshcd-crypto-qti.ko` (initramfs storage) and `sched-walt.ko`.
- `firmware/` — extraction policy, checksums only. Firmware blobs are
  never committed.

## Partition layout (from mb003, read-only)

Verified via `ls -l /dev/block/by-name` (`by-name.txt` in the private
reference set) and the stock Android fstab (`init/fstab.default` in
Nothing's device trees, cross-checked against on-device
`dev.mnt.*` getprop): A/B slotted `boot`, `vendor_boot`, `init_boot`,
`dtbo`, `vbmeta`, `vbmeta_system`, `vbmeta_vendor`, `recovery`, `modem`,
`dsp`, `bluetooth`; single `persist`, `userdata`, `super` (logical
system/vendor/odm), f2fs `userdata`/`metadata` with wrapped-key
metadata encryption. Firmware mounts (stock fstab):

| partition | stock mount | fs |
| --- | --- | --- |
| modem_a/b | /vendor/firmware_mnt | vfat |
| dsp_a/b | /vendor/dsp | ext4 |
| bluetooth_a/b | /vendor/bt_firmware | vfat |
| persist | /mnt/vendor/persist | ext4 |

Stock image sha256 identifiers (rollback references, blobs not in git)
are in `firmware/firmware-sha256.txt`.
