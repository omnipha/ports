# AGENTS.md — omnipha/ports

Purpose: device packages + device.yaml database for all Omnipha-supported phones.

## Layout
- `devices/<codename>/device.yaml` — machine-readable device status. THE source of truth.
- `devices.json` and `DEVICES.md` — generated machine-readable and human-readable indexes; rebuild with `tools/harvest.py index`.
- `schema/device.schema.json` — validates every device.yaml; `tools/harvest.py check` fails on stale index or schema violations.
- `hardware/gpus.yaml`, `hardware/socs.yaml` — GPU model and external Android benchmarks, keyed by SoC. `GPU.md` is generated from them. `status.gpu` stays the separate Linux test result.
- `devices/<codename>/` — packaging files (APKBUILD, deviceinfo) derived from upstream pmaports.
- `firmware/` — policy: never commit blobs; document extraction + checksums.

## Data rules
- `upstream_os.ut` is refreshed by `tools/harvest.py ut` from devices.ubuntu-touch.io; do not hand-edit its numbers.
- `upstream_os.nura` is curated by hand (the Nura wiki is not machine-readable). Keep `source` and `checked` on every claim.
- `upstream_os` describes upstream projects only; it never implies an Omnipha release. Omnipha image status lives in `release`.
- `device_repo` must be the canonical URL `https://github.com/omnipha/device-<codename>`; having a repo never implies `official`.
- `maintainers` lists public identities and roles (`hardware-tester` | `maintainer` | `release-owner`); never host details or secrets.
- `release.status: official` requires the gate in README.md ("Official images"): reproducible CI build, flashing/rollback docs, physical boot/network/SSH test (`release.evidence`), named `release-owner`, and `maintenance: maintained`. Enforced by `tools/harvest.py check` and tests (`python3 -m pytest tools/`).
- `variants` lists sold ram/storage combinations. Do not store ram and storage as independent lists.
- Never add prices. Used-price estimates go to omnipha/market.
- GPU model and external benchmarks live once in `hardware/`, never copied into a device file. A benchmark is not a Linux result.

## Commands
No build here directly; images are built from omnipha/images (which references this repo).

## Conventions
- One device per ports PR. Cross-repo code and device status require linked PRs; after implementation and public test evidence land, update device.yaml in a separate ports PR. GitHub PRs cannot span repositories. Never claim boot from CI alone.
- Status vocabulary: works | partial | untested | broken. New measured claims require a public status_evidence URL, date and variant. Legacy snapshot is not proof; see CONTRIBUTING.md.
- Never commit proprietary firmware. Reference firmware-sha256.txt entries.
- Kernel packaging pins: repo `omnipha/linux-<soc>`, branch `omnipha`.
- English only. Sign commits.

## Facts
- First device: xiaomi-laurel (Mi A3). Works: boot, ssh, wifi, display, gpu.
- Upstream pmaports overlay base: https://gitlab.postmarketos.org/postmarketOS/pmaports (see omnipha/pmaports-mirror).
