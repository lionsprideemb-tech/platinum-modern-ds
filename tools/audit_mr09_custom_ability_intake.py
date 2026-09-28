#!/usr/bin/env python3
"""Audit MR09 custom Ability intake without installing mechanics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
    "name",
    "source",
    "exact_effect",
    "trigger",
    "restrictions",
    "mechanic_family",
    "duplicate_status",
    "implementation_class",
    "approval_state",
    "implementation_ready",
)

APPROVAL_STATES = {"locked", "provisional", "redesign", "verify", "rejected"}
IMPLEMENTATION_CLASSES = {"existing_hook", "light_extension", "new_engine_system"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("intake", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr09-custom-ability-intake-audit.json"))
    args = ap.parse_args()

    data = json.loads(args.intake.read_text(encoding="utf-8"))
    abilities = data.get("abilities", [])

    errors: list[str] = []
    seen: set[str] = set()

    if data.get("status") != "STAGING_ONLY":
        errors.append("status must remain STAGING_ONLY until runtime implementation is explicitly approved")

    if data.get("policy", {}).get("assign_numeric_ids") is not False:
        errors.append("numeric Ability IDs must not be assigned during staging")

    if data.get("policy", {}).get("install_runtime_mechanics") is not False:
        errors.append("runtime mechanics must remain disabled during staging")

    for i, entry in enumerate(abilities):
        prefix = f"abilities[{i}]"
        missing = [key for key in REQUIRED if key not in entry]
        if missing:
            errors.append(f"{prefix}: missing required fields: {', '.join(missing)}")
            continue

        name = entry["name"]
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{prefix}: name must be non-empty")
        elif name in seen:
            errors.append(f"{prefix}: duplicate symbolic name {name}")
        else:
            seen.add(name)

        if "id" in entry or "ability_id" in entry or "numeric_id" in entry:
            errors.append(f"{prefix}: numeric IDs are forbidden in staging")

        if entry["approval_state"] not in APPROVAL_STATES:
            errors.append(f"{prefix}: invalid approval_state {entry['approval_state']}")

        if entry["implementation_class"] not in IMPLEMENTATION_CLASSES:
            errors.append(f"{prefix}: invalid implementation_class {entry['implementation_class']}")

        ready = entry["implementation_ready"] is True
        if ready:
            if entry["approval_state"] != "locked":
                errors.append(f"{prefix}: implementation_ready requires approval_state=locked")
            for key in ("source", "exact_effect", "trigger", "mechanic_family", "duplicate_status"):
                if not isinstance(entry[key], str) or not entry[key].strip():
                    errors.append(f"{prefix}: implementation_ready requires non-empty {key}")

    report = {
        "gate": "MERCURY_MR09_CUSTOM_ABILITY_STAGING_AUDIT",
        "status": "PASS" if not errors else "FAIL",
        "staging_only": True,
        "ability_count": len(abilities),
        "implementation_ready_count": sum(
            1 for entry in abilities if entry.get("implementation_ready") is True
        ),
        "errors": errors,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if errors:
        raise SystemExit("MR09 custom Ability intake audit failed")


if __name__ == "__main__":
    main()
