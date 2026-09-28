#!/usr/bin/env python3
"""MR08K — canonical Ability fast pass, redirect/copy/control family.

Adds nine official/current-mainline Ability mechanics using existing Platinum
battle hooks:

- Moody
- Magic Bounce
- Propeller Tail
- Stalwart
- Costar
- Curious Medicine
- Mind's Eye
- As One (Glastrier)
- As One (Spectrier)

Mechanics-only pass; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_MOODY",
    "ABILITY_MAGIC_BOUNCE",
    "ABILITY_PROPELLER_TAIL",
    "ABILITY_STALWART",
    "ABILITY_CURIOUS_MEDICINE",
    "ABILITY_AS_ONE_GLASTRIER",
    "ABILITY_AS_ONE_SPECTRIER",
    "ABILITY_COSTAR",
    "ABILITY_MINDS_EYE",
)

EXPECTED_IDS = {
    "ABILITY_MOODY": 141,
    "ABILITY_MAGIC_BOUNCE": 156,
    "ABILITY_PROPELLER_TAIL": 239,
    "ABILITY_STALWART": 242,
    "ABILITY_CURIOUS_MEDICINE": 261,
    "ABILITY_AS_ONE_GLASTRIER": 266,
    "ABILITY_AS_ONE_SPECTRIER": 267,
    "ABILITY_COSTAR": 294,
    "ABILITY_MINDS_EYE": 300,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all_exact(path: Path, old: str, new: str, expected: int, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            f"{label}: expected exactly {expected} matches in {path}, found {count}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


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


def patch_moody(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_HARVEST:
""",
        """    switch (Battler_Ability(battleCtx, battler)) {
    case ABILITY_MOODY: {
        static const u8 sMoodyStats[] = {
            BATTLE_STAT_ATTACK,
            BATTLE_STAT_DEFENSE,
            BATTLE_STAT_SP_ATTACK,
            BATTLE_STAT_SP_DEFENSE,
            BATTLE_STAT_SPEED,
        };
        int candidates[NELEMS(sMoodyStats)];
        int candidateCount;
        int i;
        int raiseStat = -1;
        int lowerStat = -1;

        candidateCount = 0;
        for (i = 0; i < NELEMS(sMoodyStats); i++) {
            if (battleCtx->battleMons[battler].statBoosts[sMoodyStats[i]]
                < MAX_STAT_STAGE) {
                candidates[candidateCount++] = sMoodyStats[i];
            }
        }
        if (candidateCount) {
            raiseStat = candidates[BattleSystem_RandNext(battleSys) % candidateCount];
            battleCtx->battleMons[battler].statBoosts[raiseStat] += 2;
            if (battleCtx->battleMons[battler].statBoosts[raiseStat] > MAX_STAT_STAGE) {
                battleCtx->battleMons[battler].statBoosts[raiseStat] = MAX_STAT_STAGE;
            }
        }

        candidateCount = 0;
        for (i = 0; i < NELEMS(sMoodyStats); i++) {
            if (sMoodyStats[i] != raiseStat
                && battleCtx->battleMons[battler].statBoosts[sMoodyStats[i]]
                    > MIN_STAT_STAGE) {
                candidates[candidateCount++] = sMoodyStats[i];
            }
        }
        if (candidateCount) {
            lowerStat = candidates[BattleSystem_RandNext(battleSys) % candidateCount];
            battleCtx->battleMons[battler].statBoosts[lowerStat]--;
        }

        if (raiseStat != -1 || lowerStat != -1) {
            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgTemp = ABILITY_MOODY;
            subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

    case ABILITY_HARVEST:
""",
        "Moody current-mainline end-turn stats",
    )


def patch_magic_bounce(root: Path) -> None:
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
        if (DEFENDER_TURN_FLAGS.magicCoat) {
            DEFENDER_TURN_FLAGS.magicCoat = FALSE;
        }
""",
        "Magic Bounce shares Magic Coat reflection lane",
    )


def patch_redirection_immunity(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_all_exact(
        path,
        """        if (battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        """        if (Battler_Ability(battleCtx, attacker) != ABILITY_PROPELLER_TAIL
            && Battler_Ability(battleCtx, attacker) != ABILITY_STALWART
            && battleCtx->sideConditions[enemySide].followMe
            && battleCtx->battleMons[battleCtx->sideConditions[enemySide].followMeUser].curHP) {
""",
        2,
        "Propeller Tail / Stalwart Follow Me bypass",
    )

    replace_once(
        path,
        """    if (battleCtx->defender == BATTLER_NONE
        || Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE
        || Battler_Ability(battleCtx, attacker) == ABILITY_MOLD_BREAKER) {
        return;
    }
""",
        """    if (battleCtx->defender == BATTLER_NONE
        || Battler_Ability(battleCtx, attacker) == ABILITY_NORMALIZE
        || Battler_Ability(battleCtx, attacker) == ABILITY_MOLD_BREAKER
        || Battler_Ability(battleCtx, attacker) == ABILITY_PROPELLER_TAIL
        || Battler_Ability(battleCtx, attacker) == ABILITY_STALWART) {
        return;
    }
""",
        "Propeller Tail / Stalwart redirection-Ability bypass",
    )


def patch_switch_in_copy_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && Battler_Ability(battleCtx, battler) == ABILITY_DOWNLOAD) {
""",
        """                if (battleCtx->battleMons[battler].downloadAnnounced == FALSE
                    && battleCtx->battleMons[battler].curHP
                    && (Battler_Ability(battleCtx, battler) == ABILITY_COSTAR
                        || Battler_Ability(battleCtx, battler) == ABILITY_CURIOUS_MEDICINE)) {
                    int ally = battler ^ 2;

                    battleCtx->battleMons[battler].downloadAnnounced = TRUE;
                    if ((BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_DOUBLES)
                        && ally < maxBattlers
                        && battleCtx->battleMons[ally].curHP) {
                        int j;

                        if (Battler_Ability(battleCtx, battler) == ABILITY_COSTAR) {
                            for (j = BATTLE_STAT_ATTACK; j < BATTLE_STAT_MAX; j++) {
                                battleCtx->battleMons[battler].statBoosts[j] =
                                    battleCtx->battleMons[ally].statBoosts[j];
                            }
                        } else {
                            for (j = BATTLE_STAT_ATTACK; j < BATTLE_STAT_MAX; j++) {
                                battleCtx->battleMons[ally].statBoosts[j] =
                                    DEFAULT_STAT_STAGE;
                            }
                        }

                        battleCtx->msgBattlerTemp = battler;
                        battleCtx->msgTemp = Battler_Ability(battleCtx, battler);
                        subscript = subscript_mold_breaker;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;
                    }
                }

""",
        "Costar / Curious Medicine switch-in family",
    )


def patch_minds_eye(root: Path) -> None:
    controller = root / "src/battle/battle_controller_player.c"
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"

    replace_once(
        controller,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE) {
        evaStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE) {
        evaStages = 0;
    }
    if (Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE) {
        if (accStages < 0) {
            accStages = 0;
        }
        evaStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        "Mind's Eye accuracy/evasion rule",
    )

    replace_once(
        lib,
        """                if ((battleCtx->battleMons[defender].statusVolatile & VOLATILE_CONDITION_FORESIGHT)
                    || Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY) {
""",
        """                if ((battleCtx->battleMons[defender].statusVolatile & VOLATILE_CONDITION_FORESIGHT)
                    || Battler_Ability(battleCtx, attacker) == ABILITY_SCRAPPY
                    || Battler_Ability(battleCtx, attacker) == ABILITY_MINDS_EYE) {
""",
        "Mind's Eye direct type-chart Ghost bypass",
    )

    replace_once(
        lib,
        """                if (attackerAbility == ABILITY_SCRAPPY) {
""",
        """                if (attackerAbility == ABILITY_SCRAPPY
                    || attackerAbility == ABILITY_MINDS_EYE) {
""",
        "Mind's Eye generic type-chart Ghost bypass",
    )

    replace_once(
        script,
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)) {
""",
        """                } else if (AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_KEEN_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_MINDS_EYE, BATTLE_STAT_ACCURACY)
                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_HYPER_CUTTER, BATTLE_STAT_ATTACK)) {
""",
        "Mind's Eye accuracy-drop prevention",
    )


def patch_as_one(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

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
        && (BattleSystem_CountAbility(
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
        "As One Unnerve component",
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
        "As One Glastrier Chilling Neigh component",
    )

    replace_once(
        path,
        """    case ABILITY_GRIM_NEIGH:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
""",
        """    case ABILITY_GRIM_NEIGH:
    case ABILITY_AS_ONE_SPECTRIER:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
""",
        "As One Spectrier Grim Neigh component",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "moody_hook":
            "case ABILITY_MOODY:" in lib
            and "sMoodyStats" in lib,
        "magic_bounce_hook":
            "ABILITY_MAGIC_BOUNCE" in controller
            and "MOVE_FLAG_CAN_MAGIC_COAT" in controller,
        "propeller_tail_hook":
            lib.count("ABILITY_PROPELLER_TAIL") >= 3,
        "stalwart_hook":
            lib.count("ABILITY_STALWART") >= 3,
        "costar_hook":
            "ABILITY_COSTAR" in lib
            and "statBoosts[j] =" in lib,
        "curious_medicine_hook":
            "ABILITY_CURIOUS_MEDICINE" in lib
            and "DEFAULT_STAT_STAGE" in lib,
        "minds_eye_hook":
            "ABILITY_MINDS_EYE" in controller
            and lib.count("ABILITY_MINDS_EYE") >= 2
            and "AbilityBlocksSpecificStatReduction" in script
            and "ABILITY_MINDS_EYE" in script,
        "as_one_glastrier_hook":
            lib.count("ABILITY_AS_ONE_GLASTRIER") >= 2,
        "as_one_spectrier_hook":
            lib.count("ABILITY_AS_ONE_SPECTRIER") >= 2,
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
        default=Path("mr08k-canonical-ability-redirect-copy-control.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_moody(root)
    patch_magic_bounce(root)
    patch_redirection_immunity(root)
    patch_switch_in_copy_family(root)
    patch_minds_eye(root)
    patch_as_one(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08K_CANONICAL_ABILITY_REDIRECT_COPY_CONTROL",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 119,
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
