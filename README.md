# omnipha/ports

Device packages, firmware handling, kernel packaging and the machine-readable
device database for Omnipha. This is where new device support lands.

## Layout
- `devices/<codename>/` — one folder per device
  - `device.yaml` — status database entry (source of truth)
  - `APKBUILD`, `deviceinfo`, … — packaging, based on upstream pmaports, with our fixes
- `firmware/` — firmware extraction policy and helpers

## Device lifecycle
`new` → `boot` → `ssh+network` → `usable-server` (profile: server) → `daily-phone`.

A device is only listed as `usable-server` when an image build from `images/`
boots, joins WiFi, and accepts SSH keys without any manual password entry.

## Agent notes
See AGENTS.md. Query `devices/<codename>/device.yaml` before making claims about
device support. One device per PR; update device.yaml in the same PR.

## License
GPL-3.0-only (upstream pmaports derivatives).
