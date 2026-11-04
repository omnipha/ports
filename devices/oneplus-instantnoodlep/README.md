# OnePlus 8 Pro (`oneplus-instantnoodlep`)

This is a device-package port, not an Omnipha image, a hardware test or a
flashing guide. The existing `device.yaml` is unchanged. The partition and
bootloader settings in `deviceinfo` are upstream metadata, **not verified safe
flashing instructions**.

## Reproducible source provenance

The four package files come from pmaports testing, mirrored at the immutable
commit [`dfb010f5b9885d185d089b6e1e493030062f9756`](https://github.com/omnipha/pmaports-mirror/tree/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep)
(upstream package version `7-r0`). Original, unmodified files and their SHA-256:

| File | Upstream SHA-256 |
| --- | --- |
| [`APKBUILD`](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep/APKBUILD) | `23e56f894a84786a9d0ea4d1df573b8e094b484a6fa7b334917eee5db888eb9b` |
| [`deviceinfo`](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep/deviceinfo) | `d17adb572bc4c735fb0ecd139ab904649377c470f6a1050a5c70b60fa7bd7f44` |
| [`kernel-cmdline.conf`](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep/kernel-cmdline.conf) | `5fc53b43a25ce72a628b52a845054d9fd7688da7a323ed60c33977b0c7228d1b` |
| [`sm8250-oneplus-instantnoodlep-empty.dts`](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep/sm8250-oneplus-instantnoodlep-empty.dts) | `ab1c6f88803ed130ffd58e7f28da1f8e707d2fc61aed06f3a2d20a1c2bdb24fd` |

The last three files are byte-identical to the mirror and verified with the
upstream APKBUILD's SHA-512 hashes. Our APKBUILD is based on that file but
bumps `pkgrel` to 1, removes the proprietary firmware dependency, and pins the
kernel package to `7.2.0_git20261010-r0`. `dtc` still builds the upstream empty
DTBO and the device package still installs it. The mirror package has no
`modules-initfs`; none is invented here.

## Kernel and firmware dependencies

The versioned `linux-postmarketos-qcom-sm8250` package is **not provided by this
repository**. The pin matches [`omnipha/linux-sm8250` UPSTREAM.md](https://github.com/omnipha/linux-sm8250/blob/aff10181998c2123182c0dc464aba9f40a0dfec4/UPSTREAM.md).
That repository is a tracking repository, not a kernel source tree, so the
usual `omnipha/linux-<soc>` kernel-branch convention cannot currently be used
here. No Omnipha kernel recipe is claimed. A builder must provide the pinned
package and its complete build inputs from a compatible, controlled repository.

For review, the [pinned upstream kernel APKBUILD](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/linux-postmarketos-qcom-sm8250/APKBUILD)
has SHA-256 `c6c4a314676686f85c7704e71f4b40c53b39865fae169f78ce54fd97cd453655`,
and its [kernel config](https://github.com/omnipha/pmaports-mirror/blob/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/linux-postmarketos-qcom-sm8250/config-postmarketos-qcom-sm8250.aarch64)
has SHA-256 `47af492a30666c5c43b40109bd10336d45b108ff1c80cb1d49d3ad765a8fbe5f`.
That recipe pins tag `sm8250-7.2.0_git20261010` of the [SM8250 kernel](https://gitlab.postmarketos.org/soc/qualcomm-sm8250/linux)
and records the kernel source archive's SHA-512 as
`05df1589411d2817fecc403402f1dea2c405c5de102bf92e23089e430fc2c623702bd778fbea5b87f70ea02e9eff7f02a7de292f895d47ff40ae88dafdfbab58`.
The tag resolved to Git object `3c5440e9dd3c3e3b5735ad8f1b22bdfd02c707d9` when
checked. This is a source reference, not proof that the tag or archive was
built or that the binary dependency came from it; confirm the object and hash
when building.

Upstream depends on `firmware-oneplus-instantnoodlep`; this port deliberately
does not fetch or depend on that proprietary package. Supplying needed firmware
is a separate, unresolved build/integration task. Follow the repository's
[firmware policy](../../firmware/README.md), including documented provenance and
SHA-256 of legally obtained device-specific files. No firmware file list or
hashes are asserted here without evidence. This package alone is insufficient
for a usable or release-ready image.
