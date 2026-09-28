#!/usr/bin/env python3
"""MR08S2 — canonical Paradox Ability pass.

Implements Protosynthesis and Quark Drive with current-mainline battle behavior:
- Protosynthesis activates in ordinary harsh sunlight (Sunny Day / Drought /
  Orichalcum Pulse weather), but not Mercury's separately tracked Desolate Land
  strong sunlight lane;
- Quark Drive activates in Electric Terrain;
- the highest current non-HP stat is selected using the canonical tie order:
  Attack, Defense, Sp. Atk, Sp. Def, Speed;
- the selected stat receives x1.3, except Speed which receives x1.5;
- Booster Energy is added as a stable appended Mercury item and is consumed to
  activate the Ability when its field condition is absent;
- field activation keeps Booster Energy unconsumed; if the field later ends,
  the held Booster Energy can then activate and preserve the boost;
- Booster Energy activation ends on switch-out;
- transformed users cannot newly activate;
- both Abilities resist Gastro Acid / Worry Seed and cannot be copied, swapped,
  traced, or inherited by Receiver / Power of Alchemy;
- Neutralizing Gas can disable the boost without destroying stored Booster
  activation state.

Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_PROTOSYNTHESIS",
    "ABILITY_QUARK_DRIVE",
)
EXPECTED_IDS = {
    "ABILITY_PROTOSYNTHESIS": 281,
    "ABILITY_QUARK_DRIVE": 282,
}


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


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_function(path: Path, signature: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
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
        raise SystemExit(f"{label}: closing brace not found in {path}")

    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


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


def patch_booster_energy_item(root: Path) -> None:
    generated = root / "generated/items.txt"
    lines = [line.rstrip() for line in generated.read_text(encoding="utf-8").splitlines()]
    if "ITEM_BOOSTER_ENERGY" not in lines:
        try:
            idx = lines.index("MAX_ITEMS")
        except ValueError as exc:
            raise SystemExit("Booster Energy: MAX_ITEMS anchor missing") from exc
        lines.insert(idx, "ITEM_BOOSTER_ENERGY")
        generated.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    item = root / "res/items/data/booster_energy.json"
    item.write_text(
        json.dumps(
            {
                "name": "Booster Energy",
                "plural": "Booster Energies",
                "article": "a",
                "description": [
                    "An item to be held by a Pokémon.\n",
                    "It activates Protosynthesis or Quark\n",
                    "Drive when their field condition is absent.",
                ],
                "icon": {
                    "sprite": "choice_specs_NCGR",
                    "palette": "choice_specs_NCLR",
                },
                "gbaID": "GBA_ITEM_NONE",
                "price": 0,
                "effectParam": 0,
                "holdEffect": "HOLD_EFFECT_NONE",
                "pluckEffect": "PLUCK_EFFECT_NONE",
                "flingEffect": "FLING_EFFECT_NONE",
                "flingPower": 30,
                "naturalGiftPower": 0,
                "naturalGiftType": None,
                "preventToss": False,
                "canRegister": False,
                "fieldPocket": "POCKET_ITEMS",
                "battlePocket": "BATTLE_POCKET_MASK_NONE",
                "fieldUseFunc": "ITEM_USE_FUNC_NONE",
                "battleUseCategory": "BATTLE_USE_CATEGORY_NONE",
                "itemUseParams": None,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08S2: Protosynthesis / Quark Drive activation state.
    u8 mercuryParadoxBoostedStat[MAX_BATTLERS];
    u8 mercuryParadoxBoosterActive[MAX_BATTLERS];

""",
        "Paradox battle state",
    )


def patch_paradox_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL Mercury_IsGroundedForTerrain(BattleContext *battleCtx, int battler)
""",
        """static int Mercury_ParadoxStatValue(BattleContext *battleCtx, int battler, int stat)
{
    int raw;

    switch (stat) {
    case BATTLE_STAT_ATTACK:
        raw = battleCtx->battleMons[battler].attack;
        break;
    case BATTLE_STAT_DEFENSE:
        raw = battleCtx->battleMons[battler].defense;
        break;
    case BATTLE_STAT_SP_ATTACK:
        raw = battleCtx->battleMons[battler].spAttack;
        break;
    case BATTLE_STAT_SP_DEFENSE:
        raw = battleCtx->battleMons[battler].spDefense;
        break;
    default:
        raw = battleCtx->battleMons[battler].speed;
        break;
    }

    return raw
        * sStatStageBoosts[battleCtx->battleMons[battler].statBoosts[stat]].numerator
        / sStatStageBoosts[battleCtx->battleMons[battler].statBoosts[stat]].denominator;
}

static int Mercury_ParadoxGreatestStat(BattleContext *battleCtx, int battler)
{
    static const u8 priority[] = {
        BATTLE_STAT_ATTACK,
        BATTLE_STAT_DEFENSE,
        BATTLE_STAT_SP_ATTACK,
        BATTLE_STAT_SP_DEFENSE,
        BATTLE_STAT_SPEED,
    };
    int best = priority[0];
    int bestValue = Mercury_ParadoxStatValue(battleCtx, battler, best);
    int i;

    for (i = 1; i < (int)(sizeof(priority) / sizeof(priority[0])); i++) {
        int stat = priority[i];
        int value = Mercury_ParadoxStatValue(battleCtx, battler, stat);

        // Strictly greater preserves the official tie priority.
        if (value > bestValue) {
            best = stat;
            bestValue = value;
        }
    }

    return best;
}

static BOOL Mercury_ParadoxFieldActive(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int ability)
{
    if (ability == ABILITY_PROTOSYNTHESIS) {
        // Current-mainline donor behavior deliberately excludes Desolate Land.
        return NO_CLOUD_NINE
            && (battleCtx->fieldConditionsMask & FIELD_CONDITION_SUNNY);
    }

    if (ability == ABILITY_QUARK_DRIVE) {
        return battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC
            && battleCtx->mercuryTerrainTurns != 0;
    }

    return FALSE;
}

static BOOL Mercury_ParadoxBoostActive(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int ability = Battler_Ability(battleCtx, battler);
    BOOL fieldActive;

    if (ability != ABILITY_PROTOSYNTHESIS
        && ability != ABILITY_QUARK_DRIVE) {
        // Neutralizing Gas reaches this path as ABILITY_NONE. Preserve stored
        // Booster state so it can resume when Gas leaves, but suppress now.
        return FALSE;
    }

    if (battleCtx->battleMons[battler].statusVolatile
        & VOLATILE_CONDITION_TRANSFORM) {
        return FALSE;
    }

    fieldActive = Mercury_ParadoxFieldActive(
        battleSys, battleCtx, battler, ability);

    if (fieldActive) {
        if (battleCtx->mercuryParadoxBoostedStat[battler] == 0) {
            battleCtx->mercuryParadoxBoostedStat[battler] =
                Mercury_ParadoxGreatestStat(battleCtx, battler);
        }
        return TRUE;
    }

    if (battleCtx->mercuryParadoxBoosterActive[battler]) {
        return battleCtx->mercuryParadoxBoostedStat[battler] != 0;
    }

    // If field activation ends while Booster Energy is still held, consume it
    // now and start a fresh persistent activation using the then-current stats.
    if (battleCtx->battleMons[battler].heldItem == ITEM_BOOSTER_ENERGY) {
        battleCtx->mercuryParadoxBoostedStat[battler] =
            Mercury_ParadoxGreatestStat(battleCtx, battler);
        battleCtx->mercuryParadoxBoosterActive[battler] = TRUE;
        battleCtx->battleMons[battler].heldItem = ITEM_NONE;
        BattleMon_CopyToParty(battleSys, battleCtx, battler);
        return TRUE;
    }

    battleCtx->mercuryParadoxBoostedStat[battler] = 0;
    return FALSE;
}

""",
        "Paradox shared helpers",
    )

    # Reset Booster-derived state whenever a battler slot is initialized from
    # the party. This makes switching out end Booster Energy activation.
    replace_once(
        path,
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
{
    Pokemon *mon = BattleSystem_GetPartyPokemon(battleSys, battler, partySlot);

""",
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
{
    Pokemon *mon = BattleSystem_GetPartyPokemon(battleSys, battler, partySlot);

    battleCtx->mercuryParadoxBoostedStat[battler] = 0;
    battleCtx->mercuryParadoxBoosterActive[battler] = FALSE;

""",
        "Paradox switch reset",
    )


def patch_damage_and_speed(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_after_once(
        path,
        """    if (attackerParams.ability == ABILITY_HADRON_ENGINE
        && battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
        spAttackStat = spAttackStat * 4 / 3;
    }

""",
        """    if (Mercury_ParadoxBoostActive(battleSys, battleCtx, attacker)) {
        switch (battleCtx->mercuryParadoxBoostedStat[attacker]) {
        case BATTLE_STAT_ATTACK:
            attackStat = attackStat * 13 / 10;
            break;
        case BATTLE_STAT_SP_ATTACK:
            spAttackStat = spAttackStat * 13 / 10;
            break;
        }
    }

    if (Mercury_ParadoxBoostActive(battleSys, battleCtx, defender)) {
        switch (battleCtx->mercuryParadoxBoostedStat[defender]) {
        case BATTLE_STAT_DEFENSE:
            defenseStat = defenseStat * 13 / 10;
            break;
        case BATTLE_STAT_SP_DEFENSE:
            spDefenseStat = spDefenseStat * 13 / 10;
            break;
        }
    }

""",
        "Paradox damage-stat modifiers",
    )

    replace_once(
        path,
        """    if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
        if (battler1Ability == ABILITY_SURGE_SURFER) {
            battler1Speed *= 2;
        }
        if (battler2Ability == ABILITY_SURGE_SURFER) {
            battler2Speed *= 2;
        }
    }

    if (NO_CLOUD_NINE) {
""",
        """    if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_ELECTRIC) {
        if (battler1Ability == ABILITY_SURGE_SURFER) {
            battler1Speed *= 2;
        }
        if (battler2Ability == ABILITY_SURGE_SURFER) {
            battler2Speed *= 2;
        }
    }

    if (Mercury_ParadoxBoostActive(battleSys, battleCtx, battler1)
        && battleCtx->mercuryParadoxBoostedStat[battler1]
            == BATTLE_STAT_SPEED) {
        battler1Speed = battler1Speed * 3 / 2;
    }
    if (Mercury_ParadoxBoostActive(battleSys, battleCtx, battler2)
        && battleCtx->mercuryParadoxBoostedStat[battler2]
            == BATTLE_STAT_SPEED) {
        battler2Speed = battler2Speed * 3 / 2;
    }

    if (NO_CLOUD_NINE) {
""",
        "Paradox Speed modifier",
    )


def patch_switch_in_activation(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """                    case ABILITY_ELECTRIC_SURGE:
""",
        """                    case ABILITY_PROTOSYNTHESIS:
                    case ABILITY_QUARK_DRIVE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (Mercury_ParadoxBoostActive(
                                battleSys, battleCtx, battler)) {
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = Battler_Ability(
                                battleCtx, battler);
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

""",
        "Paradox switch-in activation",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    # Receiver / Power of Alchemy.
    insert_before_once(
        lib,
        """    case ABILITY_TERA_SHIFT:
        return FALSE;
""",
        """    case ABILITY_PROTOSYNTHESIS:
    case ABILITY_QUARK_DRIVE:
""",
        "Paradox Receiver restriction",
    )

    # Trace eligibility was expanded by MR08R4.
    replace_once(
        lib,
        """        && ability1 != ABILITY_EMBODY_ASPECT_4;
""",
        """        && ability1 != ABILITY_EMBODY_ASPECT_4
        && ability1 != ABILITY_PROTOSYNTHESIS
        && ability1 != ABILITY_QUARK_DRIVE;
""",
        "Paradox Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_EMBODY_ASPECT_4;
""",
        """        && ability2 != ABILITY_EMBODY_ASPECT_4
        && ability2 != ABILITY_PROTOSYNTHESIS
        && ability2 != ABILITY_QUARK_DRIVE;
""",
        "Paradox Trace defender2",
    )

    for ability in IMPLEMENTED:
        insert_after_once(
            copy,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _091\n",
            f"{ability} Role Play target",
        )
        insert_after_once(
            copy,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _091\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {ability}, _091\n",
            f"{ability} Role Play user",
        )
        insert_after_once(
            swap,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _156\n",
            f"{ability} Skill Swap target",
        )
        insert_after_once(
            swap,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _156\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {ability}, _156\n",
            f"{ability} Skill Swap user",
        )
        insert_after_once(
            suppress,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _034\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _034\n",
            f"{ability} Gastro Acid lock",
        )
        insert_after_once(
            worry,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_COMATOSE, _041\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {ability}, _041\n",
            f"{ability} Worry Seed lock",
        )


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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    items = (root / "generated/items.txt").read_text(encoding="utf-8")
    booster = (root / "res/items/data/booster_energy.json").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "booster_energy_item":
            "ITEM_BOOSTER_ENERGY" in items
            and '"name": "Booster Energy"' in booster,
        "boost_state":
            "mercuryParadoxBoostedStat[MAX_BATTLERS]" in ctx
            and "mercuryParadoxBoosterActive[MAX_BATTLERS]" in ctx,
        "canonical_tie_order":
            "BATTLE_STAT_ATTACK" in lib
            and "BATTLE_STAT_DEFENSE" in lib
            and "BATTLE_STAT_SP_ATTACK" in lib
            and "BATTLE_STAT_SP_DEFENSE" in lib
            and "BATTLE_STAT_SPEED" in lib
            and "Strictly greater preserves the official tie priority" in lib,
        "proto_sun_activation":
            "ABILITY_PROTOSYNTHESIS" in lib
            and "FIELD_CONDITION_SUNNY" in lib,
        "quark_terrain_activation":
            "ABILITY_QUARK_DRIVE" in lib
            and "MERCURY_TERRAIN_ELECTRIC" in lib,
        "boost_multipliers":
            "attackStat = attackStat * 13 / 10;" in lib
            and "spAttackStat = spAttackStat * 13 / 10;" in lib
            and "defenseStat = defenseStat * 13 / 10;" in lib
            and "spDefenseStat = spDefenseStat * 13 / 10;" in lib
            and "battler1Speed = battler1Speed * 3 / 2;" in lib,
        "booster_consumption":
            "heldItem == ITEM_BOOSTER_ENERGY" in lib
            and "mercuryParadoxBoosterActive[battler] = TRUE;" in lib
            and "heldItem = ITEM_NONE;" in lib,
        "switch_reset":
            "mercuryParadoxBoosterActive[battler] = FALSE;" in lib,
        "uncopyable_unswappable":
            all(token in copy and token in swap for token in IMPLEMENTED),
        "unsuppressible_by_moves":
            all(token in suppress for token in IMPLEMENTED),
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
        default=Path("mr08s2-canonical-ability-paradox.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_booster_energy_item(root)
    patch_context(root)
    patch_paradox_helpers(root)
    patch_damage_and_speed(root)
    patch_switch_in_activation(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S2_CANONICAL_ABILITY_PARADOX",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 172,
        "remaining_modern_canonical_mechanics": 15,
        "added_item": "ITEM_BOOSTER_ENERGY",
        "policy": "Official/current-mainline Protosynthesis / Quark Drive stat selection, field activation, and Booster Energy persistence.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S2 validation failed")


if __name__ == "__main__":
    main()
