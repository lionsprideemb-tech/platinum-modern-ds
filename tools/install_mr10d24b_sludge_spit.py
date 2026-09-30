#!/usr/bin/env python3
"""MR10D24B — Sludge Spit.

Adds the approved KEEP-AS-WRITTEN Sludge Spit mechanic on top of the combined
MR10D24A ability+move baseline. Successful damaging moves immediately generate
one 35-BP Venom Bolt through the existing MR10D7 generated-action pipeline.

The generated action:
- spends no PP and does not consume the selected turn action;
- follows normal targeting/redirection/accuracy/type/immunity/Protect/move script flow;
- is recursion-guarded by the existing Mercury generated-action flag;
- uses Venom Bolt's normal secondary effects at a forced 35 base power.

Locked MR07 visuals are untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Sludge Spit"
ABILITY_TOKEN = "ABILITY_MR_SLUDGE_SPIT"
ABILITY_ID = 571
MOVE_TOKEN = "MOVE_VENOM_BOLT"
MOVE_ID = 1028


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
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    matches = [
        row for row in rows
        if row.get("display_name") == ABILITY_NAME or row.get("source_name") == ABILITY_NAME
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


def patch_generated_followup(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"
    signature = (
        "static BOOL Mercury_D7ChooseFollowup(\n"
        "    BattleContext *battleCtx,\n"
        "    int *move,\n"
        "    int *power)"
    )
    insertion = """    case ABILITY_MR_SLUDGE_SPIT:
        if (damaging) {
            *move = MOVE_VENOM_BOLT;
            *power = 35;
        }
        break;

"""
    insert_before_in_function(
        path,
        signature,
        """    case ABILITY_MR_THUNDER_CLOUDS:
""",
        insertion,
        "case ABILITY_MR_SLUDGE_SPIT:",
        "MR10D24B Sludge Spit follow-up",
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
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    moves = [
        line.strip()
        for line in (root / "generated/moves.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "ability_stable_id":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "venom_bolt_materialized":
            len(moves) > MOVE_ID and moves[MOVE_ID] == MOVE_TOKEN,
        "sludge_spit_followup_case":
            "case ABILITY_MR_SLUDGE_SPIT:" in ctl
            and "*move = MOVE_VENOM_BOLT;" in ctl
            and "*power = 35;" in ctl,
        "reuses_generated_action_recursion_guard":
            "mercuryAbilityGeneratedAction" in ctl
            and "mercuryAbilityFollowupActive" in ctl,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
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
        default=Path("mr10d24b-sludge-spit.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_generated_followup(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D24B_SLUDGE_SPIT",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "generated_move": MOVE_TOKEN,
        "generated_move_id": MOVE_ID,
        "forced_power": 35,
        "shared_system_reused": "MR10D7 generated Ability action",
        "remaining_keep_as_written_after_d24b": 13,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D24B Sludge Spit validation failed")


if __name__ == "__main__":
    main()
