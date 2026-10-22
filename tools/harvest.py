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
LEGACY_STATUSES = ROOT / "schema" / "legacy-statuses.json"
CATALOG = ROOT / "DEVICES.md"
GPU_CATALOG = ROOT / "GPU.md"
GPUS = ROOT / "hardware" / "gpus.yaml"
SOCS = ROOT / "hardware" / "socs.yaml"
UT_INDEX_URL = "https://devices.ubuntu-touch.io/"
UT_SOURCE = "devices.ubuntu-touch.io"


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
    if data.get("project", {}).get("stage") == "field-tested" and not data.get("status"):
        messages.append(f"{path}: field-tested requires a hardware status matrix")
    if release.get("status") in ("testing", "official") and data.get("project", {}).get("stage") != "field-tested":
        messages.append(f"{path}: a released image requires a field-tested device")
    evidence = release.get("evidence") or {}
    test = evidence.get("physical_test") or {}
    tester = test.get("tester")
    if tester and tester not in {
        item.get("id") for item in maintainers if isinstance(item, dict) and item.get("role") == "hardware-tester"
    }:
        messages.append(f"{path}: physical_test.tester must be a listed hardware-tester")
    return messages


def validate_status_evidence(path, data, legacy):
    """Require a public test record on every NEW assessed status claim.

    Historical status values have no reliable public evidence index yet; these
    are grandfathered per device+component+exact value only. Adding a new
    device or changing a claim cannot silently inherit that exemption.
    """
    errors = []
    status = data.get("status") or {}
    records = data.get("status_evidence") or {}
    for component in records:
        if component not in status:
            errors.append(f"{path}: status_evidence.{component} has no status entry")
    for component, value in status.items():
        if value == "untested":
            continue
        if component in records:
            continue
        if legacy.get(data.get("codename"), {}).get(component) == value:
            continue
        if component not in records:
            errors.append(f"{path}: new status.{component}={value} requires status_evidence.{component} (date, variant, public URL)")
    return errors


def build_index():
    entries = []
    for path in device_files():
        data = load(path)
        entries.append({"id": path.parent.name, **data})
    return json.dumps(entries, indent=2, ensure_ascii=False, default=str) + "\n"


def render_catalog():
    """Discoverable contributor index; derived from device.yaml, never hand-edited."""
    data = json.loads(build_index())
    data.sort(key=lambda d: (d.get("project", {}).get("stage", "research") == "research", d["name"].casefold(), d["id"]))
    available = sum(d.get("release", {}).get("status") in ("testing", "official") for d in data)
    tested = sum(d.get("project", {}).get("stage") == "field-tested" for d in data)
    lines = [
        "# Omnipha devices",
        "",
        "Generated by `python3 tools/harvest.py index` from `devices/*/device.yaml`. Do not edit by hand.",
        f"{len(data)} tracked, {tested} with field-tested hardware, {available} with a tested or official Omnipha image.",
        "A tracked device, a working subsystem or an upstream OS image is **not** an installable Omnipha release.",
        "Only `release.status: testing` or `official` with a public artifact, checksum, manifest and measured test/rollback evidence means an installable image.",
        "",
        "To contribute: open the device workspace if linked, otherwise propose a device port using [CONTRIBUTING.md](CONTRIBUTING.md). Read status and evidence before claiming that hardware works. Never flash from `image.yaml` alone.",
        "",
        "| Phone | Omnipha progress | Omnipha image | Reported hardware | Contribute |",
        "| --- | --- | --- | --- | --- |",
    ]
    for d in data:
        slug = d["id"]
        entry = f"https://github.com/omnipha/ports/tree/main/devices/{slug}"
        stage = d.get("project", {}).get("stage", "research")
        release = d.get("release", {}).get("status", "unreleased")
        statuses = d.get("status") or {}
        hardware = ", ".join(f"{key}: {value}" for key, value in sorted(statuses.items())) or "no Omnipha hardware tests recorded"
        contributor = d.get("device_repo") or d.get("project", {}).get("mission") or (
            "https://github.com/omnipha/ports/issues/new/choose"
        )
        label = "Device issues" if d.get("device_repo") else (
            "Bring-up mission" if d.get("project", {}).get("mission") else "Open a device issue"
        )
        lines.append(f"| [{d['name']}]({entry}) (`{slug}`) | {stage} | {release} | {hardware} | [{label}]({contributor}) |")
    return "\n".join(lines) + "\n"


def load_hardware():
    return load(GPUS) or {}, load(SOCS) or {}


def validate_hardware(gpus, socs):
    """Cross-reference and provenance rules for hardware/gpus.yaml and socs.yaml."""
    errors = []
    for gpu_id, gpu in gpus.items():
        for key in ("vendor", "name", "benchmarks"):
            if key not in gpu:
                errors.append(f"gpus.yaml: {gpu_id} missing {key}")
        for bench, row in (gpu.get("benchmarks") or {}).items():
            for key in ("avg", "min", "max", "n", "source", "checked"):
                if key not in row:
                    errors.append(f"gpus.yaml: {gpu_id}.{bench} missing {key}")
            if all(k in row for k in ("avg", "min", "max")) and not row["min"] <= row["avg"] <= row["max"]:
                errors.append(f"gpus.yaml: {gpu_id}.{bench} requires min <= avg <= max")
    known = {path.parent.name: load(path) for path in device_files()}
    soc_ids = {d.get("soc") for d in known.values()}
    for soc_id, row in socs.items():
        if row.get("gpu") not in gpus:
            errors.append(f"socs.yaml: {soc_id} references unknown gpu {row.get('gpu')!r}")
        for key in ("source", "checked"):
            if key not in row:
                errors.append(f"socs.yaml: {soc_id} missing {key}")
        if soc_id not in soc_ids:
            errors.append(f"socs.yaml: {soc_id} matches no device soc")
    return errors


def gpu_rows():
    """One row per device: GPU model, external benchmarks, max RAM and Linux GPU status."""
    gpus, socs = load_hardware()
    rows = []
    for path in device_files():
        data = load(path)
        soc = socs.get(data.get("soc"))
        gpu = gpus.get(soc["gpu"]) if soc else None
        bench = (gpu or {}).get("benchmarks") or {}
        rams = [v.get("ram_gb") for v in data.get("variants") or [] if v.get("ram_gb")]
        rows.append({
            "id": path.parent.name,
            "name": data["name"],
            "soc": data.get("soc") or "unknown",
            "soc_name": data.get("soc_name") or "",
            "gpu": gpu["name"] if gpu else None,
            "wild_life": (bench.get("3dmark_wild_life_extreme_unlimited") or {}).get("avg"),
            "opencl": (bench.get("geekbench6_opencl") or {}).get("avg"),
            "max_ram": max(rams) if rams else None,
            "linux_gpu": (data.get("status") or {}).get("gpu", "untested"),
        })
    return rows


def render_gpu_catalog():
    """GPU and RAM view for choosing a device for GPU workloads; derived, never hand-edited."""
    rows = gpu_rows()
    mapped = [r for r in rows if r["gpu"]]
    mapped.sort(key=lambda r: (-(r["wild_life"] or 0), -(r["max_ram"] or 0), r["name"].casefold()))
    unmapped = sorted((r for r in rows if not r["gpu"]), key=lambda r: r["name"].casefold())
    lines = [
        "# Omnipha devices by GPU",
        "",
        "Generated by `python3 tools/harvest.py index` from `devices/*/device.yaml` and `hardware/*.yaml`. Do not edit by hand.",
        "",
        "Use this to pick hardware for GPU workloads such as local language models. Two different things are shown and must not be mixed up:",
        "",
        "- **Android benchmark** columns are external results for the GPU, averaged by the cited source (see `hardware/gpus.yaml`). They rank GPUs. They do not predict Linux performance.",
        "- **Linux GPU** is what we observed on a test unit (`status.gpu` in `device.yaml`). `untested` means nobody has checked it under Linux.",
        "",
        "**Max RAM** is the largest sold variant. For language models RAM usually limits model size before the GPU does. A device is not suitable just because it appears here: check the Linux GPU column and [DEVICES.md](DEVICES.md).",
        "",
        f"{len(mapped)} of {len(rows)} devices have a known GPU. {len(unmapped)} are not mapped yet.",
        "",
        "| Phone | SoC | GPU | 3DMark Wild Life Extreme | Geekbench 6 OpenCL | Max RAM | Linux GPU |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in mapped:
        wl = r["wild_life"] if r["wild_life"] is not None else "n/a"
        cl = r["opencl"] if r["opencl"] is not None else "n/a"
        ram = f"{r['max_ram']:g} GB" if r["max_ram"] else "unknown"
        soc = f"{r['soc_name']} (`{r['soc']}`)" if r["soc_name"] else f"`{r['soc']}`"
        lines.append(
            f"| [{r['name']}](https://github.com/omnipha/ports/tree/main/devices/{r['id']}) | {soc} | {r['gpu']} | {wl} | {cl} | {ram} | {r['linux_gpu']} |"
        )
    lines += [
        "",
        "## GPU not mapped yet",
        "",
        "To add one, put the GPU into `hardware/gpus.yaml` with a cited source and map its SoC in `hardware/socs.yaml`.",
        "",
        ", ".join(f"{r['name']} (`{r['soc']}`)" for r in unmapped) or "none",
        "",
    ]
    return "\n".join(lines)


def cmd_index(_args):
    INDEX.write_text(build_index())
    CATALOG.write_text(render_catalog())
    GPU_CATALOG.write_text(render_gpu_catalog())
    print(f"devices.json: {len(device_files())} devices")
    return 0


def cmd_check(_args):
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    legacy = json.loads(LEGACY_STATUSES.read_text())
    errors = 0
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for path in device_files():
        data = json.loads(json.dumps(load(path), default=str))
        if data.get("codename") != path.parent.name:
            print(f"{path}: codename must equal folder name", file=sys.stderr)
            errors += 1
        for message in validate_consistency(path, data) + validate_status_evidence(path, data, legacy):
            print(message, file=sys.stderr)
            errors += 1
        for err in validator.iter_errors(data):
            print(f"{path}: {'/'.join(map(str, err.path))}: {err.message}", file=sys.stderr)
            errors += 1
    if not INDEX.exists() or INDEX.read_text() != build_index():
        print("devices.json is stale: run tools/harvest.py index", file=sys.stderr)
        errors += 1
    if not CATALOG.exists() or CATALOG.read_text() != render_catalog():
        print("DEVICES.md is stale: run tools/harvest.py index", file=sys.stderr)
        errors += 1
    for message in validate_hardware(*load_hardware()):
        print(message, file=sys.stderr)
        errors += 1
    if not GPU_CATALOG.exists() or GPU_CATALOG.read_text() != render_gpu_catalog():
        print("GPU.md is stale: run tools/harvest.py index", file=sys.stderr)
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
