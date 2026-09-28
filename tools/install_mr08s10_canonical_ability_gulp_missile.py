#!/usr/bin/env python3
"""MR08S10 — canonical Gulp Missile battle-state pass.

Implements current-mainline Gulp Missile:
- Cramorant loads Gulping (> 1/2 HP) or Gorging (<= 1/2 HP) after a successful
  Surf or Dive use;
- a damaging hit makes it spit the loaded prey and return to normal, even if
  Cramorant itself faints from that hit;
- the attacker takes 1/4 max HP damage unless protected by Magic Guard;
- Gulping additionally lowers the attacker's Defense by one stage;
- Gorging additionally attempts to paralyze the attacker;
- loaded prey resets when Cramorant leaves battle;
- Gulp Missile is cantsuppress and notransform under current-mainline rules,
  while remaining copyable/swappable/traceable/receivable as in current data.

Type-specific Cramorant form graphics are deferred to Mercury's form-asset pass.
Locked MR07 Summary/editor visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_GULP_MISSILE",)
EXPECTED_IDS = {"ABILITY_GULP_MISSILE": 241}


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
        """    // Mercury MR08S10: 0 normal, 1 Gulping/Arrokuda, 2 Gorging/Pikachu.
    u8 mercuryGulpMissileForm[MAX_BATTLERS];
    u8 mercuryGulpMissileFollowup;
    u8 mercuryGulpMissileSource;

""",
        "Gulp Missile state",
    )


def patch_public_helpers(root: Path) -> None:
    path = root / "include/battle/battle_lib.h"
    insert_before_once(
        path,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);
""",
        """void Mercury_TryLoadGulpMissile(BattleSystem *battleSys, BattleContext *battleCtx);
BOOL Mercury_TryGulpMissileFollowup(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);

""",
        "Gulp Missile helper declarations",
    )


def patch_battle_lib(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)
""",
        """void Mercury_TryLoadGulpMissile(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int battler = battleCtx->attacker;

    if (battler >= BattleSystem_GetMaxBattlers(battleSys)
        || battleCtx->battleMons[battler].curHP == 0
        || battleCtx->battleMons[battler].species != SPECIES_CRAMORANT
        || Battler_Ability(battleCtx, battler) != ABILITY_GULP_MISSILE
        || battleCtx->mercuryGulpMissileForm[battler] != 0
        || (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM)) {
        return;
    }

    if (battleCtx->moveCur != MOVE_SURF
        && battleCtx->moveCur != MOVE_DIVE) {
        return;
    }

    if (battleCtx->moveStatusFlags & MOVE_STATUS_DID_NOT_HIT) {
        // Dive's charge turn deliberately carries FIRST_OF_MULTI_TURN and is
        // still a successful use for Gulp Missile.
        if (battleCtx->moveCur != MOVE_DIVE
            || (battleCtx->battleStatusMask & SYSCTL_FIRST_OF_MULTI_TURN) == 0) {
            return;
        }
    }

    if (battleCtx->battleMons[battler].curHP
        <= battleCtx->battleMons[battler].maxHP / 2) {
        battleCtx->mercuryGulpMissileForm[battler] = 2;
    } else {
        battleCtx->mercuryGulpMissileForm[battler] = 1;
    }
}

BOOL Mercury_TryGulpMissileFollowup(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int *subscript)
{
    int followup = battleCtx->mercuryGulpMissileFollowup;
    int source = battleCtx->mercuryGulpMissileSource;

    if (followup == 0) {
        return FALSE;
    }

    battleCtx->mercuryGulpMissileFollowup = 0;

    if (battleCtx->attacker >= BattleSystem_GetMaxBattlers(battleSys)
        || battleCtx->battleMons[battleCtx->attacker].curHP == 0) {
        return FALSE;
    }

    battleCtx->sideEffectMon = battleCtx->attacker;
    battleCtx->sideEffectType = SIDE_EFFECT_TYPE_ABILITY;
    battleCtx->msgBattlerTemp = source;

    if (followup == 1) {
        battleCtx->sideEffectParam = MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE;
        *subscript = subscript_update_stat_stage;
    } else {
        *subscript = subscript_paralyze;
    }

    return TRUE;
}

""",
        "Gulp Missile helpers",
    )

    replace_in_function(
        path,
        "void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)",
        """    battleCtx->mercuryZenActive[battler] = FALSE;
""",
        """    battleCtx->mercuryGulpMissileForm[battler] = 0;

    battleCtx->mercuryZenActive[battler] = FALSE;
""",
        "Gulp Missile switch reset",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)",
        """    case ABILITY_COLOR_CHANGE:
""",
        """    case ABILITY_GULP_MISSILE:
        if (ATTACKING_MON.curHP
            && battleCtx->mercuryGulpMissileForm[battleCtx->defender] != 0
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int form =
                battleCtx->mercuryGulpMissileForm[battleCtx->defender];

            // Spit the loaded prey immediately; Cramorant returns to normal
            // even if the projectile's damage is blocked by Magic Guard.
            battleCtx->mercuryGulpMissileForm[battleCtx->defender] = 0;
            battleCtx->mercuryGulpMissileFollowup = form;
            battleCtx->mercuryGulpMissileSource = battleCtx->defender;

            if (Battler_Ability(battleCtx, battleCtx->attacker)
                != ABILITY_MAGIC_GUARD) {
                battleCtx->hpCalcTemp =
                    -(ATTACKING_MON.maxHP / 4);
                if (battleCtx->hpCalcTemp == 0) {
                    battleCtx->hpCalcTemp = -1;
                }
                battleCtx->msgBattlerTemp = battleCtx->defender;
                *subscript = subscript_rough_skin;
                result = TRUE;
            }
        }
        break;

    case ABILITY_COLOR_CHANGE:
""",
        "Gulp Missile damaging-hit trigger",
    )

    # Current-mainline Gulp Missile is receivable; remove the older HG-Engine
    # exclusion inherited by MR08K.
    replace_in_function(
        path,
        "static BOOL Mercury_AbilityCanBeReceived(int ability)",
        """    case ABILITY_GULP_MISSILE:
""",
        """""",
        "Gulp Missile Receiver current-mainline rule",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    replace_in_function(
        path,
        "static void BattleControllerPlayer_AfterMoveMessage(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        case ONE_HIT_EXTRA_FLINCH:
            battleCtx->afterMoveMessageState++;
""",
        """        case ONE_HIT_EXTRA_FLINCH:
            int gulpSeq;
            if (Mercury_TryGulpMissileFollowup(
                    battleSys, battleCtx, &gulpSeq)) {
                LOAD_SUBSEQ(gulpSeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }

            battleCtx->afterMoveMessageState++;
""",
        "Gulp Missile one-hit followup",
    )

    replace_in_function(
        path,
        "static void BattleControllerPlayer_AfterMoveMessage(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        case MULTI_HIT_STATUS:
            battleCtx->afterMoveMessageState++;
""",
        """        case MULTI_HIT_STATUS:
            int gulpSeq;
            if (Mercury_TryGulpMissileFollowup(
                    battleSys, battleCtx, &gulpSeq)) {
                LOAD_SUBSEQ(gulpSeq);
                battleCtx->commandNext = battleCtx->command;
                battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
                return;
            }

            battleCtx->afterMoveMessageState++;
""",
        "Gulp Missile multi-hit followup",
    )

    replace_in_function(
        path,
        "static void BattleControllerPlayer_AfterMoveEffects(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    default:
        break;
    }

    battleCtx->afterMoveEffectState = AFTER_MOVE_EFFECT_START;
""",
        """    default:
        Mercury_TryLoadGulpMissile(battleSys, battleCtx);
        break;
    }

    battleCtx->afterMoveEffectState = AFTER_MOVE_EFFECT_START;
""",
        "Gulp Missile Surf/Dive load hook",
    )


def patch_current_mainline_flags(root: Path) -> None:
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"
    transform = root / "res/battle/scripts/subscripts/subscript_transform_into_target.s"
    lib = root / "src/battle/battle_lib.c"

    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_GULP_MISSILE, _034\n",
        "Gulp Missile Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_GULP_MISSILE, _041\n",
        "Gulp Missile Worry Seed lock",
    )
    insert_before_once(
        transform,
        "    Call BATTLE_SUBSCRIPT_ATTACK_MESSAGE_AND_ANIMATION\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_GULP_MISSILE, _023\n",
        "Gulp Missile Transform target lock",
    )

    replace_once(
        lib,
        """                    || (battleCtx->battleMons[target].moveEffectsMask
                        & MOVE_EFFECT_SEMI_INVULNERABLE)) {
""",
        """                    || (battleCtx->battleMons[target].moveEffectsMask
                        & MOVE_EFFECT_SEMI_INVULNERABLE)
                    || battleCtx->battleMons[target].ability
                        == ABILITY_GULP_MISSILE) {
""",
        "Gulp Missile Imposter target lock",
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
    controller = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    transform = (root / "res/battle/scripts/subscripts/subscript_transform_into_target.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    checks = {
        "gulp_state":
            "mercuryGulpMissileForm[MAX_BATTLERS]" in ctx
            and "mercuryGulpMissileFollowup" in ctx,
        "surf_dive_load":
            "MOVE_SURF" in lib
            and "MOVE_DIVE" in lib
            and "mercuryGulpMissileForm[battler] = 2" in lib
            and "mercuryGulpMissileForm[battler] = 1" in lib,
        "half_hp_form_split":
            "<= battleCtx->battleMons[battler].maxHP / 2" in lib,
        "quarter_hp_projectile":
            "-(ATTACKING_MON.maxHP / 4)" in lib,
        "magic_guard_blocks_damage":
            "!= ABILITY_MAGIC_GUARD" in lib,
        "gulping_defense_drop":
            "MOVE_SUBSCRIPT_PTR_DEFENSE_DOWN_1_STAGE" in lib
            and "subscript_update_stat_stage" in lib,
        "gorging_paralysis":
            "subscript_paralyze" in lib,
        "followup_controller":
            controller.count("Mercury_TryGulpMissileFollowup") >= 2
            and "Mercury_TryLoadGulpMissile" in controller,
        "switch_resets_prey":
            "mercuryGulpMissileForm[battler] = 0;" in lib,
        "neutralizing_gas_cannot_suppress":
            "ABILITY_GULP_MISSILE" in cannot,
        "gastro_and_worry_seed_fail":
            "ABILITY_GULP_MISSILE" in suppress
            and "ABILITY_GULP_MISSILE" in worry,
        "not_transformable":
            "ABILITY_GULP_MISSILE" in transform
            and "== ABILITY_GULP_MISSILE" in lib,
        "current_receiver_rule":
            "ABILITY_GULP_MISSILE" not in receiver,
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
        default=Path("mr08s10-canonical-ability-gulp-missile.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()

    patch_context(root)
    patch_public_helpers(root)
    patch_battle_lib(root)
    patch_controller(root)
    patch_current_mainline_flags(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S10_CANONICAL_ABILITY_GULP_MISSILE",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "running_modern_mechanics_total": 183,
        "remaining_modern_canonical_mechanics": 4,
        "form_visuals_deferred": True,
        "policy": "Current-mainline Gulp Missile Surf/Dive prey loading, retaliatory damage and Arrokuda/Pikachu follow-up effects.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S10 validation failed")


if __name__ == "__main__":
    main()
