# omnipha/ports

Device packages, firmware handling, kernel packaging and the machine-readable
device database for Omnipha. This is where new device support lands.

## Layout
- `devices/<codename>/` — one folder per device
  - `device.yaml` — status database entry (source of truth)
  - `APKBUILD`, `deviceinfo`, … — packaging, based on upstream pmaports, with our fixes
- [`DEVICES.md`](DEVICES.md) — browsable status and contribution index, generated from `device.yaml`
- [`GPU.md`](GPU.md) — devices ranked by GPU and max RAM for GPU workloads, generated from `hardware/*.yaml`
- `devices.json` — machine-readable aggregate of all `device.yaml`, rebuilt by `tools/harvest.py index` (CI verifies it is fresh)
- `schema/device.schema.json` — JSON Schema for `device.yaml`
- `hardware/` — `gpus.yaml` and `socs.yaml`: GPU identity plus cited Android benchmarks. Not a Linux performance claim.
- `tools/harvest.py` — database tooling: `ut` (refresh Ubuntu Touch status from devices.ubuntu-touch.io), `index`, `check`
- `firmware/` — firmware extraction policy and helpers

The database answers "which phones run full Linux and how well": hardware
facts, sold `variants` (one ram/storage combination each), and upstream OS
support (`upstream_os.ut`, `upstream_os.nura`), each with `source` and
`checked`. Used-price estimates live in omnipha/market. This repo stays
price-free; the schema rejects price keys.

## Discover and contribute

Start at [DEVICES.md](DEVICES.md) to find a phone, its Omnipha project stage,
reported component status, image availability and the correct device or mission
issue board. [CONTRIBUTING.md](CONTRIBUTING.md) explains new devices, evidence,
linked cross-repo PRs, and how status claims become public. All 179 tracked
entries remain visible, including research-only models; only active ports need
an individual device repo. `status` is historical/observed hardware, not a
promise that an image is available. Old status entries without a public test
link are legacy claims, not independently verified evidence.

## Official images
`upstream_os` records what upstream projects (Ubuntu Touch, Nura) report — it
never implies an Omnipha release. Omnipha's own image status is the separate
`release` block:

- `device_repo` — canonical device repository `https://github.com/omnipha/device-<codename>`.
  Its presence does not make a release official.
- `maintainers` — public identities with roles (`hardware-tester`,
  `maintainer`, `release-owner`). Hardware-test responsibility is explicit.
- Missing `release` or `release.status: unreleased` means no Omnipha image to
  install, even if `status.boot: works` or an `images` definition exists.
- `release.status: testing` requires an immutable public artifact (URL and SHA-256),
  input/build manifest, reproducible CI, flashing/rollback instructions and
  physical boot/network/SSH evidence on real hardware.
- `release.status: official` requires the same gate plus a named `release-owner`
  and `maintenance: maintained`. Schema and tests enforce the *shape* of the
  evidence; maintainers must review its actual contents and accessibility.

## Device lifecycle
`new` → `boot` → `ssh+network` → `usable-server` (profile: server) → `daily-phone`.

A device is only listed as `usable-server` when an image build from `images/`
boots, joins WiFi, and accepts SSH keys without any manual password entry.

## Agent notes
See AGENTS.md. Query `devices/<codename>/device.yaml` or `devices.json` before
making claims about device support. One device per ports PR. Changes in other
repos need a linked status PR after implementation and public evidence land.
After changing any device.yaml run:

```bash
python3 tools/harvest.py index && python3 tools/harvest.py check
python3 -m pytest tools/
```

## License
GPL-3.0-only (upstream pmaports derivatives).
