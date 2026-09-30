#!/usr/bin/env python3
"""MR10R3 — restore contact/reaction/priority historical Ability batch.

Implements six recovered Elite Redux v2.65 beta mechanics on Mercury's
already-established DS battle hooks:

- Pretty Privilege
- Crushing Jaw
- Envenom
- Fragrant Daze
- Haunting Frenzy
- Puffy
"""

from __future__ import annotations
import argparse, json
from pathlib import Path

IMPLEMENTED = {
    "Pretty Privilege": ("ABILITY_CUTE_ANTECEDENCE", 382),
    "Crushing Jaw": ("ABILITY_CRUSHING_JAW", 379),
    "Envenom": ("ABILITY_ENVENOM", 410),
    "Fragrant Daze": ("ABILITY_FRAGRANT_DAZE", 429),
    "Haunting Frenzy": ("ABILITY_HAUNTING_FRENZY", 447),
    "Puffy": ("ABILITY_PUFFY", 535),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, ins: str, marker: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, ins + anchor, 1), encoding="utf-8")


def validate_partition(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))["abilities"]
    for name, (token, aid) in IMPLEMENTED.items():
        matches = [
            r for r in rows
            if r.get("id") == aid and r.get("token") == token
        ]
        if len(matches) != 1:
            raise SystemExit(
                f"{name}: expected one reconciled ID/token row at {aid}, got {len(matches)}"
            )
        row = matches[0]
        if row.get("exact_effect") in (None, "RESTORE_PENDING_EXACT_SEMANTICS"):
            raise SystemExit(f"{name}: exact semantics not recovered")
        if row.get("runtime_enabled") is False:
            raise SystemExit(f"{name}: runtime disabled")


def patch_priority(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    anchor = """    if (battler1Priority == battler2Priority) {
"""
    ins = """    if (battler1Move != MOVE_NONE
        && battler1Ability == ABILITY_CUTE_ANTECEDENCE
        && battleCtx->battleMons[battler1].curHP
            == battleCtx->battleMons[battler1].maxHP
        && MOVE_DATA(battler1Move).type == TYPE_FAIRY) {
        battler1Priority++;
    }

    if (battler2Move != MOVE_NONE
        && battler2Ability == ABILITY_CUTE_ANTECEDENCE
        && battleCtx->battleMons[battler2].curHP
            == battleCtx->battleMons[battler2].maxHP
        && MOVE_DATA(battler2Move).type == TYPE_FAIRY) {
        battler2Priority++;
    }

"""
    insert_before_once(
        path, anchor, ins,
        "battler1Ability == ABILITY_CUTE_ANTECEDENCE",
        "Pretty Privilege action priority",
    )

    old = """    if (battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && ((Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
                && moveType == TYPE_FLYING)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_EARLY_GRAVE
                && moveType == TYPE_GHOST)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_WATER_GALE_WINGS
                && moveType == TYPE_WATER))) {
        priority++;
    }
"""
    new = """    if (battleCtx->battleMons[attacker].curHP
            == battleCtx->battleMons[attacker].maxHP
        && ((Battler_Ability(battleCtx, attacker) == ABILITY_GALE_WINGS
                && moveType == TYPE_FLYING)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_EARLY_GRAVE
                && moveType == TYPE_GHOST)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_WATER_GALE_WINGS
                && moveType == TYPE_WATER)
            || (Battler_Ability(battleCtx, attacker) == ABILITY_CUTE_ANTECEDENCE
                && moveType == TYPE_FAIRY))) {
        priority++;
    }
"""
    replace_once(path, old, new, "Pretty Privilege priority-blocker helper")


def patch_power_and_puffy(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    old = """    if (attackerParams.ability == ABILITY_STRONG_JAW
        && Mercury_MoveIsBiting(move)) {
        movePower = movePower * 15 / 10;
    }
"""
    new = """    if ((attackerParams.ability == ABILITY_STRONG_JAW
            || attackerParams.ability == ABILITY_CRUSHING_JAW)
        && Mercury_MoveIsBiting(move)) {
        movePower = movePower * 15 / 10;
    }
"""
    replace_once(path, old, new, "Crushing Jaw Strong Jaw power")

    old = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLUFFY) == TRUE) {
        if (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) {
            damage /= 2;
        }
        if (moveType == TYPE_FIRE) {
            damage *= 2;
        }
    }
"""
    new = """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_FLUFFY) == TRUE
        || Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_PUFFY) == TRUE) {
        if (MOVE_DATA(move).flags & MOVE_FLAG_MAKES_CONTACT) {
            damage /= 2;
        }
        if (moveType == TYPE_FIRE) {
            damage *= 2;
        }
    }
"""
    replace_once(path, old, new, "Puffy Fluffy family")


def patch_attacker_reactions(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
    ins = """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_CRUSHING_JAW
        && DEFENDING_MON.curHP
        && Mercury_MoveIsBiting(battleCtx->moveCur)
        && DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE] > MIN_STAT_STAGE
        && BattleSystem_RandNext(battleSys) % 2 == 0) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE;
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_update_stat_stage;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_ENVENOM
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 3) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_poison;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_FRAGRANT_DAZE
        && DEFENDING_MON.curHP
        && (DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_CONFUSION) == FALSE
        && Mercury_MoveMakesContact(
            battleCtx, battleCtx->attacker, battleCtx->moveCur)
        && BattleSystem_RandNext(battleSys) % 10 < 3) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_confuse;
        return TRUE;
    }

    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_HAUNTING_FRENZY
        && DEFENDING_MON.curHP
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 2) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_flinch_mon;
        return TRUE;
    }

"""
    insert_before_once(
        path, anchor, ins,
        "Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_ENVENOM",
        "restored offensive contact/reaction family",
    )


def patch_defender_fragrant_daze(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    case ABILITY_THERMAL_EXCHANGE: {
"""
    ins = """    case ABILITY_FRAGRANT_DAZE:
        if (ATTACKING_MON.curHP
            && (ATTACKING_MON.statusVolatile & VOLATILE_CONDITION_CONFUSION) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
            && Mercury_MoveMakesContact(
                battleCtx, battleCtx->attacker, battleCtx->moveCur)
            && BattleSystem_RandNext(battleSys) % 10 < 3) {
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            battleCtx->msgBattlerTemp = battleCtx->defender;
            *subscript = subscript_confuse;
            result = TRUE;
        }
        break;

"""
    insert_before_once(
        path, anchor, ins,
        "case ABILITY_FRAGRANT_DAZE:",
        "Fragrant Daze defensive contact proc",
    )


def patch_haunting_frenzy_ko(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    anchor = """    case ABILITY_GRIM_NEIGH:
"""
    ins = """    case ABILITY_HAUNTING_FRENZY:
        if (battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SPEED]
            < MAX_STAT_STAGE) {
            battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE;
            battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
            battleCtx->sideEffectMon = battleCtx->attacker;
            *subscript = subscript_update_stat_stage;
            return TRUE;
        }
        break;

"""
    insert_before_once(
        path, anchor, ins,
        "case ABILITY_HAUNTING_FRENZY:",
        "Haunting Frenzy KO Speed boost",
    )


def update_registry(path: Path) -> None:
    rows = [x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    for token in TOKENS:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    abilities = [
        x.strip()
        for x in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    reg = set(registry.read_text(encoding="utf-8").splitlines())
    checks = {
        "pretty_privilege_priority":
            "ABILITY_CUTE_ANTECEDENCE" in lib
            and "moveType == TYPE_FAIRY" in lib,
        "crushing_jaw_power_and_drop":
            "ABILITY_CRUSHING_JAW" in lib
            and "MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE" in lib,
        "envenom_30_percent_poison":
            "ABILITY_ENVENOM" in lib
            and "subscript_poison" in lib,
        "fragrant_daze_bidirectional":
            lib.count("ABILITY_FRAGRANT_DAZE") >= 2
            and "subscript_confuse" in lib,
        "haunting_frenzy_flinch_and_ko_speed":
            lib.count("ABILITY_HAUNTING_FRENZY") >= 2
            and "subscript_flinch_mon" in lib
            and "MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE" in lib,
        "puffy_fluffy_family":
            "ABILITY_PUFFY) == TRUE" in lib
            and "moveType == TYPE_FIRE" in lib,
        "registry_updated": all(token in reg for token in TOKENS),
        "ids_stable": all(
            len(abilities) > aid and abilities[aid] == token
            for token, aid in IMPLEMENTED.values()
        ),
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--partition",
        type=Path,
        default=Path("data/mr10_ability_partition_16bit_full_identity.json"),
    )
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr10r3-reaction-priority.json"),
    )
    a = ap.parse_args()
    root = a.pokeplatinum_root.resolve()

    validate_partition(a.partition.resolve())
    patch_priority(root)
    patch_power_and_puffy(root)
    patch_attacker_reactions(root)
    patch_defender_fragrant_daze(root)
    patch_haunting_frenzy_ko(root)
    update_registry(a.implemented_registry.resolve())

    checks = validate(root, a.implemented_registry.resolve())
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10R3_REACTION_PRIORITY",
        "status": status,
        "implemented": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "checks": checks,
    }
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10R3 validation failed")


if __name__ == "__main__":
    main()
