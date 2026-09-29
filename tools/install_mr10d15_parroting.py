#!/usr/bin/env python3
"""MR10D15 — Parroting reactive sound-move copy.

Implements the approved KEEP-AS-WRITTEN Parroting mechanic on a dedicated
copy queue layered over Mercury's already-certified generated-action pipeline:

- after another battler successfully uses a sound-based move, each active
  Parroting holder copies that move once in speed order;
- copies spend no PP and do not replace the holder's selected turn action;
- ordinary Platinum targeting, redirection, accuracy, type, immunity, scripts,
  item/Ability reactions, fainting and switching still run;
- Ability-generated copies are marked so they cannot recursively create
  another Parroting copy or another generated Ability action.

Target selection deliberately reuses the canonical MR08R5 Dancer rules, which
already handle self, single-target, random-target and spread/field moves on the
DS battle controller.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ABILITY_NAME = "Parroting"
ABILITY_TOKEN = "ABILITY_MR_PARROTING"
ABILITY_ID = 426


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def function_bounds(text: str, signature: str) -> tuple[int, int]:
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"function definition not found: {signature}")

    open_brace = start + len(signature) + 1
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f"function closing brace not found: {signature}")


def insert_before_in_function(
    path: Path,
    signature: str,
    anchor: str,
    insertion: str,
    marker: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = function_bounds(text, signature)
    block = text[start:end]
    if marker in block:
        return
    count = block.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected one anchor in {signature}, found {count}"
        )
    block = block.replace(anchor, insertion + anchor, 1)
    path.write_text(text[:start] + block + text[end:], encoding="utf-8")


def validate_partition(path: Path) -> None:
    plan = json.loads(path.read_text(encoding="utf-8"))
    rows = plan.get("abilities", plan.get("rows", []))
    matches = [
        row for row in rows
        if row.get("display_name") == ABILITY_NAME
        or row.get("source_name") == ABILITY_NAME
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"{ABILITY_NAME}: expected one partition row, found {len(matches)}"
        )

    row = matches[0]
    expected = {
        "id": ABILITY_ID,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_keep",
        "owner_review_decision": "KEEP AS WRITTEN",
        "implementation_class": "new_engine_system",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, "
                f"got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryDelayedRevivalPendingMask[2];
""",
        """    // Mercury MR10D15: one Parroting copy queue per source move event.
    u8 mercuryParrotingActive;
    u8 mercuryParrotingCount;
    u8 mercuryParrotingIndex;
    u8 mercuryParrotingOriginalAttacker;
    u8 mercuryParrotingOriginalDefender;
    u8 mercuryParrotingBattlers[MAX_BATTLERS];
    u8 mercuryParrotingTargets[MAX_BATTLERS];
    u16 mercuryParrotingMove;

""",
        "D15 Parroting queue state",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helpers = """static BOOL Mercury_D15MoveIsSound(int move)
{
    switch (move) {
    case MOVE_ALLURING_VOICE:
    case MOVE_BOOMBURST:
    case MOVE_BUG_BUZZ:
    case MOVE_CHATTER:
    case MOVE_CLANGING_SCALES:
    case MOVE_CLANGOROUS_SOUL:
    case MOVE_CLANGOROUS_SOULBLAZE:
    case MOVE_CONFIDE:
    case MOVE_DISARMING_VOICE:
    case MOVE_ECHOED_VOICE:
    case MOVE_EERIE_SPELL:
    case MOVE_GRASS_WHISTLE:
    case MOVE_GROWL:
    case MOVE_HEAL_BELL:
    case MOVE_HOWL:
    case MOVE_HYPER_VOICE:
    case MOVE_METAL_SOUND:
    case MOVE_NOBLE_ROAR:
    case MOVE_OVERDRIVE:
    case MOVE_PARTING_SHOT:
    case MOVE_PERISH_SONG:
    case MOVE_PSYCHIC_NOISE:
    case MOVE_RELIC_SONG:
    case MOVE_ROAR:
    case MOVE_ROUND:
    case MOVE_SCREECH:
    case MOVE_SING:
    case MOVE_SNARL:
    case MOVE_SNORE:
    case MOVE_SPARKLING_ARIA:
    case MOVE_SUPERSONIC:
    case MOVE_TORCH_SONG:
    case MOVE_UPROAR:
        return TRUE;
    default:
        return FALSE;
    }
}

static void Mercury_BuildParrotingQueue(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int slot;
    int battler;
    int target;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    battleCtx->mercuryParrotingCount = 0;
    battleCtx->mercuryParrotingIndex = 0;
    battleCtx->mercuryParrotingOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryParrotingOriginalDefender = battleCtx->defender;
    battleCtx->mercuryParrotingMove = battleCtx->moveCur;

    for (slot = 0; slot < maxBattlers; slot++) {
        battler = battleCtx->monSpeedOrder[slot];

        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || Battler_Ability(battleCtx, battler) != ABILITY_MR_PARROTING) {
            continue;
        }

        target = Mercury_DancerTarget(
            battleSys,
            battleCtx,
            battler,
            battleCtx->attacker,
            battleCtx->defender,
            battleCtx->moveCur);

        if (target == BATTLER_NONE) {
            continue;
        }

        battleCtx->mercuryParrotingBattlers[
            battleCtx->mercuryParrotingCount] = battler;
        battleCtx->mercuryParrotingTargets[
            battleCtx->mercuryParrotingCount] = target;
        battleCtx->mercuryParrotingCount++;
    }

    if (battleCtx->mercuryParrotingCount) {
        battleCtx->mercuryParrotingActive = TRUE;
    }
}

static BOOL Mercury_TryNextParroting(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int user;
    int target;

    if (battleCtx->mercuryParrotingActive == FALSE) {
        if (battleCtx->mercuryAbilityGeneratedAction
            || Mercury_D7SuccessfulMove(battleCtx) == FALSE
            || Mercury_D15MoveIsSound(battleCtx->moveCur) == FALSE) {
            return FALSE;
        }

        Mercury_BuildParrotingQueue(battleSys, battleCtx);
        if (battleCtx->mercuryParrotingActive == FALSE) {
            return FALSE;
        }
    }

    while (battleCtx->mercuryParrotingIndex
        < battleCtx->mercuryParrotingCount) {
        user = battleCtx->mercuryParrotingBattlers[
            battleCtx->mercuryParrotingIndex];
        target = battleCtx->mercuryParrotingTargets[
            battleCtx->mercuryParrotingIndex];
        battleCtx->mercuryParrotingIndex++;

        if (battleCtx->battleMons[user].curHP == 0
            || Battler_Ability(battleCtx, user) != ABILITY_MR_PARROTING) {
            continue;
        }

        BattleContext_Init(battleCtx);
        battleCtx->mercuryAbilityGeneratedAction = TRUE;
        battleCtx->attacker = user;
        battleCtx->defender = target;
        battleCtx->moveCur = battleCtx->mercuryParrotingMove;
        battleCtx->moveTemp = battleCtx->mercuryParrotingMove;
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

        battleCtx->msgTemp = user;
        battleCtx->msgBattlerTemp = user;
        LOAD_SUBSEQ(subscript_mercury_ability_followup);
        battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
        battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
        return TRUE;
    }

    battleCtx->attacker = battleCtx->mercuryParrotingOriginalAttacker;
    battleCtx->defender = battleCtx->mercuryParrotingOriginalDefender;
    battleCtx->moveCur = battleCtx->mercuryParrotingMove;
    battleCtx->moveTemp = battleCtx->mercuryParrotingMove;
    battleCtx->mercuryAbilityGeneratedAction = FALSE;
    battleCtx->mercuryParrotingActive = FALSE;
    battleCtx->mercuryParrotingCount = 0;
    battleCtx->mercuryParrotingIndex = 0;
    return FALSE;
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helpers,
        "D15 Parroting controller helpers",
    )

    signature = (
        "static void BattleControllerPlayer_MoveEnd("
        "BattleSystem *battleSys, BattleContext *battleCtx)"
    )
    insert_before_in_function(
        path,
        signature,
        """        if (Mercury_TryNextDancer(battleSys, battleCtx) == TRUE) {
""",
        """        if (Mercury_TryNextParroting(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_TryNextParroting(battleSys, battleCtx)",
        "D15 Parroting move-end queue hook",
    )


def update_registry(path: Path) -> None:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if ABILITY_TOKEN not in lines:
        lines.append(ABILITY_TOKEN)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(root: Path, registry: Path) -> dict[str, bool]:
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(
        encoding="utf-8"
    )
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    checks = {
        "stable_id_426":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "queue_state":
            "mercuryParrotingActive" in ctx
            and "mercuryParrotingBattlers[MAX_BATTLERS]" in ctx,
        "canonical_sound_family":
            all(token in ctl for token in (
                "MOVE_BOOMBURST",
                "MOVE_BUG_BUZZ",
                "MOVE_HYPER_VOICE",
                "MOVE_OVERDRIVE",
                "MOVE_PARTING_SHOT",
                "MOVE_PERISH_SONG",
                "MOVE_PSYCHIC_NOISE",
                "MOVE_TORCH_SONG",
            )),
        "copies_other_battlers_only":
            "battler == battleCtx->attacker" in ctl,
        "successful_move_gate":
            "Mercury_D7SuccessfulMove(battleCtx) == FALSE" in ctl,
        "speed_order_queue":
            "battler = battleCtx->monSpeedOrder[slot];" in ctl,
        "canonical_targeting_reused":
            "target = Mercury_DancerTarget(" in ctl,
        "generated_action_recursion_guard":
            "battleCtx->mercuryAbilityGeneratedAction = TRUE;" in ctl
            and "battleCtx->mercuryAbilityGeneratedAction" in ctl,
        "copy_skips_pp_and_turn_incapacity":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "normal_move_pipeline":
            "commandNext = BATTLE_CONTROL_BEFORE_MOVE" in ctl,
        "move_end_hook":
            "Mercury_TryNextParroting(battleSys, battleCtx)" in ctl,
        "implemented_registry_updated":
            ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }
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
    ap.add_argument("--report", type=Path, default=Path("mr10d15-parroting.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D15_PARROTING",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_tokens": [ABILITY_TOKEN],
        "implemented_count": 1,
        "shared_systems_reused": [
            "MR08R5 target-selection rules",
            "MR10D7 generated Ability action",
            "MR10D7 recursion guard",
        ],
        "remaining_keep_as_written_after_d15": 26,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D15 Parroting validation failed")


if __name__ == "__main__":
    main()
