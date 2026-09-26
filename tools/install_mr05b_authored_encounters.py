#!/usr/bin/env python3
"""Install Mercury Redux authored encounter tables and full four-period land ecology.

MR05B corrective content pass:
- appends optional Mercury Morning/Day/Evening/Night 12-slot grass tables to
  Platinum encounter NARC members without moving any vanilla fields;
- selects those full tables at runtime when the Mercury magic is present;
- bypasses vanilla timed/swarm/dual-slot/daily replacements for authored
  Mercury tables so their ecology is not silently overwritten;
- installs the first recovered authored batch: Routes 201-204.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MERCURY_TOD_MAGIC = 0x4D524359
PERIODS = ("morning", "day", "evening", "night")

# Old Mercury custom forms that are not yet in the current canonical DS registry.
# Keep the source choice visible in the recovered data while providing a buildable
# temporary runtime species until that custom form is ported.
RUNTIME_FALLBACKS = {
    "SPECIES_ABRA_REDUX": "SPECIES_ABRA",
}


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def replace_count(path: Path, old: str, new: str, expected: int, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} matches in {path}, found {count}")
    path.write_text(text.replace(old, new))


def insert_after_once(path: Path, anchor: str, addition: str, label: str) -> None:
    text = path.read_text()
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + addition, 1))


def resolve_species(token: str, fallbacks_used: list[dict[str, str]]) -> str:
    runtime = RUNTIME_FALLBACKS.get(token, token)
    if runtime != token and not any(x["source"] == token for x in fallbacks_used):
        fallbacks_used.append({"source": token, "runtime": runtime})
    return runtime


def patch_wild_encounter_header(root: Path) -> None:
    path = root / "include/overlay006/wild_encounters.h"

    anchor = """typedef struct WildEncounters {
"""
    addition = f"""#define MERCURY_TIMED_GRASS_MAGIC 0x{MERCURY_TOD_MAGIC:08X}
#define MERCURY_TIMED_GRASS_TABLES 4

typedef struct MercuryGrassEncounter {{
    s8 maxLevel;
    s8 minLevel;
    u8 padding_02[2];
    int species;
}} MercuryGrassEncounter;

"""
    text = path.read_text()
    if "MERCURY_TIMED_GRASS_MAGIC" not in text:
        if text.count(anchor) != 1:
            raise SystemExit("MR05B header anchor mismatch")
        path.write_text(text.replace(anchor, addition + anchor, 1))

    replace_once(
        path,
        """    WaterEncounters goodRodEncounters;
    WaterEncounters superRodEncounters;
} WildEncounters;
""",
        """    WaterEncounters goodRodEncounters;
    WaterEncounters superRodEncounters;
    u32 mercuryTimedGrassMagic;
    MercuryGrassEncounter mercuryTimedGrass[MERCURY_TIMED_GRASS_TABLES][MAX_GRASS_ENCOUNTERS];
} WildEncounters;
""",
        "MR05B WildEncounters Mercury extension",
    )


def patch_converter(root: Path) -> None:
    path = root / "tools/jsoncnv/encounter.py"

    anchor = """def convert_water(encs: list) -> bytes:
    return b''.join(itertools.chain.from_iterable([
        (
            u8(encs[i]['level_max']),
            u8(encs[i]['level_min']),
            pad(2),
            as_species(encs[i]['species']),
        )
        for i in range(5)
    ]))


"""
    addition = f"""MERCURY_TIMED_GRASS_MAGIC = 0x{MERCURY_TOD_MAGIC:08X}
MERCURY_TOD_PERIODS = ('morning', 'day', 'evening', 'night')

def convert_mercury_tod(data: dict) -> bytes:
    tables = data.get('mercury_tod_land')
    if tables is None:
        return u32(0) + pad(4 * 12 * 8)

    out = bytearray()
    out.extend(u32(MERCURY_TIMED_GRASS_MAGIC))
    for period in MERCURY_TOD_PERIODS:
        encs = tables[period]
        if len(encs) != 12:
            raise ValueError(f"mercury_tod_land.{{period}} must contain 12 slots")
        for enc in encs:
            out.extend(u8(enc['level_max']))
            out.extend(u8(enc['level_min']))
            out.extend(pad(2))
            out.extend(as_species(enc['species']))
    return bytes(out)


"""
    text = path.read_text()
    if "def convert_mercury_tod" not in text:
        if text.count(anchor) != 1:
            raise SystemExit("MR05B converter helper anchor mismatch")
        path.write_text(text.replace(anchor, anchor + addition, 1))

    replace_once(
        path,
        """for rod in ['old', 'good', 'super']:
    packables.extend(u32(data[f'{rod}_rod_rate']))
    packables.extend(convert_water(data[f'{rod}_rod_encounters']))

with open(output_path, 'wb') as output_file:
""",
        """for rod in ['old', 'good', 'super']:
    packables.extend(u32(data[f'{rod}_rod_rate']))
    packables.extend(convert_water(data[f'{rod}_rod_encounters']))

packables.extend(convert_mercury_tod(data))

with open(output_path, 'wb') as output_file:
""",
        "MR05B converter append",
    )


def patch_runtime(root: Path) -> None:
    path = root / "src/overlay006/wild_encounters.c"

    timed_func = """void WildEncounters_ReplaceTimedEncounters(const WildEncounters *encounterData, int *timedSlot1, int *timedSlot2)
{
    int timeOfDay = GetTimeOfDay();

    if (timeOfDay == TIMEOFDAY_DAY || timeOfDay == TIMEOFDAY_TWILIGHT) {
        *timedSlot1 = encounterData->dayEncounters[0];
        *timedSlot2 = encounterData->dayEncounters[1];
    } else if (timeOfDay == TIMEOFDAY_NIGHT || timeOfDay == TIMEOFDAY_LATE_NIGHT) {
        *timedSlot1 = encounterData->nightEncounters[0];
        *timedSlot2 = encounterData->nightEncounters[1];
    }
}
"""
    helper = """
static BOOL WildEncounters_PopulateGrassEncounterTable(const WildEncounters *encounterData, EncounterSlot *encounterTable)
{
    if (encounterData->mercuryTimedGrassMagic == MERCURY_TIMED_GRASS_MAGIC) {
        int period = 0;
        int timeOfDay = GetTimeOfDay();

        if (timeOfDay == TIMEOFDAY_DAY) {
            period = 1;
        } else if (timeOfDay == TIMEOFDAY_TWILIGHT) {
            period = 2;
        } else if (timeOfDay == TIMEOFDAY_NIGHT || timeOfDay == TIMEOFDAY_LATE_NIGHT) {
            period = 3;
        }

        for (int i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
            encounterTable[i].species = encounterData->mercuryTimedGrass[period][i].species;
            encounterTable[i].maxLevel = encounterData->mercuryTimedGrass[period][i].maxLevel;
            encounterTable[i].minLevel = encounterData->mercuryTimedGrass[period][i].minLevel;
        }

        return TRUE;
    }

    for (int i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
        encounterTable[i].species = encounterData->grassEncounters.encounters[i].species;
        encounterTable[i].maxLevel = encounterData->grassEncounters.encounters[i].level;
        encounterTable[i].minLevel = encounterData->grassEncounters.encounters[i].level;
    }

    return FALSE;
}
"""
    text = path.read_text()
    if "WildEncounters_PopulateGrassEncounterTable" not in text:
        if text.count(timed_func) != 1:
            raise SystemExit("MR05B runtime helper anchor mismatch")
        path.write_text(text.replace(timed_func, timed_func + helper, 1))

    old_loop = """        for (int i = 0; i < MAX_GRASS_ENCOUNTERS; i++) {
            encounterTable[i].species = encounterData->grassEncounters.encounters[i].species;
            encounterTable[i].maxLevel = encounterData->grassEncounters.encounters[i].level;
            encounterTable[i].minLevel = encounterData->grassEncounters.encounters[i].level;
        }

        BOOL nationalDexObtained = Pokedex_IsNationalDexObtained(SaveData_GetPokedex(FieldSystem_GetSaveData(fieldSystem)));

        WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
        WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
        WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
        WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);
"""
    new_loop = """        BOOL mercuryTimedGrass = WildEncounters_PopulateGrassEncounterTable(encounterData, encounterTable);

        BOOL nationalDexObtained = Pokedex_IsNationalDexObtained(SaveData_GetPokedex(FieldSystem_GetSaveData(fieldSystem)));

        if (mercuryTimedGrass == FALSE) {
            WildEncounters_ReplaceTimedEncounters(encounterData, &encounterTable[2].species, &encounterTable[3].species);
            WildEncounters_ReplaceSwarmEncounters(fieldSystem, encounterData, &encounterTable[0].species, &encounterTable[1].species);
            WildEncounters_ReplaceTrophyGardenEncounters(fieldSystem, nationalDexObtained, &encounterTable[6].species, &encounterTable[7].species);
            WildEncounters_ReplaceDualSlotEncounters(encounterData, nationalDexObtained, &encounterTable[8].species, &encounterTable[9].species);
        }
"""
    replace_count(path, old_loop, new_loop, 3, "MR05B grass table population")

    replace_count(
        path,
        """            WildEncounters_ReplaceGreatMarshDailyEncounters(fieldSystem, safariGameActive, nationalDexObtained, encounterTable);

""",
        """            if (mercuryTimedGrass == FALSE) {
                WildEncounters_ReplaceGreatMarshDailyEncounters(fieldSystem, safariGameActive, nationalDexObtained, encounterTable);
            }

""",
        3,
        "MR05B Great Marsh authored-table guard",
    )


def validate_source_area(key: str, area: dict[str, Any]) -> None:
    for period in PERIODS:
        slots = area.get(period)
        if not isinstance(slots, list) or len(slots) != 12:
            raise SystemExit(f"{key}: {period} must contain exactly 12 slots")
        for i, slot in enumerate(slots):
            if not isinstance(slot.get("species"), str) or not slot["species"].startswith("SPECIES_"):
                raise SystemExit(f"{key}: {period}[{i}] invalid species")
            lo = slot.get("min_level")
            hi = slot.get("max_level")
            if not isinstance(lo, int) or not isinstance(hi, int) or lo < 1 or hi < lo or hi > 100:
                raise SystemExit(f"{key}: {period}[{i}] invalid level range")


def install_areas(root: Path, data_path: Path) -> dict[str, Any]:
    source = json.loads(data_path.read_text())
    if source.get("schema") != 1:
        raise SystemExit("MR05B authored encounter source schema must be 1")

    changed = []
    fallbacks_used: list[dict[str, str]] = []

    for key, area in source["areas"].items():
        validate_source_area(key, area)
        target = root / "res/field/encounters" / f"{key}.json"
        if not target.exists():
            raise SystemExit(f"MR05B target encounter file missing: {target}")

        data = json.loads(target.read_text())
        data["land_rate"] = area["encounter_rate"]

        mercury_tables = {}
        for period in PERIODS:
            mercury_tables[period] = [
                {
                    "level_max": slot["max_level"],
                    "level_min": slot["min_level"],
                    "species": resolve_species(slot["species"], fallbacks_used),
                }
                for slot in area[period]
            ]

        # Keep legacy readers/Pokedex tooling on Mercury species too. Runtime uses
        # the full tables below, so this morning table is only the compatibility view.
        data["land_encounters"] = [
            {
                "level": (slot["level_min"] + slot["level_max"]) // 2,
                "species": slot["species"],
            }
            for slot in mercury_tables["morning"]
        ]
        data["day"] = [mercury_tables["day"][2]["species"], mercury_tables["day"][3]["species"]]
        data["night"] = [mercury_tables["night"][2]["species"], mercury_tables["night"][3]["species"]]
        data["swarms"] = [mercury_tables["morning"][0]["species"], mercury_tables["morning"][1]["species"]]
        data["radar"] = [
            mercury_tables["day"][8]["species"],
            mercury_tables["day"][9]["species"],
            mercury_tables["night"][8]["species"],
            mercury_tables["night"][9]["species"],
        ]
        for version in ("ruby", "sapphire", "emerald", "firered", "leafgreen"):
            data[version] = [mercury_tables["morning"][10]["species"], mercury_tables["morning"][11]["species"]]

        data["mercury_tod_land"] = mercury_tables
        target.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
        changed.append(key)

    return {
        "changed_areas": changed,
        "fallbacks": fallbacks_used,
        "source_blob": source.get("source_blob"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("authored_data", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05b-authored-encounters.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    patch_wild_encounter_header(root)
    patch_converter(root)
    patch_runtime(root)
    installed = install_areas(root, args.authored_data)

    report = {
        "gate": "MERCURY_MR05B_AUTHORED_ENCOUNTERS",
        "status": "PASS",
        "four_period_full_land_tables": True,
        "periods": list(PERIODS),
        "changed_area_count": len(installed["changed_areas"]),
        "changed_areas": installed["changed_areas"],
        "source_blob": installed["source_blob"],
        "runtime_fallbacks": installed["fallbacks"],
        "vanilla_special_replacements_bypassed_for_mercury_tables": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
