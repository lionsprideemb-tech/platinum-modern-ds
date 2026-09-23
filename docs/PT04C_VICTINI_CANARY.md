# PT04C — Victini Native Runtime Canary

PT04C adds exactly one post-Generation-IV base species: **Victini (#494)**.

This is deliberately a structural canary, not the final Victini data pass.

## What is real in this gate

- `SPECIES_VICTINI` is a distinct species ID after Arceus.
- The native Platinum species registry, personal-data archive, learnset archive,
  icon archive, battle-sprite archive, names, and Pokédex data all build with
  the additional species.
- Victini uses DS-format front/back battle sprites and icon art sourced from the
  pinned HG-Engine donor.
- Rowan's intro temporarily requests `SPECIES_VICTINI` through Platinum's
  normal Pokémon sprite loader so runtime proof exercises the new species ID.

## Intentionally temporary until PT05

- Victory Star is not imported yet, so the canary uses Synchronize.
- Modern-only Victini moves are not imported yet, so the canary uses a small
  Gen-IV-compatible learnset.
- The shiny palette currently mirrors the normal palette.
- The cry temporarily reuses Mew's valid native-format cry so archive expansion
  can be tested before modern cry import.

None of those placeholders are considered final game data.

## Gate

PT04C passes only when:
1. the ROM compiles with #494 present,
2. generated species data identifies Victini after Arceus,
3. the real ROM reaches Rowan's intro without a species/archive crash, and
4. emulator screenshots visibly show the Victini sprite loaded by the native
   Platinum Rowan-intro Pokémon path.
