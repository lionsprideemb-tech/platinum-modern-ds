#!/usr/bin/env python3
"""Expand Platinum's level-up learnset encoding for modern move IDs.

Vanilla Platinum packs each learnset entry into 16 bits:
    move: 9 bits + level: 7 bits

That caps level-up move IDs at 511, while the pinned HG-Engine donor contains
923 canonical moves through Gen 9. Mercury keeps Pokemon save/battle move IDs
as u16 and expands only the level-up learnset NARC entry to four bytes:
    u16 move + u8 level + u8 padding

This patch is deliberately narrow and reproducible. It updates the runtime,
move reminder, public function signature, and species data compiler together.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}\n--- needle ---\n{old}"
        )
    path.write_text(text.replace(old, new, 1))


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
        """typedef struct SpeciesLearnsetEntry {
    u16 move : 9;
    u16 level : 7;
} SpeciesLearnsetEntry;""",
        """typedef struct SpeciesLearnsetEntry {
    u16 move;
    u8 level;
    u8 padding;
} SpeciesLearnsetEntry;""",
    )

    replace_once(
        pokemon_h,
        """ * @param[out] monLevelUpMoves Pointer to a u16 array to store the move table
 */
void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, u16 *monLevelUpMoves);""",
        """ * @param[out] monLevelUpMoves Pointer to a SpeciesLearnsetEntry array to store the move table
 */
void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, SpeciesLearnsetEntry *monLevelUpMoves);""",
    )

    replace_once(
        pokemon_c,
        """void BoxPokemon_SetDefaultMoves(BoxPokemon *boxMon)
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
}""",
        """void BoxPokemon_SetDefaultMoves(BoxPokemon *boxMon)
{
    BOOL reencrypt; // must pre-declare to match
    SpeciesLearnsetEntry *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    reencrypt = BoxPokemon_EnterDecryptionContext(boxMon);

    u16 monSpecies = BoxPokemon_GetValue(boxMon, MON_DATA_SPECIES, NULL);
    int monForm = BoxPokemon_GetValue(boxMon, MON_DATA_FORM, NULL);
    u8 monLevel = BoxPokemon_GetLevel(boxMon);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    for (int i = 0; monLevelUpMoves[i].move != LEARNSET_SENTINEL_ENTRY; i++) {
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
}""",
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
}""",
        """u16 Pokemon_LevelUpMove(Pokemon *mon, int *index, u16 *moveID)
{
    u16 result = MOVE_NONE;
    SpeciesLearnsetEntry *monLevelUpMoves = Heap_Alloc(HEAP_ID_SYSTEM, sizeof(SpeciesLearnset));
    u16 monSpecies = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    int monForm = Pokemon_GetValue(mon, MON_DATA_FORM, NULL);
    u8 monLevel = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);

    Pokemon_LoadLevelUpMovesOf(monSpecies, monForm, monLevelUpMoves);

    if (monLevelUpMoves[*index].move == LEARNSET_SENTINEL_ENTRY) {
        Heap_Free(monLevelUpMoves);
        return MOVE_NONE;
    }

    while (monLevelUpMoves[*index].level != monLevel) {
        (*index)++;
        if (monLevelUpMoves[*index].move == LEARNSET_SENTINEL_ENTRY) {
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
}""",
    )

    replace_once(
        pokemon_c,
        """void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, u16 *monLevelUpMoves)
{
    monSpecies = Pokemon_GetFormNarcIndex(monSpecies, monForm);
    NARC_ReadWholeMemberByIndexPair(monLevelUpMoves, NARC_INDEX_POKETOOL__PERSONAL__WOTBL, monSpecies);
}""",
        """void Pokemon_LoadLevelUpMovesOf(int monSpecies, int monForm, SpeciesLearnsetEntry *monLevelUpMoves)
{
    monSpecies = Pokemon_GetFormNarcIndex(monSpecies, monForm);
    NARC_ReadWholeMemberByIndexPair(monLevelUpMoves, NARC_INDEX_POKETOOL__PERSONAL__WOTBL, monSpecies);
}""",
    )

    reminder_c.write_text(
        reminder_c.read_text()
        .replace(
            """#define GET_LEVEL(move) ((move & 0xfe00) >> 9)
#define GET_MOVE(move)  ((move & 0x1ff) >> 0)

""",
            "",
            1,
        )
        .replace(
            """    u16 *levelUpMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));
    u16 *reminderMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));

    Pokemon_LoadLevelUpMovesOf(species, form, levelUpMoves);

    j = 0;

    for (i = 0; i < MAX_NUMBER_REMINDER_MOVES; i++) {
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
    }""",
            """    SpeciesLearnsetEntry *levelUpMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(SpeciesLearnsetEntry));
    u16 *reminderMoves = Heap_Alloc(heapID, MAX_NUMBER_REMINDER_MOVES * sizeof(u16));

    Pokemon_LoadLevelUpMovesOf(species, form, levelUpMoves);

    j = 0;

    for (i = 0; i < MAX_NUMBER_REMINDER_MOVES; i++) {
        if (levelUpMoves[i].move == LEVEL_UP_MOVESET_TERMINATOR) {
            reminderMoves[j] = LEVEL_UP_MOVESET_TERMINATOR;
            break;
        } else if (levelUpMoves[i].level > level) {
            continue;
        } else {
            u16 levelUpMove = levelUpMoves[i].move;

            for (h = 0; h < LEARNED_MOVES_MAX; h++) {
                if (levelUpMove == currentMoves[h]) {
                    break;
                }
            }

            if (h == LEARNED_MOVES_MAX) {
                for (h = 0; h < j; h++) {
                    if (reminderMoves[h] == levelUpMove) {
                        break;
                    }
                }

                if (h == j) {
                    reminderMoves[j] = levelUpMove;
                    j++;
                }
            }
        }
    }""",
            1,
        )
    )

    reminder_text = reminder_c.read_text()
    if "GET_LEVEL" in reminder_text or "GET_MOVE" in reminder_text:
        raise SystemExit("move reminder still contains packed learnset macros")
    if "SpeciesLearnsetEntry *levelUpMoves" not in reminder_text:
        raise SystemExit("move reminder replacement did not apply")

    replace_once(
        speciesproc_c,
        """        result.data.entries[result.size].move  = (u16)(dp_u16(dp_lookup(move, "enum Move")) & maxbit(9));
        result.data.entries[result.size].level = (u16)(dp_u8(level) & maxbit(7));
        result.size++;
    }

    result.data.entries[result.size].move  = (u16)UINT16_MAX & maxbit(9);
    result.data.entries[result.size].level = (u16)UINT16_MAX & maxbit(7);
    result.size++;""",
        """        result.data.entries[result.size].move    = dp_u16(dp_lookup(move, "enum Move"));
        result.data.entries[result.size].level   = dp_u8(level);
        result.data.entries[result.size].padding = 0;
        result.size++;
    }

    result.data.entries[result.size].move    = UINT16_MAX;
    result.data.entries[result.size].level   = UINT8_MAX;
    result.data.entries[result.size].padding = 0;
    result.size++;""",
    )

    # Final invariants: the old 9-bit learnset masks must no longer remain in
    # the two runtime consumers or the species compiler.
    for path in (pokemon_c, reminder_c, speciesproc_c):
        text = path.read_text()
        for marker in ("0xFE00", "0x1FF", "maxbit(9)"):
            if marker in text and path.name in {"pokemon.c", "move_reminder_data.c"}:
                raise SystemExit(f"{path}: legacy move-width marker remains: {marker}")

    print("PT05C move-capacity patch applied: level-up learnsets now store u16 move IDs.")


if __name__ == "__main__":
    main()
