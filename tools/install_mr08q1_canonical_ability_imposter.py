#!/usr/bin/env python3
"""MR08Q1 — canonical Imposter pass.

Adds current-mainline Imposter by reusing Platinum's native Transform command.
The switch-in check targets the opposing slot directly across first, falls back
to the other live opponent in doubles, and refuses transformed, substitute, or
semi-invulnerable targets. A per-battler handled mask prevents re-entry loops.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_IMPOSTER",)
EXPECTED_IDS = {"ABILITY_IMPOSTER": 150}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
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


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08Q1: one Imposter attempt per active battler entry.
    u8 mercuryImposterHandledMask;

""",
        "Imposter handled state",
    )


def patch_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    script_path = scripts / "subscript_mercury_imposter.s"
    script_path.write_text(
        """#include "macros/btlcmd.inc"


_000:
    // {0} has {1}!
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_TEMP
    Wait
    WaitButtonABTime 30
    Transform
    // {0} transformed into {1}!
    PrintMessage BattleStrings_Text_PokemonTransformedIntoPokemon_AllyAlly, TAG_NICKNAME_POKE, BTLSCR_ATTACKER, BTLSCR_DEFENDER
    Wait
    WaitButtonABTime 30
    UpdateVarFromVar OPCODE_SET, BTLVAR_ATTACKER, BTLVAR_ATTACKER_TEMP
    UpdateVarFromVar OPCODE_SET, BTLVAR_DEFENDER, BTLVAR_DEFENDER_TEMP
    End
""",
        encoding="utf-8",
    )

    order = scripts / "sub_seq.order"
    insert_before_once(
        order,
        "subscript_giratina_form_change\n",
        "subscript_mercury_imposter\n",
        "Imposter subscript order",
    )

    meson = scripts / "meson.build"
    insert_before_once(
        meson,
        "    'subscript_giratina_form_change.s',\n",
        "    'subscript_mercury_imposter.s',\n",
        "Imposter subscript build list",
    )


def patch_switch_in(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    SWITCH_IN_CHECK_STATE_FIELD_WEATHER = SWITCH_IN_CHECK_STATE_START,
    SWITCH_IN_CHECK_STATE_TRACE,
""",
        """    SWITCH_IN_CHECK_STATE_FIELD_WEATHER = SWITCH_IN_CHECK_STATE_START,
    SWITCH_IN_CHECK_STATE_IMPOSTER,
    SWITCH_IN_CHECK_STATE_TRACE,
""",
        "Imposter switch-in state enum",
    )

    insert_before_once(
        path,
        """        case SWITCH_IN_CHECK_STATE_TRACE:
""",
        """        case SWITCH_IN_CHECK_STATE_IMPOSTER:
            for (i = 0; i < maxBattlers; i++) {
                int target;

                battler = battleCtx->monSpeedOrder[i];

                if (battleCtx->battleMons[battler].curHP == 0
                    || Battler_Ability(battleCtx, battler) != ABILITY_IMPOSTER
                    || (battleCtx->mercuryImposterHandledMask & FlagIndex(battler))) {
                    continue;
                }

                battleCtx->mercuryImposterHandledMask |= FlagIndex(battler);

                target = battler ^ 1;
                if (target >= maxBattlers || battleCtx->battleMons[target].curHP == 0) {
                    target = battler ^ 3;
                }

                if (target >= maxBattlers
                    || battleCtx->battleMons[target].curHP == 0
                    || (battleCtx->battleMons[target].statusVolatile
                        & VOLATILE_CONDITION_SUBSTITUTE)
                    || (battleCtx->battleMons[target].statusVolatile
                        & VOLATILE_CONDITION_TRANSFORM)
                    || (battleCtx->battleMons[target].moveEffectsMask
                        & MOVE_EFFECT_SEMI_INVULNERABLE)) {
                    continue;
                }

                battleCtx->attackerTemp = battleCtx->attacker;
                battleCtx->defenderTemp = battleCtx->defender;
                battleCtx->attacker = battler;
                battleCtx->defender = target;
                battleCtx->msgBattlerTemp = battler;
                battleCtx->msgTemp = battler;
                battleCtx->msgAbilityTemp = ABILITY_IMPOSTER;
                subscript = subscript_mercury_imposter;
                result = SWITCH_IN_CHECK_RESULT_BREAK;
                break;
            }

            if (i == maxBattlers) {
                battleCtx->switchInCheckState++;
            }
            break;

""",
        "Imposter switch-in handler",
    )


def patch_state_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """    battleCtx->mercuryFaintHandledMask &= ~FlagIndex(battler);
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        """    battleCtx->mercuryFaintHandledMask &= ~FlagIndex(battler);
    battleCtx->mercuryImposterHandledMask &= ~FlagIndex(battler);
    battleCtx->battleMons[battler].type1 = Pokemon_GetValue(mon, MON_DATA_TYPE_1, NULL);
""",
        "Imposter switch-in reset",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (root / "res/battle/scripts/subscripts/subscript_mercury_imposter.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "imposter_state":
            "mercuryImposterHandledMask" in ctx
            and "SWITCH_IN_CHECK_STATE_IMPOSTER" in lib,
        "direct_opponent_targeting":
            "target = battler ^ 1;" in lib
            and "target = battler ^ 3;" in lib,
        "invalid_target_guards":
            "VOLATILE_CONDITION_SUBSTITUTE" in lib
            and "VOLATILE_CONDITION_TRANSFORM" in lib
            and "MOVE_EFFECT_SEMI_INVULNERABLE" in lib,
        "native_transform_reuse":
            "subscript_mercury_imposter" in order
            and "    Transform" in script,
        "battle_cursor_restore":
            "BTLVAR_ATTACKER_TEMP" in script
            and "BTLVAR_DEFENDER_TEMP" in script,
        "entry_reset":
            "mercuryImposterHandledMask &= ~FlagIndex(battler)" in lib,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08q1-canonical-ability-imposter.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_subscript(root)
    patch_switch_in(root)
    patch_state_reset(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08Q1_CANONICAL_ABILITY_IMPOSTER",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 160,
        "remaining_modern_canonical_mechanics": 27,
        "policy": "Official/current-mainline mechanics; form-changing families remain in later passes.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08Q1 validation failed")


if __name__ == "__main__":
    main()
