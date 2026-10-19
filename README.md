# omnipha/ports

Device packages, firmware handling, kernel packaging and the machine-readable
device database for Omnipha. This is where new device support lands.

## Layout
- `devices/<codename>/` — one folder per device
  - `device.yaml` — status database entry (source of truth)
  - `APKBUILD`, `deviceinfo`, … — packaging, based on upstream pmaports, with our fixes
- `devices.json` — aggregate index of all `device.yaml`, rebuilt by `tools/harvest.py index` (CI verifies it is fresh)
- `schema/device.schema.json` — JSON Schema for `device.yaml`
- `tools/harvest.py` — database tooling: `ut` (refresh Ubuntu Touch status from devices.ubuntu-touch.io), `index`, `check`
- `firmware/` — firmware extraction policy and helpers

The database answers "which phones run full Linux and how well": hardware
facts, sold `variants` (one ram/storage combination each), and upstream OS
support (`upstream_os.ut`, `upstream_os.nura`), each with `source` and
`checked`. Used-price estimates live in omnipha/market. This repo stays
price-free; the schema rejects price keys.

## Official images
`upstream_os` records what upstream projects (Ubuntu Touch, Nura) report — it
never implies an Omnipha release. Omnipha's own image status is the separate
`release` block:

- `device_repo` — canonical device repository `https://github.com/omnipha/device-<codename>`.
  Its presence does not make a release official.
- `maintainers` — public identities with roles (`hardware-tester`,
  `maintainer`, `release-owner`). Hardware-test responsibility is explicit.
- `release.status: official` requires the full gate, enforced by schema and
  tests: reproducible CI build, documented flashing/rollback, physical
  boot/network/SSH test on real hardware (`release.evidence`), and a named
  `release-owner` plus `maintenance: maintained`.

## Device lifecycle
`new` → `boot` → `ssh+network` → `usable-server` (profile: server) → `daily-phone`.

A device is only listed as `usable-server` when an image build from `images/`
boots, joins WiFi, and accepts SSH keys without any manual password entry.

## Agent notes
See AGENTS.md. Query `devices/<codename>/device.yaml` or `devices.json` before
making claims about device support. One device per PR; update device.yaml in
the same PR. After changing any device.yaml run:

```bash
python3 tools/harvest.py index && python3 tools/harvest.py check
```

## License
GPL-3.0-only (upstream pmaports derivatives).
