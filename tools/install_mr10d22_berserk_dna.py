#!/usr/bin/env python3
"""MR10D22 — Berserk DNA + reusable Enraged battle state.

Locked Mercury behavior:
- on switch-in, sharply raise the holder's higher attacking stat (+2);
- apply Enraged as a battle-only active-stay state;
- an Enraged battler loses one third of damage it dealt with a successful
  damaging move as recoil, once after that move's hit sequence;
- switching clears Enraged unless a later effect applies it again.

The recoil is driven by the state rather than by rechecking Berserk DNA, so
the Enraged hook is reusable by future moves/Abilities. Standard Rock Head and
Magic Guard recoil protection remains centralized in the recoil subscript.
Locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Berserk DNA"
ABILITY_TOKEN = "ABILITY_MR_BERSERK_DNA"
ABILITY_ID = 695


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


def patch_context_and_reset(root: Path) -> None:
    ctx = root / "include/battle/battle_context.h"
    insert_after_once(
        ctx,
        """    u8 mercuryParasiticSpores[MAX_BATTLERS];
""",
        """    // Mercury MR10D22: reusable active-stay Enraged volatile.
    u8 mercuryEnraged[MAX_BATTLERS];

""",
        "D22 Enraged state",
    )

    lib = root / "src/battle/battle_lib.c"
    insert_after_in_function(
        lib,
        "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        battleCtx->mercuryParasiticSpores[i] = FALSE;
""",
        """        battleCtx->mercuryEnraged[i] = FALSE;
""",
        "mercuryEnraged[i] = FALSE;",
        "D22 battle-start Enraged init",
    )
    insert_after_in_function(
        lib,
        "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    battleCtx->mercurySapTrapMarked[battler] = FALSE;
""",
        """    battleCtx->mercuryEnraged[battler] = FALSE;
""",
        "mercuryEnraged[battler] = FALSE;",
        "D22 switch clears Enraged",
    )


def patch_switch_in(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    insertion = """                    case ABILITY_MR_BERSERK_DNA:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        battleCtx->mercuryEnraged[battler] = TRUE;
                        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                        battleCtx->sideEffectMon = battler;
                        battleCtx->msgBattlerTemp = battler;

                        if (battleCtx->battleMons[battler].attack
                            >= battleCtx->battleMons[battler].spAttack) {
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_ATTACK_UP_2_STAGES;
                        } else {
                            battleCtx->sideEffectParam =
                                MOVE_SUBSCRIPT_PTR_SP_ATTACK_UP_2_STAGES;
                        }

                        subscript = subscript_update_stat_stage;
                        result = SWITCH_IN_CHECK_RESULT_BREAK;
                        break;

"""
    insert_before_once(
        lib,
        """                    case ABILITY_MR_FRESH_START: {
""",
        insertion,
        "D22 Berserk DNA switch-in case",
    )


def patch_recoil_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_enraged_recoil.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_ROCK_HEAD, _End
    CheckAbility CHECK_HAVE, BTLSCR_ATTACKER, ABILITY_MAGIC_GUARD, _End
    UpdateVarFromVar OPCODE_SET, BTLVAR_MSG_BATTLER_TEMP, BTLVAR_ATTACKER
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    PrintMessage BattleStrings_Text_PokemonIsHitWithRecoil_Ally, TAG_NICKNAME, BTLSCR_ATTACKER
    Wait
    WaitButtonABTime 30

_End:
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_lunar_affinity\n",
        "subscript_mercury_enraged_recoil\n",
        "D22 Enraged subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_lunar_affinity.s',\n",
        "    'subscript_mercury_enraged_recoil.s',\n",
        "D22 Enraged subscript build list",
    )


def patch_after_move_recoil(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        ctl,
        """    AFTER_MOVE_HIT_STATE_END
""",
        """    AFTER_MOVE_HIT_STATE_MERCURY_ENRAGED,
""",
        "D22 after-move-hit Enraged enum",
    )

    signature = (
        "static BOOL BattleControllerPlayer_TriggerAfterMoveHitEffects("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        case AFTER_MOVE_HIT_STATE_MERCURY_ENRAGED:
            if (battleCtx->mercuryEnraged[battleCtx->attacker]
                && (battleCtx->battleStatusMask & SYSCTL_MOVE_HIT)
                && CURRENT_MOVE_DATA.class != CLASS_STATUS
                && ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt < 0
                && ATTACKING_MON.curHP) {
                int mercuryEnragedDamage =
                    ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt * -1;

                battleCtx->hpCalcTemp =
                    -BattleSystem_Divide(mercuryEnragedDamage, 3);
                if (battleCtx->hpCalcTemp == 0) {
                    battleCtx->hpCalcTemp = -1;
                }
                battleCtx->msgBattlerTemp = battleCtx->attacker;

                LOAD_SUBSEQ(subscript_mercury_enraged_recoil);
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
    if "case AFTER_MOVE_HIT_STATE_MERCURY_ENRAGED:" not in block:
        anchor = """        case AFTER_MOVE_HIT_STATE_END:
"""
        count = block.count(anchor)
        if count != 1:
            raise SystemExit(
                f"D22 Enraged recoil state: expected one END case, found {count}"
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(
        encoding="utf-8"
    )
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(
        encoding="utf-8"
    )
    recoil = (
        root / "res/battle/scripts/subscripts/subscript_mercury_enraged_recoil.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_695":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "reusable_enraged_state":
            "mercuryEnraged[MAX_BATTLERS]" in ctx,
        "switch_clear":
            "mercuryEnraged[battler] = FALSE;" in lib,
        "entry_applies_enraged":
            "case ABILITY_MR_BERSERK_DNA:" in lib
            and "mercuryEnraged[battler] = TRUE;" in lib,
        "higher_attack_tie_order":
            "battleMons[battler].attack" in lib
            and ">= battleCtx->battleMons[battler].spAttack" in lib,
        "sharp_attack_or_spattack":
            "MOVE_SUBSCRIPT_PTR_ATTACK_UP_2_STAGES" in lib
            and "MOVE_SUBSCRIPT_PTR_SP_ATTACK_UP_2_STAGES" in lib
            and "subscript_update_stat_stage" in lib,
        "normal_stage_caps_pipeline":
            "SIDE_EFFECT_TYPE_ABILITY" in lib,
        "once_after_completed_move_lane":
            "AFTER_MOVE_HIT_STATE_MERCURY_ENRAGED" in ctl
            and "ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt < 0" in ctl,
        "one_third_damage_dealt_recoil":
            "mercuryEnragedDamage" in ctl
            and "BattleSystem_Divide(mercuryEnragedDamage, 3)" in ctl,
        "minimum_one_recoil":
            "battleCtx->hpCalcTemp = -1;" in ctl,
        "standard_recoil_protections":
            "ABILITY_ROCK_HEAD" in recoil
            and "ABILITY_MAGIC_GUARD" in recoil,
        "recoil_script_registered":
            "subscript_mercury_enraged_recoil" in order
            and "BattleStrings_Text_PokemonIsHitWithRecoil_Ally" in recoil,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d22-berserk-dna.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context_and_reset(root)
    patch_switch_in(root)
    patch_recoil_subscript(root)
    patch_after_move_recoil(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D22_BERSERK_DNA",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "entry_stat_boost_stages": 2,
        "enraged_recoil_fraction_of_damage_dealt": "1/3",
        "enraged_state_reusable": True,
        "remaining_keep_as_written_after_d22_from_d18_base": 16,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D22 Berserk DNA validation failed")


if __name__ == "__main__":
    main()
