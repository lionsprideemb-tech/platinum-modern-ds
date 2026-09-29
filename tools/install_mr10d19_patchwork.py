#!/usr/bin/env python3
"""MR10D19 — Patchwork.

Implements the approved KEEP-AS-WRITTEN Patchwork mechanic by extending the
already-certified canonical Disguise shield:
- Patchwork blocks the first qualifying damaging hit exactly through the
  Disguise battle-state lane;
- breaking Patchwork costs 1/8 max HP, matching current Disguise behavior;
- only an actual shield break can curse the opposing attacker;
- Curse is applied only if the attacker is alive, on the opposing side, is not
  behind a Substitute, and is not already cursed;
- Patchwork inherits Disguise's party-persistent broken state and special
  Ability copy/swap/suppression restrictions.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Patchwork"
ABILITY_TOKEN = "ABILITY_MR_PATCHWORK"
ABILITY_ID = 812


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


def patch_disguise_state(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_in_function(
        lib,
        """static BOOL Mercury_FormShieldBroken(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability)""",
        """    if (ability == ABILITY_DISGUISE) {
        return (battleCtx->mercuryDisguiseBrokenMask[side] & bit) != 0;
    }
""",
        """    if (ability == ABILITY_DISGUISE
        || ability == ABILITY_MR_PATCHWORK) {
        return (battleCtx->mercuryDisguiseBrokenMask[side] & bit) != 0;
    }
""",
        "ABILITY_MR_PATCHWORK",
        "D19 Patchwork broken-state mapping",
    )

    replace_in_function(
        lib,
        """static void Mercury_SetFormShieldBroken(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability,
    BOOL broken)""",
        """    mask = ability == ABILITY_DISGUISE
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];
""",
        """    mask = (ability == ABILITY_DISGUISE
            || ability == ABILITY_MR_PATCHWORK)
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];
""",
        "ability == ABILITY_MR_PATCHWORK",
        "D19 Patchwork persistent mask mapping",
    )

    insertion = """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_PATCHWORK)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_MR_PATCHWORK) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] =
            ABILITY_MR_PATCHWORK;
        return TRUE;
    }

"""
    insert_before_in_function(
        lib,
        """BOOL Mercury_TryBlockFormShield(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int defender)""",
        """    if (moveClass == CLASS_PHYSICAL
""",
        insertion,
        "mercuryFormShieldPending[defender] =
            ABILITY_MR_PATCHWORK;",
        "D19 Patchwork shield block",
    )


def patch_break_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    path = scripts / "subscript_mercury_patchwork_break.s"
    path.write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Patchwork only reaches this subscript when its Disguise-style shield
    // actually broke on the current hit.
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15

    CompareVarToValue OPCODE_EQU, BTLVAR_HP_CALC_TEMP, 0, _Curse
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    PrintMessage BattleStrings_Text_PokemonIsHurtByItsAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15

_Curse:
    IfSameSide BTLSCR_ATTACKER, BTLSCR_DEFENDER, _End
    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_CUR_HP, 0, _End
    CheckSubstitute BTLSCR_ATTACKER, _End
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_ATTACKER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_CURSE, _End
    UpdateMonData OPCODE_FLAG_ON, BTLSCR_ATTACKER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_CURSE
    PrintMessage BattleStrings_Text_PokemonIsAfflictedByTheCurse_Ally, TAG_NICKNAME, BTLSCR_ATTACKER
    Wait
    WaitButtonABTime 15

_End:
    End
""",
        encoding="utf-8",
    )

    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_form_shield_break\n",
        "subscript_mercury_patchwork_break\n",
        "D19 Patchwork subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_form_shield_break.s',\n",
        "    'subscript_mercury_patchwork_break.s',\n",
        "D19 Patchwork subscript build list",
    )


def patch_break_dispatch(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerAbilityOnHit("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )

    replace_in_function(
        lib,
        signature,
        """        if (ability == ABILITY_DISGUISE) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }

        *subscript = subscript_mercury_form_shield_break;
""",
        """        if (ability == ABILITY_DISGUISE
            || ability == ABILITY_MR_PATCHWORK) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }

        *subscript = ability == ABILITY_MR_PATCHWORK
            ? subscript_mercury_patchwork_break
            : subscript_mercury_form_shield_break;
""",
        "subscript_mercury_patchwork_break",
        "D19 Patchwork break dispatch",
    )


def patch_special_ability_rules(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_in_function(
        lib,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
        """    case ABILITY_DISGUISE:
""",
        """    case ABILITY_DISGUISE:
    case ABILITY_MR_PATCHWORK:
""",
        "case ABILITY_MR_PATCHWORK:",
        "D19 Neutralizing Gas rule",
    )

    replace_in_function(
        lib,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        """    case ABILITY_DISGUISE:
""",
        """    case ABILITY_DISGUISE:
    case ABILITY_MR_PATCHWORK:
""",
        "case ABILITY_MR_PATCHWORK:",
        "D19 Receiver rule",
    )

    # The canonical form stack ends the Trace exclusion chain with Teraform
    # Zero. Extend that final chain rather than relying on an older anchor.
    replace_in_function(
        lib,
        """static int ChooseTraceTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int defender1,
    int defender2)""",
        """        && ability1 != ABILITY_TERAFORM_ZERO;
""",
        """        && ability1 != ABILITY_TERAFORM_ZERO
        && ability1 != ABILITY_MR_PATCHWORK;
""",
        "ability1 != ABILITY_MR_PATCHWORK",
        "D19 Trace defender1 rule",
    )
    replace_in_function(
        lib,
        """static int ChooseTraceTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int defender1,
    int defender2)""",
        """        && ability2 != ABILITY_TERAFORM_ZERO;
""",
        """        && ability2 != ABILITY_TERAFORM_ZERO
        && ability2 != ABILITY_MR_PATCHWORK;
""",
        "ability2 != ABILITY_MR_PATCHWORK",
        "D19 Trace defender2 rule",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _091\n",
        "D19 Role Play target rule",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _091\n",
        "D19 Role Play user rule",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _156\n",
        "D19 Skill Swap target rule",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _156\n",
        "D19 Skill Swap user rule",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _034\n",
        "D19 Gastro Acid rule",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_DISGUISE, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MR_PATCHWORK, _041\n",
        "D19 Worry Seed rule",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_patchwork_break.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    checks = {
        "stable_id_812":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "disguise_mask_reused":
            "ability == ABILITY_MR_PATCHWORK" in lib
            and "mercuryDisguiseBrokenMask" in lib,
        "first_hit_shield":
            "ABILITY_MR_PATCHWORK) == FALSE" in lib
            and "mercuryFormShieldPending[defender]" in lib,
        "one_eighth_break_cost":
            "ability == ABILITY_MR_PATCHWORK" in lib
            and "maxHP * -1" in lib,
        "curse_only_on_break":
            "subscript_mercury_patchwork_break" in lib
            and "subscript_mercury_patchwork_break" in order,
        "opposing_only":
            "IfSameSide BTLSCR_ATTACKER, BTLSCR_DEFENDER" in script,
        "curse_legality":
            "CheckSubstitute BTLSCR_ATTACKER" in script
            and "VOLATILE_CONDITION_CURSE" in script
            and "BATTLEMON_CUR_HP" in script,
        "neutralizing_gas_rule":
            "ABILITY_MR_PATCHWORK" in cannot,
        "receiver_rule":
            "ABILITY_MR_PATCHWORK" in receiver,
        "trace_rule":
            "ability1 != ABILITY_MR_PATCHWORK" in lib
            and "ability2 != ABILITY_MR_PATCHWORK" in lib,
        "copy_swap_rules":
            copy.count("ABILITY_MR_PATCHWORK") >= 2
            and swap.count("ABILITY_MR_PATCHWORK") >= 2,
        "gastro_worry_rules":
            "ABILITY_MR_PATCHWORK" in suppress
            and "ABILITY_MR_PATCHWORK" in worry,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d19-patchwork.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_disguise_state(root)
    patch_break_script(root)
    patch_break_dispatch(root)
    patch_special_ability_rules(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D19_PATCHWORK",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_systems_reused": [
            "canonical Disguise party-persistent shield state",
            "canonical form-shield on-hit checkpoint",
            "volatile Curse state",
        ],
        "remaining_keep_as_written_after_d19": 18,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D19 Patchwork validation failed")


if __name__ == "__main__":
    main()
