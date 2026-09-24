#!/usr/bin/env python3
"""Audit Gen 5-9 move portability from pinned HG-Engine into Platinum.

Key observation: HG-Engine preserves the original Gen-IV move-effect numbering
for effects 0..276, then appends new effects from 277 onward. That lets Mercury
separate modern moves into two implementation lanes:

1. metadata-compatible moves: donor effect ID <= Platinum's highest native
   effect ID and can reuse the existing Platinum effect script slot.
2. engine-extension moves: donor effect ID is new and requires a new battle
   effect implementation before it can be considered canonical.

This tool does not modify the game. It produces the production queue for PT05C.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MOVE_DEFINE_RE = re.compile(r"^#define\s+(MOVE_[A-Z0-9_]+)\s+([0-9]+)\s*$", re.M)
EFFECT_DEFINE_RE = re.compile(r"^#define\s+(MOVE_EFFECT_[A-Z0-9_]+)\s+([0-9]+)\s*$", re.M)


def extract_block(text: str, token: str) -> str | None:
    marker = f"[{token}] = {{"
    start = text.find(marker)
    if start < 0:
        return None
    brace = text.find("{", start)
    depth = 0
    for pos in range(brace, len(text)):
        ch = text[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1]
    raise ValueError(f"unterminated block for {token}")


def capture(block: str, pattern: str):
    m = re.search(pattern, block)
    return m.group(1) if m else None


def canonical_assignment(block: str, field: str, value_pattern: str):
    expr = capture(block, rf"\.{re.escape(field)}\s*=\s*([^,\n]+)")
    if expr is None:
        return None
    direct = re.fullmatch(rf"\s*({value_pattern})\s*", expr)
    if direct:
        return direct.group(1)
    conditional = re.fullmatch(
        rf"\s*\(\(CHAMPIONS_[A-Z0-9_]+\)\s*\?\s*\(({value_pattern})\)"
        rf"\s*:\s*\(({value_pattern})\)\)\s*",
        expr,
    )
    if conditional:
        return conditional.group(2)
    raise SystemExit(f"could not parse canonical donor value for .{field}: {expr!r}")


def generation_for_move_id(move_id: int) -> int:
    if move_id <= 467:
        return 4
    if move_id <= 559:
        return 5
    if move_id <= 621:
        return 6
    if move_id <= 728:
        return 7
    if move_id <= 853:
        return 8
    return 9


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("pt05c-move-compatibility.json"))
    args = ap.parse_args()

    hg = args.hg_engine_root.resolve()
    pt = args.pokeplatinum_root.resolve()

    move_h = (hg / "include/constants/moves.h").read_text(errors="replace")
    effect_h = (hg / "include/constants/move_effects.h").read_text(errors="replace")
    moves_c = (hg / "data/Moves.c").read_text(errors="replace")

    donor_moves = {name: int(num) for name, num in MOVE_DEFINE_RE.findall(move_h)}
    donor_effects = {name: int(num) for name, num in EFFECT_DEFINE_RE.findall(effect_h)}
    # HG-Engine declares Fillet Away's effect in move_data.h as a guarded
    # compatibility define rather than in move_effects.h.
    donor_effects.setdefault("MOVE_EFFECT_ATK_SP_ATK_SPEED_UP_2_LOSE_HALF_MAX_HP", 303)

    pt_effect_lines = [
        x.strip()
        for x in (pt / "generated/move_battle_effects.txt").read_text().splitlines()
        if x.strip() and not x.lstrip().startswith("#")
    ]
    native_effect_max = len(pt_effect_lines) - 1

    rows = []
    missing_data = []
    generations = {str(g): {"total": 0, "metadata_compatible": 0, "engine_extension": 0} for g in range(5, 10)}
    new_effect_usage = {}

    for token, move_id in sorted(donor_moves.items(), key=lambda kv: kv[1]):
        if move_id < 468 or move_id > 922:
            continue
        gen = generation_for_move_id(move_id)
        block = extract_block(moves_c, token)
        if block is None:
            missing_data.append({"move": token, "id": move_id})
            continue

        effect_token = capture(block, r"\.effect\s*=\s*(MOVE_EFFECT_[A-Z0-9_]+)")
        if effect_token is None:
            missing_data.append({"move": token, "id": move_id, "reason": "effect_not_parsed"})
            continue
        effect_id = donor_effects.get(effect_token)
        if effect_id is None:
            missing_data.append({
                "move": token,
                "id": move_id,
                "reason": "effect_constant_missing",
                "effect": effect_token,
            })
            continue

        name = capture(block, r"\.name\s*=\s*\"([^\"]*)\"")
        split = canonical_assignment(block, "split", r"SPLIT_[A-Z]+")
        move_type = canonical_assignment(block, "type", r"TYPE_[A-Z0-9_]+")
        power = canonical_assignment(block, "power", r"[0-9]+")
        accuracy = canonical_assignment(block, "accuracy", r"[0-9]+")
        pp = canonical_assignment(block, "pp", r"[0-9]+")
        priority = canonical_assignment(block, "priority", r"-?[0-9]+")
        target = canonical_assignment(block, "target", r"RANGE_[A-Z0-9_]+")

        lane = "metadata_compatible" if effect_id <= native_effect_max else "engine_extension"
        generations[str(gen)]["total"] += 1
        generations[str(gen)][lane] += 1
        if lane == "engine_extension":
            new_effect_usage.setdefault(effect_token, {"effect_id": effect_id, "moves": []})["moves"].append(token)

        rows.append({
            "id": move_id,
            "generation": gen,
            "move": token,
            "name": name,
            "effect": effect_token,
            "effect_id": effect_id,
            "lane": lane,
            "split": split,
            "type": move_type,
            "power": int(power) if power is not None else None,
            "accuracy": int(accuracy) if accuracy is not None else None,
            "pp": int(pp) if pp is not None else None,
            "priority": int(priority) if priority is not None else None,
            "target": target,
        })

    report = {
        "gate": "PT05C_MOVE_COMPATIBILITY_AUDIT",
        "donor_move_range": [468, 922],
        "canonical_modern_moves_requested": 922 - 468 + 1,
        "parsed_moves": len(rows),
        "missing_move_data": missing_data,
        "platinum_native_effect_max": native_effect_max,
        "summary": {
            "metadata_compatible": sum(1 for r in rows if r["lane"] == "metadata_compatible"),
            "engine_extension": sum(1 for r in rows if r["lane"] == "engine_extension"),
            "unique_new_effects": len(new_effect_usage),
        },
        "by_generation": generations,
        "new_effect_usage": dict(sorted(new_effect_usage.items(), key=lambda kv: kv[1]["effect_id"])),
        "moves": rows,
        "next_steps": [
            "PT05C1 import all metadata-compatible modern moves in bulk",
            "PT05C2+ port the unique new battle-effect families, then enable their moves",
            "Use safe generic animations during engine bring-up; animation fidelity is a later non-blocking pass",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    if missing_data:
        raise SystemExit(f"move donor parse incomplete: {len(missing_data)} failures")
    if len(rows) != report["canonical_modern_moves_requested"]:
        raise SystemExit(f"expected 455 modern moves, parsed {len(rows)}")

    print(json.dumps({
        "gate": report["gate"],
        "parsed_moves": len(rows),
        "native_effect_max": native_effect_max,
        "summary": report["summary"],
        "by_generation": generations,
    }, indent=2))


if __name__ == "__main__":
    main()
