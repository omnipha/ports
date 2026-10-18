# google-sargo (Google Pixel 3a)

SDM670 device, second fully working Omnipha target: boots, SSH (key-only),
WiFi (ath10k/WCN3990 via our regd patch), display, GPU, Phosh UI.

- `device.yaml` — machine-readable status. Update it in the same PR as any change.
- `APKBUILD.linux-postmarketos-qcom-sdm670` — kernel package pinned to
  [omnipha/linux-sdm670](https://github.com/omnipha/linux-sdm670) branch `omnipha`
  (base tag `sdm670-v7.2.3_beta2`, upstream: gitlab.com/sdm670-mainline/linux).
- `config-postmarketos-qcom-sdm670.aarch64` — kernel config as built and verified.

## The WiFi fix

sargo units with an unprogrammed EEPROM regdomain (`0x0`) get channel 13
(2.4 GHz) hard-disabled by the ath driver: `0x0` is not detected as a world
SKU, so `ath_default_world_regdomain()` (0x64, channels 1–11 only) becomes the
custom STRICT_REG base and `CHAN_DISABLED` is baked into `orig_flags`
permanently — a later `ieee80211_regdom=DE` can never re-enable channel 13.

Patch on branch `omnipha` (commit "ath: regd: default unprogrammed EEPROM to
world regdomain with ch 12/13"): map `0x0` to WOR5_ETSIC (0x65) and use
`ath_world_regdom_63_65` (2.4 GHz 1–13, 12/13 passive) as the custom base.
Verified 2026-10-18: channel 13 (2472 MHz) WPA2 connects with
`options cfg80211 ieee80211_regdom=DE`.

5 GHz mid-band (5470–5725, e.g. channel 116/5580) stays excluded by the same
regdomain; on this unit starting a vdev there crashes the ath10k_snoc firmware
(`halphy_caldb.c` assertion). Treat 5 GHz DFS as broken until proven otherwise.

## Build your own image (generic, no private data)

```sh
git clone --depth 1 https://gitlab.com/postmarketos/pmbootstrap.git
cd pmbootstrap && ./pmbootstrap.py init
#   vendor: google, codename: sargo, channel: edge, ui: console or phosh,
#   extra packages: openssh ; ssh-keys: y
./pmbootstrap.py install            # add --password <throwaway> for console login
./pmbootstrap.py flasher flash_rootfs && ./pmbootstrap.py flasher flash_kernel
```

WiFi needs the patched kernel: replace the pmaports kernel package's `source=`
with the tarball/commit from `omnipha/linux-sdm670` branch `omnipha`
(see `APKBUILD.linux-postmarketos-qcom-sdm670` here) and rebuild with
`pmbootstrap build --force linux-postmarketos-qcom-sdm670`, then re-run
`install` and flash. For DE, put `options cfg80211 ieee80211_regdom=DE` into
`/etc/modprobe.d/` in the rootfs.

Do NOT commit: WiFi credentials, SSH keys, hostnames of private units,
throwaway build passwords. Those belong to the deployer, not the port.
