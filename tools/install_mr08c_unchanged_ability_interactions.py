#!/usr/bin/env python3
"""MR08C — unchanged canonical Ability fast pass, interaction family.

Ports ten additional official Ability mechanics that remain canonical in the
pinned Elite Redux source. The implementation follows Platinum-native battle
hooks, using hg-engine as the DS mechanics reference.

Implemented:
- Healer
- Telepathy
- Regenerator
- Moxie
- Justified
- Prankster
- Gooey
- Berserk
- Gorilla Tactics
- Screen Cleaner

This pass changes battle logic only. Locked MR07 Summary/Skills visuals remain
untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_HEALER",
    "ABILITY_TELEPATHY",
    "ABILITY_REGENERATOR",
    "ABILITY_MOXIE",
    "ABILITY_JUSTIFIED",
    "ABILITY_PRANKSTER",
    "ABILITY_GOOEY",
    "ABILITY_BERSERK",
    "ABILITY_GORILLA_TACTICS",
    "ABILITY_SCREEN_CLEANER",
)

EXPECTED_IDS = {
    "ABILITY_HEALER": 131,
    "ABILITY_TELEPATHY": 140,
    "ABILITY_REGENERATOR": 144,
    "ABILITY_MOXIE": 153,
    "ABILITY_JUSTIFIED": 154,
    "ABILITY_PRANKSTER": 158,
    "ABILITY_GOOEY": 183,
    "ABILITY_BERSERK": 201,
    "ABILITY_GORILLA_TACTICS": 255,
    "ABILITY_SCREEN_CLEANER": 251,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def patch_priority_and_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Prankster: +1 priority to status moves.
    insert_before_once(
        path,
        """    if (battler1Priority == battler2Priority) {
""",
        """    if (battler1Move
        && battler1Ability == ABILITY_PRANKSTER
        && MOVE_DATA(battler1Move).class == CLASS_STATUS) {
        battler1Priority++;
    }

    if (battler2Move
        && battler2Ability == ABILITY_PRANKSTER
        && MOVE_DATA(battler2Move).class == CLASS_STATUS) {
        battler2Priority++;
    }

""",
        "Prankster priority",
    )

    # Prankster's modern Dark-type immunity and Telepathy both terminate before
    # the move proceeds. Battler IDs preserve side parity in Platinum.
    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE) {
        moveType = TYPE_NORMAL;
    } else if (battleCtx->moveType) {
        moveType = battleCtx->moveType;
    } else {
        moveType = CURRENT_MOVE_DATA.type;
    }

    if (attacker != defender
        && ((attacker & 1) != (defender & 1))
        && Battler_Ability(battleCtx, attacker) == ABILITY_PRANKSTER
        && MOVE_DATA(battleCtx->moveCur).class == CLASS_STATUS
        && (BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL) == TYPE_DARK
            || BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL) == TYPE_DARK)) {
        return subscript_but_it_failed;
    }

    if (attacker != defender
        && ((attacker & 1) == (defender & 1))
        && Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_TELEPATHY) == TRUE
        && CURRENT_MOVE_DATA.power) {
        return subscript_but_it_failed;
    }

    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE
""",
        "Prankster / Telepathy immunity",
    )


def patch_on_hit_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Add defender-triggered modern abilities to Platinum's existing on-hit
    # dispatcher. The normal stat-stage subscript preserves cap checks,
    # Contrary, animations, messages, and other shared behavior.
    replace_once(
        path,
        """    case ABILITY_AFTERMATH:
        if (battleCtx->defender == battleCtx->faintedMon
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
            && BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_DAMP) == 0
            && (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) == FALSE
            && ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP * -1, 4);
            battleCtx->msgBattlerTemp = battleCtx->attacker;

            *subscript = subscript_aftermath;
            result = TRUE;
        }
        break;
    }
""",
        """    case ABILITY_AFTERMATH:
        if (battleCtx->defender == battleCtx->faintedMon
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_MAGIC_GUARD
            && BattleSystem_CountAbility(battleSys, battleCtx, COUNT_ALIVE_BATTLERS, 0, ABILITY_DAMP) == 0
            && (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) == FALSE
            && ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP * -1, 4);
            battleCtx->msgBattlerTemp = battleCtx->attacker;

            *subscript = subscript_aftermath;
            result = TRUE;
        }
        break;

    case ABILITY_JUSTIFIED: {
        int moveType;

        if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_NORMALIZE) {
            moveType = TYPE_NORMAL;
        } else if (battleCtx->moveType) {
            moveType = battleCtx->moveType;
        } else {
            moveType = CURRENT_MOVE_DATA.type;
        }

        if (DEFENDING_MON.curHP
            && moveType == TYPE_DARK
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

    case ABILITY_GOOEY:
        if (ATTACKING_MON.curHP
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            && ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

    case ABILITY_BERSERK: {
        int damageTaken = DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            ? DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            : DEFENDER_SELF_TURN_FLAGS.specialDamageTaken;
        int hpBeforeHit = DEFENDING_MON.curHP - damageTaken;

        if (DEFENDING_MON.curHP
            && damageTaken < 0
            && hpBeforeHit > DEFENDING_MON.maxHP / 2
            && DEFENDING_MON.curHP <= DEFENDING_MON.maxHP / 2
            && DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SP_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;
    }

    }
""",
        "Justified/Gooey/Berserk/Perish Body on-hit family",
    )


def patch_moxie(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"
    controller = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        lib,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad)
""",
        """BOOL BattleSystem_TriggerAttackerKOAbility(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
{
    if (battleCtx->attacker == BATTLER_NONE
        || battleCtx->defender == BATTLER_NONE
        || battleCtx->defender != battleCtx->faintedMon
        || battleCtx->battleMons[battleCtx->attacker].curHP == 0) {
        return FALSE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MOXIE
        && battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->attacker;
        *subscript = subscript_update_stat_stage;
        return TRUE;
    }

    return FALSE;
}

""",
        "Moxie KO helper",
    )

    insert_before_once(
        hdr,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad);
""",
        """BOOL BattleSystem_TriggerAttackerKOAbility(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        "Moxie helper declaration",
    )

    replace_once(
        controller,
        """    ONE_HIT_RAGE,
    ONE_HIT_TRIGGER_ABILITY,
    ONE_HIT_EXTRA_FLINCH,
""",
        """    ONE_HIT_RAGE,
    ONE_HIT_TRIGGER_ABILITY,
    ONE_HIT_TRIGGER_ATTACKER_KO_ABILITY,
    ONE_HIT_EXTRA_FLINCH,
""",
        "Moxie one-hit state enum",
    )
    replace_once(
        controller,
        """    MULTI_HIT_RAGE,
    MULTI_HIT_TRIGGER_ABILITY,
    MULTI_HIT_STATUS,
""",
        """    MULTI_HIT_RAGE,
    MULTI_HIT_TRIGGER_ABILITY,
    MULTI_HIT_TRIGGER_ATTACKER_KO_ABILITY,
    MULTI_HIT_STATUS,
""",
        "Moxie multi-hit state enum",
    )

    replace_once(
        controller,
        """        case ONE_HIT_EXTRA_FLINCH:
            battleCtx->afterMoveMessageState++;
""",
        """        case ONE_HIT_TRIGGER_ATTACKER_KO_ABILITY: {
            int koAbilitySeq;

            battleCtx->afterMoveMessageState++;
            if (BattleSystem_TriggerAttackerKOAbility(battleSys, battleCtx, &koAbilitySeq) == TRUE) {
                LOAD_SUBSEQ(koAbilitySeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }
        }

        case ONE_HIT_EXTRA_FLINCH:
            battleCtx->afterMoveMessageState++;
""",
        "Moxie one-hit controller hook",
    )

    replace_once(
        controller,
        """        case MULTI_HIT_STATUS:
            battleCtx->afterMoveMessageState++;
""",
        """        case MULTI_HIT_TRIGGER_ATTACKER_KO_ABILITY: {
            int koAbilitySeq;

            battleCtx->afterMoveMessageState++;
            if (BattleSystem_TriggerAttackerKOAbility(battleSys, battleCtx, &koAbilitySeq) == TRUE) {
                LOAD_SUBSEQ(koAbilitySeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }
        }

        case MULTI_HIT_STATUS:
            battleCtx->afterMoveMessageState++;
""",
        "Moxie multi-hit controller hook",
    )


def patch_regenerator(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    if (battleCtx->battleMons[battler].curHP && battleCtx->selectedPartySlot[battler] != 6) {
""",
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

    if (battleCtx->battleMons[battler].curHP
        && Battler_Ability(battleCtx, battler) == ABILITY_REGENERATOR
        && battleCtx->battleMons[battler].curHP < battleCtx->battleMons[battler].maxHP) {
        int heal = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP, 3);
        battleCtx->battleMons[battler].curHP += heal;
        if (battleCtx->battleMons[battler].curHP > battleCtx->battleMons[battler].maxHP) {
            battleCtx->battleMons[battler].curHP = battleCtx->battleMons[battler].maxHP;
        }
        BattleMon_CopyToParty(battleSys, battleCtx, battler);
    }

    if (battleCtx->battleMons[battler].curHP && battleCtx->selectedPartySlot[battler] != 6) {
""",
        "Regenerator switch-out heal",
    )


def patch_healer(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_SPEED_BOOST:
""",
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_HEALER: {
        int ally = battler ^ 2;
        int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

        if (ally < maxBattlers
            && battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[ally].curHP
            && (battleCtx->battleMons[ally].status & MON_CONDITION_ANY)
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            battleCtx->battleMons[ally].status = MON_CONDITION_NONE;
            battleCtx->battleMons[ally].statusVolatile &= ~VOLATILE_CONDITION_NIGHTMARE;
            BattleMon_CopyToParty(battleSys, battleCtx, ally);
        }
        break;
    }

    case ABILITY_SPEED_BOOST:
""",
        "Healer end-turn hook",
    )



def patch_screen_cleaner(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """                    case ABILITY_SNOW_WARNING:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;

                        if ((battleCtx->fieldConditionsMask & FIELD_CONDITION_HAILING_PERM) == FALSE) {
                            subscript = subscript_snow_warning;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
""",
        """                    case ABILITY_SNOW_WARNING:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;

                        if ((battleCtx->fieldConditionsMask & FIELD_CONDITION_HAILING_PERM) == FALSE) {
                            subscript = subscript_snow_warning;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

                    case ABILITY_SCREEN_CLEANER:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->sideConditionsMask[0] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditionsMask[1] &=
                            ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
                        battleCtx->sideConditions[0].reflectTurns = 0;
                        battleCtx->sideConditions[0].lightScreenTurns = 0;
                        battleCtx->sideConditions[1].reflectTurns = 0;
                        battleCtx->sideConditions[1].lightScreenTurns = 0;
                        break;
""",
        "Screen Cleaner switch-in hook",
    )

def patch_gorilla_tactics(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    controller = root / "src/battle/battle_controller_player.c"

    replace_once(
        lib,
        """    if (attackerParams.heldItemEffect == HOLD_EFFECT_CHOICE_ATK) {
        attackStat = attackStat * 150 / 100;
    }
""",
        """    if (attackerParams.heldItemEffect == HOLD_EFFECT_CHOICE_ATK
        || attackerParams.ability == ABILITY_GORILLA_TACTICS) {
        attackStat = attackStat * 150 / 100;
    }
""",
        "Gorilla Tactics Attack modifier",
    )

    replace_once(
        lib,
        """        if ((itemEffect == HOLD_EFFECT_CHOICE_ATK || itemEffect == HOLD_EFFECT_CHOICE_SPEED || itemEffect == HOLD_EFFECT_CHOICE_SPATK)
            && (opMask & CHECK_INVALID_CHOICE_ITEM)) {
""",
        """        if ((itemEffect == HOLD_EFFECT_CHOICE_ATK
                || itemEffect == HOLD_EFFECT_CHOICE_SPEED
                || itemEffect == HOLD_EFFECT_CHOICE_SPATK
                || Battler_Ability(battleCtx, battler) == ABILITY_GORILLA_TACTICS)
            && (opMask & CHECK_INVALID_CHOICE_ITEM)) {
""",
        "Gorilla Tactics move-selection lock",
    )

    replace_once(
        controller,
        """        if (itemEffect == HOLD_EFFECT_CHOICE_ATK
            || itemEffect == HOLD_EFFECT_CHOICE_SPEED
            || itemEffect == HOLD_EFFECT_CHOICE_SPATK) {
""",
        """        if (itemEffect == HOLD_EFFECT_CHOICE_ATK
            || itemEffect == HOLD_EFFECT_CHOICE_SPEED
            || itemEffect == HOLD_EFFECT_CHOICE_SPATK
            || Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_GORILLA_TACTICS) {
""",
        "Gorilla Tactics lock capture",
    )

    replace_once(
        controller,
        """            && (itemEffect != HOLD_EFFECT_CHOICE_ATK
                && itemEffect != HOLD_EFFECT_CHOICE_SPEED
                && itemEffect != HOLD_EFFECT_CHOICE_SPATK)) {
""",
        """            && (itemEffect != HOLD_EFFECT_CHOICE_ATK
                && itemEffect != HOLD_EFFECT_CHOICE_SPEED
                && itemEffect != HOLD_EFFECT_CHOICE_SPATK
                && Battler_Ability(battleCtx, battleCtx->defender) != ABILITY_GORILLA_TACTICS)) {
""",
        "Gorilla Tactics choice-lock preservation",
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
    battle_lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    battle_script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    controller = (
        root / "src/battle/battle_controller_player.c"
    ).read_text(encoding="utf-8")
    header = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "healer_hook":
            "case ABILITY_HEALER:" in battle_lib
            and "BattleSystem_RandNext(battleSys) % 10 < 3" in battle_lib,
        "telepathy_hook":
            "ABILITY_TELEPATHY) == TRUE" in battle_lib,
        "regenerator_hook":
            "Battler_Ability(battleCtx, battler) == ABILITY_REGENERATOR"
            in battle_script,
        "moxie_hook":
            "BattleSystem_TriggerAttackerKOAbility" in battle_lib
            and "ABILITY_MOXIE" in battle_lib
            and "ONE_HIT_TRIGGER_ATTACKER_KO_ABILITY" in controller
            and "BattleSystem_TriggerAttackerKOAbility" in header,
        "justified_hook":
            "case ABILITY_JUSTIFIED:" in battle_lib
            and "moveType == TYPE_DARK" in battle_lib,
        "prankster_priority":
            battle_lib.count("ABILITY_PRANKSTER") >= 3
            and "MOVE_DATA(battler1Move).class == CLASS_STATUS" in battle_lib,
        "gooey_hook":
            "case ABILITY_GOOEY:" in battle_lib
            and "MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE" in battle_lib,
        "berserk_hook":
            "case ABILITY_BERSERK:" in battle_lib
            and "MOVE_SUBSCRIPT_PTR_SP_ATTACK_UP_1_STAGE" in battle_lib,
        "gorilla_tactics_hook":
            battle_lib.count("ABILITY_GORILLA_TACTICS") >= 2
            and controller.count("ABILITY_GORILLA_TACTICS") >= 2,
        "screen_cleaner_hook":
            "case ABILITY_SCREEN_CLEANER:" in battle_lib
            and "SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN" in battle_lib,
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
        default=Path("mr08c-unchanged-ability-interactions.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_priority_and_immunity(root)
    patch_on_hit_family(root)
    patch_moxie(root)
    patch_regenerator(root)
    patch_healer(root)
    patch_screen_cleaner(root)
    patch_gorilla_tactics(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR08C_UNCHANGED_ABILITY_INTERACTIONS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 25,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "elite_redux_reference": "Elite-Redux/eliteredux pinned by upstream/LOCK.json",
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08C validation failed")


if __name__ == "__main__":
    main()
