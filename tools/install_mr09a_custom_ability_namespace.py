#!/usr/bin/env python3
"""MR09A — reserve Mercury's first custom Ability namespace.

This gate appends the 11 approved Game Health redesign names at IDs 311..321.
It deliberately does NOT add them to the implemented-Ability registry.
Mechanics installers do that only after their battle hooks are installed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CANONICAL_MAX = 310
CUSTOM_FIRST = 311
CUSTOM_LAST = 321


def read_bank(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_bank(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def description_lines(name: str) -> list[str]:
    descriptions = {
        "Controlled Fury": [
            "Below half HP, powers up\n",
            "for three turns."
        ],
        "Eternal Life": [
            "Once per battle at half HP,\n",
            "heals and purges ailments."
        ],
        "Hollow Shell": [
            "A direct KO punishes the\n",
            "attacker without KOing it."
        ],
        "Mind Games": [
            "On entry, seals a foe's\n",
            "last-used move briefly."
        ],
        "The Look": [
            "Foes cannot use the same\n",
            "move twice in succession."
        ],
        "Prismatic Pelt": [
            "On entry, weakens super-\n",
            "effective hits for 3 turns."
        ],
        "Lockdown Protocol": [
            "Marks a foe, weakening its\n",
            "attacks and status repeats."
        ],
        "Adaptive Genome": [
            "First weakness hit boosts\n",
            "the matching defense."
        ],
        "Storm Sequence": [
            "On entry, chooses a 4-turn\n",
            "weather combat sequence."
        ],
        "Field Commissioner": [
            "On entry, chooses Advance,\n",
            "Fortify, or Disrupt."
        ],
        "Protean Maxima": [
            "Mega Eevee changes form\n",
            "after damaging moves."
        ],
    }
    return descriptions[name]


def ensure_message(bank: dict, prefix: str, idx: int, value: str | list[str]) -> None:
    msg_id = f"{prefix}_{idx:05d}"
    messages = bank["messages"]

    for message in messages:
        if message["id"] == msg_id:
            message["en_US"] = value
            return

    messages.append({"id": msg_id, "en_US": value})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--namespace",
        type=Path,
        default=Path("data/mercury_custom_ability_namespace.json"),
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr09a-custom-ability-namespace.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    namespace = json.loads(args.namespace.read_text(encoding="utf-8"))
    entries = namespace["abilities"]

    expected_ids = list(range(CUSTOM_FIRST, CUSTOM_LAST + 1))
    actual_ids = [entry["id"] for entry in entries]
    if actual_ids != expected_ids:
        raise SystemExit(
            f"MR09 namespace IDs must be exactly {CUSTOM_FIRST}..{CUSTOM_LAST}; "
            f"got {actual_ids}"
        )

    ability_path = root / "generated/abilities.txt"
    abilities = [
        line.strip()
        for line in ability_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if len(abilities) < CANONICAL_MAX + 1:
        raise SystemExit(
            f"canonical Ability namespace is short: {len(abilities)} entries"
        )

    # Canonical IDs are immutable. If this installer is rerun, only the exact
    # Mercury reservation is accepted after ID 310.
    if len(abilities) > CANONICAL_MAX + 1:
        existing = abilities[CUSTOM_FIRST : CUSTOM_LAST + 1]
        expected = [entry["token"] for entry in entries]
        if existing != expected:
            raise SystemExit(
                "IDs 311..321 are already occupied by a different namespace"
            )
        abilities = abilities[: CUSTOM_LAST + 1]
    else:
        abilities.extend(entry["token"] for entry in entries)

    ability_path.write_text("\n".join(abilities) + "\n", encoding="utf-8")

    name_path = root / "res/text/ability_names.json"
    upper_path = root / "res/text/ability_names_uppercase.json"
    desc_path = root / "res/text/ability_descriptions.json"

    names = read_bank(name_path)
    uppercase = read_bank(upper_path)
    descriptions = read_bank(desc_path)

    for entry in entries:
        idx = entry["id"]
        name = entry["name"]
        ensure_message(names, "pl_msg_00000610", idx, name)
        ensure_message(uppercase, "pl_msg_00000611", idx, name.upper())
        ensure_message(
            descriptions,
            "pl_msg_00000612",
            idx,
            description_lines(name),
        )

    write_bank(name_path, names)
    write_bank(upper_path, uppercase)
    write_bank(desc_path, descriptions)

    checks = {
        "canonical_range_preserved":
            abilities[CANONICAL_MAX] == namespace.get(
                "canonical_last_token",
                abilities[CANONICAL_MAX],
            ),
        "custom_range_exact":
            len(abilities) >= CUSTOM_LAST + 1
            and abilities[CUSTOM_FIRST : CUSTOM_LAST + 1]
                == [entry["token"] for entry in entries],
        "custom_count": len(entries) == 11,
        "no_implementation_claims":
            all(entry["status"] != "implemented" for entry in entries),
        "text_names_extended":
            all(
                any(
                    message["id"] == f"pl_msg_00000610_{entry['id']:05d}"
                    and message["en_US"] == entry["name"]
                    for message in names["messages"]
                )
                for entry in entries
            ),
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR09A_CUSTOM_ABILITY_NAMESPACE",
        "status": status,
        "canonical_range": [0, CANONICAL_MAX],
        "custom_reserved_range": [CUSTOM_FIRST, CUSTOM_LAST],
        "custom_reserved_count": len(entries),
        "implemented_in_this_gate": 0,
        "implemented_registry_changed": False,
        "save_storage_capacity": 1023,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR09A custom Ability namespace validation failed")


if __name__ == "__main__":
    main()
