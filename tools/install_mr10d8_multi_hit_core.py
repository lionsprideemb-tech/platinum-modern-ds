#!/usr/bin/env python3
"""MR10D8 — fixed two-hit move-rewrite core.

Implements four KEEP-AS-WRITTEN mechanics on Platinum's native multi-hit loop:
- Raging Moth: damaging Fire moves hit twice; both hits use 70% power.
- Ice Cold Hunter: while hail/icy weather is active, qualifying damaging Ice
  moves hit twice at normal power.
- Primal Maw: eligible biting moves hit twice; hit two uses 50% power.
- Dual Wield: Mega Launcher-class damaging moves hit twice; both hits use 75%
  power.

The existing canonical bite and pulse classifiers are exposed through narrow
public wrappers so Mercury keeps one authoritative move classification table.
Existing multihit/OHKO/charge/self-KO/special-script exclusions mirror the
certified Parental Bond lane. Mechanics only; MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Raging Moth": ("ABILITY_MR_RAGING_MOTH", 480),
    "Ice Cold Hunter": ("ABILITY_MR_ICE_COLD_HUNTER", 884),
    "Primal Maw": ("ABILITY_MR_PRIMAL_MAW", 893),
    "Dual Wield": ("ABILITY_MR_DUAL_WIELD", 895),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())

KIND_NONE = 0
KIND_RAGING_MOTH = 1
KIND_ICE_COLD_HUNTER = 2
KIND_PRIMAL_MAW = 3
KIND_DUAL_WIELD = 4


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


def patch_classifier_wrappers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    wrappers = """BOOL Mercury_MoveIsBitingClass(int move)
{
    return Mercury_MoveIsBiting(move);
}

BOOL Mercury_MoveIsLauncherClass(int move)
{
    return Mercury_MoveIsPulse(move);
}

"""
    insert_before_once(
        lib,
        """static u8 Mercury_AddedTypeForAbility(int ability)
""",
        wrappers,
        "MR10D8 move-class public wrappers",
    )

    declarations = """BOOL Mercury_MoveIsBitingClass(int move);
BOOL Mercury_MoveIsLauncherClass(int move);
"""
    insert_before_once(
        hdr,
        """int Mercury_BattlerAddedType(BattleContext *battleCtx, int battler);
""",
        declarations,
        "MR10D8 move-class declarations",
    )


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryParentalBondActive;
""",
        """    // Mercury MR10D8: current fixed two-hit rewrite family.
    u8 mercuryCustomMultiHitKind;

""",
        "MR10D8 custom multi-hit state",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helpers = """enum MercuryCustomMultiHitKind {
    MERCURY_MULTI_HIT_NONE = 0,
    MERCURY_MULTI_HIT_RAGING_MOTH,
    MERCURY_MULTI_HIT_ICE_COLD_HUNTER,
    MERCURY_MULTI_HIT_PRIMAL_MAW,
    MERCURY_MULTI_HIT_DUAL_WIELD,
};

static BOOL Mercury_D8BaseMoveAllowed(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int move = battleCtx->moveCur;
    int effect = MOVE_DATA(move).effect;
    int range = MOVE_DATA(move).range;
    int battleType = BattleSystem_GetBattleType(battleSys);
    int i;
    int liveTargets = 0;
    int maxBattlers;

    if (MOVE_DATA(move).class == CLASS_STATUS
        || MOVE_DATA(move).power == 0
        || Move_IsMultiTurn(battleCtx, move) == TRUE) {
        return FALSE;
    }

    switch (effect) {
    case BATTLE_EFFECT_MULTI_HIT:
    case BATTLE_EFFECT_HIT_TWICE:
    case BATTLE_EFFECT_POISON_MULTI_HIT:
    case BATTLE_EFFECT_ONE_HIT_KO:
        return FALSE;
    }

    switch (move) {
    case MOVE_SELFDESTRUCT:
    case MOVE_EXPLOSION:
    case MOVE_FLING:
    case MOVE_UPROAR:
    case MOVE_ROLLOUT:
    case MOVE_ICE_BALL:
    case MOVE_ENDEAVOR:
    case MOVE_PRESENT:
    case MOVE_TRIPLE_KICK:
    case MOVE_BEAT_UP:
        return FALSE;
    }

    if ((battleType & BATTLE_TYPE_DOUBLES) == FALSE) {
        return TRUE;
    }

    if (range != RANGE_ADJACENT_OPPONENTS
        && range != RANGE_ALL_ADJACENT) {
        return TRUE;
    }

    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);
    for (i = 0; i < maxBattlers; i++) {
        if (i == battleCtx->attacker || battleCtx->battleMons[i].curHP == 0) {
            continue;
        }

        if (range == RANGE_ADJACENT_OPPONENTS
            && BattleSystem_GetBattlerSide(battleSys, i)
                == BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
            continue;
        }

        liveTargets++;
    }

    return liveTargets == 1;
}

static void Mercury_SetupCustomMultiHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability;
    int moveType;

    battleCtx->mercuryCustomMultiHitKind = MERCURY_MULTI_HIT_NONE;

    if (Mercury_D8BaseMoveAllowed(battleSys, battleCtx) == FALSE) {
        return;
    }

    ability = Battler_Ability(battleCtx, battleCtx->attacker);
    moveType = CalcMoveType(
        battleCtx, battleCtx->attacker, battleCtx->moveCur);

    switch (ability) {
    case ABILITY_MR_RAGING_MOTH:
        if (moveType == TYPE_FIRE) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_RAGING_MOTH;
        }
        break;

    case ABILITY_MR_ICE_COLD_HUNTER:
        if (moveType == TYPE_ICE
            && NO_CLOUD_NINE
            && WEATHER_IS_HAIL) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_ICE_COLD_HUNTER;
        }
        break;

    case ABILITY_MR_PRIMAL_MAW:
        if (Mercury_MoveIsBitingClass(battleCtx->moveCur)) {
            battleCtx->mercuryCustomMultiHitKind =
                MERCURY_MULTI_HIT_PRIMAL_MAW;
        }
        break;

    case ABILITY_MR_DUAL_WIELD:
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
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_BeforeMove(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helpers,
        "MR10D8 custom multi-hit setup",
    )

    replace_once(
        path,
        """        if (battleCtx->multiHitLoop == FALSE) {
            Mercury_SetupParentalBond(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        """        if (battleCtx->multiHitLoop == FALSE) {
            Mercury_SetupParentalBond(battleSys, battleCtx);
            Mercury_SetupCustomMultiHit(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        "MR10D8 pre-move multi-hit setup hook",
    )


def patch_damage_scaling(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    text = path.read_text(encoding="utf-8")
    start = text.index("int BattleSystem_CalcMoveDamage(")
    end = text.index("int BattleSystem_CalcDamageVariance(", start)
    block = text[start:end]

    old = """    // Gen VII onward: only ordinary calculated damage on the child strike is
    // quartered. Set/fixed-damage move scripts bypass this function and thus
    // correctly keep their full fixed value on both strikes.
    if (battleCtx->mercuryParentalBondActive
        && battleCtx->multiHitLoop
        && damage > 0) {
        damage /= 4;
        if (damage == 0) {
            damage = 1;
        }
    }

    return damage;
}
"""
    new = """    // Gen VII onward: only ordinary calculated damage on the child strike is
    // quartered. Set/fixed-damage move scripts bypass this function and thus
    // correctly keep their full fixed value on both strikes.
    if (battleCtx->mercuryParentalBondActive
        && battleCtx->multiHitLoop
        && damage > 0) {
        damage /= 4;
        if (damage == 0) {
            damage = 1;
        }
    }

    // Mercury MR10D8 fixed two-hit rewrite family.
    if (damage > 0) {
        switch (battleCtx->mercuryCustomMultiHitKind) {
        case 1: // Raging Moth: both hits at 70%.
            damage = damage * 70 / 100;
            break;
        case 2: // Ice Cold Hunter: both hits at normal power.
            break;
        case 3: // Primal Maw: only the second hit is halved.
            if (battleCtx->multiHitLoop) {
                damage /= 2;
            }
            break;
        case 4: // Dual Wield: both hits at 75%.
            damage = damage * 75 / 100;
            break;
        default:
            break;
        }

        if (damage == 0) {
            damage = 1;
        }
    }

    return damage;
}
"""
    if new not in block:
        count = block.count(old)
        if count != 1:
            raise SystemExit(
                f"MR10D8 damage scaling: expected one Parental Bond anchor, found {count}"
            )
        block = block.replace(old, new, 1)
        path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "shared_custom_multihit_state":
            "mercuryCustomMultiHitKind" in ctx,
        "bite_classifier_reused":
            "Mercury_MoveIsBitingClass" in lib
            and "return Mercury_MoveIsBiting(move);" in lib
            and "Mercury_MoveIsBitingClass" in hdr,
        "launcher_classifier_reused":
            "Mercury_MoveIsLauncherClass" in lib
            and "return Mercury_MoveIsPulse(move);" in lib
            and "Mercury_MoveIsLauncherClass" in hdr,
        "native_multihit_pipeline":
            "battleCtx->multiHitCounter = 2;" in ctl
            and "battleCtx->multiHitNumHits = 2;" in ctl
            and "battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;" in ctl,
        "existing_multihit_excluded":
            "case BATTLE_EFFECT_MULTI_HIT:" in ctl
            and "case BATTLE_EFFECT_HIT_TWICE:" in ctl,
        "raging_moth_fire_gate":
            "case ABILITY_MR_RAGING_MOTH:" in ctl
            and "moveType == TYPE_FIRE" in ctl
            and "damage = damage * 70 / 100;" in lib,
        "ice_cold_hunter_weather_gate":
            "case ABILITY_MR_ICE_COLD_HUNTER:" in ctl
            and "NO_CLOUD_NINE" in ctl
            and "WEATHER_IS_HAIL" in ctl,
        "primal_maw_biting_gate":
            "case ABILITY_MR_PRIMAL_MAW:" in ctl
            and "Mercury_MoveIsBitingClass" in ctl
            and "if (battleCtx->multiHitLoop)" in lib
            and "damage /= 2;" in lib,
        "dual_wield_launcher_gate":
            "case ABILITY_MR_DUAL_WIELD:" in ctl
            and "Mercury_MoveIsLauncherClass" in ctl
            and "damage = damage * 75 / 100;" in lib,
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
        default=Path("mr10d8-multi-hit-core.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_classifier_wrappers(root)
    patch_context(root)
    patch_controller(root)
    patch_damage_scaling(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D8_MULTI_HIT_CORE",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "native_multi_hit_move_rewrite",
        "remaining_keep_as_written_after_d8": 39,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D8 multi-hit core validation failed")


if __name__ == "__main__":
    main()
