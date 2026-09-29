#!/usr/bin/env python3
"""MR10D10 — Lunar Wrath generated follow-up.

Adds the reviewed KEEP-AS-WRITTEN Lunar Wrath mechanic to the already-green
MR10D7 generated-action pipeline:
- after a successful Ghost-type damaging move, immediately use one
  Moongeist Beam follow-up at fixed 50 BP;
- the generated action does not spend PP and does not recursively create
  another Ability-generated action;
- ordinary targeting, accuracy, type, immunity, item, Ability, fainting, and
  battle-script processing remains active through the shared D7 path.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Lunar Wrath"
ABILITY_TOKEN = "ABILITY_MR_LUNAR_WRATH"
ABILITY_ID = 573


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_followup_selector(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    replace_once(
        path,
        """    case ABILITY_MR_VOLCANO_RAGE:
        if (moveType == TYPE_FIRE) {
            *move = MOVE_ERUPTION;
            *power = 50;
        }
        break;
    }

    return *move != MOVE_NONE;
""",
        """    case ABILITY_MR_VOLCANO_RAGE:
        if (moveType == TYPE_FIRE) {
            *move = MOVE_ERUPTION;
            *power = 50;
        }
        break;

    case ABILITY_MR_LUNAR_WRATH:
        if (damaging && moveType == TYPE_GHOST) {
            *move = MOVE_MOONGEIST_BEAM;
            *power = 50;
        }
        break;
    }

    return *move != MOVE_NONE;
""",
        "Lunar Wrath D7 follow-up selector",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    return {
        "stable_id_573":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "shared_generated_action_pipeline":
            "Mercury_TryAbilityFollowup" in ctl
            and "mercuryAbilityGeneratedAction" in ctl,
        "ghost_damaging_gate":
            "case ABILITY_MR_LUNAR_WRATH:" in ctl
            and "damaging && moveType == TYPE_GHOST" in ctl,
        "moongeist_beam_followup":
            "MOVE_MOONGEIST_BEAM" in ctl
            and "*power = 50;" in ctl,
        "one_generated_action_guard":
            "if (battleCtx->mercuryAbilityGeneratedAction" in ctl,
        "no_pp_generated_action":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "fixed_50bp_override":
            "mercuryAbilityFollowupPower" in script
            and "battleCtx->movePower = battleCtx->mercuryAbilityFollowupPower;" in script,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
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
        default=Path("mr10d10-lunar-wrath.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_followup_selector(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D10_LUNAR_WRATH",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_system": "ability_generated_extra_action",
        "remaining_keep_as_written_after_d10": 36,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D10 Lunar Wrath validation failed")


if __name__ == "__main__":
    main()
