import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
DEVICE = ROOT / "devices" / "oneplus-instantnoodlep"


def shell_values(path, names):
    script = '. "$1"; printf "%s\\0" ' + " ".join(f'"${name}"' for name in names)
    result = subprocess.run(
        ["sh", "-eu", "-c", script, "sh", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return dict(zip(names, result.stdout.split("\0")[:-1], strict=True))


def test_package_metadata_and_source_checksums():
    names = ("pkgname", "pkgver", "pkgrel", "arch", "depends", "makedepends", "source", "sha512sums")
    package = shell_values(DEVICE / "APKBUILD", names)
    assert (package["pkgname"], package["pkgver"], package["arch"]) == (
        "device-oneplus-instantnoodlep", "7", "aarch64"
    )
    assert set(package["depends"].split()) == {
        "linux-postmarketos-qcom-sm8250=7.2.0_git20261010-r0", "mkbootimg", "postmarketos-base"
    }
    assert set(package["makedepends"].split()) == {"devicepkg-dev", "dtc"}
    sources = set(package["source"].split())
    assert sources == {"deviceinfo", "kernel-cmdline.conf", "sm8250-oneplus-instantnoodlep-empty.dts"}
    checksums = {name: digest for digest, name in (line.split() for line in package["sha512sums"].splitlines() if line)}
    assert set(checksums) == sources
    for name in sources:
        assert hashlib.sha512((DEVICE / name).read_bytes()).hexdigest() == checksums[name]


def test_deviceinfo_matches_upstream_boot_parameters():
    names = (
        "deviceinfo_codename", "deviceinfo_arch", "deviceinfo_dtb", "deviceinfo_flash_method",
        "deviceinfo_header_version", "deviceinfo_flash_fastboot_partition_rootfs",
        "deviceinfo_flash_fastboot_partition_dtbo", "deviceinfo_super_partitions",
    )
    values = shell_values(DEVICE / "deviceinfo", names)
    assert list(values.values()) == [
        "oneplus-instantnoodlep", "aarch64", "qcom/sm8250-oneplus-instantnoodlep", "fastboot",
        "2", "super", "dtbo", "/dev/sda14 /dev/sda14",
    ]


@pytest.mark.skipif(shutil.which("dtc") is None, reason="device-tree-compiler is not installed")
def test_dtbo_build_and_install_with_stubbed_devicepkg(tmp_path):
    srcdir = tmp_path / "src"
    srcdir.mkdir()
    shutil.copy(DEVICE / "sm8250-oneplus-instantnoodlep-empty.dts", srcdir)
    pkgdir = tmp_path / "pkg"
    script = (
        '. "$1"; startdir="$2"; srcdir="$3"; pkgdir="$4"; '
        'devicepkg_build() { :; }; devicepkg_package() { :; }; build; package'
    )
    subprocess.run(
        ["sh", "-eu", "-c", script, "sh", str(DEVICE / "APKBUILD"), str(DEVICE), str(srcdir), str(pkgdir)],
        check=True,
    )
    result = subprocess.run(
        ["dtc", "-I", "dtb", "-O", "dts", str(pkgdir / "boot" / "dtbo.img")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert 'compatible = "qcom,kona";' in result.stdout
