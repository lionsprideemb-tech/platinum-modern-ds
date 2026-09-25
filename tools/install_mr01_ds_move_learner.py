#!/usr/bin/env python3
"""Install Mercury's DS-native universal Move Learner.

This pass deliberately reuses Platinum's native Move Reminder application for
rendering, move details, category/type icons, scrolling, confirmation, and move
replacement. The backend is replaced with a generated legal-move pool built
from the pinned HG-Engine learnsets, and the field party menu receives a direct
MOVE LEARNER action.

The generated pool combines:
- level-up moves (respecting the Pokémon's current level),
- egg moves,
- machine moves,
- tutor moves.

Only moves present in the current Mercury implemented-move registry are exposed.
This lets Mercury retire TM compatibility as a required teaching path without
silently exposing moves whose battle mechanics are still deferred.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_POOL_MOVES = 240
MOVE_SOURCE_LEVEL = 0
MOVE_SOURCE_EGG = 1
MOVE_SOURCE_MACHINE = 2
MOVE_SOURCE_TUTOR = 3


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def load_registry(path: Path) -> list[str]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            rows.append(line)
    if len(rows) < 1025:
        raise SystemExit(f"species registry too short: {len(rows)}")
    return rows


def load_constants(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def species_dir(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def dedupe(rows: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    seen: set[str] = set()
    out: list[tuple[str, int, int]] = []
    for move, level, source in rows:
        if move in seen:
            continue
        seen.add(move)
        out.append((move, level, source))
    return out


def fallback_pool_from_platinum(pt: Path, species_const: str) -> list[tuple[str, int, int]]:
    path = pt / "res/pokemon" / species_dir(species_const) / "data.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    ls = data.get("learnset", {})
    rows: list[tuple[str, int, int]] = []
    for level, move in ls.get("by_level", []) or []:
        rows.append((move, max(1, int(level)), MOVE_SOURCE_LEVEL))
    for move in ls.get("egg_moves", []) or data.get("egg_moves", []) or []:
        rows.append((move, 1, MOVE_SOURCE_EGG))
    for move in ls.get("by_tutor", []) or []:
        rows.append((move, 1, MOVE_SOURCE_TUTOR))

    # Native Platinum stores TM compatibility as machine names. Resolve those
    # straight to moves here so runtime no longer needs the TM bitfield.
    machine_map: dict[str, str] = {}
    items_dir = pt / "res/items/data"
    for item_path in list(items_dir.glob("tm*.json")) + list(items_dir.glob("hm*.json")):
        try:
            payload = json.loads(item_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        move = payload.get("teachesMove")
        if move:
            machine_map[item_path.stem.upper()] = move
    for machine in ls.get("by_tm", []) or []:
        move = machine_map.get(str(machine).upper())
        if move:
            rows.append((move, 1, MOVE_SOURCE_MACHINE))
    return rows


def build_pools(
    pt: Path,
    hg: Path,
    registry: list[str],
    implemented: set[str],
) -> tuple[list[list[tuple[str, int, int]]], dict]:
    donor_path = hg / "data/learnsets/learnsets.json"
    if not donor_path.is_file():
        donor_path = hg / "data/learnsets/base/21_sv.json"
    donor = json.loads(donor_path.read_text(encoding="utf-8"))

    pools: list[list[tuple[str, int, int]]] = [[] for _ in range(1026)]
    counts = {"level": 0, "egg": 0, "machine": 0, "tutor": 0}
    unsupported: set[str] = set()
    missing_donor: list[str] = []
    trimmed: dict[str, int] = {}

    for dex in range(1, 1026):
        species_const = registry[dex - 1]
        src = donor.get(species_const)
        rows: list[tuple[str, int, int]] = []

        if src:
            for row in src.get("LevelMoves", []) or []:
                move = row.get("Move")
                if move:
                    rows.append((move, max(1, int(row.get("Level", 1))), MOVE_SOURCE_LEVEL))
            for move in src.get("EggMoves", []) or []:
                rows.append((move, 1, MOVE_SOURCE_EGG))
            for move in src.get("MachineMoves", []) or []:
                rows.append((move, 1, MOVE_SOURCE_MACHINE))
            for move in src.get("TutorMoves", []) or []:
                rows.append((move, 1, MOVE_SOURCE_TUTOR))
        else:
            missing_donor.append(species_const)
            rows = fallback_pool_from_platinum(pt, species_const)

        filtered: list[tuple[str, int, int]] = []
        for move, level, source in dedupe(rows):
            if move in implemented:
                filtered.append((move, level, source))
            else:
                unsupported.add(move)

        # Last-resort compatibility fallback: use the live Platinum species
        # data if donor filtering somehow leaves a species with no legal move.
        if not filtered:
            for move, level, source in dedupe(fallback_pool_from_platinum(pt, species_const)):
                if move in implemented:
                    filtered.append((move, level, source))

        if len(filtered) > MAX_POOL_MOVES:
            trimmed[species_const] = len(filtered) - MAX_POOL_MOVES
            filtered = filtered[:MAX_POOL_MOVES]

        pools[dex] = filtered
        for _, _, source in filtered:
            if source == MOVE_SOURCE_LEVEL:
                counts["level"] += 1
            elif source == MOVE_SOURCE_EGG:
                counts["egg"] += 1
            elif source == MOVE_SOURCE_MACHINE:
                counts["machine"] += 1
            else:
                counts["tutor"] += 1

    report = {
        "species_with_pools": sum(bool(p) for p in pools),
        "pool_entries": sum(len(p) for p in pools),
        "source_entries": counts,
        "max_pool_size": max(len(p) for p in pools),
        "max_pool_capacity": MAX_POOL_MOVES,
        "missing_donor_species": missing_donor,
        "trimmed_species": trimmed,
        "unsupported_move_constants": sorted(unsupported),
    }
    return pools, report


def emit_pool_source(pt: Path, registry: list[str], pools: list[list[tuple[str, int, int]]]) -> None:
    header = pt / "include/mercury_move_learner_data.h"
    source = pt / "src/mercury_move_learner_data.c"

    header.write_text(
        """#ifndef POKEPLATINUM_MERCURY_MOVE_LEARNER_DATA_H
#define POKEPLATINUM_MERCURY_MOVE_LEARNER_DATA_H

#include <nitro/types.h>

enum MercuryMoveLearnerSource {
    MERCURY_MOVE_SOURCE_LEVEL = 0,
    MERCURY_MOVE_SOURCE_EGG,
    MERCURY_MOVE_SOURCE_MACHINE,
    MERCURY_MOVE_SOURCE_TUTOR,
};

typedef struct MercuryMoveLearnerEntry {
    u16 move;
    u8 unlockLevel;
    u8 source;
} MercuryMoveLearnerEntry;

typedef struct MercuryMoveLearnerPool {
    const MercuryMoveLearnerEntry *entries;
    u16 count;
} MercuryMoveLearnerPool;

const MercuryMoveLearnerPool *MercuryMoveLearner_GetPool(u16 species);

#endif // POKEPLATINUM_MERCURY_MOVE_LEARNER_DATA_H
""",
        encoding="utf-8",
    )

    lines = [
        '#include "mercury_move_learner_data.h"',
        "",
        '#include "generated/moves.h"',
        "",
        "static const MercuryMoveLearnerEntry sEmptyPool[] = {",
        "    { MOVE_NONE, 1, MERCURY_MOVE_SOURCE_LEVEL },",
        "};",
        "",
    ]

    for dex in range(1, 1026):
        entries = pools[dex]
        if not entries:
            continue
        lines.append(f"static const MercuryMoveLearnerEntry sPool_{dex:04d}[] = {{")
        for move, level, source in entries:
            source_name = (
                "MERCURY_MOVE_SOURCE_LEVEL" if source == MOVE_SOURCE_LEVEL else
                "MERCURY_MOVE_SOURCE_EGG" if source == MOVE_SOURCE_EGG else
                "MERCURY_MOVE_SOURCE_MACHINE" if source == MOVE_SOURCE_MACHINE else
                "MERCURY_MOVE_SOURCE_TUTOR"
            )
            lines.append(f"    {{ {move}, {level}, {source_name} }},")
        lines.append("};")
        lines.append("")

    lines += [
        "static const MercuryMoveLearnerPool sPools[1026] = {",
        "    [0] = { sEmptyPool, 0 },",
    ]
    for dex in range(1, 1026):
        if pools[dex]:
            lines.append(f"    [{dex}] = {{ sPool_{dex:04d}, {len(pools[dex])} }},")
        else:
            lines.append(f"    [{dex}] = {{ sEmptyPool, 0 }},")
    lines += [
        "};",
        "",
        "const MercuryMoveLearnerPool *MercuryMoveLearner_GetPool(u16 species)",
        "{",
        "    if (species >= 1026) {",
        "        return &sPools[0];",
        "    }",
        "",
        "    return &sPools[species];",
        "}",
        "",
    ]
    source.write_text("\n".join(lines), encoding="utf-8")

    meson = pt / "src/meson.build"
    replace_once(
        meson,
        "    'move_reminder_data.c',\n",
        "    'move_reminder_data.c',\n    'mercury_move_learner_data.c',\n",
        "move learner source in meson",
    )


def patch_move_backend(pt: Path) -> None:
    path = pt / "src/move_reminder_data.c"
    replace_once(
        path,
        '#include "heap.h"\n#include "pokemon.h"\n',
        '#include "heap.h"\n#include "mercury_move_learner_data.h"\n#include "pokemon.h"\n',
        "move learner include",
    )

    start = path.read_text(encoding="utf-8")
    fn_start = start.index("u16 *MoveReminderData_GetMoves")
    fn_end = start.index("\nBOOL MoveReminderData_HasMoves", fn_start)
    old = start[fn_start:fn_end]
    new = """u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)
{
    u16 species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    u8 level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);
    const MercuryMoveLearnerPool *pool = MercuryMoveLearner_GetPool(species);

    u16 currentMoves[LEARNED_MOVES_MAX];
    for (u8 i = 0; i < LEARNED_MOVES_MAX; i++) {
        currentMoves[i] = Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);
    }

    u16 *moves = Heap_Alloc(heapID, (240 + 1) * sizeof(u16));
    u16 count = 0;

    for (u16 i = 0; i < pool->count && count < 240; i++) {
        const MercuryMoveLearnerEntry *entry = &pool->entries[i];

        if (entry->source == MERCURY_MOVE_SOURCE_LEVEL && entry->unlockLevel > level) {
            continue;
        }

        BOOL alreadyKnown = FALSE;
        for (u8 slot = 0; slot < LEARNED_MOVES_MAX; slot++) {
            if (currentMoves[slot] == entry->move) {
                alreadyKnown = TRUE;
                break;
            }
        }
        if (alreadyKnown == TRUE) {
            continue;
        }

        moves[count++] = entry->move;
    }

    moves[count] = LEVEL_UP_MOVESET_TERMINATOR;
    return moves;
}
"""
    path.write_text(start[:fn_start] + new + start[fn_end:], encoding="utf-8")


def set_message(data: dict, msg_id: str, value) -> None:
    for msg in data["messages"]:
        if msg.get("id") == msg_id:
            msg.pop("garbage", None)
            msg["en_US"] = value
            return
    raise SystemExit(f"missing message id {msg_id}")


def patch_move_learner_ui(pt: Path) -> None:
    text_path = pt / "res/text/move_reminder.json"
    data = json.loads(text_path.read_text(encoding="utf-8"))

    universal = {
        "MoveReminder_Text_Reminder_AskTeachWhichToMon": [
            "Choose a move for\n", "{STRVAR_1 1, 0, 0}."
        ],
        "MoveReminder_Text_Reminder_AskShouldTeachMove": [
            "Teach {STRVAR_1 6, 1, 0}\n", "to {STRVAR_1 1, 0, 0}?"
        ],
        "MoveReminder_Text_Reminder_AskGiveUpTeachingMon": [
            "Exit the Move Learner\n", "without teaching a move?"
        ],
        "MoveReminder_Text_Reminder_LearnedMoveNoFanfare": [
            "{STRVAR_1 1, 0, 0} learned\n", "{STRVAR_1 6, 1, 0}.\r"
        ],
        "MoveReminder_Text_Reminder_AskMoreThanFourMoves": [
            "{STRVAR_1 1, 0, 0} already knows four moves.\r",
            "Replace one with\n",
            "{STRVAR_1 6, 1, 0}?"
        ],
        "MoveReminder_Text_Reminder_LearnedMoveFanfare": [
            "{STRVAR_1 1, 0, 0} learned\n", "{STRVAR_1 6, 1, 0}.{WAIT 4}{WAIT 2}\r"
        ],
        "MoveReminder_Text_Reminder_AskStopTryingToTeachMove": [
            "Stop trying to teach\n", "{STRVAR_1 6, 1, 0}?"
        ],
        "MoveReminder_Text_Reminder_MonDidNotLearnMove": [
            "{STRVAR_1 1, 0, 0} did not learn\n", "{STRVAR_1 6, 1, 0}.\r"
        ],
        "MoveReminder_Text_Reminder_AskForgetThisMove": [
            "Replace this move with\n", "{STRVAR_1 6, 0, 0}?"
        ],
    }
    for msg_id, value in universal.items():
        set_message(data, msg_id, value)

    # Make the second legacy message family identical so scripted tutors and
    # direct party-menu access both receive Mercury wording.
    for base_id, value in list(universal.items()):
        tutor_id = base_id.replace("_Reminder_", "_Tutor_")
        try:
            set_message(data, tutor_id, value)
        except SystemExit:
            pass

    set_message(data, "MoveReminder_Text_BattleMoves", "MOVE LEARNER")
    set_message(data, "MoveReminder_Text_ContestMoves", "MOVE INFO")
    text_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    app = pt / "src/applications/move_reminder.c"
    replace_once(
        app,
        """    if (JOY_NEW(PAD_KEY_LEFT | PAD_KEY_RIGHT)) {
        Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
        controller->data->showingContest ^= 1;
        MoveReminder_DrawMovesInfo(controller);
        return MOVE_REMINDER_STATE_PROCESS_MAIN_INPUT;
    }

""",
        """    // Mercury keeps the primary battle-data view fixed. Left/right are
    // reserved for future source filters (Level/Egg/Machine/Tutor).
    controller->data->showingContest = 0;

""",
        "disable contest toggle",
    )


def patch_party_menu_access(pt: Path) -> None:
    defs = pt / "include/applications/party_menu/defs.h"
    replace_once(
        defs,
        """    PARTY_MENU_EXIT_CODE_SWEET_SCENT,
    PARTY_MENU_EXIT_CODE_CHATTER
};
""",
        """    PARTY_MENU_EXIT_CODE_SWEET_SCENT,
    PARTY_MENU_EXIT_CODE_CHATTER,
    PARTY_MENU_EXIT_CODE_MOVE_LEARNER
};
""",
        "party menu exit code",
    )
    replace_once(
        defs,
        """    PARTY_MENU_STR_MOVE2,
    PARTY_MENU_STR_MOVE3,

    NUM_PARTY_MENU_STRS,
};
""",
        """    PARTY_MENU_STR_MOVE2,
    PARTY_MENU_STR_MOVE3,
    PARTY_MENU_STR_MOVE_LEARNER,

    NUM_PARTY_MENU_STRS,
};
""",
        "party menu move learner string",
    )

    party_text = pt / "res/text/party_menu.json"
    payload = json.loads(party_text.read_text(encoding="utf-8"))
    if not any(m.get("id") == "PartyMenu_Text_MoveLearner" for m in payload["messages"]):
        payload["messages"].append({
            "id": "PartyMenu_Text_MoveLearner",
            "en_US": "MOVE LEARNER",
        })
    party_text.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    windows = pt / "src/applications/party_menu/windows.c"
    replace_once(
        windows,
        """    LoadMenuString(PartyMenu_Text_ContextConfirm, PARTY_MENU_STR_CONFIRM);

#undef LoadMenuString
""",
        """    LoadMenuString(PartyMenu_Text_ContextConfirm, PARTY_MENU_STR_CONFIRM);
    LoadMenuString(PartyMenu_Text_MoveLearner, PARTY_MENU_STR_MOVE_LEARNER);

#undef LoadMenuString
""",
        "party menu string load",
    )
    replace_once(
        windows,
        """    for (u16 i = 0; i < numEntries; i++) {
        if (entries[i] >= PARTY_MENU_STR_MOVE0) {
            StringList_AddFromString(
                application->contextMenuChoices,
                application->menuStrings[PARTY_MENU_STR_MOVE0 + numFieldMoves],
                PartyMenu_GetAction(entries[i]));
            numFieldMoves++;
        } else {
""",
        """    for (u16 i = 0; i < numEntries; i++) {
        if (entries[i] == 0xFE) {
            StringList_AddFromString(
                application->contextMenuChoices,
                application->menuStrings[PARTY_MENU_STR_MOVE_LEARNER],
                PartyMenu_GetAction(32));
        } else if (entries[i] >= PARTY_MENU_STR_MOVE0 && entries[i] <= PARTY_MENU_STR_MOVE3) {
            StringList_AddFromString(
                application->contextMenuChoices,
                application->menuStrings[PARTY_MENU_STR_MOVE0 + numFieldMoves],
                PartyMenu_GetAction(entries[i]));
            numFieldMoves++;
        } else {
""",
        "party menu sentinel rendering",
    )

    context = pt / "src/applications/party_menu/context_menu.c"
    replace_once(
        context,
        "static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState);\n",
        "static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState);\nstatic void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState);\n",
        "move learner action prototype",
    )
    replace_once(
        context,
        """    ACTION_CANCEL_3,

    ACTION_MAX,
};
""",
        """    ACTION_CANCEL_3,
    ACTION_MOVE_LEARNER,

    ACTION_MAX,
};
""",
        "move learner action enum",
    )
    replace_once(
        context,
        """    [ACTION_CANCEL_3] =    { .raw = MENU_CANCEL },
};
""",
        """    [ACTION_CANCEL_3] =    { .raw = MENU_CANCEL },
    [ACTION_MOVE_LEARNER] = PartyMenu_SelectMoveLearner,
};
""",
        "move learner action table",
    )

    marker = """static void PartyMenu_SelectSummary(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_SUMMARY;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);
    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
"""
    replacement = marker + """
static void PartyMenu_SelectMoveLearner(PartyMenuApplication *application, int *partyMenuState)
{
    application->partyMenu->menuSelectionResult = PARTY_MENU_EXIT_CODE_MOVE_LEARNER;

    Menu_Free(application->contextMenu, NULL);
    StringList_Free(application->contextMenuChoices);
    *partyMenuState = PARTY_MENU_STATE_FADE_OUT;
}
"""
    replace_once(context, marker, replacement, "move learner action function")

    main = pt / "src/applications/party_menu/main.c"
    replace_once(
        main,
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 8);\n",
        "    v0 = Heap_Alloc(HEAP_ID_PARTY_MENU, 9);\n",
        "party context buffer expansion",
    )
    replace_once(
        main,
        """        if (application->partyMembers[application->currPartySlot].isEgg == FALSE) {
            for (i = 0; i < 4; i++) {
""",
        """        if (application->partyMembers[application->currPartySlot].isEgg == FALSE) {
            menuEntriesBuffer[count] = 0xFE; // Mercury MOVE LEARNER
            count++;

            for (i = 0; i < 4; i++) {
""",
        "party menu move learner entry",
    )

    move_data_h = pt / "include/move_reminder_data.h"
    replace_once(
        move_data_h,
        """    u8 keepOldMove;
    u8 moveSlot;
} MoveReminderData;
""",
        """    u8 keepOldMove;
    u8 moveSlot;
    u8 partySlot;
} MoveReminderData;
""",
        "move learner return party slot",
    )

    start_menu = pt / "src/start_menu.c"
    replace_once(
        start_menu,
        '#include "message.h"\n#include "narc.h"\n',
        '#include "message.h"\n#include "move_reminder_data.h"\n#include "narc.h"\n',
        "start menu move learner include",
    )
    replace_once(
        start_menu,
        "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask);\n",
        "static BOOL StartMenu_ExitSummary(FieldTask *fieldTask);\nstatic BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask);\n",
        "start menu callback prototype",
    )
    replace_once(
        start_menu,
        """    case PARTY_MENU_EXIT_CODE_OVERWRITE_MOVE_TM_HM:
""",
        """    case PARTY_MENU_EXIT_CODE_MOVE_LEARNER: {
        Pokemon *mon = Party_GetPokemonBySlotIndex(
            SaveData_GetParty(fieldSystem->saveData),
            partyMenu->selectedMonSlot);

        MoveReminderData *moveLearner = MoveReminderData_Alloc(HEAP_ID_FIELD2);
        moveLearner->mon = mon;
        moveLearner->trainerInfo = SaveData_GetTrainerInfo(fieldSystem->saveData);
        moveLearner->options = SaveData_GetOptions(fieldSystem->saveData);
        moveLearner->moves = MoveReminderData_GetMoves(mon, HEAP_ID_FIELD2);
        moveLearner->isMoveTutor = FALSE;
        moveLearner->partySlot = partyMenu->selectedMonSlot;

        menu->taskData = moveLearner;
        FieldSystem_OpenMoveReminderMenu(fieldSystem, moveLearner);
        StartMenu_SetCallback(menu, StartMenu_ExitMoveLearner);
    } break;
    case PARTY_MENU_EXIT_CODE_OVERWRITE_MOVE_TM_HM:
""",
        "start menu move learner launch",
    )

    callback_anchor = """static BOOL StartMenu_ExitSummary(FieldTask *fieldTask)
{
"""
    idx = start_menu.read_text(encoding="utf-8").index(callback_anchor)
    callback = """static BOOL StartMenu_ExitMoveLearner(FieldTask *fieldTask)
{
    FieldSystem *fieldSystem = FieldTask_GetFieldSystem(fieldTask);
    StartMenu *menu = FieldTask_GetEnv(fieldTask);
    MoveReminderData *moveLearner = menu->taskData;
    u8 partySlot = moveLearner->partySlot;

    Heap_Free(moveLearner->moves);
    MoveReminderData_Free(moveLearner);

    menu->taskData = FieldSystem_OpenPartyMenu(
        fieldSystem,
        &menu->fieldMoveContext,
        partySlot);
    StartMenu_SetCallback(menu, StartMenu_ExitPartyMenu);

    return FALSE;
}

"""
    text = start_menu.read_text(encoding="utf-8")
    text = text[:idx] + callback + text[idx:]
    start_menu.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--implemented-moves", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mercury-ds-move-learner.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    implemented = load_constants(args.implemented_moves)

    pools, report = build_pools(pt, hg, registry, implemented)
    emit_pool_source(pt, registry, pools)
    patch_move_backend(pt)
    patch_move_learner_ui(pt)
    patch_party_menu_access(pt)

    report.update({
        "gate": "MERCURY_DS_MOVE_LEARNER",
        "teaching_path": "party menu -> MOVE LEARNER",
        "ui_base": "native Platinum Move Reminder application",
        "tm_items_required": False,
        "level_up_unlocks_respect_current_level": True,
        "egg_machine_tutor_policy": "available through universal learner",
        "known_moves_hidden_from_selection": True,
        "battle_view": "type/category/power/accuracy/PP/description",
        "status": "PASS",
    })
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
