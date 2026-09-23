# PT04H Gen IX Bulk Build Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation IX base-species block now configures and compiles cumulatively on top of the sealed Generation V, VI, VII, and VIII resource layers.

This is the first Mercury DS cumulative build with the full canonical National Dex base roster from **#1 through #1025** present as native contiguous species IDs.

## Scope

- Canonical Gen IX range: **#906–1025**
- First Gen IX species: **Sprigatito**
- Last canonical species: **Pecharunt**
- Installed Gen IX species: **120**
- Sealed Gen V prerequisite species restored first: **156**
- Sealed Gen VI prerequisite species restored next: **72**
- Sealed Gen VII prerequisite species restored next: **88**
- Sealed Gen VIII prerequisite species restored next: **96**
- Cumulative canonical native range: **#1–1025**
- `SPECIES_EGG`: **1026**
- `SPECIES_BAD_EGG`: **1027**

## CI proof

- Workflow: `PT04H Gen IX Bulk Build`
- Run number: **1**
- Run ID: **35915346631**
- Commit: `5b7ac49f47cc3beb9cc0086ec6f01ff1663fcbfa`
- Conclusion: **success**
- Artifact: `pt04h-gen9-bulk-build-proof`
- Artifact ID: **10775416298**
- SHA-256: `f00a220cb5b1abc3d2d09527e3284af630e15c8f221a91096b1fb7b0f7d6b7c1`

Every build gate completed successfully:

- canonical registration through #1025,
- Gen IX donor re-audit,
- sealed Gen V–VIII resource regeneration,
- installation of all 120 Gen IX canonical species,
- Mercury title-resource regeneration,
- Platinum configuration,
- full ROM compilation,
- cumulative NARC archive verification,
- proof upload.

## Compiled archive proof

The compiled ROM produced the exact expected final cumulative archive counts:

- `pl_personal.narc`: **1040 members**
- `pl_pokegra.narc`: **6156 members**
- `pl_poke_icon.narc`: **1079 members**
- `height.narc`: **4104 members**

These counts match the expected archive expansion after extending the sealed Gen VIII build by all 120 canonical Generation IX base species.

## Representative resource proof points

The build explicitly verified generated data/resources for:

- Sprigatito #906 — first Gen IX boundary
- Palafin #964 — form-sensitive modern species
- Kingambit #983 — modern evolution-line boundary
- Koraidon #1007 — legendary / Paradox-era resource path
- Terapagos #1024 — form-heavy late boundary
- Pecharunt #1025 — final canonical National Dex boundary

## Compatibility exceptions remain explicit

PT04H continues the capacity-first policy rather than silently implementing later mechanics.

For the Gen IX batch:

- **44 species** have modern base EXP values above 255 and currently use the temporary compatibility clamp,
- **83 ability slots** use `ABILITY_NONE` fallback,
- those slots represent the **47 distinct modern ability constants** identified in the sealed Gen IX donor audit,
- **0 held-item fallbacks** were required.

Still deferred to dedicated mechanics phases:

- modern abilities,
- modern moves and learnsets,
- modern evolution methods,
- base EXP field widening,
- alternate/regional/form semantics,
- final cries and footprints,
- localized Pokédex text,
- Mercury-specific custom forms and Megas.

## What this proves

Mercury DS can now configure and compile Platinum with a contiguous canonical native base-species registry spanning:

`Bulbasaur #1 -> Pecharunt #1025`

with Egg and Bad Egg moved safely after the complete canonical roster.

This is a compile/resource-capacity proof. The final Gen IX persistence and native battle gates still must be completed before PT04H is closed.

## Exact next gate

`PT04H_GEN9_SAVE_RELOAD_RUNTIME`

Primary boundary:

- **Pecharunt #1025**
- Level 50
- Party slot 0

The next phase must use Platinum's native save -> DS reset -> native reload path, visually verify a representative six-species Generation IX party, and only then proceed to native Pecharunt battle proof.

Do not repeat the sealed Generation V–VIII runtime proofs unless a later regression directly invalidates them.
