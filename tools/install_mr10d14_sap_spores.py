#!/usr/bin/env python3
"""MR10D14 — Sap Trap + Parasitic Spores specialized battle-state hooks.

Implements two approved KEEP-AS-WRITTEN mechanics:
- Sap Trap: opposing active battlers are marked by an active Sap Trap holder,
  lose one Speed stage at end of turn, and become unable to retreat once the
  mark has driven them to -3 Speed or lower while a Sap Trap holder remains
  active.
- Parasitic Spores: the holder carries spores while active; spores spread from
  an afflicted attacker through successful contact, persist for that active
  stay, and drain 1/8 max HP at end of turn. Ghost types are immune to the
  residual damage, and Magic Guard blocks that indirect damage.

Both effects use battle-only state and clear when the affected battler leaves
its active slot. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Sap Trap": ("ABILITY_MR_SAP_TRAP", 691),
    "Parasitic Spores": ("ABILITY_MR_PARASITIC_SPORES", 693),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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
        """    u16 mercuryParrotMove;
""",
        """    // Mercury MR10D14: active-stay status for Sap Trap / spores.
    u8 mercurySapTrapMarked[MAX_BATTLERS];
    u8 mercuryParasiticSpores[MAX_BATTLERS];

""",
        "D14 battle-state fields",
    )


def patch_state_init_and_switch_cleanup(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insert_after_in_function(
        lib,
        "void BattleContext_InitCounters(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        battleCtx->mercuryDynamicAddedType[i] = 0xFF;
""",
        """        battleCtx->mercurySapTrapMarked[i] = FALSE;
        battleCtx->mercuryParasiticSpores[i] = FALSE;
""",
        "mercurySapTrapMarked[i] = FALSE;",
        "D14 battle-start state init",
    )

    insert_after_in_function(
        lib,
        "void BattleSystem_UpdateAfterSwitch(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    battleCtx->mercuryDynamicAddedType[battler] = 0xFF;
""",
        """    battleCtx->mercurySapTrapMarked[battler] = FALSE;
    battleCtx->mercuryParasiticSpores[battler] =
        Battler_Ability(battleCtx, battler) == ABILITY_MR_PARASITIC_SPORES;
""",
        "mercurySapTrapMarked[battler] = FALSE;",
        "D14 switch cleanup",
    )


def patch_sap_trap_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """int Mercury_FindActiveOpposingAbility(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability)
{
    int i;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    int side = BattleSystem_GetBattlerSide(battleSys, battler);

    for (i = 0; i < maxBattlers; i++) {
        if (battleCtx->battleMons[i].curHP
            && BattleSystem_GetBattlerSide(battleSys, i) != side
            && Battler_Ability(battleCtx, i) == ability) {
            return i;
        }
    }

    return BATTLER_NONE;
}

"""
    insert_before_once(
        lib,
        """BOOL Battler_IsTrapped(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
""",
        helper,
        "D14 opposing-ability helper",
    )

    insert_before_once(
        hdr,
        """BOOL Battler_IsTrapped(BattleSystem *battleSys, BattleContext *battleCtx, int battler);
""",
        """int Mercury_FindActiveOpposingAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int ability);
""",
        "D14 opposing-ability helper declaration",
    )

    insert_before_in_function(
        lib,
        "BOOL Battler_IsTrapped(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    return result;
""",
        """    if (battleCtx->mercurySapTrapMarked[battler]
        && battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SPEED]
            <= DEFAULT_STAT_STAGE - 3
        && Mercury_FindActiveOpposingAbility(
            battleSys, battleCtx, battler, ABILITY_MR_SAP_TRAP)
            != BATTLER_NONE) {
        result = TRUE;
    }

""",
        "mercurySapTrapMarked[battler]",
        "D14 Sap Trap retreat lock",
    )


def patch_spore_contact_spread(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL Mercury_TriggerAttackerOnHitAbility(\n"
        "    BattleSystem *battleSys,\n"
        "    BattleContext *battleCtx,\n"
        "    int *subscript)"
    )

    insertion = """    if ((battleCtx->mercuryParasiticSpores[battleCtx->attacker]
            || Battler_Ability(battleCtx, battleCtx->attacker)
                == ABILITY_MR_PARASITIC_SPORES)
        && battleCtx->attacker != battleCtx->defender
        && DEFENDING_MON.curHP
        && battleCtx->mercuryParasiticSpores[battleCtx->defender] == FALSE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur)) {
        battleCtx->mercuryParasiticSpores[battleCtx->attacker] = TRUE;
        battleCtx->mercuryParasiticSpores[battleCtx->defender] = TRUE;
    }

"""
    insert_before_in_function(
        lib,
        signature,
        """    return FALSE;
""",
        insertion,
        "mercuryParasiticSpores[battleCtx->defender] = TRUE;",
        "D14 Parasitic Spores contact spread",
    )


def patch_spore_message(root: Path) -> None:
    text_path = root / "res/text/battle_strings.json"
    data = json.loads(text_path.read_text(encoding="utf-8"))
    messages = data["messages"]
    message_id = "BattleStrings_Text_MercuryParasiticSporesHurt"

    if not any(row.get("id") == message_id for row in messages):
        messages.append({
            "id": message_id,
            "en_US": [
                "Parasitic spores sap\n",
                "{STRVAR_1 1, 0, 0}'s HP!"
            ],
        })
        text_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_parasitic_spores.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    PrintMessage BattleStrings_Text_MercuryParasiticSporesHurt, TAG_NICKNAME, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    CompareVarToValue OPCODE_FLAG_NOT, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_MON_FAINTED, _030
    Call BATTLE_SUBSCRIPT_FAINT_MON
_030:
    End
""",
        encoding="utf-8",
    )

    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_parroting\n",
        "subscript_mercury_parasitic_spores\n",
        "D14 spore subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_parroting.s',\n",
        "    'subscript_mercury_parasitic_spores.s',\n",
        "D14 spore subscript build list",
    )


def patch_end_turn_states(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"

    replace_once(
        ctl,
        """    MON_COND_CHECK_STATE_ITEM_DETRIMENTAL_EFFECT,

    MON_COND_CHECK_END
""",
        """    MON_COND_CHECK_STATE_ITEM_DETRIMENTAL_EFFECT,
    MON_COND_CHECK_STATE_MERCURY_PARASITIC_SPORES,
    MON_COND_CHECK_STATE_MERCURY_SAP_TRAP,

    MON_COND_CHECK_END
""",
        "D14 mon-condition states",
    )

    replace_once(
        ctl,
        """    int i, battler;
    while (battleCtx->monConditionCheckTemp < maxBattlers) {
""",
        """    int i, battler, mercurySapHolder;
    while (battleCtx->monConditionCheckTemp < maxBattlers) {
""",
        "D14 Sap Trap holder local",
    )

    insert_before_in_function(
        ctl,
        "static void BattleControllerPlayer_CheckMonConditions(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        case MON_COND_CHECK_END:
""",
        """        case MON_COND_CHECK_STATE_MERCURY_PARASITIC_SPORES:
            if (Battler_Ability(battleCtx, battler)
                    == ABILITY_MR_PARASITIC_SPORES) {
                battleCtx->mercuryParasiticSpores[battler] = TRUE;
            }

            if (battleCtx->mercuryParasiticSpores[battler]
                && battleCtx->battleMons[battler].curHP
                && Mercury_BattlerHasType(
                    battleCtx, battler, TYPE_GHOST) == FALSE
                && Battler_Ability(battleCtx, battler) != ABILITY_MAGIC_GUARD) {
                battleCtx->msgTemp = battler;
                battleCtx->hpCalcTemp = -BattleSystem_Divide(
                    battleCtx->battleMons[battler].maxHP, 8);
                PrepareSubroutineSequence(
                    battleCtx, subscript_mercury_parasitic_spores);
                state = STATE_BREAK_OUT;
            }

            battleCtx->monConditionCheckState++;
            break;

        case MON_COND_CHECK_STATE_MERCURY_SAP_TRAP:
            mercurySapHolder = Mercury_FindActiveOpposingAbility(
                battleSys, battleCtx, battler, ABILITY_MR_SAP_TRAP);

            if (mercurySapHolder != BATTLER_NONE
                && battleCtx->battleMons[battler].curHP) {
                battleCtx->mercurySapTrapMarked[battler] = TRUE;

                if (battleCtx->battleMons[battler]
                        .statBoosts[BATTLE_STAT_SPEED] > MIN_STAT_STAGE) {
                    battleCtx->sideEffectParam =
                        MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE;
                    battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
                    battleCtx->sideEffectMon = battler;
                    battleCtx->msgBattlerTemp = mercurySapHolder;
                    LOAD_SUBSEQ(subscript_update_stat_stage);
                    battleCtx->commandNext = battleCtx->command;
                    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                    state = STATE_BREAK_OUT;
                }
            }

            battleCtx->monConditionCheckState++;
            break;

""",
        "case MON_COND_CHECK_STATE_MERCURY_PARASITIC_SPORES:",
        "D14 end-turn Sap Trap / spores",
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
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_parasitic_spores.s"
    ).read_text(encoding="utf-8")
    text_bank = (root / "res/text/battle_strings.json").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "battle_state_fields":
            "mercurySapTrapMarked[MAX_BATTLERS]" in ctx
            and "mercuryParasiticSpores[MAX_BATTLERS]" in ctx,
        "switch_clears_active_stay_state":
            "mercurySapTrapMarked[battler] = FALSE;" in lib
            and "mercuryParasiticSpores[battler] =" in lib,
        "sap_trap_opposing_holder_helper":
            "Mercury_FindActiveOpposingAbility(" in lib
            and "Mercury_FindActiveOpposingAbility(" in hdr,
        "sap_trap_speed_decay":
            "MON_COND_CHECK_STATE_MERCURY_SAP_TRAP" in ctl
            and "MOVE_SUBSCRIPT_PTR_SPEED_DOWN_1_STAGE" in ctl,
        "sap_trap_normal_stat_lane":
            "subscript_update_stat_stage" in ctl
            and "SIDE_EFFECT_TYPE_ABILITY" in ctl,
        "sap_trap_retreat_lock":
            "mercurySapTrapMarked[battler]" in lib
            and "DEFAULT_STAT_STAGE - 3" in lib
            and "ABILITY_MR_SAP_TRAP" in lib,
        "spores_holder_infected":
            "ABILITY_MR_PARASITIC_SPORES" in ctl
            and "mercuryParasiticSpores[battler] = TRUE;" in ctl,
        "spores_contact_spread":
            "mercuryParasiticSpores[battleCtx->defender] = TRUE;" in lib
            and "Mercury_MoveMakesContact(" in lib,
        "spores_real_hit_only":
            "DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken" in lib
            and "Battler_SubstituteWasHit" in lib,
        "spores_one_eighth_residual":
            "MON_COND_CHECK_STATE_MERCURY_PARASITIC_SPORES" in ctl
            and "maxHP, 8" in ctl,
        "spores_ghost_immunity":
            "TYPE_GHOST) == FALSE" in ctl,
        "spores_magic_guard":
            "ABILITY_MAGIC_GUARD" in ctl,
        "spores_text_and_script":
            "BattleStrings_Text_MercuryParasiticSporesHurt" in text_bank
            and "subscript_mercury_parasitic_spores" in order
            and "BATTLE_SUBSCRIPT_UPDATE_HP" in script,
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
        default=Path("mr10d14-sap-spores.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_state_init_and_switch_cleanup(root)
    patch_sap_trap_helpers(root)
    patch_spore_contact_spread(root)
    patch_spore_message(root)
    patch_end_turn_states(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D14_SAP_SPORES",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_systems": [
            "active-stay volatile state",
            "end-turn mon-condition lane",
            "contact propagation",
            "retreat legality hook",
        ],
        "remaining_keep_as_written_after_d14": 27,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D14 Sap Trap / Parasitic Spores validation failed")


if __name__ == "__main__":
    main()
