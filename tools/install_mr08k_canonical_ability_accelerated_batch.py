#!/usr/bin/env python3
"""MR08K — accelerated canonical Ability batch.

Ports twenty-five additional official/current-mainline Ability mechanics onto
Mercury's Platinum battle core.  This deliberately groups mechanics by shared
battle hooks so the remaining canonical pass can move in larger batches without
touching the locked MR07 Summary/Skills editor UI.

Implemented:
- Pickpocket
- Sheer Force
- Moody
- Infiltrator
- Protean
- Magician
- Soul-Heart
- Intrepid Sword
- Dauntless Shield
- Libero
- Propeller Tail
- Stalwart
- Wandering Spirit
- Curious Medicine
- As One (Glastrier)
- As One (Spectrier)
- Supreme Overlord
- Costar
- Mycelium Might
- Mind's Eye
- Embody Aspect (all four masks)
- Supersweet Syrup
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PICKPOCKET",
    "ABILITY_SHEER_FORCE",
    "ABILITY_MOODY",
    "ABILITY_INFILTRATOR",
    "ABILITY_PROTEAN",
    "ABILITY_MAGICIAN",
    "ABILITY_SOUL_HEART",
    "ABILITY_INTREPID_SWORD",
    "ABILITY_DAUNTLESS_SHIELD",
    "ABILITY_LIBERO",
    "ABILITY_PROPELLER_TAIL",
    "ABILITY_STALWART",
    "ABILITY_WANDERING_SPIRIT",
    "ABILITY_CURIOUS_MEDICINE",
    "ABILITY_AS_ONE_GLASTRIER",
    "ABILITY_AS_ONE_SPECTRIER",
    "ABILITY_SUPREME_OVERLORD",
    "ABILITY_COSTAR",
    "ABILITY_MYCELIUM_MIGHT",
    "ABILITY_MINDS_EYE",
    "ABILITY_EMBODY_ASPECT",
    "ABILITY_EMBODY_ASPECT_2",
    "ABILITY_EMBODY_ASPECT_3",
    "ABILITY_EMBODY_ASPECT_4",
    "ABILITY_SUPERSWEET_SYRUP",
)

EXPECTED_IDS = {
    "ABILITY_PICKPOCKET": 124,
    "ABILITY_SHEER_FORCE": 125,
    "ABILITY_MOODY": 141,
    "ABILITY_INFILTRATOR": 151,
    "ABILITY_PROTEAN": 168,
    "ABILITY_MAGICIAN": 170,
    "ABILITY_SOUL_HEART": 220,
    "ABILITY_INTREPID_SWORD": 234,
    "ABILITY_DAUNTLESS_SHIELD": 235,
    "ABILITY_LIBERO": 236,
    "ABILITY_PROPELLER_TAIL": 239,
    "ABILITY_STALWART": 242,
    "ABILITY_WANDERING_SPIRIT": 254,
    "ABILITY_CURIOUS_MEDICINE": 261,
    "ABILITY_AS_ONE_GLASTRIER": 266,
    "ABILITY_AS_ONE_SPECTRIER": 267,
    "ABILITY_SUPREME_OVERLORD": 293,
    "ABILITY_COSTAR": 294,
    "ABILITY_MYCELIUM_MIGHT": 298,
    "ABILITY_MINDS_EYE": 300,
    "ABILITY_EMBODY_ASPECT": 301,
    "ABILITY_EMBODY_ASPECT_2": 302,
    "ABILITY_EMBODY_ASPECT_3": 303,
    "ABILITY_EMBODY_ASPECT_4": 304,
    "ABILITY_SUPERSWEET_SYRUP": 306,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_min(path: Path, old: str, new: str, minimum: int, label: str) -> int:
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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


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


def patch_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u16 recycleItem[MAX_BATTLERS];
""",
        """    // Mercury modern-Ability state. These are battle-local and never
    // serialized into the save.
    u8 mercuryProteanUsed[MAX_BATTLERS];
    u8 mercuryIntrepidUsed[NUM_BATTLE_SIDES][MAX_PARTY_SIZE];
    u8 mercuryDauntlessUsed[NUM_BATTLE_SIDES][MAX_PARTY_SIZE];
    u8 mercurySweetSyrupUsed[NUM_BATTLE_SIDES][MAX_PARTY_SIZE];

""",
        "MR08K battle-context state",
    )


def patch_shared_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """u8 Battler_Ability(BattleContext *battleCtx, int battler)
""",
        """static BOOL Mercury_AbilityCanWanderingSpiritSwap(int ability)
{
    switch (ability) {
    case ABILITY_NONE:
    case ABILITY_MULTITYPE:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_SCHOOLING:
    case ABILITY_COMATOSE:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_DISGUISE:
    case ABILITY_BATTLE_BOND:
    case ABILITY_POWER_CONSTRUCT:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_ICE_FACE:
    case ABILITY_GULP_MISSILE:
    case ABILITY_HUNGER_SWITCH:
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_ZERO_TO_HERO:
    case ABILITY_COMMANDER:
    case ABILITY_TERA_SHIFT:
    case ABILITY_TERA_SHELL:
    case ABILITY_TERAFORM_ZERO:
        return FALSE;
    default:
        return TRUE;
    }
}

static int Mercury_CountFaintedAllies(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
{
    int fainted = 0;
    int partyCount = BattleSystem_GetPartyCount(battleSys, battler);

    for (int i = 0; i < partyCount; i++) {
        Pokemon *mon;

        if (i == battleCtx->selectedPartySlot[battler]) {
            continue;
        }

        mon = BattleSystem_GetPartyPokemon(battleSys, battler, i);
        if (Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL) != SPECIES_NONE
            && Pokemon_GetValue(mon, MON_DATA_HP, NULL) == 0) {
            fainted++;
        }
    }

    if (fainted > 5) {
        fainted = 5;
    }

    return fainted;
}

""",
        "MR08K shared helpers",
    )

    # Mycelium Might ignores the target's Ability for status moves, sharing the
    # same target-Ability bypass lane as Mold Breaker/Turboblaze/Teravolt.
    replace_once(
        path,
        """    if (!Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))) {
""",
        """    if (!Mercury_IsMoldBreakerAbility(Battler_Ability(battleCtx, attacker))
        && !(Battler_Ability(battleCtx, attacker) == ABILITY_MYCELIUM_MIGHT
            && CURRENT_MOVE_DATA.class == CLASS_STATUS)) {
""",
        "Mycelium Might target-Ability bypass",
    )

    # Mycelium Might status moves act in the Stall/Lagging-Tail lane while
    # preserving the move's native priority bracket.
    insert_before_once(
        path,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Move
        && battler1Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler1Move).class == CLASS_STATUS) {
        battler1LaggingTail = 1;
    }

    if (battler2Move
        && battler2Ability == ABILITY_MYCELIUM_MIGHT
        && MOVE_DATA(battler2Move).class == CLASS_STATUS) {
        battler2LaggingTail = 1;
    }

""",
        "Mycelium Might move-last ordering",
    )

    # Mind's Eye shares Scrappy's Ghost-immunity bypass.
    replace_all_min(
        path,
        "Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY",
        "(Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY || Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE)",
        1,
        "Mind's Eye live type-chart bypass",
    )
    replace_all_min(
        path,
        "attackerAbility == ABILITY_SCRAPPY",
        "(attackerAbility == ABILITY_SCRAPPY || attackerAbility == ABILITY_MINDS_EYE)",
        1,
        "Mind's Eye generic type-chart bypass",
    )


def patch_damage_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Sheer Force: current canonical 1.3x modifier on moves with an additional
    # effect. The matching secondary-effect suppression is installed below.
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
""",
        """    if (attackerParams.ability == ABILITY_SHEER_FORCE
        && MOVE_DATA(move).effectChance) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_SUPREME_OVERLORD) {
        int fallen = Mercury_CountFaintedAllies(battleSys, battleCtx, attacker);
        movePower = movePower * (10 + fallen) / 10;
    }

""",
        "Sheer Force / Supreme Overlord damage hooks",
    )

    # Infiltrator ignores Reflect and Light Screen.
    replace_once(
        path,
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        "Infiltrator Reflect bypass",
    )
    replace_once(
        path,
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        "Infiltrator Light Screen bypass",
    )

    # Sheer Force suppresses the qualifying move's additional effect.
    replace_once(
        path,
        """BOOL BattleSystem_TriggerSecondaryEffect(BattleSystem *battleSys, BattleContext *battleCtx, int *effect)
{
    BOOL result = FALSE;
    u16 effectChance;
""",
        """BOOL BattleSystem_TriggerSecondaryEffect(BattleSystem *battleSys, BattleContext *battleCtx, int *effect)
{
    BOOL result = FALSE;
    u16 effectChance;

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SHEER_FORCE
        && CURRENT_MOVE_DATA.effectChance) {
        battleCtx->sideEffectIndirectFlags = 0;
        return FALSE;
    }
""",
        "Sheer Force secondary-effect suppression",
    )


def patch_redirection(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Propeller Tail and Stalwart ignore Follow Me-style redirection.
    replace_all_min(
        path,
        """        if (battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        """        if (Battler_Ability(battleCtx, attacker) != ABILITY_PROPELLER_TAIL
            && Battler_Ability(battleCtx, attacker) != ABILITY_STALWART
            && battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        1,
        "Propeller Tail/Stalwart Follow Me bypass",
    )

    replace_once(
        path,
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
        "Propeller Tail/Stalwart Ability-redirection bypass",
    )


def patch_item_and_contact_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Pickpocket and Wandering Spirit are defender-on-contact reactions. They
    # update the battle copy and party copy together so switches preserve state.
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
            && BattleSystem_CanStealItem(
                battleSys, battleCtx, battleCtx->attacker)
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker,
                ABILITY_STICKY_HOLD) == FALSE) {
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
            && Mercury_AbilityCanWanderingSpiritSwap(
                battleCtx->battleMons[battleCtx->attacker].ability)
            && Mercury_AbilityCanWanderingSpiritSwap(
                battleCtx->battleMons[battleCtx->defender].ability)) {
            u16 tmpAbility = battleCtx->battleMons[battleCtx->attacker].ability;
            battleCtx->battleMons[battleCtx->attacker].ability =
                battleCtx->battleMons[battleCtx->defender].ability;
            battleCtx->battleMons[battleCtx->defender].ability = tmpAbility;
        }
        break;

""",
        "Pickpocket / Wandering Spirit contact hooks",
    )

    # Magician runs on the attacker after a successful damaging hit.
    insert_before_once(
        path,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MAGICIAN
        && ATTACKING_MON.heldItem == ITEM_NONE
        && DEFENDING_MON.heldItem != ITEM_NONE
        && CURRENT_MOVE_DATA.power
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_CanStealItem(
            battleSys, battleCtx, battleCtx->defender)
        && Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender,
            ABILITY_STICKY_HOLD) == FALSE) {
        ATTACKING_MON.heldItem = DEFENDING_MON.heldItem;
        DEFENDING_MON.heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->attacker);
        BattleMon_CopyToParty(battleSys, battleCtx, battleCtx->defender);
    }

""",
        "Magician attacker-on-hit hook",
    )


def patch_ko_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Soul-Heart reacts to any direct move KO processed through the shared KO
    # lane. Apply all living Soul-Heart holders before the attacker's own KO
    # Ability is resolved.
    insert_after_once(
        path,
        """BOOL BattleSystem_TriggerAttackerKOAbility(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
{
""",
        """    if (battleCtx->defender != BATTLER_NONE
        && battleCtx->defender == battleCtx->faintedMon) {
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

        for (int i = 0; i < maxBattlers; i++) {
            if (battleCtx->battleMons[i].curHP
                && Battler_Ability(battleCtx, i) == ABILITY_SOUL_HEART
                && battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]
                    < MAX_STAT_STAGE) {
                battleCtx->battleMons[i].statBoosts[BATTLE_STAT_SP_ATTACK]++;
            }
        }
    }

""",
        "Soul-Heart KO reaction",
    )

    replace_once(
        path,
        """    case ABILITY_MOXIE:
    case ABILITY_CHILLING_NEIGH:
""",
        """    case ABILITY_MOXIE:
    case ABILITY_CHILLING_NEIGH:
    case ABILITY_AS_ONE_GLASTRIER:
""",
        "As One Glastrier KO hook",
    )
    replace_once(
        path,
        """    case ABILITY_GRIM_NEIGH:
""",
        """    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
""",
        "As One Spectrier KO hook",
    )


def patch_as_one_unnerve(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """        && BattleSystem_CountAbility(
            battleSys,
            battleCtx,
            COUNT_ALIVE_BATTLERS_THEIR_SIDE,
            battler,
            ABILITY_UNNERVE)) {
        return FALSE;
    }
""",
        """        && (BattleSystem_CountAbility(
                battleSys,
                battleCtx,
                COUNT_ALIVE_BATTLERS_THEIR_SIDE,
                battler,
                ABILITY_UNNERVE)
            || BattleSystem_CountAbility(
                battleSys,
                battleCtx,
                COUNT_ALIVE_BATTLERS_THEIR_SIDE,
                battler,
                ABILITY_AS_ONE_GLASTRIER)
            || BattleSystem_CountAbility(
                battleSys,
                battleCtx,
                COUNT_ALIVE_BATTLERS_THEIR_SIDE,
                battler,
                ABILITY_AS_ONE_SPECTRIER))) {
        return FALSE;
    }
""",
        "As One Unnerve family",
    )


def patch_turn_end_moody(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    case ABILITY_HARVEST:
""",
        """    case ABILITY_MOODY: {
        static const int stats[] = {
            BATTLE_STAT_ATTACK,
            BATTLE_STAT_DEFENSE,
            BATTLE_STAT_SPEED,
            BATTLE_STAT_SP_ATTACK,
            BATTLE_STAT_SP_DEFENSE,
            BATTLE_STAT_ACCURACY,
            BATTLE_STAT_EVASION,
        };
        int up[7], down[7];
        int upCount = 0, downCount = 0;
        int upStat = -1;

        if (battleCtx->battleMons[battler].curHP) {
            for (int i = 0; i < 7; i++) {
                if (battleCtx->battleMons[battler].statBoosts[stats[i]]
                    < MAX_STAT_STAGE) {
                    up[upCount++] = stats[i];
                }
            }

            if (upCount) {
                upStat = up[BattleSystem_RandNext(battleSys) % upCount];
                battleCtx->battleMons[battler].statBoosts[upStat] += 2;
                if (battleCtx->battleMons[battler].statBoosts[upStat]
                    > MAX_STAT_STAGE) {
                    battleCtx->battleMons[battler].statBoosts[upStat]
                        = MAX_STAT_STAGE;
                }
            }

            for (int i = 0; i < 7; i++) {
                if (stats[i] != upStat
                    && battleCtx->battleMons[battler].statBoosts[stats[i]]
                        > MIN_STAT_STAGE) {
                    down[downCount++] = stats[i];
                }
            }

            if (downCount) {
                int downStat =
                    down[BattleSystem_RandNext(battleSys) % downCount];
                battleCtx->battleMons[battler].statBoosts[downStat]--;
            }
        }
        break;
    }

""",
        "Moody end-turn hook",
    )


def patch_switch_in_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """                    case ABILITY_SCREEN_CLEANER:
""",
        """                    case ABILITY_INTREPID_SWORD: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        int slot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (slot < MAX_PARTY_SIZE
                            && battleCtx->mercuryIntrepidUsed[side][slot] == FALSE) {
                            battleCtx->mercuryIntrepidUsed[side][slot] = TRUE;
                            if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK]
                                < MAX_STAT_STAGE) {
                                battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK]++;
                            }
                        }
                        break;
                    }

                    case ABILITY_DAUNTLESS_SHIELD: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        int slot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (slot < MAX_PARTY_SIZE
                            && battleCtx->mercuryDauntlessUsed[side][slot] == FALSE) {
                            battleCtx->mercuryDauntlessUsed[side][slot] = TRUE;
                            if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]
                                < MAX_STAT_STAGE) {
                                battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]++;
                            }
                        }
                        break;
                    }

                    case ABILITY_CURIOUS_MEDICINE: {
                        int ally = battler ^ 2;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers && battleCtx->battleMons[ally].curHP) {
                            for (int stat = 0; stat < BATTLE_STAT_MAX; stat++) {
                                battleCtx->battleMons[ally].statBoosts[stat] =
                                    DEFAULT_STAT_STAGE;
                            }
                        }
                        break;
                    }

                    case ABILITY_COSTAR: {
                        int ally = battler ^ 2;

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (ally < maxBattlers && battleCtx->battleMons[ally].curHP) {
                            for (int stat = 0; stat < BATTLE_STAT_MAX; stat++) {
                                battleCtx->battleMons[battler].statBoosts[stat] =
                                    battleCtx->battleMons[ally].statBoosts[stat];
                            }
                        }
                        break;
                    }

                    case ABILITY_EMBODY_ASPECT:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SPEED]
                            < MAX_STAT_STAGE) {
                            battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SPEED]++;
                        }
                        break;

                    case ABILITY_EMBODY_ASPECT_2:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_DEFENSE]
                            < MAX_STAT_STAGE) {
                            battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_DEFENSE]++;
                        }
                        break;

                    case ABILITY_EMBODY_ASPECT_3:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK]
                            < MAX_STAT_STAGE) {
                            battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK]++;
                        }
                        break;

                    case ABILITY_EMBODY_ASPECT_4:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]
                            < MAX_STAT_STAGE) {
                            battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]++;
                        }
                        break;

                    case ABILITY_SUPERSWEET_SYRUP: {
                        int side = BattleSystem_GetBattlerSide(battleSys, battler);
                        int slot = battleCtx->selectedPartySlot[battler];

                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (slot < MAX_PARTY_SIZE
                            && battleCtx->mercurySweetSyrupUsed[side][slot] == FALSE) {
                            battleCtx->mercurySweetSyrupUsed[side][slot] = TRUE;

                            for (int target = 0; target < maxBattlers; target++) {
                                if (battleCtx->battleMons[target].curHP
                                    && BattleSystem_GetBattlerSide(battleSys, target) != side
                                    && battleCtx->battleMons[target].statBoosts[BATTLE_STAT_EVASION]
                                        > MIN_STAT_STAGE
                                    && Battler_IgnorableAbility(
                                        battleCtx, battler, target, ABILITY_CLEAR_BODY) == FALSE
                                    && Battler_IgnorableAbility(
                                        battleCtx, battler, target, ABILITY_WHITE_SMOKE) == FALSE
                                    && Battler_IgnorableAbility(
                                        battleCtx, battler, target, ABILITY_FULL_METAL_BODY) == FALSE) {
                                    battleCtx->battleMons[target].statBoosts[BATTLE_STAT_EVASION]--;
                                }
                            }
                        }
                        break;
                    }

""",
        "MR08K switch-in Ability family",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    # Mind's Eye combines Keen Eye's own-accuracy protection with ignoring the
    # target's evasion changes.
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE) {
        evaStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE
        || Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE) {
        evaStages = 0;
    }
    if (Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE
        && accStages < 0) {
        accStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        "Mind's Eye accuracy/evasion behavior",
    )

    # Infiltrator attacks the real target through Substitute.
    replace_once(
        path,
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE) && battleCtx->damage < 0) {
""",
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_INFILTRATOR
            && battleCtx->damage < 0) {
""",
        "Infiltrator Substitute bypass",
    )

    # Gen 9 Protean/Libero: one type change per switch-in. This runs only after
    # status/obedience/target checks succeeded and immediately before the move
    # script begins.
    insert_before_once(
        path,
        """        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        """        if ((Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_PROTEAN
                || Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_LIBERO)
            && battleCtx->mercuryProteanUsed[battleCtx->attacker] == FALSE
            && battleCtx->moveCur != MOVE_STRUGGLE) {
            int mercuryType = CalcMoveType(
                battleCtx, battleCtx->attacker, battleCtx->moveCur);

            if (mercuryType != battleCtx->battleMons[battleCtx->attacker].type1
                || mercuryType != battleCtx->battleMons[battleCtx->attacker].type2) {
                battleCtx->battleMons[battleCtx->attacker].type1 = mercuryType;
                battleCtx->battleMons[battleCtx->attacker].type2 = mercuryType;
                battleCtx->mercuryProteanUsed[battleCtx->attacker] = TRUE;
            }
        }

""",
        "Protean/Libero pre-move type change",
    )

    # Sheer Force suppresses Shell Bell healing and Life Orb recoil when its
    # power boost is active, matching current mainline interaction behavior.
    replace_once(
        path,
        """        if (itemEffect == HOLD_EFFECT_HP_RESTORE_ON_DMG
            && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
""",
        """        if (itemEffect == HOLD_EFFECT_HP_RESTORE_ON_DMG
            && !(Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SHEER_FORCE
                && CURRENT_MOVE_DATA.effectChance)
            && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
""",
        "Sheer Force Shell Bell suppression",
    )
    replace_once(
        path,
        """        if (itemEffect == HOLD_EFFECT_HP_DRAIN_ON_ATK
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
""",
        """        if (itemEffect == HOLD_EFFECT_HP_DRAIN_ON_ATK
            && !(Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SHEER_FORCE
                && CURRENT_MOVE_DATA.effectChance)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
""",
        "Sheer Force Life Orb suppression",
    )


def patch_protean_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    battleCtx->battleMons[battler].timesDamaged = 0;
""",
        """    battleCtx->mercuryProteanUsed[battler] = FALSE;

""",
        "Protean/Libero switch-in reset",
    )


def update_registry(path: Path) -> None:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    context = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "pickpocket_hook": "case ABILITY_PICKPOCKET:" in lib,
        "sheer_force_hook": "ABILITY_SHEER_FORCE" in lib and "CURRENT_MOVE_DATA.effectChance" in controller,
        "moody_hook": "case ABILITY_MOODY:" in lib,
        "infiltrator_hook": "ABILITY_INFILTRATOR" in lib and "ABILITY_INFILTRATOR" in controller,
        "protean_hook": "ABILITY_PROTEAN" in controller and "mercuryProteanUsed" in context,
        "magician_hook": "ABILITY_MAGICIAN" in lib and "BattleSystem_CanStealItem" in lib,
        "soul_heart_hook": "ABILITY_SOUL_HEART" in lib,
        "intrepid_sword_hook": "case ABILITY_INTREPID_SWORD:" in lib and "mercuryIntrepidUsed" in context,
        "dauntless_shield_hook": "case ABILITY_DAUNTLESS_SHIELD:" in lib and "mercuryDauntlessUsed" in context,
        "libero_hook": "ABILITY_LIBERO" in controller,
        "propeller_tail_hook": "ABILITY_PROPELLER_TAIL" in lib,
        "stalwart_hook": "ABILITY_STALWART" in lib,
        "wandering_spirit_hook": "case ABILITY_WANDERING_SPIRIT:" in lib,
        "curious_medicine_hook": "case ABILITY_CURIOUS_MEDICINE:" in lib,
        "as_one_glastrier_hook": "ABILITY_AS_ONE_GLASTRIER" in lib,
        "as_one_spectrier_hook": "ABILITY_AS_ONE_SPECTRIER" in lib,
        "supreme_overlord_hook": "ABILITY_SUPREME_OVERLORD" in lib and "Mercury_CountFaintedAllies" in lib,
        "costar_hook": "case ABILITY_COSTAR:" in lib,
        "mycelium_might_hook": "ABILITY_MYCELIUM_MIGHT" in lib and "CLASS_STATUS" in lib,
        "minds_eye_hook": "ABILITY_MINDS_EYE" in lib and "ABILITY_MINDS_EYE" in controller,
        "embody_aspect_hook": all(token in lib for token in (
            "ABILITY_EMBODY_ASPECT",
            "ABILITY_EMBODY_ASPECT_2",
            "ABILITY_EMBODY_ASPECT_3",
            "ABILITY_EMBODY_ASPECT_4",
        )),
        "supersweet_syrup_hook": "case ABILITY_SUPERSWEET_SYRUP:" in lib and "mercurySweetSyrupUsed" in context,
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
        default=Path("mr08k-canonical-ability-accelerated-batch.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context_state(root)
    patch_shared_helpers(root)
    patch_damage_family(root)
    patch_redirection(root)
    patch_item_and_contact_family(root)
    patch_ko_family(root)
    patch_as_one_unnerve(root)
    patch_turn_end_moody(root)
    patch_switch_in_family(root)
    patch_controller(root)
    patch_protean_reset(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08K_CANONICAL_ABILITY_ACCELERATED_BATCH",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 135,
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
