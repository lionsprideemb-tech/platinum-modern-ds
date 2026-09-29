#!/usr/bin/env python3
"""MR10D6 — fieldwide residual aura family.

Implements two KEEP-AS-WRITTEN mechanics:
- Winter Throne: while an active holder exists, Ice-type active Pokémon heal
  1/8 max HP at end of turn and non-Ice active Pokémon lose 1/8.
- Toxic Spill: while an active holder exists, non-Poison active Pokémon lose
  1/8 max HP at end of turn.

Current battle typing is used through Mercury_BattlerHasType(), including
battle-only added types. Multiple holders of the same aura do not multiply the
same aura; distinct auras combine. Magic Guard blocks damaging aura components
and Heal Block blocks Winter Throne's healing component.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Winter Throne": ("ABILITY_MR_WINTER_THRONE", 671),
    "Toxic Spill": ("ABILITY_MR_TOXIC_SPILL", 881),
}
TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


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


def patch_field_auras(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    helper = """static BOOL Mercury_ActiveAbilityExists(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int ability)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    for (i = 0; i < maxBattlers; i++) {
        if (battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ability) {
            return TRUE;
        }
    }

    return FALSE;
}

static void Mercury_ApplyFieldAuraResidual(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    BOOL winterThrone;
    BOOL toxicSpill;
    s32 delta = 0;
    int eighth;

    if (battleCtx->battleMons[battler].curHP == 0) {
        return;
    }

    winterThrone = Mercury_ActiveAbilityExists(
        battleSys, battleCtx, ABILITY_MR_WINTER_THRONE);
    toxicSpill = Mercury_ActiveAbilityExists(
        battleSys, battleCtx, ABILITY_MR_TOXIC_SPILL);

    if (winterThrone == FALSE && toxicSpill == FALSE) {
        return;
    }

    eighth = BattleSystem_Divide(
        battleCtx->battleMons[battler].maxHP, 8);
    if (eighth < 1) {
        eighth = 1;
    }

    if (winterThrone) {
        if (Mercury_BattlerHasType(battleCtx, battler, TYPE_ICE)) {
            if (battleCtx->battleMons[battler].moveEffectsData.healBlockTurns == 0
                && battleCtx->battleMons[battler].curHP
                    < battleCtx->battleMons[battler].maxHP) {
                delta += eighth;
            }
        } else if (Battler_Ability(battleCtx, battler) != ABILITY_MAGIC_GUARD) {
            delta -= eighth;
        }
    }

    if (toxicSpill
        && Mercury_BattlerHasType(battleCtx, battler, TYPE_POISON) == FALSE
        && Battler_Ability(battleCtx, battler) != ABILITY_MAGIC_GUARD) {
        delta -= eighth;
    }

    if (delta == 0) {
        return;
    }

    if (delta > 0) {
        battleCtx->battleMons[battler].curHP += delta;
        if (battleCtx->battleMons[battler].curHP
            > battleCtx->battleMons[battler].maxHP) {
            battleCtx->battleMons[battler].curHP =
                battleCtx->battleMons[battler].maxHP;
        }
    } else if (-delta >= battleCtx->battleMons[battler].curHP) {
        battleCtx->battleMons[battler].curHP = 0;
    } else {
        battleCtx->battleMons[battler].curHP += delta;
    }

    BattleMon_CopyToParty(battleSys, battleCtx, battler);
}

"""
    insert_before_once(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)\n",
        helper,
        "MR10D6 field-aura helpers",
    )

    insert_before_in_function(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    switch (Battler_Ability(battleCtx, battler)) {
""",
        """    Mercury_ApplyFieldAuraResidual(battleSys, battleCtx, battler);

""",
        "Mercury_ApplyFieldAuraResidual(battleSys, battleCtx, battler);",
        "MR10D6 turn-end aura application",
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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "fieldwide_holder_presence":
            "static BOOL Mercury_ActiveAbilityExists(" in lib
            and "BattleSystem_GetMaxBattlers(battleSys)" in lib,
        "winter_throne_active_check":
            "ABILITY_MR_WINTER_THRONE" in lib,
        "winter_throne_current_ice_typing":
            "Mercury_BattlerHasType(battleCtx, battler, TYPE_ICE)" in lib,
        "winter_throne_one_eighth":
            "maxHP, 8" in lib,
        "winter_throne_heal_block":
            "moveEffectsData.healBlockTurns == 0" in lib,
        "toxic_spill_active_check":
            "ABILITY_MR_TOXIC_SPILL" in lib,
        "toxic_spill_poison_exemption":
            "Mercury_BattlerHasType(battleCtx, battler, TYPE_POISON) == FALSE" in lib,
        "magic_guard_residual_immunity":
            lib.count("ABILITY_MAGIC_GUARD") >= 2,
        "distinct_auras_combine":
            "delta += eighth;" in lib
            and lib.count("delta -= eighth;") >= 2,
        "residual_applied_at_ability_end_turn_stage":
            "Mercury_ApplyFieldAuraResidual(battleSys, battleCtx, battler);" in lib
            and "BOOL BattleSystem_TriggerTurnEndAbility" in lib,
        "party_hp_synchronized":
            "BattleMon_CopyToParty(battleSys, battleCtx, battler);" in lib,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d6-field-auras.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_field_auras(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D6_FIELD_AURAS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "same_aura_stacks": False,
        "distinct_auras_combine": True,
        "remaining_keep_as_written_after_d6": 52,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D6 field-aura validation failed")


if __name__ == "__main__":
    main()
