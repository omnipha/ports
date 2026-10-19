#!/usr/bin/env python3
"""Maintain the Omnipha device database.

Subcommands:
  ut        refresh upstream_os.ut in every device.yaml from devices.ubuntu-touch.io
  index     rebuild devices.json (aggregate of all device.yaml)
  check     validate every device.yaml against schema/device.schema.json and
            fail if devices.json is stale (used by CI)

upstream_os.nura is curated by hand: the postmarketOS/Nura wiki lists devices
through Cargo queries that are not machine-readable. harvest never edits it.

Requires: pyyaml, jsonschema.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEVICES = ROOT / "devices"
INDEX = ROOT / "devices.json"
SCHEMA = ROOT / "schema" / "device.schema.json"
UT_INDEX_URL = "https://devices.ubuntu-touch.io/"
UT_SOURCE = "devices.ubuntu-touch.io"
DEVICE_REPO_RE = re.compile(r"^https://github\.com/omnipha/device-[a-z0-9]+(?:-[a-z0-9]+)*$")


def device_files():
    return sorted(p for p in DEVICES.glob("*/device.yaml"))


def load(path):
    return yaml.safe_load(path.read_text())


def parse_ut_index(html):
    """Return {key: attrs} from the data-* attributes of the device list."""
    out = {}
    for m in re.finditer(r'<li class="device-name"([^>]*)>', html):
        attrs = dict(re.findall(r"data-([\w]+)=\"([^\"]*)\"", m.group(1)))
        if attrs.get("codename"):
            out[attrs["codename"]] = attrs
    return out


def dump_block(upstream_os):
    return yaml.safe_dump(
        {"upstream_os": upstream_os}, sort_keys=False, allow_unicode=True, width=100
    )


def write_upstream_os(path, upstream_os):
    text = path.read_text()
    block = dump_block(upstream_os)
    pattern = re.compile(r"(?ms)^upstream_os:.*?(?=^\S|\Z)")
    if pattern.search(text):
        text = pattern.sub(lambda _m: block + "\n", text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + block
    path.write_text(text.rstrip("\n") + "\n")


def cmd_ut(args):
    if args.from_file:
        html = Path(args.from_file).read_text()
    else:
        req = urllib.request.Request(UT_INDEX_URL, headers={"User-Agent": "omnipha-harvest/0.1 (github.com/omnipha)"})
        html = urllib.request.urlopen(req, timeout=30).read().decode()
    index = parse_ut_index(html)
    if len(index) < 50:
        print(f"refusing to continue: only {len(index)} devices parsed, page layout changed?", file=sys.stderr)
        return 1
    today = date.today().isoformat()
    changed = 0
    for path in device_files():
        data = load(path)
        uos = data.setdefault("upstream_os", {})
        ut = uos.setdefault("ut", {})
        key = ut.get("key")
        if not key:
            print(f"skip {path.parent.name}: no upstream_os.ut.key", file=sys.stderr)
            continue
        live = index.get(key)
        before = dict(ut)
        ut["listed"] = live is not None
        if live:
            ut["supported"] = live.get("supported") == "1"
            ut["installer"] = live.get("installerAvailable") == "1"
            ut["release"] = live.get("release")
            ut["progress_pct"] = float(live["progress"]) if live.get("progress") else None
        else:
            for k in ("supported", "installer", "release", "progress_pct"):
                ut.pop(k, None)
        ut["source"] = UT_SOURCE
        if {k: v for k, v in ut.items() if k != "checked"} != {k: v for k, v in before.items() if k != "checked"}:
            changed += 1
            print(f"changed {path.parent.name}")
        ut["checked"] = today
        write_upstream_os(path, uos)
    print(f"ut: {len(index)} devices in upstream index, {changed} device(s) changed")
    return 0


def validate_consistency(path, data):
    """Return cross-field violations that JSON Schema cannot express alone."""
    messages = []
    repo = data.get("device_repo")
    codename = data.get("codename")
    if isinstance(repo, str) and isinstance(codename, str) and repo != f"https://github.com/omnipha/device-{codename}":
        messages.append(f"{path}: device_repo must be https://github.com/omnipha/device-{codename}")
    release = data.get("release") or {}
    maintainers = data.get("maintainers") or []
    roles = {
        item.get("role")
        for item in maintainers
        if isinstance(item, dict)
    }
    if release.get("maintenance") == "maintained" and "maintainer" not in roles:
        messages.append(f"{path}: maintained status requires a maintainer")
    if release.get("status") == "official" and "release-owner" not in roles:
        messages.append(f"{path}: official status requires a release-owner")
    evidence = release.get("evidence") or {}
    test = evidence.get("physical_test") or {}
    tester = test.get("tester")
    if tester and tester not in {
        item.get("id") for item in maintainers if isinstance(item, dict) and item.get("role") == "hardware-tester"
    }:
        messages.append(f"{path}: physical_test.tester must be a listed hardware-tester")
    return messages


def build_index():
    entries = []
    for path in device_files():
        data = load(path)
        entries.append({"id": path.parent.name, **data})
    return json.dumps(entries, indent=2, ensure_ascii=False, default=str) + "\n"


def cmd_index(_args):
    INDEX.write_text(build_index())
    print(f"devices.json: {len(device_files())} devices")
    return 0


def cmd_check(_args):
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    errors = 0
    for path in device_files():
        data = json.loads(json.dumps(load(path), default=str))
        if data.get("codename") != path.parent.name:
            print(f"{path}: codename must equal folder name", file=sys.stderr)
            errors += 1
        for message in validate_consistency(path, data):
            print(message, file=sys.stderr)
            errors += 1
        for err in jsonschema.Draft202012Validator(schema).iter_errors(data):
            print(f"{path}: {'/'.join(map(str, err.path))}: {err.message}", file=sys.stderr)
            errors += 1
    if not INDEX.exists() or INDEX.read_text() != build_index():
        print("devices.json is stale: run tools/harvest.py index", file=sys.stderr)
        errors += 1
    print("check:", "ok" if not errors else f"{errors} error(s)")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_ut = sub.add_parser("ut", help="refresh Ubuntu Touch status")
    p_ut.add_argument("--from-file", help="use a saved copy of the UBports index page")
    p_ut.set_defaults(func=cmd_ut)
    sub.add_parser("index", help="rebuild devices.json").set_defaults(func=cmd_index)
    sub.add_parser("check", help="validate and verify the index is fresh").set_defaults(func=cmd_check)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
