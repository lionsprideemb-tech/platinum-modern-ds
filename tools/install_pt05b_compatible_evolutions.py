#!/usr/bin/env python3
"""Install compatible post-Gen-IV evolution data into Mercury DS.

The donor evolution table contains modern methods that native Platinum does not
understand. Directly-supported methods are translated to Platinum's names.
Methods that cannot be represented yet are converted to documented, playable
level-up fallbacks instead of leaving an evolution line permanently broken.

This is a production data pass. Every fallback is written to the report so a
later Mercury-specific evolution pass can replace it with the intended method.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_EVOLUTIONS = 7

METHOD_MAP = {
    "EVO_HAPPINESS": "EVO_LEVEL_HAPPINESS",
    "EVO_HAPPINESS_DAY": "EVO_LEVEL_HAPPINESS_DAY",
    "EVO_HAPPINESS_NIGHT": "EVO_LEVEL_HAPPINESS_NIGHT",
    "EVO_LEVEL_UP": "EVO_LEVEL",
    "EVO_LEVEL_MORE_ATTACK": "EVO_LEVEL_ATK_GT_DEF",
    "EVO_LEVEL_ATK_DEF_EQUAL": "EVO_LEVEL_ATK_EQ_DEF",
    "EVO_LEVEL_MORE_DEFENSE": "EVO_LEVEL_ATK_LT_DEF",
    "EVO_LEVEL_PID_LOW": "EVO_LEVEL_PID_LOW",
    "EVO_LEVEL_PID_HIGH": "EVO_LEVEL_PID_HIGH",
    "EVO_LEVEL_GEN_NEW_MON_1": "EVO_LEVEL_NINJASK",
    "EVO_LEVEL_GEN_NEW_MON_2": "EVO_LEVEL_SHEDINJA",
    "EVO_MAX_BEAUTY": "EVO_LEVEL_BEAUTY",
    "EVO_USE_ITEM": "EVO_USE_ITEM",
    "EVO_USE_ITEM_MALE": "EVO_USE_ITEM_MALE",
    "EVO_USE_ITEM_FEMALE": "EVO_USE_ITEM_FEMALE",
    "EVO_USE_ITEM_DAY": "EVO_LEVEL_WITH_HELD_ITEM_DAY",
    "EVO_USE_ITEM_NIGHT": "EVO_LEVEL_WITH_HELD_ITEM_NIGHT",
    "EVO_KNOWS_MOVE": "EVO_LEVEL_KNOW_MOVE",
    "EVO_MON_IN_PARTY": "EVO_LEVEL_SPECIES_IN_PARTY",
    "EVO_LEVEL_MALE": "EVO_LEVEL_MALE",
    "EVO_LEVEL_FEMALE": "EVO_LEVEL_FEMALE",
    "EVO_LEVEL_ELECTRIC_FIELD": "EVO_LEVEL_MAGNETIC_FIELD",
    "EVO_LEVEL_MOSSY_STONE": "EVO_LEVEL_MOSS_ROCK",
    "EVO_LEVEL_ICY_STONE": "EVO_LEVEL_ICE_ROCK",
}

NO_PARAM_METHODS = {
    "EVO_LEVEL_HAPPINESS",
    "EVO_LEVEL_HAPPINESS_DAY",
    "EVO_LEVEL_HAPPINESS_NIGHT",
    "EVO_LEVEL_MAGNETIC_FIELD",
    "EVO_LEVEL_MOSS_ROCK",
    "EVO_LEVEL_ICE_ROCK",
}

ITEM_METHODS = {
    "EVO_USE_ITEM",
    "EVO_USE_ITEM_MALE",
    "EVO_USE_ITEM_FEMALE",
    "EVO_LEVEL_WITH_HELD_ITEM_DAY",
    "EVO_LEVEL_WITH_HELD_ITEM_NIGHT",
}

MOVE_METHODS = {"EVO_LEVEL_KNOW_MOVE"}
SPECIES_PARAM_METHODS = {"EVO_LEVEL_SPECIES_IN_PARTY"}

ITEM_ALIASES = {
    "ITEM_THUNDER_STONE": "ITEM_THUNDERSTONE",
    "ITEM_BLACK_GLASSES": "ITEM_BLACKGLASSES",
    "ITEM_DEEP_SEA_TOOTH": "ITEM_DEEPSEATOOTH",
    "ITEM_DEEP_SEA_SCALE": "ITEM_DEEPSEASCALE",
    "ITEM_NEVER_MELT_ICE": "ITEM_NEVERMELTICE",
    "ITEM_SILVER_POWDER": "ITEM_SILVERPOWDER",
    "ITEM_TINY_MUSHROOM": "ITEM_TINYMUSHROOM",
}

# Modern methods with a meaningful level in their parameter can retain it.
LEVELISH_FALLBACKS = {
    "EVO_LEVEL_DAY",
    "EVO_LEVEL_NIGHT",
    "EVO_LEVEL_DUSK",
    "EVO_LEVEL_RAIN",
}

# These methods need mechanics Platinum does not currently have. A normal
# level-up fallback keeps the species line usable in the playable build.
GENERIC_FALLBACK_METHODS = {
    "EVO_TRADE",
    "EVO_TRADE_ITEM",
    "EVO_TRADE_SPECIFIC_MON",
    "EVO_HAS_MOVE_TYPE",
    "EVO_LEVEL_DARK_TYPE_MON_IN_PARTY",
    "EVO_LEVEL_NATURE_AMPED",
    "EVO_LEVEL_NATURE_LOW_KEY",
    "EVO_AMOUNT_OF_CRITICAL_HITS",
    "EVO_HURT_IN_BATTLE_AMOUNT",
}


def load_registry(path: Path) -> list[str]:
    rows = [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(rows) < 1025:
        raise SystemExit(f"registry is too short: {len(rows)}")
    return rows


def load_constants(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def species_dir(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


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
    raise ValueError(f"unterminated donor block for {token}")


ENTRY_RE = re.compile(
    r"\{\s*(EVO_[A-Z0-9_]+)\s*,\s*([^,{}]+?)\s*,\s*"
    r"(SPECIES_[A-Z0-9_]+)\s*\}"
)


def parse_param(raw: str):
    value = raw.strip()
    try:
        return int(value, 0)
    except ValueError:
        return value


def fallback_level(source_method: str, param) -> int:
    if source_method in LEVELISH_FALLBACKS and isinstance(param, int):
        return max(1, min(100, param))
    # Accessible late-midgame default for trade/special-mechanic evolutions.
    return 40


def translate_entry(
    source_method: str,
    param,
    target: str,
    available_methods: set[str],
    available_items: set[str],
    available_moves: set[str],
    available_species: set[str],
):
    if target not in available_species:
        return None, "target_species_missing"

    if source_method == "EVO_NONE":
        return None, None

    mapped = METHOD_MAP.get(source_method)
    if mapped:
        if mapped not in available_methods:
            return None, "mapped_method_missing"

        if mapped in NO_PARAM_METHODS:
            return [mapped, target], None

        if mapped in ITEM_METHODS:
            item = ITEM_ALIASES.get(str(param), str(param))
            if item not in available_items:
                return ["EVO_LEVEL", 40, target], "unsupported_item_fallback"
            return [mapped, item, target], None

        if mapped in MOVE_METHODS:
            if str(param) not in available_moves:
                return ["EVO_LEVEL", 40, target], "unsupported_move_fallback"
            return [mapped, str(param), target], None

        if mapped in SPECIES_PARAM_METHODS:
            if str(param) not in available_species:
                return ["EVO_LEVEL", 40, target], "unsupported_party_species_fallback"
            return [mapped, str(param), target], None

        # Remaining mapped native methods carry an integer parameter.
        if not isinstance(param, int):
            return ["EVO_LEVEL", 40, target], "non_numeric_param_fallback"
        return [mapped, param, target], None

    if source_method in GENERIC_FALLBACK_METHODS or source_method in LEVELISH_FALLBACKS:
        return ["EVO_LEVEL", fallback_level(source_method, param), target], "modern_method_fallback"

    # Unknown donor methods are kept playable but explicitly reported.
    return ["EVO_LEVEL", 40, target], "unknown_method_fallback"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--start-dex", type=int, default=494)
    ap.add_argument("--end-dex", type=int, default=1025)
    ap.add_argument("--report", type=Path, default=Path("pt05b-compatible-evolutions.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)

    donor_text = (hg / "data/Evolutions.c").read_text(errors="replace")
    available_methods = load_constants(pt / "generated/evolution_methods.txt")
    available_items = load_constants(pt / "generated/items.txt")
    available_moves = load_constants(pt / "generated/moves.txt")
    available_species = load_constants(pt / "generated/species.txt")

    installed = []
    missing_blocks = []
    fallbacks = []
    truncated = []
    total_entries = 0

    for dex in range(args.start_dex, args.end_dex + 1):
        token = registry[dex - 1]
        target_path = pt / "res/pokemon" / species_dir(token) / "data.json"
        if not target_path.is_file():
            raise SystemExit(f"missing target data: {target_path}")

        block = extract_block(donor_text, token)
        if block is None:
            missing_blocks.append({"dex": dex, "species": token})
            continue

        translated = []
        seen = set()
        for method, raw_param, target in ENTRY_RE.findall(block):
            param = parse_param(raw_param)
            row, reason = translate_entry(
                method,
                param,
                target,
                available_methods,
                available_items,
                available_moves,
                available_species,
            )
            if row is None:
                if reason:
                    fallbacks.append({
                        "dex": dex,
                        "species": token,
                        "source_method": method,
                        "source_param": param,
                        "target": target,
                        "reason": reason,
                        "stored": None,
                    })
                continue

            key = tuple(row)
            if key in seen:
                continue
            seen.add(key)
            translated.append(row)
            if reason:
                fallbacks.append({
                    "dex": dex,
                    "species": token,
                    "source_method": method,
                    "source_param": param,
                    "target": target,
                    "reason": reason,
                    "stored": row,
                })

        if len(translated) > MAX_EVOLUTIONS:
            truncated.append({
                "dex": dex,
                "species": token,
                "original_count": len(translated),
                "stored_count": MAX_EVOLUTIONS,
                "dropped": translated[MAX_EVOLUTIONS:],
            })
            translated = translated[:MAX_EVOLUTIONS]

        data = json.loads(target_path.read_text())
        data["evolutions"] = translated
        target_path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")

        total_entries += len(translated)
        installed.append({
            "dex": dex,
            "species": token,
            "evolution_count": len(translated),
        })

    report = {
        "gate": "PT05B_COMPATIBLE_EVOLUTIONS",
        "range": [args.start_dex, args.end_dex],
        "species_requested": args.end_dex - args.start_dex + 1,
        "species_processed": len(installed),
        "total_evolution_entries": total_entries,
        "missing_donor_blocks": missing_blocks,
        "fallback_count": len(fallbacks),
        "fallbacks": fallbacks,
        "truncated_species": truncated,
        "species": installed,
        "policy": {
            "trade_and_unrepresentable_modern_methods": "level 40 fallback unless source carries a usable level",
            "directly_supported_methods": "translated to native Platinum evolution method",
            "future_pass": "replace reported fallbacks with Mercury-specific item/level/mechanic rules",
        },
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    if len(installed) < 500:
        raise SystemExit(
            f"evolution donor coverage unexpectedly low: {len(installed)} / "
            f"{report['species_requested']}"
        )

    print(json.dumps({
        "gate": report["gate"],
        "species_processed": len(installed),
        "total_evolution_entries": total_entries,
        "fallback_count": len(fallbacks),
        "missing_blocks": len(missing_blocks),
        "truncated_species": len(truncated),
    }, indent=2))


if __name__ == "__main__":
    main()
