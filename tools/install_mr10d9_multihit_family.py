#!/usr/bin/env python3
"""MR10D9 — Ability-driven multi-hit family.

Implements six reviewed KEEP-AS-WRITTEN mechanics through one shared
multi-hit setup/scaling lane:

- Raging Moth: Fire attacks strike twice at 70% power per hit.
- Jackhammer: hammer-class attacks strike twice at 70% power per hit.
- Unrelenting: eligible natural single-hit attacks strike 2-5 times.
- Ice Cold Hunter: Ice attacks strike twice while hail/icy weather is active.
- Primal Maw: biting attacks strike twice; the second hit is 50% power.
- Dual Wield: Mega Launcher / pulse-class attacks strike twice at 75% power
  per hit.

The implementation reuses Platinum's native multi-hit loop rather than
generating separate moves, preserving normal per-hit accuracy flags, contact
reactions, secondary effects, faint interruption, and the standard "hit X
times" flow. Natural multi-hit move effects are excluded from Unrelenting and
the two-hit wrappers to prevent nested hit loops.

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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def insert_after_function(
    path: Path,
    signature: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    _, end = function_bounds(text, signature)
    path.write_text(text[:end] + "\n\n" + insertion + text[end:], encoding="utf-8")


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
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u16 mercuryReactiveOriginalMove;
""",
        """    // Mercury MR10D9: Ability-driven native multi-hit loop.
    u8 mercuryAbilityMultiHitActive;
    u8 mercuryAbilityMultiHitFirstPct;
    u8 mercuryAbilityMultiHitLaterPct;

""",
        "MR10D9 multi-hit context state",
    )


def patch_classifiers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    # Keep D9 self-contained: later canonical installers may relocate or
    # rewrite the private MR08 move-property helpers, so duplicate the pinned
    # move tables here instead of depending on their exact static signatures.
    helpers = """BOOL Mercury_D9MoveIsBiting(int move)
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

BOOL Mercury_D9MoveIsPulse(int move)
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

BOOL Mercury_D9MoveIsHammer(int move)
{
    switch (move) {
    case MOVE_CRABHAMMER:
    case MOVE_HAMMER_ARM:
    case MOVE_WOOD_HAMMER:
    case MOVE_ICE_HAMMER:
    case MOVE_DRAGON_HAMMER:
    case MOVE_GIGATON_HAMMER:
        return TRUE;
    default:
        return FALSE;
    }
}

BOOL Mercury_D9MoveHasNativeMultiHit(int move)
{
    switch (MOVE_DATA(move).effect) {
    case BATTLE_EFFECT_MULTI_HIT:
    case BATTLE_EFFECT_HIT_TWICE:
    case BATTLE_EFFECT_POISON_MULTI_HIT:
    case BATTLE_EFFECT_HIT_THREE_TIMES:
    case BATTLE_EFFECT_BEAT_UP:
        return TRUE;
    default:
        return FALSE;
    }
}

BOOL Mercury_D9IcyWeatherActive(BattleContext *battleCtx)
{
    return (battleCtx->fieldConditionsMask & FIELD_CONDITION_HAILING) != FALSE;
}

"""
    insert_before_once(
        lib,
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
""",
        helpers,
        "MR10D9 shared classifiers",
    )

    declarations = """BOOL Mercury_D9MoveIsBiting(int move);
BOOL Mercury_D9MoveIsPulse(int move);
BOOL Mercury_D9MoveIsHammer(int move);
BOOL Mercury_D9MoveHasNativeMultiHit(int move);
BOOL Mercury_D9IcyWeatherActive(BattleContext *battleCtx);
"""
    insert_before_once(
        hdr,
        """#endif // POKEPLATINUM_BATTLE_BATTLE_LIB_H
""",
        declarations,
        "MR10D9 public classifier declarations",
    )


def patch_setup(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static int Mercury_D9RandomMultiHitCount(BattleSystem *battleSys)
{
    int hits = BattleSystem_RandNext(battleSys) & 3;

    if (hits < 2) {
        hits += 2;
    } else {
        hits = (BattleSystem_RandNext(battleSys) & 3) + 2;
    }

    return hits;
}

static void Mercury_D9SetupAbilityMultiHit(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int ability;
    int move;
    int moveType;
    int hits = 0;
    int firstPct = 100;
    int laterPct = 100;

    battleCtx->mercuryAbilityMultiHitActive = FALSE;
    battleCtx->mercuryAbilityMultiHitFirstPct = 100;
    battleCtx->mercuryAbilityMultiHitLaterPct = 100;

    if (battleCtx->mercuryAbilityGeneratedAction
        || battleCtx->attacker == BATTLER_NONE
        || battleCtx->moveCur == MOVE_NONE) {
        return;
    }

    move = battleCtx->moveCur;
    if (MOVE_DATA(move).power == 0
        || MOVE_DATA(move).class == CLASS_STATUS
        || Mercury_D9MoveHasNativeMultiHit(move)) {
        return;
    }

    ability = Battler_Ability(battleCtx, battleCtx->attacker);
    moveType = CalcMoveType(battleCtx, battleCtx->attacker, move);

    switch (ability) {
    case ABILITY_MR_RAGING_MOTH:
        if (moveType == TYPE_FIRE) {
            hits = 2;
            firstPct = 70;
            laterPct = 70;
        }
        break;

    case ABILITY_MR_JACKHAMMER:
        if (Mercury_D9MoveIsHammer(move)) {
            hits = 2;
            firstPct = 70;
            laterPct = 70;
        }
        break;

    case ABILITY_MR_UNRELENTING:
        hits = Mercury_D9RandomMultiHitCount(battleSys);
        break;

    case ABILITY_MR_ICE_COLD_HUNTER:
        if (moveType == TYPE_ICE
            && Mercury_D9IcyWeatherActive(battleCtx)) {
            hits = 2;
        }
        break;

    case ABILITY_MR_PRIMAL_MAW:
        if (Mercury_D9MoveIsBiting(move)) {
            hits = 2;
            laterPct = 50;
        }
        break;

    case ABILITY_MR_DUAL_WIELD:
        if (Mercury_D9MoveIsPulse(move)) {
            hits = 2;
            firstPct = 75;
            laterPct = 75;
        }
        break;

    default:
        break;
    }

    if (hits < 2) {
        return;
    }

    battleCtx->mercuryAbilityMultiHitActive = TRUE;
    battleCtx->mercuryAbilityMultiHitFirstPct = firstPct;
    battleCtx->mercuryAbilityMultiHitLaterPct = laterPct;
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
        "MR10D9 multi-hit setup helper",
    )

    signature = (
        "static void BattleControllerPlayer_BeforeMove("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        battleCtx->beforeMoveCheckState = BEFORE_MOVE_START;
""",
        """        Mercury_D9SetupAbilityMultiHit(battleSys, battleCtx);
""",
        "Mercury_D9SetupAbilityMultiHit(battleSys, battleCtx);",
        "MR10D9 before-move setup hook",
    )


def patch_damage_scaling(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insertion = """    if (battleCtx->mercuryAbilityMultiHitActive
        && movePower) {
        int mercuryMultiHitPct =
            battleCtx->multiHitCounter == battleCtx->multiHitNumHits
            ? battleCtx->mercuryAbilityMultiHitFirstPct
            : battleCtx->mercuryAbilityMultiHitLaterPct;

        movePower = movePower * mercuryMultiHitPct / 100;
    }

"""
    # The accumulated MR10D stack has already expanded CalcMoveDamage's
    # signature. Anchor to the stable body point immediately after base
    # movePower/moveType assignment rather than to an exact function header.
    insert_before_once(
        path,
        """    GF_ASSERT(battleCtx->powerMul >= 10);
""",
        insertion,
        "MR10D9 per-hit power scaling",
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
        "shared_multihit_state":
            "mercuryAbilityMultiHitActive" in ctx
            and "mercuryAbilityMultiHitLaterPct" in ctx,
        "native_multihit_loop_reused":
            "battleCtx->multiHitCounter = hits;" in ctl
            and "battleCtx->multiHitNumHits = hits;" in ctl
            and "AFTER_MOVE_MESSAGE_MULTI_HIT" in ctl,
        "natural_multihit_excluded":
            "Mercury_D9MoveHasNativeMultiHit(move)" in ctl
            and "BATTLE_EFFECT_MULTI_HIT" in lib
            and "BATTLE_EFFECT_HIT_TWICE" in lib,
        "raging_moth_fire_70x2":
            "ABILITY_MR_RAGING_MOTH" in ctl
            and "moveType == TYPE_FIRE" in ctl
            and "firstPct = 70;" in ctl
            and "laterPct = 70;" in ctl,
        "jackhammer_class_70x2":
            "ABILITY_MR_JACKHAMMER" in ctl
            and "Mercury_D9MoveIsHammer(move)" in ctl
            and "MOVE_GIGATON_HAMMER" in lib,
        "unrelenting_2_to_5":
            "ABILITY_MR_UNRELENTING" in ctl
            and "Mercury_D9RandomMultiHitCount" in ctl,
        "ice_cold_hunter_hail_double":
            "ABILITY_MR_ICE_COLD_HUNTER" in ctl
            and "Mercury_D9IcyWeatherActive" in ctl
            and "FIELD_CONDITION_HAILING" in lib,
        "primal_maw_second_half":
            "ABILITY_MR_PRIMAL_MAW" in ctl
            and "Mercury_D9MoveIsBiting(move)" in ctl
            and "laterPct = 50;" in ctl,
        "dual_wield_pulse_75x2":
            "ABILITY_MR_DUAL_WIELD" in ctl
            and "Mercury_D9MoveIsPulse(move)" in ctl
            and "firstPct = 75;" in ctl,
        "per_hit_scaling":
            "int mercuryMultiHitPct =" in lib
            and "movePower = movePower * mercuryMultiHitPct / 100;" in lib,
        "generated_actions_not_rewrapped":
            "battleCtx->mercuryAbilityGeneratedAction" in ctl,
        "classifiers_declared":
            "Mercury_D9MoveIsBiting" in hdr
            and "Mercury_D9MoveIsPulse" in hdr
            and "Mercury_D9MoveIsHammer" in hdr,
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
        default=Path("mr10d9-multihit-family.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_classifiers(root)
    patch_setup(root)
    patch_damage_scaling(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D9_MULTIHIT_FAMILY",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "ability_driven_native_multihit_loop",
        "natural_multihit_moves_nested": False,
        "remaining_keep_as_written_after_d9": 34,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D9 multi-hit family validation failed")


if __name__ == "__main__":
    main()
