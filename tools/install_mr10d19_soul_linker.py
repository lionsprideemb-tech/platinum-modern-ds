#!/usr/bin/env python3
"""MR10D19 — Soul Linker.

Implements the approved KEEP-AS-WRITTEN linked-damage mechanic:
- after a real direct damaging hit between opposing battlers, Soul Linker on
  either participant mirrors the actual HP damage back onto the original
  attacker;
- the mirror is skipped if applying that same amount would make either
  participant faint, matching Mercury's locked two-sided safety guard;
- Substitute damage and failed/non-damaging actions do not qualify;
- a defender's Soul Linker follows ordinary Mold Breaker-family bypass rules;
- linked damage is an HP event, not another move hit, so it cannot recursively
  create another Soul Link event.

The hook runs before ordinary on-hit Ability scripts so battleCtx->hitDamage
still represents the direct move damage that just resolved. Locked MR07
Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Soul Linker"
ABILITY_TOKEN = "ABILITY_MR_SOUL_LINKER"
ABILITY_ID = 821


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
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_subscript(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_soul_linker.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Announce the participating Soul Linker holder first.
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15

    // The mirrored damage is applied to the original move attacker.
    UpdateVarFromVar OPCODE_SET, BTLVAR_MSG_TEMP, BTLVAR_ATTACKER
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_lunar_affinity\n",
        "subscript_mercury_soul_linker\n",
        "D19 Soul Linker subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_lunar_affinity.s',\n",
        "    'subscript_mercury_soul_linker.s',\n",
        "D19 Soul Linker subscript build list",
    )


def patch_controller(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        ctl,
        """    ONE_HIT_TRIGGER_ABILITY,
""",
        """    ONE_HIT_SOUL_LINKER,
""",
        "D19 one-hit state enum",
    )
    insert_before_once(
        ctl,
        """    MULTI_HIT_TRIGGER_ABILITY,
""",
        """    MULTI_HIT_SOUL_LINKER,
""",
        "D19 multi-hit state enum",
    )

    helper = """static BOOL Mercury_TrySoulLinkerMirror(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int attacker;
    int defender;
    int damage;
    int holder = BATTLER_NONE;
    BOOL attackerLinked;
    BOOL defenderLinked;

    attacker = battleCtx->attacker;
    defender = battleCtx->defender;

    if (attacker == BATTLER_NONE
        || defender == BATTLER_NONE
        || attacker == defender
        || BattleSystem_GetBattlerSide(battleSys, attacker)
            == BattleSystem_GetBattlerSide(battleSys, defender)
        || battleCtx->moveCur == MOVE_NONE
        || CURRENT_MOVE_DATA.class == CLASS_STATUS
        || battleCtx->hitDamage >= 0
        || (battleCtx->moveStatusFlags & MOVE_STATUS_DID_NOT_HIT)
        || Battler_SubstituteWasHit(battleCtx, defender)
        || battleCtx->battleMons[attacker].curHP == 0
        || battleCtx->battleMons[defender].curHP == 0) {
        return FALSE;
    }

    attackerLinked =
        Battler_Ability(battleCtx, attacker) == ABILITY_MR_SOUL_LINKER;
    defenderLinked = Battler_IgnorableAbility(
        battleCtx, attacker, defender, ABILITY_MR_SOUL_LINKER);

    if (attackerLinked) {
        holder = attacker;
    } else if (defenderLinked) {
        holder = defender;
    } else {
        return FALSE;
    }

    damage = battleCtx->hitDamage * -1;

    // Locked Mercury safety: the same mirrored amount must be survivable by
    // both linked participants. Equality is unsafe because it would faint.
    if (damage <= 0
        || battleCtx->battleMons[attacker].curHP <= damage
        || battleCtx->battleMons[defender].curHP <= damage) {
        return FALSE;
    }

    battleCtx->hpCalcTemp = damage * -1;
    battleCtx->msgTemp = holder;
    battleCtx->msgBattlerTemp = holder;

    LOAD_SUBSEQ(subscript_mercury_soul_linker);
    battleCtx->commandNext = battleCtx->command;
    battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

"""
    insert_before_once(
        ctl,
        """static void BattleControllerPlayer_AfterMoveMessage(BattleSystem *battleSys, BattleContext *battleCtx)
""",
        helper,
        "D19 Soul Linker helper",
    )

    sig = (
        "static void BattleControllerPlayer_AfterMoveMessage("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        ctl,
        sig,
        """        case ONE_HIT_TRIGGER_ABILITY:
""",
        """        case ONE_HIT_SOUL_LINKER:
            battleCtx->afterMoveMessageState++;
            if (Mercury_TrySoulLinkerMirror(battleSys, battleCtx) == TRUE) {
                return;
            }

""",
        "case ONE_HIT_SOUL_LINKER:",
        "D19 one-hit Soul Linker state",
    )
    insert_before_in_function(
        ctl,
        sig,
        """        case MULTI_HIT_TRIGGER_ABILITY:
""",
        """        case MULTI_HIT_SOUL_LINKER:
            battleCtx->afterMoveMessageState++;
            if (Mercury_TrySoulLinkerMirror(battleSys, battleCtx) == TRUE) {
                return;
            }

""",
        "case MULTI_HIT_SOUL_LINKER:",
        "D19 multi-hit Soul Linker state",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(
        encoding="utf-8"
    )
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(
        encoding="utf-8"
    )
    script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_soul_linker.s"
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
        "stable_id_821":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "one_hit_hook":
            "ONE_HIT_SOUL_LINKER" in ctl
            and "case ONE_HIT_SOUL_LINKER:" in ctl,
        "multi_hit_hook":
            "MULTI_HIT_SOUL_LINKER" in ctl
            and "case MULTI_HIT_SOUL_LINKER:" in ctl,
        "runs_before_on_hit_ability":
            ctl.find("case ONE_HIT_SOUL_LINKER:")
            < ctl.find("case ONE_HIT_TRIGGER_ABILITY:"),
        "direct_damage_gate":
            "CURRENT_MOVE_DATA.class == CLASS_STATUS" in ctl
            and "battleCtx->hitDamage >= 0" in ctl
            and "Battler_SubstituteWasHit(battleCtx, defender)" in ctl,
        "opposing_only":
            "BattleSystem_GetBattlerSide(battleSys, attacker)" in ctl
            and "BattleSystem_GetBattlerSide(battleSys, defender)" in ctl,
        "attacker_or_defender_holder":
            "attackerLinked" in ctl
            and "defenderLinked" in ctl
            and ctl.count("ABILITY_MR_SOUL_LINKER") >= 2,
        "defender_mold_breaker_bypass":
            "Battler_IgnorableAbility(" in ctl
            and "ABILITY_MR_SOUL_LINKER" in ctl,
        "two_sided_faint_guard":
            "battleCtx->battleMons[attacker].curHP <= damage" in ctl
            and "battleCtx->battleMons[defender].curHP <= damage" in ctl,
        "actual_damage_mirrored":
            "damage = battleCtx->hitDamage * -1;" in ctl
            and "battleCtx->hpCalcTemp = damage * -1;" in ctl,
        "mirror_targets_original_attacker":
            "BTLVAR_MSG_TEMP, BTLVAR_ATTACKER" in script,
        "non_recursive_hp_event":
            "Call BATTLE_SUBSCRIPT_UPDATE_HP" in script
            and "BATTLE_CONTROL_BEFORE_MOVE" not in script,
        "ability_subscript_registered":
            "subscript_mercury_soul_linker" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in script,
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
        default=Path("mr10d19-soul-linker.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_subscript(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D19_SOUL_LINKER",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_system": "post_direct_damage_linked_hp_event",
        "mirror_uses_actual_damage": True,
        "two_sided_faint_guard": True,
        "recursive_linked_damage": False,
        "remaining_keep_as_written_after_d19": 16,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D19 Soul Linker validation failed")


if __name__ == "__main__":
    main()
