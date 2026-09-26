#!/usr/bin/env python3
"""MR05C — persistent randomizer settings foundation.

Reuses PlayerSave's four bytes of vanilla padding:
- the two-byte alignment padding after Options becomes randomizerFlags
- the two-byte tail padding becomes randomizerSeed

This preserves sizeof(PlayerSave) while making the Mercury randomizer seed and
independent toggles persistent. All defaults are OFF, so installing MR05C
changes no gameplay behavior by itself.
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


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def write_randomizer_header(root: Path) -> None:
    path = root / "include/mercury_randomizer.h"
    path.write_text(r'''#ifndef POKEPLATINUM_MERCURY_RANDOMIZER_H
#define POKEPLATINUM_MERCURY_RANDOMIZER_H

#include "constants/heap.h"
#include "global.h"

enum MercuryRandomizerFlag {
    MERCURY_RANDOMIZER_STATS      = (1 << 0),
    MERCURY_RANDOMIZER_ABILITIES  = (1 << 1),
    MERCURY_RANDOMIZER_MOVESETS   = (1 << 2),
    MERCURY_RANDOMIZER_TYPES      = (1 << 3),
    MERCURY_RANDOMIZER_WILD       = (1 << 4),
    MERCURY_RANDOMIZER_TRAINERS   = (1 << 5),
    MERCURY_RANDOMIZER_GIFTS      = (1 << 6),
    MERCURY_RANDOMIZER_STATICS    = (1 << 7),
    MERCURY_INNATE_ABILITIES      = (1 << 8),
    MERCURY_RANDOMIZER_MASTER     = (1 << 11),
};

#define MERCURY_RANDOMIZER_PRESET_SHIFT 9
#define MERCURY_RANDOMIZER_PRESET_MASK  (3 << MERCURY_RANDOMIZER_PRESET_SHIFT)
#define MERCURY_RANDOMIZER_TOGGLE_MASK  0x01FF

enum MercuryRandomizerPreset {
    MERCURY_RANDOMIZER_PRESET_OFF = 0,
    MERCURY_RANDOMIZER_PRESET_CUSTOM,
    MERCURY_RANDOMIZER_PRESET_SCALED_PROGRESSION,
    MERCURY_RANDOMIZER_PRESET_CHAOS_FULLY_RANDOM,
};

static inline u16 MercuryRandomizer_GetPresetFromFlags(u16 flags)
{
    return (flags & MERCURY_RANDOMIZER_PRESET_MASK) >> MERCURY_RANDOMIZER_PRESET_SHIFT;
}

static inline u16 MercuryRandomizer_SetPresetInFlags(u16 flags, enum MercuryRandomizerPreset preset)
{
    flags &= ~MERCURY_RANDOMIZER_PRESET_MASK;
    flags |= ((u16)preset << MERCURY_RANDOMIZER_PRESET_SHIFT) & MERCURY_RANDOMIZER_PRESET_MASK;
    return flags;
}

#endif // POKEPLATINUM_MERCURY_RANDOMIZER_H
''')


def patch_player_save(root: Path) -> None:
    header = root / "include/save_player.h"
    source = root / "src/save_player.c"

    insert_after_once(
        header,
        '#include "game_options.h"\n',
        '#include "mercury_randomizer.h"\n',
        "MR05C randomizer header include",
    )

    replace_once(
        header,
        """typedef struct PlayerSave {
    Options options; // u16 bitfield
    // u8 padding_02[2]; // implicit padding in vanilla
    TrainerInfo info;
    u16 coins;
    PlayTime playTime;
    u8 padding_2A[2];
} PlayerSave;
""",
        """typedef struct PlayerSave {
    Options options; // u16 bitfield
    u16 randomizerFlags; // reuses vanilla alignment padding at offset 0x02
    TrainerInfo info;
    u16 coins;
    PlayTime playTime;
    u16 randomizerSeed; // reuses vanilla tail padding at offset 0x2A
} PlayerSave;
""",
        "MR05C PlayerSave padding reuse",
    )

    insert_after_once(
        header,
        "PlayTime *SaveData_GetPlayTime(SaveData *saveData);\n",
        """u16 SaveData_GetMercuryRandomizerFlags(SaveData *saveData);
void SaveData_SetMercuryRandomizerFlags(SaveData *saveData, u16 flags);
u16 SaveData_GetMercuryRandomizerSeed(SaveData *saveData);
void SaveData_SetMercuryRandomizerSeed(SaveData *saveData, u16 seed);
BOOL SaveData_IsMercuryRandomizerEnabled(SaveData *saveData);
BOOL SaveData_GetMercuryRandomizerFlag(SaveData *saveData, enum MercuryRandomizerFlag flag);
enum MercuryRandomizerPreset SaveData_GetMercuryRandomizerPreset(SaveData *saveData);
""",
        "MR05C PlayerSave accessors",
    )

    insert_after_once(
        source,
        """PlayTime *SaveData_GetPlayTime(SaveData *saveData)
{
    PlayerSave *state = SaveData_SaveTable(saveData, SAVE_TABLE_ENTRY_PLAYER);
    return &state->playTime;
}
""",
        r'''
u16 SaveData_GetMercuryRandomizerFlags(SaveData *saveData)
{
    PlayerSave *state = SaveData_SaveTable(saveData, SAVE_TABLE_ENTRY_PLAYER);
    return state->randomizerFlags;
}

void SaveData_SetMercuryRandomizerFlags(SaveData *saveData, u16 flags)
{
    PlayerSave *state = SaveData_SaveTable(saveData, SAVE_TABLE_ENTRY_PLAYER);
    state->randomizerFlags = flags;
}

u16 SaveData_GetMercuryRandomizerSeed(SaveData *saveData)
{
    PlayerSave *state = SaveData_SaveTable(saveData, SAVE_TABLE_ENTRY_PLAYER);
    return state->randomizerSeed;
}

void SaveData_SetMercuryRandomizerSeed(SaveData *saveData, u16 seed)
{
    PlayerSave *state = SaveData_SaveTable(saveData, SAVE_TABLE_ENTRY_PLAYER);
    state->randomizerSeed = seed;
}

BOOL SaveData_IsMercuryRandomizerEnabled(SaveData *saveData)
{
    return (SaveData_GetMercuryRandomizerFlags(saveData) & MERCURY_RANDOMIZER_MASTER) != 0;
}

BOOL SaveData_GetMercuryRandomizerFlag(SaveData *saveData, enum MercuryRandomizerFlag flag)
{
    return (SaveData_GetMercuryRandomizerFlags(saveData) & (u16)flag) != 0;
}

enum MercuryRandomizerPreset SaveData_GetMercuryRandomizerPreset(SaveData *saveData)
{
    return (enum MercuryRandomizerPreset)MercuryRandomizer_GetPresetFromFlags(
        SaveData_GetMercuryRandomizerFlags(saveData));
}
''',
        "MR05C PlayerSave accessor implementations",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("defaults", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05c-randomizer-persistence.json"))
    args = ap.parse_args()

    cfg = json.loads(args.defaults.read_text())
    if cfg.get("schema") != 1:
        raise SystemExit("MR05C defaults schema must be 1")
    if cfg.get("seed") != 0:
        raise SystemExit("MR05C baseline seed must be 0")
    toggles = cfg.get("toggles", {})
    if not toggles or any(value is not False for value in toggles.values()):
        raise SystemExit("MR05C baseline requires every randomizer toggle OFF")

    root = args.pokeplatinum_root.resolve()
    write_randomizer_header(root)
    patch_player_save(root)

    report = {
        "gate": "MERCURY_MR05C_RANDOMIZER_PERSISTENCE",
        "status": "PASS",
        "save_block": "PlayerSave",
        "save_size_change_bytes": 0,
        "storage": {
            "randomizerFlags": "reuses vanilla 2-byte alignment padding",
            "randomizerSeed": "reuses vanilla 2-byte tail padding",
        },
        "seed_bits": 16,
        "persistent_controls": [
            "master enabled",
            "stats",
            "abilities",
            "movesets",
            "types",
            "wild",
            "trainers",
            "gifts",
            "statics",
            "innate abilities",
            "preset",
        ],
        "presets": cfg["presets"],
        "baseline_behavior": "all randomizer toggles off",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
