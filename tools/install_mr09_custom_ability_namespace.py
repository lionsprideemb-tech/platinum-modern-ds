#!/usr/bin/env python3
"""MR09 — install Mercury custom Ability namespace 311..321.

This stage extends the already-installed canonical MP05 namespace with the
approved custom-health redesign set. It installs constants and text only.
Battle mechanics are certified separately by MR09 implementation passes.

The existing MP05 architecture already stores 10-bit Ability IDs (0..1023), so
this pass does not alter save layout, Pokémon struct widths, Summary structs,
or the locked MR07 visuals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CANONICAL_MAX = 310
CUSTOM_MIN = 311
CUSTOM_MAX = 321
CAPACITY_MAX = 1023


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def message(prefix: str, idx: int, value):
    return {"id": f"{prefix}_{idx:05d}", "en_US": value}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--namespace",
        type=Path,
        default=Path("data/mr09_custom_ability_namespace.json"),
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr09-custom-ability-namespace.json"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    cfg = load_json(args.namespace)
    rows = sorted(cfg["abilities"], key=lambda x: int(x["id"]))

    ids = [int(row["id"]) for row in rows]
    if ids != list(range(CUSTOM_MIN, CUSTOM_MAX + 1)):
        raise SystemExit(
            f"MR09 redesign IDs must be contiguous {CUSTOM_MIN}..{CUSTOM_MAX}, got {ids}"
        )

    if CUSTOM_MAX > CAPACITY_MAX:
        raise SystemExit("MR09 custom namespace exceeds MP05 10-bit Ability capacity")

    registry = pt / "generated" / "abilities.txt"
    abilities = [
        line.strip()
        for line in registry.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    # Idempotent success when this exact namespace is already present.
    expected_tokens = [row["token"] for row in rows]
    if len(abilities) >= CUSTOM_MAX + 1:
        if abilities[CUSTOM_MIN:CUSTOM_MAX + 1] != expected_tokens:
            raise SystemExit("existing 311..321 Ability namespace conflicts with MR09 reservation")
    else:
        if len(abilities) != CANONICAL_MAX + 1:
            raise SystemExit(
                f"expected canonical registry length {CANONICAL_MAX + 1}, got {len(abilities)}"
            )
        for row in rows:
            if row["token"] in abilities:
                raise SystemExit(f"duplicate Ability token before reserved ID: {row['token']}")
            if int(row["id"]) != len(abilities):
                raise SystemExit(
                    f"namespace gap: next ID is {len(abilities)}, row requested {row['id']}"
                )
            abilities.append(row["token"])
        registry.write_text("\n".join(abilities) + "\n", encoding="utf-8")

    text_specs = (
        ("ability_names.json", "pl_msg_00000610", "name"),
        ("ability_names_uppercase.json", "pl_msg_00000611", "upper"),
        ("ability_descriptions.json", "pl_msg_00000612", "description"),
    )

    for filename, prefix, mode in text_specs:
        path = pt / "res" / "text" / filename
        data = load_json(path)
        messages = data["messages"]

        if len(messages) < CANONICAL_MAX + 1:
            raise SystemExit(
                f"{filename}: canonical MP05 text bank not installed; got {len(messages)} entries"
            )

        if len(messages) >= CUSTOM_MAX + 1:
            # Validate IDs already occupying the reserved range.
            for row in rows:
                idx = int(row["id"])
                expected_id = f"{prefix}_{idx:05d}"
                if messages[idx].get("id") != expected_id:
                    raise SystemExit(
                        f"{filename}: conflicting message ID at {idx}: {messages[idx].get('id')}"
                    )
            continue

        if len(messages) != CANONICAL_MAX + 1:
            raise SystemExit(
                f"{filename}: expected {CANONICAL_MAX + 1} pre-MR09 entries, got {len(messages)}"
            )

        for row in rows:
            idx = int(row["id"])
            if mode == "name":
                value = row["display_name"]
            elif mode == "upper":
                value = row["display_name"].upper()
            else:
                value = row["description"]
            messages.append(message(prefix, idx, value))

        save_json(path, data)

    report = {
        "gate": "MERCURY_MR09_CUSTOM_ABILITY_NAMESPACE",
        "status": "PASS",
        "canonical_range_preserved": [0, CANONICAL_MAX],
        "custom_reserved_range": [CUSTOM_MIN, CUSTOM_MAX],
        "custom_reserved_count": len(rows),
        "runtime_capacity": [0, CAPACITY_MAX],
        "save_layout_changed": False,
        "mr07_ui_changed": False,
        "mechanics_installed": False,
        "implemented_registry_changed": False,
        "tokens": expected_tokens,
    }
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
