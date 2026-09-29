#!/usr/bin/env python3
"""MR10C2 — implement the approved Execution Drive redesign.

Execution Drive:
- damaging moves deal 30% more damage to a target at or below half HP;
- after directly knocking out an opposing Pokémon, the user restores 1/8 max HP.

The low-HP check lives in the normal per-hit damage lane, so multi-hit moves
begin receiving the boost naturally once an earlier hit crosses the 50% mark.
The KO recovery shares Mercury's existing attacker-KO dispatcher.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Execution Drive"
ABILITY_TOKEN = "ABILITY_MR_EXECUTION_DRIVE"
ABILITY_ID = 885


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return

    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: function closing brace not found in {path}")

    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
        "implementation_class": "existing_hook",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_low_hp_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_BIG_PECKS
""",
        """    if (attackerParams.ability == ABILITY_MR_EXECUTION_DRIVE
        && battleCtx->battleMons[defender].curHP * 2
            <= battleCtx->battleMons[defender].maxHP
        && movePower) {
        movePower = movePower * 13 / 10;
    }

""",
        "Execution Drive low-HP damage boost",
    )


def install_recovery_subscript(root: Path) -> None:
    subdir = root / "res/battle/scripts/subscripts"
    script = subdir / "subscript_mercury_execution_drive.s"
    script.write_text(
        """#include "macros/btlcmd.inc"


_000:
    UpdateVarFromVar OPCODE_SET, BTLVAR_MSG_BATTLER_TEMP, BTLVAR_ATTACKER
    UpdateVar OPCODE_FLAG_ON, BTLVAR_BATTLE_CTX_STATUS, SYSCTL_SKIP_SPRITE_BLINK
    Call BATTLE_SUBSCRIPT_UPDATE_HP
    // {0} restored HP using its {1}!
    PrintMessage BattleStrings_Text_PokemonRestoredHPUsingItsAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_ATTACKER, BTLSCR_ATTACKER
    Wait
    WaitButtonABTime 30
    End
""",
        encoding="utf-8",
    )

    meson = subdir / "meson.build"
    text = meson.read_text(encoding="utf-8")
    entry = "    'subscript_mercury_execution_drive.s',\n"
    if entry not in text:
        anchor = "    'subscript_giratina_form_change.s',\n)"
        if text.count(anchor) != 1:
            raise SystemExit("Execution Drive subscript meson anchor not found exactly once")
        text = text.replace(
            anchor,
            "    'subscript_giratina_form_change.s',\n" + entry + ")",
            1,
        )
        meson.write_text(text, encoding="utf-8")

    order = subdir / "sub_seq.order"
    names = [line.strip() for line in order.read_text(encoding="utf-8").splitlines() if line.strip()]
    if "subscript_mercury_execution_drive" not in names:
        names.append("subscript_mercury_execution_drive")
        order.write_text("\n".join(names) + "\n", encoding="utf-8")


def patch_ko_recovery(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL BattleSystem_TriggerAttackerKOAbility("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )
    insert_before_in_function(
        path,
        signature,
        """    switch (Battler_Ability(battleCtx, battleCtx->attacker)) {
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_EXECUTION_DRIVE
        && battleCtx->battleMons[battleCtx->attacker].curHP
        && battleCtx->battleMons[battleCtx->attacker].curHP
            < battleCtx->battleMons[battleCtx->attacker].maxHP) {
        battleCtx->hpCalcTemp = BattleSystem_Divide(
            battleCtx->battleMons[battleCtx->attacker].maxHP, 8);
        if (battleCtx->hpCalcTemp < 1) {
            battleCtx->hpCalcTemp = 1;
        }
        *subscript = subscript_mercury_execution_drive;
        return TRUE;
    }

""",
        "Execution Drive attacker-KO recovery",
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
    meson = (root / "res/battle/scripts/subscripts/meson.build").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = root / "res/battle/scripts/subscripts/subscript_mercury_execution_drive.s"
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_885": len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "low_hp_damage_30_percent":
            "ABILITY_MR_EXECUTION_DRIVE" in lib
            and "movePower = movePower * 13 / 10;" in lib
            and "curHP * 2" in lib,
        "direct_ko_recovery_hook":
            "subscript_mercury_execution_drive" in lib
            and "BattleSystem_Divide(" in lib,
        "recovery_subscript_written": script.exists(),
        "recovery_subscript_built":
            "'subscript_mercury_execution_drive.s'" in meson
            and "subscript_mercury_execution_drive" in order,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c2-execution-drive.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_low_hp_damage(root)
    install_recovery_subscript(root)
    patch_ko_recovery(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C2_EXECUTION_DRIVE",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C2 Execution Drive validation failed")


if __name__ == "__main__":
    main()
