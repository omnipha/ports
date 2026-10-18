# AGENTS.md — omnipha/ports

Purpose: device packages + device.yaml database for all Omnipha-supported phones.

## Layout
- `devices/<codename>/device.yaml` — machine-readable device status. THE source of truth.
- `devices/<codename>/` — packaging files (APKBUILD, deviceinfo) derived from upstream pmaports.
- `firmware/` — policy: never commit blobs; document extraction + checksums.

## Commands
No build here directly; images are built from omnipha/images (which references this repo).

## Conventions
- One device per PR. Update device.yaml in the same PR as any functional change.
- Status vocabulary: works | partial | untested | broken.
- Never commit proprietary firmware. Reference firmware-sha256.txt entries.
- Kernel packaging pins: repo `omnipha/linux-<soc>`, branch `omnipha`.
- English only. Sign commits.

## Facts
- First device: xiaomi-laurel (Mi A3). Works: boot, ssh, wifi, display, gpu.
- Upstream pmaports overlay base: https://gitlab.postmarketos.org/postmarketOS/pmaports (see omnipha/pmaports-mirror).
