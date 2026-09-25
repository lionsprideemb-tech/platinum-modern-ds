#!/usr/bin/env python3
"""Install Mercury's DS-native universal Move Learner.

The learner deliberately does not depend on Platinum's TM bitfield.  Instead it
builds one legal move pool per species from the species data already present in
our compiled Platinum source:
  * level-up moves
  * egg moves
  * tutor moves

TM/HM compatibility is intentionally excluded.  This lets Mercury retire the
legacy machine-compatibility system while preserving Platinum's native move
teaching / four-slot replacement flow and DS move-detail UI.

The runtime list omits moves the Pokemon already knows.  The existing
Move Reminder application is reused as the first DS-native front end, so the
screen keeps Platinum's type/category icons, scrolling, descriptions, power,
accuracy, PP, and Summary-screen replacement flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUNTIME_SPECIES_MAX = 1025
RUNTIME_LIST_LIMIT = 254  # MoveReminderController::numMoves is u8.


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1))


def replace_c_function(path: Path, signature: str, replacement: str) -> None:
    text = path.read_text()
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"{path}: function signature not found: {signature}")
    brace = text.find("{", start)
    if brace < 0:
        raise SystemExit(f"{path}: opening brace not found for {signature}")

    depth = 0
    end = None
    for i in range(brace, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f"{path}: unterminated function: {signature}")

    path.write_text(text[:start] + replacement.rstrip() + "\n" + text[end:])


def load_registry(path: Path) -> list[str]:
    rows = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            rows.append(line)
    if len(rows) <= RUNTIME_SPECIES_MAX:
        raise SystemExit(
            f"species registry has {len(rows)} rows; expected IDs through {RUNTIME_SPECIES_MAX}"
        )
    return rows


def load_constants(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def species_dir(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def append_move(pool: list[str], seen: set[str], move: object, available: set[str]) -> None:
    if not isinstance(move, str):
        return
    if move == "MOVE_NONE" or move not in available or move in seen:
        return
    seen.add(move)
    pool.append(move)


def species_pool(data: dict, available: set[str]) -> list[str]:
    learnset = data.get("learnset") or {}
    pool: list[str] = []
    seen: set[str] = set()

    # Level-up moves are intentionally all available in the learner.  This is
    # Mercury's replacement for machine hunting: the legal species pool is the
    # gate, not an inventory item.
    for row in learnset.get("by_level", []) or []:
        if isinstance(row, list) and len(row) >= 2:
            append_move(pool, seen, row[1], available)

    for move in learnset.get("egg_moves", []) or []:
        append_move(pool, seen, move, available)

    for move in learnset.get("by_tutor", []) or []:
        append_move(pool, seen, move, available)

    return pool


def write_pool_header(pt: Path, report_path: Path) -> dict:
    registry = load_registry(pt / "generated/species.txt")
    available = load_constants(pt / "generated/moves.txt")

    all_moves: list[str] = []
    spans: list[tuple[int, int]] = [(0, 0)] * (RUNTIME_SPECIES_MAX + 1)
    report_species = []
    max_count = 0
    max_species = "SPECIES_NONE"

    for species_id in range(1, RUNTIME_SPECIES_MAX + 1):
        species_const = registry[species_id]
        data_path = pt / "res/pokemon" / species_dir(species_const) / "data.json"
        if not data_path.is_file():
            raise SystemExit(f"missing species data for ID {species_id}: {data_path}")
        data = json.loads(data_path.read_text())
        pool = species_pool(data, available)

        if len(pool) > RUNTIME_LIST_LIMIT:
            raise SystemExit(
                f"{species_const}: move pool has {len(pool)} entries; "
                f"runtime UI limit is {RUNTIME_LIST_LIMIT}"
            )

        offset = len(all_moves)
        all_moves.extend(pool)
        spans[species_id] = (offset, len(pool))

        if len(pool) > max_count:
            max_count = len(pool)
            max_species = species_const

        report_species.append({
            "id": species_id,
            "species": species_const,
            "move_count": len(pool),
        })

    header = pt / "res/pokemon/mercury_move_pools.h"
    lines = [
        "#ifndef POKEPLATINUM_MERCURY_MOVE_POOLS_H",
        "#define POKEPLATINUM_MERCURY_MOVE_POOLS_H",
        "",
        '#include "generated/moves.h"',
        "",
        f"#define MERCURY_MOVE_LEARNER_SPECIES_MAX {RUNTIME_SPECIES_MAX}",
        f"#define MERCURY_MOVE_LEARNER_LIST_LIMIT {RUNTIME_LIST_LIMIT}",
        "",
        "typedef struct MercuryMovePoolSpan {",
        "    u32 offset;",
        "    u16 count;",
        "    u16 padding;",
        "} MercuryMovePoolSpan;",
        "",
        "static const u16 sMercuryMovePoolMoves[] = {",
    ]

    if all_moves:
        for i in range(0, len(all_moves), 8):
            lines.append("    " + ", ".join(all_moves[i:i + 8]) + ",")
    else:
        lines.append("    MOVE_NONE,")

    lines += [
        "};",
        "",
        f"static const MercuryMovePoolSpan sMercuryMovePoolSpans[{RUNTIME_SPECIES_MAX + 1}] = {{",
        "    [0] = { 0, 0, 0 },",
    ]

    for species_id in range(1, RUNTIME_SPECIES_MAX + 1):
        offset, count = spans[species_id]
        lines.append(f"    [{species_id}] = {{ {offset}, {count}, 0 }},")

    lines += [
        "};",
        "",
        "#endif // POKEPLATINUM_MERCURY_MOVE_POOLS_H",
        "",
    ]
    header.write_text("\n".join(lines))

    report = {
        "gate": "ML01_DS_MOVE_LEARNER",
        "species_covered": RUNTIME_SPECIES_MAX,
        "tm_compatibility_dependency": False,
        "sources": ["by_level", "egg_moves", "by_tutor"],
        "total_pool_entries": len(all_moves),
        "largest_pool": {
            "species": max_species,
            "count": max_count,
        },
        "runtime_list_limit": RUNTIME_LIST_LIMIT,
        "species": report_species,
        "status": "PASS",
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def patch_runtime(pt: Path) -> None:
    reminder_c = pt / "src/move_reminder_data.c"
    include_anchor = '#include "pokemon.h"\n'
    include_line = '#include "res/pokemon/mercury_move_pools.h"\n'
    text = reminder_c.read_text()
    if include_line not in text:
        replace_once(
            reminder_c,
            include_anchor,
            include_anchor + "\n" + include_line,
            "Pokemon include anchor",
        )

    replacement = r'''u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)
{
    u16 currentMoves[LEARNED_MOVES_MAX];
    u16 species = Pokemon_GetValue(mon, MON_DATA_SPECIES, NULL);

    for (u8 i = 0; i < LEARNED_MOVES_MAX; i++) {
        currentMoves[i] = Pokemon_GetValue(mon, MON_DATA_MOVE1 + i, NULL);
    }

    u16 allocationCount = 1;
    MercuryMovePoolSpan span = { 0, 0, 0 };

    if (species <= MERCURY_MOVE_LEARNER_SPECIES_MAX) {
        span = sMercuryMovePoolSpans[species];
        allocationCount = span.count + 1;
    }

    u16 *learnerMoves = Heap_Alloc(heapID, allocationCount * sizeof(u16));
    u16 out = 0;

    for (u16 i = 0; i < span.count; i++) {
        u16 move = sMercuryMovePoolMoves[span.offset + i];
        BOOL alreadyKnown = FALSE;

        for (u8 slot = 0; slot < LEARNED_MOVES_MAX; slot++) {
            if (move == currentMoves[slot]) {
                alreadyKnown = TRUE;
                break;
            }
        }

        if (alreadyKnown == FALSE) {
            learnerMoves[out++] = move;
        }
    }

    learnerMoves[out] = LEVEL_UP_MOVESET_TERMINATOR;
    return learnerMoves;
}'''

    replace_c_function(
        reminder_c,
        "u16 *MoveReminderData_GetMoves(Pokemon *mon, enum HeapID heapID)",
        replacement,
    )


def patch_text(pt: Path) -> None:
    path = pt / "res/text/move_reminder.json"
    data = json.loads(path.read_text())
    replacements = {
        "MoveReminder_Text_BattleMoves": "MOVE LEARNER",
        "MoveReminder_Text_Reminder_AskTeachWhichToMon": [
            "Choose a move for\n",
            "{STRVAR_1 1, 0, 0}."
        ],
        "MoveReminder_Text_Reminder_AskShouldTeachMove": [
            "Teach {STRVAR_1 6, 1, 0}\n",
            "to this Pokémon?"
        ],
        "MoveReminder_Text_Reminder_AskGiveUpTeachingMon": [
            "Exit the Move Learner\n",
            "without teaching a move?"
        ],
        "MoveReminder_Text_Reminder_LearnedMoveNoFanfare": [
            "{STRVAR_1 1, 0, 0} learned\n",
            "{STRVAR_1 6, 1, 0}.\r"
        ],
        "MoveReminder_Text_Reminder_AskStopTryingToTeachMove": [
            "Stop trying to teach\n",
            "{STRVAR_1 6, 1, 0}?"
        ],
        "MoveReminder_Text_Reminder_MonDidNotLearnMove": [
            "{STRVAR_1 1, 0, 0} did not learn\n",
            "{STRVAR_1 6, 1, 0}.\r"
        ],
    }

    found = set()
    for message in data.get("messages", []):
        mid = message.get("id")
        if mid in replacements:
            message["en_US"] = replacements[mid]
            message.pop("garbage", None)
            found.add(mid)

    missing = set(replacements) - found
    if missing:
        raise SystemExit(f"move reminder text IDs missing: {sorted(missing)}")

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_pastoria_access(pt: Path) -> None:
    script = pt / "res/field/scripts/scripts_pastoria_city_east_house.s"
    text = script.read_text()

    old_intro = '''    BufferItemNameWithArticle 4, ITEM_HEART_SCALE
    GoToIfUnset FLAG_TALKED_TO_PASTORIA_CITY_EAST_HOUSE_MOVE_MANIAC, PastoriaCityEastHouse_CheckHeartScale
    CheckItem ITEM_HEART_SCALE, 1, VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, PastoriaCityEastHouse_ComeBackWithHeartScale
    GoTo PastoriaCityEastHouse_TryTeachMove
'''
    new_intro = '''    Message PastoriaCityEastHouse_Text_TeachMoveForHeartScale
    GoTo PastoriaCityEastHouse_TryTeachMove
'''
    if old_intro not in text:
        raise SystemExit(f"{script}: expected Heart Scale intro block not found")
    text = text.replace(old_intro, new_intro, 1)

    old_payment = '''    RemoveItem ITEM_HEART_SCALE, 1, VAR_RESULT
    BufferPlayerName 3
    Message PastoriaCityEastHouse_Text_HandedOverHeartScale
'''
    new_payment = '''    Message PastoriaCityEastHouse_Text_HandedOverHeartScale
'''
    if old_payment not in text:
        raise SystemExit(f"{script}: expected Heart Scale payment block not found")
    text = text.replace(old_payment, new_payment, 1)
    script.write_text(text)

    text_path = pt / "res/text/pastoria_city_east_house.json"
    data = json.loads(text_path.read_text())
    replacements = {
        "PastoriaCityEastHouse_Text_TeachMoveForHeartScale": [
            "Welcome to the Mercury Move Learner!\r",
            "I can open a Pokémon’s legal move pool\n",
            "without using a TM or Heart Scale."
        ],
        "PastoriaCityEastHouse_Text_ThatsAHeartScale": "Ready to open the Move Learner?",
        "PastoriaCityEastHouse_Text_TutorWhichPokemon": "Which Pokémon wants to learn a move?",
        "PastoriaCityEastHouse_Text_TeachWhichMove": "Choose a move from its legal move pool.",
        "PastoriaCityEastHouse_Text_HandedOverHeartScale": "All set! Come back anytime.",
        "PastoriaCityEastHouse_Text_ComeBackWithHeartScale": "Come back anytime you want to change moves.",
        "PastoriaCityEastHouse_Text_NoMovesToTeach": [
            "That Pokémon already knows every move\n",
            "currently available in its legal pool."
        ],
    }
    found = set()
    for message in data.get("messages", []):
        mid = message.get("id")
        if mid in replacements:
            message["en_US"] = replacements[mid]
            message.pop("garbage", None)
            found.add(mid)
    missing = set(replacements) - found
    if missing:
        raise SystemExit(f"Pastoria text IDs missing: {sorted(missing)}")
    text_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("ml01-move-learner.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    report = write_pool_header(pt, args.report)
    patch_runtime(pt)
    patch_text(pt)
    patch_pastoria_access(pt)

    print(json.dumps({
        "gate": report["gate"],
        "species_covered": report["species_covered"],
        "total_pool_entries": report["total_pool_entries"],
        "largest_pool": report["largest_pool"],
        "tm_dependency": report["tm_compatibility_dependency"],
        "status": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()
