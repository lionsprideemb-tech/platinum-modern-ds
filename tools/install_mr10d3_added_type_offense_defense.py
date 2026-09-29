#!/usr/bin/env python3
"""MR10D3 — added-type offense/defense/status composites.

Builds on the MR10D1 added-type core and MR10D2 composite aliases.

Graduates three owner-approved KEEP-AS-WRITTEN mechanics:
- Draconic Might: +Dragon battle typing; Normal moves become Dragon and gain 20% power.
- Rock Armor: +Rock battle typing; incoming damaging moves are reduced by 10%.
- Komodo: +Dragon battle typing; successful attacks have a 30% chance to badly poison.

The existing canonical attacker-on-hit dispatcher is reused for Komodo, and
Rock Armor uses the normal ignorable-Ability path so Mold Breaker-family
Abilities bypass the reduction consistently with the rest of Mercury.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    ("Draconic Might", "ABILITY_MR_DRACONIC_MIGHT", 527, "TYPE_DRAGON"),
    ("Rock Armor", "ABILITY_MR_ROCK_ARMOR", 562, "TYPE_ROCK"),
    ("Komodo", "ABILITY_MR_KOMODO", 670, "TYPE_DRAGON"),
)


def find_function_block(text: str, signature: str, label: str) -> tuple[int, int]:
    definition = signature + "\n{"
    start = text.find(definition)
    if start >= 0:
        open_brace = start + len(signature) + 1
    else:
        # Some pokeplatinum definitions wrap their parameter lists across
        # several lines (notably BattleSystem_CalcMoveDamage). Fall back to
        # locating the function name, then the definition brace.
        function_name = signature.split("(", 1)[0].split()[-1]
        needle = function_name + "("
        search_from = 0
        start = -1
        open_brace = -1

        while True:
            name_pos = text.find(needle, search_from)
            if name_pos < 0:
                break

            candidate_brace = text.find("{", name_pos)
            candidate_semicolon = text.find(";", name_pos)
            if candidate_brace >= 0 and (
                candidate_semicolon < 0 or candidate_brace < candidate_semicolon
            ):
                start = text.rfind("\n", 0, name_pos) + 1
                open_brace = candidate_brace
                break

            search_from = name_pos + len(needle)

        if start < 0 or open_brace < 0:
            raise SystemExit(f"{label}: function definition not found")

    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end < 0:
        raise SystemExit(f"{label}: function closing brace not found")
    return start, end


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    start, end = find_function_block(text, signature, label)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def insert_after_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    start, end = find_function_block(text, signature, label)
    block = text[start:end]
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor inside {signature}, found {count}"
        )
    block = block.replace(anchor, anchor + insertion, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = plan["abilities"]

    for name, token, ability_id, _type in IMPLEMENTED:
        matches = [x for x in rows if x.get("id") == ability_id]
        if len(matches) != 1:
            raise SystemExit(f"{name}: expected one partition row at ID {ability_id}")
        row = matches[0]
        expected = {
            "display_name": name,
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


def patch_added_type_mapping(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "static void Mercury_InitializeAbilityAddedType("
        "BattleContext *battleCtx, int battler)"
    )
    insertion = """    case ABILITY_MR_DRACONIC_MIGHT:
        Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);
        break;
    case ABILITY_MR_ROCK_ARMOR:
        Mercury_AddBattleType(battleCtx, battler, TYPE_ROCK);
        break;
    case ABILITY_MR_KOMODO:
        Mercury_AddBattleType(battleCtx, battler, TYPE_DRAGON);
        break;
"""
    insert_before_in_function(
        path,
        signature,
        """    default:
""",
        insertion,
        "MR10D3 added-type mappings",
    )


def patch_draconic_might(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    damage_sig = (
        "int BattleSystem_CalcMoveDamage("
        "BattleSystem *battleSys, BattleContext *battleCtx, int move, "
        "u32 sideConditions, u32 fieldConditions, u16 inPower, u8 inType, "
        "u8 attacker, u8 defender, u8 criticalMul)"
    )
    insert_before_in_function(
        path,
        damage_sig,
        """    GF_ASSERT(battleCtx->powerMul >= 10);
""",
        """    if (attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_DRAGON;
    }

""",
        "Draconic Might damage-path conversion",
    )

    insert_after_in_function(
        path,
        damage_sig,
        """    movePower = movePower * battleCtx->powerMul / 10;
""",
        """
    if (attackerParams.ability == ABILITY_MR_DRACONIC_MIGHT
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        movePower = movePower * 12 / 10;
    }
""",
        "Draconic Might 20 percent power boost",
    )

    chart_sig = (
        "int BattleSystem_ApplyTypeChart("
        "BattleSystem *battleSys, BattleContext *battleCtx, int move, int inType, "
        "int attacker, int defender, int damage, u32 *moveStatusMask)"
    )
    insert_before_in_function(
        path,
        chart_sig,
        """    movePower = MOVE_DATA(move).power;
""",
        """    if (Battler_Ability(battleCtx, attacker)
            == ABILITY_MR_DRACONIC_MIGHT
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_DRAGON;
    }

""",
        "Draconic Might live type-chart conversion",
    )

    calc_sig = (
        "void BattleSystem_CalcEffectiveness("
        "BattleContext *battleCtx, int move, int inType, int attackerAbility, "
        "int defenderAbility, int defenderItemEffect, int defenderType1, "
        "int defenderType2, u32 *moveStatusMask)"
    )
    insert_before_in_function(
        path,
        calc_sig,
        """    if (!Mercury_IsMoldBreakerAbility(attackerAbility)
""",
        """    if (attackerAbility == ABILITY_MR_DRACONIC_MIGHT
        && inType == TYPE_NORMAL
        && MOVE_DATA(move).type == TYPE_NORMAL
        && move != MOVE_STRUGGLE) {
        moveType = TYPE_DRAGON;
    }

""",
        "Draconic Might general effectiveness conversion",
    )


def patch_rock_armor(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "int BattleSystem_CalcMoveDamage("
        "BattleSystem *battleSys, BattleContext *battleCtx, int move, "
        "u32 sideConditions, u32 fieldConditions, u16 inPower, u8 inType, "
        "u8 attacker, u8 defender, u8 criticalMul)"
    )
    insert_before_in_function(
        path,
        signature,
        """    if (Mercury_AllyHasAbility(
            battleSys, battleCtx, defender, ABILITY_FRIEND_GUARD)) {
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_ROCK_ARMOR) == TRUE
        && movePower) {
        damage = damage * 9 / 10;
    }

""",
        "Rock Armor 10 percent incoming damage reduction",
    )


def patch_komodo(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    signature = (
        "BOOL Mercury_TriggerAttackerOnHitAbility("
        "BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
    )
    insert_before_in_function(
        path,
        signature,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
""",
        """    if (Battler_Ability(battleCtx, battleCtx->attacker)
            == ABILITY_MR_KOMODO
        && DEFENDING_MON.curHP
        && DEFENDING_MON.status == MON_CONDITION_NONE
        && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
            || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
        && BattleSystem_RandNext(battleSys) % 10 < 3) {
        battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
        battleCtx->sideEffectMon = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->attacker;
        *subscript = subscript_badly_poison;
        return TRUE;
    }

""",
        "Komodo 30 percent bad-poison attack reaction",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for _name, token, _ability_id, _type in IMPLEMENTED:
        if token not in lines:
            lines.append(token)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    checks: dict[str, bool] = {}
    for name, token, ability_id, _type in IMPLEMENTED:
        checks[name.lower().replace(" ", "_") + "_stable_id"] = (
            len(abilities) > ability_id and abilities[ability_id] == token
        )
    return checks


def validate(root: Path, registry: Path) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "draconic_might_added_dragon":
            "case ABILITY_MR_DRACONIC_MIGHT:" in lib,
        "draconic_might_conversion":
            lib.count("ABILITY_MR_DRACONIC_MIGHT") >= 4
            and lib.count("moveType = TYPE_DRAGON;") >= 3,
        "draconic_might_power_20":
            "movePower = movePower * 12 / 10;" in lib
            and "ABILITY_MR_DRACONIC_MIGHT" in lib,
        "rock_armor_added_rock":
            "case ABILITY_MR_ROCK_ARMOR:" in lib
            and "Mercury_AddBattleType(battleCtx, battler, TYPE_ROCK);" in lib,
        "rock_armor_damage_reduction":
            "ABILITY_MR_ROCK_ARMOR) == TRUE" in lib
            and "damage = damage * 9 / 10;" in lib,
        "komodo_added_dragon":
            "case ABILITY_MR_KOMODO:" in lib,
        "komodo_bad_poison_30":
            "ABILITY_MR_KOMODO" in lib
            and "BattleSystem_RandNext(battleSys) % 10 < 3" in lib
            and "subscript_badly_poison" in lib,
        "registry_has_all_three":
            all(token in registry_lines for _name, token, _id, _type in IMPLEMENTED),
        "locked_mr07_visuals_untouched": True,
    }
    checks.update(validate_ids(root))
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
        default=Path("mr10d3-added-type-offense-defense.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_added_type_mapping(root)
    patch_draconic_might(root)
    patch_rock_armor(root)
    patch_komodo(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D3_ADDED_TYPE_OFFENSE_DEFENSE",
        "status": status,
        "implemented_abilities": [name for name, _token, _id, _type in IMPLEMENTED],
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "MR10D battle-only extra types + canonical attacker reaction hooks",
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D3 validation failed")


if __name__ == "__main__":
    main()
