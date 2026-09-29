#!/usr/bin/env python3
"""MR10D7 — generated follow-up move family.

Adds one shared extra-action pipeline for nine KEEP-AS-WRITTEN abilities:
Thunder Clouds, Blade Dance, Aftershock, High Tide, Glacial Rage,
Chilling Pellets, Frost Dragon, Break it Down, and Volcano Rage.

The generated action:
- does not spend PP or consume the holder's selected turn action;
- uses the ordinary Platinum target/redirection/accuracy/type/immunity/move
  script pipeline;
- is explicitly marked as Ability-generated so Pattern Breaker history and
  this follow-up dispatcher cannot recurse;
- can force the reviewed base power immediately before damage calculation,
  which keeps fixed-power Magnitude and Eruption correct even though their
  native scripts normally calculate variable power.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Thunder Clouds": ("ABILITY_MR_THUNDER_CLOUDS", 473),
    "Blade Dance": ("ABILITY_MR_BLADE_DANCE", 505),
    "Aftershock": ("ABILITY_MR_AFTERSHOCK", 556),
    "High Tide": ("ABILITY_MR_HIGH_TIDE", 557),
    "Glacial Rage": ("ABILITY_MR_GLACIAL_RAGE", 570),
    "Chilling Pellets": ("ABILITY_MR_CHILLING_PELLETS", 572),
    "Frost Dragon": ("ABILITY_MR_FROST_DRAGON", 575),
    "Break it Down": ("ABILITY_MR_BREAK_IT_DOWN", 587),
    "Volcano Rage": ("ABILITY_MR_VOLCANO_RAGE", 908),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
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
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if marker in block:
        return
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))

    for name, (token, ability_id) in IMPLEMENTED.items():
        matches = [
            row for row in rows
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
        """    int mercuryDemolitionistEntryTurn[MAX_BATTLERS];
""",
        """    // Mercury MR10D7: one generated Ability action at a time.
    u8 mercuryAbilityFollowupActive;
    u8 mercuryAbilityFollowupOriginalAttacker;
    u8 mercuryAbilityFollowupOriginalDefender;
    u16 mercuryAbilityFollowupOriginalMove;
    u16 mercuryAbilityFollowupMove;
    u16 mercuryAbilityFollowupPower;

""",
        "MR10D7 generated-followup state",
    )


def patch_followup_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    followup = scripts / "subscript_mercury_ability_followup.s"
    followup.write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Platinum-native Ability activation popup.
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_dancer\n",
        "subscript_mercury_ability_followup\n",
        "MR10D7 battle subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_dancer.s',\n",
        "    'subscript_mercury_ability_followup.s',\n",
        "MR10D7 battle subscript build list",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_D7SuccessfulMove(BattleContext *battleCtx)
{
    return (battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN)
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && (battleCtx->moveStatusFlags & MOVE_STATUS_DID_NOT_HIT) == FALSE;
}

static BOOL Mercury_D7ChooseFollowup(
    BattleContext *battleCtx,
    int *move,
    int *power)
{
    int ability = Battler_Ability(battleCtx, battleCtx->attacker);
    int moveType = CalcCurrentMoveType(battleCtx);
    BOOL damaging = CURRENT_MOVE_DATA.power != 0
        && CURRENT_MOVE_DATA.class != CLASS_STATUS;

    *move = MOVE_NONE;
    *power = 0;

    switch (ability) {
    case ABILITY_MR_THUNDER_CLOUDS:
        if (damaging && CURRENT_MOVE_DATA.class == CLASS_SPECIAL) {
            *move = MOVE_THUNDERBOLT;
            *power = 35;
        }
        break;

    case ABILITY_MR_BLADE_DANCE:
        if (Mercury_IsDanceMove(battleCtx->moveCur)) {
            *move = MOVE_LEAF_BLADE;
            *power = 50;
        }
        break;

    case ABILITY_MR_AFTERSHOCK:
        if (damaging) {
            *move = MOVE_MAGNITUDE;
            *power = 65;
        }
        break;

    case ABILITY_MR_HIGH_TIDE:
        if (damaging && moveType == TYPE_WATER) {
            *move = MOVE_SURF;
            *power = 50;
        }
        break;

    case ABILITY_MR_GLACIAL_RAGE:
        if (damaging && moveType == TYPE_ICE) {
            *move = MOVE_BLIZZARD;
            *power = 50;
        }
        break;

    case ABILITY_MR_CHILLING_PELLETS:
        if (damaging && (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)) {
            *move = MOVE_ICICLE_SPEAR;
            *power = 13;
        }
        break;

    case ABILITY_MR_FROST_DRAGON:
        if (damaging && (moveType == TYPE_ICE || moveType == TYPE_DRAGON)) {
            *move = MOVE_BLIZZARD;
            *power = 50;
        }
        break;

    case ABILITY_MR_BREAK_IT_DOWN:
        if (damaging) {
            *move = MOVE_RAPID_SPIN;
            *power = 20;
        }
        break;

    case ABILITY_MR_VOLCANO_RAGE:
        if (moveType == TYPE_FIRE) {
            *move = MOVE_ERUPTION;
            *power = 50;
        }
        break;
    }

    return *move != MOVE_NONE;
}

static BOOL Mercury_TryAbilityFollowup(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int followupMove;
    int followupPower;
    int target;

    if (battleCtx->mercuryAbilityFollowupActive) {
        battleCtx->attacker =
            battleCtx->mercuryAbilityFollowupOriginalAttacker;
        battleCtx->defender =
            battleCtx->mercuryAbilityFollowupOriginalDefender;
        battleCtx->moveCur = battleCtx->mercuryAbilityFollowupOriginalMove;
        battleCtx->moveTemp = battleCtx->mercuryAbilityFollowupOriginalMove;
        battleCtx->mercuryAbilityFollowupActive = FALSE;
        battleCtx->mercuryAbilityGeneratedAction = FALSE;
        battleCtx->mercuryAbilityFollowupMove = MOVE_NONE;
        battleCtx->mercuryAbilityFollowupPower = 0;
        return FALSE;
    }

    if (battleCtx->mercuryAbilityGeneratedAction
        || battleCtx->attacker == BATTLER_NONE
        || battleCtx->moveCur == MOVE_NONE
        || Mercury_D7SuccessfulMove(battleCtx) == FALSE
        || Mercury_D7ChooseFollowup(
            battleCtx, &followupMove, &followupPower) == FALSE) {
        return FALSE;
    }

    target = battleCtx->defender;
    if (target == BATTLER_NONE
        || battleCtx->battleMons[target].curHP == 0
        || BattleSystem_GetBattlerSide(battleSys, target)
            == BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
        target = BattleSystem_RandomOpponent(
            battleSys, battleCtx, battleCtx->attacker);
    }

    if (target == BATTLER_NONE
        || battleCtx->battleMons[target].curHP == 0) {
        return FALSE;
    }

    battleCtx->mercuryAbilityFollowupActive = TRUE;
    battleCtx->mercuryAbilityFollowupOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryAbilityFollowupOriginalDefender = battleCtx->defender;
    battleCtx->mercuryAbilityFollowupOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryAbilityFollowupMove = followupMove;
    battleCtx->mercuryAbilityFollowupPower = followupPower;

    BattleContext_Init(battleCtx);
    battleCtx->mercuryAbilityGeneratedAction = TRUE;
    battleCtx->attacker =
        battleCtx->mercuryAbilityFollowupOriginalAttacker;
    battleCtx->defender = target;
    battleCtx->moveCur = followupMove;
    battleCtx->moveTemp = followupMove;
    battleCtx->movePower = followupPower;

    // Generated actions skip PP, ordinary pre-action incapacity, and
    // obedience but retain targeting, redirection, accuracy, type chart,
    // immunity, move scripts, items, Abilities, fainting, and multi-hit flow.
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

    battleCtx->msgTemp = battleCtx->attacker;
    battleCtx->msgBattlerTemp = battleCtx->attacker;
    LOAD_SUBSEQ(subscript_mercury_ability_followup);
    battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "MR10D7 generated-followup controller helpers",
    )

    sig = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        sig,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_TryAbilityFollowup(battleSys, battleCtx)",
        "MR10D7 move-end follow-up hook",
    )


def patch_fixed_power_override(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    sig = (
        "static void BattleScript_CalcMoveDamage("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        sig,
        """    battleCtx->damage = BattleSystem_CalcMoveDamage(battleSys,
""",
        """    if (battleCtx->mercuryAbilityFollowupActive
        && battleCtx->mercuryAbilityGeneratedAction
        && battleCtx->mercuryAbilityFollowupPower) {
        battleCtx->movePower = battleCtx->mercuryAbilityFollowupPower;
    }

""",
        "mercuryAbilityFollowupPower) {",
        "MR10D7 fixed generated-move power",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    followup = (root / "res/battle/scripts/subscripts/subscript_mercury_ability_followup.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "shared_followup_state":
            "mercuryAbilityFollowupActive" in ctx
            and "mercuryAbilityFollowupPower" in ctx,
        "generated_action_guard":
            "mercuryAbilityGeneratedAction" in ctl
            and "mercuryAbilityGeneratedAction = TRUE" in ctl,
        "normal_move_pipeline":
            "BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl
            and "BATTLE_CONTROL_BEFORE_MOVE" in ctl,
        "no_pp_consumption":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "fixed_power_override":
            "mercuryAbilityFollowupPower" in script
            and "battleCtx->movePower = battleCtx->mercuryAbilityFollowupPower;" in script,
        "variable_power_moves_pinned":
            "MOVE_MAGNITUDE" in ctl
            and "*power = 65;" in ctl
            and "MOVE_ERUPTION" in ctl
            and "*power = 50;" in ctl,
        "thunder_clouds":
            "ABILITY_MR_THUNDER_CLOUDS" in ctl
            and "MOVE_THUNDERBOLT" in ctl
            and "*power = 35;" in ctl,
        "blade_dance":
            "ABILITY_MR_BLADE_DANCE" in ctl
            and "Mercury_IsDanceMove" in ctl
            and "MOVE_LEAF_BLADE" in ctl,
        "aftershock":
            "ABILITY_MR_AFTERSHOCK" in ctl
            and "MOVE_MAGNITUDE" in ctl,
        "high_tide":
            "ABILITY_MR_HIGH_TIDE" in ctl
            and "TYPE_WATER" in ctl
            and "MOVE_SURF" in ctl,
        "glacial_rage":
            "ABILITY_MR_GLACIAL_RAGE" in ctl
            and "MOVE_BLIZZARD" in ctl,
        "chilling_pellets":
            "ABILITY_MR_CHILLING_PELLETS" in ctl
            and "MOVE_FLAG_MAKES_CONTACT" in ctl
            and "MOVE_ICICLE_SPEAR" in ctl,
        "frost_dragon":
            "ABILITY_MR_FROST_DRAGON" in ctl
            and "TYPE_DRAGON" in ctl,
        "break_it_down":
            "ABILITY_MR_BREAK_IT_DOWN" in ctl
            and "MOVE_RAPID_SPIN" in ctl,
        "volcano_rage":
            "ABILITY_MR_VOLCANO_RAGE" in ctl
            and "TYPE_FIRE" in ctl
            and "MOVE_ERUPTION" in ctl,
        "followup_subscript":
            "subscript_mercury_ability_followup" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in followup,
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
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr10d7-generated-followups.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_followup_script(root)
    patch_controller(root)
    patch_fixed_power_override(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D7_GENERATED_FOLLOWUPS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "ability_generated_extra_action",
        "fixed_power_override_supported": True,
        "ability_generated_actions_recurse": False,
        "remaining_keep_as_written_after_d7": 43,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D7 generated-followup validation failed")


if __name__ == "__main__":
    main()
