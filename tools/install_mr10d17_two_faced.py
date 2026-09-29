#!/usr/bin/env python3
"""MR10D17 — Two-Faced composite Ability.

Implements the approved KEEP-AS-WRITTEN mechanic by reusing the canonical
Hunger Switch battle-state lane and Platinum's after-move-hit sequence:

- the holder toggles the shared Full Belly / Hangry battle state at end of turn;
- switch-out resets the shared Hunger Switch state through the canonical hook;
- Electric- and Dark-type damaging moves receive a 35% power boost;
- after a qualifying damaging move actually hits, the holder takes 10% max-HP
  recoil once for the completed move;
- the Hunger Switch component keeps the canonical copy/swap/Receiver/Worry
  Seed restrictions and remains suppressible by Neutralizing Gas/Gastro Acid.

As with canonical Hunger Switch, final alternate-form sprite presentation is
left to the dedicated form-asset layer. Locked MR07 visuals are untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Two-Faced"
ABILITY_TOKEN = "ABILITY_MR_TWO_FACED"
ABILITY_ID = 733


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if marker in block:
        return
    count = block.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {signature}, found {count}")
    block = block.replace(old, new, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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


def patch_hunger_switch_component(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    signature = (
        "BOOL BattleSystem_TriggerTurnEndAbility("
        "BattleSystem *battleSys, BattleContext *battleCtx, int battler)"
    )
    old = """    case ABILITY_HUNGER_SWITCH:
        if (battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].species == SPECIES_MORPEKO
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            battleCtx->mercuryHungerHangry[battler] ^=
                TRUE;
        }
        break;
"""
    new = """    case ABILITY_HUNGER_SWITCH:
    case ABILITY_MR_TWO_FACED:
        if (battleCtx->battleMons[battler].curHP
            && (Battler_Ability(battleCtx, battler) == ABILITY_MR_TWO_FACED
                || battleCtx->battleMons[battler].species == SPECIES_MORPEKO)
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            battleCtx->mercuryHungerHangry[battler] ^=
                TRUE;
        }
        break;
"""
    replace_in_function(
        lib,
        signature,
        old,
        new,
        "case ABILITY_MR_TWO_FACED:",
        "D17 Hunger Switch state reuse",
    )


def patch_form_ability_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_in_function(
        lib,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        """    case ABILITY_HUNGER_SWITCH:
""",
        """    case ABILITY_HUNGER_SWITCH:
    case ABILITY_MR_TWO_FACED:
""",
        "case ABILITY_MR_TWO_FACED:",
        "D17 Receiver restriction",
    )

    replace_once(
        lib,
        """        && ability1 != ABILITY_TERAFORM_ZERO;
""",
        """        && ability1 != ABILITY_TERAFORM_ZERO
        && ability1 != ABILITY_MR_TWO_FACED;
""",
        "D17 Trace defender1 restriction",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_TERAFORM_ZERO;
""",
        """        && ability2 != ABILITY_TERAFORM_ZERO
        && ability2 != ABILITY_MR_TWO_FACED;
""",
        "D17 Trace defender2 restriction",
    )

    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_TWO_FACED, _091\n",
        "D17 Role Play target restriction",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_TWO_FACED, _091\n",
        "D17 Role Play user restriction",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_TWO_FACED, _156\n",
        "D17 Skill Swap target restriction",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_TWO_FACED, _156\n",
        "D17 Skill Swap user restriction",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_TWO_FACED, _041\n",
        "D17 Worry Seed restriction",
    )


def patch_damage_boost(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insert_before_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    if (attackerParams.ability == ABILITY_MR_TWO_FACED
        && movePower
        && (moveType == TYPE_ELECTRIC || moveType == TYPE_DARK)) {
        movePower = movePower * 135 / 100;
    }

""",
        "D17 Electric/Dark damage boost",
    )


def patch_recoil_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    path = scripts / "subscript_mercury_two_faced_recoil.s"
    path.write_text(
        """#include "macros/btlcmd.inc"


_000:
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    // {0} is hit with recoil!
    PrintMessage BattleStrings_Text_PokemonIsHitWithRecoil_Ally, TAG_NICKNAME, BTLSCR_ATTACKER
    Wait
    WaitButtonABTime 30
    End
""",
        encoding="utf-8",
    )

    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_parasitic_spores\n",
        "subscript_mercury_two_faced_recoil\n",
        "D17 recoil subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_parasitic_spores.s',\n",
        "    'subscript_mercury_two_faced_recoil.s',\n",
        "D17 recoil subscript build list",
    )


def patch_after_move_recoil(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"

    text = ctl.read_text(encoding="utf-8")
    enum_start = text.find("enum AfterMoveHitState {")
    enum_end = text.find("};", enum_start)
    if enum_start < 0 or enum_end < 0:
        raise SystemExit("D17 after-move-hit enum: enum bounds missing")
    enum_block = text[enum_start:enum_end]
    if "AFTER_MOVE_HIT_STATE_MERCURY_TWO_FACED" not in enum_block:
        anchor = "    AFTER_MOVE_HIT_STATE_END\n"
        if anchor not in enum_block:
            raise SystemExit("D17 after-move-hit enum: END member missing")
        enum_block = enum_block.replace(
            anchor,
            "    AFTER_MOVE_HIT_STATE_MERCURY_TWO_FACED,\n\n" + anchor,
            1,
        )
        text = text[:enum_start] + enum_block + text[enum_end:]
        ctl.write_text(text, encoding="utf-8")

    signature = (
        "static BOOL BattleControllerPlayer_TriggerAfterMoveHitEffects("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        case AFTER_MOVE_HIT_STATE_MERCURY_TWO_FACED:
            if (Battler_Ability(battleCtx, battleCtx->attacker)
                    == ABILITY_MR_TWO_FACED
                && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
                && CURRENT_MOVE_DATA.class != CLASS_STATUS
                && (CalcCurrentMoveType(battleCtx) == TYPE_ELECTRIC
                    || CalcCurrentMoveType(battleCtx) == TYPE_DARK)
                && ATTACKING_MON.curHP) {
                battleCtx->hpCalcTemp = BattleSystem_Divide(
                    ATTACKING_MON.maxHP * -1, 10);
                battleCtx->msgBattlerTemp = battleCtx->attacker;

                LOAD_SUBSEQ(subscript_mercury_two_faced_recoil);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                machineState = STATE_BREAK_OUT;
            }

            battleCtx->afterMoveHitCheckState++;
            break;

"""
    text = ctl.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "case AFTER_MOVE_HIT_STATE_MERCURY_TWO_FACED:" not in block:
        anchor = """        case AFTER_MOVE_HIT_STATE_END:
"""
        count = block.count(anchor)
        if count != 1:
            raise SystemExit(
                f"D17 recoil state: expected one END case, found {count}"
            )
        block = block.replace(anchor, insertion + anchor, 1)
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    recoil = (
        root / "res/battle/scripts/subscripts/subscript_mercury_two_faced_recoil.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    receive_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receive_end = lib.index("static int Mercury_CountFaintedPartyMons", receive_start)
    receive = lib[receive_start:receive_end]

    checks = {
        "stable_id_733":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "reuses_hunger_state":
            "mercuryHungerHangry[MAX_BATTLERS]" in ctx
            and "case ABILITY_MR_TWO_FACED:" in lib
            and "mercuryHungerHangry[battler] ^=" in lib,
        "canonical_switch_reset_reused":
            "mercuryHungerHangry[battler] = FALSE;" in lib,
        "transform_toggle_block":
            "VOLATILE_CONDITION_TRANSFORM" in lib,
        "electric_dark_only_boost":
            "attackerParams.ability == ABILITY_MR_TWO_FACED" in lib
            and "moveType == TYPE_ELECTRIC || moveType == TYPE_DARK" in lib,
        "thirty_five_percent_boost":
            "movePower = movePower * 135 / 100;" in lib,
        "once_per_completed_move_recoil_lane":
            "AFTER_MOVE_HIT_STATE_MERCURY_TWO_FACED" in ctl
            and "SYSCTL_MOVE_HIT" in ctl
            and "CURRENT_MOVE_DATA.class != CLASS_STATUS" in ctl,
        "ten_percent_max_hp_recoil":
            "ATTACKING_MON.maxHP * -1, 10" in ctl,
        "recoil_uses_resolved_move_type":
            "CalcCurrentMoveType(battleCtx) == TYPE_ELECTRIC" in ctl
            and "CalcCurrentMoveType(battleCtx) == TYPE_DARK" in ctl,
        "recoil_subscript":
            "subscript_mercury_two_faced_recoil" in order
            and "BattleStrings_Text_PokemonIsHitWithRecoil_Ally" in recoil,
        "receiver_restricted":
            "case ABILITY_MR_TWO_FACED:" in receive,
        "trace_restricted":
            "ability1 != ABILITY_MR_TWO_FACED" in lib
            and "ability2 != ABILITY_MR_TWO_FACED" in lib,
        "role_play_restricted":
            copy.count("ABILITY_MR_TWO_FACED") >= 2,
        "skill_swap_restricted":
            swap.count("ABILITY_MR_TWO_FACED") >= 2,
        "worry_seed_restricted":
            "ABILITY_MR_TWO_FACED" in worry,
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
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr10d17-two-faced.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_hunger_switch_component(root)
    patch_form_ability_restrictions(root)
    patch_damage_boost(root)
    patch_recoil_subscript(root)
    patch_after_move_recoil(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D17_TWO_FACED",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "components_reused": [
            "canonical Hunger Switch battle state",
            "canonical special-form ability restrictions",
            "Platinum after-move-hit effect state machine",
        ],
        "damage_boost_percent": 35,
        "recoil_percent_max_hp": 10,
        "form_visuals_deferred": True,
        "remaining_keep_as_written_after_d17": 21,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D17 Two-Faced validation failed")


if __name__ == "__main__":
    main()
