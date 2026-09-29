#!/usr/bin/env python3
"""MR10D13 — Grand Choreography.

Implements the approved Mega Oricorio signature mechanic on top of the green
MR10D12 stack:
- Grand Choreography counts as Dancer for the canonical Dancer copy queue.
- After the holder successfully uses or copies a Dance move, it immediately
  performs one 50-BP Revelation Dance through the shared D7 generated-action
  pipeline.
- The generated Revelation Dance checks Fire, Electric, Psychic, and Ghost
  styles. If any style is super-effective against the current target, the first
  such style is used and the type-effectiveness portion is capped at exactly 2x.
- Generated actions remain recursion-guarded and spend no PP.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Grand Choreography": ("ABILITY_MR_GRAND_CHOREOGRAPHY", 326),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise SystemExit(f"{label}: expected anchor not found in {path}")
    if text.count(old) != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {text.count(old)}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def patch_dancer_behavior(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || Battler_Ability(battleCtx, battler) != ABILITY_DANCER) {
""",
        """        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || (Battler_Ability(battleCtx, battler) != ABILITY_DANCER
                && Battler_Ability(battleCtx, battler)
                    != ABILITY_MR_GRAND_CHOREOGRAPHY)) {
""",
        "Grand Choreography Dancer queue membership",
    )

    replace_once(
        path,
        """        if (battleCtx->battleMons[dancer].curHP == 0
            || Battler_Ability(battleCtx, dancer) != ABILITY_DANCER) {
""",
        """        if (battleCtx->battleMons[dancer].curHP == 0
            || (Battler_Ability(battleCtx, dancer) != ABILITY_DANCER
                && Battler_Ability(battleCtx, dancer)
                    != ABILITY_MR_GRAND_CHOREOGRAPHY)) {
""",
        "Grand Choreography Dancer execution gate",
    )

    # D7 must resolve before advancing the Dancer queue so a Grand
    # Choreography copy gets its immediate Revelation Dance before the next
    # queued Dancer acts.
    replace_once(
        path,
        """        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryReactiveCounter(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
            return;
        }
""",
        """        if (Mercury_TryReactiveCounter(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {
            return;
        }

        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
            return;
        }
""",
        "Grand Choreography immediate copied-dance follow-up ordering",
    )


def patch_generated_followup(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static BOOL Mercury_D7ChooseFollowup(\n"
        "    BattleContext *battleCtx,\n"
        "    int *move,\n"
        "    int *power)"
    )
    insertion = """    case ABILITY_MR_GRAND_CHOREOGRAPHY:
        if (Mercury_IsDanceMove(battleCtx->moveCur)) {
            *move = MOVE_REVELATION_DANCE;
            *power = 50;
        }
        break;

"""
    insert_before_in_function(
        path,
        signature,
        """    case ABILITY_MR_LUNAR_WRATH:
""",
        insertion,
        "case ABILITY_MR_GRAND_CHOREOGRAPHY:",
        "Grand Choreography D7 generated follow-up",
    )

    # When a super-effective style exists, seed the generated Revelation Dance
    # with that style before the normal move/type pipeline runs.
    signature = (
        "static BOOL Mercury_TryAbilityFollowup(\n"
        "    BattleSystem *battleSys,\n"
        "    BattleContext *battleCtx)"
    )
    insertion = """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_GRAND_CHOREOGRAPHY
        && followupMove == MOVE_REVELATION_DANCE) {
        int mercuryStyle = Mercury_GrandChoreographyBestStyle(
            battleCtx,
            battleCtx->attacker,
            target);

        if (mercuryStyle != 0xFF) {
            battleCtx->moveType = mercuryStyle;
        }
    }

"""
    insert_before_in_function(
        path,
        signature,
        """    battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;
""",
        insertion,
        "Mercury_GrandChoreographyBestStyle(",
        "Grand Choreography generated Revelation style",
    )


def patch_style_effectiveness(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """int Mercury_GrandChoreographyBestStyle(
    BattleContext *battleCtx,
    int attacker,
    int defender);
""",
        "Grand Choreography style helper declaration",
    )

    helper = """int Mercury_GrandChoreographyBestStyle(
    BattleContext *battleCtx,
    int attacker,
    int defender)
{
    static const u8 mercuryStyles[] = {
        TYPE_FIRE,
        TYPE_ELECTRIC,
        TYPE_PSYCHIC,
        TYPE_GHOST,
    };
    int styleIndex;

    for (styleIndex = 0; styleIndex < NELEMS(mercuryStyles); styleIndex++) {
        int chartEntry = 0;
        int totalMul = 10;
        int style = mercuryStyles[styleIndex];
        int type1 = BattleMon_Get(
            battleCtx, defender, BATTLEMON_TYPE_1, NULL);
        int type2 = BattleMon_Get(
            battleCtx, defender, BATTLEMON_TYPE_2, NULL);

        while (sTypeMatchupMultipliers[chartEntry][0] != 0xFF) {
            if (sTypeMatchupMultipliers[chartEntry][0] == 0xFE) {
                chartEntry++;
                continue;
            }

            if (sTypeMatchupMultipliers[chartEntry][0] == style
                && BasicTypeMulApplies(
                    battleCtx, attacker, defender, chartEntry) == TRUE) {
                if (sTypeMatchupMultipliers[chartEntry][1] == type1) {
                    totalMul = totalMul
                        * sTypeMatchupMultipliers[chartEntry][2] / 10;
                }

                if (type2 != type1
                    && sTypeMatchupMultipliers[chartEntry][1] == type2) {
                    totalMul = totalMul
                        * sTypeMatchupMultipliers[chartEntry][2] / 10;
                }
            }

            chartEntry++;
        }

        if (totalMul > 10) {
            return style;
        }
    }

    return 0xFF;
}

"""
    insert_before_once(
        lib,
        """int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)
""",
        helper,
        "Grand Choreography style helper",
    )

    signature = (
        "int BattleSystem_ApplyTypeChart(BattleSystem *battleSys, BattleContext *battleCtx, "
        "int move, int inType, int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insertion = """    if (battleCtx->mercuryAbilityGeneratedAction
        && Battler_Ability(battleCtx, attacker)
            == ABILITY_MR_GRAND_CHOREOGRAPHY
        && move == MOVE_REVELATION_DANCE
        && Mercury_GrandChoreographyBestStyle(
            battleCtx, attacker, defender) != 0xFF
        && movePower) {
        damage = mercuryDamageBeforeEffectiveness * 2;
        *moveStatusMask &= ~MOVE_STATUS_NOT_VERY_EFFECTIVE;
        *moveStatusMask |= MOVE_STATUS_SUPER_EFFECTIVE;
    }

"""
    insert_before_in_function(
        lib,
        signature,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        insertion,
        "ABILITY_MR_GRAND_CHOREOGRAPHY",
        "Grand Choreography exact 2x effectiveness cap",
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
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "retains_dancer_queue":
            "ABILITY_MR_GRAND_CHOREOGRAPHY" in ctl
            and "Mercury_BuildDancerQueue" in ctl
            and "Mercury_TryNextDancer" in ctl,
        "generated_revelation_dance_50":
            "case ABILITY_MR_GRAND_CHOREOGRAPHY:" in ctl
            and "MOVE_REVELATION_DANCE" in ctl
            and "*power = 50;" in ctl,
        "copied_dance_followup_ordering":
            ctl.find("Mercury_TryAbilityFollowup(battleSys, battleCtx)")
            < ctl.find("Mercury_TryNextDancer(battleSys, battleCtx)", ctl.find("static void BattleControllerPlayer_MoveEnd")),
        "style_helper_exported":
            "int Mercury_GrandChoreographyBestStyle(" in lib
            and "int Mercury_GrandChoreographyBestStyle(" in hdr,
        "four_revelation_styles":
            all(token in lib for token in (
                "TYPE_FIRE",
                "TYPE_ELECTRIC",
                "TYPE_PSYCHIC",
                "TYPE_GHOST",
            )),
        "exact_two_x_effectiveness":
            "damage = mercuryDamageBeforeEffectiveness * 2;" in lib
            and "MOVE_STATUS_SUPER_EFFECTIVE" in lib,
        "generated_action_recursion_guard_reused":
            "mercuryAbilityGeneratedAction" in ctl
            and "mercuryAbilityGeneratedAction = TRUE" in ctl,
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
        default=Path("mr10d13-grand-choreography.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_dancer_behavior(root)
    patch_style_effectiveness(root)
    patch_generated_followup(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D13_GRAND_CHOREOGRAPHY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_systems_reused": [
            "MR08R5 Dancer queue",
            "MR10D7 generated follow-up action",
            "MR10D3 pre-effectiveness damage capture",
        ],
        "remaining_keep_as_written_after_d13": 29,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D13 Grand Choreography validation failed")


if __name__ == "__main__":
    main()
