#!/usr/bin/env python3
"""Install Mercury Redux's DS-native universal Move Learner.

This deliberately avoids Platinum's TM/HM compatibility bitfields.  The
learner combines:
  * level-up moves the Pokémon has reached,
  * egg moves,
  * machine moves, and
  * tutor moves
from the pinned modern learnset donor, filtered to move effects currently
implemented by Mercury.

The presentation reuses Platinum's native Move Reminder application so the
result uses real DS windows, fonts, type icons, category icons, scrolling, PP,
power/accuracy, descriptions, and the native four-move replacement flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


MAX_POOL = 512
MAX_SPECIES = 1025


def load_registry(path: Path) -> list[str]:
    rows: list[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            rows.append(line)
    if len(rows) < MAX_SPECIES:
        raise SystemExit(f"canonical registry too short: {len(rows)}")
    return rows[:MAX_SPECIES]


def load_constants(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def iter_move_names(value: object) -> Iterable[str]:
    """Accept donor lists, Move dictionaries, and nested category objects."""
    if isinstance(value, str):
        if value.startswith("MOVE_"):
            yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from iter_move_names(item)
        return
    if isinstance(value, dict):
        for key in ("Move", "move"):
            move = value.get(key)
            if isinstance(move, str) and move.startswith("MOVE_"):
                yield move
                return
        for item in value.values():
            yield from iter_move_names(item)


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1))


def insert_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1))


def build_extra_table(
    registry: list[str],
    donor: dict[str, object],
    implemented: set[str],
) -> tuple[list[int], list[str], dict[str, object]]:
    offsets = [0]
    flat: list[str] = []
    missing_species: list[str] = []
    filtered: dict[str, list[str]] = {}
    per_category = {"EggMoves": 0, "MachineMoves": 0, "TutorMoves": 0}
    max_pool = {"species": None, "count": 0}

    for species in registry:
        source = donor.get(species)
        extras: list[str] = []
        rejected: list[str] = []
        seen: set[str] = set()

        if not isinstance(source, dict):
            missing_species.append(species)
            source = {}

        for category in ("EggMoves", "MachineMoves", "TutorMoves"):
            accepted_here = 0
            for move in iter_move_names(source.get(category, [])):
                if move == "MOVE_NONE":
                    continue
                if move not in implemented:
                    rejected.append(move)
                    continue
                if move in seen:
                    continue
                seen.add(move)
                extras.append(move)
                accepted_here += 1
            per_category[category] += accepted_here

        if rejected:
            filtered[species] = sorted(set(rejected))

        if len(extras) > max_pool["count"]:
            max_pool = {"species": species, "count": len(extras)}

        # Runtime still owns the final safety cap after level-up moves are added.
        flat.extend(extras)
        offsets.append(len(flat))

    # offset[species + 1] is required for species MAX_SPECIES.
    offsets.append(len(flat))

    report = {
        "species_count": len(registry),
        "species_missing_donor": missing_species,
        "total_extra_move_entries": len(flat),
        "accepted_by_source_category": per_category,
        "max_extra_pool": max_pool,
        "unsupported_extra_moves_by_species": filtered,
    }
    return offsets, flat, report


def write_generated_header(path: Path, offsets: list[int], flat: list[str]) -> None:
    lines = [
        "#ifndef POKEPLATINUM_GENERATED_MERCURY_MOVE_LEARNER_H",
        "#define POKEPLATINUM_GENERATED_MERCURY_MOVE_LEARNER_H",
        "",
        '#include "generated/moves.h"',
        "",
        f"#define MERCURY_MOVE_LEARNER_SPECIES_MAX {MAX_SPECIES}",
        "",
        "static const u32 sMercuryMoveLearnerExtraOffsets[MERCURY_MOVE_LEARNER_SPECIES_MAX + 2] = {",
    ]
    for i in range(0, len(offsets), 12):
        lines.append("    " + ", ".join(str(v) for v in offsets[i:i + 12]) + ",")
    lines += [
        "};",
        "",
        "static const u16 sMercuryMoveLearnerExtraMoves[] = {",
    ]
    if flat:
        for i in range(0, len(flat), 8):
            lines.append("    " + ", ".join(flat[i:i + 8]) + ",")
    else:
        lines.append("    MOVE_NONE,")
    lines += [
        "};",
        "",
        "#endif // POKEPLATINUM_GENERATED_MERCURY_MOVE_LEARNER_H",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def patch_move_backend(root: Path) -> None:
    header = root / "include/move_reminder_data.h"
    source = root / "src/move_reminder_data.c"

    insert_once(
        header,
        '#include "trainer_info.h"\n',
        f"\n#define MERCURY_MOVE_LEARNER_MAX_MOVES {MAX_POOL}\n",
        "Move Learner pool-size declaration",
    )

    text = source.read_text()
    include_anchor = '#include <string.h>\n'
    include_line = '\n#include "generated/mercury_move_learner.h"\n'
    if include_line not in text:
        if text.count(include_anchor) != 1:
            raise SystemExit("move reminder generated-table include anchor changed")
        text = text.replace(include_anchor, include_anchor + include_line, 1)

    text = text.replace("#define MAX_NUMBER_REMINDER_MOVES 22\n\n", "", 1)

    start = text.find("u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)")
    end = text.find("\nBOOL MoveReminderData_HasMoves", start)
    if start < 0 or end < 0:
        raise SystemExit("could not locate MoveReminderData_GetMoves after move-width install")

    replacement = r'''static BOOL MercuryMoveLearner_AddMove(
    u16 *moves,
    u16 *moveCount,
    const u16 currentMoves[LEARNED_MOVES_MAX],
    u16 move)
{
    if (move == MOVE_NONE || move == LEVEL_UP_MOVESET_TERMINATOR) {
        return FALSE;
    }

    for (u16 i = 0; i < LEARNED_MOVES_MAX; i++) {
        if (currentMoves[i] == move) {
            return FALSE;
        }
    }

    for (u16 i = 0; i < *moveCount; i++) {
        if (moves[i] == move) {
            return FALSE;
        }
    }

    // Always reserve the final slot for LEVEL_UP_MOVESET_TERMINATOR.
    if (*moveCount >= MERCURY_MOVE_LEARNER_MAX_MOVES - 1) {
        return FALSE;
    }

    moves[*moveCount] = move;
    (*moveCount)++;
    return TRUE;
}

u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)
{
    u16 species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);
    u8 form = Pokemon_GetValue(mon, MON_DATA_FORM, NULL);
    u8 level = Pokemon_GetValue(mon, MON_DATA_LEVEL, NULL);

    u16 currentMoves[LEARNED_MOVES_MAX];
    for (u16 i = 0; i < LEARNED_MOVES_MAX; i++) {
        currentMoves[i] = Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);
    }

    SpeciesLearnsetEntry *levelUpMoves = Heap_Alloc(heapID, sizeof(SpeciesLearnset));
    u16 *learnerMoves = Heap_Alloc(
        heapID,
        MERCURY_MOVE_LEARNER_MAX_MOVES * sizeof(u16));

    Pokemon_LoadLevelUpMovesOf(species, form, levelUpMoves);

    u16 moveCount = 0;

    // Preserve adventure progression for level-up moves: only moves whose
    // required level has been reached appear in the learner.
    for (u16 i = 0; i < MAX_LEARNSET_ENTRIES + 1; i++) {
        if (LEARNSET_ENTRY_IS_SENTINEL(levelUpMoves[i])) {
            break;
        }

        if (levelUpMoves[i].level <= level) {
            MercuryMoveLearner_AddMove(
                learnerMoves,
                &moveCount,
                currentMoves,
                levelUpMoves[i].move);
        }
    }

    // Redux-style universal pool.  These entries are generated from the
    // canonical egg/machine/tutor compatibility data, not Platinum TM bits.
    if (species > SPECIES_NONE && species <= MERCURY_MOVE_LEARNER_SPECIES_MAX) {
        u32 begin = sMercuryMoveLearnerExtraOffsets[species];
        u32 finish = sMercuryMoveLearnerExtraOffsets[species + 1];

        for (u32 i = begin; i < finish; i++) {
            MercuryMoveLearner_AddMove(
                learnerMoves,
                &moveCount,
                currentMoves,
                sMercuryMoveLearnerExtraMoves[i]);
        }
    }

    learnerMoves[moveCount] = LEVEL_UP_MOVESET_TERMINATOR;
    Heap_Free(levelUpMoves);
    return learnerMoves;
}
'''
    source.write_text(text[:start] + replacement + text[end:])


def patch_move_ui(root: Path) -> None:
    source = root / "src/applications/move_reminder.c"
    replace_once(source, "    u8 numMoves;\n", "    u16 numMoves;\n", "Move Learner list count width")
    replace_once(
        source,
        "    for (i = 0; i < 256; i++) {\n",
        "    for (i = 0; i < MERCURY_MOVE_LEARNER_MAX_MOVES; i++) {\n",
        "Move Learner list scan bound",
    )
    replace_once(
        source,
        "    controller->numMoves = (u8)MoveReminder_GetNumMoves(controller) + 1;\n",
        "    controller->numMoves = (u16)MoveReminder_GetNumMoves(controller) + 1;\n",
        "Move Learner list count assignment",
    )

    text_path = root / "res/text/move_reminder.json"
    data = json.loads(text_path.read_text())
    replacements = {
        "MoveReminder_Text_BattleMoves": "MOVE LEARNER",
        "MoveReminder_Text_ContestMoves": "CONTEST INFO",
        "MoveReminder_Text_Tutor_AskTeachWhichToMon": [
            "Choose a move for\\n",
            "{STRVAR_1 1, 0, 0}."
        ],
        "MoveReminder_Text_Tutor_AskShouldTeachMove": [
            "Teach {STRVAR_1 6, 1, 0} to\\n",
            "{STRVAR_1 1, 0, 0}?"
        ],
        "MoveReminder_Text_Tutor_AskGiveUpTeachingMon": [
            "Close the Move Learner for\\n",
            "{STRVAR_1 1, 0, 0}?"
        ],
        "MoveReminder_Text_Tutor_Payment": "No item is required.",
    }
    found: set[str] = set()
    for msg in data["messages"]:
        msg_id = msg.get("id")
        if msg_id in replacements:
            msg["en_US"] = replacements[msg_id]
            msg.pop("garbage", None)
            found.add(msg_id)
    if found != set(replacements):
        raise SystemExit(f"move reminder text IDs changed; missing {sorted(set(replacements) - found)}")
    text_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_free_pastoria_entry(root: Path) -> None:
    script_path = root / "res/field/scripts/scripts_pastoria_city_east_house.s"
    script_path.write_text(r'''#include "macros/scrcmd.inc"
#include "res/text/bank/pastoria_city_east_house.h"


    ScriptEntry PastoriaCityEastHouse_MoveManiac
    ScriptEntry PastoriaCityEastHouse_Youngster
    ScriptEntryEnd

PastoriaCityEastHouse_MoveManiac:
    PlaySE SE_CONFIRM_sseq_3
    LockAll
    FacePlayer
    SetFlag FLAG_TALKED_TO_PASTORIA_CITY_EAST_HOUSE_MOVE_MANIAC
    Message PastoriaCityEastHouse_Text_TeachMoveForHeartScale
    GoTo PastoriaCityEastHouse_TryTeachMove

PastoriaCityEastHouse_ComeBackWithHeartScale:
    Message PastoriaCityEastHouse_Text_ComeBackWithHeartScale
    WaitButton
    CloseMessage
    ReleaseAll
    End

PastoriaCityEastHouse_TryTeachMove:
    Message PastoriaCityEastHouse_Text_TutorWhichPokemon
    CloseMessage
    FadeScreenOut
    WaitFadeScreen
    SelectMoveTutorPokemon
    GetSelectedPartySlot VAR_0x8005
    ReturnToField
    FadeScreenIn
    WaitFadeScreen
    GoToIfEq VAR_0x8005, PARTY_SLOT_NONE, PastoriaCityEastHouse_ComeBackWithHeartScale
    GetPartyMonSpecies VAR_0x8005, VAR_RESULT
    GoToIfEq VAR_RESULT, 0, PastoriaCityEastHouse_EggsCantLearnMoves
    CheckHasLearnableReminderMoves VAR_RESULT, VAR_0x8005
    GoToIfEq VAR_RESULT, FALSE, PastoriaCityEastHouse_NoMovesToTeach
    Message PastoriaCityEastHouse_Text_TeachWhichMove
    CloseMessage
    FadeScreenOut
    WaitFadeScreen
    OpenMoveReminderMenu VAR_0x8005
    CheckLearnedReminderMove VAR_RESULT
    ReturnToField
    FadeScreenIn
    WaitFadeScreen
    GoToIfEq VAR_RESULT, 0xFF, PastoriaCityEastHouse_ComeBackWithHeartScale
    ReleaseAll
    End

PastoriaCityEastHouse_NoMovesToTeach:
    Message PastoriaCityEastHouse_Text_NoMovesToTeach
    WaitButton
    CloseMessage
    ReleaseAll
    End

PastoriaCityEastHouse_EggsCantLearnMoves:
    Message PastoriaCityEastHouse_Text_EggsCantLearnMoves
    WaitButton
    CloseMessage
    ReleaseAll
    End

PastoriaCityEastHouse_Youngster:
    NPCMessage PastoriaCityEastHouse_Text_NewspaperGivesHeartScales
    End
''')

    text_path = root / "res/text/pastoria_city_east_house.json"
    data = json.loads(text_path.read_text())
    replacements = {
        "PastoriaCityEastHouse_Text_TeachMoveForHeartScale": [
            "I’ve upgraded my tutoring setup.\\r",
            "Your Pokémon can now review all of\\n",
            "their compatible moves right here.\\r",
            "Level-up, Egg, machine, and tutor\\n",
            "moves are all handled by one system.\\r",
            "There’s no fee. Want to use the\\n",
            "Move Learner?"
        ],
        "PastoriaCityEastHouse_Text_ComeBackWithHeartScale":
            "Come back whenever you want to use the Move Learner.",
        "PastoriaCityEastHouse_Text_TutorWhichPokemon":
            "Which Pokémon should open the Move Learner?\\r",
        "PastoriaCityEastHouse_Text_TeachWhichMove":
            "All right. Pick any compatible move.\\r",
        "PastoriaCityEastHouse_Text_NoMovesToTeach": [
            "That Pokémon already knows every move\\n",
            "currently available in its learner."
        ],
        "PastoriaCityEastHouse_Text_HandedOverHeartScale":
            "The Move Learner never consumes an item.",
    }
    found: set[str] = set()
    for msg in data["messages"]:
        msg_id = msg.get("id")
        if msg_id in replacements:
            msg["en_US"] = replacements[msg_id]
            msg.pop("garbage", None)
            found.add(msg_id)
    if found != set(replacements):
        raise SystemExit(f"Pastoria text IDs changed; missing {sorted(set(replacements) - found)}")
    text_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--implemented-moves", type=Path, required=True)
    ap.add_argument("--report", type=Path, default=Path("mercury-move-learner.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    implemented = load_constants(args.implemented_moves)

    donor_path = hg / "data/learnsets/learnsets.json"
    if not donor_path.is_file():
        raise SystemExit(f"missing pinned merged learnset donor: {donor_path}")
    donor = json.loads(donor_path.read_text())

    offsets, flat, table_report = build_extra_table(registry, donor, implemented)
    write_generated_header(root / "generated/mercury_move_learner.h", offsets, flat)
    patch_move_backend(root)
    patch_move_ui(root)
    patch_free_pastoria_entry(root)

    report = {
        "gate": "MERCURY_DS_MOVE_LEARNER",
        "status": "PASS",
        "runtime_pool_capacity": MAX_POOL,
        "species_id_capacity": MAX_SPECIES,
        "donor": str(donor_path),
        "implemented_move_registry": str(args.implemented_moves),
        "policy": {
            "level_up_moves": "available after their required level is reached",
            "egg_moves": "available directly in Move Learner",
            "machine_moves": "available directly; no Platinum TM compatibility bit required",
            "tutor_moves": "available directly in Move Learner",
            "known_moves": "excluded from the selectable list",
            "unsupported_move_effects": "filtered out rather than approximated",
            "cost": "free; Heart Scale removed from Pastoria Move Learner entry",
        },
        "ui": {
            "base": "native Platinum Move Reminder application",
            "label": "MOVE LEARNER",
            "features": [
                "native DS windows/fonts",
                "scrolling move list",
                "type icons",
                "physical/special/status category icon",
                "power/accuracy/PP",
                "move description",
                "native four-move replacement flow",
            ],
        },
        **table_report,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "gate": report["gate"],
        "status": report["status"],
        "species_count": report["species_count"],
        "total_extra_move_entries": report["total_extra_move_entries"],
        "max_extra_pool": report["max_extra_pool"],
    }, indent=2))


if __name__ == "__main__":
    main()
