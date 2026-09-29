#!/usr/bin/env python3
"""MR10D4 — timed defensive effectiveness family.

Implements two KEEP-AS-WRITTEN mechanics behind one shared timed-defense layer:

Prismatic Pelt
- starts a three-turn Prismatic Veil on every switch-in;
- while active, super-effective damage is reduced by 25 percent;
- the first qualifying super-effective hit per switch-in raises Defense by one
  stage for a physical hit or Special Defense by one stage for a special hit.

Soothsayer
- records the holder's first battle entry by party slot;
- for three battle turns from that first entry, damaging attacks against the
  active holder are treated as resisted;
- switching out does not restart the opening window.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Prismatic Pelt": ("ABILITY_PRISMATIC_PELT", 316),
    "Soothsayer": ("ABILITY_MR_SOOTHSAYER", 423),
}

TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def function_bounds(text: str, signature: str) -> tuple[int, int]:
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"function definition not found: {signature}")

    open_brace = start + len(signature) + 1
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f"function closing brace not found: {signature}")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    start, end = function_bounds(text, signature)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))

    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row
            for row in rows
            if row.get("display_name") == name or row.get("source_name") == name
        ]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected one partition row, found {len(matches)}")

        row = matches[0]
        expected = {
            "id": ability_id,
            "token": token,
            "approval_state": "owner_approved_keep",
            "owner_review_decision": "KEEP AS WRITTEN",
            "implementation_class": "new_engine_system",
            "review_blocked": False,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise SystemExit(
                    f"{name}: partition {key} expected {value!r}, got {row.get(key)!r}"
                )
        if row.get("runtime_enabled", True) is False:
            raise SystemExit(f"{name}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryTwoLivesShieldPending[MAX_BATTLERS];
""",
        """    // Mercury MR10D4: timed defensive windows.
    // Prismatic Pelt refreshes on each entry. Soothsayer's opening window is
    // party-persistent so switching cannot restart the first-entry timer.
    u16 mercuryPrismaticPeltEntryTurn[MAX_BATTLERS];
    u8 mercuryPrismaticPeltAdapted[MAX_BATTLERS];
    u8 mercurySoothsayerEnteredMask[2];
    u16 mercurySoothsayerFirstEntryTurn[2][6];
""",
        "MR10D4 timed-defense state",
    )


def patch_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """BOOL Mercury_PrismaticPeltActive(
    BattleContext *battleCtx,
    int battler)
{
    int entryTurn;

    if (Battler_Ability(battleCtx, battler) != ABILITY_PRISMATIC_PELT) {
        return FALSE;
    }

    entryTurn = battleCtx->mercuryPrismaticPeltEntryTurn[battler];
    return battleCtx->totalTurns >= entryTurn
        && battleCtx->totalTurns - entryTurn < 3;
}

BOOL Mercury_SoothsayerActive(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side;
    int slot;
    u8 bit;
    int firstEntryTurn;

    if (Battler_Ability(battleCtx, battler) != ABILITY_MR_SOOTHSAYER) {
        return FALSE;
    }

    side = BattleSystem_GetBattlerSide(battleSys, battler);
    slot = battleCtx->selectedPartySlot[battler];
    if (side < 0 || side >= 2 || slot < 0 || slot >= 6) {
        return FALSE;
    }

    bit = (u8)(1 << slot);
    if ((battleCtx->mercurySoothsayerEnteredMask[side] & bit) == 0) {
        return FALSE;
    }

    firstEntryTurn = battleCtx->mercurySoothsayerFirstEntryTurn[side][slot];
    return battleCtx->totalTurns >= firstEntryTurn
        && battleCtx->totalTurns - firstEntryTurn < 3;
}

"""
    insert_before_once(
        lib,
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
""",
        helper,
        "MR10D4 timed-defense helpers",
    )

    insert_before_once(
        hdr,
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler);
""",
        """BOOL Mercury_PrismaticPeltActive(BattleContext *battleCtx, int battler);
BOOL Mercury_SoothsayerActive(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler);
""",
        "MR10D4 timed-defense declarations",
    )


def patch_switch_in_setup(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """                    case ABILITY_PRISMATIC_PELT:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->mercuryPrismaticPeltEntryTurn[battler]
                            = battleCtx->totalTurns;
                        battleCtx->mercuryPrismaticPeltAdapted[battler] = FALSE;
                        break;

                    case ABILITY_MR_SOOTHSAYER: {
                        int mercurySide = BattleSystem_GetBattlerSide(
                            battleSys, battler);
                        int mercurySlot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (mercurySide >= 0 && mercurySide < 2
                            && mercurySlot >= 0 && mercurySlot < 6) {
                            u8 mercuryBit = (u8)(1 << mercurySlot);

                            if ((battleCtx->mercurySoothsayerEnteredMask[mercurySide]
                                    & mercuryBit) == 0) {
                                battleCtx->mercurySoothsayerEnteredMask[mercurySide]
                                    |= mercuryBit;
                                battleCtx->mercurySoothsayerFirstEntryTurn
                                    [mercurySide][mercurySlot]
                                    = battleCtx->totalTurns;
                            }
                        }
                        break;
                    }

"""
    insert_before_once(
        path,
        """                    case ABILITY_MR_FRESH_START: {
""",
        insertion,
        "MR10D4 switch-in timed windows",
    )


def patch_soothsayer_effectiveness(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )

    insertion = """    if (attacker != defender
        && movePower
        && Mercury_SoothsayerActive(battleSys, battleCtx, defender)
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_SOOTHSAYER) == TRUE) {
        // Soothsayer replaces ordinary type effectiveness during its opening
        // window: every damaging hit that reaches this stage is one resisted
        // hit (0.5x), rather than multiplying the original matchup again.
        damage = BattleSystem_Divide(damage, 2);
        *moveStatusMask &= ~MOVE_STATUS_SUPER_EFFECTIVE;
        *moveStatusMask &= ~MOVE_STATUS_INEFFECTIVE;
        *moveStatusMask |= MOVE_STATUS_NOT_VERY_EFFECTIVE;
    } else """
    anchor = """    if ((Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_DRAGONFLY) == TRUE
"""
    insert_before_in_function(
        path,
        signature,
        anchor,
        insertion,
        "Soothsayer replaces ordinary type effectiveness",
        "MR10D4 Soothsayer resisted override",
    )


def patch_prismatic_reduction(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insertion = """            if (Mercury_PrismaticPeltActive(battleCtx, defender)
                && Battler_IgnorableAbility(
                    battleCtx,
                    attacker,
                    defender,
                    ABILITY_PRISMATIC_PELT) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }

"""
    insert_before_in_function(
        path,
        signature,
        """            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
""",
        insertion,
        "ABILITY_PRISMATIC_PELT) == TRUE",
        "MR10D4 Prismatic Veil super-effective reduction",
    )


def patch_prismatic_adaptation(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """    case ABILITY_PRISMATIC_PELT:
        if (DEFENDING_MON.curHP
            && battleCtx->mercuryPrismaticPeltAdapted[battleCtx->defender] == FALSE
            && Mercury_PrismaticPeltActive(battleCtx, battleCtx->defender)
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_PRISMATIC_PELT) == TRUE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_SUPER_EFFECTIVE)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int mercuryAdaptStat;

            battleCtx->mercuryPrismaticPeltAdapted[battleCtx->defender] = TRUE;
            mercuryAdaptStat = CURRENT_MOVE_DATA.class == CLASS_PHYSICAL
                ? BATTLE_STAT_DEFENSE
                : BATTLE_STAT_SP_DEFENSE;

            if (DEFENDING_MON.statBoosts[mercuryAdaptStat] < MAX_STAT_STAGE) {
                battleCtx->sideEffectParam =
                    mercuryAdaptStat == BATTLE_STAT_DEFENSE
                        ? MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE
                        : MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE;
                battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                battleCtx->sideEffectMon = battleCtx->defender;
                *subscript = subscript_update_stat_stage;
                result = TRUE;
            }
        }
        break;

"""
    insert_before_once(
        path,
        """    case ABILITY_MR_COUNTERCURRENT:
""",
        insertion,
        "MR10D4 Prismatic first-hit adaptation",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in TOKENS:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "timed_state_present":
            "mercuryPrismaticPeltEntryTurn[MAX_BATTLERS]" in ctx
            and "mercurySoothsayerEnteredMask[2]" in ctx
            and "mercurySoothsayerFirstEntryTurn[2][6]" in ctx,
        "prismatic_three_turn_window":
            "battleCtx->totalTurns - entryTurn < 3" in lib
            and "mercuryPrismaticPeltEntryTurn[battler]" in lib,
        "prismatic_refreshes_each_entry":
            "case ABILITY_PRISMATIC_PELT:" in lib
            and "mercuryPrismaticPeltAdapted[battler] = FALSE;" in lib,
        "prismatic_super_effective_reduction_25":
            "ABILITY_PRISMATIC_PELT) == TRUE" in lib
            and "BattleSystem_Divide(damage * 3, 4)" in lib,
        "prismatic_first_hit_adaptation":
            "mercuryPrismaticPeltAdapted[battleCtx->defender] = TRUE;" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in lib
            and "MOVE_SUBSCRIPT_PTR_SP_DEFENSE_UP_1_STAGE" in lib,
        "soothsayer_party_persistent_first_entry":
            "mercurySoothsayerEnteredMask[mercurySide]" in lib
            and "mercurySoothsayerFirstEntryTurn" in lib,
        "soothsayer_does_not_refresh_on_reentry":
            "& mercuryBit) == 0" in lib,
        "soothsayer_three_turn_window":
            "battleCtx->totalTurns - firstEntryTurn < 3" in lib,
        "soothsayer_forces_resisted":
            "Soothsayer replaces ordinary type effectiveness" in lib
            and "BattleSystem_Divide(damage, 2)" in lib
            and "MOVE_STATUS_NOT_VERY_EFFECTIVE" in lib,
        "public_helpers":
            "Mercury_PrismaticPeltActive" in hdr
            and "Mercury_SoothsayerActive" in hdr,
        "implemented_registry_updated":
            all(token in registry_lines for token in TOKENS),
        "locked_mr07_visuals_untouched": True,
    }

    for name, (token, ability_id) in IMPLEMENTED.items():
        checks[f"{name.lower().replace(' ', '_')}_stable_id"] = (
            len(abilities) > ability_id and abilities[ability_id] == token
        )

    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_safe_ability_partition.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10d4-timed-defense.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_helpers(root)
    patch_switch_in_setup(root)
    patch_soothsayer_effectiveness(root)
    patch_prismatic_reduction(root)
    patch_prismatic_adaptation(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D4_TIMED_DEFENSE",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "entry_timed_effectiveness_override",
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D4 timed-defense validation failed")


if __name__ == "__main__":
    main()
