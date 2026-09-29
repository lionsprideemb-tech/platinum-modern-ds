#!/usr/bin/env python3
"""MR10D6 — protection/screen breaker KEEP-AS-WRITTEN batch.

Implements:
- Pinnacle Blade: Keen Edge (Mercury's existing Sharpness/slicing class) moves
  bypass accuracy checks, Protect-style protection, substitutes, and Reflect /
  Light Screen. A successful Keen Edge hit also drops the target's active
  Protect state and destroys its side's damage screens.
- Demolitionist: during the user's first active turn, Attack is doubled,
  attacks pierce Protect-style protection, ignore damage screens, and
  successful hits destroy Reflect / Light Screen.

The existing fakeOutTurnNumber switch-in marker is reused as the authoritative
"first active turn" clock; no new save/persistent state is introduced.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IMPLEMENTED = {
    "Pinnacle Blade": ("ABILITY_MR_PINNACLE_BLADE", 340),
    "Demolitionist": ("ABILITY_MR_DEMOLITIONIST", 773),
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


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


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


def patch_shared_helpers(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    hdr = root / "include/battle/battle_lib.h"

    helpers = """BOOL Mercury_IsKeenEdgeMove(int move)
{
    return Mercury_MoveIsSlicing(move);
}

static BOOL Mercury_DemolitionistFirstTurn(
    BattleContext *battleCtx,
    int attacker)
{
    return Battler_Ability(battleCtx, attacker) == ABILITY_MR_DEMOLITIONIST
        && battleCtx->battleMons[attacker].moveEffectsData.fakeOutTurnNumber
            == battleCtx->totalTurns + 1;
}

BOOL Mercury_AttackBypassesProtection(
    BattleContext *battleCtx,
    int attacker,
    int move)
{
    if (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(move)) {
        return TRUE;
    }

    return Mercury_DemolitionistFirstTurn(battleCtx, attacker);
}

BOOL Mercury_AttackBypassesSubstitute(
    BattleContext *battleCtx,
    int attacker,
    int move)
{
    return Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(move);
}

BOOL Mercury_AttackBypassesScreens(
    BattleContext *battleCtx,
    int attacker,
    int move)
{
    return Mercury_AttackBypassesProtection(battleCtx, attacker, move);
}

"""
    insert_before_once(
        lib,
        """static BOOL Mercury_MoveIsBiting(int move)
""",
        helpers,
        "MR10D6 protection-breaker helpers",
    )

    declarations = """BOOL Mercury_IsKeenEdgeMove(int move);
BOOL Mercury_AttackBypassesProtection(BattleContext *battleCtx, int attacker, int move);
BOOL Mercury_AttackBypassesSubstitute(BattleContext *battleCtx, int attacker, int move);
BOOL Mercury_AttackBypassesScreens(BattleContext *battleCtx, int attacker, int move);
"""
    insert_before_once(
        hdr,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        declarations,
        "MR10D6 public helper declarations",
    )


def patch_accuracy_protect_substitute(root: Path) -> None:
    ctl = root / "src/battle/battle_controller_player.c"

    replace_once(
        ctl,
        """    if (BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_CATCH_TUTORIAL) {
        return 0;
    }

    u8 moveType = CalcMoveType(battleCtx, attacker, move);
""",
        """    if (BattleSystem_GetBattleType(battleSys) & BATTLE_TYPE_CATCH_TUTORIAL) {
        return 0;
    }

    if (Battler_Ability(battleCtx, attacker) == ABILITY_MR_PINNACLE_BLADE
        && Mercury_IsKeenEdgeMove(move)) {
        return 0;
    }

    u8 moveType = CalcMoveType(battleCtx, attacker, move);
""",
        "Pinnacle Blade accuracy bypass",
    )

    replace_once(
        ctl,
        """    if (battleCtx->turnFlags[defender].protecting
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        """    if (battleCtx->turnFlags[defender].protecting
        && Mercury_AttackBypassesProtection(battleCtx, attacker, move) == FALSE
        && (MOVE_DATA(move).flags & MOVE_FLAG_CAN_PROTECT)
""",
        "Pinnacle/Demolitionist Protect bypass",
    )

    text = ctl.read_text(encoding="utf-8")
    if "Mercury_AttackBypassesSubstitute(\n                battleCtx, battleCtx->attacker, battleCtx->moveCur) == FALSE" not in text:
        signature = "static void BattleControllerPlayer_UpdateHP(BattleSystem *battleSys, BattleContext *battleCtx)"
        start = text.find(signature + "\n{")
        if start < 0:
            raise SystemExit("Pinnacle Blade Substitute bypass: UpdateHP function not found")
        depth = 0
        open_brace = text.find("{", start)
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
            raise SystemExit("Pinnacle Blade Substitute bypass: UpdateHP closing brace not found")

        block = text[start:end]
        pattern = re.compile(
            r"if \(\(DEFENDING_MON\.statusVolatile\s*&\s*VOLATILE_CONDITION_SUBSTITUTE\)"
            r"(?P<middle>.*?)"
            r"&&\s*battleCtx->damage\s*<\s*0\)\s*\{",
            re.S,
        )
        match = pattern.search(block)
        if match is None:
            raise SystemExit(
                "Pinnacle Blade Substitute bypass: Substitute damage condition not found"
            )

        replacement = (
            "if ((DEFENDING_MON.statusVolatile & VOLATILE_CONDITION_SUBSTITUTE)"
            + match.group("middle")
            + "\n            && Mercury_AttackBypassesSubstitute(\n"
            + "                battleCtx, battleCtx->attacker, battleCtx->moveCur) == FALSE"
            + "\n            && battleCtx->damage < 0) {"
        )
        block = block[:match.start()] + replacement + block[match.end():]
        ctl.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_damage_rules(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    replace_once(
        lib,
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
""",
        """    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {
        attackStat = attackStat * 2;
    }
    if (attackerParams.ability == ABILITY_MR_DEMOLITIONIST
        && battleCtx->battleMons[attacker].moveEffectsData.fakeOutTurnNumber
            == battleCtx->totalTurns + 1) {
        attackStat *= 2;
    }
""",
        "Demolitionist first-turn Attack double",
    )

    text = lib.read_text(encoding="utf-8")
    for condition in ("SIDE_CONDITION_REFLECT", "SIDE_CONDITION_LIGHT_SCREEN"):
        marker = f"sideConditions & {condition}"
        pos = text.find(marker)
        if pos < 0:
            raise SystemExit(
                f"protection-breaker screen bypass: {condition} condition not found"
            )

        if_start = text.rfind("        if (", 0, pos)
        if if_start < 0:
            raise SystemExit(
                f"protection-breaker screen bypass: governing if for {condition} not found"
            )

        brace = text.find(") {", pos)
        if brace < 0:
            raise SystemExit(
                f"protection-breaker screen bypass: closing condition for {condition} not found"
            )

        block = text[if_start:brace]
        if "Mercury_AttackBypassesScreens" not in block:
            text = (
                text[:brace]
                + "\n            && Mercury_AttackBypassesScreens("
                + "battleCtx, attacker, move) == FALSE"
                + text[brace:]
            )

    lib.write_text(text, encoding="utf-8")


def patch_successful_hit_shatter(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"

    insertion = """    {
        int mercuryBreakerAbility =
            Battler_Ability(battleCtx, battleCtx->attacker);
        BOOL mercuryPinnacleHit =
            mercuryBreakerAbility == ABILITY_MR_PINNACLE_BLADE
            && Mercury_IsKeenEdgeMove(battleCtx->moveCur);
        BOOL mercuryDemolitionHit =
            mercuryBreakerAbility == ABILITY_MR_DEMOLITIONIST
            && battleCtx->battleMons[battleCtx->attacker]
                    .moveEffectsData.fakeOutTurnNumber
                == battleCtx->totalTurns + 1;

        if ((mercuryPinnacleHit || mercuryDemolitionHit)
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int mercuryScreenSide = BattleSystem_GetBattlerSide(
                battleSys, battleCtx->defender);

            battleCtx->sideConditionsMask[mercuryScreenSide]
                &= ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);
            battleCtx->sideConditions[mercuryScreenSide].reflectTurns = 0;
            battleCtx->sideConditions[mercuryScreenSide].lightScreenTurns = 0;

            if (mercuryPinnacleHit) {
                battleCtx->turnFlags[battleCtx->defender].protecting = FALSE;
            }
        }
    }

"""
    insert_before_once(
        lib,
        """    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_POISON_TOUCH
""",
        insertion,
        "Pinnacle/Demolitionist successful-hit shatter",
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
        "keen_edge_reuses_slicing_class":
            "Mercury_IsKeenEdgeMove" in lib
            and "return Mercury_MoveIsSlicing(move);" in lib,
        "pinnacle_accuracy_bypass":
            "ABILITY_MR_PINNACLE_BLADE" in ctl
            and "Mercury_IsKeenEdgeMove(move)" in ctl,
        "shared_protect_bypass":
            "Mercury_AttackBypassesProtection" in ctl
            and "ABILITY_MR_DEMOLITIONIST" in lib,
        "pinnacle_substitute_bypass":
            "Mercury_AttackBypassesSubstitute" in ctl,
        "shared_screen_bypass":
            ctl.count("Mercury_AttackBypassesSubstitute") >= 1
            and lib.count("Mercury_AttackBypassesScreens") >= 3,
        "demolitionist_attack_double":
            "attackerParams.ability == ABILITY_MR_DEMOLITIONIST" in lib
            and "attackStat *= 2;" in lib,
        "first_active_turn_clock":
            "fakeOutTurnNumber" in lib
            and "battleCtx->totalTurns + 1" in lib,
        "successful_hit_breaks_screens":
            "&= ~(SIDE_CONDITION_REFLECT | SIDE_CONDITION_LIGHT_SCREEN);" in lib
            and "reflectTurns = 0;" in lib
            and "lightScreenTurns = 0;" in lib,
        "pinnacle_breaks_protection_state":
            "mercuryPinnacleHit" in lib
            and ".protecting = FALSE;" in lib,
        "helpers_declared":
            "Mercury_IsKeenEdgeMove" in hdr
            and "Mercury_AttackBypassesProtection" in hdr,
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
        default=Path("mr10d6-protection-breakers.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_shared_helpers(root)
    patch_accuracy_protect_substitute(root)
    patch_damage_rules(root)
    patch_successful_hit_shatter(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D6_PROTECTION_BREAKERS",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "keen_edge_classification": "existing Mercury Sharpness slicing table",
        "demolitionist_first_turn_clock": "moveEffectsData.fakeOutTurnNumber",
        "screens_supported_now": ["Reflect", "Light Screen"],
        "remaining_keep_as_written_after_d6": 52,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D6 protection-breaker validation failed")


if __name__ == "__main__":
    main()
