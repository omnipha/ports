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

## Staged guest closure versus server image (#18, 2026-10-27)

This is a **host-only packaging comparison**, not an Omnipha boot or image.
[Run 49's public finding](https://github.com/omnipha/linux-sm7635/pull/141)
and [verified stock restore](https://github.com/omnipha/linux-sm7635/issues/139#issuecomment-6437437247)
measured a RAM-backed postmarketOS v24.12 / Alpine 3.21.9 process environment
on the **stock 6.1.84** kernel, followed by restoration of stock `init_boot_a`,
five matching stock slot-A hashes and stock Android boot. The separate
[host-only PTY fixture](https://github.com/omnipha/linux-sm7635/blob/897c018c4b833fab5b1d5f44d730c7b837300187/BOOT.md#L1-L40)
did not measure a device PTY.

The diagnostic input is the [134-APK aarch64 lock](https://github.com/omnipha/linux-sm7635/blob/4b77c6f046ba67bdbcb05fe20a4aa9e343e60be4/scripts/alpine-session-packages.lock)
(Git blob `1ab1e2800889ecd5d9c540240e0f252f97e49e17`, **not** an image
SHA-256). Its [assembly script](https://github.com/omnipha/linux-sm7635/blob/4b77c6f046ba67bdbcb05fe20a4aa9e343e60be4/scripts/build-alpine-session.py#L18-L26)
pins Alpine v3.21 main/community and postmarketOS v24.12 repository index
hashes; the lock pins package names, versions, APK sizes, installed sizes and
per-APK SHA-256. Signed indexes, APK hashes and an offline no-scripts install
were checked in #139. Two offline host assemblies matched a 23,713,302-byte
diagnostic archive (SHA-256
`7a76a11062615387af5eac8f67b7f672d5f9004decac89529396d442ab3c6e26`);
390 aarch64 ELFs had no missing linked libraries. Neither the lock nor that
archive is a server-image world, a packaged device kernel or a release rootfs.

| Input or function | What run 49 demonstrated | What the image path actually declares or still needs |
| --- | --- | --- |
| Base and shell | Lock contains `postmarketos-base=38-r3`, musl `1.2.5-r12`, BusyBox `1.37.0-r14` and OpenRC `0.55.1-r2`; a host reached a UID-0 non-PTY shell inside the staged chroot. The original diagnostic PID 1 remained in charge. | [`device-nothing-asteroids`](APKBUILD) is a `pkgver=1`/`pkgrel=0` source recipe already depending on **unversioned** `postmarketos-base`, the pinned kernel package and `android-tools-mkbootimg`. The upstream base provides an init/ramdisk path and SSH dependencies, but neither this dependency nor installed OpenRC proves that the device boots the distribution as PID 1. Do not add the whole diagnostic lock to `depends`. |
| SSH | `dropbear=2024.86-r0` was started separately with an ephemeral host key and key-only login; the diagnostic USB SSH stayed available. `openssh=9.9_p2-r0` was present in the closure but was **not** the measured guest server. | The [server definition](https://github.com/omnipha/images/blob/53982ea0999025119b4115e4fe931acecf6126b6/devices/nothing-asteroids/image.yaml#L7-L17) asks for `openssh`; the upstream base includes OpenSSH-server/OpenRC inputs. Builder [PR #2](https://github.com/omnipha/builder/pull/2) proposes locked passwords, public-key injection and an enabled `sshd`, but remains unmerged and rejects this device recipe. Production SSH key provisioning, start and reachability after cold boot are unverified; adding diagnostic Dropbear here would select a different service, not solve that gate. |
| WLAN and modem | `iw=6.9-r0`, `wpa_supplicant=2.10-r11` and BusyBox `udhcpc` were driven **manually** after guarded stock modem/WPSS startup: scan, association, DHCP, gateway, DNS and external reachability succeeded in-session. Packaged OpenRC/eudev were not started as the guest's boot services. | Neither this APKBUILD nor the image definition requests `iw`/`wpa_supplicant` or configures a WLAN service, DHCP, firmware mount, modem/WPSS ordering or reboot autoconnect. The image requests `rmtfs`, `tqftpserv`, `qrtr` and device-extracted firmware; the [firmware policy](firmware/README.md) supplies references, not blobs or init integration. Resolve the **actual** image package world and choose/test a production network/service and private provisioning path in images/builder; do not infer the final world from this lock. |
| Kernel, initfs and boot chain | The successful chroot used stock `6.1.84` modules/firmware and retained the diagnostic init; no own-kernel PID-1 boot, persistent rootfs or device PTY was measured. | [`linux-omnipha-nothing-sm7635`](APKBUILD.linux-omnipha-nothing-sm7635) pins NothingOSS `d5f5f965fd0b478eaf4eb63fd984c5a4a92135a7` (**6.1.78**) with three build patches; `modules-initfs` names only `ufs_qcom` and `ufshcd-crypto-qti`. [`deviceinfo`](deviceinfo) selects a QRD Pro DTB and header v4 boot/vendor_boot/dtbo/vbmeta metadata, not a verified ordered stock-compatible DTB/DTBO/AVB set or generic `init_boot` ramdisk. The physical own-kernel [#12](https://github.com/omnipha/linux-sm7635/issues/12) boot boundary is still open. |

The [images CI workflow](https://github.com/omnipha/images/blob/53982ea0999025119b4115e4fe931acecf6126b6/.github/workflows/build.yml#L17-L36)
validates `image.yaml` against ports commit
`0633617cd90dfdc12fb8a8941c4ad0dddad36d3b` and prints a **definition**
hash, not an image hash. There is no final pinned pmaports resolver revision,
APK world, built server rootfs, immutable artifact or image SHA-256 for this
profile. The recipe's header-v4 A/B metadata omits `init_boot`; its f2fs
`userdata` requests **metadata encryption**, not plaintext or LUKS. Green
validation cannot establish boot-chain compatibility, persistence, private
key/firmware provisioning or cold-boot SSH/WLAN.

**Decision: no ports package, kernel, initfs or `device.yaml` change.** The
observed shell/network clients ran from a stock-kernel diagnostic closure;
no evidence isolates a missing *ports-side* dependency or safe init correction
for the unbuilt 6.1.78 image. The smallest handoff is to
[images #1](https://github.com/omnipha/images/issues/1): select and record the
real server world, key-only OpenSSH and WLAN/firmware/modem/init integration,
then build/hash an artifact through [builder #1](https://github.com/omnipha/builder/issues/1).
Builder [#3](https://github.com/omnipha/builder/issues/3) still requires
verified permitted header-v4 `init_boot`/DTB/DTBO/AVB inputs and A/B checks;
[#4](https://github.com/omnipha/builder/issues/4) still requires an authorized
metadata-encrypted userdata provisioning/definition decision. These specific
missing downstream inputs are already tracked there; there is no authorized
unencrypted `/data` fallback. Do not mark [ports #6](https://github.com/omnipha/ports/issues/6)
tested, bypass own-kernel #12 or claim an Omnipha image or release from this
comparison.

Host-only verification for this comparison: `bash -n` on both APKBUILDs and
`deviceinfo`; `sha512sum` on the six locally available package inputs matched
both APKBUILD declarations, and the config SHA-256 matched the baseline above;
`python3 tools/harvest.py index && python3 tools/harvest.py check` passed and
`python3 -m pytest tools/` passed (18 tests). This is a bounded **static input
fixture**, not dependency resolution, APK compilation or a kernel build:
`abuild`, `apk` and `clang` are unavailable here (the installed `pmbootstrap`
alone cannot supply those build tools or the missing verified image inputs).

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
