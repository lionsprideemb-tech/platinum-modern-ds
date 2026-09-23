# PT04D Gen V Bulk Build Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The full canonical Generation V base-species block now configures and compiles together in the native Platinum resource pipeline.

## Scope

- Canonical National Dex range: **#494–649**
- First species: **Victini**
- Last species: **Genesect**
- Installed species: **156**
- Canonical native IDs remain equal to National Dex numbers.
- Donor content is mapped by species identity, not HG-Engine's offset numeric IDs.

## Corrected CI proof

The final sealed build includes the corrected Platinum dual-gender sprite member ordering:

1. female back
2. male back
3. female front
4. male front

Single-gender/genderless species emit only the native entries that exist.

Final build run:

- Workflow: `PT04D Gen V Bulk Build`
- Run number: **3**
- Run ID: **35893532810**
- Commit: `eabcbbcf790aeca9611890b8a4ccd48ffbc7584d`
- Conclusion: **success**
- Artifact: `pt04d-gen5-bulk-build-proof`
- Artifact ID: **10765843795**
- SHA-256: `63eaf6310b010e13784476294f7641149b379d3379cccc61bc12621218f97d8b`

## Compiled archive proof

- `pl_personal.narc`: **664 members**
- `pl_pokegra.narc`: **3900 members**
- `pl_poke_icon.narc`: **703 members**
- `height.narc`: **2600 members**

These counts prove the native compiled archives extend through Genesect while retaining the pre-existing Platinum alternate-form entries.

## Resource import status

Authentic pinned HG-Engine donor data/resources are used for the PT04D species-capacity layer, including:

- base stats,
- types,
- catch rates,
- EV yields,
- gender ratios,
- hatch cycles,
- friendship,
- growth rates,
- egg groups,
- compatible abilities,
- compatible held items and known naming aliases,
- body color/shape and Pokédex metrics,
- front/back battle sprites by available gender,
- icons,
- normal and shiny palettes,
- sprite animation/frame/shadow metadata.

## Explicit PT05 compatibility exceptions

PT04D does not silently pretend modern mechanics are complete.

Current temporary build compatibility measures:

- **26** species have modern base EXP values above 255 and are clamped to 255 until the field/runtime is widened.
- **78 ability slots** use `ABILITY_NONE`, representing **28 distinct modern abilities** not yet imported.
- **4 held-item slots** using `ITEM_ABSORB_BULB` fall back to `ITEM_NONE`.
- Five other donor item names are translated to their existing Platinum constant spellings.
- Learnsets remain compatibility-only pending the modern move import.
- Evolution tables remain deferred pending modern evolution-method support.
- Modern cries and footprints remain later asset passes.
- Full localized Pokédex text remains later content work.

## Next gate

`PT04D_GEN5_SAVE_RELOAD_RUNTIME`

The next runtime proof intentionally places **Genesect #649** in party slot 0. This is important because #649 crosses the 511/512 species-ID boundary that the sealed Victini #494 PT04C proof could not exercise.

The runtime representative party is:

1. Genesect #649 — upper Gen V / >511 boundary
2. Victini #494 — first post-Gen-IV species
3. Snivy #495 — ordinary Gen V starter
4. Cottonee #546 — Fairy-enabled modern typing
5. Deerling #585 — dual-gender resource path
6. Mandibuzz #630 — female-only resource path

The test must save, reset through Platinum's native load path, assert the six-species party after reload, and reopen the native Party application for visual review.
