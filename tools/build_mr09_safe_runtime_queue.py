#!/usr/bin/env python3
"""Build MR09's conservative safe-runtime queue.

The queue deliberately excludes:
- every ability classified as new_engine_system;
- any non-new-engine row that still depends on a custom field/status system
  that is part of the pending Mercury mechanics review;
- canonical Elite Redux overrides from the custom-ID namespace. Those are
  patched onto their existing canonical IDs instead.

This tool DOES NOT claim mechanics are implemented. It creates a stable,
auditable work queue so runtime installers can only mark entries complete after
their actual battle hooks pass.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CUSTOM_FIRST_ID = 311
ABILITY_ID_CAPACITY_LAST = 1023

PENDING_SYSTEM_MARKERS = (
    "bleed",
    "bleeding",
    "fear",
    "scare",
    "scared",
    "enrage",
    "enraged",
    "toxic terrain",
    "eerie fog",
    "creeping thorns",
    "frostbite",
    "parasitic spores",
    "spore condition",
)

def slug_token(name: str) -> str:
    text = name.upper()
    text = text.replace("’", "").replace("'", "")
    text = text.replace(">", " GREATER ")
    text = re.sub(r"[^A-Z0-9]+", "_", text).strip("_")
    return "ABILITY_" + text

def has_pending_dependency(row: dict) -> list[str]:
    blob = " ".join(
        str(row.get(key, ""))
        for key in ("name", "mechanic_family", "exact_effect", "trigger", "restrictions")
    ).lower()
    return [marker for marker in PENDING_SYSTEM_MARKERS if marker in blob]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", type=Path, default=Path("data/mr09_custom_ability_intake.json"))
    ap.add_argument("--overrides", type=Path, default=Path("data/mr09_er_vanilla_ability_overrides.json"))
    ap.add_argument("--output", type=Path, default=Path("data/mr09_safe_runtime_queue.json"))
    args = ap.parse_args()

    intake = json.loads(args.intake.read_text(encoding="utf-8"))
    overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
    override_names = {row["name"] for row in overrides["entries"]}

    deferred_new_engine = []
    deferred_dependency = []
    canonical_overrides = []
    safe_custom = []

    for row in intake["abilities"]:
        if not row.get("implementation_ready", False):
            raise SystemExit(f"staging row unexpectedly not implementation-ready: {row['name']}")

        if row["implementation_class"] == "new_engine_system":
            deferred_new_engine.append(row)
            continue

        deps = has_pending_dependency(row)
        if deps:
            deferred_dependency.append({
                "name": row["name"],
                "mechanic_family": row["mechanic_family"],
                "implementation_class": row["implementation_class"],
                "dependencies": deps,
            })
            continue

        if row["name"] in override_names:
            canonical_overrides.append({
                "name": row["name"],
                "mechanic_family": row["mechanic_family"],
                "implementation_class": row["implementation_class"],
            })
            continue

        safe_custom.append(row)

    seen_names: set[str] = set()
    seen_tokens: set[str] = set()
    namespace = []
    for index, row in enumerate(safe_custom, start=CUSTOM_FIRST_ID):
        name = row["name"]
        token = slug_token(name)
        if name in seen_names:
            raise SystemExit(f"duplicate safe custom ability name: {name}")
        if token in seen_tokens:
            raise SystemExit(f"custom token collision: {token}")
        if index > ABILITY_ID_CAPACITY_LAST:
            raise SystemExit(
                f"safe custom namespace exceeds current save capacity: {index} > "
                f"{ABILITY_ID_CAPACITY_LAST}"
            )
        seen_names.add(name)
        seen_tokens.add(token)
        namespace.append({
            "id": index,
            "token": token,
            "name": name,
            "source": row["source"],
            "exact_effect": row["exact_effect"],
            "trigger": row["trigger"],
            "restrictions": row.get("restrictions", ""),
            "mechanic_family": row["mechanic_family"],
            "implementation_class": row["implementation_class"],
            "runtime_status": "queued_not_implemented",
        })

    payload = {
        "schema_version": 1,
        "phase": "MR09 conservative safe runtime queue",
        "policy": (
            "No pending custom battle-system decision may be smuggled into the "
            "safe lane. Runtime status changes only after a real battle hook is "
            "installed and validated."
        ),
        "counts": {
            "staged_total": len(intake["abilities"]),
            "deferred_new_engine_system": len(deferred_new_engine),
            "deferred_custom_system_dependency": len(deferred_dependency),
            "safe_canonical_er_overrides": len(canonical_overrides),
            "safe_custom_namespace": len(namespace),
            "safe_total": len(canonical_overrides) + len(namespace),
            "custom_id_first": CUSTOM_FIRST_ID,
            "custom_id_last": namespace[-1]["id"] if namespace else None,
            "remaining_ids_through_1023": (
                ABILITY_ID_CAPACITY_LAST - namespace[-1]["id"]
                if namespace else ABILITY_ID_CAPACITY_LAST - CUSTOM_FIRST_ID + 1
            ),
        },
        "canonical_overrides": canonical_overrides,
        "safe_custom_abilities": namespace,
        "deferred_custom_system_dependencies": deferred_dependency,
        "deferred_new_engine_names": [row["name"] for row in deferred_new_engine],
    }

    expected = {
        "staged_total": 883,
        "deferred_new_engine_system": 93,
        "deferred_custom_system_dependency": 38,
        "safe_canonical_er_overrides": 48,
        "safe_custom_namespace": 704,
        "safe_total": 752,
        "custom_id_first": 311,
        "custom_id_last": 1014,
        "remaining_ids_through_1023": 9,
    }
    if payload["counts"] != expected:
        raise SystemExit(
            "safe queue count drifted from the reviewed checkpoint:\n"
            + json.dumps({"expected": expected, "actual": payload["counts"]}, indent=2)
        )

    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["counts"], indent=2))

if __name__ == "__main__":
    main()
