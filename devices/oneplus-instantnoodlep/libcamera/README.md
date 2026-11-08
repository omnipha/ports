# libcamera 0.7.2 overlay used for the OnePlus 8 Pro camera work

Temporary downstream package, forked from Alpine/postmarketOS `temp/libcamera`.
It builds libcamera 0.7.2 (`pkgver` 99990.7.2, `pkgrel` 12) with the sensor and
autofocus patches for the OnePlus 8 Pro: S5K3M5, IMX471, IMX586, IMX689, GC5035,
plus contrast-detection autofocus.

The upstream tarball is fetched from
`https://gitlab.freedesktop.org/camera/libcamera/-/archive/v0.7.2/libcamera-v0.7.2.tar.gz`.
It is not stored here. The patch bodies for the OnePlus sensors match the
already published patches in
`darknagel/oneplus-instantnoodlep-nura-unofficial` `libcamera-patches/` at
`02118a12`; only the patch subject numbering differs.

This is not the libcamera 0.8.0 package installed on the phone
(`qcam-99990.8.0-r0`). The 0.8.0 build does not contain the OnePlus sensor
helpers. A local `abuild` of this 0.7.2 recipe produced the aarch64 packages
under `mb005-build/libcamera-pmb/build/repo/build/aarch64/` on 2026-11-08.
That build was not installed on the phone and is not a camera proof.
