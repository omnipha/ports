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
installed 7.2.0 modules. No package has been built from this recipe yet.
