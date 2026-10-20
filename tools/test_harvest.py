"""Focused tests for the maintainer and release-status schema additions."""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import harvest  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "device.schema.json").read_text())


def validate(data):
    data = json.loads(json.dumps(data, default=str))
    return list(jsonschema.Draft202012Validator(SCHEMA, format_checker=jsonschema.FormatChecker()).iter_errors(data))


def laurel():
    return yaml.safe_load((ROOT / "devices" / "xiaomi-laurel" / "device.yaml").read_text())


def test_existing_database_validates_unchanged():
    for path in harvest.device_files():
        data = harvest.load(path)
        assert not validate(data), path
        assert not harvest.validate_consistency(path, data), path


def test_laurel_links_device_repo_and_hardware_tester_without_official_claim():
    data = laurel()
    assert data["device_repo"] == "https://github.com/omnipha/device-xiaomi-laurel"
    assert {"id": "sprintberlin", "role": "hardware-tester"} in data["maintainers"]
    assert data["release"]["status"] == "unreleased"


def test_maintainers_minimum_and_roles():
    data = laurel()
    data["maintainers"] = []
    assert validate(data)
    data["maintainers"] = [{"id": "x", "role": "ceo"}]
    assert validate(data)


def test_device_repo_canonical():
    data = laurel()
    data["device_repo"] = "git@github.com:omnipha/device-xiaomi-laurel.git"
    assert validate(data)
    data["device_repo"] = "https://github.com/omnipha/device-other"
    assert not validate(data)
    assert harvest.validate_consistency("p", data)


def test_official_requires_gate_evidence():
    data = laurel()
    data["release"] = {"status": "official", "maintenance": "unowned"}
    assert validate(data)
    data["release"] = {"status": "official", "maintenance": "maintained"}
    assert validate(data)  # evidence missing
    data["release"] = {
        "status": "official",
        "maintenance": "maintained",
        "artifact": {
            "url": "https://github.com/omnipha/images/releases/download/device-xiaomi-laurel-v1/image.img",
            "sha256": "a" * 64,
            "manifest": "https://github.com/omnipha/images/releases/download/device-xiaomi-laurel-v1/manifest.json",
        },
        "evidence": {
            "ci_build": "https://ci.example/xiaomi-laurel/123",
            "flashing_rollback": "https://github.com/omnipha/device-xiaomi-laurel/blob/main/FLASHING.md",
            "physical_test": {
                "date": "2026-10-19",
                "tester": "sprintberlin",
                "boot": "works",
                "network": "works",
                "ssh": "works",
            },
        },
    }
    assert not validate(data)


def test_unreleased_rejects_evidence():
    data = laurel()
    data["release"] = {
        "status": "unreleased",
        "maintenance": "maintained",
        "evidence": {
            "ci_build": "https://ci.example/1",
            "flashing_rollback": "https://ci.example/2",
            "physical_test": {
                "date": "2026-10-19",
                "tester": "sprintberlin",
                "boot": "works",
                "network": "works",
                "ssh": "works",
            },
        },
    }
    assert validate(data)


def test_official_requires_named_release_owner():
    data = laurel()
    data["maintainers"] = [{"id": "sprintberlin", "role": "hardware-tester"}]
    data["release"] = {
        "status": "official",
        "maintenance": "maintained",
        "artifact": {
            "url": "https://github.com/omnipha/images/releases/download/device-xiaomi-laurel-v1/image.img",
            "sha256": "a" * 64,
            "manifest": "https://github.com/omnipha/images/releases/download/device-xiaomi-laurel-v1/manifest.json",
        },
        "evidence": {
            "ci_build": "https://ci.example/xiaomi-laurel/123",
            "flashing_rollback": "https://github.com/omnipha/device-xiaomi-laurel/blob/main/FLASHING.md",
            "physical_test": {
                "date": "2026-10-19",
                "tester": "sprintberlin",
                "boot": "works",
                "network": "works",
                "ssh": "works",
            },
        },
    }
    assert not validate(data)
    assert harvest.validate_consistency("p", data)
    data["maintainers"].append({"id": "someone", "role": "maintainer"})
    data["maintainers"].append({"id": "owner", "role": "release-owner"})
    assert not harvest.validate_consistency("p", data)


def test_maintained_requires_maintainer_role():
    data = laurel()
    data["release"] = {"status": "unreleased", "maintenance": "maintained"}
    data["maintainers"] = [{"id": "sprintberlin", "role": "hardware-tester"}]
    assert harvest.validate_consistency("p", data)
    data["maintainers"].append({"id": "someone", "role": "maintainer"})
    assert not harvest.validate_consistency("p", data)


def test_official_distinguished_from_upstream_support():
    data = laurel()
    assert data["upstream_os"]["ut"]["supported"] is True
    assert data["release"]["status"] == "unreleased"


def test_check_command_passes():
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "harvest.py"), "check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "check: ok" in result.stdout


def test_installability_is_not_inferred_from_source_or_definition():
    data = laurel()
    assert data["status"]["boot"] == "works"
    assert data["image"] == "images/xiaomi-laurel"
    assert data["release"]["status"] == "unreleased"
    data["release"] = {"status": "testing", "maintenance": "unowned"}
    assert validate(data)  # missing artifact and evidence


def test_new_hardware_claim_requires_test_record():
    baseline = json.loads(harvest.LEGACY_STATUSES.read_text())
    data = laurel()
    assert not harvest.validate_status_evidence("p", data, baseline)
    data["status"]["cameras"] = "broken"
    assert harvest.validate_status_evidence("p", data, baseline)  # old broken claim not grandfathered
    data["status"]["cameras"] = "works"
    assert harvest.validate_status_evidence("p", data, baseline)
    data["status_evidence"] = {"cameras": {
        "date": "2026-10-21", "variant": "4/64 Mi A3", "url": "https://github.com/omnipha/device-xiaomi-laurel/issues/1"
    }}
    assert not harvest.validate_status_evidence("p", data, baseline)
    assert not validate(data)
    data["status_evidence"]["ghost"] = data["status_evidence"]["cameras"]
    assert harvest.validate_status_evidence("p", data, baseline)


def test_new_device_cannot_inherit_status_exception():
    baseline = json.loads(harvest.LEGACY_STATUSES.read_text())
    data = laurel()
    data["codename"] = "new-device"
    assert harvest.validate_status_evidence("p", data, baseline)


def test_status_enum_and_stage():
    data = laurel()
    data["status"]["wifi"] = "awesome"
    assert validate(data)
    data["status"]["wifi"] = "works"
    data["project"]["stage"] = "nonsense"
    assert validate(data)


def test_catalog_is_generated_and_no_omnipha_image_is_claimed():
    catalog = harvest.render_catalog()
    assert catalog == harvest.CATALOG.read_text()
    assert "xiaomi-laurel" in catalog and "nothing-asteroids" in catalog
    assert "0 with a tested or official Omnipha image" in catalog
    assert "No device" not in catalog  # device inventory is present, but releases are not
