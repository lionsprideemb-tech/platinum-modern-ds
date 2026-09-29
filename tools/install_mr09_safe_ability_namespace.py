#!/usr/bin/env python3
"""Install MR09's conservative safe custom Ability namespace (IDs 311..1014).

This installs constants and player-facing text only. It deliberately does NOT
add any custom Ability to the implemented-Ability registry; individual runtime
batches own that responsibility after their mechanics are actually patched and
validated.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path

FIRST_ID = 311
LAST_ID = 1014
SAVE_CAPACITY_LAST = 1023


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def clean_text(value: str) -> str:
    value = value.replace("×", "x").replace("½", "half")
    value = value.replace("—", "-").replace("–", "-")
    value = value.replace("…", "...")
    value = value.replace("\\n", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", value).strip()


def description_lines(effect: str) -> list[str]:
    chunks = textwrap.wrap(
        clean_text(effect),
        width=30,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(chunks) > 4:
        chunks = chunks[:4]
        chunks[-1] = chunks[-1].rstrip(" ,;:-") + "..."
    return [line + ("\n" if i < len(chunks) - 1 else "") for i, line in enumerate(chunks)]


def extend_text_bank(path: Path, rows: list[dict], *, uppercase: bool = False, descriptions: bool = False) -> int:
    data = load_json(path)
    messages = data["messages"]
    if len(messages) != FIRST_ID:
        raise SystemExit(f"{path}: expected canonical bank length {FIRST_ID}, found {len(messages)}")

    prefix = messages[0]["id"].rsplit("_", 1)[0]
    for row in rows:
        idx = int(row["id"])
        if idx != len(messages):
            raise SystemExit(f"{path}: namespace gap at {idx}, current length {len(messages)}")
        if descriptions:
            value = description_lines(row["exact_effect"])
        else:
            name = clean_text(row["name"])
            value = name.upper() if uppercase else name
        messages.append({"id": f"{prefix}_{idx:05d}", "en_US": value})

    save_json(path, data)
    return len(messages)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--queue", type=Path, default=Path("data/mr09_safe_runtime_queue.json"))
    ap.add_argument("--report", type=Path, default=Path("mr09-safe-ability-namespace.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    queue = load_json(args.queue)
    rows = queue["safe_custom_abilities"]

    if len(rows) != 704:
        raise SystemExit(f"expected 704 safe custom Abilities, found {len(rows)}")
    if rows[0]["id"] != FIRST_ID or rows[-1]["id"] != LAST_ID:
        raise SystemExit("safe custom Ability IDs must occupy 311..1014")
    if LAST_ID > SAVE_CAPACITY_LAST:
        raise SystemExit("safe custom namespace exceeds the current 10-bit save capacity")

    registry = root / "generated/abilities.txt"
    current = [line.strip() for line in registry.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(current) != FIRST_ID:
        raise SystemExit(
            f"expected canonical Gen 1-9 registry length {FIRST_ID}, got {len(current)}; "
            "run the MP05 width/namespace foundation first"
        )
    if current[-1] != "ABILITY_POISON_PUPPETEER":
        raise SystemExit(f"unexpected canonical Ability tail: {current[-1]}")

    seen = set(current)
    for row in rows:
        expected = int(row["id"])
        if expected != len(current):
            raise SystemExit(f"safe namespace gap: expected {len(current)}, got {expected}")
        token = row["token"]
        if token in seen:
            raise SystemExit(f"duplicate Ability token: {token}")
        seen.add(token)
        current.append(token)

    registry.write_text("\n".join(current) + "\n", encoding="utf-8")

    name_count = extend_text_bank(root / "res/text/ability_names.json", rows)
    upper_count = extend_text_bank(root / "res/text/ability_names_uppercase.json", rows, uppercase=True)
    desc_count = extend_text_bank(root / "res/text/ability_descriptions.json", rows, descriptions=True)

    checks = {
        "safe_count_704": len(rows) == 704,
        "first_id_311": rows[0]["id"] == FIRST_ID,
        "last_id_1014": rows[-1]["id"] == LAST_ID,
        "within_10_bit_save_capacity": LAST_ID <= SAVE_CAPACITY_LAST,
        "nine_ids_reserved": SAVE_CAPACITY_LAST - LAST_ID == 9,
        "registry_length_1015": len(current) == LAST_ID + 1,
        "name_bank_length_1015": name_count == LAST_ID + 1,
        "uppercase_bank_length_1015": upper_count == LAST_ID + 1,
        "description_bank_length_1015": desc_count == LAST_ID + 1,
    }
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR09_SAFE_CUSTOM_ABILITY_NAMESPACE",
        "status": status,
        "custom_ids": [FIRST_ID, LAST_ID],
        "custom_abilities_added": len(rows),
        "remaining_ids_through_1023": SAVE_CAPACITY_LAST - LAST_ID,
        "species_assignment": "not_until_runtime_mechanics_certified",
        "implemented_registry_changed": False,
        "pending_custom_systems_installed": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR09 safe custom Ability namespace validation failed")


if __name__ == "__main__":
    main()
