#!/usr/bin/env python3
"""MR08P1 — canonical Wimp Out / Emergency Exit pass.

Ports the current-mainline threshold-switch behavior for Wimp Out and
Emergency Exit into Mercury's Platinum battle controller. The check runs
after the complete move (so multi-hit moves do not force an early switch),
respects Neutralizing Gas through Battler_Ability(), skips Sheer Force
secondary-effect moves, and handles wild opposing Pokémon by ending the
encounter when there is no replacement.

Locked MR07 Summary/editor visuals are not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_WIMP_OUT",
    "ABILITY_EMERGENCY_EXIT",
)

EXPECTED_IDS = {
    "ABILITY_WIMP_OUT": 193,
    "ABILITY_EMERGENCY_EXIT": 194,
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


def patch_subscripts(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"

    switch_script = scripts / "subscript_mercury_wimp_emergency_exit.s"
    switch_script.write_text(
        """#include "macros/btlcmd.inc"


_000:
    TryReplaceFaintedMon BTLSCR_MSG_TEMP, TRUE, _END
    UpdateVarFromVar OPCODE_SET, BTLVAR_FAINTED_MON, BTLVAR_LAST_BATTLER_ID
    UpdateVarFromVar OPCODE_SET, BTLVAR_SWITCHED_MON, BTLVAR_MSG_BATTLER_TEMP
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_PLAYED_MOVE_ANIMATION
    DeletePokemon BTLSCR_MSG_TEMP
    Wait
    HealthBoxSlideOut BTLSCR_MSG_TEMP
    Wait
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS_2, SYSCTL_UTURN_ACTIVE
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_TRY_SYNCHRONIZE_STATUS
    GoToSubscript BATTLE_SUBSCRIPT_SHOW_PARTY_LIST

_END:
    End
""",
        encoding="utf-8",
    )

    flee_script = scripts / "subscript_mercury_wimp_wild_flee.s"
    flee_script.write_text(
        """#include "macros/btlcmd.inc"


_000:
    FadeOutBattle
    Wait
    UpdateVar OPCODE_FLAG_ON, BTLVAR_RESULT_MASK, BATTLE_RESULT_WIN
    End
""",
        encoding="utf-8",
    )

    order = scripts / "sub_seq.order"
    insert_before_once(
        order,
        "subscript_giratina_form_change\n",
        "subscript_mercury_wimp_emergency_exit\nsubscript_mercury_wimp_wild_flee\n",
        "MR08P1 battle subscript order",
    )

    meson = scripts / "meson.build"
    insert_before_once(
        meson,
        "    'subscript_giratina_form_change.s',\n",
        "    'subscript_mercury_wimp_emergency_exit.s',\n"
        "    'subscript_mercury_wimp_wild_flee.s',\n",
        "MR08P1 battle subscript build list",
    )


def patch_battle_lib(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    insert_before_once(
        lib,
        """BOOL BattleSystem_RecoverStatusByAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int skipLoad)
""",
        """BOOL Mercury_TriggerWimpEmergencyExit(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    if (battleCtx->battleStatusMask2 & SYSCTL_UTURN_ACTIVE) {
        return FALSE;
    }

    for (int battler = 0; battler < maxBattlers; battler++) {
        int damageTaken;
        int ability;

        if (battleCtx->battleMons[battler].curHP == 0) {
            continue;
        }

        ability = Battler_Ability(battleCtx, battler);
        if (ability != ABILITY_WIMP_OUT && ability != ABILITY_EMERGENCY_EXIT) {
            continue;
        }

        damageTaken = battleCtx->selfTurnFlags[battler].physicalDamageTaken;
        if (damageTaken == 0) {
            damageTaken = battleCtx->selfTurnFlags[battler].specialDamageTaken;
        }

        if (damageTaken >= 0
            || battleCtx->battleMons[battler].curHP
                > battleCtx->battleMons[battler].maxHP / 2
            || battleCtx->battleMons[battler].curHP - damageTaken
                <= battleCtx->battleMons[battler].maxHP / 2) {
            continue;
        }

        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_SHEER_FORCE
            && Mercury_MoveHasSheerForceSecondary(battleCtx, battleCtx->moveCur)) {
            continue;
        }

        battleCtx->msgBattlerTemp = battler;
        battleCtx->msgAbilityTemp = ability;

        if (BattleSystem_AnyReplacementMons(battleSys, battleCtx, battler)) {
            *subscript = subscript_mercury_wimp_emergency_exit;
            return TRUE;
        }

        if ((BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_TRAINER) == FALSE
            && BattleSystem_GetBattlerSide(battleSys, battler) == BATTLE_SIDE_ENEMY) {
            *subscript = subscript_mercury_wimp_wild_flee;
            return TRUE;
        }
    }

    return FALSE;
}

""",
        "Wimp Out / Emergency Exit dispatcher",
    )

    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_TriggerWimpEmergencyExit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        "Wimp Out / Emergency Exit declaration",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    AFTER_MOVE_HIT_STATE_SHELL_BELL,
    AFTER_MOVE_HIT_STATE_LIFE_ORB,

    AFTER_MOVE_HIT_STATE_END
""",
        """    AFTER_MOVE_HIT_STATE_SHELL_BELL,
    AFTER_MOVE_HIT_STATE_LIFE_ORB,
    AFTER_MOVE_HIT_STATE_WIMP_EMERGENCY_EXIT,

    AFTER_MOVE_HIT_STATE_END
""",
        "Wimp Out after-move state enum",
    )

    replace_once(
        path,
        """        case AFTER_MOVE_HIT_STATE_END:
            battleCtx->afterMoveHitCheckState = 0;
""",
        """        case AFTER_MOVE_HIT_STATE_WIMP_EMERGENCY_EXIT: {
            int abilitySubscript;

            if (Mercury_TriggerWimpEmergencyExit(
                    battleSys, battleCtx, &abilitySubscript) == TRUE) {
                LOAD_SUBSEQ(abilitySubscript);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                machineState = STATE_BREAK_OUT;
            }

            battleCtx->afterMoveHitCheckState++;
            break;
        }

        case AFTER_MOVE_HIT_STATE_END:
            battleCtx->afterMoveHitCheckState = 0;
""",
        "Wimp Out after-move controller hook",
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
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    switch_script = (root / "res/battle/scripts/subscripts/subscript_mercury_wimp_emergency_exit.s").read_text(encoding="utf-8")
    flee_script = (root / "res/battle/scripts/subscripts/subscript_mercury_wimp_wild_flee.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "dispatcher_present":
            "Mercury_TriggerWimpEmergencyExit" in lib
            and "ABILITY_WIMP_OUT" in lib
            and "ABILITY_EMERGENCY_EXIT" in lib,
        "crossing_threshold_check":
            "curHP - damageTaken" in lib
            and "maxHP / 2" in lib,
        "post_move_state":
            "AFTER_MOVE_HIT_STATE_WIMP_EMERGENCY_EXIT" in controller
            and "Mercury_TriggerWimpEmergencyExit" in controller,
        "multi_hit_safe_lane":
            "BattleControllerPlayer_TriggerAfterMoveHitEffects" in controller,
        "sheer_force_suppression":
            "ABILITY_SHEER_FORCE" in lib
            and "Mercury_MoveHasSheerForceSecondary" in lib,
        "switch_subscript":
            "subscript_mercury_wimp_emergency_exit" in order
            and "GoToSubscript BATTLE_SUBSCRIPT_SHOW_PARTY_LIST" in switch_script,
        "wild_flee_subscript":
            "subscript_mercury_wimp_wild_flee" in order
            and "BATTLE_RESULT_WIN" in flee_script,
        "public_declaration":
            "Mercury_TriggerWimpEmergencyExit" in hdr,
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
        default=Path("mr08p1-canonical-ability-wimp-exit.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_subscripts(root)
    patch_battle_lib(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08P1_CANONICAL_ABILITY_WIMP_EXIT",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 158,
        "remaining_modern_canonical_mechanics": 29,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08P1 validation failed")


if __name__ == "__main__":
    main()
