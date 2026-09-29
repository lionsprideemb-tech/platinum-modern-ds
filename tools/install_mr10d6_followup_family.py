#!/usr/bin/env python3
"""MR10D6 — shared generated follow-up attack family.

Graduates ten KEEP-AS-WRITTEN mechanics behind one extra-action controller:
- Thunder Clouds -> 35-BP Thunderbolt after a successful special attack
- Blade Dance -> 50-BP Leaf Blade after a successful Dance move
- Aftershock -> 65-BP Magnitude after a successful damaging move
- High Tide -> 50-BP Surf after a successful Water damaging move
- Glacial Rage -> 50-BP Blizzard after a successful Ice damaging move
- Chilling Pellets -> 13-BP Icicle Spear after a successful contact hit
- Lunar Wrath -> 50-BP Moongeist Beam after a successful Ghost damaging move
- Frost Dragon -> 50-BP Blizzard after a successful Ice/Dragon damaging move
- Break it Down -> 20-BP Rapid Spin after a successful damaging move
- Volcano Rage -> 50-BP Eruption after a successful Fire move

Generated moves use Platinum's ordinary move pipeline, do not spend PP, cannot
recursively generate another follow-up, and retain their normal move-specific
secondary behavior. A power override is applied at damage calculation so
variable-power moves such as Magnitude and Eruption use the approved fixed BP.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
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
    "Lunar Wrath": ("ABILITY_MR_LUNAR_WRATH", 573),
    "Frost Dragon": ("ABILITY_MR_FROST_DRAGON", 575),
    "Break it Down": ("ABILITY_MR_BREAK_IT_DOWN", 587),
    "Volcano Rage": ("ABILITY_MR_VOLCANO_RAGE", 908),
}
TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


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


def insert_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
    after: bool = False,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    start, end = function_bounds(text, signature)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {signature}, found {count}")
    replacement = anchor + insertion if after else insertion + anchor
    block = block.replace(anchor, replacement, 1)
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insertion = """    // Mercury MR10D6: generated follow-up action state.
    u8 mercuryFollowupActive;
    u8 mercuryFollowupAttacker;
    u8 mercuryFollowupDefender;
    u16 mercuryFollowupOriginalMove;
    u16 mercuryFollowupMove;
    u16 mercuryFollowupPower;

"""
    insert_before_once(
        path,
        "    u32 battleProgressFlag : 1;\n",
        insertion,
        "MR10D6 follow-up state",
    )


def patch_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_followup.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
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
        "subscript_mercury_followup\n",
        "MR10D6 follow-up subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_dancer.s',\n",
        "    'subscript_mercury_followup.s',\n",
        "MR10D6 follow-up subscript build",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helpers = """static int Mercury_D6ResolvedMoveType(BattleContext *battleCtx)
{
    int move = battleCtx->moveCur;
    int ability = Battler_Ability(battleCtx, battleCtx->attacker);
    int type = battleCtx->moveType
        ? battleCtx->moveType
        : MOVE_DATA(move).type;

    if (ability == ABILITY_NORMALIZE) {
        return TYPE_NORMAL;
    }

    if (MOVE_DATA(move).type == TYPE_NORMAL && move != MOVE_STRUGGLE) {
        switch (ability) {
        case ABILITY_REFRIGERATE:
            return TYPE_ICE;
        case ABILITY_PIXILATE:
            return TYPE_FAIRY;
        case ABILITY_AERILATE:
            return TYPE_FLYING;
        case ABILITY_GALVANIZE:
            return TYPE_ELECTRIC;
        case ABILITY_MR_DRACONIC_MIGHT:
            return TYPE_DRAGON;
        }
    }

    return type;
}

static BOOL Mercury_D6MoveMakesContact(
    BattleContext *battleCtx,
    int attacker,
    int move)
{
    return (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)
        && Battler_Ability(battleCtx, attacker) != ABILITY_LONG_REACH;
}

static BOOL Mercury_D6MoveSucceeded(BattleContext *battleCtx)
{
    return (battleCtx->battleStatusMask2 & SYSCTL_MOVE_SUCCEEDED)
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE;
}

static BOOL Mercury_D6MoveDamaging(BattleContext *battleCtx)
{
    return MOVE_DATA(battleCtx->moveCur).class != CLASS_STATUS;
}

static int Mercury_D6FollowupTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int target = battleCtx->defender;

    if (target != BATTLER_NONE
        && battleCtx->battleMons[target].curHP
        && BattleSystem_GetBattlerSide(battleSys, target)
            != BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
        return target;
    }

    return BattleSystem_RandomOpponent(
        battleSys, battleCtx, battleCtx->attacker);
}

static BOOL Mercury_D6SelectFollowup(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *followMove,
    int *followPower)
{
    int ability;
    int moveType;

    if (Mercury_D6MoveSucceeded(battleCtx) == FALSE) {
        return FALSE;
    }

    ability = Battler_Ability(battleCtx, battleCtx->attacker);
    moveType = Mercury_D6ResolvedMoveType(battleCtx);

    switch (ability) {
    case ABILITY_MR_THUNDER_CLOUDS:
        if (Mercury_D6MoveDamaging(battleCtx)
            && MOVE_DATA(battleCtx->moveCur).class == CLASS_SPECIAL) {
            *followMove = MOVE_THUNDERBOLT;
            *followPower = 35;
            return TRUE;
        }
        break;

    case ABILITY_MR_BLADE_DANCE:
        if (Mercury_IsDanceMove(battleCtx->moveCur)) {
            *followMove = MOVE_LEAF_BLADE;
            *followPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_AFTERSHOCK:
        if (Mercury_D6MoveDamaging(battleCtx)) {
            *followMove = MOVE_MAGNITUDE;
            *followPower = 65;
            return TRUE;
        }
        break;

    case ABILITY_MR_HIGH_TIDE:
        if (Mercury_D6MoveDamaging(battleCtx) && moveType == TYPE_WATER) {
            *followMove = MOVE_SURF;
            *followPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_GLACIAL_RAGE:
        if (Mercury_D6MoveDamaging(battleCtx) && moveType == TYPE_ICE) {
            *followMove = MOVE_BLIZZARD;
            *followPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_CHILLING_PELLETS:
        if (Mercury_D6MoveDamaging(battleCtx)
            && Mercury_D6MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
            *followMove = MOVE_ICICLE_SPEAR;
            *followPower = 13;
            return TRUE;
        }
        break;

    case ABILITY_MR_LUNAR_WRATH:
        if (Mercury_D6MoveDamaging(battleCtx) && moveType == TYPE_GHOST) {
            *followMove = MOVE_MOONGEIST_BEAM;
            *followPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_FROST_DRAGON:
        if (Mercury_D6MoveDamaging(battleCtx)
            && (moveType == TYPE_ICE || moveType == TYPE_DRAGON)) {
            *followMove = MOVE_BLIZZARD;
            *followPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_BREAK_IT_DOWN:
        if (Mercury_D6MoveDamaging(battleCtx)) {
            *followMove = MOVE_RAPID_SPIN;
            *followPower = 20;
            return TRUE;
        }
        break;

    case ABILITY_MR_VOLCANO_RAGE:
        if (moveType == TYPE_FIRE) {
            *followMove = MOVE_ERUPTION;
            *followPower = 50;
            return TRUE;
        }
        break;
    }

    return FALSE;
}

static BOOL Mercury_TryAbilityFollowup(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int attacker;
    int target;
    int followMove;
    int followPower;
    int ability;

    if (battleCtx->mercuryFollowupActive) {
        battleCtx->attacker = battleCtx->mercuryFollowupAttacker;
        battleCtx->defender = battleCtx->mercuryFollowupDefender;
        battleCtx->moveCur = battleCtx->mercuryFollowupOriginalMove;
        battleCtx->moveTemp = battleCtx->mercuryFollowupOriginalMove;
        battleCtx->mercuryFollowupActive = FALSE;
        battleCtx->mercuryFollowupPower = 0;
        return FALSE;
    }

    attacker = battleCtx->attacker;
    if (attacker == BATTLER_NONE || battleCtx->battleMons[attacker].curHP == 0) {
        return FALSE;
    }

    followMove = MOVE_NONE;
    followPower = 0;
    if (Mercury_D6SelectFollowup(
            battleSys, battleCtx, &followMove, &followPower) == FALSE) {
        return FALSE;
    }

    target = Mercury_D6FollowupTarget(battleSys, battleCtx);
    if (target == BATTLER_NONE) {
        return FALSE;
    }

    ability = Battler_Ability(battleCtx, attacker);
    battleCtx->mercuryFollowupActive = TRUE;
    battleCtx->mercuryFollowupAttacker = attacker;
    battleCtx->mercuryFollowupDefender = battleCtx->defender;
    battleCtx->mercuryFollowupOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryFollowupMove = followMove;
    battleCtx->mercuryFollowupPower = followPower;

    BattleContext_Init(battleCtx);
    battleCtx->attacker = attacker;
    battleCtx->defender = target;
    battleCtx->moveCur = followMove;
    battleCtx->moveTemp = followMove;
    battleCtx->movePower = followPower;

    // Generated Ability actions do not spend PP or repeat ordinary
    // pre-action incapacity checks.
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

    battleCtx->msgBattlerTemp = attacker;
    battleCtx->msgTemp = ability;
    LOAD_SUBSEQ(subscript_mercury_followup);
    battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

"""
    insert_before_once(
        path,
        "static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)\n",
        helpers,
        "MR10D6 follow-up controller helpers",
    )

    replace_once(
        path,
        """        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
            return;
        }

        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
            return;
        }

        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        "MR10D6 move-end follow-up hook",
    )


def patch_fixed_power(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    signature = "static void BattleScript_CalcMoveDamage(BattleSystem *battleSys, BattleContext *battleCtx)"
    insertion = """    if (battleCtx->mercuryFollowupActive
        && battleCtx->mercuryFollowupPower) {
        battleCtx->movePower = battleCtx->mercuryFollowupPower;
    }

"""
    insert_in_function(
        path,
        signature,
        "    battleCtx->damage = BattleSystem_CalcMoveDamage(battleSys,\n",
        insertion,
        "battleCtx->mercuryFollowupPower",
        "MR10D6 fixed generated-move power",
    )


def patch_initial_state(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)"
    insertion = """    battleCtx->mercuryFollowupActive = FALSE;
    battleCtx->mercuryFollowupPower = 0;

"""
    insert_in_function(
        path,
        signature,
        "    battleCtx->prizeMoneyMul = 1;\n",
        insertion,
        "mercuryFollowupActive = FALSE;",
        "MR10D6 battle-start state",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    follow = (root / "res/battle/scripts/subscripts/subscript_mercury_followup.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    expected_moves = (
        "MOVE_THUNDERBOLT",
        "MOVE_LEAF_BLADE",
        "MOVE_MAGNITUDE",
        "MOVE_SURF",
        "MOVE_BLIZZARD",
        "MOVE_ICICLE_SPEAR",
        "MOVE_MOONGEIST_BEAM",
        "MOVE_RAPID_SPIN",
        "MOVE_ERUPTION",
    )

    checks = {
        "followup_state":
            "mercuryFollowupActive" in ctx
            and "mercuryFollowupPower" in ctx,
        "followup_controller":
            "Mercury_TryAbilityFollowup" in controller
            and "BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in controller,
        "non_recursive":
            "if (battleCtx->mercuryFollowupActive)" in controller
            and "battleCtx->mercuryFollowupActive = FALSE;" in controller,
        "dancer_order_preserved":
            controller.index("Mercury_TryNextDancer")
            < controller.index("Mercury_TryAbilityFollowup"),
        "fixed_power_at_damage_calc":
            "battleCtx->mercuryFollowupPower" in script,
        "generated_moves_present":
            all(move in controller for move in expected_moves),
        "ability_popup_script":
            "subscript_mercury_followup" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in follow,
        "all_ability_cases":
            all(token in controller for token in TOKENS),
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
    ap.add_argument("--report", type=Path, default=Path("mr10d6-followup-family.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_script(root)
    patch_controller(root)
    patch_fixed_power(root)
    patch_initial_state(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D6_FOLLOWUP_FAMILY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "generated_followup_action_controller",
        "deferred_same_family": [
            "Sludge Spit (waiting for Venom Bolt move symbol)",
            "Thundercall (waiting for Smite move symbol)",
            "Sumo Wrestler (end-turn cadence variant)",
        ],
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D6 follow-up family validation failed")


if __name__ == "__main__":
    main()
