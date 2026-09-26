#!/usr/bin/env python3
"""Install Mercury Redux instant regional Honey Trees into Platinum DS."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALIASES = {
    "SPECIES_FARFETCHD_GALAR": "SPECIES_FARFETCHD",
    "SPECIES_VULPIX_ALOLA": "SPECIES_VULPIX",
    "SPECIES_VOLTORB_HISUI": "SPECIES_VOLTORB",
}


def sp(token: str) -> str:
    return ALIASES.get(token, token)


def parse_legacy_script(path: Path) -> dict[str, list[dict[str, int | str]]]:
    text = path.read_text()
    region_names = (
        "Floaroma", "Eterna", "Route215", "Route214", "Route213",
        "Route212South", "Route212North", "Route218",
    )
    out = {}

    for region in region_names:
        start_label = f"MercuryHoneyTree_EventScript_{region}::"
        start = text.find(start_label)
        if start < 0:
            raise SystemExit(f"Missing recovered Honey Tree region {region}")
        next_starts = [
            text.find(f"MercuryHoneyTree_EventScript_{other}::", start + 1)
            for other in region_names
            if text.find(f"MercuryHoneyTree_EventScript_{other}::", start + 1) >= 0
        ]
        end = min(next_starts) if next_starts else text.find("MercuryHoneyTree_EventScript_StartBattle::", start)
        if end < 0:
            end = len(text)
        block = text[start:end]

        thresholds = []
        for m in re.finditer(
            r"goto_if_lt VAR_RESULT,\s*(\d+),\s*(MercuryHoneyTree_EventScript_[A-Za-z0-9_]+)",
            block,
        ):
            thresholds.append((int(m.group(1)), m.group(2)))
        final = re.search(
            r"^\s*goto\s+(MercuryHoneyTree_EventScript_[A-Za-z0-9_]+)\s*$",
            block,
            re.MULTILINE,
        )
        if final is None:
            raise SystemExit(f"{region}: missing final Honey Tree target")

        targets = [target for _threshold, target in thresholds] + [final.group(1)]
        cutoffs = [threshold for threshold, _target in thresholds] + [100]
        previous = 0
        pool = []

        for cutoff, target in zip(cutoffs, targets):
            label_pos = block.find(target + "::")
            if label_pos < 0:
                raise SystemExit(f"{region}: missing target body {target}")
            body = block[label_pos:label_pos + 250]
            match = re.search(r"setwildbattle\s+(SPECIES_[A-Z0-9_]+),\s*(\d+)", body)
            if match is None:
                raise SystemExit(f"{region}: missing setwildbattle for {target}")
            weight = cutoff - previous
            previous = cutoff
            level = int(match.group(2))
            pool.append({
                "species": sp(match.group(1)),
                "min_level": level,
                "max_level": level,
                "weight": weight,
            })

        if sum(int(x["weight"]) for x in pool) != 100:
            raise SystemExit(f"{region}: weights do not total 100")
        out[region] = pool
    return out


def normalize_pool(raw: list[dict[str, Any]], default_levels: tuple[int, int] | None = None):
    pool = []
    for row in raw:
        weight = int(row.get("weight", row.get("chance", 0)))
        if "min_level" in row:
            lo = int(row["min_level"])
            hi = int(row["max_level"])
        elif default_levels is not None:
            lo, hi = default_levels
        else:
            raise SystemExit(f"Honey pool row has no level range: {row}")
        pool.append({
            "species": sp(row["species"]),
            "min_level": lo,
            "max_level": hi,
            "weight": weight,
        })
    if sum(x["weight"] for x in pool) != 100:
        raise SystemExit(f"Honey pool weights must total 100: {pool}")
    if any(x["species"] == "SPECIES_BURMY" for x in pool):
        raise SystemExit("Burmy is forbidden from Mercury premium Honey Tree pools")
    return pool


def load_json(path: Path):
    return json.loads(path.read_text())


def build_pools(recovered: Path):
    legacy = parse_legacy_script(recovered / "mercury_honey_tree.inc")

    missing = load_json(recovered / "sinnoh_missing_area_audit_registry_2026-09-05.json")
    r210 = load_json(recovered / "route210_north_celestic_registry_2026-09-05.json")
    r211 = load_json(recovered / "route211_mt_coronet_celestic_registry_2026-09-05.json")
    r222 = load_json(recovered / "distortion_route222_sunyshore_registry_2026-09-05.json")

    pools = {name: normalize_pool(pool) for name, pool in legacy.items()}
    pools["Route205North"] = normalize_pool(missing["areas"]["ROUTE_205_NORTH"]["instant_honey_tree"])
    pools["Route210North"] = normalize_pool(r210["instant_honey_tree"]["pool"], (38, 42))
    pools["Route211East"] = normalize_pool(r211["route211_east"]["instant_honey_tree"]["pool"], (40, 43))
    pools["Route221"] = normalize_pool(missing["areas"]["ROUTE_221"]["instant_honey_tree"])
    pools["Route222"] = normalize_pool(r222["areas"]["ROUTE_222"]["instant_honey_tree"])

    pools["Fuego"] = normalize_pool([
        {"species":"SPECIES_ELEKID","min_level":35,"max_level":38,"weight":15},
        {"species":"SPECIES_CHARCADET","min_level":35,"max_level":38,"weight":15},
        {"species":"SPECIES_TORKOAL","min_level":36,"max_level":38,"weight":15},
        {"species":"SPECIES_HEATMOR","min_level":36,"max_level":38,"weight":10},
        {"species":"SPECIES_TURTONATOR","min_level":37,"max_level":39,"weight":10},
        {"species":"SPECIES_TOGEDEMARU","min_level":36,"max_level":38,"weight":10},
        {"species":"SPECIES_LARVESTA","min_level":37,"max_level":39,"weight":10},
        {"species":"SPECIES_FLETCHINDER","min_level":35,"max_level":38,"weight":5},
        {"species":"SPECIES_LITLEO","min_level":35,"max_level":38,"weight":5},
        {"species":"SPECIES_PORYGON","min_level":37,"max_level":39,"weight":5},
    ])
    return pools


TREE_PROFILE = {
    "MAP_HEADER_ROUTE_205_SOUTH": "Floaroma",
    "MAP_HEADER_ROUTE_205_NORTH": "Route205North",
    "MAP_HEADER_ROUTE_206": "Eterna",
    "MAP_HEADER_ROUTE_207": "Fuego",
    "MAP_HEADER_ROUTE_208": "Eterna",
    "MAP_HEADER_ROUTE_209": "Eterna",
    "MAP_HEADER_ROUTE_210_SOUTH": "Eterna",
    "MAP_HEADER_ROUTE_210_NORTH": "Route210North",
    "MAP_HEADER_ROUTE_211_EAST": "Route211East",
    "MAP_HEADER_ROUTE_212_NORTH": "Route212North",
    "MAP_HEADER_ROUTE_212_SOUTH": "Route212South",
    "MAP_HEADER_ROUTE_213": "Route213",
    "MAP_HEADER_ROUTE_214": "Route214",
    "MAP_HEADER_ROUTE_215": "Route215",
    "MAP_HEADER_ROUTE_218": "Route218",
    "MAP_HEADER_ROUTE_221": "Route221",
    "MAP_HEADER_ROUTE_222": "Route222",
    "MAP_HEADER_VALLEY_WINDWORKS_OUTSIDE": "Floaroma",
    "MAP_HEADER_ETERNA_FOREST_OUTSIDE": "Eterna",
    "MAP_HEADER_FUEGO_IRONWORKS_OUTSIDE": "Fuego",
    "MAP_HEADER_FLOAROMA_MEADOW": "Floaroma",
}


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def write_header(root: Path, pools: dict):
    used_profiles = sorted(set(TREE_PROFILE.values()))
    lines = [
        "#ifndef POKEPLATINUM_GENERATED_MERCURY_HONEY_TREES_H",
        "#define POKEPLATINUM_GENERATED_MERCURY_HONEY_TREES_H",
        "",
        '#include "generated/map_headers.h"',
        "",
        "typedef struct MercuryHoneyTreeEntry {",
        "    u16 species;",
        "    u8 minLevel;",
        "    u8 maxLevel;",
        "    u8 cumulative;",
        "} MercuryHoneyTreeEntry;",
        "",
    ]
    index = {}
    for i, profile in enumerate(used_profiles):
        index[profile] = i
        cumulative = 0
        entries = pools[profile]
        lines.append(f"static const MercuryHoneyTreeEntry sMercuryHoneyPool{i}[] = {{ // {profile}")
        for row in entries:
            cumulative += int(row["weight"])
            lines.append(
                f"    {{ {row['species']}, {row['min_level']}, {row['max_level']}, {cumulative} }},"
            )
        lines += ["};", ""]

    lines += [
        "static BOOL MercuryHoneyTree_SelectByMap(",
        "    const enum MapHeaderID mapHeaderID, int *species, u8 *level)",
        "{",
        "    const MercuryHoneyTreeEntry *pool = NULL;",
        "    u8 count = 0;",
        "    switch (mapHeaderID) {",
    ]
    for header, profile in TREE_PROFILE.items():
        i=index[profile]
        lines += [
            f"    case {header}:",
            f"        pool = sMercuryHoneyPool{i};",
            f"        count = NELEMS(sMercuryHoneyPool{i});",
            "        break;",
        ]
    lines += [
        "    default:",
        "        return FALSE;",
        "    }",
        "",
        "    const u8 roll = LCRNG_RandMod(100);",
        "    for (u8 i = 0; i < count; i++) {",
        "        if (roll < pool[i].cumulative) {",
        "            *species = pool[i].species;",
        "            *level = pool[i].minLevel;",
        "            if (pool[i].maxLevel > pool[i].minLevel) {",
        "                *level += LCRNG_RandMod(pool[i].maxLevel - pool[i].minLevel + 1);",
        "            }",
        "            return TRUE;",
        "        }",
        "    }",
        "    return FALSE;",
        "}",
        "",
        "#endif",
        "",
    ]
    out=root/"include/generated/mercury_honey_trees.h"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(lines))


def patch_honey_runtime(root: Path):
    header = root / "include/overlay005/honey_tree.h"
    replace_once(
        header,
        "int HoneyTree_GetSpecies(FieldSystem *fieldSystem);\n",
        "int HoneyTree_GetSpecies(FieldSystem *fieldSystem);\nBOOL HoneyTree_SelectMercuryEncounter(FieldSystem *fieldSystem, int *species, u8 *level);\n",
        "Mercury Honey declaration",
    )

    source = root / "src/overlay005/honey_tree.c"
    text=source.read_text()
    anchor='#include "trainer_info.h"\n'
    include='#include "generated/mercury_honey_trees.h"\n'
    if include not in text:
        if text.count(anchor)!=1:
            raise SystemExit("Mercury Honey generated-header include anchor mismatch")
        text=text.replace(anchor,anchor+"\n"+include,1)

    getter="int HoneyTree_GetSpecies(FieldSystem *fieldSystem)\n"
    wrapper="""BOOL HoneyTree_SelectMercuryEncounter(FieldSystem *fieldSystem, int *species, u8 *level)
{
    return MercuryHoneyTree_SelectByMap(fieldSystem->location->mapHeaderID, species, level);
}

"""
    if wrapper not in text:
        if text.count(getter)!=1:
            raise SystemExit("Mercury Honey getter anchor mismatch")
        text=text.replace(getter,wrapper+getter,1)
    source.write_text(text)

    wild = root / "src/overlay006/wild_encounters.c"
    old="""    int species = HoneyTree_GetSpecies(fieldSystem);

    Party *playerParty = SaveData_GetParty(fieldSystem->saveData);
    firstPartyMon = Party_GetPokemonBySlotIndex(playerParty, 0);

    WildEncounters_FieldParams encounterFieldParams;
    InitEncounterFieldParams(fieldSystem, firstPartyMon, NULL, &encounterFieldParams);

    u8 levelVariance = 15 - 5 + 1;

    u8 level = 5 + LCRNG_RandMod(levelVariance);

    if (!encounterFieldParams.isFirstMonEgg && (encounterFieldParams.firstMonAbility == ABILITY_HUSTLE || encounterFieldParams.firstMonAbility == ABILITY_VITAL_SPIRIT || encounterFieldParams.firstMonAbility == ABILITY_PRESSURE)) {
        if (LCRNG_RandMod(2) == 0) {
            (void)0;
        } else {
            level = 15;
        }
    }
"""
    new="""    int species;
    u8 level;
    BOOL mercuryHoney = HoneyTree_SelectMercuryEncounter(fieldSystem, &species, &level);

    Party *playerParty = SaveData_GetParty(fieldSystem->saveData);
    firstPartyMon = Party_GetPokemonBySlotIndex(playerParty, 0);

    WildEncounters_FieldParams encounterFieldParams;
    InitEncounterFieldParams(fieldSystem, firstPartyMon, NULL, &encounterFieldParams);

    if (mercuryHoney == FALSE) {
        species = HoneyTree_GetSpecies(fieldSystem);

        u8 levelVariance = 15 - 5 + 1;
        level = 5 + LCRNG_RandMod(levelVariance);

        if (!encounterFieldParams.isFirstMonEgg && (encounterFieldParams.firstMonAbility == ABILITY_HUSTLE || encounterFieldParams.firstMonAbility == ABILITY_VITAL_SPIRIT || encounterFieldParams.firstMonAbility == ABILITY_PRESSURE)) {
            if (LCRNG_RandMod(2) != 0) {
                level = 15;
            }
        }
    }
"""
    replace_once(wild,old,new,"Mercury Honey species/level selector")

    scripts=root/"res/field/scripts/scripts_common.s"
    old_script="""    SlatherHoneyTree
    WaitTime 10, VAR_RESULT
    Message CommonStrings_Text_BarkWasSlathered
    WaitButton
    CloseMessage
    ReleaseAll
    End
"""
    new_script="""    SlatherHoneyTree
    WaitTime 10, VAR_RESULT
    Message CommonStrings_Text_BarkWasSlathered
    WaitButton
    CloseMessage
    GoTo CommonScript_HoneyTreeEncounter
"""
    replace_once(scripts,old_script,new_script,"Mercury instant Honey interaction")


def patch_global_fallback(root: Path):
    path=root/"res/field/encounters/encounters_honey_tree.json"
    data=json.loads(path.read_text())
    data["common"]=[
        "SPECIES_AIPOM","SPECIES_TEDDIURSA","SPECIES_CUTIEFLY",
        "SPECIES_APPLIN","SPECIES_HERACROSS","SPECIES_PINSIR",
    ]
    data["uncommon"]=[
        "SPECIES_SCYTHER","SPECIES_MUNCHLAX","SPECIES_PHANTUMP",
        "SPECIES_SLAKOTH","SPECIES_LARVESTA","SPECIES_EEVEE",
    ]
    data["rare"]=[
        "SPECIES_MUNCHLAX","SPECIES_HERACROSS","SPECIES_SCYTHER",
        "SPECIES_LARVESTA","SPECIES_EEVEE","SPECIES_APPLIN",
    ]
    path.write_text(json.dumps(data,indent=4)+"\n")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("recovered_dir",type=Path)
    ap.add_argument("--report",type=Path,default=Path("mr05b-honey-trees.json"))
    args=ap.parse_args()

    pools=build_pools(args.recovered_dir)
    missing_profiles=sorted(set(TREE_PROFILE.values())-set(pools))
    if missing_profiles:
        raise SystemExit(f"Missing Mercury Honey profiles: {missing_profiles}")
    if len(TREE_PROFILE)!=21:
        raise SystemExit(f"Expected 21 Platinum Honey Tree maps, found {len(TREE_PROFILE)}")

    write_header(args.pokeplatinum_root,pools)
    patch_honey_runtime(args.pokeplatinum_root)
    patch_global_fallback(args.pokeplatinum_root)

    report={
        "gate":"MERCURY_MR05B_INSTANT_REGIONAL_HONEY_TREES",
        "status":"PASS",
        "tree_map_count":len(TREE_PROFILE),
        "regional_profile_count":len(set(TREE_PROFILE.values())),
        "instant_battle":True,
        "real_time_wait_hours":0,
        "burmy_present":False,
        "consume_one_honey_per_encounter":True,
        "map_profiles":TREE_PROFILE,
        "profile_species":{
            name:[row["species"] for row in pool]
            for name,pool in pools.items()
            if name in set(TREE_PROFILE.values())
        },
    }
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
