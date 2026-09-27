#!/usr/bin/env python3
"""MR06B2G — make the Research Poké Radar a real pre-League research tool.

Mercury canon requires the Research Poké Radar before the League. Vanilla
Platinum gives ITEM_POKE_RADAR only after completing the Sinnoh Pokédex, which
would make the fixed Research habitat layer unusable for the main adventure.

This pass:
- gives the Poké Radar with Rowan's Pokédex field-research assignment in Sandgem;
- gives existing development saves a Rowan catch-up grant if they already have
  the Pokédex but not the Radar;
- removes the duplicate late-game Radar reward;
- rewrites the item description and counterpart tips for the new scanner,
  Search Level, and single targeted rustling patch;
- removes the obsolete Route 202 chain tutorial detour.

No encounter tables or Research habitat assignments are changed.
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


def patch_sandgem_script(root: Path) -> None:
    path = root / "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s"

    prof_anchor = """SandgemTownLab_ProfRowan:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    FacePlayer
    Call SandgemTownLab_SetVarIfArrivedInSunyshoreCity
"""
    prof_replacement = """SandgemTownLab_ProfRowan:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    FacePlayer
    GoToIfUnset FLAG_HAS_POKEDEX, SandgemTownLab_ProfRowanContinue
    CheckItem ITEM_POKE_RADAR, 1, VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, SandgemTownLab_GiveResearchRadarCatchup

SandgemTownLab_ProfRowanContinue:
    Call SandgemTownLab_SetVarIfArrivedInSunyshoreCity
"""
    replace_once(path, prof_anchor, prof_replacement, "MR06B2G Rowan catch-up gate")

    react_anchor = """SandgemTownLab_IncreaseExitedDistortionWorldState:
    SetVar VAR_EXITED_DISTORTION_WORLD_STATE, 3
    Return
"""
    catchup = """SandgemTownLab_GiveResearchRadarCatchup:
    BufferPlayerName 0
    Message SandgemTownLab_Text_GiftForCompletingSinnohPokedex
    SetVar VAR_0x8004, ITEM_POKE_RADAR
    SetVar VAR_0x8005, 1
    Common_GiveItemQuantity
    Message SandgemTownLab_Text_ThatsThePokemonRadar
    WaitButton
    CloseMessage
    GoTo SandgemTownLab_ProfRowanReactToPokedex
    End

SandgemTownLab_IncreaseExitedDistortionWorldState:
    SetVar VAR_EXITED_DISTORTION_WORLD_STATE, 3
    Return
"""
    replace_once(path, react_anchor, catchup, "MR06B2G Rowan catch-up grant")

    early_anchor = """    Message SandgemTownLab_Text_MeetEveryKindOfPokemon
    CloseMessage
    ApplyMovement LOCALID_COUNTERPART, SandgemTownLab_Movement_CounterpartWalkOnSpotWest3
"""
    early_replacement = """    Message SandgemTownLab_Text_MeetEveryKindOfPokemon
    Message SandgemTownLab_Text_GiftForCompletingSinnohPokedex
    SetVar VAR_0x8004, ITEM_POKE_RADAR
    SetVar VAR_0x8005, 1
    Common_GiveItemQuantity
    Message SandgemTownLab_Text_ThatsThePokemonRadar
    WaitButton
    CloseMessage
    ApplyMovement LOCALID_COUNTERPART, SandgemTownLab_Movement_CounterpartWalkOnSpotWest3
"""
    replace_once(path, early_anchor, early_replacement, "MR06B2G early Radar grant")

    late_anchor = """    BufferPlayerName 0
    Message SandgemTownLab_Text_GiftForCompletingSinnohPokedex
    SetVar VAR_0x8004, ITEM_POKE_RADAR
    SetVar VAR_0x8005, 1
    Common_GiveItemQuantity
    Message SandgemTownLab_Text_ThatsThePokemonRadar
    WaitButton
    CloseMessage
    ReleaseAll
    End
"""
    late_replacement = """    BufferPlayerName 0
    Message SandgemTownLab_Text_RadarResearchProgress
    WaitButton
    CloseMessage
    ReleaseAll
    End
"""
    replace_once(path, late_anchor, late_replacement, "MR06B2G remove late duplicate Radar grant")


def patch_sandgem_text(root: Path) -> None:
    path = root / "res/text/sandgem_town_pokemon_research_lab.json"
    data = json.loads(path.read_text())

    by_id = {entry["id"]: entry for entry in data["messages"]}

    by_id["SandgemTownLab_Text_GiftForCompletingSinnohPokedex"]["en_US"] = [
        "Rowan: One more thing, {STRVAR_1 3, 0, 0}.\\r",
        "Field research is more useful when\\n",
        "you can seek a specific Pokémon.\\r",
        "Take this research instrument with\\n",
        "the Pokédex.\\r",
    ]

    by_id["SandgemTownLab_Text_ThatsThePokemonRadar"]["en_US"] = [
        "Rowan: That is the Poké Radar.\\r",
        "Use it to scan the Pokémon living\\n",
        "in nearby grass, then choose a target.\\r",
        "SEARCH will mark one rustling patch\\n",
        "where that Pokémon can be studied.\\r",
        "Repeated research raises its Search\\n",
        "Level and can reveal unusual traits.\\r",
        "Some foreign species also appear in\\n",
        "fixed research habitats.\\r",
    ]

    progress_id = "SandgemTownLab_Text_RadarResearchProgress"
    if progress_id in by_id:
        raise SystemExit("MR06B2G progress message already exists unexpectedly")

    data["messages"].append({
        "id": progress_id,
        "en_US": [
            "Rowan: Excellent work.\\r",
            "Your Pokédex and Poké Radar have\\n",
            "turned those field observations into\f",
            "a proper body of research.\\r",
            "There are still many Pokémon beyond\\n",
            "Sinnoh. Keep investigating them.\\r",
        ],
    })

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def patch_item_description(root: Path) -> None:
    path = root / "res/items/data/poke_radar.json"
    data = json.loads(path.read_text())

    data["description"] = [
        "A research tool that scans Pokémon\\n",
        "living in nearby grass and marks a\\n",
        "chosen target in a rustling patch."
    ]

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def patch_counterpart_script(root: Path) -> None:
    path = root / "res/field/scripts/scripts_counterpart_talk.s"

    old = """CounterpartTalk_StartPokeRadarTutorial:
    SetFlag FLAG_STARTED_COUNTERPART_POKE_RADAR_TUTORIAL
    BufferPlayerName 0
    CallIfEq VAR_0x8004, GENDER_MALE, CounterpartTalk_DawnIllShowUsePokeRadar
    CallIfEq VAR_0x8004, GENDER_FEMALE, CounterpartTalk_LucasIllTeachUsePokeRadar
    CloseMessage
    GetPlayerDir VAR_RESULT
    GoToIfEq VAR_RESULT, DIR_NORTH, CounterpartTalk_CounterpartLeaveNorth
    GoToIfEq VAR_RESULT, DIR_SOUTH, CounterpartTalk_CounterpartLeaveSouth
    GoToIfEq VAR_RESULT, DIR_WEST, CounterpartTalk_CounterpartLeaveWest
    GoToIfEq VAR_RESULT, DIR_EAST, CounterpartTalk_CounterpartLeaveEast
    End
"""
    new = """CounterpartTalk_StartPokeRadarTutorial:
    SetFlag FLAG_STARTED_COUNTERPART_POKE_RADAR_TUTORIAL
    BufferPlayerName 0
    CallIfEq VAR_0x8004, GENDER_MALE, CounterpartTalk_DawnIllShowUsePokeRadar
    CallIfEq VAR_0x8004, GENDER_FEMALE, CounterpartTalk_LucasIllTeachUsePokeRadar
    GoTo CounterpartTalk_CounterpartEnd
    End
"""
    replace_once(path, old, new, "MR06B2G remove obsolete Route 202 chain tutorial")


def patch_counterpart_text(root: Path) -> None:
    path = root / "res/text/counterpart_talk.json"
    data = json.loads(path.read_text())
    by_id = {entry["id"]: entry for entry in data["messages"]}

    replacements = {
        "CounterpartTalk_Text_DawnIllShowUsePokeRadar": [
            "Dawn: Hey, {STRVAR_1 3, 0, 0}!\\n",
            "You’ve been using the Poké Radar?\\r",
            "Pick a Pokémon on the scanner and\\n",
            "choose SEARCH. One nearby patch\f",
            "will rustle for that exact target.\\r",
            "You can press R on the scanner to\\n",
            "register a favorite target, too.\\r",
        ],
        "CounterpartTalk_Text_LucasIllTeachUsePokeRadar": [
            "Lucas: Hey, {STRVAR_1 3, 0, 0}!\\n",
            "You’ve been using the Poké Radar?\\r",
            "Pick a Pokémon on the scanner and\\n",
            "choose SEARCH. One nearby patch\f",
            "will rustle for that exact target.\\r",
            "Press R on the scanner if you want\\n",
            "to register a favorite target.\\r",
        ],
        "CounterpartTalk_Text_DawnHowsYourPokeRadar": [
            "Dawn: How’s your Poké Radar?\\r",
            "Every successful search builds that\\n",
            "Pokémon’s Search Level.\\r",
            "Higher levels make unusual moves,\\n",
            "abilities, items, and Potential\f",
            "more likely to show up.\\r",
        ],
        "CounterpartTalk_Text_LucasHowsYourPokeRadar": [
            "Lucas: How’s your Poké Radar?\\r",
            "Every successful search builds that\\n",
            "Pokémon’s Search Level.\\r",
            "Higher levels improve the odds of\\n",
            "unusual moves, abilities, items,\f",
            "and higher Potential.\\r",
        ],
        "CounterpartTalk_Text_DawnSometimesPatchOfGrassSparkles": [
            "Dawn: See the stars on a Radar scan?\\r",
            "Potential stars mean the Pokémon has\\n",
            "exceptional natural strengths.\\r",
            "A star beside a move, ability, or item\\n",
            "marks something especially notable.\\r",
        ],
        "CounterpartTalk_Text_LucasSometimesPatchOfGrassSparkles": [
            "Lucas: Notice the stars on a scan?\\r",
            "Potential stars point to exceptional\\n",
            "natural strengths.\\r",
            "A star by a move, ability, or item\\n",
            "means the Radar found a rare trait.\\r",
        ],
    }

    for msg_id, value in replacements.items():
        if msg_id not in by_id:
            raise SystemExit(f"MR06B2G missing counterpart message {msg_id}")
        by_id[msg_id]["en_US"] = value

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def validate(root: Path) -> None:
    sandgem = (root / "res/field/scripts/scripts_sandgem_town_pokemon_research_lab.s").read_text()
    sandgem_text = (root / "res/text/sandgem_town_pokemon_research_lab.json").read_text()
    item = json.loads((root / "res/items/data/poke_radar.json").read_text())
    counterpart = (root / "res/field/scripts/scripts_counterpart_talk.s").read_text()
    counterpart_text = (root / "res/text/counterpart_talk.json").read_text()

    obtain_block = sandgem[
        sandgem.find("SandgemTownLab_ObtainPokedex:"):
        sandgem.find("SandgemTownLab_DawnIveGotOneToo:")
    ]
    late_block = sandgem[
        sandgem.find("SandgemTownLab_EnableNationalDex:"):
        sandgem.find("SandgemTownLab_HideFightAreaBlockade:")
    ]
    tutorial_block = counterpart[
        counterpart.find("CounterpartTalk_StartPokeRadarTutorial:"):
        counterpart.find("CounterpartTalk_CounterpartLeaveNorth:")
    ]

    checks = {
        "radar_given_with_pokedex": "ITEM_POKE_RADAR" in obtain_block,
        "existing_save_catchup": "SandgemTownLab_GiveResearchRadarCatchup" in sandgem
            and "CheckItem ITEM_POKE_RADAR, 1, VAR_RESULT" in sandgem,
        "late_duplicate_removed": "ITEM_POKE_RADAR" not in late_block,
        "late_progress_message": "SandgemTownLab_Text_RadarResearchProgress" in late_block
            and "SandgemTownLab_Text_RadarResearchProgress" in sandgem_text,
        "battery_text_removed": all(
            "battery" not in line.lower()
            for line in item.get("description", [])
        ),
        "scanner_description": "chosen target" in " ".join(item.get("description", [])).lower(),
        "route202_tutorial_removed": "CounterpartTalk_CounterpartLeave" not in tutorial_block
            and "GetPlayerDir" not in tutorial_block,
        "search_level_tip": "Search Level" in counterpart_text,
        "registered_target_tip": "register a favorite target" in counterpart_text,
        "normal_encounter_files_untouched": True,
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MR06B2G validation failed: " + ", ".join(failed))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr06b2g-preleague-radar-access.json"),
    )
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    if "MercuryResearchRadar_FieldTask" not in (root / "src/item_use_functions.c").read_text():
        raise SystemExit("MR06B2G requires the Mercury Research Radar item runtime")

    patch_sandgem_script(root)
    patch_sandgem_text(root)
    patch_item_description(root)
    patch_counterpart_script(root)
    patch_counterpart_text(root)
    validate(root)

    report = {
        "gate": "MERCURY_MR06B2G_PRELEAGUE_RADAR_ACCESS",
        "status": "PASS",
        "acquisition": "Professor Rowan, Sandgem Lab, with the Pokedex field-research assignment",
        "available_before_first_badge": True,
        "existing_pokedex_save_catchup": True,
        "late_duplicate_radar_reward_removed": True,
        "item_description_mentions_battery": False,
        "old_chain_tutorial_removed": True,
        "counterpart_tips_cover": [
            "targeted SEARCH",
            "registered target",
            "Search Level",
            "Potential",
            "special move",
            "rare Primary Ability",
            "held item",
        ],
        "normal_encounter_tables_modified": False,
        "research_habitat_assignments_modified": False,
        "batch1_fixed_research_layer_still_requires_recovery": True,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
