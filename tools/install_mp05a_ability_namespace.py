#!/usr/bin/env python3
"""Install Mercury's compact modern ability namespace into pokeplatinum.

This stage intentionally installs constants and UI text only.  It does not
assign the new abilities to species yet, so unsupported mechanics cannot leak
into normal gameplay before their battle hooks are ported.

Platinum stores species and Pokemon ability IDs in u8 fields.  The compact
Mercury namespace therefore keeps vanilla IDs 0..123 unchanged and fills
124..255 with 132 modern abilities actually used by base species #1..1025.
Four stateful abilities are deliberately deferred rather than aliased.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--namespace",
        type=Path,
        default=Path("data/modern_ability_namespace.json"),
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mp05a-ability-namespace.json"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    cfg = load_json(args.namespace)
    rows = sorted(cfg["abilities"], key=lambda x: int(x["internal_id"]))

    if len(rows) != 132:
        raise SystemExit(f"expected 132 compact modern abilities, got {len(rows)}")
    if rows[0]["internal_id"] != 124 or rows[-1]["internal_id"] != 255:
        raise SystemExit("compact ability IDs must occupy 124..255 exactly")

    ability_registry = pt / "generated" / "abilities.txt"
    current = [
        line.strip()
        for line in ability_registry.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(current) != 124:
        raise SystemExit(
            f"expected native Platinum ability registry length 124, got {len(current)}"
        )
    if current[0] != "ABILITY_NONE" or current[-1] != "ABILITY_BAD_DREAMS":
        raise SystemExit("native Platinum ability registry boundary changed")

    for row in rows:
        expected = int(row["internal_id"])
        if expected != len(current):
            raise SystemExit(
                f"ability namespace gap: expected internal ID {len(current)}, got {expected}"
            )
        token = row["token"]
        if token in current:
            raise SystemExit(f"duplicate ability token: {token}")
        current.append(token)

    if len(current) != 256:
        raise SystemExit(f"final compact ability registry must be 256 entries, got {len(current)}")

    ability_registry.write_text("\n".join(current) + "\n", encoding="utf-8")

    text_specs = [
        ("ability_names.json", "pl_msg_00000610_", False, False),
        ("ability_names_uppercase.json", "pl_msg_00000611_", True, False),
        ("ability_descriptions.json", "pl_msg_00000612_", False, True),
    ]

    for filename, prefix, uppercase, description in text_specs:
        path = pt / "res" / "text" / filename
        data = load_json(path)
        messages = data["messages"]
        if len(messages) != 124:
            raise SystemExit(
                f"{filename}: expected 124 native messages, got {len(messages)}"
            )

        for row in rows:
            idx = int(row["internal_id"])
            name = str(row["display_name"])
            if uppercase:
                value = name.upper()
            elif description:
                value = [
                    "Modern ability effect\n",
                    "support pending.",
                ]
            else:
                value = name
            messages.append({
                "id": f"{prefix}{idx:05d}",
                "en_US": value,
            })

        if len(messages) != 256:
            raise SystemExit(f"{filename}: expected 256 messages, got {len(messages)}")
        save_json(path, data)

    report = {
        "gate": "MP05A_COMPACT_ABILITY_NAMESPACE",
        "architecture": cfg["architecture"],
        "vanilla_ids": [0, 123],
        "modern_ids": [124, 255],
        "modern_abilities_added": len(rows),
        "deferred_stateful_abilities": cfg["deferred_stateful_abilities"],
        "species_assignment": "not_yet",
        "mechanics_status": "pending",
        "result": "PASS",
    }
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
