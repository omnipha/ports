---
date: 2026-11-04
issue: ports#26
subsystem: ports
result: confirmed
---
# OnePlus 8 Pro package port

Ported the pmaports testing package version 7 from mirror commit
[dfb010f5b9885d185d089b6e1e493030062f9756](https://github.com/omnipha/pmaports-mirror/tree/dfb010f5b9885d185d089b6e1e493030062f9756/device/testing/device-oneplus-instantnoodlep).
The package requires the command-line and DTS inputs as well as deviceinfo;
`dtc -O dtb` compiled the upstream DTS successfully.

The kernel dependency is pinned to package `linux-postmarketos-qcom-sm8250`
version `7.2.0_git20261010-r0`, corresponding to tag
`sm8250-7.2.0_git20261010` in [linux-sm8250 UPSTREAM.md](https://github.com/omnipha/linux-sm8250/blob/aff10181998c2123182c0dc464aba9f40a0dfec4/UPSTREAM.md).
The proprietary firmware dependency is omitted; extraction instructions and
checksums for this device remain to be established under the repository policy.
This is packaging only, not evidence of a build, boot, flashing, or hardware
functionality.
