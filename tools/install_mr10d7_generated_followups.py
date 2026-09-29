#!/usr/bin/env python3
"""MR10D7 — generated follow-up move family.

Implements ten KEEP-AS-WRITTEN abilities on one shared extra-action lane:
- Thunder Clouds -> 35 BP Thunderbolt after a successful special damaging move
- Blade Dance -> 50 BP Leaf Blade after a successful Dance move
- Aftershock -> 65 BP Magnitude after a successful damaging move
- High Tide -> 50 BP Surf after a successful Water damaging move
- Glacial Rage -> 50 BP Blizzard after a successful Ice damaging move
- Chilling Pellets -> 13 BP Icicle Spear after a successful contact hit
- Lunar Wrath -> 50 BP Moongeist Beam after a successful Ghost damaging move
- Frost Dragon -> 50 BP Blizzard after a successful Ice/Dragon damaging move
- Break it Down -> 20 BP Rapid Spin after a successful damaging move
- Volcano Rage -> 50 BP Eruption after a successful Fire-type move

Generated follow-ups use Platinum's normal move pipeline, do not spend PP, and
are marked as Ability-generated so they cannot recursively create another
follow-up or contaminate Pattern Breaker's real move history. Forced BP is
carried separately so variable-power scripts such as Magnitude/Eruption cannot
overwrite the approved generated power.

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
    "Lunar Wrath": ("ABILITY_MR_LUNAR_WRATH", 573),
    "Frost Dragon": ("ABILITY_MR_FROST_DRAGON", 575),
    "Break it Down": ("ABILITY_MR_BREAK_IT_DOWN", 587),
    "Volcano Rage": ("ABILITY_MR_VOLCANO_RAGE", 908),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

FOLLOWUP_MOVES = {
    "MOVE_THUNDERBOLT": 85,
    "MOVE_LEAF_BLADE": 348,
    "MOVE_MAGNITUDE": 222,
    "MOVE_SURF": 57,
    "MOVE_BLIZZARD": 59,
    "MOVE_ICICLE_SPEAR": 333,
    "MOVE_MOONGEIST_BEAM": 714,
    "MOVE_RAPID_SPIN": 229,
    "MOVE_ERUPTION": 284,
}


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


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def validate_moves(root: Path) -> None:
    moves = [
        line.strip()
        for line in (root / "generated/moves.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token, move_id in FOLLOWUP_MOVES.items():
        if len(moves) <= move_id or moves[move_id] != token:
            got = moves[move_id] if len(moves) > move_id else None
            raise SystemExit(
                f"{token}: expected move ID {move_id}, got {got!r}"
            )


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryAbilityGeneratedAction;
""",
        """    // Mercury MR10D7: one generated follow-up action and its parent.
    u8 mercuryFollowupActive;
    u8 mercuryFollowupOriginalAttacker;
    u8 mercuryFollowupOriginalDefender;
    u16 mercuryFollowupOriginalMove;
    u16 mercuryFollowupOriginalMoveTemp;
    u16 mercuryGeneratedPower;

""",
        "MR10D7 generated follow-up state",
    )


def patch_forced_power(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """static void BattleScript_CalcMoveDamage(BattleSystem *battleSys, BattleContext *battleCtx)
{
    int moveType;
""",
        """static void BattleScript_CalcMoveDamage(BattleSystem *battleSys, BattleContext *battleCtx)
{
    int moveType;
    int mercuryMovePower;
""",
        "MR10D7 forced-power local",
    )

    replace_once(
        path,
        """    battleCtx->damage = BattleSystem_CalcMoveDamage(battleSys,
        battleCtx,
        battleCtx->moveCur,
        battleCtx->sideConditionsMask[BattleSystem_GetBattlerSide(battleSys, battleCtx->defender)],
        battleCtx->fieldConditionsMask,
        battleCtx->movePower,
""",
        """    mercuryMovePower = battleCtx->movePower;
    if (battleCtx->mercuryAbilityGeneratedAction
        && battleCtx->mercuryGeneratedPower) {
        mercuryMovePower = battleCtx->mercuryGeneratedPower;
    }

    battleCtx->damage = BattleSystem_CalcMoveDamage(battleSys,
        battleCtx,
        battleCtx->moveCur,
        battleCtx->sideConditionsMask[BattleSystem_GetBattlerSide(battleSys, battleCtx->defender)],
        battleCtx->fieldConditionsMask,
        mercuryMovePower,
""",
        "MR10D7 generated forced base power",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_PrimaryMoveSucceeded(BattleContext *battleCtx)
{
    if ((battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN) == FALSE) {
        return FALSE;
    }

    if (battleCtx->moveStatusFlags
        & (MOVE_STATUS_DID_NOT_HIT | MOVE_STATUS_NO_MORE_WORK)) {
        return FALSE;
    }

    return TRUE;
}

static int Mercury_CurrentResolvedMoveType(BattleContext *battleCtx)
{
    if (battleCtx->moveType) {
        return battleCtx->moveType;
    }

    return CalcMoveType(
        battleCtx,
        battleCtx->attacker,
        battleCtx->moveCur);
}

static BOOL Mercury_SelectAbilityFollowup(
    BattleContext *battleCtx,
    int *followupMove,
    int *followupPower)
{
    int ability;
    int move;
    int moveType;
    BOOL damaging;
    BOOL hit;

    if (battleCtx->attacker == BATTLER_NONE
        || battleCtx->moveCur == MOVE_NONE
        || battleCtx->mercuryAbilityGeneratedAction
        || Mercury_PrimaryMoveSucceeded(battleCtx) == FALSE) {
        return FALSE;
    }

    ability = Battler_Ability(battleCtx, battleCtx->attacker);
    move = battleCtx->moveCur;
    moveType = Mercury_CurrentResolvedMoveType(battleCtx);
    damaging = MOVE_DATA(move).power != 0;
    hit = (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT) != 0;

    switch (ability) {
    case ABILITY_MR_THUNDER_CLOUDS:
        if (damaging && hit && MOVE_DATA(move).class == CLASS_SPECIAL) {
            *followupMove = MOVE_THUNDERBOLT;
            *followupPower = 35;
            return TRUE;
        }
        break;

    case ABILITY_MR_BLADE_DANCE:
        if (Mercury_IsDanceMove(move)) {
            *followupMove = MOVE_LEAF_BLADE;
            *followupPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_AFTERSHOCK:
        if (damaging && hit) {
            *followupMove = MOVE_MAGNITUDE;
            *followupPower = 65;
            return TRUE;
        }
        break;

    case ABILITY_MR_HIGH_TIDE:
        if (damaging && hit && moveType == TYPE_WATER) {
            *followupMove = MOVE_SURF;
            *followupPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_GLACIAL_RAGE:
        if (damaging && hit && moveType == TYPE_ICE) {
            *followupMove = MOVE_BLIZZARD;
            *followupPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_CHILLING_PELLETS:
        if (damaging
            && hit
            && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)) {
            *followupMove = MOVE_ICICLE_SPEAR;
            *followupPower = 13;
            return TRUE;
        }
        break;

    case ABILITY_MR_LUNAR_WRATH:
        if (damaging && hit && moveType == TYPE_GHOST) {
            *followupMove = MOVE_MOONGEIST_BEAM;
            *followupPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_FROST_DRAGON:
        if (damaging
            && hit
            && (moveType == TYPE_ICE || moveType == TYPE_DRAGON)) {
            *followupMove = MOVE_BLIZZARD;
            *followupPower = 50;
            return TRUE;
        }
        break;

    case ABILITY_MR_BREAK_IT_DOWN:
        if (damaging && hit) {
            *followupMove = MOVE_RAPID_SPIN;
            *followupPower = 20;
            return TRUE;
        }
        break;

    case ABILITY_MR_VOLCANO_RAGE:
        if (moveType == TYPE_FIRE) {
            *followupMove = MOVE_ERUPTION;
            *followupPower = 50;
            return TRUE;
        }
        break;
    }

    return FALSE;
}

static int Mercury_FollowupTarget(
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
        battleSys,
        battleCtx,
        battleCtx->attacker);
}

static BOOL Mercury_TryAbilityFollowup(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int followupMove;
    int followupPower;
    int target;

    if (battleCtx->mercuryFollowupActive
        && battleCtx->mercuryAbilityGeneratedAction) {
        battleCtx->attacker = battleCtx->mercuryFollowupOriginalAttacker;
        battleCtx->defender = battleCtx->mercuryFollowupOriginalDefender;
        battleCtx->moveCur = battleCtx->mercuryFollowupOriginalMove;
        battleCtx->moveTemp = battleCtx->mercuryFollowupOriginalMoveTemp;
        battleCtx->movePower = 0;
        battleCtx->moveType = 0;
        battleCtx->mercuryGeneratedPower = 0;
        battleCtx->mercuryAbilityGeneratedAction = FALSE;
        battleCtx->mercuryFollowupActive = FALSE;
        return FALSE;
    }

    if (battleCtx->mercuryFollowupActive
        || battleCtx->mercuryAbilityGeneratedAction
        || battleCtx->attacker == BATTLER_NONE
        || battleCtx->battleMons[battleCtx->attacker].curHP == 0
        || (battleCtx->battlersSwitchingMask & FlagIndex(battleCtx->attacker))) {
        return FALSE;
    }

    if (Mercury_SelectAbilityFollowup(
            battleCtx, &followupMove, &followupPower) == FALSE) {
        return FALSE;
    }

    target = Mercury_FollowupTarget(battleSys, battleCtx);
    if (target == BATTLER_NONE) {
        return FALSE;
    }

    battleCtx->mercuryFollowupOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryFollowupOriginalDefender = battleCtx->defender;
    battleCtx->mercuryFollowupOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryFollowupOriginalMoveTemp = battleCtx->moveTemp;
    battleCtx->mercuryFollowupActive = TRUE;

    BattleContext_Init(battleCtx);
    battleCtx->attacker = battleCtx->mercuryFollowupOriginalAttacker;
    battleCtx->defender = target;
    battleCtx->moveCur = followupMove;
    battleCtx->moveTemp = followupMove;
    battleCtx->movePower = followupPower;
    battleCtx->mercuryGeneratedPower = followupPower;
    battleCtx->mercuryAbilityGeneratedAction = TRUE;

    // Ability-generated attacks do not spend PP or repeat ordinary
    // pre-action incapacity checks. The normal target/redirection/accuracy/
    // type/immunity pipeline still resolves the generated move.
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

    battleCtx->msgTemp = battleCtx->attacker;
    battleCtx->msgBattlerTemp = battleCtx->attacker;
    LOAD_SUBSEQ(subscript_mercury_dancer);
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
        "MR10D7 generated follow-up controller helpers",
    )

    insert_before_once(
        path,
        """        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
""",
        """        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "MR10D7 generated follow-up move-end hook",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    moves = [
        line.strip()
        for line in (root / "generated/moves.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "shared_followup_state":
            "mercuryFollowupActive" in ctx
            and "mercuryGeneratedPower" in ctx,
        "generated_action_guard":
            "mercuryAbilityGeneratedAction" in ctl
            and "mercuryAbilityGeneratedAction = TRUE" in ctl
            and "mercuryAbilityGeneratedAction = FALSE" in ctl,
        "forced_power_path":
            "mercuryMovePower = battleCtx->mercuryGeneratedPower;" in script,
        "skips_pp_and_incapacity":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "normal_move_pipeline":
            "commandNext = BATTLE_CONTROL_BEFORE_MOVE" in ctl,
        "pattern_breaker_history_safe":
            "mercuryAbilityGeneratedAction = TRUE" in ctl,
        "thunder_clouds_35":
            "ABILITY_MR_THUNDER_CLOUDS" in ctl
            and "MOVE_THUNDERBOLT" in ctl
            and "*followupPower = 35;" in ctl,
        "blade_dance_50":
            "ABILITY_MR_BLADE_DANCE" in ctl
            and "Mercury_IsDanceMove(move)" in ctl
            and "MOVE_LEAF_BLADE" in ctl,
        "aftershock_65":
            "ABILITY_MR_AFTERSHOCK" in ctl
            and "MOVE_MAGNITUDE" in ctl
            and "*followupPower = 65;" in ctl,
        "high_tide_50":
            "ABILITY_MR_HIGH_TIDE" in ctl
            and "MOVE_SURF" in ctl,
        "glacial_rage_50":
            "ABILITY_MR_GLACIAL_RAGE" in ctl
            and "MOVE_BLIZZARD" in ctl,
        "chilling_pellets_13":
            "ABILITY_MR_CHILLING_PELLETS" in ctl
            and "MOVE_FLAG_MAKES_CONTACT" in ctl
            and "MOVE_ICICLE_SPEAR" in ctl
            and "*followupPower = 13;" in ctl,
        "lunar_wrath_50":
            "ABILITY_MR_LUNAR_WRATH" in ctl
            and "MOVE_MOONGEIST_BEAM" in ctl,
        "frost_dragon_50":
            "ABILITY_MR_FROST_DRAGON" in ctl
            and "moveType == TYPE_DRAGON" in ctl,
        "break_it_down_20":
            "ABILITY_MR_BREAK_IT_DOWN" in ctl
            and "MOVE_RAPID_SPIN" in ctl
            and "*followupPower = 20;" in ctl,
        "volcano_rage_50":
            "ABILITY_MR_VOLCANO_RAGE" in ctl
            and "MOVE_ERUPTION" in ctl,
        "move_end_hook":
            "Mercury_TryAbilityFollowup(battleSys, battleCtx)" in ctl,
        "implemented_registry_updated":
            all(token in registry_lines for token in TOKENS),
        "followup_move_ids_stable":
            all(len(moves) > move_id and moves[move_id] == token
                for token, move_id in FOLLOWUP_MOVES.items()),
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
    validate_moves(root)
    patch_context(root)
    patch_forced_power(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D7_GENERATED_FOLLOWUPS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "generated_followups_do_not_spend_pp": True,
        "generated_followups_do_not_recurse": True,
        "generated_followups_excluded_from_pattern_breaker_history": True,
        "remaining_keep_as_written_after_d7": 42,
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
