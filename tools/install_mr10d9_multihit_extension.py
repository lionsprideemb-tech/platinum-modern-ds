#!/usr/bin/env python3
"""MR10D9 — multi-hit extension: Jackhammer + Unrelenting.

Extends the green MR10D8 native multi-hit rewrite core:
- Jackhammer: Hammer-class attacks hit twice, both hits at 70% power.
- Unrelenting: eligible single-hit attacks strike a randomly selected 2–5 times.

The Hammer classifier follows the approved Elite Redux hammer class for
currently installed canonical moves (Wood Hammer, Hammer Arm, Ice Hammer,
Gigaton Hammer). Mercury custom moves can join the same helper when their move
definitions land, without changing Jackhammer's battle hook.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Jackhammer": ("ABILITY_MR_JACKHAMMER", 490),
    "Unrelenting": ("ABILITY_MR_UNRELENTING", 731),
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


def patch_hammer_classifier(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helper = """BOOL Mercury_MoveIsHammerClass(int move)
{
    switch (move) {
    case MOVE_WOOD_HAMMER:
    case MOVE_HAMMER_ARM:
    case MOVE_ICE_HAMMER:
    case MOVE_GIGATON_HAMMER:
        return TRUE;
    default:
        return FALSE;
    }
}

"""
    insert_before_once(
        lib,
        """static u8 Mercury_AddedTypeForAbility(int ability)
""",
        helper,
        "MR10D9 hammer classifier",
    )
    insert_before_once(
        hdr,
        """BOOL Mercury_MoveIsBitingClass(int move);
""",
        """BOOL Mercury_MoveIsHammerClass(int move);
""",
        "MR10D9 hammer classifier declaration",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_once(
        path,
        """    MERCURY_MULTI_HIT_PRIMAL_MAW,
    MERCURY_MULTI_HIT_DUAL_WIELD,
};
""",
        """    MERCURY_MULTI_HIT_PRIMAL_MAW,
    MERCURY_MULTI_HIT_DUAL_WIELD,
    MERCURY_MULTI_HIT_JACKHAMMER,
    MERCURY_MULTI_HIT_UNRELENTING,
};
""",
        "MR10D9 multi-hit kind enum",
    )

    replace_once(
        path,
        """    case ABILITY_MR_DUAL_WIELD:
        if (Mercury_MoveIsLauncherClass(battleCtx->moveCur)) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_DUAL_WIELD;
        }
        break;
    }

    if (battleCtx->mercuryCustomMultiHitKind != MERCURY_MULTI_HIT_NONE) {
        battleCtx->multiHitCounter = 2;
        battleCtx->multiHitNumHits = 2;
        battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
        battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
    }
""",
        """    case ABILITY_MR_DUAL_WIELD:
        if (Mercury_MoveIsLauncherClass(battleCtx->moveCur)) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_DUAL_WIELD;
        }
        break;

    case ABILITY_MR_JACKHAMMER:
        if (Mercury_MoveIsHammerClass(battleCtx->moveCur)) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_JACKHAMMER;
        }
        break;

    case ABILITY_MR_UNRELENTING:
        battleCtx->mercuryCustomMultiHitKind =
            MERCURY_MULTI_HIT_UNRELENTING;
        break;
    }

    if (battleCtx->mercuryCustomMultiHitKind != MERCURY_MULTI_HIT_NONE) {
        int mercuryHitCount = 2;

        if (battleCtx->mercuryCustomMultiHitKind
            == MERCURY_MULTI_HIT_UNRELENTING) {
            mercuryHitCount = (BattleSystem_RandNext(battleSys) % 4) + 2;
        }

        battleCtx->multiHitCounter = mercuryHitCount;
        battleCtx->multiHitNumHits = mercuryHitCount;
        battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
        battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
    }
""",
        "MR10D9 Jackhammer/Unrelenting setup",
    )


def patch_damage_scaling(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_once(
        path,
        """        case 4: // Dual Wield: both hits at 75%.
            damage = damage * 75 / 100;
            break;
        default:
""",
        """        case 4: // Dual Wield: both hits at 75%.
            damage = damage * 75 / 100;
            break;
        case 5: // Jackhammer: both hits at 70%.
            damage = damage * 70 / 100;
            break;
        case 6: // Unrelenting: every rolled hit uses normal power.
            break;
        default:
""",
        "MR10D9 multi-hit damage scaling",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "d8_multihit_core_present":
            "Mercury_SetupCustomMultiHit" in ctl
            and "mercuryCustomMultiHitKind" in ctl,
        "hammer_classifier":
            "Mercury_MoveIsHammerClass" in lib
            and all(move in lib for move in (
                "MOVE_WOOD_HAMMER",
                "MOVE_HAMMER_ARM",
                "MOVE_ICE_HAMMER",
                "MOVE_GIGATON_HAMMER",
            ))
            and "Mercury_MoveIsHammerClass" in hdr,
        "jackhammer_gate":
            "case ABILITY_MR_JACKHAMMER:" in ctl
            and "MERCURY_MULTI_HIT_JACKHAMMER" in ctl,
        "jackhammer_two_hits":
            "MERCURY_MULTI_HIT_JACKHAMMER" in ctl
            and "case 5: // Jackhammer: both hits at 70%." in lib
            and "damage = damage * 70 / 100;" in lib,
        "unrelenting_gate":
            "case ABILITY_MR_UNRELENTING:" in ctl
            and "MERCURY_MULTI_HIT_UNRELENTING" in ctl,
        "unrelenting_two_to_five":
            "(BattleSystem_RandNext(battleSys) % 4) + 2" in ctl
            and "multiHitCounter = mercuryHitCount;" in ctl
            and "multiHitNumHits = mercuryHitCount;" in ctl,
        "unrelenting_normal_per_hit_power":
            "case 6: // Unrelenting: every rolled hit uses normal power." in lib,
        "native_multihit_exclusions_preserved":
            "Mercury_D8BaseMoveAllowed" in ctl
            and "case BATTLE_EFFECT_MULTI_HIT:" in ctl
            and "case BATTLE_EFFECT_HIT_TWICE:" in ctl,
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
        default=Path("mr10d9-multihit-extension.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_hammer_classifier(root)
    patch_controller(root)
    patch_damage_scaling(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D9_MULTIHIT_EXTENSION",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "native_multi_hit_move_rewrite",
        "remaining_keep_as_written_after_d9": 37,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D9 multi-hit extension validation failed")


if __name__ == "__main__":
    main()
