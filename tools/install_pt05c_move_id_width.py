#!/usr/bin/env python3
"""Expand Platinum's level-up learnset move IDs from 9 bits to 16 bits.

Native Platinum packs each level-up learnset entry into 16 bits:
  9 bits move ID + 7 bits level.
That caps level-up move IDs at 511, which is incompatible with the Gen 5-9
canonical move namespace (through 922 in the pinned donor).

Mercury changes only the WOTBL learnset member format. Saved Pokemon already
store known move IDs as u16, and the battle/UI move paths are predominantly
u16, so the save format does not need to change for this gate.

New WOTBL entry layout (4 bytes):
  u16 move
  u8  level
  u8  padding

The padding byte is 0 for normal rows and 0xFF for the sentinel.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1))


def replace_all_exact(path: Path, old: str, new: str, expected: int, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{path}: expected {expected} {label} matches, found {count}")
    path.write_text(text.replace(old, new))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    species_h = root / "include/struct_defs/species.h"
    pokemon_h = root / "include/pokemon.h"
    pokemon_c = root / "src/pokemon.c"
    reminder_c = root / "src/move_reminder_data.c"
    speciesproc_c = root / "tools/dataproc/src/speciesproc.c"

    replace_once(
        species_h,
        """#define MAX_LEARNSET_ENTRIES        20
#define LEARNSET_NO_MOVE_TO_LEARN   0
#define LEARNSET_MOVE_ALREADY_KNOWN 0xFFFE
#define LEARNSET_ALL_SLOTS_FILLED   0xFFFF
#define LEARNSET_SENTINEL_ENTRY     0xFFFF
""",
        """#define MAX_LEARNSET_ENTRIES        20
#define LEARNSET_NO_MOVE_TO_LEARN   0
#define LEARNSET_MOVE_ALREADY_KNOWN 0xFFFE
#define LEARNSET_ALL_SLOTS_FILLED   0xFFFF
#define LEARNSET_SENTINEL_MOVE      0xFFFF
#define LEARNSET_SENTINEL_LEVEL     0xFF
""",
        "learnset constants",
    )

    replace_once(
        species_h,
        """typedef struct SpeciesLearnsetEntry {
    u16 move : 9;
    u16 level : 7;
} SpeciesLearnsetEntry;
""",
        """typedef struct SpeciesLearnsetEntry {
    u16 move;
    u8 level;
    u8 padding;
} SpeciesLearnsetEntry;

#define LEARNSET_ENTRY_IS_SENTINEL(entry) \
    ((entry).move == LEARNSET_SENTINEL_MOVE && (entry).level == LEARNSET_SENTINEL_LEVEL)
""",
        "learnset struct",
    )

    replace_once(
        pokemon_h,
        """ * @param[out] monLevelUpMoves Pointer to a u16 array to store the move table
 */
void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, u16 *monLevelUpMoves);
""",
        """ * @param[out] monLevelUpMoves Pointer to a SpeciesLearnsetEntry array to store the move table
 */
void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, SpeciesLearnsetEntry *monLevelUpMoves);
""",
        "learnset loader declaration",
    )

    replace_once(
        pokemon_c,
        """static void BoxPokemon_SetDefaultMoves(BoxPokemon *boxMon)
{
    BOOL reencrypt; // must pre-declare to match
    u16 *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    reencrypt = BoxPokemon_EnterDecryptionContext(boxMon);

    u16 monSpecies = BoxPokemon_GetValue(boxMon, MON_DATA_SPECIES, NULL);
    int monForm = BoxPokemon_GetValue(boxMon, MON_DATA_FORM, NULL);
    u8 monLevel = BoxPokemon_GetLevel(boxMon);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    for (int i = 0; monLevelUpMoves[i] != LEARNSET_SENTINEL_ENTRY; i++) {
        if ((monLevelUpMoves[i] & 0xFE00) <= monLevel << 9) {
            u16 monLevelUpMoveID = monLevelUpMoves[i] & 0x1FF;
            if (BoxPokemon_AddMove(boxMon, monLevelUpMoveID) == LEARNSET_ALL_SLOTS_FILLED) {
                BoxPokemon_ReplaceMove(boxMon, monLevelUpMoveID);
            }
        } else {
            break;
        }
    }

    Heap_Free(monLevelUpMoves);
    BoxPokemon_ExitDecryptionContext(boxMon, reencrypt);
}
""",
        """static void BoxPokemon_SetDefaultMoves(BoxPokemon *boxMon)
{
    BOOL reencrypt; // must pre-declare to match
    SpeciesLearnsetEntry *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    reencrypt = BoxPokemon_EnterDecryptionContext(boxMon);

    u16 monSpecies = BoxPokemon_GetValue(boxMon, MON_DATA_SPECIES, NULL);
    int monForm = BoxPokemon_GetValue(boxMon, MON_DATA_FORM, NULL);
    u8 monLevel = BoxPokemon_GetLevel(boxMon);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    for (int i = 0; !LEARNSET_ENTRY_IS_SENTINEL(monLevelUpMoves[i]); i++) {
        if (monLevelUpMoves[i].level <= monLevel) {
            u16 monLevelUpMoveID = monLevelUpMoves[i].move;
            if (BoxPokemon_AddMove(boxMon, monLevelUpMoveID) == LEARNSET_ALL_SLOTS_FILLED) {
                BoxPokemon_ReplaceMove(boxMon, monLevelUpMoveID);
            }
        } else {
            break;
        }
    }

    Heap_Free(monLevelUpMoves);
    BoxPokemon_ExitDecryptionContext(boxMon, reencrypt);
}
""",
        "default move loader",
    )

    replace_once(
        pokemon_c,
        """u16 Pokemon_LevelUpMove(Pokemon *mon, int *index, u16 *moveID)
{
    u16 result = MOVE_NONE;
    u16 *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    u16 monSpecies = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    int monForm = Pokemon_GetValue(mon, MON_DATA_FORM, NULL);
    u8 monLevel = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    if (monLevelUpMoves[*index] == LEARNSET_SENTINEL_ENTRY) {
        Heap_Free(monLevelUpMoves);
        return MOVE_NONE;
    }

    while ((monLevelUpMoves[*index] & 0xFE00) != monLevel << 9) {
        (*index)++;
        if (monLevelUpMoves[*index] == LEARNSET_SENTINEL_ENTRY) {
            Heap_Free(monLevelUpMoves);
            return MOVE_NONE;
        }
    }

    if ((monLevelUpMoves[*index] & 0xFE00) == monLevel << 9) {
        *moveID = monLevelUpMoves[*index] & 0x1FF;
        (*index)++;
        result = Pokemon_AddMove(mon, *moveID);
    }

    Heap_Free(monLevelUpMoves);
    return result;
}
""",
        """u16 Pokemon_LevelUpMove(Pokemon *mon, int *index, u16 *moveID)
{
    u16 result = MOVE_NONE;
    SpeciesLearnsetEntry *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    u16 monSpecies = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    int monForm = Pokemon_GetValue(mon, MON_DATA_FORM, NULL);
    u8 monLevel = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    if (LEARNSET_ENTRY_IS_SENTINEL(monLevelUpMoves[*index])) {
        Heap_Free(monLevelUpMoves);
        return MOVE_NONE;
    }

    while (monLevelUpMoves[*index].level != monLevel) {
        (*index)++;
        if (LEARNSET_ENTRY_IS_SENTINEL(monLevelUpMoves[*index])) {
            Heap_Free(monLevelUpMoves);
            return MOVE_NONE;
        }
    }

    if (monLevelUpMoves[*index].level == monLevel) {
        *moveID = monLevelUpMoves[*index].move;
        (*index)++;
        result = Pokemon_AddMove(mon, *moveID);
    }

    Heap_Free(monLevelUpMoves);
    return result;
}
""",
        "level-up move learner",
    )

    replace_once(
        pokemon_c,
        """int Pokemon_LoadLevelUpMoveIdsOf(int monSpecies, int monForm, u16 *monLevelUpMoveIDs)
{
    u16 *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    int result = 0;

    while (monLevelUpMoves[result] != LEARNSET_ALL_SLOTS_FILLED) {
        monLevelUpMoveIDs[result] = monLevelUpMoves[result] & 0x1FF;
        result++;
    }

    Heap_Free(monLevelUpMoves);
    return result;
}
""",
        """int Pokemon_LoadLevelUpMoveIdsOf(int monSpecies, int monForm, u16 *monLevelUpMoveIDs)
{
    SpeciesLearnsetEntry *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    int result = 0;

    while (!LEARNSET_ENTRY_IS_SENTINEL(monLevelUpMoves[result])) {
        monLevelUpMoveIDs[result] = monLevelUpMoves[result].move;
        result++;
    }

    Heap_Free(monLevelUpMoves);
    return result;
}
""",
        "move ID list loader",
    )

    replace_once(
        pokemon_c,
        """void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, u16 *monLevelUpMoves)
{
    monSpecies = Pokemon_GetFormNarcIndex(monSpecies, monForm);
    NARC_ReadWholeMemberByIndexPair(monLevelUpMoves, NARC_INDEX_POKETOOL__PERSONAL__WOTBL, monSpecies);
}
""",
        """void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, SpeciesLearnsetEntry *monLevelUpMoves)
{
    monSpecies = Pokemon_GetFormNarcIndex(monSpecies, monForm);
    NARC_ReadWholeMemberByIndexPair(monLevelUpMoves, NARC_INDEX_POKETOOL__PERSONAL__WOTBL, monSpecies);
}
""",
        "learnset loader definition",
    )

    replace_once(
        reminder_c,
        """#define GET_LEVEL(move) ((move & 0xfe00) >> 9)
#define GET_MOVE(move)  ((move & 0x1ff) >> 0)

""",
        "",
        "legacy reminder bit macros",
    )

    replace_once(
        reminder_c,
        """    u16 *levelUpMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));
    u16 *reminderMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));
""",
        """    SpeciesLearnsetEntry *levelUpMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(SpeciesLearnsetEntry));
    u16 *reminderMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));
""",
        "reminder allocation",
    )

    replace_once(
        reminder_c,
        """    for (i = 0; i < MAX_NUMBER_REMINDER_MOVES; i++) {
        if (levelUpMoves[i] == LEVEL_UP_MOVESET_TERMINATOR) {
            reminderMoves[j] = LEVEL_UP_MOVESET_TERMINATOR;
            break;
        } else if (GET_LEVEL(levelUpMoves[i]) > level) {
            continue;
        } else {
            levelUpMoves[i] = GET_MOVE(levelUpMoves[i]);

            for (h = 0; h < LEARNED_MOVES_MAX; h++) {
                if (levelUpMoves[i] == currentMoves[h]) {
                    break;
                }
            }

            if (h == LEARNED_MOVES_MAX) {
                for (h = 0; h < j; h++) {
                    if (reminderMoves[h] == levelUpMoves[i]) {
                        break;
                    }
                }

                if (h == j) {
                    reminderMoves[j] = levelUpMoves[i];
                    j++;
                }
            }
        }
    }
""",
        """    for (i = 0; i < MAX_NUMBER_REMINDER_MOVES; i++) {
        if (LEARNSET_ENTRY_IS_SENTINEL(levelUpMoves[i])) {
            reminderMoves[j] = LEVEL_UP_MOVESET_TERMINATOR;
            break;
        } else if (levelUpMoves[i].level > level) {
            continue;
        } else {
            u16 move = levelUpMoves[i].move;

            for (h = 0; h < LEARNED_MOVES_MAX; h++) {
                if (move == currentMoves[h]) {
                    break;
                }
            }

            if (h == LEARNED_MOVES_MAX) {
                for (h = 0; h < j; h++) {
                    if (reminderMoves[h] == move) {
                        break;
                    }
                }

                if (h == j) {
                    reminderMoves[j] = move;
                    j++;
                }
            }
        }
    }
""",
        "reminder traversal",
    )

    replace_once(
        speciesproc_c,
        """        result.data.entries[result.size].move  = (u16)(dp_u16(dp_lookup(move, "enum Move")) & maxbit(9));
        result.data.entries[result.size].level = (u16)(dp_u8(level) & maxbit(7));
        result.size++;
    }

    result.data.entries[result.size].move  = (u16)UINT16_MAX & maxbit(9);
    result.data.entries[result.size].level = (u16)UINT16_MAX & maxbit(7);
    result.size++;
""",
        """        result.data.entries[result.size].move    = dp_u16(dp_lookup(move, "enum Move"));
        result.data.entries[result.size].level   = dp_u8(level);
        result.data.entries[result.size].padding = 0;
        result.size++;
    }

    result.data.entries[result.size].move    = UINT16_MAX;
    result.data.entries[result.size].level   = UINT8_MAX;
    result.data.entries[result.size].padding = UINT8_MAX;
    result.size++;
""",
        "speciesproc learnset packing",
    )

    # Final safety audit: the old 9-bit learnset masks must be gone from the
    # only gameplay paths that interpreted WOTBL entries.
    for path in (pokemon_c, reminder_c, speciesproc_c):
        text = path.read_text()
        for forbidden in ("0xFE00", "0xfe00", "0x1FF", "0x1ff"):
            if forbidden in text and path.name in {"pokemon.c", "move_reminder_data.c"}:
                raise SystemExit(f"{path}: legacy WOTBL bit mask remains: {forbidden}")

    print("PT05C move-ID width expansion installed")
    print("WOTBL entry size: 4 bytes; move field: u16; level field: u8")


if __name__ == "__main__":
    main()
