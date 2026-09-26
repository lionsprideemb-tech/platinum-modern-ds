#!/usr/bin/env python3
"""MR05C — make Platinum's Regi loop available before the League.

This installer keeps the original Platinum ruin rooms, seven-dot puzzles,
legendary battle scripts, and Level-1 Regigigas gimmick, but removes the
Hall-of-Fame / National-Dex / fateful-event-Regigigas circular gate.

Mercury flow implemented here:
1. Icicle Badge allows Snowpoint Temple entry.
2. Dormant Regigigas is visible in B5F before the League.
3. First interaction with Regigigas sets a persistent Titan Tablet story flag.
4. That flag enables the real Iron Ruins and Iceberg Ruins entrances.
5. Rock Peak Ruins is relocated to the Route 214 Ruin Maniac Tunnel through
   the existing Ruin Maniac NPC so Route 228 does not need to open early.
6. Regirock / Regice / Registeel battle at Lv55 and remain retryable on
   leave/re-entry until captured.
7. Regigigas remains Lv1 and still requires all three Titans in the party.

FLAG_UNUSED_0x0163 is intentionally used as an internal story-state slot and
aliased locally as FLAG_MERCURY_TITAN_TABLET. This avoids expanding the save
flag layout while keeping the player-facing concept independent from the old
external-event Regigigas requirement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TITAN_ALIAS = "#define FLAG_MERCURY_TITAN_TABLET FLAG_UNUSED_0x0163\n"

RUIN_FILES = {
    "iron": "res/field/scripts/scripts_iron_ruins.s",
    "iceberg": "res/field/scripts/scripts_iceberg_ruins.s",
    "rock_peak": "res/field/scripts/scripts_rock_peak_ruins.s",
}


def replace_once(text: str, old: str, new: str, where: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{where}: expected exactly one replacement anchor, found {count}")
    return text.replace(old, new, 1)


def replace_n(text: str, old: str, new: str, expected: int, where: str) -> str:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{where}: expected {expected} replacement anchors, found {count}")
    return text.replace(old, new)


def insert_titan_alias(text: str, where: str) -> str:
    if "FLAG_MERCURY_TITAN_TABLET" in text:
        return text
    anchor = '#include "macros/scrcmd.inc"\n'
    if anchor not in text:
        raise SystemExit(f"{where}: scrcmd include anchor missing")
    return text.replace(anchor, anchor + TITAN_ALIAS, 1)


def patch_snowpoint_city(root: Path) -> None:
    path = root / "res/field/scripts/scripts_snowpoint_city.s"
    text = path.read_text()

    text = replace_once(
        text,
        """SnowpointCity_OnTransition:
    GoToIfGe VAR_SNOWPOINT_CITY_STATE, 1, SnowpointCity_HideCandice
    End
""",
        """SnowpointCity_OnTransition:
    CheckBadgeAcquired BADGE_ID_ICICLE, VAR_MAP_LOCAL_0x00
    CallIfEq VAR_MAP_LOCAL_0x00, TRUE, SnowpointCity_EnablePreLeagueTemple
    GoToIfGe VAR_SNOWPOINT_CITY_STATE, 1, SnowpointCity_HideCandice
    End

SnowpointCity_EnablePreLeagueTemple:
    ClearFlag FLAG_HIDE_SNOWPOINT_TEMPLE_B5F_REGIGIGAS
    Return
""",
        str(path),
    )

    text = replace_once(
        text,
        """    GetNationalDexEnabled VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, SnowpointCity_CheckAllowEnterTemple
    GoTo SnowpointCity_TempleGuardBlockPlayer
""",
        """    CheckBadgeAcquired BADGE_ID_ICICLE, VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, SnowpointCity_CheckAllowEnterTemple
    GoTo SnowpointCity_TempleGuardBlockPlayer
""",
        str(path) + " coord gate",
    )

    text = replace_once(
        text,
        """SnowpointCity_CheckAllowEnterTemple:
    GoToIfUnset FLAG_GAME_COMPLETED, SnowpointCity_TempleGuardBlockPlayer
    GoTo SnowpointCity_CallAllowEnterTemple
""",
        """SnowpointCity_CheckAllowEnterTemple:
    GoTo SnowpointCity_CallAllowEnterTemple
""",
        str(path) + " completion gate",
    )

    text = replace_once(
        text,
        """    GetNationalDexEnabled VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, SnowpointCity_TempleGuardNationalDex
    GoTo SnowpointCity_MayNotEnterTemple
""",
        """    CheckBadgeAcquired BADGE_ID_ICICLE, VAR_RESULT
    GoToIfEq VAR_RESULT, TRUE, SnowpointCity_TempleGuardNationalDex
    GoTo SnowpointCity_MayNotEnterTemple
""",
        str(path) + " guard gate",
    )

    text = replace_once(
        text,
        """SnowpointCity_TempleGuardNationalDex:
    GoToIfUnset FLAG_GAME_COMPLETED, SnowpointCity_MayNotEnterTemple
    GoToIfEq VAR_SNOWPOINT_CITY_STATE, 0, SnowpointCity_OnlyChosenMayEnterTemple
""",
        """SnowpointCity_TempleGuardNationalDex:
    GoToIfEq VAR_SNOWPOINT_CITY_STATE, 0, SnowpointCity_OnlyChosenMayEnterTemple
""",
        str(path) + " guard completion",
    )

    path.write_text(text)


def patch_regigigas(root: Path) -> None:
    path = root / "res/field/scripts/scripts_snowpoint_temple_b5f.s"
    text = insert_titan_alias(path.read_text(), str(path))

    text = replace_once(
        text,
        """    WaitSE SE_CONFIRM_sseq_3
    GoToIfSet FLAG_AWAKENED_REGIGIGAS, SnowpointTempleB5F_EncounterRegigigas
    CheckHasAllLegendaryTitansInParty VAR_RESULT
""",
        """    WaitSE SE_CONFIRM_sseq_3
    SetFlag FLAG_MERCURY_TITAN_TABLET
    GoToIfSet FLAG_AWAKENED_REGIGIGAS, SnowpointTempleB5F_EncounterRegigigas
    CheckHasAllLegendaryTitansInParty VAR_RESULT
""",
        str(path),
    )

    path.write_text(text)


def patch_ruin_script(root: Path, rel: str, species: str) -> None:
    path = root / rel
    text = insert_titan_alias(path.read_text(), str(path))

    # If the player failed to capture a Titan, re-entering the ruin resets the
    # seven-dot state so the encounter is retryable without a parent-map hack.
    prefix = {
        "SPECIES_REGISTEEL": "IronRuins",
        "SPECIES_REGICE": "IcebergRuins",
        "SPECIES_REGIROCK": "RockPeakRuins",
    }[species]
    var = {
        "SPECIES_REGISTEEL": "VAR_IRON_RUINS_STATE",
        "SPECIES_REGICE": "VAR_ICEBERG_RUINS_STATE",
        "SPECIES_REGIROCK": "VAR_ROCK_PEAK_RUINS_STATE",
    }[species]

    text = replace_once(
        text,
        f"""{prefix}_OnTransition:
    GoToIfLt {var}, RUINS_STATE_DID_NOT_CATCH_REGI, {prefix}_ResetState
    End
""",
        f"""{prefix}_OnTransition:
    GoToIfEq {var}, RUINS_STATE_DID_NOT_CATCH_REGI, {prefix}_ResetState
    GoToIfLt {var}, RUINS_STATE_DID_NOT_CATCH_REGI, {prefix}_ResetState
    End
""",
        str(path) + " retry reset",
    )

    # Replace the old Hall-of-Fame gate at both the statue and final-dot paths.
    text = replace_n(
        text,
        "GoToIfUnset FLAG_GAME_COMPLETED",
        "GoToIfUnset FLAG_MERCURY_TITAN_TABLET",
        2,
        str(path) + " completion gates",
    )

    # Remove the external-event / fateful-Regigigas requirement from the
    # statue interaction. The Titan Tablet flag now owns access.
    fateful_block = {
        "SPECIES_REGISTEEL": """    CheckPartyHasFatefulEncounterRegigigas VAR_RESULT
    GoToIfEq VAR_RESULT, 0, IronRuins_ItsAStatueOfAPokemon
""",
        "SPECIES_REGICE": """    CheckPartyHasFatefulEncounterRegigigas VAR_RESULT
    GoToIfEq VAR_RESULT, 0, IcebergRuins_ItsAStatueOfAPokemon
""",
        "SPECIES_REGIROCK": """    CheckPartyHasFatefulEncounterRegigigas VAR_RESULT
    GoToIfEq VAR_RESULT, 0, RockPeakRuins_FromSomewhereSomethingSpokeOut
""",
    }[species]
    text = replace_once(text, fateful_block, "", str(path) + " fateful gate")

    text = replace_once(
        text,
        f"StartLegendaryBattle {species}, 30",
        f"StartLegendaryBattle {species}, 55",
        str(path) + " level",
    )

    path.write_text(text)


def patch_iron_and_iceberg_entrances(root: Path) -> None:
    patches = [
        (
            root / "res/field/scripts/scripts_iron_island_b3f.s",
            """    CheckPartyHasFatefulEncounterRegigigas VAR_MAP_LOCAL_0x04
    GoToIfEq VAR_MAP_LOCAL_0x04, FALSE, IronIslandB3F_RemoveWarpIronRuinsWithRegisteel
    GoToIfEq VAR_MAP_LOCAL_0x04, TRUE, IronIslandB3F_RemoveWarpIronRuinsWithoutRegisteel
""",
            """    GoToIfUnset FLAG_MERCURY_TITAN_TABLET, IronIslandB3F_RemoveWarpIronRuinsWithRegisteel
    GoToIfSet FLAG_MERCURY_TITAN_TABLET, IronIslandB3F_RemoveWarpIronRuinsWithoutRegisteel
""",
            2,
        ),
        (
            root / "res/field/scripts/scripts_mt_coronet_1f_north_room_2.s",
            """    CheckPartyHasFatefulEncounterRegigigas VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, FALSE, MtCoronet1FNorthRoom2_RemoveWarpIcebergRuinsWithRegice
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, MtCoronet1FNorthRoom2_RemoveWarpIcebergRuinsWithoutRegice
""",
            """    GoToIfUnset FLAG_MERCURY_TITAN_TABLET, MtCoronet1FNorthRoom2_RemoveWarpIcebergRuinsWithRegice
    GoToIfSet FLAG_MERCURY_TITAN_TABLET, MtCoronet1FNorthRoom2_RemoveWarpIcebergRuinsWithoutRegice
""",
            2,
        ),
    ]

    for path, old, new, expected in patches:
        text = insert_titan_alias(path.read_text(), str(path))
        text = replace_n(text, old, new, expected, str(path))
        path.write_text(text)


def patch_rock_peak_access(root: Path) -> None:
    # The Route 214 Ruin Maniac becomes the pre-League entrance to the real
    # Rock Peak Ruins once the Titan Tablet flag is active.
    tunnel = root / "res/field/scripts/scripts_maniac_tunnel.s"
    text = insert_titan_alias(tunnel.read_text(), str(tunnel))
    text = replace_once(
        text,
        """ManiacTunnel_RuinManiac:
    NPCMessage ManiacTunnel_Text_IDugToThisWeirdPlace
    End
""",
        """ManiacTunnel_RuinManiac:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    FacePlayer
    GoToIfUnset FLAG_MERCURY_TITAN_TABLET, ManiacTunnel_RuinManiac_Default
    Message ManiacTunnel_Text_IDugToThisWeirdPlace
    WaitButton
    CloseMessage
    FadeScreenOut
    WaitFadeScreen
    Warp MAP_HEADER_ROCK_PEAK_RUINS, 7, 11, DIR_NORTH
    FadeScreenIn
    WaitFadeScreen
    ReleaseAll
    End

ManiacTunnel_RuinManiac_Default:
    Message ManiacTunnel_Text_IDugToThisWeirdPlace
    WaitButton
    CloseMessage
    ReleaseAll
    End
""",
        str(tunnel),
    )
    tunnel.write_text(text)

    # The relocated ruin must return to the tunnel instead of dumping a
    # pre-League player onto postgame Route 228.
    events_path = root / "res/field/events/events_rock_peak_ruins.json"
    events = load_json(events_path)
    warps = events.get("warp_events", [])
    if len(warps) != 1:
        raise SystemExit("Rock Peak Ruins: expected exactly one exit warp")
    warp = warps[0]
    if warp.get("dest_header_id") != "MAP_HEADER_ROUTE_228":
        raise SystemExit("Rock Peak Ruins: unexpected vanilla exit destination")
    warp["dest_header_id"] = "MAP_HEADER_MANIAC_TUNNEL"
    warp["dest_warp_id"] = 1
    events_path.write_text(json.dumps(events, indent=4) + "\n")

    # Keep Route 228's event-version duplicate from opening the real Regirock
    # room later. Route 228 may retain its decorative/non-Regi ruin alias.
    route228 = root / "res/field/scripts/scripts_route_228.s"
    text = route228.read_text()
    old = """    CheckPartyHasFatefulEncounterRegigigas VAR_MAP_LOCAL_0x01
    GoToIfEq VAR_MAP_LOCAL_0x01, FALSE, Route228_RemoveWarpRockPeakRuinsWithRegirock
    GoToIfEq VAR_MAP_LOCAL_0x01, TRUE, Route228_RemoveWarpRockPeakRuinsWithoutRegirock
"""
    new = """    GoTo Route228_RemoveWarpRockPeakRuinsWithRegirock
"""
    text = replace_n(text, old, new, 2, str(route228))
    route228.write_text(text)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def validate(root: Path) -> dict[str, Any]:
    snowpoint = (root / "res/field/scripts/scripts_snowpoint_city.s").read_text()
    regigigas = (root / "res/field/scripts/scripts_snowpoint_temple_b5f.s").read_text()
    iron_parent = (root / "res/field/scripts/scripts_iron_island_b3f.s").read_text()
    ice_parent = (root / "res/field/scripts/scripts_mt_coronet_1f_north_room_2.s").read_text()
    tunnel = (root / "res/field/scripts/scripts_maniac_tunnel.s").read_text()
    route228 = (root / "res/field/scripts/scripts_route_228.s").read_text()
    rock_events = load_json(root / "res/field/events/events_rock_peak_ruins.json")

    ruin_texts = {
        name: (root / rel).read_text()
        for name, rel in RUIN_FILES.items()
    }

    if "CheckBadgeAcquired BADGE_ID_ICICLE" not in snowpoint:
        raise SystemExit("Snowpoint Temple entry is not badge-gated")
    if "ClearFlag FLAG_HIDE_SNOWPOINT_TEMPLE_B5F_REGIGIGAS" not in snowpoint:
        raise SystemExit("Regigigas is not enabled pre-League from Snowpoint")
    if "SetFlag FLAG_MERCURY_TITAN_TABLET" not in regigigas:
        raise SystemExit("Regigigas does not activate the Titan Tablet flag")
    if "CheckHasAllLegendaryTitansInParty" not in regigigas:
        raise SystemExit("Regigigas trio-party requirement was lost")
    if "StartLegendaryBattle SPECIES_REGIGIGAS, 1" not in regigigas:
        raise SystemExit("Regigigas Level-1 encounter was lost")

    for name, text in ruin_texts.items():
        if "CheckPartyHasFatefulEncounterRegigigas" in text:
            raise SystemExit(f"{name}: fateful-Regigigas gate still present")
        if "GoToIfUnset FLAG_GAME_COMPLETED" in text:
            raise SystemExit(f"{name}: Hall-of-Fame gate still present")
        if "FLAG_MERCURY_TITAN_TABLET" not in text:
            raise SystemExit(f"{name}: Titan Tablet gate missing")
        if "RUINS_STATE_DID_NOT_CATCH_REGI" not in text:
            raise SystemExit(f"{name}: retry state missing")

    expected_levels = {
        "iron": "StartLegendaryBattle SPECIES_REGISTEEL, 55",
        "iceberg": "StartLegendaryBattle SPECIES_REGICE, 55",
        "rock_peak": "StartLegendaryBattle SPECIES_REGIROCK, 55",
    }
    for name, needle in expected_levels.items():
        if needle not in ruin_texts[name]:
            raise SystemExit(f"{name}: Lv55 legendary battle missing")

    if "CheckPartyHasFatefulEncounterRegigigas" in iron_parent:
        raise SystemExit("Iron Ruins entrance still uses fateful-Regigigas gate")
    if "CheckPartyHasFatefulEncounterRegigigas" in ice_parent:
        raise SystemExit("Iceberg Ruins entrance still uses fateful-Regigigas gate")
    if "Warp MAP_HEADER_ROCK_PEAK_RUINS, 7, 11, DIR_NORTH" not in tunnel:
        raise SystemExit("Ruin Maniac Tunnel does not lead to Rock Peak Ruins")
    if "CheckPartyHasFatefulEncounterRegigigas" in route228:
        raise SystemExit("Route 228 still conditionally exposes the real Rock Peak Ruins")

    warp = rock_events["warp_events"][0]
    if warp["dest_header_id"] != "MAP_HEADER_MANIAC_TUNNEL" or warp["dest_warp_id"] != 1:
        raise SystemExit("Rock Peak Ruins does not return to Ruin Maniac Tunnel")

    return {
        "snowpoint_temple_preleague_badge": "ICICLE",
        "titan_story_flag": "FLAG_UNUSED_0x0163",
        "titan_story_alias": "FLAG_MERCURY_TITAN_TABLET",
        "regirock_level": 55,
        "regice_level": 55,
        "registeel_level": 55,
        "regigigas_level": 1,
        "regigigas_requires_trio_in_party": True,
        "external_fateful_regigigas_required": False,
        "hall_of_fame_required": False,
        "national_dex_required": False,
        "rock_peak_preleague_location": "Route 214 Ruin Maniac Tunnel",
        "rock_peak_exit_returns_to": "Maniac Tunnel",
        "retry_on_leave_reenter": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05c-regi-preleague.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_snowpoint_city(root)
    patch_regigigas(root)
    patch_ruin_script(root, RUIN_FILES["iron"], "SPECIES_REGISTEEL")
    patch_ruin_script(root, RUIN_FILES["iceberg"], "SPECIES_REGICE")
    patch_ruin_script(root, RUIN_FILES["rock_peak"], "SPECIES_REGIROCK")
    patch_iron_and_iceberg_entrances(root)
    patch_rock_peak_access(root)

    details = validate(root)
    report = {
        "gate": "MERCURY_MR05C_PRELEAGUE_REGI_LOOP",
        "status": "PASS",
        **details,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
