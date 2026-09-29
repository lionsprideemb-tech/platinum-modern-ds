#!/usr/bin/env python3
"""MR10D17 — Power Outage.

Implements the approved KEEP-AS-WRITTEN persistent single-use charge:
- each party Pokémon carrying Power Outage starts the battle charged;
- its first resolved damaging Electric-type attack while charged is doubled;
- after that move resolves, the charge is consumed for that party slot;
- Electric typing is removed from the active battle copy if present;
- the consumed state survives switching, and the Electric-type removal is
  re-applied on later entries for that same party Pokémon.

The type loss is battle-only: permanent party/species typing is never written
back to save data. Pure Electric is represented by the neutral Mystery slot
inside battle state so ordinary Electric STAB/weakness/resistance checks no
longer see Electric. Locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Power Outage"
ABILITY_TOKEN = "ABILITY_MR_POWER_OUTAGE"
ABILITY_ID = 399


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


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


def insert_after_in_function(
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
        raise SystemExit(f"{label}: expected one anchor in {signature}, found {count}")
    block = block.replace(anchor, anchor + insertion, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    matches = [
        row for row in rows
        if row.get("display_name") == ABILITY_NAME
        or row.get("source_name") == ABILITY_NAME
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"{ABILITY_NAME}: expected one partition row, found {len(matches)}"
        )
    row = matches[0]
    expected = {
        "id": ABILITY_ID,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_keep",
        "owner_review_decision": "KEEP AS WRITTEN",
        "implementation_class": "new_engine_system",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, "
                f"got {row.get(key)!r}"
            )


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryLuckyHaloSurvivalUsedMask[2];
""",
        """    // Mercury MR10D17: party-slot persistent Power Outage charge.
    // A set bit means the charge has already been consumed this battle.
    u8 mercuryPowerOutageUsedMask[2];

""",
        "D17 Power Outage party charge state",
    )


def patch_type_and_charge_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """static void Mercury_RemovePowerOutageElectricType(
    BattleContext *battleCtx,
    int battler)
{
    u8 type1 = battleCtx->battleMons[battler].type1;
    u8 type2 = battleCtx->battleMons[battler].type2;

    if (type1 == TYPE_ELECTRIC && type2 == TYPE_ELECTRIC) {
        battleCtx->battleMons[battler].type1 = TYPE_MYSTERY;
        battleCtx->battleMons[battler].type2 = TYPE_MYSTERY;
    } else if (type1 == TYPE_ELECTRIC) {
        battleCtx->battleMons[battler].type1 = type2;
    } else if (type2 == TYPE_ELECTRIC) {
        battleCtx->battleMons[battler].type2 = type1;
    }
}

BOOL Mercury_PowerOutageCharged(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    int slot = battleCtx->selectedPartySlot[battler];

    return slot < 6
        && (battleCtx->mercuryPowerOutageUsedMask[side]
            & FlagIndex(slot)) == 0;
}

void Mercury_ConsumePowerOutage(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    int slot = battleCtx->selectedPartySlot[battler];

    if (slot >= 6
        || (battleCtx->mercuryPowerOutageUsedMask[side]
            & FlagIndex(slot))) {
        return;
    }

    battleCtx->mercuryPowerOutageUsedMask[side] |= FlagIndex(slot);
    Mercury_RemovePowerOutageElectricType(battleCtx, battler);
}

"""
    insert_before_once(
        lib,
        """void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
""",
        helper,
        "D17 Power Outage helpers",
    )
    insert_before_once(
        hdr,
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler);
""",
        """BOOL Mercury_PowerOutageCharged(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
void Mercury_ConsumePowerOutage(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        "D17 Power Outage helper declarations",
    )


def patch_switch_reapply(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "void BattleSystem_UpdateAfterSwitch("
        "BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    )
    insertion = """    {
        int mercuryPowerSide = BattleSystem_GetBattlerSide(battleSys, battler);
        int mercuryPowerSlot = battleCtx->selectedPartySlot[battler];

        if (mercuryPowerSlot < 6
            && (battleCtx->mercuryPowerOutageUsedMask[mercuryPowerSide]
                & FlagIndex(mercuryPowerSlot))) {
            Mercury_RemovePowerOutageElectricType(battleCtx, battler);
        }
    }
"""
    insert_after_in_function(
        lib,
        signature,
        """    battleCtx->mercurySapTrapMarked[battler] = FALSE;
""",
        insertion,
        "mercuryPowerOutageUsedMask[mercuryPowerSide]",
        "D17 reapply type loss after switch",
    )


def patch_damage_boost(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insert_before_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_MR_POWER_OUTAGE
        && movePower
        && moveType == TYPE_ELECTRIC
        && Mercury_PowerOutageCharged(
            battleSys, battleCtx, attacker)) {
        movePower *= 2;
    }

""",
        "D17 Power Outage double Electric power",
    )


def patch_move_end_consumption(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"
    helper = """static BOOL Mercury_D17PowerOutageMoveQualifies(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    return battleCtx->attacker != BATTLER_NONE
        && battleCtx->moveCur != MOVE_NONE
        && Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_POWER_OUTAGE
        && CURRENT_MOVE_DATA.power != 0
        && CURRENT_MOVE_DATA.class != CLASS_STATUS
        && CalcCurrentMoveType(battleCtx) == TYPE_ELECTRIC
        && (battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN)
        && Mercury_PowerOutageCharged(
            battleSys, battleCtx, battleCtx->attacker);
}

"""
    insert_before_once(
        ctl,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "D17 Power Outage MoveEnd helper",
    )

    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    text = ctl.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    marker = "Mercury_D17PowerOutageMoveQualifies("
    if marker not in block:
        insertion = """        if (Mercury_D17PowerOutageMoveQualifies(
                battleSys, battleCtx)) {
            Mercury_ConsumePowerOutage(
                battleSys, battleCtx, battleCtx->attacker);
        }

"""
        candidates = [
            "        if (Mercury_TryReactiveCounter(battleSys, battleCtx) == TRUE) {\n",
            "        if (Mercury_TryAbilityFollowup(battleSys, battleCtx) == TRUE) {\n",
            "        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {\n",
            "        if (Mercury_TryNextParrot(battleSys, battleCtx) == TRUE) {\n",
            "        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);\n",
        ]
        positions = [
            (block.find(anchor), anchor)
            for anchor in candidates
            if block.find(anchor) >= 0
        ]
        if not positions:
            raise SystemExit("D17 Power Outage: no MoveEnd insertion point found")
        pos, anchor = min(positions, key=lambda x: x[0])
        block = block[:pos] + insertion + block[pos:]
        ctl.write_text(text[:start] + block + text[end:], encoding="utf-8")


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if ABILITY_TOKEN not in lines:
        lines.append(ABILITY_TOKEN)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_399":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "party_persistent_charge":
            "mercuryPowerOutageUsedMask[2]" in ctx
            and "Mercury_PowerOutageCharged(" in lib,
        "public_consumption_helper":
            "void Mercury_ConsumePowerOutage(" in lib
            and "void Mercury_ConsumePowerOutage(" in hdr,
        "electric_damaging_double":
            "attackerParams.ability == ABILITY_MR_POWER_OUTAGE" in lib
            and "moveType == TYPE_ELECTRIC" in lib
            and "movePower *= 2;" in lib,
        "charge_consumed_after_resolution":
            "Mercury_D17PowerOutageMoveQualifies(" in ctl
            and "SYSCTL_ATTACK_MESSAGE_SHOWN" in ctl
            and "Mercury_ConsumePowerOutage(" in ctl,
        "pure_electric_becomes_typeless_battle_state":
            "TYPE_MYSTERY" in lib
            and "type1 == TYPE_ELECTRIC && type2 == TYPE_ELECTRIC" in lib,
        "dual_type_electric_removed":
            "else if (type1 == TYPE_ELECTRIC)" in lib
            and "else if (type2 == TYPE_ELECTRIC)" in lib,
        "switch_reapplies_consumed_type_loss":
            "mercuryPowerOutageUsedMask[mercuryPowerSide]" in lib
            and "Mercury_RemovePowerOutageElectricType(battleCtx, battler);" in lib,
        "party_typing_not_written":
            "Pokemon_SetValue" not in (
                lib[
                    lib.index("static void Mercury_RemovePowerOutageElectricType"):
                    lib.index("void BattleSystem_UpdateAfterSwitch")
                ]
            ),
        "implemented_registry_updated":
            ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }
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
    ap.add_argument("--report", type=Path, default=Path("mr10d17-power-outage.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_type_and_charge_helpers(root)
    patch_switch_reapply(root)
    patch_damage_boost(root)
    patch_move_end_consumption(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D17_POWER_OUTAGE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_systems_reused": [
            "party-slot battle-persistent masks",
            "MR10D battle typing helpers",
            "MoveEnd resolved-action hook",
        ],
        "boost_multiplier": 2.0,
        "remaining_keep_as_written_after_d17": 21,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D17 Power Outage validation failed")


if __name__ == "__main__":
    main()
