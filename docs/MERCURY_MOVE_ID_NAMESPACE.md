# Mercury Redux — 16-bit Move ID Namespace

**Locked architecture:** 2026-09-24  
**Active modernization branch:** `feature/mercury-build-forward`

## Decision

ID **919 is the current normalized Gen 1-9 canonical endpoint, not Mercury's ceiling**.

PT05C0 widens Platinum's packed 9-bit level-up move field to a true `u16`.
That removes the old 511-move storage limit permanently. The learnset layout is:

```c
typedef struct SpeciesLearnsetEntry {
    u16 move;
    u8 level;
    u8 padding;
} SpeciesLearnsetEntry;
```

ID **0** remains `MOVE_NONE`. ID **65535 / 0xFFFF** remains the learnset
sentinel, so the largest representable playable ID is **65534**.


## HG-Engine donor numbering

The pinned HG-Engine source keeps three HGSS dummy entries at donor IDs
468-470. Its Hone Claws is therefore donor ID 471 and its Malignant Chain is
donor ID 922. Mercury does **not** keep those dummy gaps in the canonical
namespace: donor IDs 471-922 are imported as canonical IDs 468-919.

This translation is source-facing only. It does not reduce the 16-bit
architecture or the reserved future capacity.

## Important DS-specific rule: wide encoding, compact live IDs

The 16-bit format does **not** mean Mercury should immediately place custom
moves at IDs such as 8192, 16000, or 60000.

Platinum uses move IDs as direct table/NARC indexes in several places. The
battle AI also contains `MoveTable moveTable[MAX_MOVES]`, and
`MoveTable_Load` reads `sizeof(MoveTable) * MAX_MOVES`. Therefore a very
high sparse ID can inflate RAM and resource tables even when almost all IDs
below it are empty.

So Mercury separates two ideas:

- **Encoding capacity:** 1-65534 is valid in the u16 architecture.
- **Active DS allocation:** keep live move IDs compact unless runtime testing
  proves a higher table budget is safe.

The current active soft ceiling is **4095**. IDs above 4095 remain reserved,
but they are not to be materialized just to create large empty gaps.

## Active allocation lanes

| Range | Lane | Use |
|---|---|---|
| 0 | `MOVE_NONE` | No move |
| 1-2047 | Official canonical | Official Pokémon moves. Gen 1-9 from the pinned HG donor normalizes through canonical ID 919, leaving 1128 future official slots. |
| 2048-2559 | Community imports | Curated reusable fan-made/community moves with source/provenance metadata. |
| 2560-3071 | Mercury custom | Original Mercury Redux moves for ordinary player/trainer use. |
| 3072-3583 | Boss / variant / signature | Mega, Delta, boss, event, alternate-form, and other signature moves. |
| 3584-4095 | Experimental staging | Provisional development IDs only. Must graduate before a sealed release. |
| 4096-65534 | Inactive future space | Valid u16 space, but not used on DS until a memory/table audit raises the live ceiling. |
| 65535 | Sentinel | Reserved permanently; never a playable move. |

## Rules for generators and imports

1. Never renumber an official canonical move to make room for custom content.
2. New official moves preserve their canonical IDs while they remain inside the
   official lane.
3. Community, Mercury-original, and signature moves stay in their own lanes.
4. Experimental IDs are not stable API and may not survive a sealed release.
5. `65535` must never be emitted as a real move.
6. Every importer must fail on collisions instead of silently replacing data.
7. Do not raise the active ceiling above 4095 without a build + battle-memory
   proof that covers `MAX_MOVES`, AI move-table storage, move-data NARCs,
   battle UI, Move Reminder, and save/reload.
8. The current normalized Gen 1-9 endpoint, 919, is tracked as `canonical_floor`; moving
   that floor upward does not require another learnset-format migration.

## Why 2047 for official moves?

It gives the current normalized Gen 1-9 move set **1128 additional official IDs** before any
custom namespace begins, while keeping the first custom lane at 2048 instead of
jumping thousands of entries higher. That is a much safer fit for Nintendo DS
memory than treating the full 16-bit address space as a sparse table.

## Validation

Run:

```bash
python3 tools/audit_move_id_namespace.py
```

The PT05C0 GitHub Actions build runs this audit before compiling the ROM.
