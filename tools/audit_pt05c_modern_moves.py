#!/usr/bin/env python3
"""Audit Gen 5-9 canonical move compatibility for the Platinum runtime."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MOVE_DEFINE_RE = re.compile(r"^#define\s+(MOVE_[A-Z0-9_]+)\s+(\d+)\s*$", re.M)


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
                return text[start : pos + 1]
    return None


def capture(block: str, pattern: str) -> str | None:
    m = re.search(pattern, block)
    return m.group(1) if m else None


def canonical_assignment(block: str, field: str, value_pattern: str) -> str | None:
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


def load_lines(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("pt05c-modern-move-audit.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    move_defs = (hg / "include/constants/moves.h").read_text(errors="replace")
    donor_moves = dict(MOVE_DEFINE_RE.findall(move_defs))
    donor_moves = {
        k: int(v) - 3
        for k, v in donor_moves.items()
        if 471 <= int(v) <= 922
    }

    moves_c = (hg / "data/Moves.c").read_text(errors="replace")
    pt_effects = load_lines(pt / "generated/move_battle_effects.txt")
    pt_types = load_lines(pt / "generated/pokemon_types.txt")

    rows = []
    missing_blocks = []
    direct_effect = 0
    fallback_effect = 0
    unsupported_types = set()
    effects_missing = {}

    for token, move_id in sorted(donor_moves.items(), key=lambda kv: kv[1]):
        block = extract_block(moves_c, token)
        if block is None:
            missing_blocks.append({"id": move_id, "move": token})
            continue

        hg_effect = capture(block, r"\.effect\s*=\s*(MOVE_EFFECT_[A-Z0-9_]+)")
        move_type = canonical_assignment(block, "type", r"TYPE_[A-Z0-9_]+")
        split = canonical_assignment(block, "split", r"SPLIT_[A-Z0-9_]+")
        power = canonical_assignment(block, "power", r"\d+")
        accuracy = canonical_assignment(block, "accuracy", r"\d+")
        pp = canonical_assignment(block, "pp", r"\d+")

        candidate = None
        compatible = False
        if hg_effect:
            candidate = hg_effect.replace("MOVE_EFFECT_", "BATTLE_EFFECT_", 1)
            compatible = candidate in pt_effects
        if compatible:
            direct_effect += 1
        else:
            fallback_effect += 1
            if hg_effect:
                effects_missing.setdefault(hg_effect, 0)
                effects_missing[hg_effect] += 1

        if move_type and move_type not in pt_types:
            unsupported_types.add(move_type)

        rows.append({
            "id": move_id,
            "move": token,
            "donor_effect": hg_effect,
            "platinum_effect_candidate": candidate,
            "direct_effect_compatible": compatible,
            "type": move_type,
            "split": split,
            "power": int(power) if power else None,
            "accuracy": int(accuracy) if accuracy else None,
            "pp": int(pp) if pp else None,
        })

    report = {
        "gate": "PT05C_MODERN_MOVE_COMPATIBILITY_AUDIT",
        "range": [468, 919],
        "canonical_modern_move_count": len(donor_moves),
        "parsed_move_count": len(rows),
        "missing_move_blocks": missing_blocks,
        "direct_effect_compatible_count": direct_effect,
        "requires_new_effect_or_fallback_count": fallback_effect,
        "unsupported_types": sorted(unsupported_types),
        "distinct_missing_effects": len(effects_missing),
        "missing_effect_usage": dict(sorted(effects_missing.items(), key=lambda kv: (-kv[1], kv[0]))),
        "moves": rows,
        "recommended_order": [
            "expand level-up move ID capacity beyond 9 bits",
            "install move registry and metadata",
            "enable directly compatible effects",
            "port remaining shared effect handlers in batches",
            "finish unique complex move handlers",
        ],
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")

    if len(donor_moves) != 452:
        raise SystemExit(f"expected 452 post-Gen-IV canonical move IDs, found {len(donor_moves)}")
    if missing_blocks:
        raise SystemExit(f"missing {len(missing_blocks)} donor move blocks")

    print(json.dumps({
        "gate": report["gate"],
        "canonical_modern_move_count": len(donor_moves),
        "direct_effect_compatible_count": direct_effect,
        "requires_new_effect_or_fallback_count": fallback_effect,
        "distinct_missing_effects": len(effects_missing),
        "unsupported_types": sorted(unsupported_types),
    }, indent=2))


if __name__ == "__main__":
    main()
