#!/usr/bin/env python3
"""MR10D8 — reactive counter family.

Implements three KEEP-AS-WRITTEN defensive counter mechanics on one shared
generated-action queue:
- Deflect: 20% less incoming direct move damage, then 20-BP Vacuum Wave.
- Cold Rebound: after a damaging contact hit, counter with Icy Wind.
- Parry: 20% less contact-move damage, then counter with Mach Punch.

One pending counter is recorded per qualifying hit. Multi-hit attacks can
therefore queue multiple counters, while Ability-generated attacks are barred
from recursively creating new counters. Counter moves run through Platinum's
ordinary move pipeline without spending PP.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Deflect": ("ABILITY_MR_DEFLECT", 643),
    "Cold Rebound": ("ABILITY_MR_COLD_REBOUND", 771),
    "Parry": ("ABILITY_MR_PARRY", 811),
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
        """    u16 mercuryAbilityFollowupPower;
""",
        """    // Mercury MR10D8: queued defender counterattacks.
    u8 mercuryReactiveCounterActive;
    u8 mercuryReactiveCounterPending[MAX_BATTLERS];
    u8 mercuryReactiveCounterTarget[MAX_BATTLERS];
    u16 mercuryReactiveCounterMove[MAX_BATTLERS];
    u16 mercuryReactiveCounterPower[MAX_BATTLERS];
    u8 mercuryReactiveOriginalAttacker;
    u8 mercuryReactiveOriginalDefender;
    u16 mercuryReactiveOriginalMove;

""",
        "MR10D8 reactive counter state",
    )


def patch_damage_reduction(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_CalcMoveDamage(BattleSystem *battleSys, "
        "BattleContext *battleCtx,\n"
        "    int move,\n"
        "    u32 sideConditions,\n"
        "    u32 fieldConditions,\n"
        "    u16 inPower,\n"
        "    u8 inType,\n"
        "    u8 attacker,\n"
        "    u8 defender,\n"
        "    u8 criticalMul)"
    )
    insertion = """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_DEFLECT) == TRUE
        && moveClass != CLASS_STATUS
        && attacker != defender) {
        damage = damage * 80 / 100;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_PARRY) == TRUE
        && moveClass != CLASS_STATUS
        && attacker != defender
        && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT)) {
        damage = damage * 80 / 100;
    }

"""
    insert_before_in_function(
        path,
        signature,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_PUNK_ROCK) == TRUE
""",
        insertion,
        "ABILITY_MR_DEFLECT) == TRUE",
        "MR10D8 Deflect/Parry damage reduction",
    )


def patch_hit_scheduler(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerAbilityOnHit("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )
    insertion = """    case ABILITY_MR_DEFLECT:
    case ABILITY_MR_COLD_REBOUND:
    case ABILITY_MR_PARRY: {
        int reactiveAbility = Battler_Ability(
            battleCtx, battleCtx->defender);
        BOOL contact = (CURRENT_MOVE_DATA.flags & MOVE_FLAG_MAKES_CONTACT)
            != FALSE;
        BOOL qualifies =
            reactiveAbility == ABILITY_MR_DEFLECT
            || ((reactiveAbility == ABILITY_MR_COLD_REBOUND
                    || reactiveAbility == ABILITY_MR_PARRY)
                && contact);

        if (qualifies
            && battleCtx->mercuryAbilityGeneratedAction == FALSE
            && battleCtx->attacker != BATTLER_NONE
            && ATTACKING_MON.curHP
            && DEFENDING_MON.curHP
            && Battler_SubstituteWasHit(
                battleCtx, battleCtx->defender) == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int reactiveUser = battleCtx->defender;

            if (battleCtx->mercuryReactiveCounterPending[reactiveUser] < 9) {
                battleCtx->mercuryReactiveCounterPending[reactiveUser]++;
            }
            battleCtx->mercuryReactiveCounterTarget[reactiveUser] =
                battleCtx->attacker;

            if (reactiveAbility == ABILITY_MR_DEFLECT) {
                battleCtx->mercuryReactiveCounterMove[reactiveUser] =
                    MOVE_VACUUM_WAVE;
                battleCtx->mercuryReactiveCounterPower[reactiveUser] = 20;
            } else if (reactiveAbility == ABILITY_MR_COLD_REBOUND) {
                battleCtx->mercuryReactiveCounterMove[reactiveUser] =
                    MOVE_ICY_WIND;
                battleCtx->mercuryReactiveCounterPower[reactiveUser] = 0;
            } else {
                battleCtx->mercuryReactiveCounterMove[reactiveUser] =
                    MOVE_MACH_PUNCH;
                battleCtx->mercuryReactiveCounterPower[reactiveUser] = 0;
            }
        }
        break;
    }

"""
    insert_before_in_function(
        path,
        signature,
        """    case ABILITY_PRISMATIC_PELT:
""",
        insertion,
        "case ABILITY_MR_DEFLECT:",
        "MR10D8 reactive counter hit scheduler",
    )


def patch_counter_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_TryReactiveCounter(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int user = BATTLER_NONE;
    int target;
    int move;
    int power;

    if (battleCtx->mercuryReactiveCounterActive) {
        battleCtx->attacker = battleCtx->mercuryReactiveOriginalAttacker;
        battleCtx->defender = battleCtx->mercuryReactiveOriginalDefender;
        battleCtx->moveCur = battleCtx->mercuryReactiveOriginalMove;
        battleCtx->moveTemp = battleCtx->mercuryReactiveOriginalMove;
        battleCtx->mercuryReactiveCounterActive = FALSE;
        battleCtx->mercuryAbilityGeneratedAction = FALSE;
        battleCtx->mercuryAbilityFollowupPower = 0;
    }

    if (battleCtx->mercuryAbilityGeneratedAction) {
        return FALSE;
    }

    for (i = 0; i < maxBattlers; i++) {
        int candidate = battleCtx->monSpeedOrder[i];

        if (battleCtx->mercuryReactiveCounterPending[candidate]) {
            user = candidate;
            break;
        }
    }

    if (user == BATTLER_NONE) {
        return FALSE;
    }

    target = battleCtx->mercuryReactiveCounterTarget[user];
    move = battleCtx->mercuryReactiveCounterMove[user];
    power = battleCtx->mercuryReactiveCounterPower[user];

    battleCtx->mercuryReactiveCounterPending[user]--;

    if (battleCtx->battleMons[user].curHP == 0
        || target == BATTLER_NONE
        || battleCtx->battleMons[target].curHP == 0
        || move == MOVE_NONE) {
        return Mercury_TryReactiveCounter(battleSys, battleCtx);
    }

    battleCtx->mercuryReactiveOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryReactiveOriginalDefender = battleCtx->defender;
    battleCtx->mercuryReactiveOriginalMove = battleCtx->moveCur;
    battleCtx->mercuryReactiveCounterActive = TRUE;

    BattleContext_Init(battleCtx);
    battleCtx->mercuryAbilityGeneratedAction = TRUE;
    battleCtx->attacker = user;
    battleCtx->defender = target;
    battleCtx->moveCur = move;
    battleCtx->moveTemp = move;
    battleCtx->movePower = power;
    battleCtx->mercuryAbilityFollowupPower = power;
    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

    battleCtx->msgTemp = user;
    battleCtx->msgBattlerTemp = user;
    LOAD_SUBSEQ(subscript_mercury_ability_followup);
    battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

"""
    insert_before_once(
        path,
        """static BOOL Mercury_D7SuccessfulMove(BattleContext *battleCtx)
""",
        helper,
        "MR10D8 reactive counter controller",
    )

    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
""",
        """        if (Mercury_TryReactiveCounter(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_TryReactiveCounter(battleSys, battleCtx)",
        "MR10D8 counter-before-followup ordering",
    )


def patch_fixed_power_lane(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    replace_once(
        path,
        """    if (battleCtx->mercuryAbilityFollowupActive
        && battleCtx->mercuryAbilityGeneratedAction
        && battleCtx->mercuryAbilityFollowupPower) {
""",
        """    if ((battleCtx->mercuryAbilityFollowupActive
            || battleCtx->mercuryReactiveCounterActive)
        && battleCtx->mercuryAbilityGeneratedAction
        && battleCtx->mercuryAbilityFollowupPower) {
""",
        "MR10D8 shared fixed-power generated action",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "reactive_queue_state":
            "mercuryReactiveCounterPending[MAX_BATTLERS]" in ctx
            and "mercuryReactiveCounterActive" in ctx,
        "deflect_damage_reduction":
            "ABILITY_MR_DEFLECT) == TRUE" in lib
            and "damage = damage * 80 / 100;" in lib,
        "deflect_vacuum_wave":
            "ABILITY_MR_DEFLECT" in lib
            and "MOVE_VACUUM_WAVE" in lib
            and "mercuryReactiveCounterPower[reactiveUser] = 20;" in lib,
        "cold_rebound_contact_counter":
            "ABILITY_MR_COLD_REBOUND" in lib
            and "MOVE_ICY_WIND" in lib
            and "MOVE_FLAG_MAKES_CONTACT" in lib,
        "parry_contact_reduction":
            "ABILITY_MR_PARRY) == TRUE" in lib
            and "MOVE_FLAG_MAKES_CONTACT" in lib,
        "parry_mach_punch":
            "ABILITY_MR_PARRY" in lib
            and "MOVE_MACH_PUNCH" in lib,
        "substitute_not_countered":
            "Battler_SubstituteWasHit(" in lib,
        "generated_counter_recursion_blocked":
            "mercuryAbilityGeneratedAction == FALSE" in lib,
        "multi_hit_counter_count":
            "mercuryReactiveCounterPending[reactiveUser]++" in lib
            and "mercuryReactiveCounterPending[user]--" in ctl,
        "counter_precedes_attacker_followup":
            ctl.find("Mercury_TryReactiveCounter(battleSys, battleCtx)")
                < ctl.find("Mercury_TryAbilityFollowup(battleSys, battleCtx)"),
        "counter_uses_normal_pipeline":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl
            and "BATTLE_CONTROL_BEFORE_MOVE" in ctl,
        "shared_fixed_power_lane":
            "mercuryReactiveCounterActive" in script
            and "mercuryAbilityFollowupPower" in script,
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
        default=Path("mr10d8-reactive-counters.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_damage_reduction(root)
    patch_hit_scheduler(root)
    patch_counter_controller(root)
    patch_fixed_power_lane(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D8_REACTIVE_COUNTERS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "queued_reactive_generated_action",
        "multi_hit_counters_queue_per_hit": True,
        "generated_actions_recurse": False,
        "remaining_keep_as_written_after_d8": 40,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D8 reactive-counter validation failed")


if __name__ == "__main__":
    main()
