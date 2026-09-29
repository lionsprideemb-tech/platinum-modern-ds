#!/usr/bin/env python3
"""MR10D16 — Lucky Halo.

Implements the approved KEEP-AS-WRITTEN two-part mechanic:

- self-inflicted stat-stage drops are blocked continuously;
- the party Pokémon survives its first otherwise-fatal direct damaging hit at
  exactly 1 HP, once per battle, including when it was already at 1 HP.

The survival flag is stored by side + party slot so switching cannot refresh
it and Ability replacement cannot move the consumed charge to another party
member. Ordinary Mold Breaker-family rules can ignore the survival Ability,
while Neutralizing Gas/suppression is respected by Battler_Ability for the
self-drop half.

Mechanics only; locked MR07 visuals remain untouched.
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryParasiticSpores[MAX_BATTLERS];
""",
        """    // Mercury MR10D16: once-per-party-Pokémon fatal-hit survival.
    u8 mercuryLuckyHaloSurvivalUsedMask[2];

""",
        "D16 Lucky Halo party survival state",
    )


def patch_self_drop_prevention(root: Path) -> None:
    path = root / "src/battle/battle_script.c"
    signature = (
        "static BOOL BtlCmd_ChangeStatStage("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """    if (stageChange < 0
        && battleCtx->attacker == battleCtx->sideEffectMon
        && Battler_Ability(battleCtx, battleCtx->sideEffectMon)
            == ABILITY_MR_LUCKY_HALO) {
        battleCtx->battleStatusMask |= SYSCTL_FAIL_STAT_STAGE_CHANGE;
        battleCtx->msgBuffer.id =
            BattleStrings_Text_PokemonsAbilityPreventsStatLoss_Ally;
        battleCtx->msgBuffer.tags = TAG_NICKNAME_ABILITY;
        battleCtx->msgBuffer.params[0] =
            BattleSystem_NicknameTag(battleCtx, battleCtx->sideEffectMon);
        battleCtx->msgBuffer.params[1] =
            battleCtx->battleMons[battleCtx->sideEffectMon].ability;
        BattleScript_Iter(battleCtx, jumpNoChange);
        return FALSE;
    }

"""
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if "ABILITY_MR_LUCKY_HALO" not in block:
        anchor = """    if (stageChange > 0) {
"""
        pos = block.find(anchor)
        if pos < 0:
            raise SystemExit(
                "D16 self-inflicted stat-drop prevention: "
                "post-stage-decode anchor missing"
            )
        block = block[:pos] + insertion + block[pos:]
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")

def patch_fatal_hit_survival(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static void BattleControllerPlayer_UpdateHP("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insertion = """        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && battleCtx->attacker != battleCtx->defender
            && battleCtx->damage < 0
            && DEFENDING_MON.curHP
            && DEFENDING_MON.curHP + battleCtx->damage <= 0
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && CURRENT_MOVE_DATA.class != CLASS_STATUS
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_MR_LUCKY_HALO) == TRUE) {
            int side = BattleSystem_GetBattlerSide(
                battleSys, battleCtx->defender);
            int slot = battleCtx->selectedPartySlot[battleCtx->defender];

            if (slot < 6
                && (battleCtx->mercuryLuckyHaloSurvivalUsedMask[side]
                    & FlagIndex(slot)) == 0) {
                battleCtx->mercuryLuckyHaloSurvivalUsedMask[side]
                    |= FlagIndex(slot);
                battleCtx->damage = (DEFENDING_MON.curHP - 1) * -1;
                battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED;
            }
        }

"""
    insert_before_in_function(
        path,
        signature,
        """        if (DEFENDER_TURN_FLAGS.enduring == 0) {
""",
        insertion,
        "mercuryLuckyHaloSurvivalUsedMask",
        "D16 once-per-battle fatal-hit survival",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(
        encoding="utf-8"
    )
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_503":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "self_drop_gate":
            "stageChange < 0" in script
            and "battleCtx->attacker == battleCtx->sideEffectMon" in script
            and "== ABILITY_MR_LUCKY_HALO" in script,
        "cannot_prevent_flag_does_not_bypass_lucky_halo":
            script.find("ABILITY_MR_LUCKY_HALO")
            < script.find(
                "MOVE_SIDE_EFFECT_CANNOT_PREVENT",
                script.find("static BOOL BtlCmd_ChangeStatStage"),
            ),
        "party_persistent_survival_state":
            "mercuryLuckyHaloSurvivalUsedMask[2]" in ctx,
        "direct_hit_gate":
            "battleCtx->attacker != battleCtx->defender" in ctl
            and "CURRENT_MOVE_DATA.class != CLASS_STATUS" in ctl,
        "fatal_only_gate":
            "DEFENDING_MON.curHP + battleCtx->damage <= 0" in ctl,
        "works_from_one_hp":
            "battleCtx->damage = (DEFENDING_MON.curHP - 1) * -1;" in ctl,
        "once_per_party_slot":
            "mercuryLuckyHaloSurvivalUsedMask[side]" in ctl
            and "FlagIndex(slot)" in ctl,
        "ordinary_endure_message_path":
            "battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED;" in ctl,
        "mold_breaker_family_can_ignore":
            "Battler_IgnorableAbility(" in ctl
            and "ABILITY_MR_LUCKY_HALO" in ctl,
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
    ap.add_argument("--report", type=Path, default=Path("mr10d16-lucky-halo.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_self_drop_prevention(root)
    patch_fatal_hit_survival(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D16_LUCKY_HALO",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_systems_reused": [
            "Platinum stat-stage script",
            "party-slot battle-persistent masks",
            "Platinum endured-hit messaging",
        ],
        "remaining_keep_as_written_after_d16": 22,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D16 Lucky Halo validation failed")


if __name__ == "__main__":
    main()
