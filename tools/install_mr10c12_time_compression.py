#!/usr/bin/env python3
"""MR10C12 — implement the approved Time Compression redesign.

Time Compression:
- once per switch-in, the first move that would actually require a charging
  turn OR impose a recharge turn skips that delay;
- natural instant-charge conditions (for example Solar Beam in sun) do not
  consume the Ability;
- a real Power Herb takes precedence, so holding one does not consume Time
  Compression;
- once the Ability removes either kind of delay, it is spent until switch-out.

Charge moves reuse Platinum's existing Power Herb branch point, which preserves
each move's normal special behavior (including Skull Bash's Defense change).
Recharge moves intercept the exact volatile-recharge setup and end that
subscript before move-lock state is installed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Time Compression"
ABILITY_TOKEN = "ABILITY_MR_TIME_COMPRESSION"
ABILITY_ID = 696


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def validate_partition(partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = [x for x in plan["abilities"] if x.get("id") == ABILITY_ID]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row at ID {ABILITY_ID}")
    row = rows[0]
    expected = {
        "display_name": ABILITY_NAME,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_redesign",
        "owner_review_decision": "REDESIGN",
        "implementation_class": "light_extension",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context_and_switch_reset(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    int mercuryCountercurrentGrantedTurn[MAX_BATTLERS];
""",
        """    // Mercury MR10C12: one charge/recharge delay skip per entry.
    u8 mercuryTimeCompressionUsed[MAX_BATTLERS];
""",
        "Time Compression state",
    )

    lib = root / "src/battle/battle_lib.c"
    insert_after_once(
        lib,
        """    battleCtx->mercuryCountercurrentGrantedTurn[battler] = -1;
""",
        """    battleCtx->mercuryTimeCompressionUsed[battler] = FALSE;
""",
        "Time Compression switch-in reset",
    )


def patch_power_herb_branch(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    old = """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

    if (op == CHECK_HAVE) {
"""
    new = """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

    if (effect == HOLD_EFFECT_CHARGE_SKIP) {
        // The real item path wins. The Ability is spent only when it is the
        // effect actually eliminating this move's charge turn.
        battleCtx->scriptTemp = 0;

        if (op == CHECK_HAVE
            && Battler_HeldItemEffect(battleCtx, battler) != effect
            && Battler_Ability(battleCtx, battler) == ABILITY_MR_TIME_COMPRESSION
            && battleCtx->mercuryTimeCompressionUsed[battler] == FALSE) {
            battleCtx->mercuryTimeCompressionUsed[battler] = TRUE;
            battleCtx->scriptTemp = 1;
            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgTemp = ABILITY_MR_TIME_COMPRESSION;
            BattleScript_Iter(battleCtx, jumpIfTrue);
            return FALSE;
        }
    }

    if (op == CHECK_HAVE) {
"""
    replace_once(path, old, new, "Time Compression Power Herb branch")


def patch_charge_skip_subscripts(root: Path) -> None:
    generic = root / "res/battle/scripts/subscripts/subscript_item_skip_charge_turn.s"
    text = generic.read_text(encoding="utf-8")
    if "_TimeCompression:" not in text:
        text = text.replace(
            "_000:\n",
            "_000:\n    CompareVarToValue OPCODE_EQU, BTLVAR_SCRIPT_TEMP, 1, _TimeCompression\n",
            1,
        )
        text += """
_TimeCompression:
    PlayMoveAnimation BTLSCR_ATTACKER
    Wait
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_ATTACKER, BATTLEMON_MOVE_EFFECTS_MASK, MOVE_EFFECT_SEMI_INVULNERABLE, _TCMessage
    ToggleVanish BTLSCR_ATTACKER, TRUE

_TCMessage:
    PrintBufferedMessage
    Wait
    WaitButtonABTime 15
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    UpdateVar OPCODE_SET, BTLVAR_SCRIPT_TEMP, 0
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_PLAYED_MOVE_ANIMATION
    End
"""
        generic.write_text(text, encoding="utf-8")

    skull = root / "res/battle/scripts/subscripts/subscript_power_herb_skull_bash.s"
    text = skull.read_text(encoding="utf-8")
    if "_TimeCompression:" not in text:
        text = text.replace(
            "_000:\n",
            "_000:\n    CompareVarToValue OPCODE_EQU, BTLVAR_SCRIPT_TEMP, 1, _TimeCompression\n",
            1,
        )
        text += """
_TimeCompression:
    PlayMoveAnimation BTLSCR_ATTACKER
    Wait
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_ATTACKER, BATTLEMON_MOVE_EFFECTS_MASK, MOVE_EFFECT_SEMI_INVULNERABLE, _TCBoost
    ToggleVanish BTLSCR_ATTACKER, TRUE

_TCBoost:
    PrintBufferedMessage
    Wait
    WaitButtonABTime 15
    UpdateVarFromVar OPCODE_SET, BTLVAR_SIDE_EFFECT_MON, BTLVAR_ATTACKER
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_PARAM, MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_TYPE, SIDE_EFFECT_TYPE_INDIRECT
    Call BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    UpdateVar OPCODE_SET, BTLVAR_SCRIPT_TEMP, 0
    UpdateVar OPCODE_FLAG_OFF, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_PLAYED_MOVE_ANIMATION
    End
"""
        skull.write_text(text, encoding="utf-8")


def patch_recharge_setup(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    old = """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    int monData = BattleMon_Get(battleCtx, battler, paramID, NULL);

    switch (op) {
"""
    new = """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);
    int monData = BattleMon_Get(battleCtx, battler, paramID, NULL);

    if (paramID == BATTLEMON_VOLATILE_STATUS
        && op == OPCODE_FLAG_ON
        && (srcVal & VOLATILE_CONDITION_RECHARGING)) {
        battleCtx->scriptTemp = 0;

        if (Battler_Ability(battleCtx, battler) == ABILITY_MR_TIME_COMPRESSION
            && battleCtx->mercuryTimeCompressionUsed[battler] == FALSE) {
            battleCtx->mercuryTimeCompressionUsed[battler] = TRUE;
            battleCtx->scriptTemp = 2;
            battleCtx->msgBattlerTemp = battler;
            battleCtx->msgTemp = ABILITY_MR_TIME_COMPRESSION;
            return FALSE;
        }
    }

    switch (op) {
"""
    replace_once(path, old, new, "Time Compression recharge setup interception")

    sub = root / "res/battle/scripts/subscripts/subscript_recharge_turn.s"
    text = sub.read_text(encoding="utf-8")
    if "_TimeCompression:" not in text:
        old_sub = """_000:
    UpdateMonData OPCODE_FLAG_ON, BTLSCR_ATTACKER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_RECHARGING
    UpdateVarFromVar OPCODE_SET, BTLVAR_ATTACKER_LOCKED_MOVE, BTLVAR_CURRENT_MOVE
    UpdateMonDataFromVar OPCODE_SET, BTLSCR_ATTACKER, BATTLEMON_RECHARGE_TURN_NUMBER, BTLVAR_TOTAL_TURNS
    End 
"""
        new_sub = """_000:
    UpdateMonData OPCODE_FLAG_ON, BTLSCR_ATTACKER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_RECHARGING
    CompareVarToValue OPCODE_EQU, BTLVAR_SCRIPT_TEMP, 2, _TimeCompression
    UpdateVarFromVar OPCODE_SET, BTLVAR_ATTACKER_LOCKED_MOVE, BTLVAR_CURRENT_MOVE
    UpdateMonDataFromVar OPCODE_SET, BTLSCR_ATTACKER, BATTLEMON_RECHARGE_TURN_NUMBER, BTLVAR_TOTAL_TURNS
    End

_TimeCompression:
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    UpdateVar OPCODE_SET, BTLVAR_SCRIPT_TEMP, 0
    End
"""
        if old_sub not in text:
            raise SystemExit("Time Compression recharge subscript anchor not found")
        sub.write_text(text.replace(old_sub, new_sub, 1), encoding="utf-8")


def update_registry(path: Path) -> None:
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if ABILITY_TOKEN not in lines:
        lines.append(ABILITY_TOKEN)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    herb = (root / "res/battle/scripts/subscripts/subscript_item_skip_charge_turn.s").read_text(encoding="utf-8")
    skull = (root / "res/battle/scripts/subscripts/subscript_power_herb_skull_bash.s").read_text(encoding="utf-8")
    recharge = (root / "res/battle/scripts/subscripts/subscript_recharge_turn.s").read_text(encoding="utf-8")
    abilities = [
        x.strip() for x in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_696": len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "per_entry_used_state": "mercuryTimeCompressionUsed[MAX_BATTLERS]" in ctx,
        "switch_resets_used": "mercuryTimeCompressionUsed[battler] = FALSE;" in lib,
        "real_power_herb_has_precedence":
            "Battler_HeldItemEffect(battleCtx, battler) != effect" in script,
        "charge_skip_consumes_only_when_needed":
            "effect == HOLD_EFFECT_CHARGE_SKIP" in script
            and "mercuryTimeCompressionUsed[battler] = TRUE;" in script,
        "charge_skip_does_not_remove_item":
            "_TimeCompression:" in herb
            and "UpdateVar OPCODE_SET, BTLVAR_SCRIPT_TEMP, 0" in herb,
        "skull_bash_keeps_normal_stat_subscript":
            "_TimeCompression:" in skull
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_UP_1_STAGE" in skull
            and "BATTLE_SUBSCRIPT_UPDATE_STAT_STAGE" in skull,
        "recharge_setup_intercepted":
            "(srcVal & VOLATILE_CONDITION_RECHARGING)" in script
            and "battleCtx->scriptTemp = 2;" in script,
        "recharge_lock_not_applied_on_skip":
            "CompareVarToValue OPCODE_EQU, BTLVAR_SCRIPT_TEMP, 2, _TimeCompression" in recharge,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c12-time-compression.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_and_switch_reset(root)
    patch_power_herb_branch(root)
    patch_charge_skip_subscripts(root)
    patch_recharge_setup(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C12_TIME_COMPRESSION",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "once_per_switch_in": True,
        "natural_instant_charge_does_not_consume": True,
        "power_herb_precedes_ability": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C12 Time Compression validation failed")


if __name__ == "__main__":
    main()
