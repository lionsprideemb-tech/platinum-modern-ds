#!/usr/bin/env python3
"""MR10B3 — safe precision/offense/status canonical overrides.

This batch uses only already-approved MR09 mechanics and does not touch any of
the 93 held new-engine-system decisions.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path

CHANGED = (
    "Keen Eye",
    "Inner Focus",
    "Hyper Cutter",
    "Toxic Boost",
    "Flare Boost",
    "Illusion",
    "Long Reach",
    "Weak Armor",
)


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


def replace_case(path: Path, start_marker: str, end_marker: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return

    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1

    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: function closing brace not found in {path}")

    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )

    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def update_descriptions(root: Path, partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = {x["source_name"]: x for x in plan["abilities"]}
    path = root / "res/text/ability_descriptions.json"
    bank = json.loads(path.read_text(encoding="utf-8"))
    messages = {x["id"]: x for x in bank["messages"]}

    for name in CHANGED:
        row = rows[name]
        msg_id = f"pl_msg_00000612_{row['id']:05d}"
        lines = textwrap.wrap(
            re.sub(r"\s+", " ", row["exact_effect"].strip()),
            width=31,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = lines[-1].rstrip(" .") + "..."
        value = [line + ("\n" if i < len(lines) - 1 else "") for i, line in enumerate(lines)]
        if msg_id in messages:
            messages[msg_id]["en_US"] = value
        else:
            bank["messages"].append({"id": msg_id, "en_US": value})

    path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_accuracy_family(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE) {
        evaStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_UNAWARE) {
        evaStages = 0;
    }
    if (Battler_Ability(battleCtx, attacker) == ABILITY_KEEN_EYE
        && evaStages < 0) {
        evaStages = 0;
    }
    if (MON_IS_IDENTIFIED(defender) && evaStages < 0) {
""",
        "Keen Eye positive-evasion bypass",
    )

    insert_before_in_function(
        path,
        "static int BattleControllerPlayer_CheckMoveHitAccuracy(BattleSystem *battleSys, BattleContext *battleCtx, int attacker, int defender, int move)",
        """    if (NO_CLOUD_NINE) {
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_KEEN_EYE) {
        hitRate = hitRate * 120 / 100;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_INNER_FOCUS
        && move == MOVE_FOCUS_BLAST
        && hitRate < 90) {
        hitRate = 90;
    }

""",
        "Keen Eye and Inner Focus accuracy extensions",
    )


def patch_inner_focus_intimidate(root: Path) -> None:
    path = root / "res/battle/scripts/subscripts/subscript_intimidate.s"
    insert_before_once(
        path,
        """    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_ATTACK_DOWN_1_STAGE
""",
        """    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_INNER_FOCUS, _038
""",
        "Inner Focus Intimidate immunity",
    )


def patch_hyper_cutter_crit(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """        + criticalStage
        + (attackerAbility == ABILITY_SUPER_LUCK)
""",
        """        + criticalStage
        + (attackerAbility == ABILITY_SUPER_LUCK)
        + (attackerAbility == ABILITY_HYPER_CUTTER
            && (MOVE_DATA(battleCtx->moveCur).flags & MOVE_FLAG_MAKES_CONTACT))
""",
        "Hyper Cutter contact critical stage",
    )


def patch_status_residual_immunity(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_POISON) && battleCtx->battleMons[battler].curHP) {
""",
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_POISON)
                && battleCtx->battleMons[battler].curHP
                && Battler_Ability(battleCtx, battler) != ABILITY_TOXIC_BOOST) {
""",
        "Toxic Boost regular-poison residual immunity",
    )

    replace_once(
        path,
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_TOXIC) && battleCtx->battleMons[battler].curHP) {
""",
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_TOXIC)
                && battleCtx->battleMons[battler].curHP
                && Battler_Ability(battleCtx, battler) != ABILITY_TOXIC_BOOST) {
""",
        "Toxic Boost toxic residual immunity",
    )

    replace_once(
        path,
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_BURN) && battleCtx->battleMons[battler].curHP) {
""",
        """            if ((battleCtx->battleMons[battler].status & MON_CONDITION_BURN)
                && battleCtx->battleMons[battler].curHP
                && Battler_Ability(battleCtx, battler) != ABILITY_FLARE_BOOST) {
""",
        "Flare Boost burn residual immunity",
    )


def patch_damage_extensions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_REFRIGERATE
""",
        """    if (attackerParams.ability == ABILITY_ILLUSION
        && battleCtx->mercuryIllusionActive[attacker]
        && movePower) {
        movePower = movePower * 13 / 10;
    }

    if (attackerParams.ability == ABILITY_LONG_REACH
        && moveClass == CLASS_PHYSICAL
        && (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) == FALSE
        && movePower) {
        movePower = movePower * 12 / 10;
    }

""",
        "Illusion and Long Reach safe damage extensions",
    )


def patch_weak_armor(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replacement = """    case ABILITY_WEAK_ARMOR:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_WEAK_ARMOR) == TRUE
            && DEFENDING_MON.curHP
            && DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken) {
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]--;
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE] > MIN_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]--;
            }

            if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] += 2;
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] > MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] = MAX_STAT_STAGE;
                }
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] += 2;
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] > MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK] = MAX_STAT_STAGE;
                }
            }
            if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] < MAX_STAT_STAGE) {
                DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] += 2;
                if (DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] > MAX_STAT_STAGE) {
                    DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED] = MAX_STAT_STAGE;
                }
            }

            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;

"""
    replace_case(
        path,
        "    case ABILITY_WEAK_ARMOR:\n",
        "    case ABILITY_CURSED_BODY:\n",
        replacement,
        "Weak Armor ER stat package",
    )


def validate(root: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    intimidate = (root / "res/battle/scripts/subscripts/subscript_intimidate.s").read_text(encoding="utf-8")
    return {
        "keen_eye_ignores_positive_evasion": "ABILITY_KEEN_EYE" in controller and "evaStages < 0" in controller,
        "keen_eye_accuracy_1_2": "hitRate = hitRate * 120 / 100;" in controller,
        "inner_focus_focus_blast_90": "ABILITY_INNER_FOCUS" in controller and "MOVE_FOCUS_BLAST" in controller and "hitRate = 90;" in controller,
        "inner_focus_intimidate_immunity": "ABILITY_INNER_FOCUS, _038" in intimidate,
        "hyper_cutter_contact_crit_stage": "ABILITY_HYPER_CUTTER" in lib and "MOVE_FLAG_MAKES_CONTACT" in lib,
        "toxic_boost_poison_residual_immunity": controller.count("ABILITY_TOXIC_BOOST") >= 2,
        "flare_boost_burn_residual_immunity": "ABILITY_FLARE_BOOST" in controller,
        "illusion_active_damage_1_3": "mercuryIllusionActive[attacker]" in lib and "movePower = movePower * 13 / 10;" in lib,
        "long_reach_natural_noncontact_1_2": "attackerParams.ability == ABILITY_LONG_REACH" in lib and "(MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) == FALSE" in lib,
        "weak_armor_full_stat_package": all(x in lib for x in (
            "case ABILITY_WEAK_ARMOR:",
            "BATTLE_STAT_DEFENSE]--",
            "BATTLE_STAT_SP_DEFENSE]--",
            "BATTLE_STAT_ATTACK] += 2",
            "BATTLE_STAT_SP_ATTACK] += 2",
            "BATTLE_STAT_SPEED] += 2",
        )),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--report", type=Path, default=Path("mr10b3-safe-precision-offense-status.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_accuracy_family(root)
    patch_inner_focus_intimidate(root)
    patch_hyper_cutter_crit(root)
    patch_status_residual_immunity(root)
    patch_damage_extensions(root)
    patch_weak_armor(root)
    update_descriptions(root, args.partition.resolve())

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10B3_SAFE_PRECISION_OFFENSE_STATUS",
        "status": status,
        "implemented_or_overridden": list(CHANGED),
        "count": len(CHANGED),
        "depends_on_held_93": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10B3 validation failed")


if __name__ == "__main__":
    main()
