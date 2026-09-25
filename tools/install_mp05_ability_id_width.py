#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CANONICAL_LAST = "ABILITY_POISON_PUPPETEER"
CANONICAL_LAST_ID = 310


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1))


def parse_abilities(header: Path) -> list[tuple[int, str]]:
    found: dict[int, str] = {}
    rx = re.compile(r"^#define\s+(ABILITY_[A-Z0-9_]+)\s+(\d+)\s*$")
    for line in header.read_text().splitlines():
        m = rx.match(line.strip())
        if not m:
            continue
        token, value = m.group(1), int(m.group(2))
        if value <= CANONICAL_LAST_ID:
            found[value] = token
    expected = list(range(CANONICAL_LAST_ID + 1))
    if sorted(found) != expected:
        missing = sorted(set(expected) - set(found))
        raise SystemExit(f"HG ability namespace is not contiguous through {CANONICAL_LAST_ID}; missing {missing}")
    if found[CANONICAL_LAST_ID] != CANONICAL_LAST:
        raise SystemExit("Unexpected canonical Gen 9 ability tail")
    return [(i, found[i]) for i in expected]


def load_hg_names(path: Path) -> list[str]:
    names = path.read_text().splitlines()
    if len(names) <= CANONICAL_LAST_ID:
        raise SystemExit(f"HG ability-name bank only has {len(names)} entries")
    names = names[: CANONICAL_LAST_ID + 1]
    # HG uses a typographic apostrophe for Dragon’s Maw / Mind’s Eye, which
    # Platinum's charmap already supports.
    return names


def extend_text_bank(path: Path, names: list[str], *, uppercase: bool = False) -> int:
    data = json.loads(path.read_text())
    messages = data["messages"]
    original = len(messages)
    if original != 124:
        raise SystemExit(f"{path}: expected vanilla 124 messages, found {original}")

    prefix = messages[0]["id"].rsplit("_", 1)[0]
    for idx in range(original, CANONICAL_LAST_ID + 1):
        name = names[idx].upper() if uppercase else names[idx]
        messages.append({
            "id": f"{prefix}_{idx:05d}",
            "en_US": name,
        })
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return len(messages) - original


def extend_descriptions(path: Path, names: list[str]) -> int:
    data = json.loads(path.read_text())
    messages = data["messages"]
    original = len(messages)
    if original != 124:
        raise SystemExit(f"{path}: expected vanilla 124 descriptions, found {original}")

    prefix = messages[0]["id"].rsplit("_", 1)[0]
    for idx in range(original, CANONICAL_LAST_ID + 1):
        name = names[idx]
        messages.append({
            "id": f"{prefix}_{idx:05d}",
            "en_US": [
                f"{name} is a modern Ability.\n",
                "Its battle effect is ported separately."
            ],
        })
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return len(messages) - original


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("platinum", type=Path)
    ap.add_argument("hg_engine", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    pt = args.platinum
    hg = args.hg_engine

    abilities = parse_abilities(hg / "include/constants/ability.h")
    names = load_hg_names(hg / "data/text/720.txt")

    (pt / "generated/abilities.txt").write_text(
        "\n".join(token for _, token in abilities) + "\n"
    )

    # Personal-data records: widen species ability slots to 16 bits.
    replace_once(
        pt / "include/struct_defs/species.h",
        "    u8 abilities[MAX_ABILITIES];",
        "    u16 abilities[MAX_ABILITIES];",
    )
    replace_once(
        pt / "tools/dataproc/src/speciesproc.c",
        '''        .abilities = {
            enum_u8(".abilities[0]", enum Ability),
            enum_u8(".abilities[1]", enum Ability),
        },''',
        '''        .abilities = {
            enum_u16(".abilities[0]", enum Ability),
            enum_u16(".abilities[1]", enum Ability),
        },''',
    )

    # Individual save data must not grow. Keep the original low ability byte,
    # keep all six user-facing marking bits, and use only the two unused high
    # bits of the markings byte for ability bits 8-9.
    replace_once(
        pt / "include/struct_defs/pokemon.h",
        '''    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings;
    /* 0x0F */ u8 originLanguage;''',
        '''    /* 0x0C */ u8 friendship;
    /* 0x0D */ u8 ability;
    /* 0x0E */ u8 markings : 6;
    /*      */ u8 abilityHigh : 2;
    /* 0x0F */ u8 originLanguage;''',
    )

    pokemon_c = pt / "src/pokemon.c"
    replace_once(
        pokemon_c,
        '''    case MON_DATA_ABILITY:
        result = monDataBlockA->ability;
        break;''',
        '''    case MON_DATA_ABILITY:
        result = monDataBlockA->ability | (monDataBlockA->abilityHigh << 8);
        break;''',
    )
    replace_once(
        pokemon_c,
        '''    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u8Value;
        break;''',
        '''    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u16Value & 0xFF;
        monDataBlockA->abilityHigh = (*u16Value >> 8) & 0x3;
        break;''',
    )

    # Battle and Summary runtime holders must not truncate the widened value.
    replace_once(
        pt / "include/battle/battle_mon.h",
        "    u8 ability;",
        "    u16 ability;",
    )
    replace_once(
        pt / "include/applications/pokemon_summary_screen/main.h",
        '''    u16 speed;
    u8 ability;
    u8 nature;''',
        '''    u16 speed;
    u16 ability;
    u8 nature;''',
    )

    names_added = extend_text_bank(pt / "res/text/ability_names.json", names)
    upper_added = extend_text_bank(
        pt / "res/text/ability_names_uppercase.json", names, uppercase=True
    )
    descriptions_added = extend_descriptions(
        pt / "res/text/ability_descriptions.json", names
    )

    # Static invariants: save payload stays two bytes for ability+markings and
    # the namespace is large enough for every canonical Gen 9 ability.
    pokemon_h = (pt / "include/struct_defs/pokemon.h").read_text()
    species_h = (pt / "include/struct_defs/species.h").read_text()
    assert "u8 markings : 6;" in pokemon_h
    assert "u8 abilityHigh : 2;" in pokemon_h
    assert "u16 abilities[MAX_ABILITIES];" in species_h

    report = {
        "gate": "MP05_ABILITY_ID_WIDTH_FOUNDATION",
        "canonical_abilities": len(abilities),
        "first_id": abilities[0][0],
        "last_id": abilities[-1][0],
        "last_token": abilities[-1][1],
        "ability_id_bits": 10,
        "save_layout_growth_bytes": 0,
        "marking_bits_preserved": 6,
        "name_messages_added": names_added,
        "uppercase_name_messages_added": upper_added,
        "description_messages_added": descriptions_added,
        "modern_ability_behaviors_ported": 0,
        "species_assignment_policy": "Keep existing MP04 assignments until behavior ports are installed.",
        "status": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
