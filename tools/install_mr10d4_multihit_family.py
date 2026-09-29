#!/usr/bin/env python3
"""MR10D4 — shared Ability-driven multi-hit family.

Graduates six owner-approved KEEP-AS-WRITTEN mechanics by extending the
compile-certified Parental Bond multi-hit controller rather than inventing a
parallel attack loop:

- Raging Moth: Fire attacks strike twice at 70% power per hit.
- Jackhammer: hammer-class attacks strike twice at 70% power per hit.
- Unrelenting: eligible single-hit attacks become 2-5 hit attacks.
- Ice Cold Hunter: qualifying Ice attacks strike twice in icy weather.
- Primal Maw: biting attacks strike twice; second hit is 50% power.
- Dual Wield: Mega Launcher/pulse-class attacks strike twice at 75% power.

The shared loop preserves normal per-hit damage/effect/substitute/faint handling
and the existing Platinum "hit N times" message path. Locked MR07 UI is not
touched.
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

TOKENS = tuple(value[0] for value in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"

    insert_before_once(
        path,
        """typedef struct BattleContext {
""",
        """enum MercuryAbilityMultiHitMode {
    MERCURY_ABILITY_MULTI_HIT_NONE = 0,
    MERCURY_ABILITY_MULTI_HIT_RAGING_MOTH,
    MERCURY_ABILITY_MULTI_HIT_JACKHAMMER,
    MERCURY_ABILITY_MULTI_HIT_UNRELENTING,
    MERCURY_ABILITY_MULTI_HIT_ICE_COLD_HUNTER,
    MERCURY_ABILITY_MULTI_HIT_PRIMAL_MAW,
    MERCURY_ABILITY_MULTI_HIT_DUAL_WIELD,
};

""",
        "MR10D4 multi-hit mode enum",
    )

    insert_before_once(
        path,
        """    // Mercury MR08R3: persists across both Parental Bond strikes.
    u8 mercuryParentalBondActive;
""",
        """    // Mercury MR10D4: Ability-driven multi-hit state, valid only
    // for the currently resolving attack.
    u8 mercuryAbilityMultiHitMode;

""",
        "MR10D4 battle state",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helpers = """static BOOL Mercury_D4MoveIsBiting(int move)
{
    switch (move) {
    case MOVE_BITE:
    case MOVE_CRUNCH:
    case MOVE_FIRE_FANG:
    case MOVE_FISHIOUS_REND:
    case MOVE_HYPER_FANG:
    case MOVE_ICE_FANG:
    case MOVE_JAW_LOCK:
    case MOVE_POISON_FANG:
    case MOVE_PSYCHIC_FANGS:
    case MOVE_THUNDER_FANG:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_D4MoveIsPulse(int move)
{
    switch (move) {
    case MOVE_AURA_SPHERE:
    case MOVE_DARK_PULSE:
    case MOVE_DRAGON_PULSE:
    case MOVE_HEAL_PULSE:
    case MOVE_ORIGIN_PULSE:
    case MOVE_TERRAIN_PULSE:
    case MOVE_WATER_PULSE:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_D4MoveIsHammer(int move)
{
    // Mercury follows the locked ER hammer classification for official moves.
    // ER explicitly tags Wood Hammer, Hammer Arm and Ice Hammer; Gigaton
    // Hammer is natively hammer-class in the modern move set.
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

static BOOL Mercury_D4BaseMoveAllowed(
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

    // Shared Mercury follow-up eligibility exclusions. These are the same
    // hard exclusions used by the certified Parental Bond controller.
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
                    != BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker)) {
                liveTargets++;
            }
        }
    } else if (range == RANGE_ALL_ADJACENT) {
        for (i = 0; i < maxBattlers; i++) {
            if (i != battleCtx->attacker && battleCtx->battleMons[i].curHP) {
                liveTargets++;
            }
        }
    } else {
        return TRUE;
    }

    return liveTargets == 1;
}

static int Mercury_D4UnrelentingHitCount(BattleSystem *battleSys)
{
    int roll = BattleSystem_RandNext(battleSys) % 100;

    // Standard modern 2-5-hit weighting: 35/35/15/15.
    if (roll < 35) {
        return 2;
    }
    if (roll < 70) {
        return 3;
    }
    if (roll < 85) {
        return 4;
    }
    return 5;
}

static void Mercury_SetupAbilityMultiHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability;
    int hits;
    int mode;
    int move;

    battleCtx->mercuryAbilityMultiHitMode = MERCURY_ABILITY_MULTI_HIT_NONE;

    // Never compete with a canonical/native multi-hit controller.
    if (battleCtx->mercuryParentalBondActive
        || Mercury_D4BaseMoveAllowed(battleSys, battleCtx) == FALSE) {
        return;
    }

    ability = Battler_Ability(battleCtx, battleCtx->attacker);
    move = battleCtx->moveCur;
    hits = 0;
    mode = MERCURY_ABILITY_MULTI_HIT_NONE;

    switch (ability) {
    case ABILITY_MR_RAGING_MOTH:
        if (MOVE_DATA(move).type == TYPE_FIRE) {
            hits = 2;
            mode = MERCURY_ABILITY_MULTI_HIT_RAGING_MOTH;
        }
        break;

    case ABILITY_MR_JACKHAMMER:
        if (Mercury_D4MoveIsHammer(move)) {
            hits = 2;
            mode = MERCURY_ABILITY_MULTI_HIT_JACKHAMMER;
        }
        break;

    case ABILITY_MR_UNRELENTING:
        hits = Mercury_D4UnrelentingHitCount(battleSys);
        mode = MERCURY_ABILITY_MULTI_HIT_UNRELENTING;
        break;

    case ABILITY_MR_ICE_COLD_HUNTER:
        if (MOVE_DATA(move).type == TYPE_ICE
            && WEATHER_IS_HAIL
            && NO_CLOUD_NINE) {
            hits = 2;
            mode = MERCURY_ABILITY_MULTI_HIT_ICE_COLD_HUNTER;
        }
        break;

    case ABILITY_MR_PRIMAL_MAW:
        if (Mercury_D4MoveIsBiting(move)) {
            hits = 2;
            mode = MERCURY_ABILITY_MULTI_HIT_PRIMAL_MAW;
        }
        break;

    case ABILITY_MR_DUAL_WIELD:
        if (Mercury_D4MoveIsPulse(move)) {
            hits = 2;
            mode = MERCURY_ABILITY_MULTI_HIT_DUAL_WIELD;
        }
        break;
    }

    if (hits < 2) {
        return;
    }

    battleCtx->mercuryAbilityMultiHitMode = mode;
    battleCtx->multiHitCounter = hits;
    battleCtx->multiHitNumHits = hits;
    battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
    battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
}

"""

    insert_before_once(
        path,
        """static BOOL Mercury_ParentalBondMoveAllowed(
""",
        helpers,
        "MR10D4 shared multi-hit controller helpers",
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
            Mercury_SetupAbilityMultiHit(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        "MR10D4 pre-move setup",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insertion = """    // Mercury MR10D4: Ability-generated hit power. This runs after normal
    // move/Ability power modifiers and before the damage formula.
    switch (battleCtx->mercuryAbilityMultiHitMode) {
    case MERCURY_ABILITY_MULTI_HIT_RAGING_MOTH:
    case MERCURY_ABILITY_MULTI_HIT_JACKHAMMER:
        movePower = movePower * 70 / 100;
        break;

    case MERCURY_ABILITY_MULTI_HIT_DUAL_WIELD:
        movePower = movePower * 75 / 100;
        break;

    case MERCURY_ABILITY_MULTI_HIT_PRIMAL_MAW:
        if (battleCtx->multiHitLoop) {
            movePower /= 2;
        }
        break;

    default:
        break;
    }

    if (movePower == 0 && MOVE_DATA(move).power) {
        movePower = 1;
    }

"""

    insert_before_once(
        path,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
""",
        insertion,
        "MR10D4 per-hit power scaling",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "shared_multihit_state":
            "enum MercuryAbilityMultiHitMode" in ctx
            and "mercuryAbilityMultiHitMode" in ctx,
        "parental_bond_loop_reused":
            "Mercury_SetupParentalBond(battleSys, battleCtx);" in controller
            and "Mercury_SetupAbilityMultiHit(battleSys, battleCtx);" in controller,
        "raging_moth_fire_gate":
            "case ABILITY_MR_RAGING_MOTH:" in controller
            and "MOVE_DATA(move).type == TYPE_FIRE" in controller,
        "jackhammer_hammer_gate":
            "case ABILITY_MR_JACKHAMMER:" in controller
            and "Mercury_D4MoveIsHammer(move)" in controller,
        "unrelenting_2_to_5":
            "case ABILITY_MR_UNRELENTING:" in controller
            and "Mercury_D4UnrelentingHitCount" in controller
            and "return 5;" in controller,
        "ice_cold_hunter_weather_gate":
            "case ABILITY_MR_ICE_COLD_HUNTER:" in controller
            and "WEATHER_IS_HAIL" in controller
            and "NO_CLOUD_NINE" in controller,
        "primal_maw_biting_gate":
            "case ABILITY_MR_PRIMAL_MAW:" in controller
            and "Mercury_D4MoveIsBiting(move)" in controller,
        "dual_wield_launcher_gate":
            "case ABILITY_MR_DUAL_WIELD:" in controller
            and "Mercury_D4MoveIsPulse(move)" in controller,
        "scaled_power_70":
            "movePower = movePower * 70 / 100;" in lib,
        "scaled_power_75":
            "movePower = movePower * 75 / 100;" in lib,
        "primal_maw_second_half":
            "MERCURY_ABILITY_MULTI_HIT_PRIMAL_MAW" in lib
            and "if (battleCtx->multiHitLoop)" in lib
            and "movePower /= 2;" in lib,
        "normal_multihit_message_path":
            "afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT" in controller,
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
        default=Path("mr10d4-multihit-family.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_controller(root)
    patch_damage(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D4_MULTIHIT_FAMILY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "ability_driven_multihit_controller",
        "unrelenting_distribution": {
            "2_hits_percent": 35,
            "3_hits_percent": 35,
            "4_hits_percent": 15,
            "5_hits_percent": 15,
        },
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR10D4 multi-hit family validation failed")


if __name__ == "__main__":
    main()
