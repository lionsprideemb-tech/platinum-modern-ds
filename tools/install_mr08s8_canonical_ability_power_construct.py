#!/usr/bin/env python3
"""MR08S8 — canonical Power Construct pass.

Implements Zygarde's current-mainline Power Construct battle mechanics:
- at end of turn, a living non-transformed Zygarde at 50% HP or less changes
  to Complete Forme if Power Construct is active;
- Complete Forme persists for that party slot for the rest of the battle;
- Complete Forme uses exact base stats 216/100/121/91/95/85;
- max HP is recalculated from level/IV/EV and current HP increases by exactly
  the max-HP increase, preserving damage taken;
- switching out and back in preserves the battle-only Complete state and its
  true Complete-form current HP while keeping the backing party struct in a
  safe base-form HP range until the form-asset layer exists;
- Neutralizing Gas can suppress activation, while Gastro Acid, Worry Seed,
  Trace, Role Play, Skill Swap, Receiver and Power of Alchemy retain the
  canonical special-Ability restrictions.

Complete-form sprite/model presentation is deferred to Mercury's form-asset
phase. Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_POWER_CONSTRUCT",)
EXPECTED_IDS = {"ABILITY_POWER_CONSTRUCT": 211}


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
        """    // Mercury MR08S8: battle-persistent Zygarde Complete state.
    u8 mercuryPowerConstructPartyMask[2];
    u8 mercuryPowerConstructActive[MAX_BATTLERS];
    u16 mercuryPowerConstructHP[2][6];

""",
        "Power Construct battle state",
    )


def patch_helpers_and_switch_in(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """static u16 Mercury_ThresholdFormCalcStat(
""",
        """static void Mercury_SetThresholdFormStats(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon,
    int atk,
    int def,
    int spa,
    int spd,
    int spe);

static u16 Mercury_PowerConstructMaxHP(Pokemon *mon)
{
    int level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);
    int iv = Pokemon_GetValue(mon, MON_DATA_HP_IV, NULL);
    int ev = Pokemon_GetValue(mon, MON_DATA_HP_EV, NULL);

    return ((2 * 216 + iv + ev / 4) * level / 100 + level + 10);
}

static void Mercury_ApplyPowerConstructComplete(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    int oldMax = battleCtx->battleMons[battler].maxHP;
    int damageTaken = oldMax - battleCtx->battleMons[battler].curHP;
    int newMax = Mercury_PowerConstructMaxHP(mon);

    battleCtx->battleMons[battler].maxHP = newMax;
    if (battleCtx->battleMons[battler].curHP) {
        battleCtx->battleMons[battler].curHP = newMax - damageTaken;
        if (battleCtx->battleMons[battler].curHP < 1) {
            battleCtx->battleMons[battler].curHP = 1;
        } else if (battleCtx->battleMons[battler].curHP > newMax) {
            battleCtx->battleMons[battler].curHP = newMax;
        }
    }

    Mercury_SetThresholdFormStats(
        battleCtx, battler, mon, 100, 121, 91, 95, 85);
    battleCtx->battleMons[battler].type1 = TYPE_DRAGON;
    battleCtx->battleMons[battler].type2 = TYPE_GROUND;
    battleCtx->mercuryPowerConstructActive[battler] = TRUE;
}

""",
        "Power Construct helpers",
    )

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryZenActive[battler] = FALSE;
""",
        """    battleCtx->mercuryPowerConstructActive[battler] = FALSE;
    if (battleCtx->battleMons[battler].species == SPECIES_ZYGARDE
        && battleCtx->battleMons[battler].ability == ABILITY_POWER_CONSTRUCT
        && partySlot < 6
        && (battleCtx->mercuryPowerConstructPartyMask[side]
            & FlagIndex(partySlot))) {
        Mercury_ApplyPowerConstructComplete(battleCtx, battler, mon);

        if (battleCtx->mercuryPowerConstructHP[side][partySlot]) {
            battleCtx->battleMons[battler].curHP =
                battleCtx->mercuryPowerConstructHP[side][partySlot];
            if (battleCtx->battleMons[battler].curHP
                > battleCtx->battleMons[battler].maxHP) {
                battleCtx->battleMons[battler].curHP =
                    battleCtx->battleMons[battler].maxHP;
            }
        }
    }

    battleCtx->mercuryZenActive[battler] = FALSE;
""",
        "Power Construct switch-in restore",
    )

    replace_in_function(
        path,
        "void BattleMon_CopyToParty(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    if (battleCtx->battleMons[battler].heldItem == ITEM_NONE) {
""",
        """    if (battleCtx->mercuryPowerConstructActive[battler]
        && battleCtx->selectedPartySlot[battler] < 6) {
        int side = BattleSystem_GetBattlerSide(battleSys, battler);
        int slot = battleCtx->selectedPartySlot[battler];

        battleCtx->mercuryPowerConstructPartyMask[side] |= FlagIndex(slot);
        battleCtx->mercuryPowerConstructHP[side][slot] =
            battleCtx->battleMons[battler].curHP;
    }

    if (battleCtx->battleMons[battler].heldItem == ITEM_NONE) {
""",
        "Power Construct live HP cache",
    )


def patch_party_hp_normalization(root: Path) -> None:
    path = root / "src/battle/battle_controller.c"

    replace_in_function(
        path,
        "void BattleController_EmitUpdatePartyMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    message.curHP = battleCtx->battleMons[battler].curHP;
""",
        """    message.curHP = battleCtx->battleMons[battler].curHP;

    // Until the Complete-form party asset exists, keep the backing party
    // Pokémon in a legal base-form HP range. The true Complete-form HP is
    // cached in BattleContext and restored on re-entry.
    if (battleCtx->mercuryPowerConstructActive[battler]
        && message.partySlot < 6
        && message.curHP) {
        Pokemon *partyMon = BattleSystem_GetPartyPokemon(
            battleSys, battler, message.partySlot);
        int partyMax = Pokemon_GetValue(partyMon, MON_DATA_MAX_HP, NULL);
        int damageTaken =
            battleCtx->battleMons[battler].maxHP - message.curHP;
        int normalizedHP = partyMax - damageTaken;

        if (normalizedHP < 1) {
            normalizedHP = 1;
        } else if (normalizedHP > partyMax) {
            normalizedHP = partyMax;
        }
        message.curHP = normalizedHP;
    }
""",
        "Power Construct party HP normalization",
    )


def patch_end_turn(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    case ABILITY_ZEN_MODE: {
""",
        """    case ABILITY_POWER_CONSTRUCT: {
        int side = BattleSystem_GetBattlerSide(battleSys, battler);
        int slot = battleCtx->selectedPartySlot[battler];

        if (battleCtx->battleMons[battler].species == SPECIES_ZYGARDE
            && battleCtx->battleMons[battler].curHP
            && battleCtx->battleMons[battler].curHP
                <= battleCtx->battleMons[battler].maxHP / 2
            && battleCtx->mercuryPowerConstructActive[battler] == FALSE
            && (battleCtx->battleMons[battler].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE
            && slot < 6) {
            Pokemon *mon = BattleSystem_GetPartyPokemon(
                battleSys, battler, slot);

            Mercury_ApplyPowerConstructComplete(
                battleCtx, battler, mon);
            battleCtx->mercuryPowerConstructPartyMask[side] |=
                FlagIndex(slot);
            battleCtx->mercuryPowerConstructHP[side][slot] =
                battleCtx->battleMons[battler].curHP;

            BattleMon_CopyToParty(battleSys, battleCtx, battler);
            battleCtx->msgBattlerTemp = battler;
            subscript = subscript_mold_breaker;
            result = TRUE;
        }
        break;
    }

    case ABILITY_ZEN_MODE: {
""",
        "Power Construct end-turn activation",
    )


def patch_neutralizing_gas(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    replace_in_function(
        path,
        "static BOOL Mercury_AbilityCannotBeNeutralized(int ability)",
        """    case ABILITY_POWER_CONSTRUCT:
""",
        "",
        "Power Construct Neutralizing Gas suppression",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_SHIELDS_DOWN;
""",
        """        && ability1 != ABILITY_SHIELDS_DOWN
        && ability1 != ABILITY_POWER_CONSTRUCT;
""",
        "Power Construct Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_SHIELDS_DOWN;
""",
        """        && ability2 != ABILITY_SHIELDS_DOWN
        && ability2 != ABILITY_POWER_CONSTRUCT;
""",
        "Power Construct Trace defender2",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _091\n",
        "Power Construct Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _091\n",
        "Power Construct Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _156\n",
        "Power Construct Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _156\n",
        "Power Construct Skill Swap user",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _034\n",
        "Power Construct Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_SHIELDS_DOWN, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _041\n",
        "Power Construct Worry Seed lock",
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
    controller = (root / "src/battle/battle_controller.c").read_text(encoding="utf-8")
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
        "persistent_party_slot_state":
            "mercuryPowerConstructPartyMask[2]" in ctx
            and "mercuryPowerConstructHP[2][6]" in ctx,
        "half_hp_end_turn_trigger":
            "case ABILITY_POWER_CONSTRUCT:" in lib
            and "<= battleCtx->battleMons[battler].maxHP / 2" in lib,
        "transform_block":
            "VOLATILE_CONDITION_TRANSFORM" in lib,
        "complete_hp_base_216":
            "2 * 216" in lib
            and "MON_DATA_HP_IV" in lib
            and "MON_DATA_HP_EV" in lib,
        "complete_non_hp_stats":
            "battleCtx, battler, mon, 100, 121, 91, 95, 85" in lib,
        "preserve_damage_taken":
            "damageTaken = oldMax - battleCtx->battleMons[battler].curHP" in lib
            and "newMax - damageTaken" in lib,
        "switch_persistence":
            "mercuryPowerConstructPartyMask[side]" in lib
            and "FlagIndex(partySlot)" in lib
            and "mercuryPowerConstructHP[side][partySlot]" in lib,
        "safe_party_hp_projection":
            "normalizedHP = partyMax - damageTaken" in controller
            and "mercuryPowerConstructActive[battler]" in controller,
        "neutralizing_gas_can_suppress_activation":
            "ABILITY_POWER_CONSTRUCT" not in cannot,
        "trace_blocked":
            "ability1 != ABILITY_POWER_CONSTRUCT" in lib
            and "ability2 != ABILITY_POWER_CONSTRUCT" in lib,
        "role_play_and_skill_swap_blocked":
            "ABILITY_POWER_CONSTRUCT" in copy
            and "ABILITY_POWER_CONSTRUCT" in swap,
        "gastro_acid_and_worry_seed_blocked":
            "ABILITY_POWER_CONSTRUCT" in suppress
            and "ABILITY_POWER_CONSTRUCT" in worry,
        "receiver_blocked":
            "ABILITY_POWER_CONSTRUCT" in receiver,
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
        default=Path("mr08s8-canonical-ability-power-construct.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_helpers_and_switch_in(root)
    patch_party_hp_normalization(root)
    patch_end_turn(root)
    patch_neutralizing_gas(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S8_CANONICAL_ABILITY_POWER_CONSTRUCT",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 181,
        "remaining_modern_canonical_mechanics": 6,
        "form_visuals_deferred": True,
        "policy": "Official Power Construct <=50% end-turn transformation with Complete-form stats, damage-preserving HP growth and battle-persistent Complete state.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S8 validation failed")


if __name__ == "__main__":
    main()
