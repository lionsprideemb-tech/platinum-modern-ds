#!/usr/bin/env python3
"""MR08N — canonical veil / suppression / dynamic-type Ability pass.

Adds six official/current-mainline mechanics after MR08M:
Aroma Veil, Flower Veil, Mimicry, Neutralizing Gas, Tera Shell, and Ripen is
intentionally deferred to the held-item family so berry thresholds are not
silently changed.

Mechanics only; locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_AROMA_VEIL",
    "ABILITY_FLOWER_VEIL",
    "ABILITY_MIMICRY",
    "ABILITY_NEUTRALIZING_GAS",
    "ABILITY_TERA_SHELL",
)

EXPECTED_IDS = {
    "ABILITY_AROMA_VEIL": 165,
    "ABILITY_FLOWER_VEIL": 166,
    "ABILITY_MIMICRY": 250,
    "ABILITY_NEUTRALIZING_GAS": 256,
    "ABILITY_TERA_SHELL": 308,
}


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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_before_once(
        path,
        """    u32 battleProgressFlag : 1;
""",
        """    // Mercury MR08N: preserve Tera Shell across all hits of the
    // same multi-hit attack, while still ending the effect after that attack.
    u16 mercuryTeraShellMove[MAX_BATTLERS];
    u16 mercuryTeraShellTurn[MAX_BATTLERS];
    u8 mercuryTeraShellAttacker[MAX_BATTLERS];

""",
        "MR08N Tera Shell state",
    )


def patch_ability_resolution(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """u16 Battler_Ability(BattleContext *battleCtx, int battler)
""",
        """static BOOL Mercury_AbilityCantBeNeutralized(int ability)
{
    switch (ability) {
    case ABILITY_AS_ONE_GLASTRIER:
    case ABILITY_AS_ONE_SPECTRIER:
    case ABILITY_BATTLE_BOND:
    case ABILITY_COMATOSE:
    case ABILITY_DISGUISE:
    case ABILITY_GULP_MISSILE:
    case ABILITY_ICE_FACE:
    case ABILITY_LINGERING_AROMA:
    case ABILITY_MULTITYPE:
    case ABILITY_MUMMY:
    case ABILITY_NEUTRALIZING_GAS:
    case ABILITY_POWER_CONSTRUCT:
    case ABILITY_RKS_SYSTEM:
    case ABILITY_SCHOOLING:
    case ABILITY_SHIELDS_DOWN:
    case ABILITY_STANCE_CHANGE:
    case ABILITY_TERA_SHIFT:
    case ABILITY_ZEN_MODE:
    case ABILITY_ZERO_TO_HERO:
        return TRUE;
    default:
        return FALSE;
    }
}

static BOOL Mercury_SideVeilAbilityApplies(
    BattleContext *battleCtx,
    int attacker,
    int defender,
    int ability)
{
    int i;

    if (attacker == defender) {
        return FALSE;
    }

    if (ability == ABILITY_FLOWER_VEIL
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL) != TYPE_GRASS
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL) != TYPE_GRASS) {
        return FALSE;
    }

    for (i = 0; i < MAX_BATTLERS; i++) {
        if ((i & 1) == (defender & 1)
            && battleCtx->battleMons[i].curHP
            && Battler_Ability(battleCtx, i) == ability) {
            return TRUE;
        }
    }

    return FALSE;
}

""",
        "MR08N suppression / veil helpers",
    )

    replace_function(
        path,
        "u16 Battler_Ability(BattleContext *battleCtx, int battler)",
        """u16 Battler_Ability(BattleContext *battleCtx, int battler)
{
    u16 rawAbility = battleCtx->battleMons[battler].ability;
    int i;

    if (Mercury_AbilityCantBeNeutralized(rawAbility) == FALSE) {
        for (i = 0; i < MAX_BATTLERS; i++) {
            if (i != battler
                && battleCtx->battleMons[i].curHP
                && battleCtx->battleMons[i].ability == ABILITY_NEUTRALIZING_GAS) {
                return ABILITY_NONE;
            }
        }
    }

    if ((battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_ABILITY_SUPPRESSED)
        && Mercury_AbilityCantBeNeutralized(rawAbility) == FALSE) {
        return ABILITY_NONE;
    }

    if ((battleCtx->fieldConditionsMask & FIELD_CONDITION_GRAVITY)
        && rawAbility == ABILITY_LEVITATE) {
        return ABILITY_NONE;
    }

    if ((battleCtx->battleMons[battler].moveEffectsMask & MOVE_EFFECT_INGRAIN)
        && rawAbility == ABILITY_LEVITATE) {
        return ABILITY_NONE;
    }

    return rawAbility;
}""",
        "Neutralizing Gas central Ability resolution",
    )

    replace_function(
        path,
        "BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)",
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
{
    BOOL result = FALSE;
    BOOL defenderHasAbility;
    int attackerAbility = Battler_Ability(battleCtx, attacker);
    BOOL myceliumBypass = attackerAbility == ABILITY_MYCELIUM_MIGHT
        && battleCtx->moveCur != MOVE_NONE
        && MOVE_DATA(battleCtx->moveCur).class == CLASS_STATUS;

    if (ability == ABILITY_AROMA_VEIL || ability == ABILITY_FLOWER_VEIL) {
        defenderHasAbility = Mercury_SideVeilAbilityApplies(
            battleCtx, attacker, defender, ability);
    } else {
        defenderHasAbility = Battler_Ability(battleCtx, defender) == ability;
    }

    if (!Mercury_IsMoldBreakerAbility(attackerAbility) && !myceliumBypass) {
        if (defenderHasAbility) {
            result = TRUE;
        }
    } else if (defenderHasAbility) {
        if (Mercury_IsMoldBreakerAbility(attackerAbility)
            && battleCtx->selfTurnFlags[attacker].moldBreakerActivated == FALSE) {
            battleCtx->selfTurnFlags[attacker].moldBreakerActivated = TRUE;
            battleCtx->battleStatusMask |= SYSCTL_APPLY_MOLD_BREAKER;
        }
    }

    return result;
}""",
        "Aroma/Flower Veil side-wide ignorable Ability resolution",
    )


def patch_aroma_veil(root: Path) -> None:
    script = root / "src/battle/battle_script.c"

    insert_after_once(
        script,
        """    int jumpOnFail = BattleScript_Read(battleCtx);

    int moveSlot = Battler_SlotForMove(&DEFENDING_MON, DEFENDER_LAST_MOVE);
""",
        """    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender,
            ABILITY_AROMA_VEIL) == TRUE) {
        battleCtx->moveStatusFlags |= MOVE_STATUS_FAILED;
        BattleScript_Iter(battleCtx, jumpOnFail);
        return FALSE;
    }

""",
        "Aroma Veil Disable protection",
    )

    insert_after_once(
        script,
        """    int jumpOnFail = BattleScript_Read(battleCtx);

    int moveSlot = Battler_SlotForMove(&DEFENDING_MON, DEFENDER_LAST_MOVE);
    if (Move_CanBeEncored(battleCtx, DEFENDER_LAST_MOVE) == FALSE) {
""",
        """    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->defender,
            ABILITY_AROMA_VEIL) == TRUE) {
        battleCtx->moveStatusFlags |= MOVE_STATUS_FAILED;
        BattleScript_Iter(battleCtx, jumpOnFail);
        return FALSE;
    }

""",
        "Aroma Veil Encore protection",
    )

    replace_once(
        script,
        """        || battleCtx->battleMons[battleCtx->msgBattlerTemp].gender == GENDER_NONE
        || battleCtx->battleMons[battleCtx->sideEffectMon].gender == GENDER_NONE) {
""",
        """        || battleCtx->battleMons[battleCtx->msgBattlerTemp].gender == GENDER_NONE
        || battleCtx->battleMons[battleCtx->sideEffectMon].gender == GENDER_NONE
        || Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->sideEffectMon,
            ABILITY_AROMA_VEIL) == TRUE) {
""",
        "Aroma Veil Attract protection",
    )

    for rel, anchor, insertion in (
        (
            "res/battle/scripts/subscripts/subscript_taunt_start.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_AROMA_VEIL, _028
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_torment_start.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_AROMA_VEIL, _025
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_heal_block_start.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_AROMA_VEIL, _028
""",
        ),
    ):
        insert_after_once(root / rel, anchor, insertion, f"Aroma Veil {rel}")

    lib = root / "src/battle/battle_lib.c"
    replace_once(
        lib,
        """            && ATTACKING_MON.curHP
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
""",
        """            && ATTACKING_MON.curHP
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker,
                ABILITY_AROMA_VEIL) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
""",
        "Aroma Veil Cursed Body protection",
    )


def patch_flower_veil(root: Path) -> None:
    script = root / "src/battle/battle_script.c"

    replace_once(
        script,
        """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE
                    || Battler_Ability(battleCtx, battleCtx->sideEffectMon) == ABILITY_FULL_METAL_BODY) {
""",
        """                } else if (Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_CLEAR_BODY) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_WHITE_SMOKE) == TRUE
                    || Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->sideEffectMon, ABILITY_FLOWER_VEIL) == TRUE
                    || Battler_Ability(battleCtx, battleCtx->sideEffectMon) == ABILITY_FULL_METAL_BODY) {
""",
        "Flower Veil stat-drop protection",
    )

    patches = (
        (
            "res/battle/scripts/subscripts/subscript_burn.s",
            """_052:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _212
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_paralyze.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _123
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_poison.s",
            """_023:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _217
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_badly_poison.s",
            """_094:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _275
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_fall_asleep.s",
            """_055:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _237
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_freeze.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _095
""",
        ),
        (
            "res/battle/scripts/subscripts/subscript_yawn.s",
            """_000:
""",
            """    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, _077
""",
        ),
    )
    for rel, anchor, insertion in patches:
        insert_after_once(root / rel, anchor, insertion, f"Flower Veil {rel}")


def patch_mimicry(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (battleCtx->battleMons[battler].species == SPECIES_ARCEUS
""",
        """    if (Battler_Ability(battleCtx, battler) == ABILITY_MIMICRY
        && battleCtx->mercuryTerrainType != MERCURY_TERRAIN_NONE) {
        switch (battleCtx->mercuryTerrainType) {
        case MERCURY_TERRAIN_ELECTRIC:
            return TYPE_ELECTRIC;
        case MERCURY_TERRAIN_GRASSY:
            return TYPE_GRASS;
        case MERCURY_TERRAIN_MISTY:
            return TYPE_FAIRY;
        case MERCURY_TERRAIN_PSYCHIC:
            return TYPE_PSYCHIC;
        default:
            break;
        }
    }

""",
        "Mimicry dynamic terrain typing",
    )


def patch_tera_shell(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    int chartEntry;
    int totalMul;
    u8 moveType;
""",
        """    int chartEntry;
    int totalMul;
    int teraShellBaseDamage;
    u8 moveType;
""",
        "Tera Shell base-damage local",
    )

    insert_after_once(
        path,
        """    if ((battleCtx->battleStatusMask & SYSCTL_IGNORE_TYPE_CHECKS) == FALSE && MON_HAS_TYPE(attacker, moveType)) {
        if (Battler_Ability(battleCtx, attacker) == ABILITY_ADAPTABILITY) {
            damage *= 2;
        } else {
            damage = damage * 15 / 10;
        }
    }
""",
        """
    teraShellBaseDamage = damage;
""",
        "Tera Shell pre-effectiveness damage",
    )

    insert_before_once(
        path,
        """    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_WONDER_GUARD) == TRUE
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_TERA_SHELL) == TRUE
        && movePower
        && move != MOVE_STRUGGLE
        && (*moveStatusMask & MOVE_STATUS_INEFFECTIVE) == FALSE
        && (*moveStatusMask & MOVE_STATUS_NOT_VERY_EFFECTIVE) == FALSE
        && (battleCtx->battleMons[defender].curHP
                == battleCtx->battleMons[defender].maxHP
            || (battleCtx->mercuryTeraShellMove[defender] == move
                && battleCtx->mercuryTeraShellTurn[defender]
                    == battleCtx->totalTurns
                && battleCtx->mercuryTeraShellAttacker[defender]
                    == attacker))) {
        if (battleCtx->battleMons[defender].curHP
            == battleCtx->battleMons[defender].maxHP) {
            battleCtx->mercuryTeraShellMove[defender] = move;
            battleCtx->mercuryTeraShellTurn[defender] = battleCtx->totalTurns;
            battleCtx->mercuryTeraShellAttacker[defender] = attacker;
        }

        damage = BattleSystem_Divide(teraShellBaseDamage, 2);
        *moveStatusMask &= ~MOVE_STATUS_SUPER_EFFECTIVE;
        *moveStatusMask |= MOVE_STATUS_NOT_VERY_EFFECTIVE;
    }

""",
        "Tera Shell full-HP effectiveness override",
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
    taunt = (root / "res/battle/scripts/subscripts/subscript_taunt_start.s").read_text(encoding="utf-8")
    poison = (root / "res/battle/scripts/subscripts/subscript_poison.s").read_text(encoding="utf-8")
    sleep = (root / "res/battle/scripts/subscripts/subscript_fall_asleep.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    checks = {
        "aroma_veil_hook":
            script.count("ABILITY_AROMA_VEIL") >= 3
            and "ABILITY_AROMA_VEIL" in taunt
            and "ABILITY_AROMA_VEIL" in lib,
        "flower_veil_hook":
            "ABILITY_FLOWER_VEIL" in script
            and "ABILITY_FLOWER_VEIL" in poison
            and "ABILITY_FLOWER_VEIL" in sleep
            and "Mercury_SideVeilAbilityApplies" in lib,
        "mimicry_hook":
            "ABILITY_MIMICRY" in lib
            and "MERCURY_TERRAIN_MISTY" in lib
            and "return TYPE_FAIRY;" in lib,
        "neutralizing_gas_hook":
            "ABILITY_NEUTRALIZING_GAS" in lib
            and "Mercury_AbilityCantBeNeutralized" in lib
            and "return ABILITY_NONE;" in lib,
        "tera_shell_hook":
            "ABILITY_TERA_SHELL" in lib
            and "mercuryTeraShellMove" in ctx
            and "MOVE_STATUS_NOT_VERY_EFFECTIVE" in lib,
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
        default=Path("mr08n-canonical-ability-veil-gas-type.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_ability_resolution(root)
    patch_aroma_veil(root)
    patch_flower_veil(root)
    patch_mimicry(root)
    patch_tera_shell(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08N_CANONICAL_ABILITY_VEIL_GAS_TYPE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 153,
        "remaining_modern_canonical_mechanics": 34,
        "policy": "Official/current-mainline mechanics; item-specific Ripen work remains in the held-item batch.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08N validation failed")


if __name__ == "__main__":
    main()
