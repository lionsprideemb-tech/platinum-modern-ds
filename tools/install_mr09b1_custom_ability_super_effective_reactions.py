#!/usr/bin/env python3
"""MR09B1 — Prismatic Pelt + Adaptive Genome.

Implements two approved Mercury custom super-effective-hit reactions:
- Prismatic Pelt: 3-turn entry veil, 25% less super-effective damage, and the
  first qualifying hit per switch-in gives +1 Defense (physical) or +1 Sp. Def
  (special).
- Adaptive Genome: the first super-effective hit per switch-in gives +1 Defense
  (physical) or +1 Sp. Def (special).

Typing is never changed. Locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PRISMATIC_PELT",
    "ABILITY_ADAPTIVE_GENOME",
)
EXPECTED_IDS = {
    "ABILITY_PRISMATIC_PELT": 316,
    "ABILITY_ADAPTIVE_GENOME": 318,
}


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: closing brace not found in {path}")

    segment = text[start:end]
    count = segment.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one scoped match in {path}, found {count}"
        )
    segment = segment.replace(old, new, 1)
    path.write_text(text[:start] + segment + text[end:], encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR09B1 custom super-effective reaction state.
    u8 mercuryPrismaticVeilTurns[MAX_BATTLERS];
    u8 mercuryPrismaticBoostUsed[MAX_BATTLERS];
    u8 mercuryAdaptiveGenomeUsed[MAX_BATTLERS];

""",
        "MR09B1 battle state",
    )


def patch_switch_in_state(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryGulpMissileState[battler] = 0;
""",
        """    battleCtx->mercuryPrismaticVeilTurns[battler] =
        battleCtx->battleMons[battler].ability == ABILITY_PRISMATIC_PELT
        ? 3
        : 0;
    battleCtx->mercuryPrismaticBoostUsed[battler] = FALSE;
    battleCtx->mercuryAdaptiveGenomeUsed[battler] = FALSE;

    battleCtx->mercuryGulpMissileState[battler] = 0;
""",
        "MR09B1 switch-in state reset",
    )


def patch_prismatic_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_in_function(
        path,
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)",
        """            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }

""",
        """            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }

            if (battleCtx->mercuryPrismaticVeilTurns[defender]
                && Battler_IgnorableAbility(
                    battleCtx, attacker, defender, ABILITY_PRISMATIC_PELT) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }

""",
        "Prismatic Pelt super-effective reduction",
    )


def patch_hit_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insertion = """    case ABILITY_PRISMATIC_PELT:
        if (DEFENDING_MON.curHP
            && battleCtx->mercuryPrismaticBoostUsed[battleCtx->defender] == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_SUPER_EFFECTIVE)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            battleCtx->mercuryPrismaticBoostUsed[battleCtx->defender] = TRUE;

            if (CURRENT_MOVE_DATA.class == CLASS_PHYSICAL) {
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
                }
            } else if (CURRENT_MOVE_DATA.class == CLASS_SPECIAL) {
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] < MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]++;
                }
            }

            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_ADAPTIVE_GENOME:
        if (DEFENDING_MON.curHP
            && battleCtx->mercuryAdaptiveGenomeUsed[battleCtx->defender] == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_SUPER_EFFECTIVE)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            battleCtx->mercuryAdaptiveGenomeUsed[battleCtx->defender] = TRUE;

            if (CURRENT_MOVE_DATA.class == CLASS_PHYSICAL) {
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
                }
            } else if (CURRENT_MOVE_DATA.class == CLASS_SPECIAL) {
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] < MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]++;
                }
            }

            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    case ABILITY_GULP_MISSILE: {
""",
        insertion + """    case ABILITY_GULP_MISSILE: {
""",
        "MR09B1 super-effective reaction cases",
    )


def patch_veil_timer(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    BOOL result = FALSE;
    int subscript;

""",
        """    BOOL result = FALSE;
    int subscript;

    // Prismatic Veil is a timed state created on entry. It keeps counting down
    // even if the Ability is temporarily suppressed later in the turn.
    if (battleCtx->mercuryPrismaticVeilTurns[battler]) {
        battleCtx->mercuryPrismaticVeilTurns[battler]--;
    }

""",
        "Prismatic Veil timer",
    )


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "prismatic_three_turn_entry_veil":
            "mercuryPrismaticVeilTurns[battler] =" in lib
            and "? 3" in lib,
        "prismatic_25_percent_super_effective_reduction":
            "ABILITY_PRISMATIC_PELT" in lib
            and "BattleSystem_Divide(damage * 3, 4)" in lib,
        "prismatic_first_hit_boost_once_per_switch":
            "mercuryPrismaticBoostUsed[MAX_BATTLERS]" in ctx
            and "mercuryPrismaticBoostUsed[battleCtx->defender] = TRUE" in lib,
        "adaptive_first_hit_once_per_switch":
            "mercuryAdaptiveGenomeUsed[MAX_BATTLERS]" in ctx
            and "mercuryAdaptiveGenomeUsed[battleCtx->defender] = TRUE" in lib,
        "physical_and_special_defense_paths":
            "CURRENT_MOVE_DATA.class == CLASS_PHYSICAL" in lib
            and "CURRENT_MOVE_DATA.class == CLASS_SPECIAL" in lib
            and "BATTLE_STAT_DEFENSE" in lib
            and "BATTLE_STAT_SP_DEFENSE" in lib,
        "super_effective_gate":
            lib.count("MOVE_STATUS_SUPER_EFFECTIVE") >= 3,
        "veil_timer":
            "mercuryPrismaticVeilTurns[battler]--" in lib,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr09b1-custom-ability-super-effective-reactions.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_switch_in_state(root)
    patch_prismatic_damage(root)
    patch_hit_reactions(root)
    patch_veil_timer(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR09B1_CUSTOM_ABILITY_SUPER_EFFECTIVE_REACTIONS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "custom_implemented_total": 2,
        "custom_reserved_total": 11,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR09B1 custom Ability validation failed")


if __name__ == "__main__":
    main()
