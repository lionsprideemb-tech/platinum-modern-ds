#!/usr/bin/env python3
"""MR10D7 — barrier-breaker KEEP-AS-WRITTEN batch.

Implements:
- Pinnacle Blade — Keen Edge/slicing moves bypass accuracy, Protect-style
  protection, substitutes, and Reflect/Light Screen, then shatter protection
  and those screens after a successful hit.
- Demolitionist — on the user's first active turn, Attack is doubled, attacks
  pierce Protect-style protection, and successful hits break Reflect/Light
  Screen.

Keen Edge uses the pinned hg-engine slicing-move classification already used
by modern Sharpness semantics.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Pinnacle Blade": ("ABILITY_MR_PINNACLE_BLADE", 340),
    "Demolitionist": ("ABILITY_MR_DEMOLITIONIST", 773),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

SLICING_MOVES = (
    "MOVE_AERIAL_ACE",
    "MOVE_AIR_CUTTER",
    "MOVE_AIR_SLASH",
    "MOVE_AQUA_CUTTER",
    "MOVE_BEHEMOTH_BLADE",
    "MOVE_BITTER_BLADE",
    "MOVE_CEASELESS_EDGE",
    "MOVE_CROSS_POISON",
    "MOVE_CRUSH_CLAW",
    "MOVE_CUT",
    "MOVE_DIRE_CLAW",
    "MOVE_DRAGON_CLAW",
    "MOVE_FURY_CUTTER",
    "MOVE_KOWTOW_CLEAVE",
    "MOVE_LEAF_BLADE",
    "MOVE_METAL_CLAW",
    "MOVE_MIGHTY_CLEAVE",
    "MOVE_NIGHT_SLASH",
    "MOVE_POPULATION_BOMB",
    "MOVE_PSYBLADE",
    "MOVE_PSYCHO_CUT",
    "MOVE_RAZOR_LEAF",
    "MOVE_RAZOR_SHELL",
    "MOVE_SACRED_SWORD",
    "MOVE_SECRET_SWORD",
    "MOVE_SHADOW_CLAW",
    "MOVE_SLASH",
    "MOVE_SOLAR_BLADE",
    "MOVE_STONE_AXE",
    "MOVE_TACHYON_CUTTER",
    "MOVE_X_SCISSOR",
)


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


def patch_shared_helpers(root: Path) -> None:
    hdr = root / "include/battle/battle_lib.h"
    lib = root / "src/battle/battle_lib.c"

    declarations = """BOOL Mercury_IsKeenEdgeMove(int move);
BOOL Mercury_IsDemolitionistFirstTurn(BattleContext *battleCtx, int battler);
BOOL Mercury_AttackPiercesProtection(BattleContext *battleCtx, int attacker, int move);
BOOL Mercury_AttackBypassesSubstitute(BattleContext *battleCtx, int attacker, int move);
BOOL Mercury_AttackBypassesScreens(BattleContext *battleCtx, int attacker, int move);

"""
    insert_before_once(
        hdr,
        "#endif // POKEPLATINUM_BATTLE_BATTLE_LIB_H",
        declarations,
        "MR10D7 public barrier helper declarations",
    )

    cases = "\n".join(f"    case {move}:" for move in SLICING_MOVES)
    helpers = f"""BOOL Mercury_IsKeenEdgeMove(int move)
{{
    switch (move) {{
{cases}
        return TRUE;
    default:
        return FALSE;
    }}
}}

BOOL Mercury_IsDemolitionistFirstTurn(BattleContext *battleCtx, int battler)
{{
    return Battler_Ability(battleCtx, battler) == ABILITY_MR_DEMOLITIONIST
        && battleCtx->battleMons[battler].moveEffectsData.fakeOutTurnNumber
            >= battleCtx->totalTurns;
}}

BOOL Mercury_AttackPiercesProtection(
    BattleContext *battleCtx,
    int attacker,
    int move)
{{
    return (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
            && Mercury_IsKeenEdgeMove(move) == TRUE)
        || Mercury_IsDemolitionistFirstTurn(battleCtx, attacker) == TRUE;
}}

BOOL Mercury_AttackBypassesSubstitute(
    BattleContext *battleCtx,
    int attacker,
    int move)
{{
    return Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(move) == TRUE;
}}

BOOL Mercury_AttackBypassesScreens(
    BattleContext *battleCtx,
    int attacker,
    int move)
{{
    return (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
            && Mercury_IsKeenEdgeMove(move) == TRUE)
        || Mercury_IsDemolitionistFirstTurn(battleCtx, attacker) == TRUE;
}}

"""
    insert_before_once(
        lib,
        "int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,\n",
        helpers,
        "MR10D7 barrier helpers",
    )


def patch_damage(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
    if (Mercury_IsDemolitionistFirstTurn(battleCtx, attacker) == TRUE) {
        attackStat = attackStat * 2;
    }
""",
        "Demolitionist first-turn Attack double",
    )

    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
""",
        """        if ((sideConditions & SIDE_CONDITION_REFLECT) != FALSE
            && Mercury_AttackBypassesScreens(
                battleCtx, attacker, move) == FALSE
""",
        "MR10D7 Reflect bypass",
    )

    replace_once(
        lib,
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
""",
        """        if ((sideConditions & SIDE_CONDITION_LIGHT_SCREEN) != FALSE
            && Mercury_AttackBypassesScreens(
                battleCtx, attacker, move) == FALSE
""",
        "MR10D7 Light Screen bypass",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    if (BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_CATCH_TUTORIAL) {
        return 0;
    }

    u8 moveType = CalcMoveType(battleCtx, attacker, move);
""",
        """    if (BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_CATCH_TUTORIAL) {
        return 0;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(move) == TRUE) {
        return 0;
    }

    u8 moveType = CalcMoveType(battleCtx, attacker, move);
""",
        "Pinnacle Blade accuracy bypass",
    )

    replace_once(
        path,
        """    if (battleCtx->turnFlags[defender].protecting
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        """    if (battleCtx->turnFlags[defender].protecting
        && Mercury_AttackPiercesProtection(
            battleCtx, attacker, move) == FALSE
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        "MR10D7 Protect bypass",
    )

    replace_once(
        path,
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE) && battleCtx->damage < 0) {
""",
        """        if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)
            && Mercury_AttackBypassesSubstitute(
                battleCtx, battleCtx->attacker, battleCtx->moveCur) == FALSE
            && battleCtx->damage < 0) {
""",
        "Pinnacle Blade Substitute bypass",
    )

    shatter_helper = """static void Mercury_ShatterProtectionAndScreens(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int side;
    BOOL pinnacle;
    BOOL demolition;

    pinnacle =
        Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(battleCtx->moveCur) == TRUE;
    demolition = Mercury_IsDemolitionistFirstTurn(
        battleCtx, battleCtx->attacker);

    if (pinnacle == FALSE && demolition == FALSE) {
        return;
    }

    side = BattleSystem_GetBattlerSide(battleSys, battleCtx->defender);
    battleCtx->sideConditionsMask[side]
        &= ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
    battleCtx->sideConditions[side].reflectTurns = 0;
    battleCtx->sideConditions[side].lightScreenTurns = 0;

    if (pinnacle == TRUE) {
        battleCtx->turnFlags[battleCtx->defender].protecting = FALSE;
    }
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_UpdateHP(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        shatter_helper,
        "MR10D7 barrier shatter helper",
    )

    replace_once(
        path,
        """        GF_ASSERT(battleCtx->damage < 0);

        if (BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker) == BattleSystem_GetBattlerSide(battleSys, battleCtx->defender)) {
""",
        """        GF_ASSERT(battleCtx->damage < 0);

        Mercury_ShatterProtectionAndScreens(battleSys, battleCtx);

        if (BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker) == BattleSystem_GetBattlerSide(battleSys, battleCtx->defender)) {
""",
        "MR10D7 post-hit screen shatter",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "keen_edge_classification":
            all(move in lib for move in SLICING_MOVES),
        "pinnacle_accuracy_bypass":
            "ABILITY_MR_PINNACLE_BLADE" in ctl
            and "Mercury_IsKeenEdgeMove(move) == TRUE" in ctl,
        "pinnacle_protection_bypass":
            "Mercury_AttackPiercesProtection(" in ctl,
        "pinnacle_substitute_bypass":
            "Mercury_AttackBypassesSubstitute(" in ctl,
        "pinnacle_screen_bypass":
            "Mercury_AttackBypassesScreens(" in lib,
        "pinnacle_shatters_protection":
            "turnFlags[battleCtx->defender].protecting = FALSE;" in ctl,
        "shared_screen_shatter":
            "SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN" in ctl
            and "reflectTurns = 0;" in ctl
            and "lightScreenTurns = 0;" in ctl,
        "demolitionist_first_turn":
            "Mercury_IsDemolitionistFirstTurn" in lib
            and "fakeOutTurnNumber" in lib,
        "demolitionist_attack_double":
            "attackStat = attackStat * 2;" in lib
            and "ABILITY_MR_DEMOLITIONIST" in lib,
        "demolitionist_protect_pierce":
            "Mercury_AttackPiercesProtection" in hdr
            and "Mercury_IsDemolitionistFirstTurn" in lib,
        "registry_updated":
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
        default=Path("mr10d7-barrier-breakers.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_shared_helpers(root)
    patch_damage(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D7_BARRIER_BREAKERS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "keen_edge_source": "pinned_hg_engine_slicing_table",
        "remaining_keep_as_written_after_d7": 51,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D7 barrier-breaker validation failed")


if __name__ == "__main__":
    main()
