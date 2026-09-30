#!/usr/bin/env python3
"""MR10R5 — second historical Ability fast pass.

Restores twenty more identities from the actual historical-runtime queue using
existing canonical/MR10 hooks.  This batch focuses on scalar damage, contact
reactions, simple switch-in effects, priority, healing and weather end-turn
behavior; it intentionally avoids new engine state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Dead Power": ("ABILITY_DEAD_POWER", 385),
    "Flaming Jaws": ("ABILITY_MR_FLAMING_JAWS", 650),
    "Raw Wood": ("ABILITY_MR_RAW_WOOD", 548),
    "Vengeance": ("ABILITY_MR_VENGEANCE", 607),
    "Mighty Horn": ("ABILITY_MR_MIGHTY_HORN", 495),
    "Keen Edge": ("ABILITY_MR_KEEN_EDGE", 472),
    "Super Slammer": ("ABILITY_SUPER_SLAMMER", 590),
    "TerminalVelocity": ("ABILITY_TERMINAL_VELOCITY", 596),
    "Energy Siphon": ("ABILITY_ENERGY_SIPHON", 408),
    "Vitality Strike": ("ABILITY_VITALITY_STRIKE", 612),
    "Inflatable": ("ABILITY_MR_INFLATABLE", 466),
    "Flaming Maw": ("ABILITY_FLAMING_MAW", 424),
    "Smoldering Wood": ("ABILITY_SMOLDERING_WOOD", 571),
    "Venom Crown": ("ABILITY_VENOM_CROWN", 610),
    "Sepia Lens": ("ABILITY_SEPIA_LENS", 565),
    "Malicious": ("ABILITY_MALICIOUS", 489),
    "Funeral Pyre": ("ABILITY_FUNERAL_PYRE", 433),
    "Rest in Peace": ("ABILITY_MR_REST_IN_PEACE", 903),
    "Low Visibility": ("ABILITY_LOW_VISIBILITY", 483),
    "On the Prowl": ("ABILITY_MR_ON_THE_PROWL", 878),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(
    path: Path,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(
    path: Path,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def validate_partition(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row for row in rows
            if row.get("id") == ability_id and row.get("token") == token
        ]
        if len(matches) != 1:
            raise SystemExit(
                f"{name}: expected one reconciled row at {ability_id}, got {len(matches)}"
            )
        row = matches[0]
        if row.get("runtime_enabled") is False or row.get("review_blocked") is True:
            raise SystemExit(f"{name}: runtime-disabled or review-blocked")
        if row.get("exact_effect") in (None, "RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics unavailable")


def patch_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    helpers = """static BOOL Mercury_R5MoveIsHornOrDrill(int move)
{
    switch (move) {
    case MOVE_HORN_ATTACK:
    case MOVE_HORN_DRILL:
    case MOVE_MEGAHORN:
    case MOVE_DRILL_PECK:
    case MOVE_DRILL_RUN:
    case MOVE_SMART_STRIKE:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R5MoveIsHammerOrSlam(int move)
{
    switch (move) {
    case MOVE_SLAM:
    case MOVE_BODY_SLAM:
    case MOVE_HEAVY_SLAM:
    case MOVE_HAMMER_ARM:
    case MOVE_WOOD_HAMMER:
    case MOVE_DRAGON_HAMMER:
    case MOVE_ICE_HAMMER:
    case MOVE_CRABHAMMER:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_R5MoveIsPunching(int move)
{
    int i;

    for (i = 0; i < NELEMS(sPunchingMoves); i++) {
        if (sPunchingMoves[i] == move) {
            return TRUE;
        }
    }

    return FALSE;
}

"""
    insert_before_once(
        path,
        """int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,
""",
        helpers,
        "Mercury_R5MoveIsHornOrDrill",
        "R5 move-family helpers",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    stat_anchor = """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
"""
    stat_block = """    if (attackerParams.ability == ABILITY_DEAD_POWER) {
        attackStat = attackStat * 15 / 10;
    }

    if (attackerParams.ability == ABILITY_TERMINAL_VELOCITY
        && moveClass == CLASS_SPECIAL) {
        spAttackStat += BattleMon_Get(
            battleCtx, attacker, BATTLEMON_SPEED, NULL) / 5;
    }

"""
    insert_before_once(
        path,
        stat_anchor,
        stat_block,
        "attackerParams.ability == ABILITY_TERMINAL_VELOCITY",
        "Dead Power / Terminal Velocity stats",
    )

    offense_anchor = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
"""
    offense_block = """    if ((attackerParams.ability == ABILITY_MR_RAW_WOOD
            || attackerParams.ability == ABILITY_SMOLDERING_WOOD)
        && moveType == TYPE_ROCK && movePower) {
        movePower = movePower * 110 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_VENGEANCE
        && moveType == TYPE_GHOST && movePower
        && attackerParams.curHP <= attackerParams.maxHP / 3) {
        movePower = movePower * 150 / 100;
    }

    if ((attackerParams.ability == ABILITY_MR_MIGHTY_HORN
            || attackerParams.ability == ABILITY_VENOM_CROWN)
        && Mercury_R5MoveIsHornOrDrill(move)) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_MR_KEEN_EDGE
        && Mercury_MoveIsSlicing(move)) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_SUPER_SLAMMER
        && Mercury_R5MoveIsHammerOrSlam(move)) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_FLAMING_MAW
        && Mercury_MoveIsBiting(move)) {
        movePower = movePower * 15 / 10;
    }

"""
    insert_before_once(
        path,
        offense_anchor,
        offense_block,
        "attackerParams.ability == ABILITY_MR_KEEN_EDGE",
        "R5 offensive scalar family",
    )

    defensive_anchor = """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    defensive_block = """    if ((Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_MR_RAW_WOOD) == TRUE
            || Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_SMOLDERING_WOOD) == TRUE)
        && moveType == TYPE_ROCK) {
        damage /= 2;
    }

    if ((fieldConditions & FIELD_CONDITION_SANDSTORM)
        && moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SEPIA_LENS) == TRUE) {
        damage /= 2;
    }

"""
    insert_before_once(
        path,
        defensive_anchor,
        defensive_block,
        "defender, ABILITY_SEPIA_LENS) == TRUE",
        "Raw Wood / Sepia Lens defense",
    )

    nve_anchor = """        if ((*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE) && movePower) {
"""
    nve_block = """            if (attackerParams.ability == ABILITY_SEPIA_LENS) {
                damage *= 2;
            }

"""
    insert_after_once(
        path,
        nve_anchor,
        nve_block,
        "attackerParams.ability == ABILITY_SEPIA_LENS",
        "Sepia Lens Tinted Lens family",
    )


def patch_on_prowl_priority(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;
"""
    block = """
        if (battler1Move != MOVE_NONE
            && battler1Ability == ABILITY_MR_ON_THE_PROWL
            && battleCtx->battleMons[battler1].moveEffectsData.fakeOutTurnNumber
                == battleCtx->totalTurns + 1) {
            if (battler1Priority < 0) {
                battler1Priority = 0;
            } else {
                battler1Priority++;
            }
        }

        if (battler2Move != MOVE_NONE
            && battler2Ability == ABILITY_MR_ON_THE_PROWL
            && battleCtx->battleMons[battler2].moveEffectsData.fakeOutTurnNumber
                == battleCtx->totalTurns + 1) {
            if (battler2Priority < 0) {
                battler2Priority = 0;
            } else {
                battler2Priority++;
            }
        }
"""
    insert_after_once(
        path,
        anchor,
        block,
        "battler1Ability == ABILITY_MR_ON_THE_PROWL",
        "On the Prowl action priority",
    )


def patch_attacker_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
    block = """    if ((DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && battleCtx->attacker != BATTLER_NONE
        && ATTACKING_MON.curHP) {
        int damageTaken = DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            ? DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            : DEFENDER_SELF_TURN_FLAGS.specialDamageTaken;
        int dealt = damageTaken < 0 ? -damageTaken : damageTaken;
        int ability = Battler_Ability(battleCtx, battleCtx->attacker);

        if (ability == ABILITY_ENERGY_SIPHON && dealt > 0) {
            int heal = dealt / 4;
            if (heal < 1) heal = 1;
            ATTACKING_MON.curHP += heal;
            if (ATTACKING_MON.curHP > ATTACKING_MON.maxHP) {
                ATTACKING_MON.curHP = ATTACKING_MON.maxHP;
            }
            BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
        }

        if (ability == ABILITY_VITALITY_STRIKE
            && dealt > 0
            && Mercury_R5MoveIsPunching(battleCtx->moveCur)) {
            int heal = dealt / 10;
            if (heal < 1) heal = 1;
            ATTACKING_MON.curHP += heal;
            if (ATTACKING_MON.curHP > ATTACKING_MON.maxHP) {
                ATTACKING_MON.curHP = ATTACKING_MON.maxHP;
            }
            BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
        }
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_DEAD_POWER
        && DEFENDING_MON.curHP
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur)
        && (DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_CURSE) == FALSE
        && BattleSystem_RandNext(battleSys) % 10 < 2) {
        DEFENDING_MON.statusVolatile |= VOLATILE_CONDITION_CURSE;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_mold_breaker;
        return TRUE;
    }

    if ((Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_FLAMING_JAWS
            || Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_FLAMING_MAW)
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveIsBiting(battleCtx->moveCur)
        && BattleSystem_RandNext(battleSys) % 2 == 0) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_burn;
        return TRUE;
    }

"""
    insert_before_once(
        path,
        anchor,
        block,
        "== ABILITY_MR_FLAMING_JAWS",
        "R5 attacker reactions/healing",
    )


def patch_defender_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    case ABILITY_POISON_POINT:
""",
        """    case ABILITY_VENOM_CROWN:
    case ABILITY_POISON_POINT:
""",
        "Venom Crown Poison Point family",
    )
    replace_once(
        path,
        """    case ABILITY_FLAME_BODY:
""",
        """    case ABILITY_SMOLDERING_WOOD:
    case ABILITY_FLAME_BODY:
""",
        "Smoldering Wood Flame Body family",
    )

    anchor = """    case ABILITY_THERMAL_EXCHANGE: {
"""
    block = """    case ABILITY_MR_INFLATABLE: {
        int moveType;

        if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (DEFENDING_MON.curHP
            && (moveType == TYPE_FIRE || moveType == TYPE_FLYING)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]++;
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

"""
    insert_before_once(
        path,
        anchor,
        block,
        "case ABILITY_MR_INFLATABLE:",
        "Inflatable defensive reaction",
    )


def patch_sand_guard_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    int partner = defender ^ 2;

"""
    block = """    if (WEATHER_IS_SAND
        && (Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_SEPIA_LENS)
            || (partner < MAX_BATTLERS
                && battleCtx->battleMons[partner].curHP
                && Battler_IgnorableAbility(
                    battleCtx, attacker, partner, ABILITY_SEPIA_LENS)))) {
        return TRUE;
    }

"""
    insert_after_once(
        path,
        anchor,
        block,
        "partner, ABILITY_SEPIA_LENS",
        "Sepia Lens Sand Guard priority protection",
    )


def patch_switch_in(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """        case SWITCH_IN_CHECK_STATE_DOWNLOAD:
            for (i = 0; i < maxBattlers; i++) {
                battler = battleCtx->monSpeedOrder[i];

"""
    block = """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && Battler_Ability(battleCtx, battler) == ABILITY_LOW_VISIBILITY) {
                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                    battleCtx->fieldConditionsMask |= FIELD_CONDITION_DEEP_FOG;
                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = SWITCH_IN_CHECK_RESULT_BREAK;
                    break;
                }

                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && Battler_Ability(battleCtx, battler) == ABILITY_MALICIOUS) {
                    int foe;

                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                    for (foe = 0; foe < maxBattlers; foe++) {
                        BattleMon *mon;

                        if (BattleSystem_GetBattlerSide(battleSys, foe)
                                == BattleSystem_GetBattlerSide(battleSys, battler)
                            || battleCtx->battleMons[foe].curHP == 0) {
                            continue;
                        }

                        mon = &battleCtx->battleMons[foe];
                        if (mon->attack >= mon->spAttack) {
                            if (mon->statBoosts[BATTLE_STAT_ATTACK] > MIN_STAT_STAGE) {
                                mon->statBoosts[BATTLE_STAT_ATTACK]--;
                            }
                        } else if (mon->statBoosts[BATTLE_STAT_SP_ATTACK] > MIN_STAT_STAGE) {
                            mon->statBoosts[BATTLE_STAT_SP_ATTACK]--;
                        }

                        if (mon->defense >= mon->spDefense) {
                            if (mon->statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE) {
                                mon->statBoosts[BATTLE_STAT_DEFENSE]--;
                            }
                        } else if (mon->statBoosts[BATTLE_STAT_SP_DEFENSE] > MIN_STAT_STAGE) {
                            mon->statBoosts[BATTLE_STAT_SP_DEFENSE]--;
                        }
                    }

                    battleCtx->msgBattlerTemp = battler;
                    subscript = subscript_mold_breaker;
                    result = SWITCH_IN_CHECK_RESULT_BREAK;
                    break;
                }

"""
    insert_after_once(
        path,
        anchor,
        block,
        "Battler_Ability(battleCtx, battler) == ABILITY_MALICIOUS",
        "Low Visibility / Malicious switch-in",
    )


def patch_turn_end(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    case ABILITY_SHED_SKIN:
"""
    block = """    case ABILITY_MR_REST_IN_PEACE:
        if (battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].curHP
                < battleCtx->battleMons[battler].maxHP
            && (battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG)) {
            int heal = battleCtx->battleMons[battler].maxHP / 8;
            if (heal < 1) heal = 1;
            battleCtx->battleMons[battler].curHP += heal;
            if (battleCtx->battleMons[battler].curHP
                > battleCtx->battleMons[battler].maxHP) {
                battleCtx->battleMons[battler].curHP =
                    battleCtx->battleMons[battler].maxHP;
            }
            BattleMon_CopyToParty(battleSys, battleCtx, battler);
            battleCtx->msgBattlerTemp = battler;
            subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_FUNERAL_PYRE: {
        int i;
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
        BOOL damaged = FALSE;

        for (i = 0; i < maxBattlers; i++) {
            int chip;

            if (battleCtx->battleMons[i].curHP == 0
                || battleCtx->battleMons[i].type1 == TYPE_GHOST
                || battleCtx->battleMons[i].type2 == TYPE_GHOST
                || battleCtx->battleMons[i].type1 == TYPE_DARK
                || battleCtx->battleMons[i].type2 == TYPE_DARK) {
                continue;
            }

            chip = battleCtx->battleMons[i].maxHP / 4;
            if (chip < 1) chip = 1;
            battleCtx->battleMons[i].curHP =
                battleCtx->battleMons[i].curHP > chip
                ? battleCtx->battleMons[i].curHP - chip
                : 0;
            BattleMon_CopyToParty(battleSys, battleCtx, i);
            damaged = TRUE;
        }

        if (damaged) {
            battleCtx->msgBattlerTemp = battler;
            subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

"""
    insert_before_once(
        path,
        anchor,
        block,
        "case ABILITY_FUNERAL_PYRE:",
        "Rest in Peace / Funeral Pyre turn end",
    )


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "dead_power": "ABILITY_DEAD_POWER" in lib and "VOLATILE_CONDITION_CURSE" in lib,
        "flaming_jaws": "ABILITY_MR_FLAMING_JAWS" in lib and "subscript_burn" in lib,
        "raw_wood": "ABILITY_MR_RAW_WOOD" in lib and "movePower = movePower * 110 / 100;" in lib,
        "vengeance": "ABILITY_MR_VENGEANCE" in lib and "moveType == TYPE_GHOST" in lib,
        "mighty_horn": "ABILITY_MR_MIGHTY_HORN" in lib and "Mercury_R5MoveIsHornOrDrill" in lib,
        "keen_edge": "ABILITY_MR_KEEN_EDGE" in lib and "Mercury_MoveIsSlicing(move)" in lib,
        "super_slammer": "ABILITY_SUPER_SLAMMER" in lib and "Mercury_R5MoveIsHammerOrSlam" in lib,
        "terminal_velocity": "ABILITY_TERMINAL_VELOCITY" in lib and "BATTLEMON_SPEED" in lib,
        "energy_siphon": "ABILITY_ENERGY_SIPHON" in lib and "dealt / 4" in lib,
        "vitality_strike": "ABILITY_VITALITY_STRIKE" in lib and "dealt / 10" in lib,
        "inflatable": "case ABILITY_MR_INFLATABLE:" in lib,
        "flaming_maw": "ABILITY_FLAMING_MAW" in lib and "movePower = movePower * 15 / 10;" in lib,
        "smoldering_wood": "case ABILITY_SMOLDERING_WOOD:" in lib,
        "venom_crown": "case ABILITY_VENOM_CROWN:" in lib,
        "sepia_lens": lib.count("ABILITY_SEPIA_LENS") >= 3,
        "malicious": "ABILITY_MALICIOUS" in lib and "mon->attack >= mon->spAttack" in lib,
        "funeral_pyre": "case ABILITY_FUNERAL_PYRE:" in lib and "maxHP / 4" in lib,
        "rest_in_peace": "case ABILITY_MR_REST_IN_PEACE:" in lib and "maxHP / 8" in lib,
        "low_visibility": "ABILITY_LOW_VISIBILITY" in lib and "FIELD_CONDITION_DEEP_FOG" in lib,
        "on_the_prowl": "ABILITY_MR_ON_THE_PROWL" in lib and "battler1Priority = 0;" in lib,
        "registry_updated": all(token in reg for token in TOKENS),
        "ids_stable": all(
            len(abilities) > ability_id and abilities[ability_id] == token
            for token, ability_id in IMPLEMENTED.values()
        ),
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_ability_partition_16bit_full_identity.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10r5-fast-pass.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_helpers(root)
    patch_damage(root)
    patch_on_prowl_priority(root)
    patch_attacker_reactions(root)
    patch_defender_reactions(root)
    patch_sand_guard_family(root)
    patch_switch_in(root)
    patch_turn_end(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R5_HISTORICAL_FAST_PASS",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "historical_runtime_before": 80,
        "historical_runtime_after": 60,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10R5 historical fast pass failed")


if __name__ == "__main__":
    main()
