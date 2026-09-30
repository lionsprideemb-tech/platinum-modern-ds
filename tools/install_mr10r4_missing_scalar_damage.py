#!/usr/bin/env python3
"""MR10R4 — historical Ability fast pass.

Restores twenty identities from the actual historical-runtime queue in one
shared-hook pass.  This batch deliberately reuses the canonical Gen 1-9
Ability machinery and MR10's already-installed reaction/switch-in hooks rather
than building twenty isolated systems.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Battle Aura": ("ABILITY_BATTLE_AURA", 353),
    "Blind Rage": ("ABILITY_BLIND_RAGE", 358),
    "Contempt": ("ABILITY_CONTEMPT", 378),
    "Elemental Vortex": ("ABILITY_ELEMENTAL_VORTEX", 406),
    "Guilt Trip": ("ABILITY_GUILT_TRIP", 444),
    "Impulse": ("ABILITY_IMPULSE", 464),
    "Mind Crunch": ("ABILITY_MIND_CRUSH", 496),
    "Nika": ("ABILITY_NIKA", 510),
    "Noise Cancel": ("ABILITY_NOISE_CANCEL", 511),
    "Pattern Change": ("ABILITY_PATTERN_CHANGE", 519),
    "Petrify": ("ABILITY_PETRIFY", 523),
    "Reservoir": ("ABILITY_RESERVOIR", 550),
    "Sand Guard": ("ABILITY_SAND_GUARD", 560),
    "Stun Shock": ("ABILITY_STUN_SHOCK", 586),
    "Sugar Rush": ("ABILITY_SUGAR_RUSH", 588),
    "Super Hot Goo": ("ABILITY_SUPER_HOT_GOO", 589),
    "Tipping Point": ("ABILITY_TIPPING_POINT", 601),
    "VenoblazePincers": ("ABILITY_VENOBLAZE_PINCERS", 609),
    "Watch Your Step": ("ABILITY_WATCH_YOUR_STEP", 615),
    "Catastrophe": ("ABILITY_WEATHER_DOUBLE_BOOST", 618),
}
TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_required(
    path: Path,
    old: str,
    new: str,
    minimum: int,
    label: str,
) -> int:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        return 0
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f"{label}: expected at least {minimum} matches, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return count


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
            row
            for row in rows
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


def patch_battle_aura(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    helper = """static int Mercury_BattleAuraCritBoost(BattleContext *battleCtx)
{
    int i;

    for (i = 0; i < MAX_BATTLERS; i++) {
        if (battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ABILITY_BATTLE_AURA) {
            return 2;
        }
    }

    return 0;
}

"""
    insert_before_once(
        path,
        """static const u8 sCriticalStageRates[] = {
""",
        helper,
        "Mercury_BattleAuraCritBoost",
        "Battle Aura crit helper",
    )

    old = """        + criticalStage
        + (attackerAbility == ABILITY_SUPER_LUCK)
"""
    new = """        + criticalStage
        + Mercury_BattleAuraCritBoost(battleCtx)
        + (attackerAbility == ABILITY_SUPER_LUCK)
"""
    replace_once(path, old, new, "Battle Aura +2 critical stage")


def patch_blind_rage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (!Mercury_IsMoldBreakerAbility(attackerAbility) && !myceliumBypass) {
""",
        """    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
        && attackerAbility != ABILITY_BLIND_RAGE
        && !myceliumBypass) {
""",
        "Blind Rage Mold Breaker bypass",
    )
    replace_once(
        path,
        """        if (Mercury_IsMoldBreakerAbility(attackerAbility)
            && battleCtx->selfTurnFlags[attacker].moldBreakerActivated == FALSE) {
""",
        """        if ((Mercury_IsMoldBreakerAbility(attackerAbility)
                || attackerAbility == ABILITY_BLIND_RAGE)
            && battleCtx->selfTurnFlags[attacker].moldBreakerActivated == FALSE) {
""",
        "Blind Rage Mold Breaker announcement path",
    )

    text = path.read_text(encoding="utf-8")
    direct_old = "Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY"
    direct_new = (
        "(Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY "
        "|| Battler_Ability(battleCtx, attacker) == ABILITY_BLIND_RAGE)"
    )
    if direct_new not in text:
        if direct_old not in text:
            raise SystemExit("Blind Rage Scrappy direct path not found")
        text = text.replace(direct_old, direct_new)

    cached_old = "attackerAbility == ABILITY_SCRAPPY"
    cached_new = (
        "(attackerAbility == ABILITY_SCRAPPY "
        "|| attackerAbility == ABILITY_BLIND_RAGE)"
    )
    if cached_new not in text:
        if cached_old not in text:
            raise SystemExit("Blind Rage Scrappy cached path not found")
        text = text.replace(cached_old, cached_new)

    path.write_text(text, encoding="utf-8")


def patch_contempt(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"

    replace_once(
        lib,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_UNAWARE) == TRUE) {
        attackStage = 0;
        spAttackStage = 0;
    }

    if (attackerParams.ability == ABILITY_UNAWARE) {
        defenseStage = 0;
        spDefenseStage = 0;
    }
""",
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_UNAWARE) == TRUE
        || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_CONTEMPT) == TRUE) {
        attackStage = 0;
        spAttackStage = 0;
    }

    if (attackerParams.ability == ABILITY_UNAWARE
        || attackerParams.ability == ABILITY_CONTEMPT) {
        defenseStage = 0;
        spDefenseStage = 0;
    }
""",
        "Contempt Unaware family",
    )

    old = """            if (Battler_Ability(
                    battleCtx, battleCtx->sideEffectMon) == ABILITY_DEFIANT
                && mon->statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
"""
    new = """            if ((Battler_Ability(
                    battleCtx, battleCtx->sideEffectMon) == ABILITY_DEFIANT
                    || Battler_Ability(
                        battleCtx, battleCtx->sideEffectMon) == ABILITY_CONTEMPT)
                && mon->statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
"""
    replace_once(script, old, new, "Contempt Defiant family")


def patch_elemental_vortex_and_reservoir(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WATER_ABSORB) == TRUE
        && moveType == TYPE_WATER
""",
        """    if ((Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WATER_ABSORB) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ELEMENTAL_VORTEX) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_RESERVOIR) == TRUE)
        && moveType == TYPE_WATER
""",
        "Elemental Vortex/Reservoir Water Absorb",
    )
    replace_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLASH_FIRE) == TRUE
        && moveType == TYPE_FIRE
""",
        """    if ((Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLASH_FIRE) == TRUE
            || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_ELEMENTAL_VORTEX) == TRUE)
        && moveType == TYPE_FIRE
""",
        "Elemental Vortex Flash Fire",
    )

    old = """        && BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS_EXCEPT_ME, attacker, ABILITY_STORM_DRAIN)) {
"""
    new = """        && (BattleSystem_CountAbility(
                battleSys, battleCtx, COUNT_ALIVE_BATTLERS_EXCEPT_ME,
                attacker, ABILITY_STORM_DRAIN)
            || BattleSystem_CountAbility(
                battleSys, battleCtx, COUNT_ALIVE_BATTLERS_EXCEPT_ME,
                attacker, ABILITY_RESERVOIR))) {
"""
    replace_once(path, old, new, "Reservoir Storm Drain count")

    old = """            if (Battler_Ability(battleCtx, battler) == ABILITY_STORM_DRAIN
                && battleCtx->battleMons[battler].curHP
"""
    new = """            if ((Battler_Ability(battleCtx, battler) == ABILITY_STORM_DRAIN
                    || Battler_Ability(battleCtx, battler) == ABILITY_RESERVOIR)
                && battleCtx->battleMons[battler].curHP
"""
    replace_once(path, old, new, "Reservoir Storm Drain holder")


def patch_damage_stat_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """    attackStage += DEFAULT_STAT_STAGE;
    defenseStage += DEFAULT_STAT_STAGE;
    spAttackStage += DEFAULT_STAT_STAGE;
    spDefenseStage += DEFAULT_STAT_STAGE;

"""
    insertion = """    if (attackerParams.ability == ABILITY_IMPULSE
        && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) == FALSE) {
        attackStat = BattleMon_Get(battleCtx, attacker, BATTLEMON_SPEED, NULL);
        spAttackStat = attackStat;
        attackStage =
            BattleMon_Get(battleCtx, attacker, BATTLEMON_SPEED_STAGE, NULL)
            - DEFAULT_STAT_STAGE;
        spAttackStage = attackStage;
    }

    if (attackerParams.ability == ABILITY_MIND_CRUSH
        && Mercury_MoveIsBiting(move)) {
        attackStat = spAttackStat;
        attackStage = spAttackStage;
        movePower = movePower * 130 / 100;
    }

    if (attackerParams.ability == ABILITY_VENOBLAZE_PINCERS
        && moveClass == CLASS_PHYSICAL && movePower) {
        movePower = movePower * 120 / 100;
    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "attackerParams.ability == ABILITY_IMPULSE",
        "Impulse/Mind Crunch/Venoblaze damage family",
    )

    old = """        if (sPunchingMoves[i] == move && attackerParams.ability == ABILITY_IRON_FIST) {
"""
    new = """        if (sPunchingMoves[i] == move
            && (attackerParams.ability == ABILITY_IRON_FIST
                || attackerParams.ability == ABILITY_NIKA)) {
"""
    replace_once(path, old, new, "Nika Iron Fist family")


def patch_nika_catastrophe_weather(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """            case TYPE_FIRE:
                damage /= 2;
                break;
""",
        """            case TYPE_FIRE:
                if (attackerParams.ability == ABILITY_WEATHER_DOUBLE_BOOST) {
                    damage = damage * 15 / 10;
                } else {
                    damage /= 2;
                }
                break;
""",
        "Catastrophe rain Fire boost",
    )

    replace_once(
        path,
        """            case TYPE_WATER:
                damage /= 2;
                break;
""",
        """            case TYPE_WATER:
                if (attackerParams.ability == ABILITY_WEATHER_DOUBLE_BOOST) {
                    damage = damage * 15 / 10;
                } else if (attackerParams.ability != ABILITY_NIKA) {
                    damage /= 2;
                }
                break;
""",
        "Catastrophe/Nika sunny Water behavior",
    )


def patch_noise_cancel(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOUNDPROOF) == TRUE) {
"""
    insertion = """    if (Mercury_MoveIsSound(battleCtx->moveCur)) {
        int ally = defender ^ 2;

        if (Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_NOISE_CANCEL) == TRUE
            || (ally < MAX_BATTLERS
                && battleCtx->battleMons[ally].curHP
                && Battler_IgnorableAbility(
                    battleCtx, attacker, ally, ABILITY_NOISE_CANCEL) == TRUE)) {
            subscript = subscript_blocked_by_soundproof;
        }
    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "ABILITY_NOISE_CANCEL",
        "Noise Cancel party sound immunity",
    )


def patch_pattern_change(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (ability != ABILITY_PROTEAN && ability != ABILITY_LIBERO) {
        return;
    }
""",
        """    if (ability != ABILITY_PROTEAN
        && ability != ABILITY_LIBERO
        && ability != ABILITY_PATTERN_CHANGE) {
        return;
    }
""",
        "Pattern Change Protean family",
    )

    replace_once(
        path,
        """    case ABILITY_SHED_SKIN:
        if ((battleCtx->battleMons[battler].status & MON_CONDITION_ANY)
""",
        """    case ABILITY_SHED_SKIN:
    case ABILITY_PATTERN_CHANGE:
        if ((battleCtx->battleMons[battler].status & MON_CONDITION_ANY)
""",
        "Pattern Change Shed Skin family",
    )


def patch_sand_guard(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """    int partner = defender ^ 2;

"""
    insertion = """    if (WEATHER_IS_SAND
        && (Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_SAND_GUARD)
            || (partner < MAX_BATTLERS
                && battleCtx->battleMons[partner].curHP
                && Battler_IgnorableAbility(
                    battleCtx, attacker, partner, ABILITY_SAND_GUARD)))) {
        return TRUE;
    }

"""
    insert_after_once(
        path,
        anchor,
        insertion,
        "ABILITY_SAND_GUARD",
        "Sand Guard priority block",
    )

    anchor = """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
    insertion = """    if ((fieldConditions & FIELD_CONDITION_SANDSTORM)
        && moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_SAND_GUARD) == TRUE) {
        damage /= 2;
    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "defender, ABILITY_SAND_GUARD) == TRUE",
        "Sand Guard special damage reduction",
    )


def patch_sugar_rush(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (battler1Ability == ABILITY_UNBURDEN
        && battleCtx->battleMons[battler1].moveEffectsData.canUnburden
""",
        """    if ((battler1Ability == ABILITY_UNBURDEN
            || battler1Ability == ABILITY_SUGAR_RUSH)
        && battleCtx->battleMons[battler1].moveEffectsData.canUnburden
""",
        "Sugar Rush Unburden battler1",
    )
    replace_once(
        path,
        """    if (battler2Ability == ABILITY_UNBURDEN
        && battleCtx->battleMons[battler2].moveEffectsData.canUnburden
""",
        """    if ((battler2Ability == ABILITY_UNBURDEN
            || battler2Ability == ABILITY_SUGAR_RUSH)
        && battleCtx->battleMons[battler2].moveEffectsData.canUnburden
""",
        "Sugar Rush Unburden battler2",
    )

    replace_once(
        path,
        """        && Item_IsBerry(berry) == TRUE
        && Battler_Ability(battleCtx, recipient) == ABILITY_RIPEN;
""",
        """        && Item_IsBerry(berry) == TRUE
        && (Battler_Ability(battleCtx, recipient) == ABILITY_RIPEN
            || Battler_Ability(battleCtx, recipient) == ABILITY_SUGAR_RUSH);
""",
        "Sugar Rush Ripen family",
    )


def patch_attacker_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_VENOBLAZE_PINCERS
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 2) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = (BattleSystem_RandNext(battleSys) & 1)
            ? subscript_burn
            : subscript_poison;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_STUN_SHOCK
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 6) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = (BattleSystem_RandNext(battleSys) & 1)
            ? subscript_paralyze
            : subscript_poison;
        return TRUE;
    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "== ABILITY_VENOBLAZE_PINCERS",
        "Venoblaze/Stun Shock attacker reactions",
    )


def patch_defender_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    case ABILITY_THERMAL_EXCHANGE: {
"""
    insertion = """    case ABILITY_GUILT_TRIP:
        if (battleCtx->defender == battleCtx->faintedMon
            && ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int attackStage = ATTACKING_MON.statBoosts[BATTLE_STAT_ATTACK] - 2;
            int spAttackStage = ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] - 2;

            if (attackStage < MIN_STAT_STAGE) {
                attackStage = MIN_STAT_STAGE;
            }
            if (spAttackStage < MIN_STAT_STAGE) {
                spAttackStage = MIN_STAT_STAGE;
            }
            ATTACKING_MON.statBoosts[BATTLE_STAT_ATTACK] = attackStage;
            ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] = spAttackStage;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_TIPPING_POINT:
        if (DEFENDING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            if (battleCtx->criticalMul > 1) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] = MAX_STAT_STAGE;
            } else if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]
                < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]++;
            }
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_SUPER_HOT_GOO:
        if (ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
            if (ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE) {
                ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED]--;
            }
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = ATTACKING_MON.status == MON_CONDITION_NONE
                ? subscript_burn
                : subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "case ABILITY_GUILT_TRIP:",
        "Guilt Trip/Tipping Point/Super Hot Goo reactions",
    )


def patch_switch_in_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """                    case ABILITY_ELECTRIC_SURGE:
"""
    insertion = """                    case ABILITY_PETRIFY: {
                        int foe;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        for (foe = 0; foe < maxBattlers; foe++) {
                            int stat;

                            if (BattleSystem_GetBattlerSide(battleSys, foe)
                                    == BattleSystem_GetBattlerSide(battleSys, battler)
                                || battleCtx->battleMons[foe].curHP == 0) {
                                continue;
                            }

                            for (stat = BATTLE_STAT_ATTACK;
                                 stat <= BATTLE_STAT_EVASION;
                                 stat++) {
                                if (battleCtx->battleMons[foe].statBoosts[stat]
                                    > DEFAULT_STAT_STAGE) {
                                    battleCtx->battleMons[foe].statBoosts[stat]
                                        = DEFAULT_STAT_STAGE;
                                }
                            }

                            if (battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]
                                > MIN_STAT_STAGE) {
                                battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]--;
                            }
                        }

                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

                    case ABILITY_WATCH_YOUR_STEP: {
                        int foeSide =
                            BattleSystem_GetBattlerSide(battleSys, battler) ^ 1;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->sideConditionsMask[foeSide] |= SIDE_CONDITION_SPIKES;
                        if (battleCtx->sideConditions[foeSide].spikesLayers < 2) {
                            battleCtx->sideConditions[foeSide].spikesLayers = 2;
                        }
                        battleCtx->msgBattlerTemp = battler;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }

"""
    insert_before_once(
        path,
        anchor,
        insertion,
        "case ABILITY_PETRIFY:",
        "Petrify/Watch Your Step switch-in family",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "battle_aura": "Mercury_BattleAuraCritBoost" in lib,
        "blind_rage_scrappy_mold_breaker":
            "ABILITY_BLIND_RAGE" in lib
            and "attackerAbility != ABILITY_BLIND_RAGE" in lib,
        "contempt_unaware_defiant":
            "ABILITY_CONTEMPT" in lib and "ABILITY_CONTEMPT" in script,
        "elemental_vortex_dual_absorb":
            lib.count("ABILITY_ELEMENTAL_VORTEX") >= 2,
        "guilt_trip_faint_reaction": "case ABILITY_GUILT_TRIP:" in lib,
        "impulse_speed_offense":
            "attackerParams.ability == ABILITY_IMPULSE" in lib
            and "BATTLEMON_SPEED_STAGE" in lib,
        "mind_crunch_spa_biting":
            "ABILITY_MIND_CRUSH" in lib and "Mercury_MoveIsBiting(move)" in lib,
        "nika_iron_fist_sun_water":
            "ABILITY_NIKA" in lib
            and "attackerParams.ability != ABILITY_NIKA" in lib,
        "noise_cancel_party_soundproof":
            "ABILITY_NOISE_CANCEL" in lib
            and "Mercury_MoveIsSound(battleCtx->moveCur)" in lib,
        "pattern_change_protean_shed_skin":
            lib.count("ABILITY_PATTERN_CHANGE") >= 2,
        "petrify_entry":
            "case ABILITY_PETRIFY:" in lib
            and "stat <= BATTLE_STAT_EVASION" in lib,
        "reservoir_absorb_redirect":
            lib.count("ABILITY_RESERVOIR") >= 3,
        "sand_guard_dual_effect":
            lib.count("ABILITY_SAND_GUARD") >= 2,
        "stun_shock":
            "ABILITY_STUN_SHOCK" in lib and "subscript_paralyze" in lib,
        "sugar_rush_unburden_ripen":
            lib.count("ABILITY_SUGAR_RUSH") >= 3,
        "super_hot_goo":
            "case ABILITY_SUPER_HOT_GOO:" in lib
            and "subscript_burn" in lib,
        "tipping_point":
            "case ABILITY_TIPPING_POINT:" in lib
            and "criticalMul > 1" in lib,
        "venoblaze_pincers":
            "ABILITY_VENOBLAZE_PINCERS" in lib
            and "movePower = movePower * 120 / 100;" in lib,
        "watch_your_step":
            "case ABILITY_WATCH_YOUR_STEP:" in lib
            and "spikesLayers = 2;" in lib,
        "catastrophe":
            "ABILITY_WEATHER_DOUBLE_BOOST" in lib
            and lib.count("damage = damage * 15 / 10;") >= 2,
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
    ap.add_argument("--report", type=Path, default=Path("mr10r4-fast-pass.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(args.partition.resolve())
    patch_battle_aura(root)
    patch_blind_rage(root)
    patch_contempt(root)
    patch_elemental_vortex_and_reservoir(root)
    patch_damage_stat_family(root)
    patch_nika_catastrophe_weather(root)
    patch_noise_cancel(root)
    patch_pattern_change(root)
    patch_sand_guard(root)
    patch_sugar_rush(root)
    patch_attacker_reactions(root)
    patch_defender_reactions(root)
    patch_switch_in_family(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R4_HISTORICAL_FAST_PASS",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "historical_runtime_before": 100,
        "historical_runtime_after": 80,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10R4 historical fast pass failed")


if __name__ == "__main__":
    main()
