# DS03 Platinum → HG-Engine World Compatibility

## Confirmed compatibility

### Map matrices — direct format compatibility

The pinned Platinum and HeartGold source trees use the same serialized matrix layout:

1. width (u8)
2. height (u8)
3. has-header section (u8)
4. has-altitude section (u8)
5. name length (u8)
6. name bytes
7. optional u16 header IDs
8. optional u8 altitudes
9. u16 map/model IDs

The parser logic in both engines is materially identical. Platinum matrices therefore do not need geometric reconstruction. Header/model IDs must be remapped to their target IDs.

### Zone events — near-direct structural compatibility

Serialized sizes/semantics align closely:

- BG event: 20-byte compatible footprint
- Object event: 32 bytes on both
- Coord event: 16 bytes on both
- Warp event: 12 bytes on both

Platinum's final four warp bytes are unused; HGSS names the final u32 field `y`. Ordinary HGSS source warps commonly use `y: 0`, while actual transitions use x/z/header/anchor. The converter normalizes imported Platinum warps to `y: 0`.

The supplied converter translates source-level JSON field names and requires explicit mappings for symbols that differ between games.

### Map headers — remap, not direct copy

Both headers reference the same core concepts (area data, matrix, scripts, messages, day/night music, events, weather, camera, map type, battle background, travel permissions) but HGSS adds fields such as world-map coordinates, follow mode, phone/radio flags, and region number. A generated target header is required.

### Scripts — selective translation

Across the seven initial Twinleaf scripts, an initial lexical audit found 84 command/movement/helper tokens. 25 script commands match HGSS macro names exactly. Most remaining tokens are renamed commands, common-script helpers, or movement-action names.

We should translate only the commands actually used by the current Platinum region slice instead of porting Platinum's whole command interpreter.

## Twinleaf source-truth map IDs

- Main Twinleaf cell: `MAP_000` in `map_matrix_000`, cell x=3, y=27
- Generic northeast/southwest house: `MAP_180` through `map_matrix_123`
- Rival house 1F: `MAP_184` / `map_matrix_126`
- Rival house 2F: `MAP_185` / `map_matrix_127`
- Player house 1F: `MAP_186` / `map_matrix_128`
- Player house 2F: `MAP_187` / `map_matrix_129`

Platinum header IDs are 411–417 in that order, beginning with Twinleaf Town.

## Compatibility gates

Completed in DS03:
- [x] Validate Platinum land-data/map-model container against HGSS layout.
- [x] Resolve area-data/model/texture dependencies for `area_data_006` and `area_data_020`.
- [x] Allocate append-only HGSS map/header/script/event/message/visual resource ranges.
- [x] Validate all six real Twinleaf land-data members.
- [x] Remap every building/prop model actually placed by the six Twinleaf land-data members.
- [x] Validate required NSBMD and NSBTX source resources.
- [x] Generate and validate HGSS prop-set members.
- [x] Smoke-test Twinleaf zone-event conversion.

Remaining before the first **interactive/playable** Twinleaf proof:
- [ ] Build explicit Platinum→HGSS object-sprite mapping for Twinleaf NPC/event objects.
- [ ] Translate Twinleaf script commands and common-script calls.
- [ ] Rebuild/assign Twinleaf message banks.
- [ ] Generate target HGSS map headers and matrices in the build tree.
- [ ] Append converted resources to the target NARCs during a reproducible build.
- [ ] Boot first in the imported player room and validate rendering/collision/warps.
- [ ] Redirect normal New Game start only after the imported player house is certified.

The first transplant should remain isolated from `main` until it compiles and boots.


## DS03 certification evidence

The compatibility layer is certified by GitHub Actions run `35766528414` (job `106877351674`), which completed successfully on 2026-09-22.

The run verified the pinned Platinum and HeartGold sources, target capacity, area-data conversion, NSBMD/NSBTX source signatures, generated HGSS prop sets, all six real Twinleaf land-data conversions with model-ID remapping, the event conversion shape, and the append-only manifests.

DS03 certification means **the Twinleaf world resources are mechanically convertible and fully allocated**. It does not yet mean the imported maps have booted in HG-Engine; that is the next transplant/build phase.
