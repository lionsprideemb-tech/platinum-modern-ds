#!/usr/bin/env python3
"""MR08A — canonical modern ability mechanics, batch 1.

Ports a first low-risk DS-native mechanics batch from the pinned hg-engine
behavior into pokeplatinum's decompiled battle script layer.

Batch 1:
- Contrary: reverses stat-stage changes.
- Big Pecks: prevents Defense reductions.
- Full Metal Body: prevents stat reductions and is not bypassed by Mold Breaker.

This installer deliberately does not touch the locked MR07 Summary/Skills UI.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITIES = [
    "ABILITY_CONTRARY",
    "ABILITY_BIG_PECKS",
    "ABILITY_FULL_METAL_BODY",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pokeplatinum", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = args.pokeplatinum
    battle_script = root / "src" / "battle" / "battle_script.c"
    abilities_txt = root / "generated" / "abilities.txt"

    if not battle_script.is_file():
        raise SystemExit(f"missing battle source: {battle_script}")
    if not abilities_txt.is_file():
        raise SystemExit(f"missing generated ability registry: {abilities_txt}")

    registry = abilities_txt.read_text()
    missing = [ability for ability in ABILITIES if ability not in registry]
    if missing:
        raise SystemExit(f"MR08A requires registered ability constants: {missing}")

    text = battle_script.read_text()

    contrary_anchor = """    } else {
        statOffset = battleCtx->sideEffectParam - MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
        stageChange = 1;
        battleCtx->scriptTemp = BATTLE_ANIMATION_STAT_BOOST;
    }

    if (stageChange > 0) {
"""

    contrary_patch = """    } else {
        statOffset = battleCtx->sideEffectParam - MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
        stageChange = 1;
        battleCtx->scriptTemp = BATTLE_ANIMATION_STAT_BOOST;
    }

    // MR08A: Contrary reverses the direction of every stat-stage change.
    // Use the normal ignorable-ability path so Mold Breaker interactions
    // follow the battle engine's existing suppression rules.
    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->sideEffectMon,
            ABILITY_CONTRARY) == TRUE) {
        stageChange = -stageChange;
        battleCtx->scriptTemp = stageChange > 0
            ? BATTLE_ANIMATION_STAT_BOOST
            : BATTLE_ANIMATION_STAT_DROP;
    }

    if (stageChange > 0) {
"""

    text = replace_once(
        text,
        contrary_anchor,
        contrary_patch,
        "Contrary stat-stage hook",
    )

    full_metal_anchor = """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE) {
"""

    full_metal_patch = """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE
                    // MR08A: Full Metal Body has Clear Body's effect but is
                    // explicitly non-ignorable by Mold Breaker.
                    || battleCtx->battleMons[battleCtx->sideEffectMon].ability == ABILITY_FULL_METAL_BODY) {
"""

    text = replace_once(
        text,
        full_metal_anchor,
        full_metal_patch,
        "Full Metal Body stat-loss prevention hook",
    )

    big_pecks_anchor = """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)) {
"""

    big_pecks_patch = """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)
                    // MR08A: Big Pecks blocks Defense reduction.
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE)) {
"""

    text = replace_once(
        text,
        big_pecks_anchor,
        big_pecks_patch,
        "Big Pecks Defense-loss prevention hook",
    )

    battle_script.write_text(text)

    checks = {
        "contrary_hook": "ABILITY_CONTRARY" in text
        and "stageChange = -stageChange;" in text,
        "big_pecks_hook": "ABILITY_BIG_PECKS" in text
        and "BATTLE_STAT_DEFENSE" in text,
        "full_metal_body_hook": "ABILITY_FULL_METAL_BODY" in text
        and "non-ignorable by Mold Breaker" in text,
    }

    if not all(checks.values()):
        raise SystemExit(f"MR08A validation failed: {checks}")

    report = {
        "status": "PASS",
        "phase": "MR08A",
        "batch": "canonical-modern-ability-mechanics-1",
        "donor": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "abilities": {
            "Contrary": {
                "token": "ABILITY_CONTRARY",
                "mechanic": "reverse stat-stage changes",
                "source_family": "hg-engine btl_scr_cmd_33_statbuffchange",
                "status": "installed",
            },
            "Big Pecks": {
                "token": "ABILITY_BIG_PECKS",
                "mechanic": "prevent Defense reductions",
                "source_family": "hg-engine btl_scr_cmd_33_statbuffchange",
                "status": "installed",
            },
            "Full Metal Body": {
                "token": "ABILITY_FULL_METAL_BODY",
                "mechanic": "prevent stat reductions; non-ignorable",
                "source_family": "hg-engine btl_scr_cmd_33_statbuffchange",
                "status": "installed",
            },
        },
        "ui_changed": False,
        "innate_storage_changed": False,
        "compile_required": True,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
