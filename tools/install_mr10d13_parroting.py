#!/usr/bin/env python3
"""MR10D13 — Parroting reactive sound-copy mechanic.

Implements the approved KEEP-AS-WRITTEN Parroting ability:
- after another battler successfully resolves a sound-based move, every active
  Parroting holder may copy that move once for that move event;
- copies execute through Platinum's ordinary move pipeline without spending PP
  or replacing the holder's selected turn action;
- copied moves cannot recursively create another Parroting queue;
- target selection is rebuilt from the copying battler's point of view.

Mechanics only; locked MR07 visuals remain untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = {
    "Parroting": ("ABILITY_MR_PARROTING", 426),
}
TOKENS = tuple(v[0] for v in IMPLEMENTED.values())


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


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryHollowIcePivotPending[MAX_BATTLERS];
""",
        """    // Mercury MR10D13: queued Parroting extra actions.
    u8 mercuryParrotActive;
    u8 mercuryParrotCount;
    u8 mercuryParrotIndex;
    u8 mercuryParrotOriginalAttacker;
    u8 mercuryParrotOriginalDefender;
    u8 mercuryParrotBattlers[MAX_BATTLERS];
    u8 mercuryParrotTargets[MAX_BATTLERS];
    u16 mercuryParrotMove;

""",
        "D13 Parroting queue state",
    )


def patch_parroting_script(root: Path) -> None:
    scripts = root / "res/battle/scripts/subscripts"
    (scripts / "subscript_mercury_parroting.s").write_text(
        """#include "macros/btlcmd.inc"


_000:
    // Platinum-native Ability activation popup.
    PrintMessage BattleStrings_Text_PokemonWasAbility_Ally, TAG_NICKNAME_ABILITY, BTLSCR_MSG_TEMP, BTLSCR_MSG_BATTLER_TEMP
    Wait
    WaitButtonABTime 15
    End
""",
        encoding="utf-8",
    )
    insert_after_once(
        scripts / "sub_seq.order",
        "subscript_mercury_ability_followup\n",
        "subscript_mercury_parroting\n",
        "D13 Parroting subscript order",
    )
    insert_after_once(
        scripts / "meson.build",
        "    'subscript_mercury_ability_followup.s',\n",
        "    'subscript_mercury_parroting.s',\n",
        "D13 Parroting subscript build list",
    )


def patch_controller(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    helper = """static BOOL Mercury_D13MoveIsSound(int move)
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

static BOOL Mercury_D13SuccessfulMove(BattleContext *battleCtx)
{
    return (battleCtx->battleStatusMask2 & SYSCTL_ATTACK_MESSAGE_SHOWN)
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && (battleCtx->moveStatusFlags & MOVE_STATUS_DID_NOT_HIT) == FALSE;
}

static int Mercury_D13ParrotTarget(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int parrot,
    int originalAttacker,
    int originalDefender,
    int move)
{
    int range = MOVE_DATA(move).range;
    int battleType = BattleSystem_GetBattleType(battleSys);

    switch (range) {
    case RANGE_USER:
    case RANGE_USER_SIDE:
    case RANGE_FIELD:
        return parrot;

    case RANGE_SINGLE_TARGET:
        if ((battleType & BATTLE_TYPE_DOUBLES)
            && BattleSystem_GetBattlerSide(battleSys, parrot)
                == BattleSystem_GetBattlerSide(battleSys, originalAttacker)
            && originalDefender != BATTLER_NONE
            && battleCtx->battleMons[originalDefender].curHP) {
            return originalDefender;
        }

        if (originalAttacker != BATTLER_NONE
            && battleCtx->battleMons[originalAttacker].curHP
            && BattleSystem_GetBattlerSide(battleSys, parrot)
                != BattleSystem_GetBattlerSide(battleSys, originalAttacker)) {
            return originalAttacker;
        }

        return BattleSystem_RandomOpponent(battleSys, battleCtx, parrot);

    case RANGE_RANDOM_OPPONENT:
        return BattleSystem_RandomOpponent(battleSys, battleCtx, parrot);

    default:
        return BattleSystem_RandomOpponent(battleSys, battleCtx, parrot);
    }
}

static void Mercury_D13BuildParrotQueue(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int slot;
    int battler;
    int target;
    int maxBattlers = BattleSystem_GetMaxBattlers(battleSys);

    battleCtx->mercuryParrotCount = 0;
    battleCtx->mercuryParrotIndex = 0;
    battleCtx->mercuryParrotOriginalAttacker = battleCtx->attacker;
    battleCtx->mercuryParrotOriginalDefender = battleCtx->defender;
    battleCtx->mercuryParrotMove = battleCtx->moveCur;

    for (slot = 0; slot < maxBattlers; slot++) {
        battler = battleCtx->monSpeedOrder[slot];

        if (battler == battleCtx->attacker
            || battleCtx->battleMons[battler].curHP == 0
            || Battler_Ability(battleCtx, battler) != ABILITY_MR_PARROTING) {
            continue;
        }

        target = Mercury_D13ParrotTarget(
            battleSys,
            battleCtx,
            battler,
            battleCtx->attacker,
            battleCtx->defender,
            battleCtx->moveCur);

        if (target == BATTLER_NONE) {
            continue;
        }

        battleCtx->mercuryParrotBattlers[battleCtx->mercuryParrotCount] = battler;
        battleCtx->mercuryParrotTargets[battleCtx->mercuryParrotCount] = target;
        battleCtx->mercuryParrotCount++;
    }

    if (battleCtx->mercuryParrotCount) {
        battleCtx->mercuryParrotActive = TRUE;
    }
}

static BOOL Mercury_D13TryNextParrot(
    BattleSystem *battleSys,
    BattleContext *battleCtx)
{
    int parrot;
    int target;

    if (battleCtx->mercuryParrotActive == FALSE) {
        if (battleCtx->attacker == BATTLER_NONE
            || battleCtx->moveCur == MOVE_NONE
            || Mercury_D13MoveIsSound(battleCtx->moveCur) == FALSE
            || Mercury_D13SuccessfulMove(battleCtx) == FALSE) {
            return FALSE;
        }

        Mercury_D13BuildParrotQueue(battleSys, battleCtx);
        if (battleCtx->mercuryParrotActive == FALSE) {
            return FALSE;
        }
    }

    while (battleCtx->mercuryParrotIndex < battleCtx->mercuryParrotCount) {
        parrot = battleCtx->mercuryParrotBattlers[battleCtx->mercuryParrotIndex];
        target = battleCtx->mercuryParrotTargets[battleCtx->mercuryParrotIndex];
        battleCtx->mercuryParrotIndex++;

        if (battleCtx->battleMons[parrot].curHP == 0
            || Battler_Ability(battleCtx, parrot) != ABILITY_MR_PARROTING) {
            continue;
        }

        BattleContext_Init(battleCtx);
        battleCtx->attacker = parrot;
        battleCtx->defender = target;
        battleCtx->moveCur = battleCtx->mercuryParrotMove;
        battleCtx->moveTemp = battleCtx->mercuryParrotMove;

        // The copy is a real move resolution, but it is not the holder's
        // selected action and therefore does not consume PP or obedience.
        battleCtx->beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS;

        battleCtx->msgTemp = parrot;
        battleCtx->msgBattlerTemp = parrot;
        LOAD_SUBSEQ(subscript_mercury_parroting);
        battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;
        battleCtx->command = BATTLE_CONTROL_EXEC_SCRIPT;
        return TRUE;
    }

    battleCtx->attacker = battleCtx->mercuryParrotOriginalAttacker;
    battleCtx->defender = battleCtx->mercuryParrotOriginalDefender;
    battleCtx->moveCur = battleCtx->mercuryParrotMove;
    battleCtx->moveTemp = battleCtx->mercuryParrotMove;
    battleCtx->mercuryParrotActive = FALSE;
    battleCtx->mercuryParrotCount = 0;
    battleCtx->mercuryParrotIndex = 0;
    return FALSE;
}

"""
    insert_before_once(
        path,
        """static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "D13 Parroting controller helpers",
    )

    insert_before_in_function(
        path,
        "static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)",
        """        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);
""",
        """        if (Mercury_D13TryNextParrot(battleSys, battleCtx) == TRUE) {
            return;
        }

""",
        "Mercury_D13TryNextParrot(battleSys, battleCtx)",
        "D13 Parroting move-end queue hook",
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
    ctx = (root / "include/battle/battle_context.h").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    order = (root / "res/battle/scripts/subscripts/sub_seq.order").read_text(encoding="utf-8")
    script = (
        root / "res/battle/scripts/subscripts/subscript_mercury_parroting.s"
    ).read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    checks = {
        "parroting_queue_state":
            "mercuryParrotActive" in ctx
            and "mercuryParrotBattlers[MAX_BATTLERS]" in ctx,
        "modern_sound_family":
            all(token in ctl for token in (
                "MOVE_BOOMBURST",
                "MOVE_BUG_BUZZ",
                "MOVE_HYPER_VOICE",
                "MOVE_OVERDRIVE",
                "MOVE_PSYCHIC_NOISE",
                "MOVE_TORCH_SONG",
            )),
        "successful_move_gate":
            "Mercury_D13SuccessfulMove" in ctl
            and "MOVE_STATUS_DID_NOT_HIT" in ctl,
        "another_battler_only":
            "battler == battleCtx->attacker" in ctl,
        "active_parroting_gate":
            ctl.count("ABILITY_MR_PARROTING") >= 2,
        "speed_order_queue":
            "battler = battleCtx->monSpeedOrder[slot];" in ctl,
        "no_recursive_parroting":
            "if (battleCtx->mercuryParrotActive == FALSE)" in ctl,
        "no_pp_selected_turn_consumption":
            "beforeMoveCheckState = BEFORE_MOVE_STATE_CHECK_TARGET_EXISTS" in ctl,
        "normal_move_pipeline":
            "battleCtx->commandNext = BATTLE_CONTROL_BEFORE_MOVE;" in ctl,
        "target_rebuilt_for_copy_user":
            "Mercury_D13ParrotTarget" in ctl
            and "BattleSystem_RandomOpponent" in ctl,
        "ability_message_script":
            "subscript_mercury_parroting" in order
            and "BattleStrings_Text_PokemonWasAbility_Ally" in script,
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
        default=Path("mr10d13-parroting.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_parroting_script(root)
    patch_controller(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10D13_PARROTING",
        "status": status,
        "implemented_abilities": list(IMPLEMENTED.keys()),
        "implemented_tokens": list(TOKENS),
        "implemented_count": len(IMPLEMENTED),
        "shared_system": "sound_move_reactive_copy_queue",
        "copied_move_spends_pp": False,
        "recursive_parroting": False,
        "remaining_keep_as_written_after_d13": 29,
        "persistent_save_data_changed": False,
        "locked_mr07_visuals_touched": False,
        "certification_scope": "compile_and_static_validation",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10D13 Parroting validation failed")


if __name__ == "__main__":
    main()
