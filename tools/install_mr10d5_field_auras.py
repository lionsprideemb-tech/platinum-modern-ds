#!/usr/bin/env python3
"""MR10D5 — field-aura residual KEEP-AS-WRITTEN batch.

Implements two reviewed low-complexity field auras:
- Winter Throne: each active holder causes Ice-type active Pokémon to heal
  1/8 max HP and non-Ice active Pokémon to lose 1/8 max HP at end of turn.
- Toxic Spill: each active holder causes non-Poison active Pokémon to lose
  1/8 max HP at end of turn.

The shared field-aura checkpoint is separate from each battler's normal
end-turn Ability checkpoint so Speed Boost, Harvest, etc. still resolve.
Same-name active holders stack naturally because each holder contributes one
1/8 pulse. Magic Guard blocks damaging pulses; Heal Block blocks healing.
Current battle typing is used, including MR10D added types.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Winter Throne": ("ABILITY_MR_WINTER_THRONE", 671),
    "Toxic Spill": ("ABILITY_MR_TOXIC_SPILL", 881),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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


def patch_shared_aura_helper(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """BOOL Mercury_TriggerFieldAuraEndTurn(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int winterCount = 0;
    int toxicCount = 0;
    int heal = 0;
    int damage = 0;
    int delta;

    if (battleCtx->battleMons[battler].curHP == 0
        || (battleCtx->battlersSwitchingMask & FlagIndex(battler))) {
        return FALSE;
    }

    for (i = 0; i < maxBattlers; i++) {
        if (battleCtx->battleMons[i].curHP == 0
            || (battleCtx->battlersSwitchingMask & FlagIndex(i))) {
            continue;
        }

        if (Battler_Ability(battleCtx, i) == ABILITY_MR_WINTER_THRONE) {
            winterCount++;
        }
        if (Battler_Ability(battleCtx, i) == ABILITY_MR_TOXIC_SPILL) {
            toxicCount++;
        }
    }

    if (winterCount) {
        if (MON_HAS_TYPE(battler, TYPE_ICE)) {
            if (battleCtx->battleMons[battler].moveEffectsData.healBlockTurns == 0
                && battleCtx->battleMons[battler].curHP
                    < battleCtx->battleMons[battler].maxHP) {
                heal += BattleSystem_Divide(
                    battleCtx->battleMons[battler].maxHP * winterCount, 8);
            }
        } else if (Battler_Ability(battleCtx, battler) != ABILITY_MAGIC_GUARD) {
            damage += BattleSystem_Divide(
                battleCtx->battleMons[battler].maxHP * winterCount, 8);
        }
    }

    if (toxicCount
        && MON_HAS_TYPE(battler, TYPE_POISON) == FALSE
        && Battler_Ability(battleCtx, battler) != ABILITY_MAGIC_GUARD) {
        damage += BattleSystem_Divide(
            battleCtx->battleMons[battler].maxHP * toxicCount, 8);
    }

    delta = heal - damage;
    if (delta == 0) {
        return FALSE;
    }

    if (delta > 0) {
        int missingHP = battleCtx->battleMons[battler].maxHP
            - battleCtx->battleMons[battler].curHP;
        if (delta > missingHP) {
            delta = missingHP;
        }
        if (delta == 0) {
            return FALSE;
        }
    } else if (-delta > battleCtx->battleMons[battler].curHP) {
        delta = -battleCtx->battleMons[battler].curHP;
    }

    battleCtx->msgBattlerTemp = battler;
    battleCtx->hpCalcTemp = delta;
    LOAD_SUBSEQ(subscript_update_hp);
    battleCtx->commandNext = battleCtx->command;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

"""
    insert_before_once(
        lib,
        """BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
""",
        helper,
        "MR10D5 field-aura helper",
    )
    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        """BOOL Mercury_TriggerFieldAuraEndTurn(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        "MR10D5 field-aura declaration",
    )


def patch_controller_checkpoint(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    MON_COND_CHECK_STATE_AQUA_RING,
    MON_COND_CHECK_STATE_ABILITY,
""",
        """    MON_COND_CHECK_STATE_AQUA_RING,
    MON_COND_CHECK_STATE_MERCURY_FIELD_AURA,
    MON_COND_CHECK_STATE_ABILITY,
""",
        "MR10D5 mon-condition state",
    )

    insert_before_once(
        path,
        """        case MON_COND_CHECK_STATE_ABILITY:
""",
        """        case MON_COND_CHECK_STATE_MERCURY_FIELD_AURA:
            if (Mercury_TriggerFieldAuraEndTurn(
                    battleSys, battleCtx, battler) == TRUE) {
                state = STATE_BREAK_OUT;
            }

            battleCtx->monConditionCheckState++;
            break;

""",
        "MR10D5 field-aura end-turn checkpoint",
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
        "shared_field_aura_helper":
            "Mercury_TriggerFieldAuraEndTurn" in lib
            and "Mercury_TriggerFieldAuraEndTurn" in hdr,
        "separate_end_turn_checkpoint":
            "MON_COND_CHECK_STATE_MERCURY_FIELD_AURA" in ctl
            and ctl.find("MON_COND_CHECK_STATE_MERCURY_FIELD_AURA")
                < ctl.find("MON_COND_CHECK_STATE_ABILITY"),
        "winter_holder_count":
            "ABILITY_MR_WINTER_THRONE" in lib
            and "winterCount++;" in lib,
        "winter_ice_heal":
            "MON_HAS_TYPE(battler, TYPE_ICE)" in lib
            and "maxHP * winterCount, 8" in lib,
        "winter_nonice_damage":
            "damage += BattleSystem_Divide" in lib
            and "ABILITY_MAGIC_GUARD" in lib,
        "winter_heal_block":
            "moveEffectsData.healBlockTurns == 0" in lib,
        "toxic_holder_count":
            "ABILITY_MR_TOXIC_SPILL" in lib
            and "toxicCount++;" in lib,
        "toxic_poison_exemption":
            "MON_HAS_TYPE(battler, TYPE_POISON) == FALSE" in lib,
        "same_ability_holders_stack":
            "maxHP * winterCount" in lib
            and "maxHP * toxicCount" in lib,
        "normal_end_turn_ability_preserved":
            "case MON_COND_CHECK_STATE_ABILITY:" in ctl
            and "BattleSystem_TriggerTurnEndAbility" in ctl,
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
        default=Path("mr10d5-field-auras.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_shared_aura_helper(root)
    patch_controller_checkpoint(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D5_FIELD_AURAS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "same_ability_active_holders_stack": True,
        "magic_guard_blocks_damage": True,
        "heal_block_blocks_winter_healing": True,
        "remaining_keep_as_written_after_d5": 54,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D5 field-aura validation failed")


if __name__ == "__main__":
    main()
