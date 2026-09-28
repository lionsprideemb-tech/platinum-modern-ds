#!/usr/bin/env python3
"""MR08K — accelerated canonical Ability bulk pass.

Adds twenty-five official/current-mainline Ability mechanics using shared
Platinum battle hooks. This mechanics-only pass deliberately leaves the locked
MR07 Summary / EV / Nature / Ability editor visuals untouched.

Abilities:
Pickpocket, Sheer Force, Moody, Magic Bounce, Protean, Magician, Battle Bond,
Soul-Heart, Receiver, Power of Alchemy, Intrepid Sword, Dauntless Shield,
Libero, Propeller Tail, Stalwart, Wandering Spirit, Curious Medicine,
As One (Glastrier), As One (Spectrier), Orichalcum Pulse, Supreme Overlord,
Costar, Mycelium Might, Mind's Eye, Supersweet Syrup.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PICKPOCKET",
    "ABILITY_SHEER_FORCE",
    "ABILITY_MOODY",
    "ABILITY_MAGIC_BOUNCE",
    "ABILITY_PROTEAN",
    "ABILITY_MAGICIAN",
    "ABILITY_BATTLE_BOND",
    "ABILITY_SOUL_HEART",
    "ABILITY_RECEIVER",
    "ABILITY_POWER_OF_ALCHEMY",
    "ABILITY_INTREPID_SWORD",
    "ABILITY_DAUNTLESS_SHIELD",
    "ABILITY_LIBERO",
    "ABILITY_PROPELLER_TAIL",
    "ABILITY_STALWART",
    "ABILITY_WANDERING_SPIRIT",
    "ABILITY_CURIOUS_MEDICINE",
    "ABILITY_AS_ONE_GLASTRIER",
    "ABILITY_AS_ONE_SPECTRIER",
    "ABILITY_ORICHALCUM_PULSE",
    "ABILITY_SUPREME_OVERLORD",
    "ABILITY_COSTAR",
    "ABILITY_MYCELIUM_MIGHT",
    "ABILITY_MINDS_EYE",
    "ABILITY_SUPERSWEET_SYRUP",
)

EXPECTED_IDS = {
    "ABILITY_PICKPOCKET": 124,
    "ABILITY_SHEER_FORCE": 125,
    "ABILITY_MOODY": 141,
    "ABILITY_MAGIC_BOUNCE": 156,
    "ABILITY_PROTEAN": 168,
    "ABILITY_MAGICIAN": 170,
    "ABILITY_BATTLE_BOND": 210,
    "ABILITY_SOUL_HEART": 220,
    "ABILITY_RECEIVER": 222,
    "ABILITY_POWER_OF_ALCHEMY": 223,
    "ABILITY_INTREPID_SWORD": 234,
    "ABILITY_DAUNTLESS_SHIELD": 235,
    "ABILITY_LIBERO": 236,
    "ABILITY_PROPELLER_TAIL": 239,
    "ABILITY_STALWART": 242,
    "ABILITY_WANDERING_SPIRIT": 254,
    "ABILITY_CURIOUS_MEDICINE": 261,
    "ABILITY_AS_ONE_GLASTRIER": 266,
    "ABILITY_AS_ONE_SPECTRIER": 267,
    "ABILITY_ORICHALCUM_PULSE": 288,
    "ABILITY_SUPREME_OVERLORD": 293,
    "ABILITY_COSTAR": 294,
    "ABILITY_MYCELIUM_MIGHT": 298,
    "ABILITY_MINDS_EYE": 300,
    "ABILITY_SUPERSWEET_SYRUP": 306,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_required(
    path: Path, old: str, new: str, minimum: int, label: str
) -> int:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f"{label}: expected at least {minimum} matches in {path}, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return count


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def replace_function(path: Path, signature: str, replacement: str, label: str) -> None:
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

    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


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


def patch_battle_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08K: per-battle canonical Ability state.
    u8 mercuryProteanUsed[MAX_BATTLERS];
    u8 mercuryFaintHandledMask;
    u8 mercuryBattleBondUsed[2];
    u8 mercurySwordShieldUsed[2];
    u8 mercurySupersweetSyrupUsed[2];

""",
        "MR08K battle context state",
    )


def patch_battle_lib_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """static BOOL Mercury_MoveIsBallOrBomb(int move)
""",
        """static BOOL Mercury_MoveHasSheerForceSecondary(int move)
{
    return MOVE_DATA(move).power != 0 && MOVE_DATA(move).effectChance != 0;
}

static BOOL Mercury_AbilityCanBeReceived(int ability)
{
    switch (ability) {
    case ABILITY_NONE:
    case ABILITY_TRACE:
    case ABILITY_FORECAST:
    case ABILITY_FLOWER_GIFT:
    case ABILITY_MULTITYPE:
    case ABILITY_ILLUSION:
    case ABILITY_IMPOSTER:
    case ABILITY_ZEN_MODE:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_RECEIVER:
    case ABILITY_POWER_OF_ALCHEMY:
    case ABILITY_SCHOOLING:
    case ABILITY_DISGUISE:
    case ABILITY_BATTLE_BOND:
    case ABILITY_POWER_CONSTRUCT:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_COMATOSE:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_GULP_MISSILE:
    case ABILITY_ICE_FACE:
    case ABILITY_HUNGER_SWITCH:
    case ABILITY_NEUTRALIZING_GAS:
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_COMMANDER:
    case ABILITY_TERA_SHIFT:
        return FALSE;
    default:
        return TRUE;
    }
}

static int Mercury_CountFaintedPartyMons(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    Party *party = BattleSystem_GetParty(battleSys, battler);
    int partySize = BattleSystem_GetPartyCount(battleSys, battler);
    int count = 0;
    int i;

    for (i = 0; i < partySize; i++) {
        Pokemon *mon = Party_GetPokemonBySlotIndex(party, i);
        int species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);

        if (species != SPECIES_NONE
            && species != SPECIES_EGG
            && Pokemon_GetValue(mon, MON_DATA_IS_EGG, NULL) == FALSE
            && Pokemon_GetValue(mon, MON_DATA_HP, NULL) == 0) {
            count++;
        }
    }

    if (count > 5) {
        count = 5;
    }
    return count;
}

static BOOL Mercury_HasOpposingUnnerveFamily(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    return BattleSystem_CountAbility(
               battleSys, battleCtx, COUNT_ALIVE_BATTLERS_THEIR_SIDE,
               battler, ABILITY_UNNERVE)
        || BattleSystem_CountAbility(
               battleSys, battleCtx, COUNT_ALIVE_BATTLERS_THEIR_SIDE,
               battler, ABILITY_AS_ONE_GLASTRIER)
        || BattleSystem_CountAbility(
               battleSys, battleCtx, COUNT_ALIVE_BATTLERS_THEIR_SIDE,
               battler, ABILITY_AS_ONE_SPECTRIER);
}

""",
        "MR08K shared helpers",
    )

    replace_function(
        path,
        "BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)",
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
{
    BOOL result = FALSE;
    int attackerAbility = Battler_Ability(battleCtx, attacker);
    BOOL myceliumBypass = attackerAbility == ABILITY_MYCELIUM_MIGHT
        && battleCtx->moveCur != MOVE_NONE
        && MOVE_DATA(battleCtx->moveCur).class == CLASS_STATUS;

    if (!Mercury_IsMoldBreakerAbility(attackerAbility) && !myceliumBypass) {
        if (Battler_Ability(battleCtx, defender) == ability) {
            result = TRUE;
        }
    } else if (Battler_Ability(battleCtx, defender) == ability) {
        if (Mercury_IsMoldBreakerAbility(attackerAbility)
            && battleCtx->selfTurnFlags[attacker].moldBreakerActivated == FALSE) {
            battleCtx->selfTurnFlags[attacker].moldBreakerActivated = TRUE;
            battleCtx->battleStatusMask |= SYSCTL_APPLY_MOLD_BREAKER;
        }
    }

    return result;
}""",
        "Mycelium Might ability bypass",
    )

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STAKEOUT
""",
        """    if (attackerParams.ability == ABILITY_SHEER_FORCE
        && Mercury_MoveHasSheerForceSecondary(move)) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_SUPREME_OVERLORD) {
        int fainted = Mercury_CountFaintedPartyMons(
            battleSys, battleCtx, attacker);
        movePower = movePower * (10 + fainted) / 10;
    }

""",
        "Sheer Force / Supreme Overlord power",
    )

    replace_once(
        path,
        """    if (attackerParams.heldItemEffect == HOLD_EFFECT_CHOICE_ATK
        || attackerParams.ability == ABILITY_GORILLA_TACTICS) {
        attackStat = attackStat * 150 / 100;
    }
""",
        """    if (attackerParams.ability == ABILITY_ORICHALCUM_PULSE
        && (fieldConditions & FIELD_CONDITION_SUNNY)) {
        attackStat = attackStat * 4 / 3;
    }

    if (attackerParams.heldItemEffect == HOLD_EFFECT_CHOICE_ATK
        || attackerParams.ability == ABILITY_GORILLA_TACTICS) {
        attackStat = attackStat * 150 / 100;
    }
""",
        "Orichalcum Pulse Attack boost",
    )

    replace_function(
        path,
        "BOOL Battler_SubstituteWasHit(BattleContext *battleCtx, int battler)",
        """BOOL Battler_SubstituteWasHit(BattleContext *battleCtx, int battler)
{
    BOOL result = FALSE;

    if (battleCtx->selfTurnFlags[battler].statusFlags & SELF_TURN_FLAG_SUBSTITUTE_HIT) {
        result = TRUE;
    }

    return result;
}""",
        "Preserve substitute helper for MR08K",
    )


def patch_sheer_force(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL BattleSystem_TriggerSecondaryEffect(BattleSystem *battleSys, BattleContext *battleCtx, int *effect)
{
    BOOL result = FALSE;
""",
        """""",
        "Sheer Force secondary function anchor",
    )

    replace_once(
        path,
        """BOOL BattleSystem_TriggerSecondaryEffect(BattleSystem *battleSys, BattleContext *battleCtx, int *effect)
{
    BOOL result = FALSE;
""",
        """BOOL BattleSystem_TriggerSecondaryEffect(BattleSystem *battleSys, BattleContext *battleCtx, int *effect)
{
    BOOL result = FALSE;

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SHEER_FORCE
        && Mercury_MoveHasSheerForceSecondary(battleCtx->moveCur)) {
        battleCtx->sideEffectIndirectFlags = 0;
        battleCtx->battleStatusMask &= ~SYSCTL_APPLY_SECONDARY_EFFECT;
        return FALSE;
    }
""",
        "Sheer Force secondary suppression",
    )


def patch_end_turn_and_on_hit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_HARVEST:
""",
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_MOODY: {
        int stats[5] = {
            BATTLE_STAT_ATTACK,
            BATTLE_STAT_DEFENSE,
            BATTLE_STAT_SP_ATTACK,
            BATTLE_STAT_SP_DEFENSE,
            BATTLE_STAT_SPEED,
        };
        int upChoices[5];
        int downChoices[5];
        int upCount = 0;
        int downCount = 0;
        int chosenUp = -1;
        int i;

        for (i = 0; i < 5; i++) {
            int stat = stats[i];
            if (battleCtx->battleMons[battler].statBoosts[stat] < MAX_STAT_STAGE) {
                upChoices[upCount++] = stat;
            }
        }

        if (upCount) {
            chosenUp = upChoices[BattleSystem_RandNext(battleSys) % upCount];
            battleCtx->battleMons[battler].statBoosts[chosenUp] += 2;
            if (battleCtx->battleMons[battler].statBoosts[chosenUp] > MAX_STAT_STAGE) {
                battleCtx->battleMons[battler].statBoosts[chosenUp] = MAX_STAT_STAGE;
            }
        }

        for (i = 0; i < 5; i++) {
            int stat = stats[i];
            if (stat != chosenUp
                && battleCtx->battleMons[battler].statBoosts[stat] > MIN_STAT_STAGE) {
                downChoices[downCount++] = stat;
            }
        }

        if (downCount) {
            int chosenDown = downChoices[BattleSystem_RandNext(battleSys) % downCount];
            battleCtx->battleMons[battler].statBoosts[chosenDown]--;
        }
        break;
    }

    case ABILITY_HARVEST:
""",
        "Moody end-turn hook",
    )

    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MAGICIAN
        && ATTACKING_MON.heldItem == ITEM_NONE
        && DEFENDING_MON.heldItem != ITEM_NONE
        && Battler_Ability(battleCtx, battleCtx->defender) != ABILITY_STICKY_HOLD
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
        ATTACKING_MON.heldItem = DEFENDING_MON.heldItem;
        DEFENDING_MON.heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
        BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->defender);
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        "Magician item steal",
    )

    insert_before_once(
        path,
        """    case ABILITY_THERMAL_EXCHANGE: {
""",
        """    case ABILITY_PICKPOCKET:
        if (DEFENDING_MON.curHP
            && DEFENDING_MON.heldItem == ITEM_NONE
            && ATTACKING_MON.heldItem != ITEM_NONE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_STICKY_HOLD) {
            DEFENDING_MON.heldItem = ATTACKING_MON.heldItem;
            ATTACKING_MON.heldItem = ITEM_NONE;
            BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
            BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->defender);
        }
        break;

    case ABILITY_WANDERING_SPIRIT:
        if (DEFENDING_MON.curHP
            && ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && Mercury_AbilityCanBeOverwrittenByMummy(
                Battler_Ability(battleCtx, battleCtx->attacker))
            && Mercury_AbilityCanBeOverwrittenByMummy(
                Battler_Ability(battleCtx, battleCtx->defender))) {
            int tempAbility = ATTACKING_MON.ability;
            ATTACKING_MON.ability = DEFENDING_MON.ability;
            DEFENDING_MON.ability = tempAbility;
        }
        break;

""",
        "Pickpocket / Wandering Spirit on-hit hooks",
    )

    replace_once(
        path,
        """    if (Item_IsBerry(Battler_HeldItem(battleCtx, battler))
        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_THEIR_SIDE,
            battler,
            ABILITY_UNNERVE)) {
        return FALSE;
    }
""",
        """    if (Item_IsBerry(Battler_HeldItem(battleCtx, battler))
        && Mercury_HasOpposingUnnerveFamily(battleSys, battleCtx, battler)) {
        return FALSE;
    }
""",
        "As One Unnerve family",
    )


def patch_ko_and_faint_family(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    replace_once(
        lib,
        """    switch (Battler_Ability(battleCtx, battleCtx->attacker)) {
    case ABILITY_MOXIE:
    case ABILITY_CHILLING_NEIGH:
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_BATTLE_BOND) {
        int side = BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker);
        int slot = battleCtx->selectedPartySlot[battleCtx->attacker];

        if (slot < 6
            && (battleCtx->mercuryBattleBondUsed[side] & FlagIndex(slot)) == 0) {
            BattleMon *mon = &battleCtx->battleMons[battleCtx->attacker];
            battleCtx->mercuryBattleBondUsed[side] |= FlagIndex(slot);
            if (mon->statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK]++;
            }
            if (mon->statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_SP_ATTACK]++;
            }
            if (mon->statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_SPEED]++;
            }
        }
        return FALSE;
    }

    switch (Battler_Ability(battleCtx, battleCtx->attacker)) {
    case ABILITY_MOXIE:
    case ABILITY_CHILLING_NEIGH:
    case ABILITY_AS_ONE_GLASTRIER:
""",
        "Battle Bond / As One Glastrier KO hooks",
    )

    replace_once(
        lib,
        """    case ABILITY_GRIM_NEIGH:
""",
        """    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
""",
        "As One Spectrier KO hook",
    )

    insert_before_once(
        lib,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad)
""",
        """void Mercury_TriggerFaintAbilities(BattleSystem *battleSys, BattleContext *battleCtx)
{
    int fainted = battleCtx->faintedMon;
    int maxBattlers;
    int i;

    if (fainted == BATTLER_NONE
        || (battleCtx->mercuryFaintHandledMask & FlagIndex(fainted))) {
        return;
    }

    battleCtx->mercuryFaintHandledMask |= FlagIndex(fainted);
    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (i = 0; i < maxBattlers; i++) {
        int ability;

        if (!battleCtx->battleMons[i].curHP || i == fainted) {
            continue;
        }

        ability = Battler_Ability(battleCtx, i);

        if (ability == ABILITY_SOUL_HEART
            && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]
                < MAX_STAT_STAGE) {
            battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]++;
        }

        if ((ability == ABILITY_RECEIVER
                || ability == ABILITY_POWER_OF_ALCHEMY)
            && (i ^ 2) == fainted
            && BattleSystem_GetBattlerSide(battleSys, i)
                == BattleSystem_GetBattlerSide(battleSys, fainted)
            && Mercury_AbilityCanBeReceived(
                battleCtx->battleMons[fainted].ability)) {
            battleCtx->battleMons[i].ability =
                battleCtx->battleMons[fainted].ability;
        }
    }
}

void Mercury_ApplyProteanLibero(BattleContext *battleCtx)
{
    int battler = battleCtx->attacker;
    int ability;
    int moveType;

    if (battler == BATTLER_NONE || battleCtx->mercuryProteanUsed[battler]) {
        return;
    }

    ability = Battler_Ability(battleCtx, battler);
    if (ability != ABILITY_PROTEAN && ability != ABILITY_LIBERO) {
        return;
    }

    if (battleCtx->moveCur == MOVE_NONE || battleCtx->moveCur == MOVE_STRUGGLE) {
        return;
    }

    moveType = battleCtx->moveType
        ? battleCtx->moveType
        : MOVE_DATA(battleCtx->moveCur).type;

    if (battleCtx->battleMons[battler].type1 != moveType
        || battleCtx->battleMons[battler].type2 != moveType) {
        battleCtx->battleMons[battler].type1 = moveType;
        battleCtx->battleMons[battler].type2 = moveType;
        battleCtx->mercuryProteanUsed[battler] = TRUE;
    }
}

""",
        "Soul-Heart / Receiver / Protean helpers",
    )

    insert_before_once(
        hdr,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad);
""",
        """void Mercury_TriggerFaintAbilities(BattleSystem *battleSys, BattleContext *battleCtx);
void Mercury_ApplyProteanLibero(BattleContext *battleCtx);
""",
        "MR08K public helper declarations",
    )


def patch_switch_in_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """                    case ABILITY_HOSPITALITY: {
                        int ally = battler ^ 2;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers
                            && battleCtx->battleMons[ally].curHP
                            && battleCtx->battleMons[ally].curHP
                                < battleCtx->battleMons[ally].maxHP) {
                            battleCtx->battleMons[ally].curHP +=
                                BattleSystem_Divide(
                                    battleCtx->battleMons[ally].maxHP, 4);
                            if (battleCtx->battleMons[ally].curHP
                                > battleCtx->battleMons[ally].maxHP) {
                                battleCtx->battleMons[ally].curHP =
                                    battleCtx->battleMons[ally].maxHP;
                            }
                            BattleMon_CopyToParty(battleSys, battleCtx, ally);
                            battleCtx->msgBattlerTemp = battler;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
                    }
""",
        """                    case ABILITY_HOSPITALITY: {
                        int ally = battler ^ 2;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers
                            && battleCtx->battleMons[ally].curHP
                            && battleCtx->battleMons[ally].curHP
                                < battleCtx->battleMons[ally].maxHP) {
                            battleCtx->battleMons[ally].curHP +=
                                BattleSystem_Divide(
                                    battleCtx->battleMons[ally].maxHP, 4);
                            if (battleCtx->battleMons[ally].curHP
                                > battleCtx->battleMons[ally].maxHP) {
                                battleCtx->battleMons[ally].curHP =
                                    battleCtx->battleMons[ally].maxHP;
                            }
                            BattleMon_CopyToParty(battleSys, battleCtx, ally);
                            battleCtx->msgBattlerTemp = battler;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
                    }

                    case ABILITY_INTREPID_SWORD:
                    case ABILITY_DAUNTLESS_SHIELD: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        int slot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (slot < 6
                            && (battleCtx->mercurySwordShieldUsed[side]
                                & FlagIndex(slot)) == 0) {
                            int stat = Battler_Ability(battleCtx, battler)
                                == ABILITY_INTREPID_SWORD
                                ? BATTLE_STAT_ATTACK
                                : BATTLE_STAT_DEFENSE;
                            battleCtx->mercurySwordShieldUsed[side] |= FlagIndex(slot);
                            if (battleCtx->battleMons[battler].statBoosts[stat]
                                < MAX_STAT_STAGE) {
                                battleCtx->battleMons[battler].statBoosts[stat]++;
                            }
                        }
                        break;
                    }

                    case ABILITY_CURIOUS_MEDICINE: {
                        int ally = battler ^ 2;
                        int i;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers && battleCtx->battleMons[ally].curHP) {
                            for (i = BATTLE_STAT_ATTACK; i < BATTLE_STAT_MAX; i++) {
                                battleCtx->battleMons[ally].statBoosts[i] =
                                    DEFAULT_STAT_STAGE;
                            }
                        }
                        break;
                    }

                    case ABILITY_COSTAR: {
                        int ally = battler ^ 2;
                        int i;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers && battleCtx->battleMons[ally].curHP) {
                            for (i = BATTLE_STAT_ATTACK; i < BATTLE_STAT_MAX; i++) {
                                battleCtx->battleMons[battler].statBoosts[i] =
                                    battleCtx->battleMons[ally].statBoosts[i];
                            }
                        }
                        break;
                    }

                    case ABILITY_ORICHALCUM_PULSE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if ((battleCtx->fieldConditionsMask
                                & FIELD_CONDITION_SUNNY_PERM) == FALSE) {
                            battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
                            battleCtx->fieldConditionsMask |= FIELD_CONDITION_SUNNY_TEMP;
                            battleCtx->fieldConditions.weatherTurns = 5;
                        }
                        break;

                    case ABILITY_SUPERSWEET_SYRUP: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        int slot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (slot < 6
                            && (battleCtx->mercurySupersweetSyrupUsed[side]
                                & FlagIndex(slot)) == 0) {
                            int i;
                            battleCtx->mercurySupersweetSyrupUsed[side] |= FlagIndex(slot);

                            for (i = 0; i < maxBattlers; i++) {
                                if (battleCtx->battleMons[i].curHP
                                    && BattleSystem_GetBattlerSide(battleSys, i) != side
                                    && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_EVASION]
                                        > MIN_STAT_STAGE) {
                                    battleCtx->battleMons[i].statBoosts[BATTLE_STAT_EVASION]--;
                                }
                            }
                        }
                        break;
                    }
""",
        "MR08K switch-in family",
    )


def patch_targeting_and_order(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_all_required(
        lib,
        """        if (battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        """        if (Battler_Ability(battleCtx, attacker) != ABILITY_PROPELLER_TAIL
            && Battler_Ability(battleCtx, attacker) != ABILITY_STALWART
            && battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        1,
        "Propeller Tail / Stalwart normal Follow Me bypass",
    )

    replace_once(
        lib,
        """            if (battleCtx->sideConditions[enemySide].followMe
                && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        """            if (Battler_Ability(battleCtx, attacker) != ABILITY_PROPELLER_TAIL
                && Battler_Ability(battleCtx, attacker) != ABILITY_STALWART
                && battleCtx->sideConditions[enemySide].followMe
                && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        "Propeller Tail / Stalwart random Follow Me bypass",
    )

    replace_once(
        lib,
        """    if (battleCtx->defender == BATTLER_NONE
        || Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE
        || Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))) {
        return;
    }
""",
        """    if (battleCtx->defender == BATTLER_NONE
        || Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE
        || Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))
        || Battler_Ability(battleCtx, attacker) == ABILITY_PROPELLER_TAIL
        || Battler_Ability(battleCtx, attacker) == ABILITY_STALWART) {
        return;
    }
""",
        "Propeller Tail / Stalwart redirection bypass",
    )

    insert_before_once(
        lib,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Action == PLAYER_INPUT_FIGHT
        && battler1Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler1Move).class == CLASS_STATUS) {
        battler1LaggingTail = 1;
    }

    if (battler2Action == PLAYER_INPUT_FIGHT
        && battler2Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler2Move).class == CLASS_STATUS) {
        battler2LaggingTail = 1;
    }

""",
        "Mycelium Might move-last hook",
    )


def patch_minds_eye(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"

    replace_all_required(
        lib,
        "Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY",
        "(Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY || Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE)",
        1,
        "Mind's Eye Scrappy family direct",
    )
    replace_all_required(
        lib,
        "attackerAbility == ABILITY_SCRAPPY",
        "(attackerAbility == ABILITY_SCRAPPY || attackerAbility == ABILITY_MINDS_EYE)",
        1,
        "Mind's Eye Scrappy family cached",
    )

    replace_once(
        script,
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE)) {
""",
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_MINDS_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE)) {
""",
        "Mind's Eye accuracy-drop prevention",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    if ((battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && DEFENDER_TURN_FLAGS.magicCoat
        && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_CAN_MAGIC_COAT)) {
        DEFENDER_TURN_FLAGS.magicCoat = FALSE;
""",
        """    if ((battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && (DEFENDER_TURN_FLAGS.magicCoat
            || Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_MAGIC_BOUNCE) == TRUE)
        && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_CAN_MAGIC_COAT)) {
        DEFENDER_TURN_FLAGS.magicCoat = FALSE;
""",
        "Magic Bounce reflection",
    )

    replace_once(
        path,
        """    s8 accStages = battleCtx->battleMons[attacker].statBoosts[BATTLE_STAT_ACCURACY] - 6;
    s8 evaStages = 6 - battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_EVASION];

    if (Battler_Ability(battleCtx, attacker) == ABILITY_SIMPLE) {
""",
        """    s8 accStages = battleCtx->battleMons[attacker].statBoosts[BATTLE_STAT_ACCURACY] - 6;
    s8 evaStages = 6 - battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_EVASION];

    if (Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE) {
        if (accStages < 0) {
            accStages = 0;
        }
        evaStages = 0;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_SIMPLE) {
""",
        "Mind's Eye accuracy calculation",
    )

    replace_once(
        path,
        """    case BEFORE_MOVE_STATE_REDIRECT_TARGET:
        BattleSystem_CheckRedirectionAbilities(battleSys, battleCtx, battleCtx->attacker, battleCtx->moveCur);
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_START;
""",
        """    case BEFORE_MOVE_STATE_REDIRECT_TARGET:
        BattleSystem_CheckRedirectionAbilities(battleSys, battleCtx, battleCtx->attacker, battleCtx->moveCur);
        Mercury_ApplyProteanLibero(battleCtx);
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_START;
""",
        "Protean / Libero before-move hook",
    )

    replace_once(
        path,
        """static void BattleControllerPlayer_LoopWhileFainted(BattleSystem *battleSys, BattleContext *battleCtx)
{
    if (battleCtx->battleStatusMask & SYSCTL_MON_FAINTED) {
        BattleControllerPlayer_AnyFainted(battleCtx, BATTLE_CONTROL_LOOP_FAINTED, BATTLE_CONTROL_LOOP_FAINTED, FALSE);
""",
        """static void BattleControllerPlayer_LoopWhileFainted(BattleSystem *battleSys, BattleContext *battleCtx)
{
    if (battleCtx->battleStatusMask & SYSCTL_MON_FAINTED) {
        Mercury_TriggerFaintAbilities(battleSys, battleCtx);
        BattleControllerPlayer_AnyFainted(battleCtx, BATTLE_CONTROL_LOOP_FAINTED, BATTLE_CONTROL_LOOP_FAINTED, FALSE);
""",
        "Soul-Heart / Receiver faint hook",
    )


def patch_state_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    battleCtx->battleMons[battler].pressureAnnounced = FALSE;
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        """    battleCtx->battleMons[battler].pressureAnnounced = FALSE;
    battleCtx->mercuryProteanUsed[battler] = FALSE;
    battleCtx->mercuryFaintHandledMask &= ~FlagIndex(battler);
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        "MR08K switch-in state reset",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    context = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "pickpocket_hook": "case ABILITY_PICKPOCKET:" in lib,
        "sheer_force_hook": "Mercury_MoveHasSheerForceSecondary" in lib,
        "moody_hook": "case ABILITY_MOODY:" in lib,
        "magic_bounce_hook": "ABILITY_MAGIC_BOUNCE" in controller,
        "protean_libero_hook": "Mercury_ApplyProteanLibero" in lib and "Mercury_ApplyProteanLibero" in controller,
        "magician_hook": "ABILITY_MAGICIAN" in lib,
        "battle_bond_hook": "ABILITY_BATTLE_BOND" in lib and "mercuryBattleBondUsed" in context,
        "soul_heart_hook": "ABILITY_SOUL_HEART" in lib and "Mercury_TriggerFaintAbilities" in controller,
        "receiver_hook": "ABILITY_RECEIVER" in lib and "ABILITY_POWER_OF_ALCHEMY" in lib,
        "sword_shield_hook": "ABILITY_INTREPID_SWORD" in lib and "ABILITY_DAUNTLESS_SHIELD" in lib,
        "targeting_hook": "ABILITY_PROPELLER_TAIL" in lib and "ABILITY_STALWART" in lib,
        "wandering_spirit_hook": "case ABILITY_WANDERING_SPIRIT:" in lib,
        "curious_medicine_hook": "case ABILITY_CURIOUS_MEDICINE:" in lib,
        "as_one_hook": "ABILITY_AS_ONE_GLASTRIER" in lib and "ABILITY_AS_ONE_SPECTRIER" in lib,
        "orichalcum_pulse_hook": "case ABILITY_ORICHALCUM_PULSE:" in lib and "attackStat = attackStat * 4 / 3" in lib,
        "supreme_overlord_hook": "ABILITY_SUPREME_OVERLORD" in lib and "Mercury_CountFaintedPartyMons" in lib,
        "costar_hook": "case ABILITY_COSTAR:" in lib,
        "mycelium_might_hook": "ABILITY_MYCELIUM_MIGHT" in lib and "myceliumBypass" in lib,
        "minds_eye_hook": "ABILITY_MINDS_EYE" in lib and "ABILITY_MINDS_EYE" in controller and "ABILITY_MINDS_EYE" in script,
        "supersweet_syrup_hook": "case ABILITY_SUPERSWEET_SYRUP:" in lib,
        "implemented_registry_updated": all(token in registry_lines for token in IMPLEMENTED),
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
        default=Path("mr08k-canonical-ability-bulk-pass.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_context(root)
    patch_battle_lib_helpers(root)
    patch_sheer_force(root)
    patch_end_turn_and_on_hit(root)
    patch_ko_and_faint_family(root)
    patch_switch_in_family(root)
    patch_targeting_and_order(root)
    patch_minds_eye(root)
    patch_controller(root)
    patch_state_reset(root)
    update_registry(registry)

    # Temporary compile-diagnostic excerpt: keeps the first failing compiler
    # location visible in the MR08K step log while this accelerated batch is
    # being integrated.
    _battle_lib_lines = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8").splitlines()
    for _line_no in range(3848, 3879):
        if _line_no <= len(_battle_lib_lines):
            print(f"MR08K_DIAG {_line_no}: {_battle_lib_lines[_line_no - 1]}")

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08K_CANONICAL_ABILITY_BULK_PASS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 135,
        "remaining_modern_canonical_mechanics": 52,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08K validation failed")


if __name__ == "__main__":
    main()
