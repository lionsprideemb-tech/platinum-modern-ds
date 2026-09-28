#!/usr/bin/env python3
"""MR08A — canonical modern Ability mechanics batch 1.

Step one for Mercury's modern Ability rollout. This gate deliberately changes
battle mechanics only; the locked MR07 Summary/Skills visual design is not
touched.

Implemented in this batch:
- Contrary
- Big Pecks
- Full Metal Body

The gate also closes several 8-bit runtime truncation paths left after the
canonical 10-bit Ability namespace was introduced, so later canonical Abilities
above ID 255 can safely flow through battle logic and the AI cache.

The implemented-Ability registry is updated only after the mechanics hooks are
installed. Because the species importer consumes that registry, moving this
gate before species import allows donor species to receive these Abilities
instead of falling back to ABILITY_NONE.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_CONTRARY",
    "ABILITY_BIG_PECKS",
    "ABILITY_FULL_METAL_BODY",
)

EXPECTED_IDS = {
    "ABILITY_CONTRARY": 126,
    "ABILITY_BIG_PECKS": 145,
    "ABILITY_FULL_METAL_BODY": 230,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_exact_count(
    path: Path, old: str, new: str, expected: int, label: str
) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            f"{label}: expected {expected} matches in {path}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    checks: dict[str, bool] = {}
    for token, expected in EXPECTED_IDS.items():
        checks[f"{token.lower()}_id"] = (
            len(abilities) > expected and abilities[expected] == token
        )
    return checks


def patch_wide_runtime(root: Path) -> None:
    # The namespace installer widens BattleMon::ability itself, but every API
    # edge that reads/writes/caches it must also preserve all 10 bits.
    replace_once(
        root / "include/battle/battle_lib.h",
        "u8 Battler_Ability(BattleContext *battleCtx, int battler);",
        "u16 Battler_Ability(BattleContext *battleCtx, int battler);",
        "Battler_Ability declaration width",
    )

    battle_lib = root / "src/battle/battle_lib.c"
    replace_once(
        battle_lib,
        """    case BATTLEMON_ABILITY:
        mon->ability = *(u8 *)buf;
        break;
""",
        """    case BATTLEMON_ABILITY:
        mon->ability = *(u16 *)buf;
        break;
""",
        "BattleMon_Set Ability width",
    )
    replace_once(
        battle_lib,
        "u8 Battler_Ability(BattleContext *battleCtx, int battler)",
        "u16 Battler_Ability(BattleContext *battleCtx, int battler)",
        "Battler_Ability definition width",
    )

    replace_once(
        root / "include/battle/ai_context.h",
        "    u8 battlerAbilities[MAX_BATTLERS];",
        "    u16 battlerAbilities[MAX_BATTLERS];",
        "AI known-Ability cache width",
    )

    # One forward declaration + one definition.
    replace_exact_count(
        root / "src/battle/battle_script.c",
        "BattleAI_SetAbility(BattleContext *battleCtx, u8 battler, u8 ability)",
        "BattleAI_SetAbility(BattleContext *battleCtx, u8 battler, u16 ability)",
        2,
        "BattleAI_SetAbility parameter width",
    )


def patch_stat_stage_abilities(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    # Contrary reverses the requested stage change before the normal cap,
    # prevention, message, and animation paths are selected. HG-Engine uses its
    # Mold-Breaker-aware Ability check here; Battler_IgnorableAbility is
    # Platinum's equivalent.
    replace_once(
        path,
        """    if (stageChange > 0) {
""",
        """    // MR08A: Contrary reverses every stat-stage change. Use the
    // Mold-Breaker-aware helper so an opposing Mold Breaker can ignore it.
    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->sideEffectMon,
            ABILITY_CONTRARY) == TRUE) {
        stageChange = -stageChange;
        battleCtx->scriptTemp =
            stageChange > 0
                ? BATTLE_ANIMATION_STAT_BOOST
                : BATTLE_ANIMATION_STAT_DROP;
    }

    if (stageChange > 0) {
""",
        "Contrary stat-stage reversal",
    )

    # Full Metal Body mirrors Clear Body / White Smoke but is deliberately
    # checked directly: canonical behavior is that Mold Breaker cannot ignore
    # it. Battler_Ability still respects explicit Ability suppression.
    replace_once(
        path,
        """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE) {
""",
        """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE
                    || Battler_Ability(battleCtx, battleCtx->sideEffectMon) == ABILITY_FULL_METAL_BODY) {
""",
        "Full Metal Body stat-drop prevention",
    )

    replace_once(
        path,
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)) {
""",
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE)) {
""",
        "Big Pecks Defense-drop prevention",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    battle_lib_h = (root / "include/battle/battle_lib.h").read_text(
        encoding="utf-8"
    )
    battle_lib_c = (root / "src/battle/battle_lib.c").read_text(
        encoding="utf-8"
    )
    battle_script_c = (root / "src/battle/battle_script.c").read_text(
        encoding="utf-8"
    )
    ai_h = (root / "include/battle/ai_context.h").read_text(
        encoding="utf-8"
    )
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "contrary_hook":
            "ABILITY_CONTRARY) == TRUE" in battle_script_c
            and "stageChange = -stageChange;" in battle_script_c,
        "big_pecks_hook":
            "ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE" in battle_script_c,
        "full_metal_body_hook":
            "Battler_Ability(battleCtx, battleCtx->sideEffectMon) == ABILITY_FULL_METAL_BODY"
            in battle_script_c,
        "battle_ability_return_u16":
            "u16 Battler_Ability(BattleContext *battleCtx, int battler);"
            in battle_lib_h
            and "u16 Battler_Ability(BattleContext *battleCtx, int battler)"
            in battle_lib_c,
        "battlemon_set_u16":
            "mon->ability = *(u16 *)buf;" in battle_lib_c,
        "ai_ability_cache_u16":
            "u16 battlerAbilities[MAX_BATTLERS];" in ai_h
            and battle_script_c.count(
                "BattleAI_SetAbility(BattleContext *battleCtx, u8 battler, u16 ability)"
            ) == 2,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--implemented-registry",
        type=Path,
        required=True,
        help="Registry generated by install_mp05_ability_namespace.py",
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08a-canonical-ability-batch.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_wide_runtime(root)
    patch_stat_stage_abilities(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08A_CANONICAL_ABILITY_MECHANICS_BATCH_1",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "donor_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "runtime_width": {
            "ability_bits": 10,
            "battle_api": "u16",
            "battle_setter": "u16",
            "ai_cache": "u16",
        },
        "checks": checks,
    }

    args.report.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08A validation failed")


if __name__ == "__main__":
    main()
