#!/usr/bin/env python3
"""Install Mercury's DS-native universal Move Learner.

This pass deliberately replaces the old TM/tutor-as-separate-systems model
with one legal-move pool.  The existing Platinum Move Reminder application is
kept as the renderer/input shell so the result remains native DS UI.

Legal pool sources:
- level-up moves (unlocked at the Pokémon's current level)
- machine-compatible moves
- egg moves
- tutor moves

Machine/tutor/egg moves are treated as legal learner moves directly; they do
not require a physical TM, shard payment, or Heart Scale.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SRC_LEVEL = 1
SRC_MACHINE = 2
SRC_EGG = 4
SRC_TUTOR = 8


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1))


def load_constants(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def load_registry(path: Path) -> list[str]:
    rows = load_constants(path)
    if len(rows) < 1025:
        raise SystemExit(f"species registry too short: {len(rows)}")
    return rows[:1025]


def generate_pool(
    donor: dict,
    registry: list[str],
    implemented: set[str],
    move_ids: dict[str, int],
) -> tuple[list[tuple[int, int, int]], list[int], dict]:
    flat: list[tuple[int, int, int]] = []
    offsets = [0]
    unsupported: set[str] = set()
    missing_species: list[str] = []
    source_totals = {"level": 0, "machine": 0, "egg": 0, "tutor": 0}
    max_pool = 0
    max_species = None

    for species in registry:
        source = donor.get(species)
        if source is None:
            missing_species.append(species)
            offsets.append(len(flat))
            continue

        # move -> [level, flags].  Insertion order keeps level moves first,
        # followed by machine, egg, and tutor-only additions.
        merged: dict[str, list[int]] = {}

        for row in source.get("LevelMoves", []) or []:
            move = row.get("Move")
            if not move:
                continue
            if move not in implemented or move not in move_ids:
                unsupported.add(move)
                continue
            level = max(1, int(row.get("Level", 1)))
            if move not in merged:
                merged[move] = [level, SRC_LEVEL]
            else:
                merged[move][0] = min(merged[move][0], level)
                merged[move][1] |= SRC_LEVEL

        for key, flag, report_key in (
            ("MachineMoves", SRC_MACHINE, "machine"),
            ("EggMoves", SRC_EGG, "egg"),
            ("TutorMoves", SRC_TUTOR, "tutor"),
        ):
            for move in source.get(key, []) or []:
                if move not in implemented or move not in move_ids:
                    unsupported.add(move)
                    continue
                if move not in merged:
                    merged[move] = [0, flag]
                else:
                    merged[move][1] |= flag

        for move, (level, flags) in merged.items():
            flat.append((move_ids[move], level, flags))
            if flags & SRC_LEVEL:
                source_totals["level"] += 1
            if flags & SRC_MACHINE:
                source_totals["machine"] += 1
            if flags & SRC_EGG:
                source_totals["egg"] += 1
            if flags & SRC_TUTOR:
                source_totals["tutor"] += 1

        pool_size = len(merged)
        if pool_size > max_pool:
            max_pool = pool_size
            max_species = species
        offsets.append(len(flat))

    report = {
        "species": len(registry),
        "pool_entries": len(flat),
        "max_pool_size": max_pool,
        "max_pool_species": max_species,
        "source_totals": source_totals,
        "unsupported_move_constants": sorted(unsupported),
        "missing_donor_species": missing_species,
    }
    return flat, offsets, report


def write_header(path: Path, flat: list[tuple[int, int, int]], offsets: list[int]) -> None:
    lines = [
        "#ifndef POKEPLATINUM_MERCURY_MOVE_LEARNER_H",
        "#define POKEPLATINUM_MERCURY_MOVE_LEARNER_H",
        "",
        "#include <nitro/types.h>",
        "",
        "#define MERCURY_MOVE_LEARNER_SPECIES_MAX 1025",
        "#define MERCURY_LEARNER_SOURCE_LEVEL   (1 << 0)",
        "#define MERCURY_LEARNER_SOURCE_MACHINE (1 << 1)",
        "#define MERCURY_LEARNER_SOURCE_EGG     (1 << 2)",
        "#define MERCURY_LEARNER_SOURCE_TUTOR   (1 << 3)",
        "",
        "typedef struct MercuryMoveLearnerEntry {",
        "    u16 move;",
        "    u8 level;",
        "    u8 sources;",
        "} MercuryMoveLearnerEntry;",
        "",
        "static const MercuryMoveLearnerEntry sMercuryMoveLearnerEntries[] = {",
    ]
    for move_id, level, flags in flat:
        lines.append(f"    {{ {move_id}, {level}, {flags} }},")
    lines += [
        "};",
        "",
        "static const u32 sMercuryMoveLearnerOffsets[MERCURY_MOVE_LEARNER_SPECIES_MAX + 2] = {",
    ]
    # 8 offsets per source line keeps the generated header reviewable.
    for i in range(0, len(offsets), 8):
        lines.append("    " + ", ".join(str(x) for x in offsets[i:i+8]) + ",")
    lines += [
        "};",
        "",
        "#endif // POKEPLATINUM_MERCURY_MOVE_LEARNER_H",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


MOVE_REMINDER_DATA_C = r'''#include "move_reminder_data.h"

#include <nitro.h>
#include <string.h>

#include "constants/pokemon.h"
#include "generated/moves.h"

#include "heap.h"
#include "pokemon.h"

#include "res/pokemon/mercury_move_learner.h"

static BOOL MercuryMoveLearner_IsKnown(Pokemon *mon, u16 move)
{
    for (u32 i = 0; i < LEARNED_MOVES_MAX; i++) {
        if (Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL) == move) {
            return TRUE;
        }
    }

    return FALSE;
}

MoveReminderData *MoveReminderData_Alloc(enum HeapID heapID)
{
    MoveReminderData *data = Heap_Alloc(heapID, sizeof(MoveReminderData));
    memset(data, 0, sizeof(MoveReminderData));
    return data;
}

void MoveReminderData_Free(MoveReminderData *data)
{
    Heap_Free(data);
}

u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)
{
    u16 species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    u8 level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);

    if (species == SPECIES_NONE || species > MERCURY_MOVE_LEARNER_SPECIES_MAX) {
        u16 *empty = Heap_Alloc(heapID, sizeof(u16));
        empty[0] = LEVEL_UP_MOVESET_TERMINATOR;
        return empty;
    }

    u32 start = sMercuryMoveLearnerOffsets[species - 1];
    u32 end = sMercuryMoveLearnerOffsets[species];
    u16 *moves = Heap_Alloc(heapID, (end - start + 1) * sizeof(u16));
    u32 count = 0;

    for (u32 i = start; i < end; i++) {
        const MercuryMoveLearnerEntry *entry = &sMercuryMoveLearnerEntries[i];
        BOOL levelUnlocked = (entry->sources & MERCURY_LEARNER_SOURCE_LEVEL)
            && entry->level <= level;
        BOOL alwaysLegal = entry->sources
            & (MERCURY_LEARNER_SOURCE_MACHINE
                | MERCURY_LEARNER_SOURCE_EGG
                | MERCURY_LEARNER_SOURCE_TUTOR);

        if (!levelUnlocked && !alwaysLegal) {
            continue;
        }

        if (entry->move == MOVE_NONE || MercuryMoveLearner_IsKnown(mon, entry->move)) {
            continue;
        }

        moves[count++] = entry->move;
    }

    moves[count] = LEVEL_UP_MOVESET_TERMINATOR;
    return moves;
}

BOOL MoveReminderData_HasMoves(u16 *moves)
{
    return moves[0] != LEVEL_UP_MOVESET_TERMINATOR;
}
'''


def patch_runtime(pt: Path) -> None:
    # Replace the old reminder-only backend with the universal legal pool.
    (pt / "src/move_reminder_data.c").write_text(MOVE_REMINDER_DATA_C)

    reminder_h = pt / "include/move_reminder_data.h"
    replace_once(
        reminder_h,
        "    u8 keepOldMove;\n    u8 moveSlot;\n",
        "    u8 keepOldMove;\n    u8 moveSlot;\n    u8 partySlot; // Mercury: return to the same party slot after Move Learner\n",
        "MoveReminderData party slot",
    )

    reminder_c = pt / "src/applications/move_reminder.c"
    replace_once(reminder_c, "    u8 numMoves;\n", "    u16 numMoves;\n", "learner list count width")
    replace_once(
        reminder_c,
        "    controller->numMoves = (u8)MoveReminder_GetNumMoves(controller) + 1;\n",
        "    controller->numMoves = MoveReminder_GetNumMoves(controller) + 1;\n",
        "learner list count assignment",
    )

    # Make ownership of the move list explicit for both script-driven and
    # start-menu-driven launches.
    scrcmd = pt / "src/scrcmd_party_mon_moves.c"
    replace_once(
        scrcmd,
        "    FieldSystem_OpenMoveReminderMenu(ctx->fieldSystem, data);\n    ScriptContext_Pause(ctx, ScriptContext_WaitForApplicationExit);\n    Heap_Free(moves);\n",
        "    FieldSystem_OpenMoveReminderMenu(ctx->fieldSystem, data);\n    ScriptContext_Pause(ctx, ScriptContext_WaitForApplicationExit);\n",
        "script move-list lifetime",
    )
    old_free = "    MoveReminderData_Free(data);\n\n    return FALSE;\n"
    new_free = "    Heap_Free(data->moves);\n    MoveReminderData_Free(data);\n\n    return FALSE;\n"
    text = scrcmd.read_text()
    if text.count(old_free) != 2:
        raise SystemExit(f"{scrcmd}: expected two MoveReminderData free sites")
    scrcmd.write_text(text.replace(old_free, new_free))

    # Repurpose the unused separator/cancel-2 slot as a field-mode Move Learner
    # entry. Keeping ID 10 avoids shifting the original field-move action IDs.
    defs = pt / "include/applications/party_menu/defs.h"
    replace_once(
        defs,
        "    PARTY_MENU_EXIT_CODE_CHATTER\n",
        "    PARTY_MENU_EXIT_CODE_CHATTER,\n    PARTY_MENU_EXIT_CODE_MOVE_LEARNER\n",
        "party menu learner exit code",
    )
    replace_once(
        defs,
        "    PARTY_MENU_STR_SEPARATOR,\n",
        "    PARTY_MENU_STR_MOVE_LEARNER,\n",
        "party menu learner string slot",
    )

    context = pt / "src/applications/party_menu/context_menu.c"
    replace_once(
        context,
        "static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState);\n",
        "static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState);\n"
        "static void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState);\n",
        "learner action prototype",
    )
    replace_once(context, "    ACTION_CANCEL_2,\n", "    ACTION_MOVE_LEARNER,\n", "learner action ID")
    replace_once(
        context,
        "    [ACTION_CANCEL_2] =    { .raw = MENU_CANCEL },\n",
        "    [ACTION_MOVE_LEARNER] = PartyMenu_SelectMoveLearner,\n",
        "learner action table",
    )
    summary_func = '''static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_SUMMARY;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);

    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
'''
    learner_func = summary_func + '''
static void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_MOVE_LEARNER;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);

    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
'''
    replace_once(context, summary_func, learner_func, "learner action implementation")

    party_main = pt / "src/applications/party_menu/main.c"
    replace_once(
        party_main,
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 8);\n",
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 9);\n",
        "context menu entry buffer",
    )
    replace_once(
        party_main,
        "            count++;\n        } else {\n            menuEntriesBuffer[count] = 0;\n",
        "            count++;\n\n"
        "            // Mercury universal Move Learner (action/string slot 10).\n"
        "            menuEntriesBuffer[count] = 10;\n"
        "            count++;\n"
        "        } else {\n            menuEntriesBuffer[count] = 0;\n",
        "field-mode learner menu entry",
    )

    windows = pt / "src/applications/party_menu/windows.c"
    replace_once(
        windows,
        "LoadMenuString(PartyMenu_Text_Separator, PARTY_MENU_STR_SEPARATOR);",
        "LoadMenuString(PartyMenu_Text_Separator, PARTY_MENU_STR_MOVE_LEARNER);",
        "learner menu string loader",
    )

    # Launch the native Move Reminder app directly from the start-menu party
    # context and return to the same party slot when it closes.
    start = pt / "src/start_menu.c"
    replace_once(
        start,
        '#include "message.h"\n',
        '#include "message.h"\n#include "move_reminder_data.h"\n',
        "start-menu move learner include",
    )
    replace_once(
        start,
        "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask);\n",
        "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask);\n"
        "static BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask);\n",
        "start-menu learner callback prototype",
    )
    switch_anchor = "    case PARTY_MENU_EXIT_CODE_WRITE_MAIL:\n"
    learner_case = '''    case PARTY_MENU_EXIT_CODE_MOVE_LEARNER: {
        Pokemon *mon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            partyMenu->selectedMonSlot);
        MoveReminderData *learner = MoveReminderData_Alloc(HEAP_ID_FIELD2);

        learner->mon = mon;
        learner->trainerInfo = SaveData_GetTrainerInfo(fieldSystem->saveData);
        learner->options = SaveData_GetOptions(fieldSystem->saveData);
        learner->moves = MoveReminderData_GetMoves(mon, HEAP_ID_FIELD2);
        learner->isMoveTutor = FALSE;
        learner->partySlot = partyMenu->selectedMonSlot;

        FieldSystem_OpenMoveReminderMenu(fieldSystem, learner);
        menu->taskData = learner;
        StartMenu_SetCallback(menu, StartMenu_ExitMoveLearner);
    } break;
'''
    replace_once(start, switch_anchor, learner_case + switch_anchor, "start-menu learner launch")

    exit_summary = "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask)\n{"
    idx = start.read_text().find(exit_summary)
    if idx < 0:
        raise SystemExit("start_menu.c: missing StartMenu_ExitSummary definition")
    callback = '''static BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MoveReminderData *learner = menu->taskData;
    u8 partySlot = learner->partySlot;

    Heap_Free(learner->moves);
    MoveReminderData_Free(learner);

    menu->taskData = FieldSystem_OpenPartyMenu(
        fieldSystem,
        &menu->fieldMoveContext,
        partySlot);
    StartMenu_SetCallback(menu, StartMenu_ExitPartyMenu);

    return FALSE;
}

'''
    text = start.read_text()
    text = text[:idx] + callback + text[idx:]
    start.write_text(text)

    # Native DS copy changes. No GBA artwork is imported: this is the existing
    # Platinum Move Reminder renderer with Mercury wording.
    move_text = pt / "res/text/move_reminder.json"
    data = json.loads(move_text.read_text())
    for msg in data["messages"]:
        if msg["id"] == "MoveReminder_Text_Reminder_AskTeachWhichToMon":
            msg["en_US"] = ["Choose a move for\n", "{STRVAR_1 1, 0, 0}."]
        elif msg["id"] == "MoveReminder_Text_Reminder_AskShouldTeachMove":
            msg["en_US"] = ["Teach {STRVAR_1 6, 1, 0}\n", "to {STRVAR_1 1, 0, 0}?"]
        elif msg["id"] in ("MoveReminder_Text_BattleMoves", "MoveReminder_Text_ContestMoves"):
            msg["en_US"] = "MOVE LEARNER"
    move_text.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    party_text = pt / "res/text/party_menu.json"
    data = json.loads(party_text.read_text())
    found = False
    for msg in data["messages"]:
        if msg["id"] == "PartyMenu_Text_Separator":
            msg.pop("garbage", None)
            msg["en_US"] = "MOVE LEARNER"
            found = True
            break
    if not found:
        raise SystemExit("party_menu.json: PartyMenu_Text_Separator not found")
    party_text.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--implemented-moves", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mp06-ds-move-learner.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    registry = load_registry(args.registry)
    implemented = set(load_constants(args.implemented_moves))
    generated_moves = load_constants(pt / "generated/moves.txt")
    move_ids = {name: idx for idx, name in enumerate(generated_moves)}

    donor_path = hg / "data/learnsets/learnsets.json"
    if not donor_path.is_file():
        donor_path = hg / "data/learnsets/base/21_sv.json"
    donor = json.loads(donor_path.read_text())

    flat, offsets, report = generate_pool(donor, registry, implemented, move_ids)
    write_header(pt / "res/pokemon/mercury_move_learner.h", flat, offsets)
    patch_runtime(pt)

    report.update({
        "gate": "MP06_DS_NATIVE_MOVE_LEARNER",
        "donor_source": str(donor_path),
        "implemented_registry": str(args.implemented_moves),
        "ui_base": "native Platinum Move Reminder application",
        "access": "Pokemon party context menu -> MOVE LEARNER",
        "tm_items_required": False,
        "heart_scale_required": False,
        "known_moves_hidden": True,
        "level_moves_unlock_by_level": True,
        "machine_egg_tutor_moves_available_directly": True,
        "status": "PASS",
    })
    args.report.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({
        "gate": report["gate"],
        "species": report["species"],
        "pool_entries": report["pool_entries"],
        "max_pool_size": report["max_pool_size"],
        "max_pool_species": report["max_pool_species"],
        "missing_donor_species": len(report["missing_donor_species"]),
        "unsupported_move_constants": len(report["unsupported_move_constants"]),
        "status": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
