# Mercury Redux — 16-bit Move ID Namespace

**Locked:** 2026-09-24  
**Active modernization branch:** `feature/mercury-build-forward`

## Decision

ID **922 is a canonical floor, not a project ceiling**.

Mercury Redux uses a 16-bit move ID architecture for level-up learnsets and
keeps move IDs as `u16` through the runtime paths that consume them. This
gives the project a permanent namespace without another format migration when
new official generations or custom content are added.

Because `0xFFFF` / **65535** is reserved as the learnset sentinel, the
largest usable move ID is **65534**. ID **0** remains `MOVE_NONE`.

## Permanent ranges

| Range | Lane | Use |
|---|---|---|
| 0 | `MOVE_NONE` | No move |
| 1-4095 | Official canonical | Official Pokémon moves. Gen 1-9 currently occupies through 922; later official generations stay here. |
| 4096-8191 | Community imports | Reusable fan-made/community moves with source, license/provenance, and compatibility metadata. |
| 8192-12287 | Mercury custom | Original Mercury Redux moves for ordinary player/trainer use. |
| 12288-16383 | Boss / variant / signature | Mega, Delta, boss, event, alternate-form, and other signature moves. |
| 16384-32767 | Experimental staging | Provisional development IDs only. Must graduate before a sealed release. |
| 32768-65534 | Future reserved | Unassigned expansion space. |
| 65535 | Sentinel | Reserved permanently; never a playable move. |

These boundaries are powers of two where practical so tooling can classify IDs
cheaply and predictably.

## Rules for generators and imports

1. Never renumber an official canonical move to make room for custom content.
2. New official moves use their canonical IDs as long as they fit inside the
   official lane.
3. Community imports never consume official IDs.
4. Mercury-original moves never consume community IDs.
5. Experimental IDs are not stable API. A sealed build may not depend on them.
6. `65535` must never be emitted as a real move.
7. Every importer must fail on collisions instead of silently replacing an
   existing move.
8. The current Gen 1-9 endpoint, 922, is tracked as
   `canonical_floor` in `data/move_id_namespace.json`; it can move upward
   without changing the binary format.

## Why this matters

The old Platinum WOTBL format packed a move into 9 bits, limiting level-up move
IDs to 511. PT05C0 widens each entry to:

```c
typedef struct SpeciesLearnsetEntry {
    u16 move;
    u8 level;
    u8 padding;
} SpeciesLearnsetEntry;
```

That solves the storage problem permanently. The namespace contract solves the
organizational problem: official, imported, Mercury-original, signature, and
experimental moves can all coexist without accidental ID collisions.

## Validation

Run:

```bash
python3 tools/audit_move_id_namespace.py
```

The PT05C0 GitHub Actions build also runs this audit before compiling the ROM.
