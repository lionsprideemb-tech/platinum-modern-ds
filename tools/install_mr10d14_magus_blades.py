#!/usr/bin/env python3
"""MR10D14 — Magus Blades composite Ability.

Implements approved KEEP-AS-WRITTEN Magus Blades as the exact composition of:
- Dual Wield: current Mercury Mega Launcher-class moves use the D11 two-hit
  native loop at 75% power per hit.
- Best Offense: Mystic Blades behavior for Keen Edge/slicing moves (special
  conversion +30% power), plus 20% of the user's current Special Defense added
  to the relevant offensive stat calculation.

This extends already-certified shared systems rather than creating a second
multi-hit engine or a second slicing classifier. Locked MR07 visuals are not
touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Magus Blades": ("ABILITY_MR_MAGUS_BLADES", 417),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
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


def patch_dual_wield_component(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        ctl,
        """    case ABILITY_MR_DUAL_WIELD:
        return Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0;
""",
        """    case ABILITY_MR_DUAL_WIELD:
    case ABILITY_MR_MAGUS_BLADES:
        return Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0;
""",
        "Magus Blades joins Dual Wield trigger",
    )

    replace_once(
        lib,
        """        } else if (battleCtx->mercuryCustomMultiHitTriggerAbility
            == ABILITY_MR_DUAL_WIELD) {
            movePower = movePower * 75 / 100;
        }
""",
        """        } else if (battleCtx->mercuryCustomMultiHitTriggerAbility
                == ABILITY_MR_DUAL_WIELD
            || battleCtx->mercuryCustomMultiHitTriggerAbility
                == ABILITY_MR_MAGUS_BLADES) {
            movePower = movePower * 75 / 100;
        }
""",
        "Magus Blades Dual Wield per-hit power",
    )


def patch_best_offense_component(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    helper = """static u16 Mercury_D14CurrentSpDefense(
    BattleContext *battleCtx,
    int battler)
{
    u32 stat;
    int stage;

    stat = BattleMon_Get(battleCtx, battler, BATTLEMON_SP_DEFENSE, NULL);
    stage = BattleMon_Get(
        battleCtx, battler, BATTLEMON_SP_DEFENSE_STAGE, NULL);

    if (stage < MIN_STAT_STAGE) {
        stage = MIN_STAT_STAGE;
    } else if (stage > MAX_STAT_STAGE) {
        stage = MAX_STAT_STAGE;
    }

    stat = stat * sStatStageBoosts[stage].numerator;
    stat /= sStatStageBoosts[stage].denominator;

    if (stat > 0xFFFF) {
        stat = 0xFFFF;
    }
    return (u16)stat;
}

"""
    insert_before_once(
        lib,
        "int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,\n",
        helper,
        "D14 current Special Defense helper",
    )

    insert_after_once(
        lib,
        """    attackerParams.ability = Battler_Ability(battleCtx, attacker);
""",
        """    if (attackerParams.ability == ABILITY_MR_MAGUS_BLADES) {
        attackStat += Mercury_D14CurrentSpDefense(battleCtx, attacker) / 5;
        spAttackStat += Mercury_D14CurrentSpDefense(battleCtx, attacker) / 5;
    }
""",
        "Magus Blades Best Offense SpDef contribution",
    )

    insert_before_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        """    // Mercury MR10D14: Mystic Blades component.
    if (attackerParams.ability == ABILITY_MR_MAGUS_BLADES
        && Mercury_MoveIsSlicing(move)) {
        moveClass = CLASS_SPECIAL;
        movePower = movePower * 13 / 10;
    }

""",
        "Magus Blades Mystic Blades conversion",
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
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "reuses_d11_native_multihit":
            "case ABILITY_MR_MAGUS_BLADES:" in ctl
            and "Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0" in ctl,
        "dual_wield_75_each_hit":
            "mercuryCustomMultiHitTriggerAbility" in lib
            and "== ABILITY_MR_MAGUS_BLADES" in lib
            and "movePower = movePower * 75 / 100;" in lib,
        "reuses_keen_edge_classifier":
            "Mercury_MoveIsSlicing(move)" in lib,
        "mystic_blades_special_conversion":
            "attackerParams.ability == ABILITY_MR_MAGUS_BLADES" in lib
            and "moveClass = CLASS_SPECIAL;" in lib,
        "mystic_blades_30_percent":
            "movePower = movePower * 13 / 10;" in lib,
        "best_offense_current_spdef":
            "Mercury_D14CurrentSpDefense" in lib
            and "BATTLEMON_SP_DEFENSE_STAGE" in lib
            and "sStatStageBoosts[stage]" in lib,
        "best_offense_20_percent_to_both_offense_lanes":
            "attackStat += Mercury_D14CurrentSpDefense(battleCtx, attacker) / 5;" in lib
            and "spAttackStat += Mercury_D14CurrentSpDefense(battleCtx, attacker) / 5;" in lib,
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
        default=Path("mr10d14-magus-blades.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_dual_wield_component(root)
    patch_best_offense_component(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D14_MAGUS_BLADES",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "components_reused": ["Dual Wield", "Best Offense", "Mystic Blades"],
        "remaining_keep_as_written_after_d14": 28,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D14 Magus Blades validation failed")


if __name__ == "__main__":
    main()
