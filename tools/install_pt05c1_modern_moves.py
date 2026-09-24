#!/usr/bin/env python3
"""Install the canonical Gen 5-9 move namespace into Platinum.

PT05C1 establishes stable canonical move IDs 468..919 and immediately enables
all moves whose HG-Engine battle-effect ID maps to one of Platinum's existing
0..276 effect scripts.

Moves that require a genuinely new battle effect are still assigned their
canonical ID and metadata, but temporarily point at a safe stub effect and are
excluded from the "implemented moves" registry. That prevents species
learnsets from teaching a move before its real battle effect has been ported.

Animations are intentionally safe placeholders during engine bring-up. The
canonical move behavior is the blocker; animation fidelity is a later pass.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MOVE_DEFINE_RE = re.compile(r"^#define\s+(MOVE_[A-Z0-9_]+)\s+([0-9]+)\s*$", re.M)
EFFECT_DEFINE_RE = re.compile(r"^#define\s+(MOVE_EFFECT_[A-Z0-9_]+)\s+([0-9]+)\s*$", re.M)

# HG-Engine intentionally preserves the three inaccessible HGSS/Platinum-era
# move slots immediately after Shadow Force. Keeping these IDs avoids shifting
# the donor's entire Gen 5-9 namespace, but they are never learnable moves.
COMPATIBILITY_PLACEHOLDERS = {"MOVE_468", "MOVE_469", "MOVE_470"}

SPLIT_MAP = {
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


def load_constants(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def extract_block(text: str, token: str) -> str:
    marker = f"[{token}] = {{"
    start = text.find(marker)
    if start < 0:
        raise ValueError(f"missing donor block for {token}")
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
    raise ValueError(f"unterminated donor block for {token}")


def cap(block: str, pattern: str, default=None):
    m = re.search(pattern, block, re.S)
    return m.group(1) if m else default


def canonical_assignment(
    block: str,
    field: str,
    value_pattern: str,
    default=None,
):
    """Read a donor assignment using the upstream/canonical value.

    HG-Engine carries optional CHAMPIONS_* balance switches in a small number
    of move-data fields. Mercury's modern-Platinum baseline must import the
    canonical Pokémon value, which is the false branch of those ternaries,
    rather than accidentally importing the optional rebalance.
    """
    expr = cap(block, rf"\.{re.escape(field)}\s*=\s*([^,\n]+)")
    if expr is None:
        return default

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


def canonical_target_assignment(block: str) -> tuple[str, str | None]:
    """Return a Platinum-safe target plus any donor composite expression.

    HG-Engine uses bitwise-composed target masks for a few post-Gen-IV moves
    (Rototiller, Flower Shield, Teatime). Platinum's move metadata expects one
    range enum. These moves are still excluded from natural learnsets until
    their modern battle effects are ported, so keep a safe all-adjacent runtime
    fallback now and preserve the original expression in the import report for
    PT05C2 targeting work.
    """
    expr = cap(block, r"\.target\s*=\s*([^,\n]+)")
    if expr is None:
        raise SystemExit("move donor block is missing .target")

    direct = re.fullmatch(r"\s*(RANGE_[A-Z0-9_]+)\s*", expr)
    if direct:
        return direct.group(1), None

    composite = re.sub(r"\s+", "", expr)
    if composite == "RANGE_ALL_ADJACENT|RANGE_USER":
        return "RANGE_ALL_ADJACENT", expr.strip()

    raise SystemExit(f"could not parse canonical donor value for .target: {expr!r}")


def c_string(block: str, field: str) -> str | None:
    raw = cap(block, rf"\.{re.escape(field)}\s*=\s*\"((?:\\.|[^\"\\])*)\"")
    if raw is None:
        return None

    # Decode escapes without round-tripping UTF-8 bytes through
    # unicode_escape. That byte-level decode corrupts valid donor characters.
    try:
        text = json.loads(f'\"{raw}\"')
    except json.JSONDecodeError:
        text = (
            raw.replace(r"\n", "\n")
               .replace(r'\\\"', '"')
               .replace(r"\\", "\\")
        )

    # The donor uses a literal \\n sequence inside C strings for message line
    # breaks. Convert it to a real newline so json.dumps emits Platinum's normal
    # JSON newline escape instead of a doubled backslash.
    text = text.replace(r"\\n", "\n")

    # Platinum's English message charmap supports the straight apostrophe but
    # not U+2019, which appears in several modern move names/descriptions.
    return text.replace("’", "'")


def description_lines(desc: str | None) -> list[str]:
    if not desc:
        return [
            "A modern move ported\n",
            "for Mercury Redux.",
        ]
    lines = desc.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        return ["A modern move."]
    return [line + ("\n" if i < len(lines) - 1 else "") for i, line in enumerate(lines)]


def generation_for_move_id(move_id: int) -> int:
    # Canonical IDs after dropping HG-Engine's three preserved dummy slots.
    if move_id <= 559:
        return 5
    if move_id <= 621:
        return 6
    if move_id <= 742:
        return 7
    if move_id <= 850:
        return 8
    return 9


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("pt05c1-move-import.json"))
    ap.add_argument(
        "--implemented-registry",
        type=Path,
        default=Path("pt05c1-implemented-moves.txt"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    move_h = (hg / "include/constants/moves.h").read_text(errors="replace")
    effect_h = (hg / "include/constants/move_effects.h").read_text(errors="replace")
    moves_c = (hg / "data/Moves.c").read_text(errors="replace")

    donor_moves = {name: int(num) for name, num in MOVE_DEFINE_RE.findall(move_h)}
    donor_effects = {name: int(num) for name, num in EFFECT_DEFINE_RE.findall(effect_h)}
    donor_effects.setdefault("MOVE_EFFECT_ATK_SP_ATK_SPEED_UP_2_LOSE_HALF_MAX_HP", 303)

    pt_effects = load_constants(pt / "generated/move_battle_effects.txt")
    pt_ranges = set(load_constants(pt / "generated/move_ranges.txt"))
    pt_types = set(load_constants(pt / "generated/pokemon_types.txt"))
    native_effect_max = len(pt_effects) - 1

    moves_txt = pt / "generated/moves.txt"
    old_move_registry = load_constants(moves_txt)
    if not old_move_registry or old_move_registry[-1] != "MAX_MOVES":
        raise SystemExit("Platinum move registry does not end in MAX_MOVES")

    existing_moves = old_move_registry[:-1]
    if existing_moves[-1] != "MOVE_SHADOW_FORCE":
        raise SystemExit(f"unexpected final native move: {existing_moves[-1]}")
    if len(existing_moves) != 468:
        raise SystemExit(f"expected 468 native move constants including MOVE_NONE, got {len(existing_moves)}")

    # The pinned HG-Engine preserves three HGSS dummy move slots at donor IDs
    # 468..470. Main-series canonical Gen-5 numbering starts Hone Claws at 468.
    # Drop those three placeholders and translate donor IDs 471..922 down by 3
    # so Mercury uses the official canonical IDs 468..919.
    donor_modern = [
        (token, donor_id)
        for token, donor_id in sorted(donor_moves.items(), key=lambda kv: kv[1])
        if 471 <= donor_id <= 922
    ]
    modern = [
        (token, donor_id, donor_id - 3)
        for token, donor_id in donor_modern
    ]
    if len(modern) != 452:
        raise SystemExit(f"expected 452 canonical Gen 5-9 moves, got {len(modern)}")
    for expected, (_, donor_id, canonical_id) in enumerate(modern, start=468):
        if canonical_id != expected:
            raise SystemExit(
                f"canonical move ID gap: expected {expected}, got {canonical_id} "
                f"(donor ID {donor_id})"
            )

    moves_txt.write_text(
        "\n".join(existing_moves + [x[0] for x in modern] + ["MAX_MOVES", ""])
    )

    rows = []
    implemented_modern = []
    stubbed_modern = []
    reserved_compatibility = []
    generated_dirs = []

    for token, donor_move_id, move_id in modern:
        block = extract_block(moves_c, token)
        effect_token = cap(block, r"\.effect\s*=\s*(MOVE_EFFECT_[A-Z0-9_]+)")
        if not effect_token or effect_token not in donor_effects:
            raise SystemExit(f"{token}: could not resolve donor effect {effect_token!r}")
        effect_id = donor_effects[effect_token]
        implemented = effect_id <= native_effect_max

        split = canonical_assignment(block, "split", r"SPLIT_[A-Z]+")
        move_type = canonical_assignment(block, "type", r"TYPE_[A-Z0-9_]+")
        target, donor_target_composite = canonical_target_assignment(block)
        target_requires_extension = donor_target_composite is not None
        power = int(canonical_assignment(block, "power", r"[0-9]+", "0"))
        accuracy = int(canonical_assignment(block, "accuracy", r"[0-9]+", "0"))
        pp = int(canonical_assignment(block, "pp", r"[0-9]+", "1"))
        effect_chance = int(canonical_assignment(block, "effectChance", r"[0-9]+", "0"))
        priority = int(canonical_assignment(block, "priority", r"-?[0-9]+", "0"))

        if split not in SPLIT_MAP:
            raise SystemExit(f"{token}: unsupported split {split}")
        if move_type not in pt_types:
            raise SystemExit(f"{token}: target Platinum build lacks type {move_type}")
        if target not in pt_ranges:
            raise SystemExit(f"{token}: target Platinum build lacks range {target}")

        is_compatibility_placeholder = token in COMPATIBILITY_PLACEHOLDERS
        implemented = (
            effect_id <= native_effect_max
            and not target_requires_extension
            and not is_compatibility_placeholder
        )

        flags_expr = cap(block, r"\.flags\s*=\s*([^,\n]+)", "") or ""
        flags = []
        for donor_flag, pt_flag in FLAG_MAP.items():
            if re.search(rf"\b{re.escape(donor_flag)}\b", flags_expr):
                flags.append(pt_flag)
        # Platinum's move-data bit 5 is King's Rock compatibility. HG-Engine
        # reuses that bit for Dexit gating, so infer it for ordinary damaging
        # moves rather than mapping bit 5 blindly.
        if power > 0:
            flags.append("MOVE_FLAG_TRIGGERS_KINGS_ROCK")

        contest_type_src = cap(block, r"\.contestType\s*=\s*(CONTEST_[A-Z]+)")
        contest_type = CONTEST_TYPE_MAP.get(contest_type_src, "CONTEST_TYPE_COOL")

        name = c_string(block, "name") or token.removeprefix("MOVE_").replace("_", " ").title()
        desc = c_string(block, "description")

        if is_compatibility_placeholder:
            battle_effect = pt_effects[effect_id]
            reserved_compatibility.append(token)
            lane = "reserved_ds_compatibility_slot"
        elif implemented:
            battle_effect = pt_effects[effect_id]
            implemented_modern.append(token)
            lane = "implemented_native_effect"
        else:
            # Keep the ID/data present but do not teach the move yet.
            battle_effect = "BATTLE_EFFECT_DO_NOTHING" if split == "SPLIT_STATUS" else "BATTLE_EFFECT_HIT"
            stubbed_modern.append(token)
            lane = (
                "stub_waiting_for_composite_target_port"
                if target_requires_extension
                else "stub_waiting_for_effect_port"
            )

        data = {
            "name": name,
            "description": description_lines(desc),
            "class": SPLIT_MAP[split],
            "type": move_type,
            "power": power,
            "accuracy": accuracy,
            "pp": pp,
            "effect": {
                "type": battle_effect,
                "chance": effect_chance if implemented else 0,
            },
            "range": target,
            "priority": priority,
            "flags": flags,
            "contest": {
                "effect": "CONTEST_EFFECT_BASIC",
                "type": contest_type,
            },
        }

        stem = token.removeprefix("MOVE_").lower()
        move_dir = pt / "res/moves" / stem
        move_dir.mkdir(parents=True, exist_ok=False)
        (move_dir / "data.json").write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
        (move_dir / "script.s").write_text(
            '#include "macros/btlcmd.inc"\n\n\n_000:\n    GoToEffectScript \n'
        )
        (move_dir / "anim.s").write_text(
            '#include "macros/btlanimcmd.inc"\n\nL_0:\n    End\n'
        )
        generated_dirs.append(stem)

        rows.append({
            "id": move_id,
            "donor_id": donor_move_id,
            "generation": generation_for_move_id(move_id),
            "move": token,
            "name": name,
            "donor_effect": effect_token,
            "donor_effect_id": effect_id,
            "stored_effect": battle_effect,
            "stored_target": target,
            "donor_target_composite": donor_target_composite,
            "target_requires_extension": target_requires_extension,
            "lane": lane,
        })

    # Learnsets may teach native Gen-IV moves plus only modern moves whose
    # canonical battle effect is currently implemented.
    implemented_registry = existing_moves + implemented_modern
    args.implemented_registry.write_text("\n".join(implemented_registry) + "\n")

    report = {
        "gate": "PT05C1_CANONICAL_MOVE_NAMESPACE_AND_NATIVE_EFFECT_IMPORT",
        "canonical_move_range": [0, 919],
        "donor_move_range": [471, 922],
        "donor_dummy_ids_dropped": [468, 469, 470],
        "donor_to_canonical_offset": -3,
        "max_move_constant": "MOVE_MALIGNANT_CHAIN",
        "modern_namespace_entries_added": len(modern),
        "reserved_compatibility_slots": len(reserved_compatibility),
        "reserved_compatibility_tokens": reserved_compatibility,
        "modern_moves_added": len(modern) - len(reserved_compatibility),
        "modern_moves_immediately_implemented": len(implemented_modern),
        "modern_moves_stubbed_pending_effect_port": len(stubbed_modern),
        "platinum_native_effect_max": native_effect_max,
        "implemented_registry": str(args.implemented_registry),
        "placeholder_animation_policy": "no-op animation during engine bring-up",
        "composite_target_policy": "RANGE_ALL_ADJACENT | RANGE_USER is temporarily stored as RANGE_ALL_ADJACENT while affected moves remain excluded pending PT05C2 effect/target port",
        "contest_policy": "basic contest effect placeholder until contest-fidelity pass",
        "moves": rows,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({
        "gate": report["gate"],
        "modern_namespace_entries_added": len(modern),
        "modern_moves_added": len(modern) - len(reserved_compatibility),
        "reserved_compatibility_slots": len(reserved_compatibility),
        "implemented_now": len(implemented_modern),
        "stubbed_pending_effects": len(stubbed_modern),
        "final_canonical_move_id": modern[-1][2],
    }, indent=2))


if __name__ == "__main__":
    main()
