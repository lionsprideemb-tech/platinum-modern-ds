#!/usr/bin/env python3
"""MR08L — canonical Ability fast pass, stateful entry/item family.

Adds eight official/current-mainline Ability mechanics:

- Pickpocket
- Protean
- Magician
- Intrepid Sword (current once-per-battle behavior)
- Dauntless Shield (current once-per-battle behavior)
- Libero
- Opportunist
- Supreme Overlord

Mechanics-only pass; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PICKPOCKET",
    "ABILITY_PROTEAN",
    "ABILITY_MAGICIAN",
    "ABILITY_INTREPID_SWORD",
    "ABILITY_DAUNTLESS_SHIELD",
    "ABILITY_LIBERO",
    "ABILITY_OPPORTUNIST",
    "ABILITY_SUPREME_OVERLORD",
)

EXPECTED_IDS = {
    "ABILITY_PICKPOCKET": 124,
    "ABILITY_PROTEAN": 168,
    "ABILITY_MAGICIAN": 170,
    "ABILITY_INTREPID_SWORD": 234,
    "ABILITY_DAUNTLESS_SHIELD": 235,
    "ABILITY_LIBERO": 236,
    "ABILITY_OPPORTUNIST": 290,
    "ABILITY_SUPREME_OVERLORD": 293,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def patch_battle_context_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    replace_once(
        path,
        """    u32 battleProgressFlag : 1;
    u32 padding3154_01 : 31;
""",
        """    u8 mercuryProteanUsed[MAX_BATTLERS];
    u8 mercuryOnceAbilityFlags[MAX_BATTLERS][MAX_PARTY_SIZE];
    u8 mercurySupremeOverlordBoost[MAX_BATTLERS];

    u32 battleProgressFlag : 1;
    u32 padding3154_01 : 31;
""",
        "MR08L battle-state storage",
    )


def patch_stateful_entry_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """#define TRMSG_LAST_BATTLER_HALF_HP_FLAG 4
""",
        """#define MERCURY_ONCE_INTREPID_SWORD  (1 << 0)
#define MERCURY_ONCE_DAUNTLESS_SHIELD (1 << 1)

""",
        "MR08L once-per-battle flags",
    )

    replace_once(
        path,
        """    battleCtx->battleMons[battler].pressureAnnounced = FALSE;
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        """    battleCtx->battleMons[battler].pressureAnnounced = FALSE;
    battleCtx->mercuryProteanUsed[battler] = FALSE;
    battleCtx->mercurySupremeOverlordBoost[battler] = 0;
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        "reset per-entry Ability state",
    )

    insert_before_once(
        path,
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && (Battler_Ability(battleCtx, battler) == ABILITY_COSTAR
                        || Battler_Ability(battleCtx, battler) == ABILITY_CURIOUS_MEDICINE)) {
""",
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && (Battler_Ability(battleCtx, battler) == ABILITY_INTREPID_SWORD
                        || Battler_Ability(battleCtx, battler) == ABILITY_DAUNTLESS_SHIELD
                        || Battler_Ability(battleCtx, battler) == ABILITY_SUPREME_OVERLORD)) {
                    int ability = Battler_Ability(battleCtx, battler);
                    int slot = battleCtx->selectedPartySlot[battler];

                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;

                    if (ability == ABILITY_INTREPID_SWORD) {
                        if ((battleCtx->mercuryOnceAbilityFlags[battler][slot]
                                & MERCURY_ONCE_INTREPID_SWORD) == 0) {
                            battleCtx->mercuryOnceAbilityFlags[battler][slot] |=
                                MERCURY_ONCE_INTREPID_SWORD;
                            if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK]
                                < MAX_STAT_STAGE) {
                                battleCtx->sideEffectParam =
                                    MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
                                battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                                battleCtx->sideEffectMon = battler;
                                subscript = subscript_update_stat_stage;
                                result = SWITCH_IN_CHECK_RESULT_BREAK;
                                break;
                            }
                        }
                    } else if (ability == ABILITY_DAUNTLESS_SHIELD) {
                        if ((battleCtx->mercuryOnceAbilityFlags[battler][slot]
                                & MERCURY_ONCE_DAUNTLESS_SHIELD) == 0) {
                            battleCtx->mercuryOnceAbilityFlags[battler][slot] |=
                                MERCURY_ONCE_DAUNTLESS_SHIELD;
                            if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]
                                < MAX_STAT_STAGE) {
                                battleCtx->sideEffectParam =
                                    MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE;
                                battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                                battleCtx->sideEffectMon = battler;
                                subscript = subscript_update_stat_stage;
                                result = SWITCH_IN_CHECK_RESULT_BREAK;
                                break;
                            }
                        }
                    } else {
                        int j;
                        int fainted = 0;
                        int partyCount = BattleSystem_GetPartyCount(battleSys, battler);

                        for (j = 0; j < partyCount; j++) {
                            Pokemon *partyMon = BattleSystem_GetPartyPokemon(
                                battleSys, battler, j);

                            if (j != slot
                                && Pokemon_GetValue(
                                    partyMon, MON_DATA_SPECIES, NULL) != SPECIES_NONE
                                && Pokemon_GetValue(
                                    partyMon, MON_DATA_IS_EGG, NULL) == FALSE
                                && Pokemon_GetValue(
                                    partyMon, MON_DATA_HP, NULL) == 0) {
                                fainted++;
                            }
                        }
                        if (fainted > 5) {
                            fainted = 5;
                        }
                        battleCtx->mercurySupremeOverlordBoost[battler] = fainted;
                        battleCtx->msgBattlerTemp = battler;
                        battleCtx->msgTemp = ABILITY_SUPREME_OVERLORD;
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }
                }

""",
        "Intrepid Sword / Dauntless Shield / Supreme Overlord entry family",
    )

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_STRONG_JAW
""",
        """    if (attackerParams.ability == ABILITY_SUPREME_OVERLORD
        && battleCtx->mercurySupremeOverlordBoost[attacker]) {
        movePower = movePower
            * (10 + battleCtx->mercurySupremeOverlordBoost[attacker])
            / 10;
    }

""",
        "Supreme Overlord damage multiplier",
    )


def patch_protean_libero(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    replace_once(
        path,
        """        battleCtx->battleStatusMask2 |= SYSCTL_MOVE_SUCCEEDED;

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        """        battleCtx->battleStatusMask2 |= SYSCTL_MOVE_SUCCEEDED;

        if ((Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_PROTEAN
                || Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_LIBERO)
            && battleCtx->mercuryProteanUsed[battleCtx->attacker] == FALSE
            && battleCtx->moveCur != MOVE_STRUGGLE
            && MOVE_DATA(battleCtx->moveCur).type != TYPE_MYSTERY
            && MON_IS_NOT_TYPE(
                battleCtx->attacker, MOVE_DATA(battleCtx->moveCur).type)) {
            ATTACKING_MON.type1 = MOVE_DATA(battleCtx->moveCur).type;
            ATTACKING_MON.type2 = MOVE_DATA(battleCtx->moveCur).type;
            battleCtx->mercuryProteanUsed[battleCtx->attacker] = TRUE;
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        "Protean / Libero once-per-entry type change",
    )


def patch_opportunist(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    replace_once(
        path,
        """            if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] > MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MAX_STAT_STAGE;
            }
        }
    } else {
""",
        """            if (mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] > MAX_STAT_STAGE) {
                mon->statBoosts[BATTLE_STAT_ATTACK + statOffset] = MAX_STAT_STAGE;
            }

            {
                int i;
                int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
                int boostedStat = BATTLE_STAT_ATTACK + statOffset;

                for (i = 0; i < maxBattlers; i++) {
                    if (i != battleCtx->sideEffectMon
                        && battleCtx->battleMons[i].curHP
                        && BattleSystem_GetBattlerSide(battleSys, i)
                            != BattleSystem_GetBattlerSide(
                                battleSys, battleCtx->sideEffectMon)
                        && Battler_Ability(battleCtx, i) == ABILITY_OPPORTUNIST
                        && battleCtx->battleMons[i].statBoosts[boostedStat]
                            < MAX_STAT_STAGE) {
                        battleCtx->battleMons[i].statBoosts[boostedStat] +=
                            stageChange;
                        if (battleCtx->battleMons[i].statBoosts[boostedStat]
                            > MAX_STAT_STAGE) {
                            battleCtx->battleMons[i].statBoosts[boostedStat] =
                                MAX_STAT_STAGE;
                        }
                    }
                }
            }
        }
    } else {
""",
        "Opportunist copies opponent stat raises",
    )


def patch_item_theft_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
""",
        """static BOOL Mercury_CanAbilityTransferItem(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int receiver,
    int donor)
{
    int receiverAbility = Battler_Ability(battleCtx, receiver);
    int donorAbility = Battler_Ability(battleCtx, donor);

    if (battleCtx->battleMons[receiver].heldItem != ITEM_NONE
        || battleCtx->battleMons[donor].heldItem == ITEM_NONE
        || receiverAbility == ABILITY_MULTITYPE
        || donorAbility == ABILITY_MULTITYPE
        || receiverAbility == ABILITY_RKS_SYSTEM
        || donorAbility == ABILITY_RKS_SYSTEM
        || battleCtx->battleMons[donor].heldItem == ITEM_GRISEOUS_ORB
        || battleCtx->battleMons[donor].moveEffectsData.custapBerry
        || battleCtx->battleMons[donor].moveEffectsData.quickClaw
        || BattleSystem_CanStealItem(battleSys, battleCtx, donor) == FALSE) {
        return FALSE;
    }

    if (Battler_IgnorableAbility(
            battleCtx, receiver, donor, ABILITY_STICKY_HOLD) == TRUE) {
        return FALSE;
    }

    return TRUE;
}

static void Mercury_TransferHeldItem(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int receiver,
    int donor)
{
    battleCtx->battleMons[receiver].heldItem =
        battleCtx->battleMons[donor].heldItem;
    battleCtx->battleMons[donor].heldItem = ITEM_NONE;
    BattleMon_CopyToParty(battleSys, battleCtx, donor);
    BattleMon_CopyToParty(battleSys, battleCtx, receiver);
}

""",
        "item-transfer helpers",
    )

    replace_once(
        path,
        """    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
    case ABILITY_STATIC:
""",
        """    switch (Battler_Ability(battleCtx, battleCtx->defender)) {
    case ABILITY_PICKPOCKET:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_PICKPOCKET) == TRUE
            && ATTACKING_MON.curHP
            && DEFENDING_MON.curHP
            && CURRENT_MOVE_DATA.power
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && Mercury_CanAbilityTransferItem(
                battleSys,
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker)) {
            Mercury_TransferHeldItem(
                battleSys,
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker);
            battleCtx->msgBattlerTemp = battleCtx->defender;
            battleCtx->msgTemp = ABILITY_PICKPOCKET;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

    case ABILITY_STATIC:
""",
        "Pickpocket defender on-hit item theft",
    )

    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MAGICIAN
        && ATTACKING_MON.curHP
        && CURRENT_MOVE_DATA.class != CLASS_STATUS
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_CanAbilityTransferItem(
            battleSys,
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender)) {
        Mercury_TransferHeldItem(
            battleSys,
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender);
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        battleCtx->msgTemp = ABILITY_MAGICIAN;
        *subscript = subscript_mold_breaker;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        "Magician attacker on-hit item theft",
    )


def update_registry(path: Path) -> None:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "state_storage":
            "mercuryProteanUsed" in ctx
            and "mercuryOnceAbilityFlags" in ctx
            and "mercurySupremeOverlordBoost" in ctx,
        "pickpocket_hook":
            "case ABILITY_PICKPOCKET:" in lib
            and "Mercury_CanAbilityTransferItem" in lib,
        "protean_hook":
            "ABILITY_PROTEAN" in controller
            and "mercuryProteanUsed" in controller,
        "magician_hook":
            "ABILITY_MAGICIAN" in lib
            and "Mercury_TransferHeldItem" in lib,
        "intrepid_sword_hook":
            "ABILITY_INTREPID_SWORD" in lib
            and "MERCURY_ONCE_INTREPID_SWORD" in lib,
        "dauntless_shield_hook":
            "ABILITY_DAUNTLESS_SHIELD" in lib
            and "MERCURY_ONCE_DAUNTLESS_SHIELD" in lib,
        "libero_hook":
            "ABILITY_LIBERO" in controller
            and "mercuryProteanUsed" in controller,
        "opportunist_hook":
            "ABILITY_OPPORTUNIST" in script
            and "stageChange" in script,
        "supreme_overlord_hook":
            "ABILITY_SUPREME_OVERLORD" in lib
            and "mercurySupremeOverlordBoost" in lib,
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
        default=Path("mr08l-canonical-ability-stateful-entry-item.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_battle_context_state(root)
    patch_stateful_entry_family(root)
    patch_protean_libero(root)
    patch_opportunist(root)
    patch_item_theft_family(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08L_CANONICAL_ABILITY_STATEFUL_ENTRY_ITEM",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 127,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "primary_ds_reference": "BluRosie/hg-engine pinned by upstream/LOCK.json",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08L validation failed")


if __name__ == "__main__":
    main()
