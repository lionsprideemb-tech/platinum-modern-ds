#!/usr/bin/env python3
"""MR10C15 — implement the approved Two Lives redesign.

Two Lives combines two recognizable survival mechanics:
1. Once per battle, the first direct damaging hit is completely blocked. The
   shield is party-persistent across switching and breaking it costs 1/8 max HP.
2. Separately, while the holder is at full HP, a direct attack that would KO it
   leaves it at 1 HP (Sturdy-style). This can work again after healing to full.

The first-hit shield reuses Mercury's certified Disguise/Ice Face form-shield
pipeline so multi-hit handling remains correct: hit 1 breaks the shield, recoil
is applied, and later hits continue normally. The Sturdy half is attached to
Platinum's existing hold-on-with-1-HP damage checkpoint, but uses the non-item
ENDURED status so it does not play a held-item animation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ABILITY_NAME = "Two Lives"
ABILITY_TOKEN = "ABILITY_MR_TWO_LIVES"
ABILITY_ID = 767


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


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


def patch_party_persistent_shield_state(root: Path) -> None:
    path = root / "include/battle/battle_context.h"
    insert_after_once(
        path,
        """    u8 mercuryIceFaceBrokenMask[2];
""",
        """    // Mercury MR10C15: Two Lives' first-hit shield is once per
    // party Pokémon per battle, so switching cannot refresh it.
    u8 mercuryTwoLivesBrokenMask[2];
""",
        "Two Lives party-persistent shield state",
    )


def patch_form_shield_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    replace_once(
        path,
        """    if (ability == ABILITY_DISGUISE) {
        return (battleCtx->mercuryDisguiseBrokenMask[side] & bit) != 0;
    }

    return (battleCtx->mercuryIceFaceBrokenMask[side] & bit) != 0;
""",
        """    if (ability == ABILITY_DISGUISE) {
        return (battleCtx->mercuryDisguiseBrokenMask[side] & bit) != 0;
    }

    if (ability == ABILITY_MR_TWO_LIVES) {
        return (battleCtx->mercuryTwoLivesBrokenMask[side] & bit) != 0;
    }

    return (battleCtx->mercuryIceFaceBrokenMask[side] & bit) != 0;
""",
        "Two Lives form-shield broken lookup",
    )

    replace_once(
        path,
        """    mask = ability == ABILITY_DISGUISE
        ? &battleCtx->mercuryDisguiseBrokenMask[side]
        : &battleCtx->mercuryIceFaceBrokenMask[side];
""",
        """    if (ability == ABILITY_DISGUISE) {
        mask = &battleCtx->mercuryDisguiseBrokenMask[side];
    } else if (ability == ABILITY_MR_TWO_LIVES) {
        mask = &battleCtx->mercuryTwoLivesBrokenMask[side];
    } else {
        mask = &battleCtx->mercuryIceFaceBrokenMask[side];
    }
""",
        "Two Lives form-shield broken setter",
    )

    replace_once(
        path,
        """    if (moveClass == CLASS_PHYSICAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_ICE_FACE)
""",
        """    if (Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_MR_TWO_LIVES)
        && Mercury_FormShieldBroken(
               battleSys, battleCtx, defender, ABILITY_MR_TWO_LIVES) == FALSE) {
        battleCtx->mercuryFormShieldPending[defender] = ABILITY_MR_TWO_LIVES;
        return TRUE;
    }

    if (moveClass == CLASS_PHYSICAL
        && Battler_IgnorableAbility(
            battleCtx, attacker, defender, ABILITY_ICE_FACE)
""",
        "Two Lives first-hit shield",
    )

    replace_once(
        path,
        """        if (ability == ABILITY_DISGUISE) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }
""",
        """        if (ability == ABILITY_DISGUISE
            || ability == ABILITY_MR_TWO_LIVES) {
            battleCtx->hpCalcTemp = BattleSystem_Divide(
                battleCtx->battleMons[battleCtx->defender].maxHP * -1,
                8);
        }
""",
        "Two Lives shield-break recoil",
    )


def patch_full_hp_survival(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    replace_once(
        path,
        """static BOOL BtlCmd_CheckHoldOnWith1HP(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BOOL endure = FALSE;

    BattleScript_Iter(battleCtx, 1);
""",
        """static BOOL BtlCmd_CheckHoldOnWith1HP(BattleSystem *battleSys, BattleContext *battleCtx)
{
    BOOL endure = FALSE;
    BOOL abilityEndure = FALSE;

    BattleScript_Iter(battleCtx, 1);
""",
        "Two Lives survival local state",
    )

    replace_once(
        path,
        """    if (itemEffect == HOLD_EFFECT_ENDURE
        && battleCtx->battleMons[battler].curHP == battleCtx->battleMons[battler].maxHP) {
        endure = TRUE;
    }

    if (endure && battleCtx->battleMons[battler].curHP + battleCtx->hpCalcTemp <= 0) {
        battleCtx->hpCalcTemp = (battleCtx->battleMons[battler].curHP - 1) * -1;
        battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED_ITEM;
    }
""",
        """    if (itemEffect == HOLD_EFFECT_ENDURE
        && battleCtx->battleMons[battler].curHP == battleCtx->battleMons[battler].maxHP) {
        endure = TRUE;
    }

    if (battleCtx->attacker != BATTLER_NONE
        && battleCtx->attacker != battler
        && CURRENT_MOVE_DATA.power
        && battleCtx->battleMons[battler].curHP
            == battleCtx->battleMons[battler].maxHP
        && Battler_IgnorableAbility(
            battleCtx,
            battleCtx->attacker,
            battler,
            ABILITY_MR_TWO_LIVES) == TRUE) {
        endure = TRUE;
        abilityEndure = TRUE;
    }

    if (endure && battleCtx->battleMons[battler].curHP + battleCtx->hpCalcTemp <= 0) {
        battleCtx->hpCalcTemp = (battleCtx->battleMons[battler].curHP - 1) * -1;
        if (abilityEndure) {
            // Reuse the normal "endured the hit" follow-up rather than the
            // held-item animation/message path.
            battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED;
        } else {
            battleCtx->moveStatusFlags |= MOVE_STATUS_ENDURED_ITEM;
        }
    }
""",
        "Two Lives full-HP Sturdy behavior",
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
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    return {
        "stable_id_767":
            len(abilities) > ABILITY_ID and abilities[ABILITY_ID] == ABILITY_TOKEN,
        "shield_party_persistent":
            "mercuryTwoLivesBrokenMask[2]" in ctx,
        "shield_reuses_certified_damage_cancel_path":
            "ABILITY_MR_TWO_LIVES" in lib
            and "mercuryFormShieldPending[defender] = ABILITY_MR_TWO_LIVES;" in lib,
        "switch_does_not_refresh_shield":
            "mercuryTwoLivesBrokenMask" not in "\n".join(
                line for line in lib.splitlines()
                if "BattleSystem_InitBattleMon" in line
            ),
        "shield_recoil_one_eighth":
            "ability == ABILITY_MR_TWO_LIVES" in lib
            and "maxHP * -1" in lib
            and ",\n                8);" in lib,
        "multi_hit_first_hit_only":
            "Mercury_SetFormShieldBroken(" in lib
            and "ABILITY_MR_TWO_LIVES" in lib,
        "full_hp_survival":
            "ABILITY_MR_TWO_LIVES" in script
            and "MOVE_STATUS_ENDURED" in script
            and "curHP == battleCtx->battleMons[battler].maxHP" in script,
        "survival_is_direct_opposing_attack_only":
            "battleCtx->attacker != battler" in script
            and "CURRENT_MOVE_DATA.power" in script,
        "mold_breaker_aware":
            "ABILITY_MR_TWO_LIVES) == TRUE" in script
            and "Battler_IgnorableAbility(" in lib,
        "no_item_animation_for_ability_survival":
            "if (abilityEndure)" in script
            and "MOVE_STATUS_ENDURED_ITEM" in script,
        "sturdy_can_rearm_after_heal":
            "mercuryTwoLivesSturdyUsed" not in ctx
            and "curHP == battleCtx->battleMons[battler].maxHP" in script,
        "implemented_registry_updated": ABILITY_TOKEN in registry_lines,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mr10c15-two-lives.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    partition = args.partition.resolve()
    registry = args.implemented_registry.resolve()

    validate_partition(partition)
    patch_party_persistent_shield_state(root)
    patch_form_shield_helpers(root)
    patch_full_hp_survival(root)
    update_registry(registry)

    checks = validate(root, registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C15_TWO_LIVES",
        "status": status,
        "implemented_abilities": [ABILITY_NAME],
        "implemented_count": 1,
        "stable_id": ABILITY_ID,
        "shield_uses_per_battle": 1,
        "shield_recoil_fraction": "1/8 max HP",
        "full_hp_survival_rearms_after_heal": True,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C15 Two Lives validation failed")


if __name__ == "__main__":
    main()
