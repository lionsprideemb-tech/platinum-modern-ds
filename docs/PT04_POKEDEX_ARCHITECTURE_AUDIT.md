# PT04 — Pokédex Expansion Architecture Audit

Status: ACTIVE
Base: sealed Mercury title screen at `f09e5e9507b05c95262df903c80896a4d5b63685`
Pinned upstream: `pret/pokeplatinum@c248fb3f8cc9934ded800e489567c5c0eeee92eb`
Target: 1,025 canonical base species before Mercury-specific forms and custom species.

## Why PT04 starts with architecture

Platinum's build system is already unusually friendly to data-driven species expansion: the generated species list drives the per-species directory walk and the construction of personal data, evolutions, level-up learnsets, Pokédex data, sprites, icons, cries, footprints, names, and related archives.

The dangerous part is not the enum itself. The dangerous part is every old assumption around save data, forms, archive ordering, icons, Pokédex UI, scripts, and special-case species code. PT04 therefore expands the engine in controlled batches rather than appending hundreds of entries at once.

## Verified capacity facts

- Boxed Pokémon store `species` as `u16`. Base species IDs through 1025 are safe in the core Pokémon structure.
- The current generated species order is `NONE, #1..#493, EGG, BAD_EGG`. At the PT04 target it becomes `NONE, #1..#1025, EGG, BAD_EGG`; the highest base-system species sentinel is therefore 1027, still well below `UINT16_MAX`.
- `NATIONAL_DEX_COUNT` is derived from `MAX_SPECIES - 2`, rather than hard-coded to 493.
- Pokédex seen/caught/gender bitsets derive their size from `NATIONAL_DEX_COUNT`. They expand from 16 u32 words at 493 species to 33 u32 words at 1025 species.
- The Pokédex save entry reports `sizeof(Pokedex)` through `Pokedex_SaveSize`, and the save table uses that function. The larger Pokédex therefore participates in the save-layout calculation rather than relying on a fixed 493-species byte count.
- The normal save area is page/sector based, so PT04 must certify total block fit after the expanded structures are introduced.
- Species graphics/data archives are assembled from `generated/species.txt` and per-species resource directories. Expansion therefore requires a complete asset/data slot for every new registered species.
- Existing icon code rejects species IDs greater than `NATIONAL_DEX_COUNT`; that comparison naturally follows the expanded count once the species registry is extended.

## Hard blocker discovered: form storage

Platinum stores the persistent Pokémon form in a 5-bit field:

`u8 form : 5;`

That provides form IDs 0–31. This is sufficient for most species, but it is not a safe universal representation for every modern form family if all forms are represented directly with vanilla semantics.

PT04 will therefore keep **base-species expansion** and **extended-form architecture** as separate concerns:

1. Expand canonical base species safely to 1025.
2. Preserve the existing 5-bit form field for species that fit naturally.
3. Add an extended-form indirection only for species/custom systems that genuinely require more than 31 persistent form IDs.
4. Do not enlarge the encrypted BoxPokemon layout casually; save compatibility and trade/battle assumptions depend on its fixed block structure.

## PT04 gates

### PT04A — Capacity audit
- Verify species ID width.
- Verify Pokédex sizing.
- Verify save-table sizing is dynamic.
- Inventory form-width constraints.
- Inventory explicit `SPECIES_ARCEUS` / legacy-form switch points that require modern handling.
- Produce machine-readable audit output in CI.

### PT04B — Registry expansion harness
- Move the project-owned species registry into the overlay.
- Add build-time checks for contiguous base-species IDs.
- Add explicit sentinels after #1025.
- Ensure every registered species has required data/assets before build.

### PT04C — First post-Gen-IV batch
- Add a deliberately small Gen V batch first.
- Build all species archives.
- Spawn at least one new species in native Platinum runtime.
- Validate party, summary, battle, icon, sprite, cry, save/reload, and Pokédex encounter/capture behavior.

### PT04D — Batch expansion
- Expand in controlled generation batches through #1025.
- Runtime-certify each generation boundary.
- Keep custom Mercury forms/Megas out of the base-species numbering until the canonical registry is stable.

## Non-negotiable runtime gates

A species batch is not complete merely because the ROM compiles. Before certification, a newly added species must survive:

- creation and party storage,
- battle entry,
- front/back sprite loading,
- icon loading,
- level/stat calculation,
- ability lookup,
- move lookup,
- evolution lookup,
- Pokédex seen/caught state,
- save and reload,
- PC deposit/withdraw,
- summary screen display.

PT04 will use real emulator proof for these gates, consistent with the project rule established by the Mercury title work.
