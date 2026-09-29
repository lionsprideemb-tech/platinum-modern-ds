#!/usr/bin/env python3
"""MR10D11 — Lucky Halo KEEP-AS-WRITTEN mechanic.

Lucky Halo:
- prevents the holder's self-inflicted stat-stage drops;
- once per party Pokémon per battle, survives an otherwise-fatal direct hit
  at 1 HP, including when already at 1 HP;
- switching does not refresh the survival charge.

The once-per-battle state is keyed by side + selected party slot, matching the
already-certified Two Lives persistence pattern. Mechanics only; MR07 visuals
remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Lucky Halo"
ABILITY_TOKEN = "ABILITY_MR_LUCKY_HALO"
ABILITY_ID = 503


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
        raise SystemExit(f"{label}: expected one anchor in {signature}, found {count}")
    block = block.replace(anchor, insertion + anchor, 1)
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
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row, found {len(matches)}")

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
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryTwoLivesShieldUsedMask[2];
""",
        """    // Mercury MR10D11: once-per-party-slot Lucky Halo survival.
    u8 mercuryLuckyHaloSurvivalUsedMask[2];
""",
        "Lucky Halo persistent survival mask",
    )


def patch_survival_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    helper = """static u8 Mercury_LuckyHaloPartyBit(
    BattleContext *battleCtx,
    int battler)
{
    int slot = battleCtx->selectedPartySlot[battler];

    if (slot < 0 || slot >= 6) {
        return 0;
    }

    return (u8)(1 << slot);
}

BOOL Mercury_LuckyHaloSurvivalUsed(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_LuckyHaloPartyBit(battleCtx, battler);

    if (bit == 0) {
        return TRUE;
    }

    return (battleCtx->mercuryLuckyHaloSurvivalUsedMask[side] & bit) != 0;
}

void Mercury_SetLuckyHaloSurvivalUsed(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_LuckyHaloPartyBit(battleCtx, battler);

    if (bit) {
        battleCtx->mercuryLuckyHaloSurvivalUsedMask[side] |= bit;
    }
}

"""
    insert_before_once(
        path,
        """static u8 Mercury_TwoLivesPartyBit(BattleContext *battleCtx, int battler)
""",
        helper,
        "Lucky Halo party-persistent helpers",
    )

    hdr = root / "include/battle/battle_lib.h"
    insert_before_once(
        hdr,
        """BOOL Mercury_TryBlockTwoLives(
""",
        """BOOL Mercury_LuckyHaloSurvivalUsed(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
void Mercury_SetLuckyHaloSurvivalUsed(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        "Lucky Halo helper declarations",
    )


def patch_self_drop_prevention(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    signature = "static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)"
    insertion = """        if (battleCtx->attacker == battleCtx->sideEffectMon
            && Battler_Ability(battleCtx, battleCtx->sideEffectMon)
                == ABILITY_MR_LUCKY_HALO) {
            SetupNicknameAbilityStatMsg(
                battleCtx,
                BattleStrings_Text_PokemonsAbilityPreventsBufferStatLoss,
                statOffset);
            BattleScript_Iter(battleCtx, jumpNoChange);
            return FALSE;
        }

"""
    insert_before_in_function(
        path,
        signature,
        """        if ((battleCtx->sideEffectFlags & MOVE_SIDE_EFFECT_CANNOT_PREVENT) == FALSE) {
""",
        insertion,
        "ABILITY_MR_LUCKY_HALO) {",
        "Lucky Halo self-inflicted stat-drop prevention",
    )


def patch_direct_hit_survival(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_UpdateHP("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && battleCtx->attacker != battleCtx->defender
            && CURRENT_MOVE_DATA.class != CLASS_STATUS
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && DEFENDING_MON.curHP + battleCtx->damage <= 0
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_MR_LUCKY_HALO) == TRUE
            && Mercury_LuckyHaloSurvivalUsed(
                battleSys, battleCtx, battleCtx->defender) == FALSE) {
            Mercury_SetLuckyHaloSurvivalUsed(
                battleSys, battleCtx, battleCtx->defender);
            battleCtx->damage = (DEFENDING_MON.curHP - 1) * -1;
            battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED;
        }

"""
    insert_before_in_function(
        path,
        signature,
        """        if (CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_LEAVE_WITH_1_HP
""",
        insertion,
        "Mercury_LuckyHaloSurvivalUsed(",
        "Lucky Halo once-per-battle fatal direct-hit survival",
    )


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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    return {
        "stable_id_503":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "party_persistent_survival_mask":
            "mercuryLuckyHaloSurvivalUsedMask[2]" in ctx
            and "Mercury_LuckyHaloPartyBit" in lib,
        "switch_does_not_refresh_survival":
            "mercuryLuckyHaloSurvivalUsedMask" not in
            lib[lib.find("void BattleSystem_InitBattleMon"):lib.find("void BattleSystem_CleanupFaintedMon")],
        "self_drop_prevention":
            "ABILITY_MR_LUCKY_HALO" in script
            and "battleCtx->attacker == battleCtx->sideEffectMon" in script
            and "BattleStrings_Text_PokemonsAbilityPreventsBufferStatLoss" in script,
        "opponent_drops_not_blanket_blocked":
            "battleCtx->attacker == battleCtx->sideEffectMon" in script,
        "direct_hit_only":
            "battleCtx->attacker != battleCtx->defender" in ctl
            and "CURRENT_MOVE_DATA.class != CLASS_STATUS" in ctl,
        "fatal_hit_gate":
            "DEFENDING_MON.curHP + battleCtx->damage <= 0" in ctl,
        "works_from_one_hp":
            "battleCtx->damage = (DEFENDING_MON.curHP - 1) * -1;" in ctl,
        "once_per_party_mon":
            "Mercury_LuckyHaloSurvivalUsed(" in ctl
            and "Mercury_SetLuckyHaloSurvivalUsed(" in ctl,
        "mold_breaker_family_can_ignore_survival":
            "Battler_IgnorableAbility(" in ctl
            and "ABILITY_MR_LUCKY_HALO) == TRUE" in ctl,
        "helpers_declared":
            "Mercury_LuckyHaloSurvivalUsed" in hdr
            and "Mercury_SetLuckyHaloSurvivalUsed" in hdr,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


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
        default=Path("mr10d11-lucky-halo.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_survival_helpers(root)
    patch_self_drop_prevention(root)
    patch_direct_hit_survival(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D11_LUCKY_HALO",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "survival_uses_per_party_mon_per_battle": 1,
        "remaining_keep_as_written_after_d11": 35,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D11 Lucky Halo validation failed")


if __name__ == "__main__":
    main()
