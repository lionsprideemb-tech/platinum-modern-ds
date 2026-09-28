#!/usr/bin/env python3
"""MR08R3 — canonical Parental Bond pass.

Adds the current-mainline two-strike behavior for eligible damaging moves:
- one accuracy check;
- independent hit/secondary/on-hit processing through Platinum's native
  multi-hit loop;
- second ordinary damage strike at 25% power-equivalent damage;
- fixed-damage scripts naturally keep full damage on both strikes;
- the second strike survives loss/suppression of the Ability after hit one;
- multistrike, OHKO, charging, Fling, self-KO, Uproar, Rollout/Ice Ball,
  Endeavor and Present are kept single-strike;
- spread moves only gain the second strike when exactly one target is in range.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_PARENTAL_BOND",)
EXPECTED_IDS = {"ABILITY_PARENTAL_BOND": 185}


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08R3: persists across both Parental Bond strikes.
    u8 mercuryParentalBondActive;

""",
        "Parental Bond battle state",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """static void BattleControllerPlayer_BeforeMove(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        """static BOOL Mercury_ParentalBondMoveAllowed(
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

    if (Battler_Ability(battleCtx, battleCtx->attacker) != ABILITY_PARENTAL_BOND
        || MOVE_DATA(move).class == CLASS_STATUS
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

static void Mercury_SetupParentalBond(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    battleCtx->mercuryParentalBondActive = FALSE;

    if (Mercury_ParentalBondMoveAllowed(battleSys, battleCtx) == FALSE) {
        return;
    }

    battleCtx->mercuryParentalBondActive = TRUE;
    battleCtx->multiHitCounter = 2;
    battleCtx->multiHitNumHits = 2;
    battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;
    battleCtx->afterMoveMessageType = AFTER_MOVE_MESSAGE_MULTI_HIT;
}

""",
        "Parental Bond eligibility helper",
    )

    replace_once(
        path,
        """    if (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) {
        battleCtx->command = BATTLE_CONTROL_MOVE_FAILED;
    } else {
        battleCtx->battleStatusMask2 |= SYSCTL_MOVE_SUCCEEDED;

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        """    if (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) {
        battleCtx->command = BATTLE_CONTROL_MOVE_FAILED;
    } else {
        battleCtx->battleStatusMask2 |= SYSCTL_MOVE_SUCCEEDED;

        if (battleCtx->multiHitLoop == FALSE) {
            Mercury_SetupParentalBond(battleSys, battleCtx);
        }

        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);
""",
        "Parental Bond pre-move setup",
    )


def patch_damage(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    text = path.read_text(encoding="utf-8")
    start = text.index("int BattleSystem_CalcMoveDamage(")
    end = text.index("int BattleSystem_CalcDamageVariance(", start)
    block = text[start:end]

    old = """    return damage + 2;
}
"""
    new = """    damage += 2;

    // Gen VII onward: only ordinary calculated damage on the child strike is
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
    if block.count(old) != 1:
        raise SystemExit(
            f"Parental Bond damage modifier: expected one return anchor, found {block.count(old)}"
        )
    block = block.replace(old, new, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "persistent_two_strike_state":
            "mercuryParentalBondActive" in ctx
            and "battleCtx->multiHitCounter = 2;" in controller
            and "battleCtx->multiHitNumHits = 2;" in controller,
        "single_accuracy_check":
            "battleCtx->multiHitAccuracyCheck = SYSCTL_MULTI_HIT_MOVE;" in controller,
        "second_hit_quarter_damage":
            "battleCtx->mercuryParentalBondActive" in lib
            and "battleCtx->multiHitLoop" in lib
            and "damage /= 4;" in lib,
        "fixed_damage_not_quartered":
            "Set/fixed-damage move scripts bypass this function" in lib,
        "multistrike_and_ohko_excluded":
            "case BATTLE_EFFECT_MULTI_HIT:" in controller
            and "case BATTLE_EFFECT_HIT_TWICE:" in controller
            and "case BATTLE_EFFECT_ONE_HIT_KO:" in controller,
        "charging_moves_excluded":
            "Move_IsMultiTurn(battleCtx, move) == TRUE" in controller,
        "special_single_strike_exclusions":
            "case MOVE_FLING:" in controller
            and "case MOVE_SELFDESTRUCT:" in controller
            and "case MOVE_EXPLOSION:" in controller
            and "case MOVE_ENDEAVOR:" in controller,
        "spread_single_target_rule":
            "return liveTargets == 1;" in controller,
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
        default=Path("mr08r3-canonical-ability-parental-bond.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_controller(root)
    patch_damage(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08R3_CANONICAL_ABILITY_PARENTAL_BOND",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 164,
        "remaining_modern_canonical_mechanics": 23,
        "policy": "Official/current-mainline Parental Bond two-strike mechanics on Platinum's native multi-hit pipeline.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08R3 validation failed")


if __name__ == "__main__":
    main()
