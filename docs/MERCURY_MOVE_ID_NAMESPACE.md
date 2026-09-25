# Mercury Redux — Compact 16-bit Move ID Namespace

**Locked architecture:** 2026-09-24  
**Compact allocation revision:** 2026-09-24  
**Current native-Platinum integration branch:** `main`

## Decision

ID **919 is the current normalized Gen 1-9 canonical endpoint, not Mercury's ceiling**.

PT05C0 widened Platinum's packed 9-bit level-up move field to a true `u16`:

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
468-470. Its Hone Claws is donor ID 471 and Malignant Chain is donor ID 922.
Mercury removes those donor-only gaps, so donor IDs 471-922 map to canonical
Mercury IDs 468-919.

## DS rule: wide encoding, compact live IDs

The format is 16-bit, but the Nintendo DS runtime should not materialize giant
empty move-ID gaps. Platinum uses move IDs as direct table/NARC indexes, and the
battle AI contains `MoveTable moveTable[MAX_MOVES]`.

The original 2048 community start created **1,128 inert entries** between the
current official endpoint and the first community move. That was unnecessary.

The compact layout reserves only IDs **920-1023** for near-term official growth,
then starts community content at **1024**.

## Active allocation lanes

| Range | Lane | Capacity / use |
|---|---|---|
| 0 | `MOVE_NONE` | No move |
| 1-919 | Current official canonical | Current normalized Gen 1-9 set |
| 920-1023 | Official growth buffer | 104 future official slots |
| 1024-1599 | Community imports | 576 slots; enough for 519 current candidates + 57 spare |
| 1600-1791 | Mercury custom | 192 original Mercury moves |
| 1792-1919 | Boss / variant / signature | 128 Mega, Delta, boss, event, and signature moves |
| 1920-2047 | Experimental staging | 128 provisional development IDs |
| 2048-65534 | Inactive future space | Valid u16 space, not materialized without a new DS memory/table audit |
| 65535 | Sentinel | Permanently reserved |

The active DS soft ceiling is now **2047**.

## Community move numbering

The first certified community batches are renumbered compactly:

| Batch | Old temporary IDs | Current IDs |
|---|---:|---:|
| CM01 | 2048-2050 | **1024-1026** |
| CM02 | 2051-2053 | **1027-1029** |
| CM03 | 2054-2059 | **1030-1035** |

After CM03, `MAX_MOVES` sits at **1036**, not 2060.

## Rules

1. Existing official moves keep canonical IDs 1-919.
2. IDs 920-1023 are reserved for near-term official additions.
3. Community imports occupy 1024-1599.
4. The current 519-candidate community catalog fits without crossing ID 1599.
5. Mercury-original and signature moves use their own compact lanes.
6. Importers must fail on collisions.
7. ID 65535 is never a playable move.
8. Raising the active ceiling above 2047 requires a new build + battle-memory audit.
9. The 16-bit architecture remains available even though live DS allocation stays compact.

## Validation

Run:

```bash
python3 tools/audit_move_id_namespace.py
```

PT05C0 and downstream native-Platinum workflows run the namespace audit before
building.
