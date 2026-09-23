# PT04E Gen VI Bulk Expansion Complete — 2026-09-23

## Status

**COMPLETE / SEALED**

PT04E extends Mercury DS's canonical native base-species roster through the complete Generation VI block.

## Canonical range completed

- **Chespin #650**
- through **Volcanion #721**
- **72 species total**

Cumulative canonical coverage is now:

- #1–493 vanilla Platinum base roster,
- #494–649 sealed Gen V expansion,
- #650–721 sealed Gen VI expansion.

## Sealed gates

1. **Donor audit**
   - 72/72 species parsed.
   - 0 missing required front/back/icon resources.

2. **Native cumulative bulk build**
   - sealed Gen V resources restored first,
   - all 72 Gen VI species generated,
   - configure and ROM build passed,
   - compiled archives extend through #721.

3. **Native save/reload**
   - Volcanion #721 persisted through the real save/reset/load path,
   - six representative Gen VI species survived reload,
   - native Party UI rendered all six correctly.

4. **Native battle**
   - Volcanion #721 entered the native battle engine,
   - player-side back sprite/name/level/HP rendered correctly,
   - battle UI remained stable through frame 4000.

## Final compiled archive counts

- `pl_personal.narc`: **736**
- `pl_pokegra.narc`: **4332**
- `pl_poke_icon.narc`: **775**
- `height.narc`: **2888**

## Explicit deferred mechanics

Still intentionally deferred to later modern-mechanics/form phases:

- 21 distinct modern Gen VI ability constants,
- 11 >255 base-EXP values requiring widening,
- modern learnsets and move mechanics,
- modern evolution methods,
- breeding-line offspring import,
- modern cries/footprints,
- full localized Pokédex text,
- Gen VI alternate-form systems such as Vivillon patterns, flower colors, Furfrou trims, Meowstic form semantics, Aegislash Blade, Pumpkaboo/Gourgeist sizes, Zygarde forms, and Hoopa Unbound.

## Architecture retained

Canonical base species remain contiguous and equal to National Dex number.

At the full target:

- Pecharunt = **1025**
- Egg = **1026**
- Bad Egg = **1027**

Alternate forms remain a separate registry/resource layer and do not consume new canonical base-species IDs.

## Next phase

Begin the Generation VII canonical batch:

- **Rowlet #722**
- through **Melmetal #809**
- **88 base species**

Use the same proven pattern:

`audit -> cumulative resource generation -> compile archives -> representative save/reload -> upper-boundary battle`
