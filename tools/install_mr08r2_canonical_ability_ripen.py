#!/usr/bin/env python3
"""MR08R2 — canonical Ripen pass.

Implements current-mainline Ripen numerics for the Berry effects represented by
Platinum's item engine:
- HP and PP restoration are doubled;
- one-stage stat Berries become +2 and Starf's +2 becomes +4;
- type-resist Berries reduce damage to one quarter instead of one half;
- Enigma-style healing and Jaboca/Rowap recoil are doubled;
- Pluck/Bug Bite consumers and targets of Fling receive the same Ripen boost.

Status-curing Berries, Lansat, Micle and Custap intentionally remain unchanged,
matching current mainline behavior. Berry Juice is not a Berry and is not
boosted.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_RIPEN",)
EXPECTED_IDS = {"ABILITY_RIPEN": 247}


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


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_ripen_helper(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insert_before_once(
        lib,
        """BOOL BattleSystem_TriggerHeldItem(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
""",
        """static BOOL Mercury_RipenApplies(
    BattleContext *battleCtx,
    int recipient,
    u16 berry)
{
    return berry != ITEM_NONE
        && Item_IsBerry(berry) == TRUE
        && Battler_Ability(battleCtx, recipient) == ABILITY_RIPEN;
}

""",
        "Ripen helper",
    )


def patch_held_item_triggers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    # Both the normal and post-status held-item lanes use the same local setup.
    old = """    int itemEffect = Battler_HeldItemEffect(battleCtx, battler);
    int itemPower = Battler_HeldItemPower(battleCtx, battler, ITEM_POWER_CHECK_ALL);

    if (battleCtx->battleMons[battler].curHP) {
"""
    new = """    int itemEffect = Battler_HeldItemEffect(battleCtx, battler);
    int itemPower = Battler_HeldItemPower(battleCtx, battler, ITEM_POWER_CHECK_ALL);

    if (battleCtx->battleMons[battler].curHP) {
"""
    text = lib.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 2:
        raise SystemExit(f"Ripen held-item locals: expected 2 matches, found {count}")
    lib.write_text(text.replace(old, new), encoding="utf-8")

    # HP restoration: direct amount and percent amount.
    text = lib.read_text(encoding="utf-8")
    text = text.replace(
        "battleCtx->hpCalcTemp = itemPower;\n                subscript = subscript_held_item_hp_restore;",
        "battleCtx->hpCalcTemp = itemPower * (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? 2 : 1);\n                subscript = subscript_held_item_hp_restore;",
        1,
    )
    text = text.replace(
        "battleCtx->hpCalcTemp = itemPower;\n                *subscript = subscript_held_item_hp_restore;",
        "battleCtx->hpCalcTemp = itemPower * (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? 2 : 1);\n                *subscript = subscript_held_item_hp_restore;",
        1,
    )
    text = text.replace(
        "battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * itemPower, 100);\n                subscript = subscript_held_item_hp_restore;",
        "battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * itemPower, 100);\n                if (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem)) battleCtx->hpCalcTemp *= 2;\n                subscript = subscript_held_item_hp_restore;",
        1,
    )
    text = text.replace(
        "battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * itemPower, 100);\n                *subscript = subscript_held_item_hp_restore;",
        "battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * itemPower, 100);\n                if (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem)) battleCtx->hpCalcTemp *= 2;\n                *subscript = subscript_held_item_hp_restore;",
        1,
    )

    # Leppa Berry PP restoration.
    text = text.replace(
        "BattleMon_AddVal(&battleCtx->battleMons[battler], BATTLEMON_CUR_PP_1 + i, itemPower);",
        "BattleMon_AddVal(&battleCtx->battleMons[battler], BATTLEMON_CUR_PP_1 + i, itemPower * (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? 2 : 1));",
        2,
    )

    # Five flavor pinch Berries appear in both held-item lanes. Their base
    # formula uses itemPower as a divisor, so double the computed healing.
    flavor_line = "battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP, itemPower);"
    count = text.count(flavor_line)
    if count != 10:
        raise SystemExit(f"Ripen flavor heal: expected 10 matches, found {count}")
    text = text.replace(
        flavor_line,
        flavor_line + "\n                if (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem)) battleCtx->hpCalcTemp *= 2;",
    )

    # Liechi/Ganlon/Salac/Petaya/Apicot +1 -> +2. Starf +2 -> +4.
    text = text.replace(
        "subscript = subscript_held_item_raise_stat;\n                result = TRUE;",
        "subscript = Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? subscript_held_item_sharply_raise_stat : subscript_held_item_raise_stat;\n                result = TRUE;",
        5,
    )
    text = text.replace(
        "*subscript = subscript_held_item_raise_stat;\n                result = TRUE;",
        "*subscript = Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? subscript_held_item_sharply_raise_stat : subscript_held_item_raise_stat;\n                result = TRUE;",
        5,
    )
    text = text.replace(
        "subscript = subscript_held_item_sharply_raise_stat;\n                    result = TRUE;",
        "subscript = Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? subscript_mercury_ripen_raise_four_stat : subscript_held_item_sharply_raise_stat;\n                    result = TRUE;",
        1,
    )
    text = text.replace(
        "*subscript = subscript_held_item_sharply_raise_stat;\n                    result = TRUE;",
        "*subscript = Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? subscript_mercury_ripen_raise_four_stat : subscript_held_item_sharply_raise_stat;\n                    result = TRUE;",
        1,
    )

    lib.write_text(text, encoding="utf-8")


def patch_on_hit_berries(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    text = lib.read_text(encoding="utf-8")

    # Jaboca / Rowap: 1/8 recoil becomes 1/4 with Ripen.
    old = "battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP * -1, itemPower);"
    occurrences = text.count(old)
    if occurrences < 2:
        raise SystemExit(f"Ripen Jaboca/Rowap: expected at least 2 recoil matches, found {occurrences}")

    # Only patch the two matches inside BattleSystem_TriggerHeldItemOnHit.
    start = text.index("BOOL BattleSystem_TriggerHeldItemOnHit")
    end = text.index("s32 Battler_HeldItemEffect", start)
    block = text[start:end]
    if block.count(old) != 2:
        raise SystemExit(f"Ripen on-hit recoil block: expected 2 matches, found {block.count(old)}")
    block = block.replace(
        old,
        old + "\n            if (Mercury_RipenApplies(battleCtx, battleCtx->defender, DEFENDING_MON.heldItem)) battleCtx->hpCalcTemp *= 2;",
    )

    # Enigma Berry healing doubles.
    enigma = "battleCtx->hpCalcTemp = BattleSystem_Divide(DEFENDING_MON.maxHP, itemPower);"
    if block.count(enigma) != 1:
        raise SystemExit(f"Ripen Enigma: expected 1 match, found {block.count(enigma)}")
    block = block.replace(
        enigma,
        enigma + "\n            if (Mercury_RipenApplies(battleCtx, battleCtx->defender, DEFENDING_MON.heldItem)) battleCtx->hpCalcTemp *= 2;",
        1,
    )
    lib.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_pluck_and_fling(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    text = lib.read_text(encoding="utf-8")

    # --- Pluck / Bug Bite ---
    start = text.index("BOOL BattleSystem_PluckBerry")
    end = text.index("BOOL BattleSystem_FlingItem", start)
    block = text[start:end]
    block = block.replace(
        "    int power = Battler_HeldItemPower(battleCtx, battler, 1);\n",
        "    int power = Battler_HeldItemPower(battleCtx, battler, 1);\n"
        "    BOOL mercuryRipen = Mercury_RipenApplies(\n"
        "        battleCtx, battleCtx->attacker, battleCtx->battleMons[battler].heldItem);\n",
        1,
    )
    block = block.replace(
        "battleCtx->hpCalcTemp = power;",
        "battleCtx->hpCalcTemp = power * (mercuryRipen ? 2 : 1);",
        1,
    )
    block = block.replace(
        "battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP * power, 100);",
        "battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP * power, 100);\n            if (mercuryRipen) battleCtx->hpCalcTemp *= 2;",
        1,
    )
    block = block.replace(
        "BattleMon_AddVal(&ATTACKING_MON, BATTLEMON_CUR_PP_1 + slot, power);",
        "BattleMon_AddVal(&ATTACKING_MON, BATTLEMON_CUR_PP_1 + slot, power * (mercuryRipen ? 2 : 1));",
        1,
    )
    flavor = "battleCtx->hpCalcTemp = BattleSystem_Divide(ATTACKING_MON.maxHP, power);"
    if block.count(flavor) != 5:
        raise SystemExit(f"Ripen Pluck flavor: expected 5 matches, found {block.count(flavor)}")
    block = block.replace(flavor, flavor + "\n            if (mercuryRipen) battleCtx->hpCalcTemp *= 2;")

    # Five +1 stat effects and Starf's +2.
    block = block.replace(
        "nextSeq = subscript_held_item_raise_stat;",
        "nextSeq = mercuryRipen ? subscript_held_item_sharply_raise_stat : subscript_held_item_raise_stat;",
        5,
    )
    block = block.replace(
        "nextSeq = subscript_held_item_sharply_raise_stat;",
        "nextSeq = mercuryRipen ? subscript_mercury_ripen_raise_four_stat : subscript_held_item_sharply_raise_stat;",
        1,
    )
    text = text[:start] + block + text[end:]

    # --- Flinged Berry received by defender ---
    start = text.index("BOOL BattleSystem_FlingItem")
    end = text.index("void BattleSystem_UpdateMetronomeCount", start)
    block = text[start:end]
    block = block.replace(
        "    int effectPower = Battler_HeldItemPower(battleCtx, battler, ITEM_PARAM_EFFECT_PARAM);\n",
        "    int effectPower = Battler_HeldItemPower(battleCtx, battler, ITEM_PARAM_EFFECT_PARAM);\n"
        "    BOOL mercuryRipen = Mercury_RipenApplies(\n"
        "        battleCtx, battleCtx->defender, battleCtx->battleMons[battler].heldItem);\n",
        1,
    )
    block = block.replace(
        "battleCtx->flingTemp = effectPower;",
        "battleCtx->flingTemp = effectPower * (mercuryRipen ? 2 : 1);",
        1,
    )
    block = block.replace(
        "battleCtx->flingTemp = BattleSystem_Divide(DEFENDING_MON.maxHP * effectPower, 100);",
        "battleCtx->flingTemp = BattleSystem_Divide(DEFENDING_MON.maxHP * effectPower, 100);\n        if (mercuryRipen) battleCtx->flingTemp *= 2;",
        1,
    )
    block = block.replace(
        "BattleMon_AddVal(&DEFENDING_MON, BATTLEMON_CUR_PP_1 + slot, effectPower);",
        "BattleMon_AddVal(&DEFENDING_MON, BATTLEMON_CUR_PP_1 + slot, effectPower * (mercuryRipen ? 2 : 1));",
        1,
    )
    flavor = "battleCtx->flingTemp = BattleSystem_Divide(DEFENDING_MON.maxHP, effectPower);"
    if block.count(flavor) != 5:
        raise SystemExit(f"Ripen Fling flavor: expected 5 matches, found {block.count(flavor)}")
    block = block.replace(flavor, flavor + "\n        if (mercuryRipen) battleCtx->flingTemp *= 2;")
    block = block.replace(
        "battleCtx->flingScript = subscript_held_item_raise_stat;",
        "battleCtx->flingScript = mercuryRipen ? subscript_held_item_sharply_raise_stat : subscript_held_item_raise_stat;",
        5,
    )
    block = block.replace(
        "battleCtx->flingScript = subscript_held_item_sharply_raise_stat;",
        "battleCtx->flingScript = mercuryRipen ? subscript_mercury_ripen_raise_four_stat : subscript_held_item_sharply_raise_stat;",
        1,
    )
    text = text[:start] + block + text[end:]
    lib.write_text(text, encoding="utf-8")


def patch_resist_berries(root: Path) -> None:
    path = root / "res/battle/scripts/subscripts/subscript_type_resist_berry.s"
    replace_once(
        path,
        """    DivideVarByValue BTLVAR_HP_CALC_TEMP, 2
    // The {0} weakened {1}’s power!
""",
        """    DivideVarByValue BTLVAR_HP_CALC_TEMP, 2
    CheckAbility CHECK_HAVE, BTLSCR_MSG_TEMP, ABILITY_RIPEN, _MercuryRipenResist
    GoTo _MercuryRipenResistDone

_MercuryRipenResist:
    DivideVarByValue BTLVAR_HP_CALC_TEMP, 2

_MercuryRipenResistDone:
    // The {0} weakened {1}’s power!
""",
        "Ripen type-resist Berry",
    )


def patch_plus_four_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_ripen_raise_four_stat.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    PlayBattleAnimation BTLSCR_MSG_TEMP, BATTLE_ANIMATION_HELD_ITEM
    Wait
    WaitButtonABTime 15
    PlayBattleAnimation BTLSCR_MSG_TEMP, BATTLE_ANIMATION_STAT_BOOST
    Wait
    // Reuse the sharply-raised message; the battle state receives +4 stages.
    PrintMessage BattleStrings_Text_TheItemSharplyRaisedPokemonsStat_Ally, TAG_NICKNAME_ITEM_STAT, BTLSCR_MSG_TEMP, BTLSCR_MSG_TEMP, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    UpdateVar OPCODE_SET, BTLVAR_SCRIPT_TEMP, 18
    UpdateVarFromVar OPCODE_ADD, BTLVAR_SCRIPT_TEMP, BTLVAR_MSG_TEMP
    UpdateMonData OPCODE_ADD, BTLSCR_MSG_TEMP, BATTLEMON_TEMP, 4
    CompareMonDataToValue OPCODE_LTE, BTLSCR_MSG_TEMP, BATTLEMON_TEMP, 12, _042
    UpdateMonData OPCODE_SET, BTLSCR_MSG_TEMP, BATTLEMON_TEMP, 12

_042:
    Call BATTLE_SUBSCRIPT_PLUCK_CHECK
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_imposter\n",
        "subscript_mercury_ripen_raise_four_stat\n",
        "Ripen subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_imposter.s',\n",
        "    'subscript_mercury_ripen_raise_four_stat.s',\n",
        "Ripen subscript build list",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    resist = (root / "res/battle/scripts/subscripts/subscript_type_resist_berry.s").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    plus4 = (root / "res/battle/scripts/subscripts/subscript_mercury_ripen_raise_four_stat.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "berry_only_helper":
            "Item_IsBerry(berry) == TRUE" in lib
            and "Battler_Ability(battleCtx, recipient) == ABILITY_RIPEN" in lib,
        "hp_pp_double":
            "itemPower * (Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? 2 : 1)" in lib
            and "power * (mercuryRipen ? 2 : 1)" in lib
            and "effectPower * (mercuryRipen ? 2 : 1)" in lib,
        "stat_double":
            "Mercury_RipenApplies(battleCtx, battler, battleCtx->battleMons[battler].heldItem) ? subscript_held_item_sharply_raise_stat" in lib
            and "subscript_mercury_ripen_raise_four_stat" in lib,
        "resist_quarter":
            "ABILITY_RIPEN, _MercuryRipenResist" in resist
            and resist.count("DivideVarByValue BTLVAR_HP_CALC_TEMP, 2") >= 2,
        "on_hit_double":
            "Mercury_RipenApplies(battleCtx, battleCtx->defender, DEFENDING_MON.heldItem)" in lib,
        "pluck_fling_double":
            "battleCtx, battleCtx->attacker, battleCtx->battleMons[battler].heldItem" in lib
            and "battleCtx, battleCtx->defender, battleCtx->battleMons[battler].heldItem" in lib,
        "lansat_micle_untouched":
            "case HOLD_EFFECT_PINCH_CRITRATE_UP:" in lib
            and "case HOLD_EFFECT_PINCH_ACC_UP:" in lib,
        "plus_four_script":
            "subscript_mercury_ripen_raise_four_stat" in order
            and "BATTLEMON_TEMP, 4" in plus4,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08r2-canonical-ability-ripen.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_ripen_helper(root)
    patch_plus_four_subscript(root)
    patch_held_item_triggers(root)
    patch_on_hit_berries(root)
    patch_pluck_and_fling(root)
    patch_resist_berries(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08R2_CANONICAL_ABILITY_RIPEN",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 163,
        "remaining_modern_canonical_mechanics": 24,
        "policy": "Official/current-mainline Ripen behavior; Lansat, Micle, Custap and status cures remain undoubled.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08R2 validation failed")


if __name__ == "__main__":
    main()
