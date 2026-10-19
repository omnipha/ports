"""Focused tests for the maintainer and release-status schema additions."""

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import harvest  # noqa: E402

SCHEMA = json.loads((ROOT / "schema" / "device.schema.json").read_text())


def validate(data):
    data = json.loads(json.dumps(data, default=str))
    return list(jsonschema.Draft202012Validator(SCHEMA).iter_errors(data))


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
