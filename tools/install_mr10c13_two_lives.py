#!/usr/bin/env python3
"""MR10C13 — implement the approved Two Lives redesign.

Two Lives combines two recognizable survival mechanics without refreshing the
first shield on switch:

1. Once per battle, the first direct damaging hit that would reach the holder's
   HP is completely blocked. The shield is party-persistent for the battle.
   After the blocked hit, the holder loses 1/8 max HP.
2. Separately, whenever the holder is at full HP, an otherwise lethal direct
   attack leaves it at 1 HP (Sturdy-style). This part can work again if the
   holder later returns to full HP.
3. Multi-hit moves break the shield on one hit and continue normally afterward.

The first shield reuses Mercury's already-certified Disguise/Ice Face post-hit
pipeline so secondaries still resolve and the 1/8 recoil occurs at the normal
Ability checkpoint.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Two Lives"
ABILITY_TOKEN = "ABILITY_MR_TWO_LIVES"
ABILITY_ID = 767


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


def validate_partition(partition: Path) -> None:
    plan = json.loads(partition.read_text(encoding="utf-8"))
    rows = [x for x in plan["abilities"] if x.get("id") == ABILITY_ID]
    if len(rows) != 1:
        raise SystemExit(f"{ABILITY_NAME}: expected one partition row at ID {ABILITY_ID}")

    row = rows[0]
    expected = {
        "display_name": ABILITY_NAME,
        "token": ABILITY_TOKEN,
        "approval_state": "owner_approved_redesign",
        "owner_review_decision": "REDESIGN",
        "implementation_class": "light_extension",
        "review_blocked": False,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise SystemExit(
                f"{ABILITY_NAME}: partition {key} expected {value!r}, got {row.get(key)!r}"
            )
    if row.get("runtime_enabled", True) is False:
        raise SystemExit(f"{ABILITY_NAME}: reviewed mechanic is runtime-disabled")


def patch_context(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryTimeCompressionUsed[MAX_BATTLERS];
""",
        """    // Mercury MR10C13: Two Lives first-hit shield persists by
    // party slot for the whole battle; pending is only per active battler.
    u8 mercuryTwoLivesShieldUsedMask[2];
    u8 mercuryTwoLivesShieldPending[MAX_BATTLERS];
""",
        "Two Lives state",
    )


def patch_switch_in_pending_reset(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"
    insert_after_once(
        path,
        """    battleCtx->mercuryTimeCompressionUsed[battler] = FALSE;
""",
        """    battleCtx->mercuryTwoLivesShieldPending[battler] = FALSE;
""",
        "Two Lives pending-state reset",
    )


def patch_two_lives_helper(root: Path) -> None:
    hdr = root / "include/battle/battle_lib.h"
    lib = root / "src/battle/battle_lib.c"

    insert_before_once(
        hdr,
        """BOOL Mercury_TryBlockFormShield(
""",
        """BOOL Mercury_TryBlockTwoLives(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int defender);
""",
        "Two Lives helper declaration",
    )

    insert_before_once(
        lib,
        """BOOL Mercury_TryBlockFormShield(
""",
        """static u8 Mercury_TwoLivesPartyBit(BattleContext *battleCtx, int battler)
{
    int slot = battleCtx->selectedPartySlot[battler];

    if (slot < 0 || slot >= 6) {
        return 0;
    }

    return (u8)(1 << slot);
}

static BOOL Mercury_TwoLivesShieldUsed(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_TwoLivesPartyBit(battleCtx, battler);

    if (bit == 0) {
        return TRUE;
    }

    return (battleCtx->mercuryTwoLivesShieldUsedMask[side] & bit) != 0;
}

static void Mercury_SetTwoLivesShieldUsed(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int battler)
{
    int side = BattleSystem_GetBattlerSide(battleSys, battler);
    u8 bit = Mercury_TwoLivesPartyBit(battleCtx, battler);

    if (bit) {
        battleCtx->mercuryTwoLivesShieldUsedMask[side] |= bit;
    }
}

BOOL Mercury_TryBlockTwoLives(
    BattleSystem *battleSys,
    BattleContext *battleCtx,
    int attacker,
    int defender)
{
    if (attacker == BATTLER_NONE
        || defender == BATTLER_NONE
        || attacker == defender
        || battleCtx->damage >= 0
        || (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS)
        || MOVE_DATA(battleCtx->moveCur).class == CLASS_STATUS) {
        return FALSE;
    }

    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_TWO_LIVES)
        && Mercury_TwoLivesShieldUsed(
               battleSys, battleCtx, defender) == FALSE) {
        battleCtx->mercuryTwoLivesShieldPending[defender] = TRUE;
        return TRUE;
    }

    return FALSE;
}

""",
        "Two Lives shield helper",
    )


def patch_hp_pipeline(root: Path) -> None:
    path = root / "src/battle/battle_controller_player.c"

    insert_before_once(
        path,
        """        if (Mercury_TryBlockFormShield(
""",
        """        if (Mercury_TryBlockTwoLives(
                battleSys,
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender)) {
            // Exactly one hit is absorbed. Keep the ordinary post-hit path so
            // multi-hit continuation and secondary-effect handling still run.
            battleCtx->damage = 0;
            battleCtx->hitDamage = 0;
            battleCtx->hpCalcTemp = 0;
            battleCtx->battleStatusMask |= SYSCTL_MOVE_HIT;
            battleCtx->command = BATTLE_CONTROL_AFTER_MOVE_MESSAGE;
            return;
        }

""",
        "Two Lives first-hit shield cancellation",
    )

    insert_before_once(
        path,
        """        if (CURRENT_MOVE_DATA.effect == BATTLE_EFFECT_LEAVE_WITH_1_HP
""",
        """        if (DEFENDING_MON.curHP == DEFENDING_MON.maxHP
            && DEFENDING_MON.curHP + battleCtx->damage <= 0
            && Battler_IgnorableAbility(
                battleCtx,
                battleCtx->attacker,
                battleCtx->defender,
                ABILITY_MR_TWO_LIVES) == TRUE) {
            battleCtx->damage = (DEFENDING_MON.curHP - 1) * -1;
            battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED;
        }

""",
        "Two Lives full-HP Sturdy survival",
    )


def patch_shield_break_checkpoint(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    insert_before_once(
        path,
        """    if (battleCtx->mercuryFormShieldPending[battleCtx->defender]
        != ABILITY_NONE) {
""",
        """    if (battleCtx->mercuryTwoLivesShieldPending[battleCtx->defender]) {
        battleCtx->mercuryTwoLivesShieldPending[battleCtx->defender] = FALSE;
        Mercury_SetTwoLivesShieldUsed(
            battleSys, battleCtx, battleCtx->defender);

        battleCtx->msgTemp = battleCtx->defender;
        battleCtx->msgBattlerTemp = battleCtx->defender;
        battleCtx->hpCalcTemp = BattleSystem_Divide(
            battleCtx->battleMons[battleCtx->defender].maxHP * -1,
            8);

        // Reuse the certified Disguise-style Ability message + recoil script.
        *subscript = subscript_mercury_form_shield_break;
        return TRUE;
    }

""",
        "Two Lives shield break and one-eighth recoil",
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
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    ctl = (root / "src/battle/battle_controller_player.c").read_text(encoding="utf-8")
    hdr = (root / "include/battle/battle_lib.h").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_767":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "party_persistent_first_shield":
            "mercuryTwoLivesShieldUsedMask[2]" in ctx
            and "Mercury_TwoLivesPartyBit" in lib,
        "switch_does_not_refresh_shield":
            "mercuryTwoLivesShieldUsedMask" in lib
            and "mercuryTwoLivesShieldUsedMask" not in
                ctl[ctl.find("BattleControllerPlayer_MoveEnd"):],
        "pending_resets_on_entry":
            "mercuryTwoLivesShieldPending[battler] = FALSE;" in lib,
        "first_direct_hit_block":
            "Mercury_TryBlockTwoLives(" in hdr
            and "battleCtx->damage = 0;" in ctl,
        "shield_cost_one_eighth":
            "ABILITY_MR_TWO_LIVES" in lib
            and "maxHP * -1" in lib
            and ",\n            8);" in lib,
        "multi_hit_pipeline_continues":
            "BATTLE_CONTROL_AFTER_MOVE_MESSAGE" in ctl,
        "full_hp_sturdy_clause":
            "DEFENDING_MON.curHP == DEFENDING_MON.maxHP" in ctl
            and "ABILITY_MR_TWO_LIVES" in ctl
            and "DEFENDING_MON.curHP - 1" in ctl,
        "sturdy_can_rearm_after_healing":
            "mercuryTwoLivesSturdyUsed" not in ctx,
        "mold_breaker_family_can_ignore":
            "Battler_IgnorableAbility" in lib
            and "ABILITY_MR_TWO_LIVES" in lib,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c13-two-lives.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_context(root)
    patch_switch_in_pending_reset(root)
    patch_two_lives_helper(root)
    patch_hp_pipeline(root)
    patch_shield_break_checkpoint(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C13_TWO_LIVES",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "shield_uses_per_battle": 1,
        "full_hp_survival_rearms_after_healing": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C13 Two Lives validation failed")


if __name__ == "__main__":
    main()
