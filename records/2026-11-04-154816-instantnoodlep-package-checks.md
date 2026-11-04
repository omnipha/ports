---
date: 2026-11-04
issue: ports#26
subsystem: packaging-tests
result: confirmed
---
# instantnoodlep package checks

Added `tools/test_oneplus_instantnoodlep.py`: focused tests that source the
APKBUILD and deviceinfo in a subshell to verify package metadata, the pinned
`linux-postmarketos-qcom-sm8250=7.2.0_git20261010-r0` dependency, exact
`source=`/`sha512sums` coverage, the upstream boot parameters, and (when `dtc`
is installed) the `build()`/`package()` steps with `devicepkg_*` stubbed,
including a `dtbo.img` round-trip. All checks pass locally; `harvest.py
index`, `harvest.py check`, and the full `pytest tools/` suite are green.
