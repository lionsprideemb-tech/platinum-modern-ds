#!/usr/bin/env python3
"""MR08O — canonical Ability veil / dynamic-type pass.

Adds three distinct official/current-mainline Ability mechanics after the
successful MR08N weather/suppression/shell pass:

- Aroma Veil
- Flower Veil
- Mimicry

MR08N already owns Neutralizing Gas and Tera Shell, so this pass deliberately
does not repatch either mechanic. Mechanics only; locked MR07 Summary/editor
visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = (
    "ABILITY_AROMA_VEIL",
    "ABILITY_FLOWER_VEIL",
    "ABILITY_MIMICRY",
)

EXPECTED_IDS = {
    "ABILITY_AROMA_VEIL": 165,
    "ABILITY_FLOWER_VEIL": 166,
    "ABILITY_MIMICRY": 250,
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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
        for line in (root / "generated/abilities.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id":
            len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def patch_side_veil_resolution(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)
""",
        """static BOOL Mercury_SideVeilAbilityApplies(
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
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_1, NULL)
            != TYPE_GRASS
        && BattleMon_Get(battleCtx, defender, BATTLEMON_TYPE_2, NULL)
            != TYPE_GRASS) {
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
        "MR08O side-wide veil helper",
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
        "MR08O side-wide Aroma/Flower Veil resolution",
    )


def patch_aroma_veil(root: Path) -> None:
    script = root / "src/battle/battle_script.c"

    replace_once(
        script,
        """static BOOL BtlCmd_TryDisable(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

""",
        """static BOOL BtlCmd_TryDisable(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

    if (Battler_IgnorableAbility(
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

    replace_once(
        script,
        """static BOOL BtlCmd_TryEncore(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

""",
        """static BOOL BtlCmd_TryEncore(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

    if (Battler_IgnorableAbility(
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
        """static BOOL BtlCmd_TryAttract(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

""",
        """static BOOL BtlCmd_TryAttract(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BattleScript_Iter(battleCtx, 1);
    int jumpOnFail = BattleScript_Read(battleCtx);

    if (Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battleCtx->sideEffectMon,
            ABILITY_AROMA_VEIL) == TRUE) {
        BattleScript_Iter(battleCtx, jumpOnFail);
        return FALSE;
    }

""",
        "Aroma Veil Attract protection",
    )

    for rel, fail_label in (
        ("res/battle/scripts/subscripts/subscript_taunt_start.s", "_028"),
        ("res/battle/scripts/subscripts/subscript_torment_start.s", "_025"),
        ("res/battle/scripts/subscripts/subscript_heal_block_start.s", "_028"),
    ):
        insert_after_once(
            root / rel,
            """_000:
""",
            f"""    CheckIgnorableAbility CHECK_HAVE, BTLSCR_DEFENDER, ABILITY_AROMA_VEIL, {fail_label}
""",
            f"Aroma Veil protection in {rel}",
        )

    lib = root / "src/battle/battle_lib.c"
    replace_once(
        lib,
        """    case ABILITY_CURSED_BODY:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_CURSED_BODY) == TRUE
            && ATTACKING_MON.curHP
""",
        """    case ABILITY_CURSED_BODY:
        if (Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_CURSED_BODY) == TRUE
            && ATTACKING_MON.curHP
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->defender,
                battleCtx->attacker,
                ABILITY_AROMA_VEIL) == FALSE
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

    status_hooks = (
        ("res/battle/scripts/subscripts/subscript_burn.s", "_052", "_212"),
        ("res/battle/scripts/subscripts/subscript_paralyze.s", "_000", "_123"),
        ("res/battle/scripts/subscripts/subscript_poison.s", "_023", "_217"),
        ("res/battle/scripts/subscripts/subscript_badly_poison.s", "_094", "_275"),
        ("res/battle/scripts/subscripts/subscript_fall_asleep.s", "_055", "_237"),
        ("res/battle/scripts/subscripts/subscript_freeze.s", "_000", "_095"),
        ("res/battle/scripts/subscripts/subscript_yawn.s", "_000", "_077"),
    )
    for rel, anchor_label, fail_label in status_hooks:
        insert_after_once(
            root / rel,
            f"""{anchor_label}:
""",
            f"""    CheckIgnorableAbility CHECK_HAVE, BTLSCR_SIDE_EFFECT_MON, ABILITY_FLOWER_VEIL, {fail_label}
""",
            f"Flower Veil protection in {rel}",
        )


def patch_mimicry(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_before_once(
        path,
        """    if (battleCtx->battleMons[battler].species == SPECIES_ARCEUS
        && battleCtx->battleMons[battler].ability == ABILITY_MULTITYPE) {
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
        "Mimicry terrain-driven typing",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    taunt = (
        root / "res/battle/scripts/subscripts/subscript_taunt_start.s"
    ).read_text(encoding="utf-8")
    poison = (
        root / "res/battle/scripts/subscripts/subscript_poison.s"
    ).read_text(encoding="utf-8")
    sleep = (
        root / "res/battle/scripts/subscripts/subscript_fall_asleep.s"
    ).read_text(encoding="utf-8")
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
        "mr08n_suppression_preserved":
            "Mercury_NeutralizingGasRawActive" in lib
            and "ABILITY_NEUTRALIZING_GAS" in lib,
        "mr08n_tera_shell_preserved":
            "ABILITY_TERA_SHELL" in lib,
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
        default=Path("mr08o-canonical-ability-veil-type.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_side_veil_resolution(root)
    patch_aroma_veil(root)
    patch_flower_veil(root)
    patch_mimicry(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08O_CANONICAL_ABILITY_VEIL_TYPE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 156,
        "remaining_modern_canonical_mechanics": 31,
        "policy": "Official/current-mainline mechanics; Redux rewrites remain review-only.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08O validation failed")


if __name__ == "__main__":
    main()
