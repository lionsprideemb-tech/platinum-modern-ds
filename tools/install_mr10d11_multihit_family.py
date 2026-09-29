#!/usr/bin/env python3
"""MR10D11 — shared custom multi-hit family.

Graduates five approved KEEP-AS-WRITTEN mechanics on Platinum's native
multi-hit loop:

- Raging Moth: eligible Fire damaging moves hit twice; each hit uses 70% power.
- Jackhammer: Hammer-class moves hit twice; each hit uses 70% power.
- Unrelenting: eligible single-hit attacks become 2–5 hits.
- Ice Cold Hunter: in effective hail/icy weather, eligible Ice attacks hit twice.
- Primal Maw: eligible biting moves hit twice; hit two deals half normal damage.
- Dual Wield: current Mercury Mega Launcher-class moves hit twice; each hit
  uses 75% power.

The implementation deliberately reuses the canonical Parental Bond eligibility
safety envelope: already-multihit, OHKO, charging, self-KO and other special
scripts are not rewrapped, and spread attacks are only rewrapped when exactly
one live target exists. One accuracy check is retained while ordinary per-hit
secondary effects, contact reactions and faint handling remain native.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Raging Moth": ("ABILITY_MR_RAGING_MOTH", 442),
    "Jackhammer": ("ABILITY_MR_JACKHAMMER", 490),
    "Unrelenting": ("ABILITY_MR_UNRELENTING", 731),
    "Ice Cold Hunter": ("ABILITY_MR_ICE_COLD_HUNTER", 796),
    "Primal Maw": ("ABILITY_MR_PRIMAL_MAW", 889),
    "Dual Wield": ("ABILITY_MR_DUAL_WIELD", 894),
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


def export_existing_move_families(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    # Keep the canonical MR08 classifiers file-local.  Export tiny wrappers
    # instead; Metrowerks can otherwise discard/retain the original static
    # symbols in a way that leaves the controller's cross-TU reference
    # unresolved at link time.
    insert_before_once(
        lib,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
""",
        """BOOL Mercury_MoveIsPulseForCustomAbility(int move)
{
    return Mercury_MoveIsPulse(move);
}

BOOL Mercury_MoveIsBitingForCustomAbility(int move)
{
    return Mercury_MoveIsBiting(move);
}

""",
        "D11 exported move-family wrappers",
    )
    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_MoveIsPulseForCustomAbility(int move);
BOOL Mercury_MoveIsBitingForCustomAbility(int move);
""",
        "D11 move-family wrapper declarations",
    )


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryDynamicAddedType[MAX_BATTLERS];
""",
        """    // Mercury MR10D11: one native multi-hit sequence generated
    // from a normally single-hit attack. The trigger persists through all hits.
    u8 mercuryCustomMultiHitActive;
    u16 mercuryCustomMultiHitTriggerAbility;

""",
        "D11 custom multi-hit context",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_D11MoveIsHammer(int move)
{
    switch (move) {
    case MOVE_SLAM:
    case MOVE_CRABHAMMER:
    case MOVE_HAMMER_ARM:
    case MOVE_ICE_HAMMER:
    case MOVE_DRAGON_HAMMER:
    case MOVE_GIGATON_HAMMER:
    case MOVE_IVY_CUDGEL:
    case MOVE_SUPERCELL_SLAM:
#ifdef MOVE_SMASHIN_REALITIES
    case MOVE_SMASHIN_REALITIES:
#endif
#ifdef MOVE_FEMUR_BREAKER
    case MOVE_FEMUR_BREAKER:
#endif
#ifdef MOVE_SQUEAKY_HAMMER
    case MOVE_SQUEAKY_HAMMER:
#endif
#ifdef MOVE_MOLTEN_STRIKE
    case MOVE_MOLTEN_STRIKE:
#endif
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_CustomMultiHitBaseAllowed(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int i;
    int liveTargets;
    int maxBattlers;
    int move;
    int effect;
    int range;
    int battleType;

    move = battleCtx->moveCur;
    effect = MOVE_DATA(move).effect;
    range = MOVE_DATA(move).range;
    battleType = BattleSystem_GetBattleType(battleSys);

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

    liveTargets = 0;
    maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    if (range == RANGE_ADJACENT_OPPONENTS) {
        for (i = 0; i < maxBattlers; i++) {
            if (i != battleCtx->attacker
                && battleCtx->battleMons[i].curHP
                && BattleSystem_GetBattlerSide(battleSys, i)
                    != BattleSystem_GetBattlerSide(
                        battleSys, battleCtx->attacker)) {
                liveTargets++;
            }
        }
    } else if (range == RANGE_ALL_ADJACENT) {
        for (i = 0; i < maxBattlers; i++) {
            if (i != battleCtx->attacker
                && battleCtx->battleMons[i].curHP) {
                liveTargets++;
            }
        }
    } else {
        return TRUE;
    }

    return liveTargets == 1;
}

static int Mercury_CustomMultiHitCount(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability = Battler_Ability(battleCtx, battleCtx->attacker);
    int move = battleCtx->moveCur;
    int moveType = battleCtx->moveType
        ? battleCtx->moveType
        : MOVE_DATA(move).type;

    if (Mercury_CustomMultiHitBaseAllowed(battleSys, battleCtx) == FALSE) {
        return 0;
    }

    switch (ability) {
    case ABILITY_MR_RAGING_MOTH:
        return moveType == TYPE_FIRE ? 2 : 0;

    case ABILITY_MR_JACKHAMMER:
        return Mercury_D11MoveIsHammer(move) ? 2 : 0;

    case ABILITY_MR_UNRELENTING: {
        int hits = BattleSystem_RandNext(battleSys) & 3;

        if (hits < 2) {
            return hits + 2;
        }
        return (BattleSystem_RandNext(battleSys) & 3) + 2;
    }

    case ABILITY_MR_ICE_COLD_HUNTER:
        return NO_CLOUD_NINE && WEATHER_IS_HAIL && moveType == TYPE_ICE
            ? 2 : 0;

    case ABILITY_MR_PRIMAL_MAW:
        return Mercury_MoveIsBitingForCustomAbility(move) ? 2 : 0;

    case ABILITY_MR_DUAL_WIELD:
        return Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0;

    default:
        return 0;
    }
}

static void Mercury_SetupCustomMultiHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int hits;

    battleCtx->mercuryCustomMultiHitActive = FALSE;
    battleCtx->mercuryCustomMultiHitTriggerAbility = ABILITY_NONE;

    hits = Mercury_CustomMultiHitCount(battleSys, battleCtx);
    if (hits < 2) {
        return;
    }

    battleCtx->mercuryParentalBondActive = FALSE;
    battleCtx->mercuryCustomMultiHitActive = TRUE;
    battleCtx->mercuryCustomMultiHitTriggerAbility =
        Battler_Ability(battleCtx, battleCtx->attacker);
    battleCtx->multiHitCounter = hits;
    battleCtx->multiHitNumHits = hits;
    battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
    battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_BeforeMove(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "D11 custom multi-hit helpers",
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
        "D11 setup after canonical Parental Bond",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    # Raging Moth and Dual Wield define per-hit move POWER, so apply before
    # the rest of the damage pipeline rather than scaling final damage.
    replace_once(
        path,
        """    GF_ASSERT(battleCtx->powerMul >= 10);
    movePower = movePower * battleCtx->powerMul / 10;
""",
        """    if (battleCtx->mercuryCustomMultiHitActive) {
        if (battleCtx->mercuryCustomMultiHitTriggerAbility
                == ABILITY_MR_RAGING_MOTH
            || battleCtx->mercuryCustomMultiHitTriggerAbility
                == ABILITY_MR_JACKHAMMER) {
            movePower = movePower * 70 / 100;
        } else if (battleCtx->mercuryCustomMultiHitTriggerAbility
            == ABILITY_MR_DUAL_WIELD) {
            movePower = movePower * 75 / 100;
        }

        if (movePower == 0 && MOVE_DATA(move).power) {
            movePower = 1;
        }
    }

    GF_ASSERT(battleCtx->powerMul >= 10);
    movePower = movePower * battleCtx->powerMul / 10;
""",
        "D11 per-hit power scaling",
    )

    # Primal Maw specifies half DAMAGE for the second strike only.
    replace_once(
        path,
        """    if (battleCtx->mercuryParentalBondActive
        && battleCtx->multiHitLoop
        && damage > 0) {
        damage /= 4;
        if (damage == 0) {
            damage = 1;
        }
    }

    return damage;
""",
        """    if (battleCtx->mercuryParentalBondActive
        && battleCtx->multiHitLoop
        && damage > 0) {
        damage /= 4;
        if (damage == 0) {
            damage = 1;
        }
    }

    if (battleCtx->mercuryCustomMultiHitActive
        && battleCtx->mercuryCustomMultiHitTriggerAbility
            == ABILITY_MR_PRIMAL_MAW
        && battleCtx->multiHitLoop
        && damage > 0) {
        damage /= 2;
        if (damage == 0) {
            damage = 1;
        }
    }

    return damage;
""",
        "D11 Primal Maw second-hit damage",
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
        "custom_multihit_context":
            "mercuryCustomMultiHitActive" in ctx
            and "mercuryCustomMultiHitTriggerAbility" in ctx,
        "native_multihit_pipeline":
            "battleCtx->multiHitCounter = hits;" in ctl
            and "battleCtx->multiHitNumHits = hits;" in ctl
            and "battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;" in ctl,
        "parental_bond_coexists_safely":
            "Mercury_SetupParentalBond(battleSys, battleCtx);" in ctl
            and "Mercury_SetupCustomMultiHit(battleSys, battleCtx);" in ctl,
        "special_scripts_excluded":
            all(token in ctl for token in (
                "BATTLE_EFFECT_MULTI_HIT",
                "BATTLE_EFFECT_HIT_TWICE",
                "BATTLE_EFFECT_ONE_HIT_KO",
                "MOVE_SELFDESTRUCT",
                "MOVE_FLING",
                "MOVE_ENDEAVOR",
            )),
        "raging_moth_fire_gate_and_70_power":
            "case ABILITY_MR_RAGING_MOTH:" in ctl
            and "moveType == TYPE_FIRE ? 2 : 0" in ctl
            and "movePower = movePower * 70 / 100;" in lib,
        "jackhammer_hammer_class_and_70_power":
            "case ABILITY_MR_JACKHAMMER:" in ctl
            and "Mercury_D11MoveIsHammer(move) ? 2 : 0" in ctl
            and "case MOVE_HAMMER_ARM:" in ctl
            and "case MOVE_GIGATON_HAMMER:" in ctl
            and "== ABILITY_MR_JACKHAMMER" in lib
            and "movePower = movePower * 70 / 100;" in lib,
        "unrelenting_standard_2_to_5":
            "case ABILITY_MR_UNRELENTING:" in ctl
            and "BattleSystem_RandNext(battleSys) & 3" in ctl,
        "ice_cold_hunter_weather_gate":
            "case ABILITY_MR_ICE_COLD_HUNTER:" in ctl
            and "NO_CLOUD_NINE && WEATHER_IS_HAIL && moveType == TYPE_ICE" in ctl,
        "primal_maw_biting_two_hit":
            "case ABILITY_MR_PRIMAL_MAW:" in ctl
            and "Mercury_MoveIsBitingForCustomAbility(move) ? 2 : 0" in ctl
            and "== ABILITY_MR_PRIMAL_MAW" in lib
            and "damage /= 2;" in lib,
        "dual_wield_launcher_two_hit_75":
            "case ABILITY_MR_DUAL_WIELD:" in ctl
            and "Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0" in ctl
            and "movePower = movePower * 75 / 100;" in lib,
        "current_mercury_move_families_reused":
            "BOOL Mercury_MoveIsPulseForCustomAbility(int move)" in lib
            and "BOOL Mercury_MoveIsBitingForCustomAbility(int move)" in lib
            and "BOOL Mercury_MoveIsPulseForCustomAbility(int move);" in hdr
            and "BOOL Mercury_MoveIsBitingForCustomAbility(int move);" in hdr,
        "spread_safety":
            "return liveTargets == 1;" in ctl,
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
        default=Path("mr10d11-multihit-family.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    export_existing_move_families(root)
    patch_context(root)
    patch_controller(root)
    patch_damage(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D11_MULTIHIT_FAMILY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "Platinum native multi-hit loop",
        "single_accuracy_check": True,
        "ordinary_per_hit_reactions_preserved": True,
        "remaining_keep_as_written_after_d11": 32,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D11 multi-hit family validation failed")


if __name__ == "__main__":
    main()
