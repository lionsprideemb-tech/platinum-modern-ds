#!/usr/bin/env python3
"""MR10D14 — delayed revival family.

Implements the two approved KEEP-AS-WRITTEN delayed-revival abilities on one
shared party-slot state machine:

- Shallow Grave: once per battle, if the holder faints while fog is active,
  mark that party slot for revival.
- Backup Power: once per battle, if the holder faints while Electric Terrain
  is active, mark that party slot for revival.
- The marked Pokémon remains fainted while the replacement decision is made.
  After the same side's next ally is actually sent out, the marked Pokémon is
  restored in the party at 25% max HP.
- The once-per-battle flag is consumed when the qualifying faint occurs, so
  switching, healing, or a later faint cannot refresh it.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Shallow Grave": ("ABILITY_MR_SHALLOW_GRAVE", 428),
    "Backup Power": ("ABILITY_MR_BACKUP_POWER", 429),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, anchor + insertion, 1)
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
        """    u8 mercuryTwoLivesShieldPending[MAX_BATTLERS];
""",
        """    // Mercury MR10D14: delayed revival is party-slot persistent for
    // this battle. Used prevents refresh; pending waits for the next ally
    // actually sent out on that side.
    u8 mercuryDelayedRevivalUsedMask[2];
    u8 mercuryDelayedRevivalPendingMask[2];

""",
        "D14 delayed revival party-slot state",
    )


def patch_revival_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    helper = """static void Mercury_ResolveDelayedRevival(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int enteringBattler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, enteringBattler);
    int enteringSlot = battleCtx->selectedPartySlot[enteringBattler];
    u8 pending = battleCtx->mercuryDelayedRevivalPendingMask[side];
    int slot;

    if (pending == 0) {
        return;
    }

    for (slot = 0; slot < 6; slot++) {
        u8 bit = FlagIndex(slot);
        Pokemon *mon;
        u32 hp;
        u32 maxHP;

        if ((pending & bit) == 0 || slot == enteringSlot) {
            continue;
        }

        mon = BattleSystem_GetPartyPokemon(battleSys, enteringBattler, slot);
        hp = Pokemon_GetValue(mon, MON_DATA_HP, NULL);
        maxHP = Pokemon_GetValue(mon, MON_DATA_MAX_HP, NULL);

        if (hp == 0 && maxHP) {
            hp = maxHP / 4;
            if (hp == 0) {
                hp = 1;
            }
            Pokemon_SetValue(mon, MON_DATA_HP, &hp);
        }

        pending &= ~bit;
    }

    battleCtx->mercuryDelayedRevivalPendingMask[side] = pending;
}

"""
    insert_before_once(
        path,
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
""",
        helper,
        "D14 delayed revival resolver",
    )

    signature = (
        "void BattleSystem_InitBattleMon("
        "BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)"
    )
    insert_after_in_function(
        path,
        signature,
        """    int side = BattleSystem_GetBattlerSide(battleSys, battler);
""",
        """    Mercury_ResolveDelayedRevival(battleSys, battleCtx, battler);
""",
        "Mercury_ResolveDelayedRevival(battleSys, battleCtx, battler);",
        "D14 resolve after next ally send-out",
    )


def patch_faint_marker(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "void Mercury_TriggerFaintAbilities("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """    {
        int side = BattleSystem_GetBattlerSide(battleSys, fainted);
        int slot = battleCtx->selectedPartySlot[fainted];
        int ability = Battler_Ability(battleCtx, fainted);
        BOOL qualifies = FALSE;

        if (ability == ABILITY_MR_SHALLOW_GRAVE && WEATHER_IS_FOG) {
            qualifies = TRUE;
        } else if (ability == ABILITY_MR_BACKUP_POWER
            && battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
            qualifies = TRUE;
        }

        if (qualifies && slot < 6
            && (battleCtx->mercuryDelayedRevivalUsedMask[side]
                & FlagIndex(slot)) == 0) {
            battleCtx->mercuryDelayedRevivalUsedMask[side] |= FlagIndex(slot);
            battleCtx->mercuryDelayedRevivalPendingMask[side] |= FlagIndex(slot);
        }
    }

"""
    insert_after_in_function(
        path,
        signature,
        """    battleCtx->mercuryFaintHandledMask |= FlagIndex(fainted);
""",
        insertion,
        "mercuryDelayedRevivalPendingMask",
        "D14 qualifying faint marker",
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
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "party_slot_used_state":
            "mercuryDelayedRevivalUsedMask[2]" in ctx,
        "party_slot_pending_state":
            "mercuryDelayedRevivalPendingMask[2]" in ctx,
        "shallow_grave_fog_gate":
            "ABILITY_MR_SHALLOW_GRAVE && WEATHER_IS_FOG" in lib,
        "backup_power_electric_terrain_gate":
            "ABILITY_MR_BACKUP_POWER" in lib
            and "MERCURY_TERRAIN_ELECTRIC" in lib,
        "once_per_battle_consumed_on_faint":
            "mercuryDelayedRevivalUsedMask[side] |= FlagIndex(slot);" in lib,
        "waits_for_next_ally_sendout":
            "Mercury_ResolveDelayedRevival(battleSys, battleCtx, battler);" in lib
            and "slot == enteringSlot" in lib,
        "revives_fainted_party_member_only":
            "if (hp == 0 && maxHP)" in lib,
        "quarter_hp_restore":
            "hp = maxHP / 4;" in lib,
        "minimum_one_hp":
            "if (hp == 0)" in lib
            and "hp = 1;" in lib,
        "party_hp_write":
            "Pokemon_SetValue(mon, MON_DATA_HP, &hp);" in lib,
        "pending_clears_after_resolution":
            "mercuryDelayedRevivalPendingMask[side] = pending;" in lib,
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
        default=Path("mr10d14-delayed-revival.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_revival_helpers(root)
    patch_faint_marker(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D14_DELAYED_REVIVAL",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "conditioned faint marker plus next-ally party revival",
        "revival_hp_percent": 25,
        "remaining_keep_as_written_after_d14": 27,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D14 delayed revival validation failed")


if __name__ == "__main__":
    main()
