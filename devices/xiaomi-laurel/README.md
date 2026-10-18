# xiaomi-laurel (Xiaomi Mi A3)

SM6125 device, first fully working Omnipha target: boots, SSH (key-only), WiFi
(WCN3990 via MPSS remoteproc — our kernel patch), display, GPU.

- `device.yaml` — machine-readable status. Update it in the same PR as any change.
- `APKBUILD`, `deviceinfo` — upstream packaging as reference.
- `deviceinfo.drm` — our variant adding `deviceinfo_drm="true"` so the panel is selectable as UI.
- `APKBUILD.linux-nura-qcom-sm61x5` — kernel package pinned to omnipha/linux-sm61x5 (branch omnipha).
- `firmware-sha256.txt` — checksums of firmware files extracted from the device. Firmware files themselves are never committed.

WiFi patch provenance: partly adapted from criollojoel10/pmos-laurel-sprout (6.1 kernel, license NOASSERTION — clarify before upstreaming).
