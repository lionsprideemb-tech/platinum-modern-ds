#!/usr/bin/env python3
"""Install canonical Gen 5-9 move registry/data into native Platinum resources.

This PT05C stage gives Platinum all canonical move IDs 0..922, preserving the
original 0..467 IDs exactly. Modern move metadata comes from the pinned
HG-Engine donor.

For battle effects:
- if the donor effect can be translated to an existing Platinum battle effect,
  that native effect is used immediately;
- otherwise the move remains usable with a documented safe fallback
  (generic hit for damaging moves, do-nothing for status moves).

Later PT05C effect batches replace those reported fallbacks with their real
modern handlers. This keeps the build playable while engine work continues.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

MOVE_DEFINE_RE = re.compile(r"^#define\s+(MOVE_[A-Z0-9_]+)\s+(\d+)\s*$", re.M)
C_STRING_RE = r'"((?:\\.|[^"\\])*)"'

CLASS_MAP = {
    "SPLIT_PHYSICAL": "CLASS_PHYSICAL",
    "SPLIT_SPECIAL": "CLASS_SPECIAL",
    "SPLIT_STATUS": "CLASS_STATUS",
}

FLAG_MAP = {
    "FLAG_CONTACT": "MOVE_FLAG_MAKES_CONTACT",
    "FLAG_PROTECT": "MOVE_FLAG_CAN_PROTECT",
    "FLAG_MAGIC_COAT": "MOVE_FLAG_CAN_MAGIC_COAT",
    "FLAG_SNATCH": "MOVE_FLAG_CAN_SNATCH",
    "FLAG_MIRROR_MOVE": "MOVE_FLAG_CAN_MIRROR_MOVE",
    "FLAG_HIDE_SHADOW": "MOVE_FLAG_HIDES_SHADOWS",
}

CONTEST_TYPE_MAP = {
    "CONTEST_COOL": "CONTEST_TYPE_COOL",
    "CONTEST_BEAUTY": "CONTEST_TYPE_BEAUTY",
    "CONTEST_CUTE": "CONTEST_TYPE_CUTE",
    "CONTEST_SMART": "CONTEST_TYPE_SMART",
    "CONTEST_TOUGH": "CONTEST_TYPE_TOUGH",
}


def load_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


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


def capture(block: str, pattern: str, flags: int = 0) -> str | None:
    m = re.search(pattern, block, flags)
    return m.group(1) if m else None


def c_string(block: str, field: str) -> str | None:
    return capture(block, rf"\.{re.escape(field)}\s*=\s*{C_STRING_RE}")


def decode_description(raw: str | None) -> list[str]:
    if not raw:
        return ["A move from a later\n", "generation."]

    # HG-Engine stores DS-friendly line breaks as the two characters \n.
    raw = raw.replace(r'\"', '"')
    parts = raw.split(r"\n")
    if parts and parts[-1] == "":
        parts.pop()
    if not parts:
        parts = ["A move from a later generation."]

    # Keep the Platinum five-line description box usable. If a donor string is
    # longer, merge the overflow into the final line rather than dropping it.
    if len(parts) > 5:
        parts = parts[:4] + [" ".join(parts[4:])]

    out = []
    for i, part in enumerate(parts):
        suffix = "\n" if i < len(parts) - 1 else ""
        out.append(part + suffix)
    return out


def donor_move_defs(hg_root: Path) -> list[str]:
    text = (hg_root / "include/constants/moves.h").read_text(errors="replace")
    pairs = [(token, int(idx)) for token, idx in MOVE_DEFINE_RE.findall(text)]
    canonical = {idx: token for token, idx in pairs if 0 <= idx <= 922}
    missing = [idx for idx in range(923) if idx not in canonical]
    if missing:
        raise SystemExit(f"donor canonical move IDs missing: {missing[:20]}")
    return [canonical[i] for i in range(923)]


def build_existing_effect_map(pt_root: Path, hg_moves_text: str, move_tokens: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    conflicts: dict[str, set[str]] = {}

    for token in move_tokens[:468]:
        block = extract_block(hg_moves_text, token)
        if not block:
            continue
        donor_effect = capture(block, r"\.effect\s*=\s*(MOVE_EFFECT_[A-Z0-9_]+)")
        if not donor_effect:
            continue

        stem = token.removeprefix("MOVE_").lower()
        path = pt_root / "res/moves" / stem / "data.json"
        if not path.is_file():
            continue
        effect = json.loads(path.read_text()).get("effect", {}).get("type")
        if not effect:
            continue

        if donor_effect in mapping and mapping[donor_effect] != effect:
            conflicts.setdefault(donor_effect, {mapping[donor_effect]}).add(effect)
        else:
            mapping[donor_effect] = effect

    # Only retain unambiguous observed mappings.
    for key in conflicts:
        mapping.pop(key, None)

    return mapping


def parse_move(block: str) -> dict:
    def number(field: str, default: int = 0) -> int:
        raw = capture(block, rf"\.{re.escape(field)}\s*=\s*(-?\d+)")
        return int(raw) if raw is not None else default

    flags_expr = capture(block, r"\.flags\s*=\s*([^,\n]+)")
    donor_flags = re.findall(r"FLAG_[A-Z0-9_]+", flags_expr or "")

    return {
        "name": c_string(block, "name"),
        "description_raw": c_string(block, "description"),
        "effect": capture(block, r"\.effect\s*=\s*(MOVE_EFFECT_[A-Z0-9_]+)"),
        "split": capture(block, r"\.split\s*=\s*(SPLIT_[A-Z0-9_]+)"),
        "power": number("power"),
        "type": capture(block, r"\.type\s*=\s*(TYPE_[A-Z0-9_]+)"),
        "accuracy": number("accuracy"),
        "pp": number("pp"),
        "effect_chance": number("effectChance"),
        "range": capture(block, r"\.target\s*=\s*(RANGE_[A-Z0-9_]+)"),
        "priority": number("priority"),
        "flags": donor_flags,
        "contest_type": capture(block, r"\.contestType\s*=\s*(CONTEST_[A-Z0-9_]+)"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("pt05c-modern-moves-install.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    tokens = donor_move_defs(hg)
    generated_moves = pt / "generated/moves.txt"
    current = load_lines(generated_moves)
    if not current or current[-1] != "MAX_MOVES":
        raise SystemExit("Platinum moves registry does not end in MAX_MOVES")

    vanilla = current[:-1]
    if vanilla != tokens[: len(vanilla)]:
        for idx, (a, b) in enumerate(zip(vanilla, tokens)):
            if a != b:
                raise SystemExit(f"move ID mismatch at {idx}: Platinum={a}, donor={b}")
        raise SystemExit(
            f"move registry length mismatch: Platinum={len(vanilla)} donor prefix={len(tokens)}"
        )
    if len(vanilla) != 468:
        raise SystemExit(f"expected 468 native move IDs, found {len(vanilla)}")

    hg_moves_text = (hg / "data/Moves.c").read_text(errors="replace")
    effects = set(load_lines(pt / "generated/move_battle_effects.txt"))
    ranges = set(load_lines(pt / "generated/move_ranges.txt"))
    types = set(load_lines(pt / "generated/pokemon_types.txt"))

    observed_effect_map = build_existing_effect_map(pt, hg_moves_text, tokens)

    # Extend the canonical registry while keeping all native IDs untouched.
    generated_moves.write_text("\n".join(tokens + ["MAX_MOVES"]) + "\n")

    script_template = (pt / "res/moves/tackle/script.s").read_text()
    anim_templates = {
        "CLASS_PHYSICAL": (pt / "res/moves/tackle/anim.s").read_text(),
        "CLASS_SPECIAL": (pt / "res/moves/water_gun/anim.s").read_text(),
        "CLASS_STATUS": (pt / "res/moves/splash/anim.s").read_text(),
    }

    installed = []
    fallbacks = []
    effect_counts: dict[str, int] = {}
    missing_blocks = []

    for move_id in range(468, 923):
        token = tokens[move_id]
        block = extract_block(hg_moves_text, token)
        if block is None:
            missing_blocks.append({"id": move_id, "move": token})
            continue

        src = parse_move(block)
        move_class = CLASS_MAP.get(src["split"], "CLASS_STATUS")
        power = max(0, min(255, src["power"]))
        accuracy = max(0, min(100, src["accuracy"]))
        pp = max(1, min(255, src["pp"] or 1))
        effect_chance = max(0, min(100, src["effect_chance"]))

        move_type = src["type"] if src["type"] in types else "TYPE_NORMAL"
        move_range = src["range"] if src["range"] in ranges else (
            "RANGE_USER" if move_class == "CLASS_STATUS" and power == 0 else "RANGE_SINGLE_TARGET"
        )

        donor_effect = src["effect"]
        candidate = donor_effect.replace("MOVE_EFFECT_", "BATTLE_EFFECT_", 1) if donor_effect else None
        effect = None
        effect_source = None

        if donor_effect in observed_effect_map:
            effect = observed_effect_map[donor_effect]
            effect_source = "observed_gen4_mapping"
        elif candidate in effects:
            effect = candidate
            effect_source = "direct_name_mapping"
        else:
            effect = "BATTLE_EFFECT_HIT" if power > 0 else "BATTLE_EFFECT_DO_NOTHING"
            effect_source = "safe_fallback"
            fallbacks.append({
                "id": move_id,
                "move": token,
                "donor_effect": donor_effect,
                "stored_effect": effect,
                "class": move_class,
                "power": power,
            })

        effect_counts[effect_source] = effect_counts.get(effect_source, 0) + 1

        flags = []
        for donor_flag in src["flags"]:
            mapped = FLAG_MAP.get(donor_flag)
            if mapped and mapped not in flags:
                flags.append(mapped)
        if power > 0:
            if "MOVE_FLAG_TRIGGERS_KINGS_ROCK" not in flags:
                flags.append("MOVE_FLAG_TRIGGERS_KINGS_ROCK")
            if "MOVE_FLAG_HIDES_HP_GAUGES" not in flags:
                flags.append("MOVE_FLAG_HIDES_HP_GAUGES")

        contest_type = CONTEST_TYPE_MAP.get(src["contest_type"], "CONTEST_TYPE_COOL")

        name = src["name"] or token.removeprefix("MOVE_").replace("_", " ").title()
        data = {
            "name": name,
            "description": decode_description(src["description_raw"]),
            "class": move_class,
            "type": move_type,
            "power": power,
            "accuracy": accuracy,
            "pp": pp,
            "effect": {
                "type": effect,
                "chance": effect_chance,
            },
            "range": move_range,
            "priority": max(-7, min(7, src["priority"])),
            "flags": flags,
            "contest": {
                "effect": "CONTEST_EFFECT_BASIC",
                "type": contest_type,
            },
        }

        stem = token.removeprefix("MOVE_").lower()
        move_dir = pt / "res/moves" / stem
        move_dir.mkdir(parents=True, exist_ok=True)
        (move_dir / "data.json").write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n"
        )
        (move_dir / "script.s").write_text(script_template)
        (move_dir / "anim.s").write_text(anim_templates[move_class])

        installed.append({
            "id": move_id,
            "move": token,
            "name": name,
            "effect": effect,
            "effect_source": effect_source,
            "class": move_class,
            "type": move_type,
        })

    report = {
        "gate": "PT05C_CANONICAL_GEN5_GEN9_MOVE_DATA_INSTALL",
        "canonical_move_count": 923,
        "native_move_count_preserved": 468,
        "modern_moves_requested": 455,
        "modern_moves_installed": len(installed),
        "missing_donor_blocks": missing_blocks,
        "effect_translation_counts": effect_counts,
        "fallback_effect_count": len(fallbacks),
        "fallbacks": fallbacks,
        "installed": installed,
        "animation_policy": {
            "physical": "temporary Tackle native DS animation",
            "special": "temporary Water Gun native DS animation",
            "status": "temporary Splash native DS animation",
            "future": "replace from Mercury DS move-animation library",
        },
        "next_gate": "PT05C_PORT_REMAINING_MODERN_EFFECT_HANDLERS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    if len(installed) != 455 or missing_blocks:
        raise SystemExit(
            f"modern move install incomplete: installed={len(installed)}, missing={len(missing_blocks)}"
        )

    print(json.dumps({
        "gate": report["gate"],
        "canonical_move_count": 923,
        "modern_moves_installed": len(installed),
        "effect_translation_counts": effect_counts,
        "fallback_effect_count": len(fallbacks),
    }, indent=2))


if __name__ == "__main__":
    main()
