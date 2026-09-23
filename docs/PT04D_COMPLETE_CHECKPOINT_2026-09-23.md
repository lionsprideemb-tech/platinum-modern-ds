# PT04D Gen V Bulk Expansion Complete — 2026-09-23

## Status

**COMPLETE / SEALED**

PT04D expanded Mercury DS from the single post-Gen-IV boundary proof into the complete canonical Generation V base roster.

## Canonical range completed

- **Victini #494**
- through **Genesect #649**
- **156 species total**

Canonical base-species IDs remain equal to National Dex numbers.

## Sealed gates

1. **Donor audit**
   - 156/156 species parsed from the pinned HG-Engine donor.
   - 0 missing required front/back/icon resources.

2. **Native bulk build**
   - full Gen V batch configured and compiled together.
   - corrected dual-gender sprite member ordering verified.
   - compiled archive counts:
     - `pl_personal.narc`: **664**
     - `pl_pokegra.narc`: **3900**
     - `pl_poke_icon.narc`: **703**
     - `height.narc`: **2600**

3. **Native save/reload**
   - Genesect #649 persisted through `FieldSystem_Save`.
   - DS reset routed through Platinum's native load-save path.
   - six representative Gen V species survived reload.
   - post-reload Party UI rendered all six species/icons correctly.

4. **Native battle**
   - Genesect #649 entered the native battle engine.
   - player back sprite/name/level/HP and Download message rendered correctly.
   - battle command UI remained stable through frame 4000.

## Explicit deferred mechanics

PT04D proves species/data/resource capacity; it does not pretend the later mechanics work is complete.

Still deferred to the modern-mechanics phases:

- 28 distinct modern ability constants,
- 26 >255 base-EXP values requiring field/runtime widening,
- Absorb Bulb item support,
- modern learnsets/moves,
- modern evolution methods,
- breeding-line offspring import,
- modern cries and footprints,
- complete localized Pokédex text.

These exceptions remain explicit in the PT04D reports and are not silently discarded.

## Authoritative numbering

Canonical base species remain contiguous:

`NONE, #1..#1025, EGG, BAD_EGG`

At the full-roster target:

- Pecharunt = **1025**
- Egg = **1026**
- Bad Egg = **1027**

HG-Engine's offset species IDs are donor implementation details and are never copied into Mercury DS.

## Next phase

Begin the next canonical batch:

- **Chespin #650**
- through **Volcanion #721**
- **72 Generation VI base species**

Use the same proven diagnostic-first pattern:

`audit -> generate -> compile archives -> representative save/reload -> upper-boundary battle`
