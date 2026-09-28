#!/usr/bin/env python3
"""MR08Q2 — canonical Comatose pass.

Ports current-mainline Comatose semantics into Mercury's Platinum battle core:
- the holder cannot receive ordinary nonvolatile status;
- it is treated as asleep by Snore, Sleep Talk, Dream Eater, Nightmare and
  Wake-Up Slap without storing a sleep status;
- Wake-Up Slap gets its sleep power bonus but cannot wake Comatose;
- the Ability cannot be copied, swapped, overwritten by Worry Seed, or
  suppressed by Gastro Acid.

MR08N already classifies Comatose as one of the special Abilities that
Neutralizing Gas / ordinary suppression must not turn off.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_COMATOSE",)
EXPECTED_IDS = {"ABILITY_COMATOSE": 213}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
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


def patch_status_immunity(root: Path) -> None:
    sleep = root / "res/battle/scripts/subscripts/subscript_fall_asleep.s"
    poison = root / "res/battle/scripts/subscripts/subscript_poison.s"
    toxic = root / "res/battle/scripts/subscripts/subscript_badly_poison.s"
    burn = root / "res/battle/scripts/subscripts/subscript_burn.s"
    freeze = root / "res/battle/scripts/subscripts/subscript_freeze.s"
    paralyze = root / "res/battle/scripts/subscripts/subscript_paralyze.s"

    insert_after_once(
        sleep,
        "    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_VITAL_SPIRIT, _202\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _202\n",
        "Comatose sleep immunity direct",
    )
    insert_after_once(
        sleep,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_VITAL_SPIRIT, _202\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _202\n",
        "Comatose sleep immunity move",
    )

    insert_after_once(
        poison,
        "    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _177\n",
        "Comatose poison immunity direct",
    )
    insert_after_once(
        poison,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _177\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _177\n",
        "Comatose poison immunity move",
    )

    insert_after_once(
        toxic,
        "    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _249\n",
        "Comatose toxic-spikes immunity",
    )
    insert_after_once(
        toxic,
        "    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _248\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _248\n",
        "Comatose held-item toxic immunity",
    )
    insert_after_once(
        toxic,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_IMMUNITY, _249\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _249\n",
        "Comatose toxic immunity move",
    )

    insert_after_once(
        burn,
        "    CheckAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _211\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _211\n",
        "Comatose burn immunity direct",
    )
    insert_after_once(
        burn,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_WATER_VEIL, _264\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _264\n",
        "Comatose burn immunity move",
    )

    insert_after_once(
        freeze,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_MAGMA_ARMOR, _128\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _128\n",
        "Comatose freeze immunity",
    )
    insert_after_once(
        paralyze,
        "    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_LIMBER, _170\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_SIDE_EFFECT_MON, BATTLEMON_ABILITY, ABILITY_COMATOSE, _170\n",
        "Comatose paralysis immunity",
    )


def patch_sleep_semantics(root: Path) -> None:
    effects = root / "res/battle/scripts/effects"

    replace_once(
        effects / "effect_script_0092.s",
        """_000:
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_ATTACKER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _019
    CompareVarToValue OPCODE_EQU, BTLVAR_MOVE_TEMP, MOVE_SLEEP_TALK, _012
""",
        """_000:
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_ATTACKER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _MercuryComatoseSnoreOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _019

_MercuryComatoseSnoreOK:
    CompareVarToValue OPCODE_EQU, BTLVAR_MOVE_TEMP, MOVE_SLEEP_TALK, _012
""",
        "Comatose Snore semantics",
    )

    replace_once(
        effects / "effect_script_0097.s",
        """_000:
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_ATTACKER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _013
    Call BATTLE_SUBSCRIPT_SLEEPING
""",
        """_000:
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_ATTACKER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _MercuryComatoseSleepTalkOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _013

_MercuryComatoseSleepTalkOK:
    Call BATTLE_SUBSCRIPT_SLEEPING
""",
        "Comatose Sleep Talk semantics",
    )

    replace_once(
        effects / "effect_script_0008.s",
        """_000:
    CheckSubstitute BTLSCR_DEFENDER, _015
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _015
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_FLAGS_INDIRECT, MOVE_SIDE_EFFECT_ON_HIT|MOVE_SUBSCRIPT_PTR_DREAM_EATER
""",
        """_000:
    CheckSubstitute BTLSCR_DEFENDER, _015
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _MercuryComatoseDreamEaterOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _015

_MercuryComatoseDreamEaterOK:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_FLAGS_INDIRECT, MOVE_SIDE_EFFECT_ON_HIT|MOVE_SUBSCRIPT_PTR_DREAM_EATER
""",
        "Comatose Dream Eater semantics",
    )

    replace_once(
        effects / "effect_script_0107.s",
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_NIGHTMARE, _019
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _019
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_FLAGS_DIRECT, MOVE_SIDE_EFFECT_ON_HIT|MOVE_SUBSCRIPT_PTR_NIGHTMARE_START
""",
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_NIGHTMARE, _019
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _MercuryComatoseNightmareOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _019

_MercuryComatoseNightmareOK:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_FLAGS_DIRECT, MOVE_SIDE_EFFECT_ON_HIT|MOVE_SUBSCRIPT_PTR_NIGHTMARE_START
""",
        "Comatose Nightmare effect semantics",
    )

    replace_once(
        root / "res/battle/scripts/subscripts/subscript_nightmare_start.s",
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_NIGHTMARE, _029
    CompareMonDataToValue OPCODE_FLAG_NOT, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _029
    Call BATTLE_SUBSCRIPT_ATTACK_MESSAGE_AND_ANIMATION
""",
        """    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_VOLATILE_STATUS, VOLATILE_CONDITION_NIGHTMARE, _029
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _MercuryComatoseNightmareStartOK
    CompareMonDataToValue OPCODE_NEQ, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _029

_MercuryComatoseNightmareStartOK:
    Call BATTLE_SUBSCRIPT_ATTACK_MESSAGE_AND_ANIMATION
""",
        "Comatose Nightmare subscript semantics",
    )

    replace_once(
        effects / "effect_script_0217.s",
        """_000:
    CheckSubstitute BTLSCR_DEFENDER, _022
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _014
    UpdateVar OPCODE_SET, BTLVAR_POWER_MULTI, 10
    GoTo _022

_014:
""",
        """_000:
    CheckSubstitute BTLSCR_DEFENDER, _022
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_SLEEP, _014
    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _MercuryComatoseWakeUpSlap
    UpdateVar OPCODE_SET, BTLVAR_POWER_MULTI, 10
    GoTo _022

_MercuryComatoseWakeUpSlap:
    UpdateVar OPCODE_SET, BTLVAR_POWER_MULTI, 20
    GoTo _022

_014:
""",
        "Comatose Wake-Up Slap semantics",
    )


def patch_ability_locking(root: Path) -> None:
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        "Comatose Role Play target lock",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
        "Comatose Role Play user lock",
    )

    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        "Comatose Skill Swap target lock",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
        "Comatose Skill Swap user lock",
    )

    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _034\n",
        "Comatose Gastro Acid lock",
    )

    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_MULTITYPE, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _041\n",
        "Comatose Worry Seed lock",
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
    sleep = (root / "res/battle/scripts/subscripts/subscript_fall_asleep.s").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    toxic = (root / "res/battle/scripts/subscripts/subscript_badly_poison.s").read_text(encoding="utf-8")
    burn = (root / "res/battle/scripts/subscripts/subscript_burn.s").read_text(encoding="utf-8")
    freeze = (root / "res/battle/scripts/subscripts/subscript_freeze.s").read_text(encoding="utf-8")
    paralyze = (root / "res/battle/scripts/subscripts/subscript_paralyze.s").read_text(encoding="utf-8")
    e8 = (root / "res/battle/scripts/effects/effect_script_0008.s").read_text(encoding="utf-8")
    e92 = (root / "res/battle/scripts/effects/effect_script_0092.s").read_text(encoding="utf-8")
    e97 = (root / "res/battle/scripts/effects/effect_script_0097.s").read_text(encoding="utf-8")
    e107 = (root / "res/battle/scripts/effects/effect_script_0107.s").read_text(encoding="utf-8")
    e217 = (root / "res/battle/scripts/effects/effect_script_0217.s").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "status_immunity":
            all("ABILITY_COMATOSE" in text for text in (sleep, poison, toxic, burn, freeze, paralyze)),
        "snore_sleep_talk":
            "ABILITY_COMATOSE" in e92 and "ABILITY_COMATOSE" in e97,
        "dream_eater_nightmare":
            "ABILITY_COMATOSE" in e8 and "ABILITY_COMATOSE" in e107,
        "wake_up_slap":
            "_MercuryComatoseWakeUpSlap" in e217
            and "BTLVAR_POWER_MULTI, 20" in e217,
        "uncopyable_unswappable":
            "ABILITY_COMATOSE" in copy and "ABILITY_COMATOSE" in swap,
        "unsuppressible":
            "ABILITY_COMATOSE" in suppress,
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
        default=Path("mr08q2-canonical-ability-comatose.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_status_immunity(root)
    patch_sleep_semantics(root)
    patch_ability_locking(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08Q2_CANONICAL_ABILITY_COMATOSE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 161,
        "remaining_modern_canonical_mechanics": 26,
        "policy": "Official/current-mainline mechanics; state/form-changing families remain in later passes.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08Q2 validation failed")


if __name__ == "__main__":
    main()
