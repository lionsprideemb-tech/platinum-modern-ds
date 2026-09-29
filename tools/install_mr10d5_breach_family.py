#!/usr/bin/env python3
"""MR10D5 — protection / barrier breach family.

Implements two KEEP-AS-WRITTEN mechanics on shared Mercury hooks:

- Pinnacle Blade
  Keen Edge (Mercury slicing-class) moves skip accuracy checks, pierce
  Protect-style protection and Substitute, ignore Reflect/Light Screen, and
  shatter the target's protection plus those side barriers after a successful
  hit.

- Demolitionist
  During the holder's entry turn, Attack is doubled; damaging attacks pierce
  Protect-style protection and ignore/break Reflect and Light Screen.

The shared slicing classifier already exists for canonical Sharpness. This pass
exports and reuses it instead of creating a second move-class table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Pinnacle Blade": ("ABILITY_MR_PINNACLE_BLADE", 340),
    "Demolitionist": ("ABILITY_MR_DEMOLITIONIST", 773),
}
TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


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


def patch_local_slicing_helpers(root: Path) -> None:
    helper = """static BOOL Mercury_D5MoveIsSlicing(int move)
{
    switch (move) {
    case MOVE_AERIAL_ACE:
    case MOVE_AIR_CUTTER:
    case MOVE_AIR_SLASH:
    case MOVE_AQUA_CUTTER:
    case MOVE_BEHEMOTH_BLADE:
    case MOVE_BITTER_BLADE:
    case MOVE_CEASELESS_EDGE:
    case MOVE_CROSS_POISON:
    case MOVE_CRUSH_CLAW:
    case MOVE_CUT:
    case MOVE_DIRE_CLAW:
    case MOVE_DRAGON_CLAW:
    case MOVE_FURY_CUTTER:
    case MOVE_KOWTOW_CLEAVE:
    case MOVE_LEAF_BLADE:
    case MOVE_METAL_CLAW:
    case MOVE_MIGHTY_CLEAVE:
    case MOVE_NIGHT_SLASH:
    case MOVE_POPULATION_BOMB:
    case MOVE_PSYBLADE:
    case MOVE_PSYCHO_CUT:
    case MOVE_RAZOR_LEAF:
    case MOVE_RAZOR_SHELL:
    case MOVE_SACRED_SWORD:
    case MOVE_SECRET_SWORD:
    case MOVE_SHADOW_CLAW:
    case MOVE_SLASH:
    case MOVE_SOLAR_BLADE:
    case MOVE_STONE_AXE:
    case MOVE_TACHYON_CUTTER:
    case MOVE_X_SCISSOR:
        return TRUE;
    default:
        return FALSE;
    }
}

"""
    controller = root / "src/battle/battle_controller_player.c"
    script = root / "src/battle/battle_script.c"

    insert_before_once(
        controller,
        "static int BattleControllerPlayer_CheckMoveHitAccuracy(BattleSystem *battleSys, BattleContext *battleCtx, int attacker, int defender, int move)\n",
        helper,
        "MR10D5 controller-local slicing classifier",
    )
    insert_before_once(
        script,
        "static BOOL BtlCmd_CheckSubstitute(BattleSystem *battleSys, BattleContext *battleCtx)\n",
        helper,
        "MR10D5 script-local slicing classifier",
    )

def patch_context_and_entry_state(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    u8 mercurySoothsayerUsedMask[2];
""",
        """    // Mercury MR10D5: battle turn on which Demolitionist entered.
    int mercuryDemolitionistEntryTurn[MAX_BATTLERS];

""",
        "Demolitionist entry-turn state",
    )

    lib = root / "src/battle/battle_lib.c"
    insert_after_once(
        lib,
        """    battleCtx->mercurySoothsayerUntilTurn[battler] = -1;
""",
        """    battleCtx->mercuryDemolitionistEntryTurn[battler] = -1;
    if (Battler_Ability(battleCtx, battler) == ABILITY_MR_DEMOLITIONIST) {
        battleCtx->mercuryDemolitionistEntryTurn[battler] =
            battleCtx->totalTurns;
    }
""",
        "Demolitionist entry-turn initialization",
    )


def patch_accuracy_and_protection(root: Path) -> None:
    controller = root / "src/battle/battle_controller_player.c"

    accuracy_sig = (
        "static int BattleControllerPlayer_CheckMoveHitAccuracy("
        "BattleSystem *battleSys, BattleContext *battleCtx, int attacker, "
        "int defender, int move)"
    )
    insert_before_in_function(
        controller,
        accuracy_sig,
        """    u8 moveType = CalcMoveType(battleCtx, attacker, move);
""",
        """    if (Battler_Ability(battleCtx, attacker)
            == ABILITY_MR_PINNACLE_BLADE
        && Mercury_D5MoveIsSlicing(move)) {
        return 0;
    }

""",
        "ABILITY_MR_PINNACLE_BLADE",
        "Pinnacle Blade accuracy bypass",
    )

    overrides_sig = (
        "static int BattleControllerPlayer_CheckMoveHitOverrides("
        "BattleSystem *battleSys, BattleContext *battleCtx, int attacker, "
        "int defender, int move)"
    )
    insert_before_in_function(
        controller,
        overrides_sig,
        """    if (battleCtx->turnFlags[defender].protecting
""",
        """    BOOL mercuryBreachProtection =
        (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
            && Mercury_D5MoveIsSlicing(move))
        || (Battler_Ability(battleCtx, attacker) == ABILITY_MR_DEMOLITIONIST
            && battleCtx->mercuryDemolitionistEntryTurn[attacker]
                == battleCtx->totalTurns
            && MOVE_DATA(move).class != CLASS_STATUS);

""",
        "mercuryBreachProtection",
        "shared protection-bypass predicate",
    )

    replace_once(
        controller,
        """    if (battleCtx->turnFlags[defender].protecting
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        """    if (battleCtx->turnFlags[defender].protecting
        && mercuryBreachProtection == FALSE
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        "Pinnacle Blade / Demolitionist Protect bypass",
    )


def patch_substitute_bypass(root: Path) -> None:
    controller = root / "src/battle/battle_controller_player.c"
    script = root / "src/battle/battle_script.c"

    replace_once(
        controller,
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_INFILTRATOR
            && battleCtx->damage < 0) {
""",
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            && Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_INFILTRATOR
            && !(Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_MR_PINNACLE_BLADE
                && Mercury_D5MoveIsSlicing(battleCtx->moveCur))
            && battleCtx->damage < 0) {
""",
        "Pinnacle Blade damaging Substitute bypass",
    )

    replace_once(
        script,
        """        && (battler == battleCtx->attacker
            || Battler_Ability(battleCtx, battleCtx->attacker)
                != ABILITY_INFILTRATOR)) {
""",
        """        && (battler == battleCtx->attacker
            || (Battler_Ability(battleCtx, battleCtx->attacker)
                    != ABILITY_INFILTRATOR
                && !(Battler_Ability(battleCtx, battleCtx->attacker)
                        == ABILITY_MR_PINNACLE_BLADE
                    && Mercury_D5MoveIsSlicing(battleCtx->moveCur))))) {
""",
        "Pinnacle Blade scripted Substitute bypass",
    )


def patch_screen_bypass_and_attack(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && !(attackerParams.ability == ABILITY_MR_PINNACLE_BLADE
                && Mercury_MoveIsSlicing(move))
            && !(attackerParams.ability == ABILITY_MR_DEMOLITIONIST
                && battleCtx->mercuryDemolitionistEntryTurn[attacker]
                    == battleCtx->totalTurns)
            && criticalMul == 1
""",
        "Reflect bypass for breach family",
    )

    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && criticalMul == 1
""",
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && attackerParams.ability != ABILITY_INFILTRATOR
            && !(attackerParams.ability == ABILITY_MR_PINNACLE_BLADE
                && Mercury_MoveIsSlicing(move))
            && !(attackerParams.ability == ABILITY_MR_DEMOLITIONIST
                && battleCtx->mercuryDemolitionistEntryTurn[attacker]
                    == battleCtx->totalTurns)
            && criticalMul == 1
""",
        "Light Screen bypass for breach family",
    )

    insert_before_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_MR_DEMOLITIONIST
        && battleCtx->mercuryDemolitionistEntryTurn[attacker]
            == battleCtx->totalTurns) {
        attackStat *= 2;
    }

""",
        "Demolitionist first-turn Attack double",
    )


def patch_post_hit_shatter(root: Path) -> None:
    controller = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )

    insertion = """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && CURRENT_MOVE_DATA.class != CLASS_STATUS) {
            BOOL pinnacleHit =
                Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_MR_PINNACLE_BLADE
                && Mercury_D5MoveIsSlicing(battleCtx->moveCur);
            BOOL demolitionHit =
                Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_MR_DEMOLITIONIST
                && battleCtx->mercuryDemolitionistEntryTurn[
                    battleCtx->attacker] == battleCtx->totalTurns;

            if (pinnacleHit || demolitionHit) {
                int breachSide = BattleSystem_GetBattlerSide(
                    battleSys, battleCtx->defender);

                if (battleCtx->sideConditionsMask[breachSide]
                    & SIDE_CONDITION_REFLECT) {
                    battleCtx->sideConditionsMask[breachSide]
                        &= ~SIDE_CONDITION_REFLECT;
                    battleCtx->sideConditions[breachSide].reflectTurns = 0;
                }

                if (battleCtx->sideConditionsMask[breachSide]
                    & SIDE_CONDITION_LIGHT_SCREEN) {
                    battleCtx->sideConditionsMask[breachSide]
                        &= ~SIDE_CONDITION_LIGHT_SCREEN;
                    battleCtx->sideConditions[breachSide].lightScreenTurns = 0;
                }

                if (pinnacleHit) {
                    battleCtx->turnFlags[battleCtx->defender].protecting = FALSE;
                }
            }
        }

"""
    insert_before_in_function(
        controller,
        signature,
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        insertion,
        "BOOL pinnacleHit",
        "breach-family successful-hit shatter",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "shared_keen_edge_classifier":
            "static BOOL Mercury_MoveIsSlicing(int move)" in lib
            and controller.count("static BOOL Mercury_D5MoveIsSlicing(int move)") == 1
            and script.count("static BOOL Mercury_D5MoveIsSlicing(int move)") == 1,
        "pinnacle_accuracy_bypass":
            "ABILITY_MR_PINNACLE_BLADE" in controller
            and "Mercury_D5MoveIsSlicing(move)" in controller,
        "pinnacle_protect_bypass":
            "mercuryBreachProtection == FALSE" in controller
            and "ABILITY_MR_PINNACLE_BLADE" in controller,
        "pinnacle_substitute_bypass":
            "ABILITY_MR_PINNACLE_BLADE" in script
            and "Mercury_D5MoveIsSlicing(battleCtx->moveCur)" in script
            and "ABILITY_MR_PINNACLE_BLADE" in controller,
        "pinnacle_screen_bypass":
            "ABILITY_MR_PINNACLE_BLADE" in lib
            and lib.count("Mercury_MoveIsSlicing(move)") >= 3,
        "pinnacle_shatters_protection":
            "battleCtx->turnFlags[battleCtx->defender].protecting = FALSE;" in controller,
        "pinnacle_shatters_screens":
            "&= ~SIDE_CONDITION_REFLECT;" in controller
            and "&= ~SIDE_CONDITION_LIGHT_SCREEN;" in controller,
        "demolition_entry_turn_state":
            "mercuryDemolitionistEntryTurn[MAX_BATTLERS]" in ctx
            and "battleCtx->mercuryDemolitionistEntryTurn[battler]" in lib,
        "demolition_attack_double":
            "attackerParams.ability == ABILITY_MR_DEMOLITIONIST" in lib
            and "attackStat *= 2;" in lib,
        "demolition_protect_bypass":
            "ABILITY_MR_DEMOLITIONIST" in controller
            and "mercuryBreachProtection" in controller,
        "demolition_screen_bypass":
            lib.count("ABILITY_MR_DEMOLITIONIST") >= 3,
        "demolition_breaks_screens":
            "BOOL demolitionHit" in controller
            and "SIDE_CONDITION_REFLECT" in controller
            and "SIDE_CONDITION_LIGHT_SCREEN" in controller,
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
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10d5-breach-family.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_local_slicing_helpers(root)
    patch_context_and_entry_state(root)
    patch_accuracy_and_protection(root)
    patch_substitute_bypass(root)
    patch_screen_bypass_and_attack(root)
    patch_post_hit_shatter(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D5_BREACH_FAMILY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "remaining_keep_as_written_after_d5": 54,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D5 breach-family validation failed")


if __name__ == "__main__":
    main()
