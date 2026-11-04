---
date: 2026-11-04
issue: ports#26
subsystem: packaging-tests
result: confirmed
---
# instantnoodlep merged package checks

PR #27 landed the OnePlus 8 Pro package from mirror commit
[`dfb010f5b9885d185d089b6e1e493030062f9756`](https://github.com/omnipha/pmaports-mirror/tree/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep)
while this assignment's duplicate PR #28 was open; this assignment's draft
package was not merged and PR #28 was closed without merging. The merged port
pins `linux-postmarketos-qcom-sm8250=7.2.0_git20261010-r0`, omits the
proprietary firmware dependency, and documents provenance in
`devices/oneplus-instantnoodlep/README.md`.

`tools/test_oneplus_instantnoodlep.py` now checks the merged package:
package metadata, pinned dependency, exact `source=`/`sha512sums` coverage,
upstream boot parameters, and the `build()`/`package()` DTBO round-trip with
`devicepkg_*` stubbed (when `dtc` is available). All checks pass locally.
