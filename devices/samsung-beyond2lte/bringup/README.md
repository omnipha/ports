# Galaxy S10+ (beyond2lte, Exynos 9820): bring-up notes (measured 2026-11-09..12)

Status: boots postmarketOS to a USB SSH shell. Display and touch work with the
base kernel config; WLAN needs a separate kernel branch. Not an official image.

## Layout (UFS, measured)
- `boot` = `sda14` (57,671,680 B): U-Boot in Android boot image format.
- `recovery` = `sda15`: TWRP 3.7.0_9-2.
- `vbmeta` = `sda23`: AVB disabled image required, otherwise the bootloader
  rejects the custom boot chain.
- `userdata` = `sda31` (938 GB) holds a **GPT container with 4096-byte
  sectors**: ESP at offset 8 MiB (503,316,480 B, vfat, `pmOS_boot`), rootfs at
  offset 511,705,088 B (ext4). Reading the GPT with 512-byte sectors yields
  garbage. U-Boot maps this container via `blkmap` and starts
  `EFI/BOOT/BOOTAA64.EFI` (systemd-boot) directly.

## U-Boot
Base `dec4927b4ad5b789b0854050096fc80250627de7` plus the three patches here:
1. `0001` replaces the `bootcmd` tail with a guarded direct EFI load
   (`ufs init && scsi scan && part start/size && blkmap … && bootefi`).
   Do **not** shorten `bootcmd` by patching the binary: a double NUL makes
   `himport_r` drop every variable after it.
2. `0002` readable menu (`font select 16x32`, `bootmenu -1` on EFI failure).
3. `0003` larger 32x64 font (optional).
Build with `ARCH=arm` (this tree's ARM64 convention), `CROSS_COMPILE=aarch64-`,
`CONFIG_DEFAULT_DEVICE_TREE=exynos/exynos9820-beyond2lte`. Wrap `u-boot.bin`
with `mkbootimg --kernel u-boot.bin` and flash to `boot`.

## Kernel
- Base config measured on device: branch `beyond2lte-pmos-defconfig` in
  `omnipha/linux-samsung-s10-exynos9820` (`DRM_SIMPLEDRM=y`,
  `TOUCHSCREEN_S6SY761=y`). With it the console and touch work.
- WLAN (BCM4375, PCIe `14e4:4475`): branch `issue-1-bcm4375-pcie`, commit
  `160cc32e597f`. That build has simpledrm and the touchscreen **disabled**, so
  the screen stays black unless `simpledrm`, `drm_sysfb_helper` and `s6sy761`
  are built out of tree and loaded. Unifying both into one config is open.
- Firmware `brcmfmac4375b1-pcie.bin/.clm_blob` and the Semco CS01 NVRAM (renamed
  to `brcmfmac4375b1-pcie.txt`) come from the Android vendor partition, not from
  `linux-firmware`. Do not commit the blobs; record checksums instead.

## Recovery
- Stock Download Mode is reachable from a boot loop by holding Volume-Down +
  Bixby only (no Power) with the cable attached, then Volume-Up once.
- Large partition writes through Heimdall stopped repeatedly after exactly
  240 MiB (13 timeouts, link stayed up, two cables, two ports, two tools).
  Cause unknown. A full stock restore was only achieved with UnlockTool's
  "Odin softbrick fix". Small partitions (boot, recovery, vbmeta) flashed fine.
