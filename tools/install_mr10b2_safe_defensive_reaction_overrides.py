#!/usr/bin/env python3
"""MR10B2 — safe defensive/precision/reaction canonical overrides."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path

CHANGED = (
    "Battle Armor",
    "Shell Armor",
    "Immunity",
    "Levitate",
    "Illuminate",
    "Magma Armor",
    "Big Pecks",
    "Poison Touch",
    "Bad Dreams",
    "Anger Point",
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
        value = [s + ("\n" if i < len(lines) - 1 else "") for i, s in enumerate(lines)]
        if msg_id in messages:
            messages[msg_id]["en_US"] = value
        else:
            bank["messages"].append({"id": msg_id, "en_US": value})
    path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_damage_family(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """    if ((Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_BATTLE_ARMOR) == TRUE
            || Battler_IgnorableAbility(
                battleCtx, attacker, defender, ABILITY_SHELL_ARMOR) == TRUE)
        && movePower) {
        movePower = movePower * 80 / 100;
    }

    if (moveType == TYPE_POISON
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_IMMUNITY) == TRUE) {
        movePower /= 2;
    }

    if ((moveType == TYPE_WATER || moveType == TYPE_ICE)
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MAGMA_ARMOR) == TRUE) {
        movePower = movePower * 70 / 100;
    }

    if (attackerParams.ability == ABILITY_LEVITATE
        && moveType == TYPE_FLYING) {
        movePower = movePower * 125 / 100;
    }

    if (attackerParams.ability == ABILITY_BIG_PECKS
        && Mercury_MoveMakesContact(battleCtx, attacker, move)) {
        movePower = movePower * 13 / 10;
    }

"""
    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
""",
        insertion,
        "MR10B2 damage modifier family",
    )


def patch_big_pecks_drop_rule(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    old = """                    || AbilityBlocksSpecificStatReduction(battleCtx, statOffset, ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE)"""
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Big Pecks legacy Defense-drop immunity: expected one match, found {count}")
    path.write_text(text.replace(old, "", 1), encoding="utf-8")


def patch_accuracy(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    insert_before_once(
        path,
        """    {
        int victoryStars = BattleSystem_CountAbility(
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_ILLUMINATE) {
        hitRate = hitRate * 120 / 100;
    }

""",
        "Illuminate 1.2x accuracy",
    )


def patch_poison_touch(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    text = path.read_text(encoding="utf-8")
    start = text.find("BOOL Mercury_TriggerAttackerOnHitAbility(")
    end = text.find("BOOL BattleSystem_TriggerAbilityOnHit(", start)
    if start < 0 or end < 0:
        raise SystemExit("Poison Touch dispatcher bounds not found")
    block = text[start:end]
    marker = "Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH"
    pos = block.find(marker)
    if pos < 0:
        raise SystemExit("Poison Touch branch not found")
    poison_pos = block.find("*subscript = subscript_poison;", pos)
    toxic_pos = block.find("*subscript = subscript_badly_poison;", pos)
    if poison_pos < 0 or (toxic_pos >= 0 and toxic_pos < poison_pos):
        raise SystemExit("Poison Touch ordinary-poison assignment not found")
    block = (
        block[:poison_pos]
        + "*subscript = subscript_badly_poison;"
        + block[poison_pos + len("*subscript = subscript_poison;"):]
    )
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_bad_dreams(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    replace_once(
        path,
        """                battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * -1, 8);
""",
        """                battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * -1, 4);
""",
        "Bad Dreams quarter-HP damage",
    )


def patch_anger_point(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    case ABILITY_STAMINA:
""",
        """    case ABILITY_ANGER_POINT:
        if (DEFENDING_MON.curHP
            && DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            && (battleCtx->moveStatusFlags & MOVE_STATUS_CRITICAL) == FALSE
            && DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK] < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_ATTACK_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->defender;
            *subscript = subscript_update_stat_stage;
            result = TRUE;
        }
        break;

""",
        "Anger Point non-critical physical-hit Attack boost",
    )


def validate(root: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    return {
        "battle_shell_armor_20_reduction": "ABILITY_BATTLE_ARMOR" in lib and "ABILITY_SHELL_ARMOR" in lib and "movePower = movePower * 80 / 100;" in lib,
        "immunity_poison_half": "ABILITY_IMMUNITY" in lib and "movePower /= 2;" in lib,
        "magma_armor_water_ice_30": "ABILITY_MAGMA_ARMOR" in lib and "movePower = movePower * 70 / 100;" in lib,
        "levitate_flying_25": "ABILITY_LEVITATE" in lib and "movePower = movePower * 125 / 100;" in lib,
        "big_pecks_contact_30": "ABILITY_BIG_PECKS" in lib and "movePower = movePower * 13 / 10;" in lib,
        "big_pecks_drop_immunity_removed": "ABILITY_BIG_PECKS, BATTLE_STAT_DEFENSE" not in script,
        "illuminate_accuracy_1_2": "ABILITY_ILLUMINATE" in controller and "hitRate = hitRate * 120 / 100;" in controller,
        "poison_touch_toxic": "ABILITY_POISON_TOUCH" in lib and "*subscript = subscript_badly_poison;" in lib,
        "bad_dreams_quarter": "ABILITY_BAD_DREAMS" in controller and "maxHP * -1, 4" in controller,
        "anger_point_physical_plus1": "case ABILITY_ANGER_POINT:" in lib and "MOVE_STATUS_CRITICAL" in lib,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--report", type=Path, default=Path("mr10b2-safe-defensive-reaction-overrides.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_damage_family(root)
    patch_big_pecks_drop_rule(root)
    patch_accuracy(root)
    patch_poison_touch(root)
    patch_bad_dreams(root)
    patch_anger_point(root)
    update_descriptions(root, args.partition.resolve())

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10B2_SAFE_DEFENSIVE_REACTION_OVERRIDES",
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
        raise SystemExit("MR10B2 validation failed")


if __name__ == "__main__":
    main()
