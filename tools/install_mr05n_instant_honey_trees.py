#!/usr/bin/env python3
"""MR05N — install Mercury's approved instant Honey Tree runtime.

Locked Mercury rule:
- spend exactly 1 Honey;
- immediately trigger the Honey Tree encounter in the same interaction;
- no six-hour real-world wait;
- no post-battle cooldown;
- the same tree may be used again immediately with another Honey;
- no trainer-ID special-tree lottery;
- no failed Honey roll;
- every tree can reach Common / Uncommon / Rare premium pools.

This phase changes Honey Tree behavior only. The already-authored premium species
pool stays untouched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def patch_honey_runtime(root: Path) -> None:
    path = root / "src/overlay005/honey_tree.c"

    old_slather = """void HoneyTree_SlatherTree(FieldSystem *fieldSystem)
{
    u8 treeId = GetTreeIDFromMapHeaderID(fieldSystem->location->mapHeaderID);
    GF_ASSERT(treeId != NUM_HONEY_TREES);

    PlayerHoneyTreeStates *treeDat = SpecialEncounter_GetPlayerHoneyTreeStates(SaveData_GetSpecialEncounters(fieldSystem->saveData));
    HoneyTree *tree = SpecialEncounter_GetHoneyTree(treeId, treeDat);

    tree->minutesRemaining = (24 * 60); // slathering lasts for one day

    TrainerInfo *trainer = SaveData_GetTrainerInfo(fieldSystem->saveData);
    BOOL munchlaxTree = IsMunchlaxTree(TrainerInfo_ID(trainer), treeId);

    // Slathering the same tree twice in succession has a 90% chance to give the same group again.
    if (SpecialEncounter_GetLastSlatheredTreeId(treeDat) == treeId) {
        if ((LCRNG_RandMod(100)) < 90) {
            GetTreeEncounterSlot(&tree->encounterSlot);
            tree->numShakes = GetShakesFromGroup(tree->encounterGroup);
            return;
        }
    }

    GetTreeEncounterGroup(munchlaxTree, &tree->encounterGroup);

    if (tree->encounterGroup != TREE_GROUP_NO_ENCOUNTER) {
        GetTreeEncounterSlot(&tree->encounterSlot);

        tree->encounterTableIndex = GetEncounterTableFromGroup(tree->encounterGroup);
    } else {
        tree->encounterTableIndex = 0;
        tree->encounterSlot = 0;
        tree->minutesRemaining = 0;
    }

    tree->numShakes = GetShakesFromGroup(tree->encounterGroup);

    SpecialEncounter_SetLastSlatheredTreeId(treeId, treeDat);
}
"""
    new_slather = """void HoneyTree_SlatherTree(FieldSystem *fieldSystem)
{
    u8 treeId = GetTreeIDFromMapHeaderID(fieldSystem->location->mapHeaderID);
    GF_ASSERT(treeId != NUM_HONEY_TREES);

    PlayerHoneyTreeStates *treeDat = SpecialEncounter_GetPlayerHoneyTreeStates(SaveData_GetSpecialEncounters(fieldSystem->saveData));
    HoneyTree *tree = SpecialEncounter_GetHoneyTree(treeId, treeDat);

    // Mercury: freshly applied Honey is encounter-ready immediately.
    // Vanilla considers <=18 hours remaining to be an encounter-ready tree.
    tree->minutesRemaining = (18 * 60);

    // Mercury removes the trainer-ID special-tree lottery and repeat-group
    // carryover. Every tree gets a fresh premium tier + slot roll.
    GetTreeEncounterGroup(FALSE, &tree->encounterGroup);
    GetTreeEncounterSlot(&tree->encounterSlot);
    tree->encounterTableIndex = GetEncounterTableFromGroup(tree->encounterGroup);
    tree->numShakes = GetShakesFromGroup(tree->encounterGroup);

    SpecialEncounter_SetLastSlatheredTreeId(treeId, treeDat);
}
"""
    replace_once(path, old_slather, new_slather, "MR05N HoneyTree_SlatherTree")

    old_group = """static void GetTreeEncounterGroup(const BOOL isMunchlaxTree, u8 *group)
{
    int roll = LCRNG_RandMod(100);

    if (isMunchlaxTree) {
        if (roll < 1) {
            *group = TREE_GROUP_C;
        } else if (roll < 10) {
            *group = TREE_GROUP_NO_ENCOUNTER;
        } else if (roll < 30) {
            *group = TREE_GROUP_A;
        } else {
            *group = TREE_GROUP_B;
        }
    } else {
        if (roll < 10) {
            *group = TREE_GROUP_NO_ENCOUNTER;
        } else if (roll < 30) {
            *group = TREE_GROUP_B;
        } else {
            *group = TREE_GROUP_A;
        }
    }
}
"""
    new_group = """static void GetTreeEncounterGroup(const BOOL isMunchlaxTree, u8 *group)
{
    (void)isMunchlaxTree;

    // Keep the familiar normal-tree shape, but Mercury converts vanilla's
    // 10% failure into the Rare premium tier: 70% / 20% / 10%.
    int roll = LCRNG_RandMod(100);

    if (roll < 10) {
        *group = TREE_GROUP_C;
    } else if (roll < 30) {
        *group = TREE_GROUP_B;
    } else {
        *group = TREE_GROUP_A;
    }
}
"""
    replace_once(path, old_group, new_group, "MR05N Honey Tree group roll")


def patch_honey_script(root: Path) -> None:
    path = root / "res/field/scripts/scripts_common.s"
    old = """CommonScript_SlatherHoneyTree:
    RemoveItem ITEM_HONEY, 1, VAR_RESULT
    IncrementTrainerScore2 TRAINER_SCORE_EVENT_HONEY_USED
    SlatherHoneyTree
    WaitTime 10, VAR_RESULT
    Message CommonStrings_Text_BarkWasSlathered
    WaitButton
    CloseMessage
    ReleaseAll
    End
"""
    new = """CommonScript_SlatherHoneyTree:
    RemoveItem ITEM_HONEY, 1, VAR_RESULT
    IncrementTrainerScore2 TRAINER_SCORE_EVENT_HONEY_USED
    SlatherHoneyTree
    WaitTime 10, VAR_RESULT
    Message CommonStrings_Text_BarkWasSlathered
    WaitButton
    CloseMessage
    GoTo CommonScript_HoneyTreeEncounter
"""
    replace_once(path, old, new, "MR05N immediate Honey Tree battle")


def validate(root: Path) -> None:
    runtime_path = root / "src/overlay005/honey_tree.c"
    script_path = root / "res/field/scripts/scripts_common.s"
    runtime = runtime_path.read_text()
    scripts = script_path.read_text()

    slather_start = runtime.index("void HoneyTree_SlatherTree(FieldSystem *fieldSystem)")
    slather_end = runtime.index("\n}\n", slather_start) + 3
    slather = runtime[slather_start:slather_end]

    if "tree->minutesRemaining = (18 * 60);" not in slather:
        raise SystemExit("MR05N immediate encounter-ready timer missing")
    if "IsMunchlaxTree" in slather or "TrainerInfo_ID" in slather:
        raise SystemExit("MR05N special-tree lottery still participates in slather flow")
    if "SpecialEncounter_GetLastSlatheredTreeId" in slather:
        raise SystemExit("MR05N repeat-group carryover still participates in slather flow")

    group_start = runtime.rindex("static void GetTreeEncounterGroup")
    group_end = runtime.index("\n}\n", group_start) + 3
    group = runtime[group_start:group_end]
    if "TREE_GROUP_NO_ENCOUNTER" in group:
        raise SystemExit("MR05N group roll still contains a failed-Honey outcome")
    for fragment in ("roll < 10", "TREE_GROUP_C", "roll < 30", "TREE_GROUP_B", "TREE_GROUP_A"):
        if fragment not in group:
            raise SystemExit(f"MR05N premium tier roll missing {fragment!r}")

    block_start = scripts.index("CommonScript_SlatherHoneyTree:")
    block_end = scripts.index("\nCommonScript_HoneyTreeEncounter:", block_start)
    block = scripts[block_start:block_end]
    if "GoTo CommonScript_HoneyTreeEncounter" not in block:
        raise SystemExit("MR05N slather flow does not immediately enter battle")
    if "ReleaseAll" in block:
        raise SystemExit("MR05N slather flow still exits before the battle")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05n-instant-honey-trees.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_honey_runtime(root)
    patch_honey_script(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR05N_INSTANT_HONEY_TREES",
        "status": "PASS",
        "honey_consumed_per_encounter": 1,
        "instant_battle_after_slather": True,
        "six_hour_wait_required": False,
        "cooldown_after_battle": False,
        "same_tree_can_repeat_immediately": True,
        "special_tree_lottery": False,
        "failed_honey_roll": False,
        "tier_distribution_percent": {
            "common": 70,
            "uncommon": 20,
            "rare": 10
        },
        "slot_distribution_within_tier_percent": [40, 20, 20, 10, 5, 5],
        "species_pool_changed_by_this_phase": False
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
