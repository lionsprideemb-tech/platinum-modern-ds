#!/usr/bin/env python3
"""MR10B1 — safe Elite Redux canonical scalar/shared-hook overrides.

Applies only already-decided MR09 semantics that do not depend on the 93 held
new-engine-system decisions. This batch intentionally stays on existing MR08
battle hooks and simple extensions.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path


CHANGED = (
    "Hustle",
    "Overgrow",
    "Blaze",
    "Torrent",
    "Swarm",
    "Iron Fist",
    "Normalize",
    "Filter",
    "Solid Rock",
    "Defeatist",
    "Triage",
    "Liquid Voice",
    "Overcoat",
    "Water Compaction",
    "Merciless",
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


def update_description_bank(root: Path, partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = {row["source_name"]: row for row in plan["abilities"]}
    desc_path = root / "res/text/ability_descriptions.json"
    bank = json.loads(desc_path.read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in bank["messages"]}

    for name in CHANGED:
        row = rows[name]
        idx = row["id"]
        msg_id = f"pl_msg_00000612_{idx:05d}"
        effect = re.sub(r"\s+", " ", row["exact_effect"].strip())
        lines = textwrap.wrap(effect, width=31, break_long_words=False, break_on_hyphens=False)
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = lines[-1].rstrip(" .") + "..."
        value = [line + ("\n" if i < len(lines) - 1 else "") for i, line in enumerate(lines)]
        if msg_id in by_id:
            by_id[msg_id]["en_US"] = value
        else:
            bank["messages"].append({"id": msg_id, "en_US": value})

    desc_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_hustle(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    controller = root / "src/battle/battle_controller_player.c"

    replace_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUSTLE) {
        attackStat = attackStat * 150 / 100;
    }
""",
        """    if (attackerParams.ability == ABILITY_HUSTLE && movePower) {
        movePower = movePower * 14 / 10;
    }
""",
        "Hustle 1.4x damaging-move power",
    )

    replace_once(
        controller,
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_HUSTLE && moveClass == CLASS_PHYSICAL) {
        hitRate = hitRate * 80 / 100;
    }
""",
        """    if (Battler_Ability(battleCtx, attacker) == ABILITY_HUSTLE) {
        hitRate = hitRate * 90 / 100;
    }
""",
        "Hustle 0.9x all-move accuracy",
    )


def patch_starters_iron_fist_normalize(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    starter_old = """    if (moveType == TYPE_GRASS
        && attackerParams.ability == ABILITY_OVERGROW
        && attackerParams.curHP <= (attackerParams.maxHP / 3)) {
        movePower = movePower * 150 / 100;
    }
    if (moveType == TYPE_FIRE
        && attackerParams.ability == ABILITY_BLAZE
        && attackerParams.curHP <= (attackerParams.maxHP / 3)) {
        movePower = movePower * 150 / 100;
    }
    if (moveType == TYPE_WATER
        && attackerParams.ability == ABILITY_TORRENT
        && attackerParams.curHP <= (attackerParams.maxHP / 3)) {
        movePower = movePower * 150 / 100;
    }
    if (moveType == TYPE_BUG
        && attackerParams.ability == ABILITY_SWARM
        && attackerParams.curHP <= (attackerParams.maxHP / 3)) {
        movePower = movePower * 150 / 100;
    }
"""
    starter_new = """    if (moveType == TYPE_GRASS && attackerParams.ability == ABILITY_OVERGROW) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
    if (moveType == TYPE_FIRE && attackerParams.ability == ABILITY_BLAZE) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
    if (moveType == TYPE_WATER && attackerParams.ability == ABILITY_TORRENT) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
    if (moveType == TYPE_BUG && attackerParams.ability == ABILITY_SWARM) {
        movePower = movePower * (attackerParams.curHP <= (attackerParams.maxHP / 3) ? 150 : 120) / 100;
    }
"""
    replace_once(path, starter_old, starter_new, "starter always-on 20% / low-HP 50% family")

    replace_once(
        path,
        """        if (sPunchingMoves[i] == move && attackerParams.ability == ABILITY_IRON_FIST) {
            movePower = movePower * 12 / 10;
            break;
        }
""",
        """        if (sPunchingMoves[i] == move && attackerParams.ability == ABILITY_IRON_FIST) {
            movePower = movePower * 13 / 10;
            break;
        }
""",
        "Iron Fist 1.3x",
    )

    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
""",
        """    if (attackerParams.ability == ABILITY_NORMALIZE
        && move != MOVE_STRUGGLE
        && movePower) {
        movePower = movePower * 11 / 10;
    }

""",
        "Normalize 1.1x power",
    )


def patch_defensive_scalars(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 3, 4);
            }
""",
        """            if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FILTER) == TRUE
                || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_SOLID_ROCK) == TRUE) {
                damage = BattleSystem_Divide(damage * 65, 100);
            }
""",
        "Filter/Solid Rock 35% reduction",
    )

    replace_once(
        path,
        """    if (attackerParams.ability == ABILITY_DEFEATIST
        && attackerParams.curHP <= attackerParams.maxHP / 2) {
""",
        """    if (attackerParams.ability == ABILITY_DEFEATIST
        && attackerParams.curHP <= attackerParams.maxHP / 3) {
""",
        "Defeatist one-third threshold",
    )

    insert_before_once(
        path,
        """    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
""",
        """    if (moveClass == CLASS_SPECIAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_OVERCOAT) == TRUE) {
        damage = damage * 80 / 100;
    }

    if (moveType == TYPE_WATER
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_WATER_COMPACTION) == TRUE) {
        damage /= 2;
    }

""",
        "Overcoat special reduction / Water Compaction resistance",
    )


def patch_triage_liquid_voice_merciless(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    for old, new, label in (
        ("        battler1Priority += 3;\n", "        battler1Priority += 1;\n", "Triage battler1 +1"),
        ("        battler2Priority += 3;\n", "        battler2Priority += 1;\n", "Triage battler2 +1"),
        ("        priority += 3;\n", "        priority += 1;\n", "Triage helper +1"),
    ):
        replace_once(path, old, new, label)

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_MEGA_LAUNCHER
        && Mercury_MoveIsPulse(move)) {
""",
        """    if (attackerParams.ability == ABILITY_LIQUID_VOICE
        && Mercury_MoveIsSound(move)
        && movePower) {
        movePower = movePower * 12 / 10;
    }

""",
        "Liquid Voice 1.2x sound power",
    )

    replace_once(
        path,
        """    if (((attackerAbility == ABILITY_MERCILESS
                && (battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
""",
        """    if (((attackerAbility == ABILITY_MERCILESS
                && ((battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON)
                    || battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_SPEED]
                        < DEFAULT_STAT_STAGE))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
""",
        "Merciless poisoned-or-lowered-Speed crit",
    )


def validate(root: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    return {
        "hustle_power_1_4": "attackerParams.ability == ABILITY_HUSTLE && movePower" in lib and "movePower = movePower * 14 / 10;" in lib,
        "hustle_accuracy_0_9": "ABILITY_HUSTLE" in controller and "hitRate = hitRate * 90 / 100;" in controller,
        "starter_20_to_50": all(x in lib for x in (
            "ABILITY_OVERGROW", "ABILITY_BLAZE", "ABILITY_TORRENT", "ABILITY_SWARM",
            "? 150 : 120",
        )),
        "iron_fist_1_3": "ABILITY_IRON_FIST" in lib and "movePower = movePower * 13 / 10;" in lib,
        "normalize_1_1": "attackerParams.ability == ABILITY_NORMALIZE" in lib and "movePower = movePower * 11 / 10;" in lib,
        "filter_solid_rock_65": "BattleSystem_Divide(damage * 65, 100)" in lib,
        "defeatist_one_third": "attackerParams.curHP <= attackerParams.maxHP / 3" in lib,
        "triage_plus_one": "battler1Priority += 1;" in lib and "battler2Priority += 1;" in lib and "priority += 1;" in lib,
        "liquid_voice_1_2": "ABILITY_LIQUID_VOICE" in lib and "Mercury_MoveIsSound(move)" in lib and "movePower = movePower * 12 / 10;" in lib,
        "overcoat_special_20": "ABILITY_OVERCOAT" in lib and "damage = damage * 80 / 100;" in lib,
        "water_compaction_half": "ABILITY_WATER_COMPACTION" in lib and "damage /= 2;" in lib,
        "merciless_speed_clause": "BATTLE_STAT_SPEED" in lib and "< DEFAULT_STAT_STAGE" in lib,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--report", type=Path, default=Path("mr10b1-er-safe-scalar-overrides.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_hustle(root)
    patch_starters_iron_fist_normalize(root)
    patch_defensive_scalars(root)
    patch_triage_liquid_voice_merciless(root)
    update_description_bank(root, args.partition.resolve())

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10B1_ER_SAFE_SCALAR_OVERRIDES",
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
        raise SystemExit("MR10B1 validation failed")


if __name__ == "__main__":
    main()
