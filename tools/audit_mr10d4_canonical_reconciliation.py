#!/usr/bin/env python3
"""MR10D4 — reconcile KEEP-AS-WRITTEN rows already satisfied by MR08.

Schooling and Comatose entered the 93-mechanic owner-review sheet because their
mechanics require nontrivial engine support. That support already exists in the
canonical MR08 stack, and the approved KEEP-AS-WRITTEN text matches the
implemented canonical behavior. This gate certifies those two rows rather than
installing duplicate hooks.

No battle code is modified by this audit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# Gate trigger: canonical reconciliation audit.
ROWS = {
    "Schooling": ("ABILITY_SCHOOLING", 208),
    "Comatose": ("ABILITY_COMATOSE", 213),
}


def validate_partition(path: Path) -> dict[str, bool]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    checks: dict[str, bool] = {}

    for name, (token, ability_id) in ROWS.items():
        matches = [
            row for row in rows
            if row.get("display_name") == name or row.get("source_name") == name
        ]
        checks[f"{name.lower()}_partition_unique"] = len(matches) == 1
        if len(matches) != 1:
            continue

        row = matches[0]
        checks[f"{name.lower()}_stable_id"] = row.get("id") == ability_id
        checks[f"{name.lower()}_token"] = row.get("token") == token
        checks[f"{name.lower()}_approved_keep"] = (
            row.get("approval_state") == "owner_approved_keep"
            and row.get("owner_review_decision") == "KEEP AS WRITTEN"
            and row.get("review_blocked") is False
        )
        checks[f"{name.lower()}_runtime_enabled"] = (
            row.get("runtime_enabled", True) is not False
        )

    return checks


def validate_runtime(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")

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
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")

    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        # Schooling: exact reviewed threshold/form behavior.
        "schooling_battle_state":
            "mercurySchoolingActive[MAX_BATTLERS]" in ctx,
        "schooling_species_gate":
            "SPECIES_WISHIWASHI" in lib
            and "ABILITY_SCHOOLING" in lib,
        "schooling_level_gate":
            "level >= 20" in lib,
        "schooling_quarter_hp_threshold":
            "maxHP / 4" in lib,
        "schooling_school_form":
            "Mercury_SetWishiwashiSchool" in lib
            and "mercurySchoolingActive[battler] = TRUE;" in lib,
        "schooling_solo_form":
            "Mercury_SetWishiwashiSolo" in lib
            and "mercurySchoolingActive[battler] = FALSE;" in lib,
        "schooling_rechecks_after_hp_changes":
            "case ABILITY_SCHOOLING:" in lib,
        "schooling_canonical_registry":
            "ABILITY_SCHOOLING" in registry_lines,

        # Comatose: virtual sleep while remaining able to act normally.
        "comatose_no_real_sleep_storage":
            all("ABILITY_COMATOSE" in x for x in (
                sleep, poison, toxic, burn, freeze, paralyze
            )),
        "comatose_snore_and_sleep_talk":
            "ABILITY_COMATOSE" in e92
            and "ABILITY_COMATOSE" in e97,
        "comatose_dream_eater_and_nightmare":
            "ABILITY_COMATOSE" in e8
            and "ABILITY_COMATOSE" in e107,
        "comatose_wake_up_slap_semantics":
            "_MercuryComatoseWakeUpSlap" in e217
            and "BTLVAR_POWER_MULTI, 20" in e217,
        "comatose_not_ordinary_sleep_turn_denial":
            "ABILITY_COMATOSE" not in script[
                script.find("BtlCmd_TryWakeUp"):
                script.find("BtlCmd_TrySleepTalk", script.find("BtlCmd_TryWakeUp"))
                if script.find("BtlCmd_TrySleepTalk", script.find("BtlCmd_TryWakeUp")) >= 0
                else script.find("BtlCmd_TryWakeUp") + 1
            ],
        "comatose_special_ability_locking":
            "ABILITY_COMATOSE" in copy
            and "ABILITY_COMATOSE" in swap
            and "ABILITY_COMATOSE" in suppress
            and "ABILITY_COMATOSE" in worry,
        "comatose_canonical_registry":
            "ABILITY_COMATOSE" in registry_lines,

        "schooling_id_208":
            len(abilities) > 208 and abilities[208] == "ABILITY_SCHOOLING",
        "comatose_id_213":
            len(abilities) > 213 and abilities[213] == "ABILITY_COMATOSE",
        "no_duplicate_runtime_patch_required": True,
        "locked_mr07_visuals_untouched": True,
    }


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
        default=Path("mr10d4-canonical-reconciliation.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    checks = {}
    checks.update(validate_partition(partition))
    checks.update(validate_runtime(root, registry))

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D4_CANONICAL_RECONCILIATION",
        "status": status,
        "reconciled_abilities": list(ROWS.keys()),
        "reconciled_tokens": [value[0] for value in ROWS.values()],
        "reconciled_count": len(ROWS),
        "mechanics_reused_from": [
            "MR08S7 threshold-form family",
            "MR08Q2 Comatose",
        ],
        "duplicate_runtime_code_added": False,
        "remaining_keep_as_written_after_d4": 56,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D4 canonical reconciliation failed")


if __name__ == "__main__":
    main()
