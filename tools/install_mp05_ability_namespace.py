#!/usr/bin/env python3
"""Install the canonical Gen 5-9 ability namespace and 9-bit runtime storage.

MP05A establishes stable canonical ability IDs 0..310 without pretending that
all modern battle hooks are already implemented. Species importers receive a
separate implemented-ability registry so unported abilities continue to fall
back to ABILITY_NONE until their real mechanics are added.

The save format stays the same size. Platinum uses only six visible marking
bits, so bit 7 of the existing markings byte stores ability bit 8.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CANONICAL_MAX = 310
NATIVE_MAX = 123
ABILITY_HIGH_MASK = "0x80"
VISIBLE_MARKINGS_MASK = "0x3F"

DEFINE_RE = re.compile(r"^#define\s+(ABILITY_[A-Z0-9_]+)\s+(\d+)\s*$", re.M)


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1))


def parse_donor_abilities(path: Path) -> list[str]:
    text = path.read_text()
    by_id = {int(num): name for name, num in DEFINE_RE.findall(text)}
    missing = [i for i in range(CANONICAL_MAX + 1) if i not in by_id]
    if missing:
        raise SystemExit(f"donor ability namespace has gaps: {missing[:20]}")
    return [by_id[i] for i in range(CANONICAL_MAX + 1)]


def read_text_bank(path: Path) -> list[str]:
    # HG-Engine stores literal \n escape tokens inside one line per entry.
    return path.read_text(encoding="utf-8").splitlines()


def platinum_message(prefix: str, index: int, value):
    return {"id": f"{prefix}_{index:05d}", "en_US": value}


def description_value(raw: str):
    parts = raw.split(r"\n")
    if len(parts) == 1:
        return parts[0]
    return [part + ("\n" if i < len(parts) - 1 else "") for i, part in enumerate(parts)]


def extend_text_bank(path: Path, donor: list[str], prefix: str, descriptions: bool = False) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data["messages"]
    if len(messages) != NATIVE_MAX + 1:
        raise SystemExit(f"{path}: expected 124 native messages, found {len(messages)}")
    if len(donor) <= CANONICAL_MAX:
        raise SystemExit(f"{path}: donor text is too short: {len(donor)}")

    for i in range(NATIVE_MAX + 1, CANONICAL_MAX + 1):
        value = description_value(donor[i]) if descriptions else donor[i]
        messages.append(platinum_message(prefix, i, value))

    if len(messages) != CANONICAL_MAX + 1:
        raise SystemExit(f"{path}: final message count mismatch: {len(messages)}")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_widths(pt: Path) -> list[str]:
    patched: list[str] = []

    species_h = pt / "include/struct_defs/species.h"
    replace_once(
        species_h,
        "    u8 abilities[MAX_ABILITIES];\n",
        "    u16 abilities[MAX_ABILITIES];\n",
        "SpeciesData ability width",
    )
    patched.append(str(species_h.relative_to(pt)))

    speciesproc = pt / "tools/dataproc/src/speciesproc.c"
    replace_once(
        speciesproc,
        '''        .abilities = {
            enum_u8(".abilities[0]", enum Ability),
            enum_u8(".abilities[1]", enum Ability),
        },
''',
        '''        .abilities = {
            enum_u16(".abilities[0]", enum Ability),
            enum_u16(".abilities[1]", enum Ability),
        },
''',
        "speciesproc ability parser",
    )
    patched.append(str(speciesproc.relative_to(pt)))

    battle_mon = pt / "include/battle/battle_mon.h"
    replace_once(
        battle_mon,
        "    u8 ability;\n\n    u32 weatherAbilityAnnounced",
        "    u16 ability;\n\n    u32 weatherAbilityAnnounced",
        "BattleMon ability width",
    )
    patched.append(str(battle_mon.relative_to(pt)))

    summary = pt / "include/applications/pokemon_summary_screen/main.h"
    replace_once(
        summary,
        "    u8 ability;\n    u8 nature;\n",
        "    u16 ability;\n    u8 nature;\n",
        "summary ability width",
    )
    patched.append(str(summary.relative_to(pt)))

    msg = pt / "include/battle/message_defs.h"
    replace_once(
        msg,
        '''typedef struct RefreshPartyStatusMessage {
    u8 command;
    u8 ability;
    u16 move;
} RefreshPartyStatusMessage;
''',
        '''typedef struct RefreshPartyStatusMessage {
    u8 command;
    u8 padding;
    u16 ability;
    u16 move;
} RefreshPartyStatusMessage;
''',
        "refresh-party ability width",
    )
    patched.append(str(msg.relative_to(pt)))

    wild = pt / "src/overlay006/wild_encounters.c"
    replace_once(
        wild,
        "    u8 firstMonAbility;\n",
        "    u16 firstMonAbility;\n",
        "wild lead ability width",
    )
    replace_once(
        wild,
        "const u8 maxEncounters, const u8 type, const u8 ability, u8 *encSlot",
        "const u8 maxEncounters, const u8 type, const u16 ability, u8 *encSlot",
        "wild type-match ability parameter",
    )
    patched.append(str(wild.relative_to(pt)))

    trainer_ai = pt / "src/battle/trainer_ai/trainer_ai.c"
    replace_once(
        trainer_ai,
        '''    u8 moveType;
    u8 ability;
    u8 checkAbility;
''',
        '''    u8 moveType;
    u16 ability;
    u16 checkAbility;
''',
        "trainer AI ability locals",
    )
    patched.append(str(trainer_ai.relative_to(pt)))

    battle_lib = pt / "src/battle/battle_lib.c"
    replace_once(
        battle_lib,
        '''    u32 statusMask;

    u8 ability;
    u8 gender;
''',
        '''    u32 statusMask;

    u16 ability;
    u8 gender;
''',
        "damage-calc ability width",
    )
    patched.append(str(battle_lib.relative_to(pt)))

    daycare = pt / "src/overlay005/daycare.c"
    replace_once(
        daycare,
        '''    u8 i;
    u8 ability;
    int partyCount = Party_GetCurrentCount(party);
''',
        '''    u8 i;
    u16 ability;
    int partyCount = Party_GetCurrentCount(party);
''',
        "daycare ability width",
    )
    patched.append(str(daycare.relative_to(pt)))

    recording_h = pt / "include/struct_defs/struct_02078B40.h"
    replace_once(
        recording_h,
        '''    u16 partyDecrypted : 1;
    u16 boxDecrypted : 1;
    u16 checksumFailed : 1;
    u16 : 13;
''',
        '''    u16 partyDecrypted : 1;
    u16 boxDecrypted : 1;
    u16 checksumFailed : 1;
    u16 abilityHigh : 1;
    u16 : 12;
''',
        "battle-recording spare ability bit",
    )
    patched.append(str(recording_h.relative_to(pt)))

    pokemon_c = pt / "src/pokemon.c"
    replace_once(
        pokemon_c,
        "#define FATEFUL_ENCOUNTER_LOCATION 3002\n",
        '''#define FATEFUL_ENCOUNTER_LOCATION 3002

// Platinum exposes six marking bits. Mercury reserves bit 7 of the same saved
// byte for ability bit 8, preserving the encrypted BoxPokemon block size.
#define MERCURY_ABILITY_HIGH_MASK 0x80
#define MERCURY_VISIBLE_MARKINGS_MASK 0x3F
''',
        "extended ability masks",
    )
    replace_once(
        pokemon_c,
        '''    case MON_DATA_ABILITY:
        result = monDataBlockA->ability;
        break;

    case MON_DATA_MARKINGS:
        result = monDataBlockA->markings;
        break;
''',
        '''    case MON_DATA_ABILITY:
        result = monDataBlockA->ability
            | ((monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) << 1);
        break;

    case MON_DATA_MARKINGS:
        result = monDataBlockA->markings & MERCURY_VISIBLE_MARKINGS_MASK;
        break;
''',
        "extended ability getter",
    )
    replace_once(
        pokemon_c,
        '''    case MON_DATA_ABILITY:
        monDataBlockA->ability = *u8Value;
        break;

    case MON_DATA_MARKINGS:
        monDataBlockA->markings = *u8Value;
        break;
''',
        '''    case MON_DATA_ABILITY: {
        u16 ability = *u16Value;
        GF_ASSERT(ability <= 0x1FF);
        monDataBlockA->ability = ability & 0xFF;
        monDataBlockA->markings = (monDataBlockA->markings & ~MERCURY_ABILITY_HIGH_MASK)
            | ((ability >> 1) & MERCURY_ABILITY_HIGH_MASK);
        break;
    }

    case MON_DATA_MARKINGS:
        monDataBlockA->markings = (monDataBlockA->markings & ~MERCURY_VISIBLE_MARKINGS_MASK)
            | (*u8Value & MERCURY_VISIBLE_MARKINGS_MASK);
        break;
''',
        "extended ability setter",
    )
    replace_once(
        pokemon_c,
        "    param1->ability = monDataBlockA->ability;\n",
        '''    param1->ability = monDataBlockA->ability;
    param1->abilityHigh = (monDataBlockA->markings & MERCURY_ABILITY_HIGH_MASK) != 0;
''',
        "recording ability export",
    )
    replace_once(
        pokemon_c,
        "    monDataBlockA->ability = param0->ability;\n",
        '''    monDataBlockA->ability = param0->ability;
    monDataBlockA->markings = (monDataBlockA->markings & ~MERCURY_ABILITY_HIGH_MASK)
        | (param0->abilityHigh ? MERCURY_ABILITY_HIGH_MASK : 0);
''',
        "recording ability import",
    )
    patched.append(str(pokemon_c.relative_to(pt)))

    frontier = pt / "src/overlay104/frontier_opponents.c"
    replace_once(
        frontier,
        '''    Pokemon_SetValue(mon, MON_DATA_ABILITY, &frontierMon->ability);
    Pokemon_SetValue(mon, MON_DATA_FRIENDSHIP, &frontierMon->friendship);
''',
        '''    u16 ability = frontierMon->ability;
    Pokemon_SetValue(mon, MON_DATA_ABILITY, &ability);
    Pokemon_SetValue(mon, MON_DATA_FRIENDSHIP, &frontierMon->friendship);
''',
        "frontier u16 ability setter temporary",
    )
    patched.append(str(frontier.relative_to(pt)))

    return patched


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mp05-ability-namespace.json"))
    ap.add_argument(
        "--implemented-registry",
        type=Path,
        default=Path("mp05-implemented-abilities.txt"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()

    donor = parse_donor_abilities(hg / "include/constants/ability.h")
    platinum = [
        x.strip()
        for x in (pt / "generated/abilities.txt").read_text().splitlines()
        if x.strip()
    ]

    if len(platinum) != NATIVE_MAX + 1:
        raise SystemExit(f"expected 124 native Platinum abilities, found {len(platinum)}")
    if platinum != donor[: NATIVE_MAX + 1]:
        for i, (a, b) in enumerate(zip(platinum, donor)):
            if a != b:
                raise SystemExit(f"native ability mismatch at {i}: Platinum={a}, donor={b}")
        raise SystemExit("native ability registry mismatch")

    # Deliberately stop at Poison Puppeteer. HG-Engine's IDs 311+ are
    # project-specific extensions and are not part of the canonical Gen 9 set.
    (pt / "generated/abilities.txt").write_text(
        "\n".join(donor) + "\n",
        encoding="utf-8",
    )
    args.implemented_registry.write_text(
        "\n".join(donor[: NATIVE_MAX + 1]) + "\n",
        encoding="utf-8",
    )

    names = read_text_bank(hg / "data/text/720.txt")
    uppercase = read_text_bank(hg / "data/text/721.txt")
    descriptions = read_text_bank(hg / "data/text/722.txt")
    for label, bank in (("names", names), ("uppercase", uppercase), ("descriptions", descriptions)):
        if len(bank) <= CANONICAL_MAX:
            raise SystemExit(f"donor {label} bank too short: {len(bank)}")

    extend_text_bank(
        pt / "res/text/ability_names.json",
        names,
        "pl_msg_00000610",
    )
    extend_text_bank(
        pt / "res/text/ability_names_uppercase.json",
        uppercase,
        "pl_msg_00000611",
    )
    extend_text_bank(
        pt / "res/text/ability_descriptions.json",
        descriptions,
        "pl_msg_00000612",
        descriptions=True,
    )

    patched = patch_widths(pt)

    report = {
        "gate": "MP05_ABILITY_NAMESPACE_AND_WIDTH",
        "canonical_id_range": [0, CANONICAL_MAX],
        "canonical_ability_count": CANONICAL_MAX + 1,
        "native_platinum_implemented_range": [0, NATIVE_MAX],
        "native_implemented_count": NATIVE_MAX + 1,
        "modern_namespace_additions": CANONICAL_MAX - NATIVE_MAX,
        "max_canonical_ability": donor[CANONICAL_MAX],
        "save_storage": {
            "ability_low_bits": "PokemonDataBlockA.ability",
            "ability_bit_8": "PokemonDataBlockA.markings bit 7",
            "visible_markings_bits": "0..5",
            "capacity": 511,
            "box_block_size_changed": False,
        },
        "species_data_ability_width": "u16",
        "battle_ability_width": "u16",
        "modern_effects_implemented_in_this_gate": 0,
        "live_species_policy": "Only abilities in --implemented-registry may be assigned; unported modern abilities remain ABILITY_NONE.",
        "excluded_donor_extensions": list(range(CANONICAL_MAX + 1, 320)),
        "patched_files": patched,
        "result": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
