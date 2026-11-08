# Experimental SM8250 kernel recipe

Not installed and not booted. The earlier local package
`linux-omnipha-qcom-sm8250-7.2.0_git20261107-r0` was built from a private
archive and does not contain the GPU/fastboot device-tree change.

This recipe fetches the public tag `sm8250-7.2.0_git20261010`
(`3c5440e9dd3c3e3b5735ad8f1b22bdfd02c707d9`) and applies the display,
audio, camera and GPU/fastboot patches from omnipha/linux-sm8250. The
complete public archive was compared byte for byte with the local copy.
`olddefconfig` resolves the module directory to
`/usr/lib/modules/7.2.0-omnipha-sm8250-r1`, so it does not overwrite the
installed 7.2.0 modules. A local abuild of this exact recipe finished on 2026-11-08:
`linux-omnipha-qcom-sm8250-7.2.0_git20261107-r1.apk`, 52 MB,
SHA-256 `0d46096d124687bfb83fecda55b0fe304adbf1106b125b2bb8719d22bccf6395`.
The package contains `boot/vmlinuz`, the OnePlus DTB and the camera
modules under `/usr/lib/modules/7.2.0-omnipha-sm8250-r1`. The built DTB
has GPU status okay, the zap-shader firmware name, PM8150 fastboot and
recovery modes, and PM8009 PON disabled. It has not been installed or booted.
