# DS03 Twinleaf Real-Map Validation

Pinned Platinum source:

`pret/pokeplatinum@c248fb3f8cc9934ded800e489567c5c0eeee92eb`

All six Twinleaf-related map members were inspected directly from the pinned repository.

| Platinum map | Source bytes | Permissions | Buildings | NSBMD | BDHC | BMD0 valid | HGSS-converted bytes |
|---|---:|---:|---:|---:|---:|---|---:|
| MAP_000 | 41486 | 2048 | 384 | 38876 | 162 | YES | 41490 |
| MAP_180 | 4956 | 2048 | 288 | 2456 | 148 | YES | 4960 |
| MAP_184 | 8066 | 2048 | 624 | 5092 | 286 | YES | 8070 |
| MAP_185 | 5330 | 2048 | 480 | 2556 | 230 | YES | 5334 |
| MAP_186 | 8006 | 2048 | 624 | 5040 | 278 | YES | 8010 |
| MAP_187 | 5394 | 2048 | 528 | 2572 | 230 | YES | 5398 |

Every source file satisfies:

- section-length totals exactly match the file size
- permissions section is exactly `0x800` bytes
- the NSBMD section begins with `BMD0`
- the HGSS transformation is a four-byte BGS insertion after the 16-byte size header
- all original DPPt section payloads remain byte-for-byte unchanged after the inserted BGS block

## Visual mapping

- `MAP_000` — Twinleaf exterior cell within Sinnoh's main matrix
- `MAP_180` — generic Twinleaf residence used by northeast/southwest houses
- `MAP_184` — rival house 1F
- `MAP_185` — rival house 2F
- `MAP_186` — player house 1F
- `MAP_187` — player house 2F

## Conclusion

The initial Twinleaf visual maps do not need to be redrawn or reconstructed for HG-Engine.

They can be mechanically converted from Platinum's native Gen IV land-data layout into HGSS layout, preserving movement permissions, building placements, NSBMD geometry, and BDHC terrain data.

Remaining dependencies are resource-ID remapping, area/building textures, map headers, events, scripts, messages, and target archive allocation.
