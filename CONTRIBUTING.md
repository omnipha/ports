# Contribute a phone port or fix

Start at [DEVICES.md](DEVICES.md), the index derived from `devices/*/device.yaml`.
The `ports` entry is the sole machine-readable record of Omnipha support.
An upstream Ubuntu Touch/Nura image, a package or an `images` YAML definition
is not an Omnipha release.

## Find the right place

1. Find the device by its name, vendor or codename in `DEVICES.md` or
   `devices.json`. Check aliases and hardware variants in its `device.yaml`.
2. If it has a `device_repo`, open its Issues for reproducible hardware tests.
   If not, search existing `ports` Issues, then open a new issue with model and
   codename, exact hardware variant, existing device entry (if any), safely
   collected evidence, and the desired next test. A research-only listing stays searchable in `ports` until someone takes it
   on; provisioning its own device repository at that point is automated and
   has no arbitrary fleet-size limit.
3. Put shared kernel fixes in `linux-<soc>` (if that repo is a tracking-only
   repo, follow its AGENTS.md policy), device packages/firmware *instructions*
   in `ports`, image definitions in `images`, and device test reports/issues in
   `device-<codename>`. No proprietary firmware, partition dumps or secrets.
   Link cross-repo issues and PRs both ways.

## Report a test, not a hunch

In an issue, record device variant, source/commit or image identity, test
procedure, dated outcome, logs redacted of keys, phone identifiers and private
data, and the issue/PR URL. `untested` means no measured result; `broken`
requires an observed failure. A compiled kernel or generated APKBUILD does not
prove boot. A hardware status PR changes exactly one device.yaml and adds
`status_evidence.<component>` with date, variant and a *public, reviewable*
URL for each new `works`, `partial` or `broken` claim. Legacy statuses in
`schema/legacy-statuses.json` are grandfathered per exact value, not proof;
retest and add evidence when you can. Add a same-device README explanation if
necessary, then run `python3 tools/harvest.py index && python3 tools/harvest.py
check && python3 -m pytest tools/`.

`ports` and a device repository cannot be updated by the same GitHub PR. Open
linked PRs: first publish the implementation and test evidence in its owning
repo; then merge the corresponding `ports` status PR once its evidence is
public. Never leave a status PR implying a completed hardware test from CI
alone.

## Installation and release gate

`project.stage` answers how far the port work has progressed. `status` answers
what was observed on a test unit. Only `release.status: testing` or `official`
indicates an installable Omnipha image. It requires an immutable public image
URL and SHA-256, a build manifest with pinned inputs and build log, reproducible
CI evidence, device-specific flashing **and rollback** instructions, and a
physical boot/network/key-only SSH test recorded by a hardware tester.
`official` additionally requires a maintainer and release owner. Until then:
**no Omnipha image is published and no one should flash from `image.yaml` or
`flash: fastboot` alone.** The image metadata is not a safe install guide.
Physical tests must follow device-specific safety procedures and authorization.

New models start as `research` with honest unknowns. Move to `bring-up` for an
active, linked mission and `field-tested` only after recording actual hardware
results. Research records scale without provisioned repos or worker claims.
