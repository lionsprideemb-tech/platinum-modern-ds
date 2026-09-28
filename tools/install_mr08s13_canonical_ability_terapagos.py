#!/usr/bin/env python3
"""MR08S13 — canonical Terapagos Ability pair.

Implements the remaining Terapagos Ability mechanics:
- Tera Shift changes a legal Terapagos from Normal Form into its battle-only
  Terastal state on first entry, preserving damage while recalculating the
  canonical 95/95/110/105/110/85 Terastal stats and changing the active
  Ability to Tera Shell;
- Terastal state persists across switches for that party slot while the backing
  party Pokémon stays in its legal base form;
- Teraform Zero exposes the canonical post-Terastallization trigger and clears
  ordinary weather, Mercury strong weather, and Mercury terrain once;
- Tera Shift is unsuppressible/notransform and both Abilities keep the
  current-mainline copy/swap/Trace/Receiver restrictions;
- Teraform Zero remains suppressible, matching current Gen IX mechanics.

Terapagos Terastal/Stellar battle sprite assets and the general Terastallization
UI/system remain separate later systems. Locked MR07 Summary/editor visuals are
untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_TERA_SHIFT",
    "ABILITY_TERAFORM_ZERO",
)
EXPECTED_IDS = {
    "ABILITY_TERA_SHIFT": 307,
    "ABILITY_TERAFORM_ZERO": 309,
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
        """    // Mercury MR08S13: battle-only Terapagos state.
    u8 mercuryTerapagosTerastalPartyMask[2];
    u8 mercuryTerapagosTerastalActive[MAX_BATTLERS];
    u8 mercuryTeraformZeroUsedPartyMask[2];

""",
        "Terapagos battle state",
    )


def patch_public_hook(root: Path) -> None:
    path = root / "include/battle/battle_lib.h"
    insert_before_once(
        path,
        """BOOL Mercury_TryBreakIllusionByAbilityLoss(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """BOOL Mercury_TriggerTeraformZeroAfterTerastallization(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int *subscript);

""",
        "Teraform Zero public hook",
    )


def patch_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """static u16 Mercury_PowerConstructMaxHP(Pokemon *mon)
""",
        """static u16 Mercury_TerapagosTerastalMaxHP(Pokemon *mon)
{
    int level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);
    int iv = Pokemon_GetValue(mon, MON_DATA_HP_IV, NULL);
    int ev = Pokemon_GetValue(mon, MON_DATA_HP_EV, NULL);

    return ((2 * 95 + iv + ev / 4) * level / 100 + level + 10);
}

static void Mercury_ApplyTerapagosTerastal(
    BattleContext *battleCtx,
    int battler,
    Pokemon *mon)
{
    int oldMax = battleCtx->battleMons[battler].maxHP;
    int damageTaken = oldMax - battleCtx->battleMons[battler].curHP;
    int newMax = Mercury_TerapagosTerastalMaxHP(mon);

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
        battleCtx, battler, mon, 95, 110, 105, 110, 85);
    battleCtx->battleMons[battler].type1 = TYPE_NORMAL;
    battleCtx->battleMons[battler].type2 = TYPE_NORMAL;
    battleCtx->battleMons[battler].ability = ABILITY_TERA_SHELL;
    battleCtx->mercuryTerapagosTerastalActive[battler] = TRUE;
}

BOOL Mercury_TriggerTeraformZeroAfterTerastallization(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler,
    int *subscript)
{
    int side;
    int slot;
    BOOL hadField;

    if (battler < 0
        || battler >= BattleSystem_GetMaxBattlers(battleSys)
        || battleCtx->battleMons[battler].species != SPECIES_TERAPAGOS
        || battleCtx->battleMons[battler].ability != ABILITY_TERAFORM_ZERO
        || (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM)) {
        return FALSE;
    }

    side = BattleSystem_GetBattlerSide(battleSys, battler);
    slot = battleCtx->selectedPartySlot[battler];
    if (slot >= MAX_PARTY_SIZE
        || (battleCtx->mercuryTeraformZeroUsedPartyMask[side]
            & FlagIndex(slot))) {
        return FALSE;
    }

    // The event happens once at the Terastallization transition. Mark it used
    // even if Neutralizing Gas suppresses the Ability or there is no field
    // effect to clear; it must not fire later when conditions change.
    battleCtx->mercuryTeraformZeroUsedPartyMask[side] |= FlagIndex(slot);

    if (Battler_Ability(battleCtx, battler) != ABILITY_TERAFORM_ZERO) {
        return FALSE;
    }

    hadField =
        (battleCtx->fieldConditionsMask & FIELD_CONDITION_WEATHER)
        || battleCtx->mercuryStrongWeatherType != MERCURY_STRONG_WEATHER_NONE
        || battleCtx->mercuryTerrainType != MERCURY_TERRAIN_NONE;

    battleCtx->fieldConditionsMask &= ~FIELD_CONDITION_WEATHER;
    battleCtx->mercuryStrongWeatherType = MERCURY_STRONG_WEATHER_NONE;
    battleCtx->mercuryStrongWeatherSource = BATTLER_NONE;
    battleCtx->mercuryTerrainType = MERCURY_TERRAIN_NONE;
    battleCtx->mercuryTerrainTurns = 0;

    if (hadField) {
        battleCtx->msgBattlerTemp = battler;
        battleCtx->msgTemp = ABILITY_TERAFORM_ZERO;
        *subscript = subscript_mold_breaker;
        return TRUE;
    }

    return FALSE;
}

""",
        "Terapagos helpers",
    )


def patch_switch_restore(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryIllusionActive[battler] = FALSE;
""",
        """    battleCtx->mercuryTerapagosTerastalActive[battler] = FALSE;

    if (battleCtx->battleMons[battler].species == SPECIES_TERAPAGOS
        && partySlot < MAX_PARTY_SIZE
        && (battleCtx->mercuryTerapagosTerastalPartyMask[side]
            & FlagIndex(partySlot))) {
        Mercury_ApplyTerapagosTerastal(battleCtx, battler, mon);
    }

    battleCtx->mercuryIllusionActive[battler] = FALSE;
""",
        "Terapagos switch-in restore",
    )


def patch_form_change_trigger(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerFormChange(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    for (i = 0; i < BattleSystem_GetMaxBattlers(battleSys); i++) {
        battleCtx->msgBattlerTemp = battleCtx->monSpeedOrder[i];

""",
        """    for (i = 0; i < BattleSystem_GetMaxBattlers(battleSys); i++) {
        battleCtx->msgBattlerTemp = battleCtx->monSpeedOrder[i];

        // Teraform Zero's real trigger is the post-Terastallization event.
        // Calling the public hook here also makes an already-Stellar legal
        // battle state resolve on the next standard form-check checkpoint.
        if (battleCtx->battleMons[battleCtx->msgBattlerTemp].ability
                == ABILITY_TERAFORM_ZERO) {
            if (Mercury_TriggerTeraformZeroAfterTerastallization(
                    battleSys,
                    battleCtx,
                    battleCtx->msgBattlerTemp,
                    subscript)) {
                result = TRUE;
                break;
            }
        }

        if (battleCtx->battleMons[battleCtx->msgBattlerTemp].species
                == SPECIES_TERAPAGOS
            && battleCtx->battleMons[battleCtx->msgBattlerTemp].curHP
            && battleCtx->mercuryTerapagosTerastalActive[
                battleCtx->msgBattlerTemp] == FALSE
            && Battler_Ability(
                battleCtx, battleCtx->msgBattlerTemp) == ABILITY_TERA_SHIFT
            && (battleCtx->battleMons[battleCtx->msgBattlerTemp].statusVolatile
                & VOLATILE_CONDITION_TRANSFORM) == FALSE) {
            int teraBattler = battleCtx->msgBattlerTemp;
            int side = BattleSystem_GetBattlerSide(battleSys, teraBattler);
            int slot = battleCtx->selectedPartySlot[teraBattler];
            Pokemon *mon = BattleSystem_GetPartyPokemon(
                battleSys, teraBattler, slot);

            Mercury_ApplyTerapagosTerastal(
                battleCtx, teraBattler, mon);
            if (slot < MAX_PARTY_SIZE) {
                battleCtx->mercuryTerapagosTerastalPartyMask[side] |=
                    FlagIndex(slot);
            }

            BattleController_EmitRefreshHPGauge(
                battleSys, battleCtx, teraBattler);
            battleCtx->msgBattlerTemp = teraBattler;
            battleCtx->msgTemp = ABILITY_TERA_SHIFT;
            *subscript = subscript_mold_breaker;
            result = TRUE;
            break;
        }

""",
        "Terapagos form-change triggers",
    )


def patch_party_normalization(root: Path) -> None:
    path = root / "src/battle/battle_controller.c"

    insert_before_once(
        path,
        """    // Until the Complete-form party asset exists, keep the backing party
""",
        """    // Terapagos Terastal is battle-only. Preserve damage when writing
    // HP back to the base-form party Pokémon and never persist Tera Shell as
    // the out-of-battle Ability.
    if (battleCtx->mercuryTerapagosTerastalActive[battler]) {
        Pokemon *partyMon = BattleSystem_GetPartyPokemon(
            battleSys, battler, message.partySlot);

        if (message.curHP) {
            int partyMax = Pokemon_GetValue(
                partyMon, MON_DATA_MAX_HP, NULL);
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

        message.ability = ABILITY_TERA_SHIFT;
    }

""",
        "Terapagos party normalization",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    script = root / "src/battle/battle_script.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_COMMANDER;
""",
        """        && ability1 != ABILITY_COMMANDER
        && ability1 != ABILITY_TERA_SHIFT
        && ability1 != ABILITY_TERAFORM_ZERO;
""",
        "Terapagos Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_COMMANDER;
""",
        """        && ability2 != ABILITY_COMMANDER
        && ability2 != ABILITY_TERA_SHIFT
        && ability2 != ABILITY_TERAFORM_ZERO;
""",
        "Terapagos Trace defender2",
    )

    for token in IMPLEMENTED:
        insert_after_once(
            copy,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _091\n",
            f"{token} Role Play target",
        )
        insert_after_once(
            copy,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _091\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {token}, _091\n",
            f"{token} Role Play user",
        )
        insert_after_once(
            swap,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, {token}, _156\n",
            f"{token} Skill Swap target",
        )
        insert_after_once(
            swap,
            "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_ILLUSION, _156\n",
            f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, {token}, _156\n",
            f"{token} Skill Swap user",
        )

    # Tera Shift is cantsuppress; Teraform Zero is intentionally not.
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_TERA_SHIFT, _034\n",
        "Tera Shift Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_TERA_SHIFT, _041\n",
        "Tera Shift Worry Seed lock",
    )

    replace_in_function(
        script,
        "static BOOL BtlCmd_Transform(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    if (battleCtx->mercuryIllusionActive[battleCtx->defender]
        && Battler_Ability(battleCtx, battleCtx->defender)
            == ABILITY_ILLUSION) {
""",
        """    if (battleCtx->battleMons[battleCtx->defender].ability
            == ABILITY_TERA_SHIFT) {
        battleCtx->moveStatusFlags |= MOVE_STATUS_FAILED;
        return FALSE;
    }

    if (battleCtx->mercuryIllusionActive[battleCtx->defender]
        && Battler_Ability(battleCtx, battleCtx->defender)
            == ABILITY_ILLUSION) {
""",
        "Tera Shift Transform lock",
    )

    # Receiver already blocks Tera Shift in MR08K; add Teraform Zero.
    replace_in_function(
        lib,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        """    case ABILITY_TERA_SHIFT:
        return FALSE;
""",
        """    case ABILITY_TERA_SHIFT:
    case ABILITY_TERAFORM_ZERO:
        return FALSE;
""",
        "Teraform Zero Receiver lock",
    )


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
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
        "terastal_state":
            "mercuryTerapagosTerastalPartyMask[2]" in ctx
            and "mercuryTerapagosTerastalActive[MAX_BATTLERS]" in ctx,
        "canonical_terastal_stats":
            "2 * 95 + iv + ev / 4" in lib
            and "Mercury_SetThresholdFormStats(" in lib
            and "battleCtx, battler, mon, 95, 110, 105, 110, 85" in lib,
        "damage_preserving_hp_growth":
            "damageTaken = oldMax - battleCtx->battleMons[battler].curHP" in lib
            and "newMax - damageTaken" in lib,
        "tera_shift_to_tera_shell":
            "ABILITY_TERA_SHIFT" in lib
            and "battleCtx->battleMons[battler].ability = ABILITY_TERA_SHELL;" in lib,
        "terastal_switch_persistence":
            "mercuryTerapagosTerastalPartyMask[side]" in lib
            and "Mercury_ApplyTerapagosTerastal(battleCtx, battler, mon)" in lib,
        "base_party_normalization":
            "mercuryTerapagosTerastalActive[battler]" in ctl
            and "message.ability = ABILITY_TERA_SHIFT;" in ctl,
        "teraform_zero_public_hook":
            "Mercury_TriggerTeraformZeroAfterTerastallization" in hdr
            and "Mercury_TriggerTeraformZeroAfterTerastallization" in lib,
        "teraform_zero_clears_weather_and_terrain":
            "fieldConditionsMask &= ~FIELD_CONDITION_WEATHER" in lib
            and "mercuryStrongWeatherType = MERCURY_STRONG_WEATHER_NONE" in lib
            and "mercuryTerrainType = MERCURY_TERRAIN_NONE" in lib
            and "mercuryTerrainTurns = 0" in lib,
        "teraform_zero_once":
            "mercuryTeraformZeroUsedPartyMask[2]" in ctx
            and "mercuryTeraformZeroUsedPartyMask[side] |= FlagIndex(slot)" in lib,
        "suppression_rules":
            "ABILITY_TERA_SHIFT" in cannot
            and "ABILITY_TERAFORM_ZERO" not in cannot
            and "ABILITY_TERA_SHIFT" in suppress
            and "ABILITY_TERA_SHIFT" in worry
            and "ABILITY_TERAFORM_ZERO" not in suppress
            and "ABILITY_TERAFORM_ZERO" not in worry,
        "trace_blocked":
            all(f"ability1 != {token}" in lib and f"ability2 != {token}" in lib
                for token in IMPLEMENTED),
        "roleplay_skillswap_blocked":
            all(token in copy and token in swap for token in IMPLEMENTED),
        "receiver_blocked":
            all(token in receiver for token in IMPLEMENTED),
        "tera_shift_transform_block":
            "ability\n            == ABILITY_TERA_SHIFT" in script,
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
        default=Path("mr08s13-canonical-ability-terapagos.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_public_hook(root)
    patch_helpers(root)
    patch_switch_restore(root)
    patch_form_change_trigger(root)
    patch_party_normalization(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S13_CANONICAL_ABILITY_TERAPAGOS",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 187,
        "remaining_modern_canonical_mechanics": 0,
        "form_visuals_deferred": True,
        "general_terastallization_ui_deferred": True,
        "policy": "Current-mainline Tera Shift battle-only Terastal state plus canonical post-Terastallization Teraform Zero weather/terrain reset hook.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S13 validation failed")


if __name__ == "__main__":
    main()
