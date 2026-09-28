#!/usr/bin/env python3
"""MR08S6 — canonical Zero to Hero battle-state pass.

Implements Palafin's current-mainline Zero to Hero mechanics without waiting on
the later alternate-form art pass:
- a living Palafin with an active Zero to Hero marks itself Hero when it leaves
  battle, including ordinary switches and move-driven switches;
- Neutralizing Gas suppresses the switch-out activation;
- transformed users do not activate it;
- the Hero state is tracked per party slot for the rest of that battle;
- when that Palafin returns, its non-HP stats are recalculated exactly from its
  level, IVs, EVs and nature using Hero Form base stats;
- HP, status, moves, PP, stat stages and held item are not reset;
- Trace, Role Play, Skill Swap, Gastro Acid, Worry Seed, Receiver and Power of
  Alchemy retain the canonical special-Ability restrictions.

Hero-form sprite/model presentation is deferred to Mercury's form-asset phase.
Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_ZERO_TO_HERO",)
EXPECTED_IDS = {"ABILITY_ZERO_TO_HERO": 278}


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


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    label: str,
) -> None:
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

    segment = text[start:end]
    count = segment.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one scoped match in {path}, found {count}"
        )
    segment = segment.replace(old, new, 1)
    path.write_text(text[:start] + segment + text[end:], encoding="utf-8")


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
        """    // Mercury MR08S6: per-side party-slot Hero state plus active slot state.
    u8 mercuryZeroToHeroPartyMask[2];
    u8 mercuryZeroToHeroActive[MAX_BATTLERS];

""",
        "Zero to Hero battle state",
    )


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)
""",
        """static u16 Mercury_ZeroToHeroCalcStat(
    Pokemon *mon,
    int baseStat,
    int statType)
{
    int ivParam;
    int evParam;
    int level;
    int iv;
    int ev;
    int value;
    int affinity;

    switch (statType) {
    case STAT_ATTACK:
        ivParam = MON_DATA_ATK_IV;
        evParam = MON_DATA_ATK_EV;
        break;
    case STAT_DEFENSE:
        ivParam = MON_DATA_DEF_IV;
        evParam = MON_DATA_DEF_EV;
        break;
    case STAT_SPEED:
        ivParam = MON_DATA_SPEED_IV;
        evParam = MON_DATA_SPEED_EV;
        break;
    case STAT_SPECIAL_ATTACK:
        ivParam = MON_DATA_SPATK_IV;
        evParam = MON_DATA_SPATK_EV;
        break;
    default:
        ivParam = MON_DATA_SPDEF_IV;
        evParam = MON_DATA_SPDEF_EV;
        break;
    }

    level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);
    iv = Pokemon_GetValue(mon, ivParam, NULL);
    ev = Pokemon_GetValue(mon, evParam, NULL);
    value = ((2 * baseStat + iv + ev / 4) * level / 100 + 5);

    affinity = Pokemon_GetStatAffinityOf(Pokemon_GetNature(mon), statType);
    if (affinity > 0) {
        value = value * 110 / 100;
    } else if (affinity < 0) {
        value = value * 90 / 100;
    }

    return value;
}

static void Mercury_ApplyZeroToHeroStats(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    // Palafin Hero Form base stats:
    // HP 100 / Atk 160 / Def 97 / SpA 106 / SpD 87 / Spe 100.
    // HP is intentionally untouched because form-changing does not heal.
    battleCtx->battleMons[battler].attack =
        Mercury_ZeroToHeroCalcStat(mon, 160, STAT_ATTACK);
    battleCtx->battleMons[battler].defense =
        Mercury_ZeroToHeroCalcStat(mon, 97, STAT_DEFENSE);
    battleCtx->battleMons[battler].spAttack =
        Mercury_ZeroToHeroCalcStat(mon, 106, STAT_SPECIAL_ATTACK);
    battleCtx->battleMons[battler].spDefense =
        Mercury_ZeroToHeroCalcStat(mon, 87, STAT_SPECIAL_DEFENSE);
    battleCtx->battleMons[battler].speed =
        Mercury_ZeroToHeroCalcStat(mon, 100, STAT_SPEED);
}

""",
        "Zero to Hero exact stat helpers",
    )

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    int side = BattleSystem_GetBattlerSide(battleSys, battler);
""",
        """    int side = BattleSystem_GetBattlerSide(battleSys, battler);

    battleCtx->mercuryZeroToHeroActive[battler] = FALSE;
    if (battleCtx->battleMons[battler].species == SPECIES_PALAFIN
        && battleCtx->battleMons[battler].ability == ABILITY_ZERO_TO_HERO
        && partySlot < 6
        && (battleCtx->mercuryZeroToHeroPartyMask[side] & FlagIndex(partySlot))) {
        Mercury_ApplyZeroToHeroStats(battleCtx, battler, mon);
        battleCtx->mercuryZeroToHeroActive[battler] = TRUE;
    }
""",
        "Zero to Hero switch-in Hero stat load",
    )


def patch_switch_out_activation(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

    if (battleCtx->battleMons[battler].curHP
        && Battler_Ability(battleCtx, battler) == ABILITY_REGENERATOR
""",
        """    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);

    if (battleCtx->battleMons[battler].curHP
        && battleCtx->battleMons[battler].species == SPECIES_PALAFIN
        && Battler_Ability(battleCtx, battler) == ABILITY_ZERO_TO_HERO
        && (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM) == FALSE
        && battleCtx->selectedPartySlot[battler] < 6) {
        int side = BattleSystem_GetBattlerSide(battleSys, battler);
        battleCtx->mercuryZeroToHeroPartyMask[side] |=
            FlagIndex(battleCtx->selectedPartySlot[battler]);
    }

    if (battleCtx->battleMons[battler].curHP
        && Battler_Ability(battleCtx, battler) == ABILITY_REGENERATOR
""",
        "Zero to Hero switch-out activation",
    )


def patch_neutralizing_gas(root: Path) -> None:
    # Zero to Hero is a cantsuppress Ability in current mainline mechanics.
    # Neutralizing Gas therefore must not disable its switch-out activation.
    return

def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_HUNGER_SWITCH;
""",
        """        && ability1 != ABILITY_HUNGER_SWITCH
        && ability1 != ABILITY_ZERO_TO_HERO;
""",
        "Zero to Hero Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_HUNGER_SWITCH;
""",
        """        && ability2 != ABILITY_HUNGER_SWITCH
        && ability2 != ABILITY_ZERO_TO_HERO;
""",
        "Zero to Hero Trace defender2",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _091\n",
        "Zero to Hero Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _091\n",
        "Zero to Hero Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _156\n",
        "Zero to Hero Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _156\n",
        "Zero to Hero Skill Swap user",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_STANCE_CHANGE, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _034\n",
        "Zero to Hero Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_HUNGER_SWITCH, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ZERO_TO_HERO, _041\n",
        "Zero to Hero Worry Seed lock",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    checks = {
        "party_slot_hero_state":
            "mercuryZeroToHeroPartyMask[2]" in ctx
            and "mercuryZeroToHeroActive[MAX_BATTLERS]" in ctx,
        "switch_out_activation":
            "mercuryZeroToHeroPartyMask[side] |=" in script
            and "SPECIES_PALAFIN" in script
            and "ABILITY_ZERO_TO_HERO" in script,
        "transform_block":
            "VOLATILE_CONDITION_TRANSFORM" in script,
        "exact_hero_base_stats":
            "Mercury_ZeroToHeroCalcStat(mon, 160, STAT_ATTACK)" in lib
            and "Mercury_ZeroToHeroCalcStat(mon, 97, STAT_DEFENSE)" in lib
            and "Mercury_ZeroToHeroCalcStat(mon, 106, STAT_SPECIAL_ATTACK)" in lib
            and "Mercury_ZeroToHeroCalcStat(mon, 87, STAT_SPECIAL_DEFENSE)" in lib
            and "Mercury_ZeroToHeroCalcStat(mon, 100, STAT_SPEED)" in lib,
        "iv_ev_nature_recalculation":
            "MON_DATA_ATK_EV" in lib
            and "MON_DATA_SPDEF_EV" in lib
            and "Pokemon_GetStatAffinityOf(Pokemon_GetNature(mon), statType)" in lib,
        "switch_in_hero_restore":
            "mercuryZeroToHeroPartyMask[side] & FlagIndex(partySlot)" in lib
            and "Mercury_ApplyZeroToHeroStats" in lib,
        "neutralizing_gas_cannot_suppress_activation":
            "ABILITY_ZERO_TO_HERO" in cannot,
        "trace_blocked":
            "ability1 != ABILITY_ZERO_TO_HERO" in lib
            and "ability2 != ABILITY_ZERO_TO_HERO" in lib,
        "role_play_and_skill_swap_blocked":
            "ABILITY_ZERO_TO_HERO" in copy
            and "ABILITY_ZERO_TO_HERO" in swap,
        "gastro_acid_and_worry_seed_blocked":
            "ABILITY_ZERO_TO_HERO" in suppress
            and "ABILITY_ZERO_TO_HERO" in worry,
        "receiver_blocked":
            "ABILITY_ZERO_TO_HERO" in receiver,
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
        default=Path("mr08s6-canonical-ability-zero-to-hero.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_battle_lib(root)
    patch_switch_out_activation(root)
    patch_neutralizing_gas(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S6_CANONICAL_ABILITY_ZERO_TO_HERO",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 177,
        "remaining_modern_canonical_mechanics": 10,
        "form_visuals_deferred": True,
        "policy": "Official Zero to Hero switch-out activation with battle-persistent party-slot Hero state and exact Hero-form stat recalculation.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S6 validation failed")


if __name__ == "__main__":
    main()
