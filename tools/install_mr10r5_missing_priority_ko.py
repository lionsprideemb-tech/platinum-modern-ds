#!/usr/bin/env python3
"""MR10R5 — second historical Ability fast pass.

Restores twenty more identities from the actual historical-runtime queue.
This batch concentrates on shared damage/stat, healing, weather, contact and
type-chart hooks so the queue can move in large chunks without one-off code.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMPLEMENTED = {
    "Blood Price": ("ABILITY_BLOOD_PRICE", 362),
    "Dead Power": ("ABILITY_DEAD_POWER", 385),
    "Energy Siphon": ("ABILITY_ENERGY_SIPHON", 408),
    "Flame Bubble": ("ABILITY_FLAME_BUBBLE", 422),
    "Flaming Maw": ("ABILITY_FLAMING_MAW", 424),
    "Funeral Pyre": ("ABILITY_FUNERAL_PYRE", 433),
    "Last Stand": ("ABILITY_LAST_STAND", 475),
    "Low Visibility": ("ABILITY_LOW_VISIBILITY", 483),
    "Molten Blades": ("ABILITY_MOLTEN_BLADES", 499),
    "Mosh Pit": ("ABILITY_MOSH_PIT", 504),
    "Permanence": ("ABILITY_PERMANENCE", 522),
    "Phantom Pain": ("ABILITY_PHANTOM_PAIN", 525),
    "Rage Point": ("ABILITY_RAGE_POINT", 544),
    "Sepia Lens": ("ABILITY_SEPIA_LENS", 565),
    "Smoldering Wood": ("ABILITY_SMOLDERING_WOOD", 571),
    "TerminalVelocity": ("ABILITY_TERMINAL_VELOCITY", 596),
    "Vengeful Spirit": ("ABILITY_VENGEFUL_SPIRIT", 608),
    "Vitality Strike": ("ABILITY_VITALITY_STRIKE", 612),
    "White Noise": ("ABILITY_WHITE_NOISE", 622),
    "Drake Of Rage": ("ABILITY_DRAKE_OF_RAGE", 395),
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


def insert_before_once(path: Path, anchor: str, insertion: str, marker: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, marker: str, label: str) -> None:
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
        matches = [r for r in rows if r.get("id") == ability_id and r.get("token") == token]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected reconciled row {ability_id}, got {len(matches)}")
        row = matches[0]
        if row.get("runtime_enabled") is False or row.get("review_blocked") is True:
            raise SystemExit(f"{name}: runtime-disabled or review-blocked")
        if row.get("exact_effect") in (None, "RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics unavailable")


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    stat_anchor = """    attackStage += DEFAULT_STAT_STAGE;
    defenseStage += DEFAULT_STAT_STAGE;
    spAttackStage += DEFAULT_STAT_STAGE;
    spDefenseStage += DEFAULT_STAT_STAGE;

"""
    stat_block = """    if (attackerParams.ability == ABILITY_DEAD_POWER) {
        attackStat = attackStat * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_TERMINAL_VELOCITY
        && moveClass == CLASS_SPECIAL) {
        spAttackStat += BattleMon_Get(
            battleCtx, attacker, BATTLEMON_SPEED, NULL) * 20 / 100;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_LAST_STAND) == TRUE
        && defenderParams.maxHP) {
        int missingHp = defenderParams.maxHP - defenderParams.curHP;
        defenseStat = defenseStat
            * (100 * defenderParams.maxHP + 60 * missingHp)
            / (100 * defenderParams.maxHP);
        spDefenseStat = spDefenseStat
            * (100 * defenderParams.maxHP + 60 * missingHp)
            / (100 * defenderParams.maxHP);
    }

"""
    insert_before_once(
        path, stat_anchor, stat_block,
        "attackerParams.ability == ABILITY_TERMINAL_VELOCITY",
        "R5 stat family",
    )

    power_anchor = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
"""
    power_block = """    if (attackerParams.ability == ABILITY_BLOOD_PRICE && movePower) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_FLAMING_MAW
        && Mercury_MoveIsBiting(move)) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_MOLTEN_BLADES
        && Mercury_MoveIsSlicing(move)) {
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_FLAME_BUBBLE
        && moveType == TYPE_WATER) {
        movePower *= 2;
    }

    if (attackerParams.ability == ABILITY_RAGE_POINT
        && attackerParams.statusMask) {
        movePower = movePower * 150 / 100;
    }

    if (attackerParams.ability == ABILITY_VENGEFUL_SPIRIT
        && moveType == TYPE_GHOST) {
        movePower = movePower
            * (attackerParams.curHP <= attackerParams.maxHP / 3 ? 150 : 100)
            / 100;
    }

    if (attackerParams.ability == ABILITY_SMOLDERING_WOOD
        && moveType == TYPE_ROCK) {
        movePower = movePower * 110 / 100;
    }

    if (Mercury_AllyHasAbility(
            battleSys, battleCtx, attacker, ABILITY_MOSH_PIT)) {
        int effect = MOVE_DATA(move).effect;
        if (effect == BATTLE_EFFECT_RECOIL_QUARTER
            || effect == BATTLE_EFFECT_RECOIL_THIRD
            || effect == BATTLE_EFFECT_RECOIL_HALF
            || effect == BATTLE_EFFECT_RECOIL_BURN_HIT
            || effect == BATTLE_EFFECT_RECOIL_PARALYZE_HIT) {
            movePower = movePower * 150 / 100;
        } else {
            movePower = movePower * 125 / 100;
        }
    }

"""
    insert_before_once(
        path, power_anchor, power_block,
        "attackerParams.ability == ABILITY_BLOOD_PRICE",
        "R5 power family",
    )

    defense_anchor = """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    defense_block = """    if (moveType == TYPE_FIRE
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_FLAME_BUBBLE) == TRUE) {
        damage /= 2;
    }

    if (moveType == TYPE_ROCK
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SMOLDERING_WOOD) == TRUE) {
        damage /= 2;
    }

"""
    insert_before_once(
        path, defense_anchor, defense_block,
        "defender, ABILITY_FLAME_BUBBLE) == TRUE",
        "R5 defensive family",
    )

    replace_once(
        path,
        """        if ((*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE) && movePower) {
            if (Battler_Ability(battleCtx, attacker) == ABILITY_TINTED_LENS) {
                damage *= 2;
            }
        }
""",
        """        if ((*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE) && movePower) {
            if (Battler_Ability(battleCtx, attacker) == ABILITY_TINTED_LENS
                || Battler_Ability(battleCtx, attacker) == ABILITY_SEPIA_LENS
                || Battler_Ability(battleCtx, attacker) == ABILITY_DRAKE_OF_RAGE) {
                damage *= 2;
            }
        }
""",
        "Sepia Lens / Drake Of Rage Tinted Lens family",
    )

    replace_once(
        path,
        """        if ((attackerParams.statusMask & MON_CONDITION_BURN) && attackerParams.ability != ABILITY_GUTS) {
            damage /= 2;
        }
""",
        """        if ((attackerParams.statusMask & MON_CONDITION_BURN)
            && attackerParams.ability != ABILITY_GUTS
            && attackerParams.ability != ABILITY_RAGE_POINT) {
            damage /= 2;
        }
""",
        "Rage Point burn Attack penalty bypass",
    )


def patch_phantom_pain(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """static BOOL BasicTypeMulApplies(BattleContext *battleCtx, int attacker, int defender, int chartEntry)
{
"""
    insertion = """    if (Battler_Ability(battleCtx, attacker) == ABILITY_PHANTOM_PAIN
        && sTypeMatchupMultipliers[chartEntry][0] == TYPE_GHOST
        && sTypeMatchupMultipliers[chartEntry][1] == TYPE_NORMAL
        && sTypeMatchupMultipliers[chartEntry][2] == TYPE_MULTI_IMMUNE) {
        return FALSE;
    }

"""
    insert_after_once(
        path, anchor, insertion,
        "attacker) == ABILITY_PHANTOM_PAIN",
        "Phantom Pain runtime type immunity",
    )

    search = """                if (sTypeMatchupMultipliers[chartEntry][0] == attackerAbility) {
"""
    # The AI/general path varies across upstream revisions. Patch the concrete
    # Ghost/Normal immunity immediately before type multipliers are applied.
    ai_anchor = """            if (sTypeMatchupMultipliers[chartEntry][0] == moveType) {
"""
    ai_block = """            if (attackerAbility == ABILITY_PHANTOM_PAIN
                && moveType == TYPE_GHOST
                && sTypeMatchupMultipliers[chartEntry][1] == TYPE_NORMAL
                && sTypeMatchupMultipliers[chartEntry][2] == TYPE_MULTI_IMMUNE) {
                chartEntry++;
                continue;
            }

"""
    # There are two loops with this text; only the latter belongs to
    # BattleSystem_CalcEffectiveness. Do a scoped insertion.
    text = path.read_text(encoding="utf-8")
    marker = "attackerAbility == ABILITY_PHANTOM_PAIN"
    if text.count(marker) < 2:
        start = text.find("void BattleSystem_CalcEffectiveness(")
        if start < 0:
            raise SystemExit("Phantom Pain: CalcEffectiveness not found")
        end = text.find("\n}", start)
        while end >= 0 and text[end + 2:end + 7] not in ("\n\nsta", "\n\nint", "\n\nBOOL", "\n\nvoid"):
            nxt = text.find("\n}", end + 2)
            if nxt < 0:
                break
            end = nxt
        block = text[start:end if end > start else len(text)]
        if ai_block not in block:
            idx = block.find(ai_anchor)
            if idx < 0:
                raise SystemExit("Phantom Pain: AI type loop anchor missing")
            block = block[:idx] + ai_block + block[idx:]
            text = text[:start] + block + text[start + len(text[start:end if end > start else len(text)]):]
            path.write_text(text, encoding="utf-8")


def patch_contact_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_DEAD_POWER
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

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_FLAMING_MAW
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

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MOLTEN_BLADES
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveIsSlicing(battleCtx->moveCur)
        && BattleSystem_RandNext(battleSys) % 10 < 2) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_burn;
        return TRUE;
    }

"""
    insert_before_once(
        path, anchor, insertion,
        "== ABILITY_DEAD_POWER",
        "Dead Power / Flaming Maw / Molten Blades reactions",
    )

    defender_anchor = """    case ABILITY_THERMAL_EXCHANGE: {
"""
    defender_block = """    case ABILITY_RAGE_POINT:
        if (battleCtx->criticalMul > 1
            && DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]++;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]++;
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_SMOLDERING_WOOD:
        if (ATTACKING_MON.curHP
            && ATTACKING_MON.status == MON_CONDITION_NONE
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_burn;
            result = TRUE;
        }
        break;

    case ABILITY_WHITE_NOISE:
        if (ATTACKING_MON.curHP
            && ATTACKING_MON.status == MON_CONDITION_NONE
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_paralyze;
            result = TRUE;
        }
        break;

    case ABILITY_VENGEFUL_SPIRIT:
        if (battleCtx->defender == battleCtx->faintedMon
            && ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (ATTACKING_MON.statusVolatile & VOLATILE_CONDITION_CURSE) == FALSE) {
            ATTACKING_MON.statusVolatile |= VOLATILE_CONDITION_CURSE;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        path, defender_anchor, defender_block,
        "case ABILITY_RAGE_POINT:",
        "R5 defender reaction family",
    )


def patch_after_move_family(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """    AFTER_MOVE_HIT_STATE_END
""",
        """    AFTER_MOVE_HIT_STATE_MERCURY_ENERGY_SIPHON,
    AFTER_MOVE_HIT_STATE_MERCURY_VITALITY_STRIKE,
    AFTER_MOVE_HIT_STATE_MERCURY_BLOOD_PRICE,

""",
        "AFTER_MOVE_HIT_STATE_MERCURY_ENERGY_SIPHON,",
        "R5 after-move state enum",
    )

    helper_anchor = """static BOOL BattleControllerPlayer_TriggerAfterMoveHitEffects(BattleSystem *battleSys, BattleContext *battleCtx)
{
"""
    helper = """static BOOL Mercury_R5MoveIsPunching(int move)
{
    switch (move) {
    case MOVE_ICE_PUNCH:
    case MOVE_FIRE_PUNCH:
    case MOVE_THUNDER_PUNCH:
    case MOVE_MACH_PUNCH:
    case MOVE_FOCUS_PUNCH:
    case MOVE_DIZZY_PUNCH:
    case MOVE_DYNAMIC_PUNCH:
    case MOVE_HAMMER_ARM:
    case MOVE_MEGA_PUNCH:
    case MOVE_COMET_PUNCH:
    case MOVE_METEOR_MASH:
    case MOVE_SHADOW_PUNCH:
    case MOVE_DRAIN_PUNCH:
    case MOVE_BULLET_PUNCH:
    case MOVE_SKY_UPPERCUT:
        return TRUE;
    default:
        return FALSE;
    }
}

"""
    insert_before_once(
        path, helper_anchor, helper,
        "Mercury_R5MoveIsPunching",
        "R5 punching helper",
    )

    case_anchor = """        case AFTER_MOVE_HIT_STATE_END:
"""
    cases = """        case AFTER_MOVE_HIT_STATE_MERCURY_ENERGY_SIPHON:
            if (Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_ENERGY_SIPHON
                && battleCtx->defender != BATTLER_NONE
                && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
                && ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt
                && ATTACKING_MON.curHP
                && ATTACKING_MON.curHP < ATTACKING_MON.maxHP) {
                battleCtx->hpCalcTemp = BattleSystem_Divide(
                    ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt * -1, 4);
                battleCtx->msgBattlerTemp = battleCtx->attacker;
                LOAD_SUBSEQ(subscript_restore_a_little_hp);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                machineState = STATE_BREAK_OUT;
            }
            battleCtx->afterMoveHitCheckState++;
            break;

        case AFTER_MOVE_HIT_STATE_MERCURY_VITALITY_STRIKE:
            if (Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_VITALITY_STRIKE
                && Mercury_R5MoveIsPunching(battleCtx->moveCur)
                && battleCtx->defender != BATTLER_NONE
                && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
                && ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt
                && ATTACKING_MON.curHP
                && ATTACKING_MON.curHP < ATTACKING_MON.maxHP) {
                battleCtx->hpCalcTemp = BattleSystem_Divide(
                    ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt * -1, 10);
                battleCtx->msgBattlerTemp = battleCtx->attacker;
                LOAD_SUBSEQ(subscript_restore_a_little_hp);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                machineState = STATE_BREAK_OUT;
            }
            battleCtx->afterMoveHitCheckState++;
            break;

        case AFTER_MOVE_HIT_STATE_MERCURY_BLOOD_PRICE:
            if (Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_BLOOD_PRICE
                && battleCtx->defender != BATTLER_NONE
                && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
                && CURRENT_MOVE_DATA.class != CLASS_STATUS
                && ATTACKING_MON.curHP) {
                battleCtx->hpCalcTemp = BattleSystem_Divide(
                    ATTACKING_MON.maxHP * -1, 10);
                battleCtx->msgBattlerTemp = battleCtx->attacker;
                LOAD_SUBSEQ(subscript_lose_hp_from_item);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                machineState = STATE_BREAK_OUT;
            }
            battleCtx->afterMoveHitCheckState++;
            break;

"""
    insert_before_once(
        path, case_anchor, cases,
        "AFTER_MOVE_HIT_STATE_MERCURY_ENERGY_SIPHON:",
        "R5 after-move effects",
    )


def patch_low_visibility(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """                    case ABILITY_ELECTRIC_SURGE:
"""
    block = """                    case ABILITY_LOW_VISIBILITY:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if ((battleCtx->fieldConditionsMask
                                & FIELD_CONDITION_DEEP_FOG) == FALSE) {
                            battleCtx->fieldConditionsMask |= FIELD_CONDITION_DEEP_FOG;
                            battleCtx->fieldConditions.weatherTurns = 8;
                            battleCtx->msgBattlerTemp = battler;
                            subscript = subscript_overworld_fog;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

"""
    insert_before_once(
        path, anchor, block,
        "case ABILITY_LOW_VISIBILITY:",
        "Low Visibility entry fog",
    )


def patch_permanence(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"
    script = root / "src/battle/battle_script.c"

    helper = """BOOL Mercury_PermanenceBlocksHealing(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    return BattleSystem_CountAbility(
        battleSys,
        battleCtx,
        COUNT_ALIVE_BATTLERS_THEIR_SIDE,
        battler,
        ABILITY_PERMANENCE) != 0;
}

"""
    insert_before_once(
        lib,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
""",
        helper,
        "Mercury_PermanenceBlocksHealing",
        "Permanence helper",
    )
    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_PermanenceBlocksHealing(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        "Mercury_PermanenceBlocksHealing",
        "Permanence declaration",
    )

    anchor = """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
"""
    block = """    if (battleCtx->hpCalcTemp > 0
        && Mercury_PermanenceBlocksHealing(
            battleSys, battleCtx, battler)) {
        battleCtx->hpCalcTemp = 0;
    }

"""
    insert_after_once(
        script, anchor, block,
        "Mercury_PermanenceBlocksHealing(",
        "Permanence global heal lock",
    )


def patch_turn_end_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
{
    BOOL result = FALSE;
    int subscript;

    switch (Battler_Ability(battleCtx, battler)) {
"""
    block = """    if (Battler_Ability(battleCtx, battler) == ABILITY_WHITE_NOISE
        && (battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG)
        && battleCtx->battleMons[battler].curHP
        && battleCtx->battleMons[battler].curHP
            < battleCtx->battleMons[battler].maxHP) {
        int heal = BattleSystem_Divide(
            battleCtx->battleMons[battler].maxHP, 8);
        battleCtx->battleMons[battler].curHP += heal;
        if (battleCtx->battleMons[battler].curHP
            > battleCtx->battleMons[battler].maxHP) {
            battleCtx->battleMons[battler].curHP
                = battleCtx->battleMons[battler].maxHP;
        }
        BattleMon_CopyToParty(battleSys, battleCtx, battler);
    }

    if (Battler_Ability(battleCtx, battler) == ABILITY_FUNERAL_PYRE
        && battleCtx->battleMons[battler].curHP) {
        int i;
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
        for (i = 0; i < maxBattlers; i++) {
            int chip;
            if (i == battler || battleCtx->battleMons[i].curHP == 0) {
                continue;
            }
            if (battleCtx->battleMons[i].type1 == TYPE_GHOST
                || battleCtx->battleMons[i].type2 == TYPE_GHOST
                || battleCtx->battleMons[i].type1 == TYPE_DARK
                || battleCtx->battleMons[i].type2 == TYPE_DARK) {
                continue;
            }
            chip = BattleSystem_Divide(battleCtx->battleMons[i].maxHP, 4);
            battleCtx->battleMons[i].curHP =
                battleCtx->battleMons[i].curHP > chip
                ? battleCtx->battleMons[i].curHP - chip : 0;
            BattleMon_CopyToParty(battleSys, battleCtx, i);
        }
    }

"""
    insert_after_once(
        path, anchor, block,
        "Battler_Ability(battleCtx, battler) == ABILITY_FUNERAL_PYRE",
        "Funeral Pyre / White Noise turn-end",
    )


def patch_flame_bubble_burn(root: Path) -> None:
    path = root / "res/battle/scripts/subscripts/subscript_burn.s"
    replace_once(
        path,
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _211
    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLAME_BUBBLE, _211
""",
        "Flame Bubble self burn immunity",
    )
    replace_once(
        path,
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
""",
        """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_BUBBLE, _264
    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLAME_BUBBLE, _264
""",
        "Flame Bubble opposing burn immunity",
    )


def patch_flame_bubble_priority(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    # Extend R1's full-HP priority family.
    old = """            || (Battler_Ability(battleCtx, attacker) == ABILITY_CUTE_ANTECEDENCE
                && moveType == TYPE_FAIRY))) {
        priority++;
    }
"""
    new = """            || (Battler_Ability(battleCtx, attacker) == ABILITY_CUTE_ANTECEDENCE
                && moveType == TYPE_FAIRY)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_FLAME_BUBBLE
                && moveType == TYPE_FIRE))) {
        priority++;
    }
"""
    replace_once(path, old, new, "Flame Bubble full-HP Fire priority helper")

    anchor = """    if (battler1Priority == battler2Priority) {
"""
    block = """    if (battler1Move != MOVE_NONE
        && battler1Ability == ABILITY_FLAME_BUBBLE
        && battleCtx->battleMons[battler1].curHP
            == battleCtx->battleMons[battler1].maxHP
        && MOVE_DATA(battler1Move).type == TYPE_FIRE) {
        battler1Priority++;
    }
    if (battler2Move != MOVE_NONE
        && battler2Ability == ABILITY_FLAME_BUBBLE
        && battleCtx->battleMons[battler2].curHP
            == battleCtx->battleMons[battler2].maxHP
        && MOVE_DATA(battler2Move).type == TYPE_FIRE) {
        battler2Priority++;
    }

"""
    insert_before_once(
        path, anchor, block,
        "battler1Ability == ABILITY_FLAME_BUBBLE",
        "Flame Bubble action priority",
    )


def patch_drake_rage_recharge(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    case ABILITY_HAUNTING_FRENZY:
"""
    block = """    case ABILITY_DRAKE_OF_RAGE:
        if (battleCtx->battleMons[battleCtx->attacker].moveEffectsData.rechargeTurnNumber) {
            battleCtx->battleMons[battleCtx->attacker].moveEffectsData.rechargeTurnNumber = 0;
            battleCtx->battleMons[battleCtx->attacker].statusVolatile &=
                ~VOLATILE_CONDITION_MOVE_LOCKED;
        }
        break;

"""
    insert_before_once(
        path, anchor, block,
        "case ABILITY_DRAKE_OF_RAGE:",
        "Drake Of Rage Rampage KO hook",
    )


def update_registry(path: Path) -> None:
    rows = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    burn = (root / "res/battle/scripts/subscripts/subscript_burn.s").read_text(encoding="utf-8")
    abilities = [x.strip() for x in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    reg = set(registry.read_text(encoding="utf-8").splitlines())
    checks = {
        "blood_price": "ABILITY_BLOOD_PRICE" in lib and "MERCURY_BLOOD_PRICE" in ctl,
        "dead_power": "ABILITY_DEAD_POWER" in lib and "VOLATILE_CONDITION_CURSE" in lib,
        "energy_siphon": "MERCURY_ENERGY_SIPHON" in ctl and "shellBellDamageDealt * -1, 4" in ctl,
        "flame_bubble": lib.count("ABILITY_FLAME_BUBBLE") >= 3 and "ABILITY_FLAME_BUBBLE" in burn,
        "flaming_maw": "ABILITY_FLAMING_MAW" in lib and "Mercury_MoveIsBiting" in lib,
        "funeral_pyre": "ABILITY_FUNERAL_PYRE" in lib and "maxHP, 4" in lib,
        "last_stand": "ABILITY_LAST_STAND" in lib and "60 * missingHp" in lib,
        "low_visibility": "ABILITY_LOW_VISIBILITY" in lib and "FIELD_CONDITION_DEEP_FOG" in lib,
        "molten_blades": "ABILITY_MOLTEN_BLADES" in lib and "Mercury_MoveIsSlicing" in lib,
        "mosh_pit": "ABILITY_MOSH_PIT" in lib and "movePower = movePower * 150 / 100" in lib,
        "permanence": "Mercury_PermanenceBlocksHealing" in script,
        "phantom_pain": lib.count("ABILITY_PHANTOM_PAIN") >= 2,
        "rage_point": lib.count("ABILITY_RAGE_POINT") >= 2,
        "sepia_lens": "ABILITY_SEPIA_LENS" in lib and "ABILITY_TINTED_LENS" in lib,
        "smoldering_wood": lib.count("ABILITY_SMOLDERING_WOOD") >= 2,
        "terminal_velocity": "ABILITY_TERMINAL_VELOCITY" in lib and "* 20 / 100" in lib,
        "vengeful_spirit": lib.count("ABILITY_VENGEFUL_SPIRIT") >= 2,
        "vitality_strike": "MERCURY_VITALITY_STRIKE" in ctl and "Mercury_R5MoveIsPunching" in ctl,
        "white_noise": lib.count("ABILITY_WHITE_NOISE") >= 2,
        "drake_of_rage": lib.count("ABILITY_DRAKE_OF_RAGE") >= 2,
        "registry_updated": all(t in reg for t in TOKENS),
        "ids_stable": all(len(abilities) > aid and abilities[aid] == tok for tok, aid in IMPLEMENTED.values()),
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10r5-historical-fast-pass.json"))
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_damage(root)
    patch_phantom_pain(root)
    patch_contact_reactions(root)
    patch_after_move_family(root)
    patch_low_visibility(root)
    patch_permanence(root)
    patch_turn_end_family(root)
    patch_flame_bubble_burn(root)
    patch_flame_bubble_priority(root)
    patch_drake_rage_recharge(root)
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
