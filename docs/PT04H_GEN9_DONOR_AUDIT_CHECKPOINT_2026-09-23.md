# PT04H Gen IX Donor Audit Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation IX base-species block is present in the pinned HG-Engine donor and passes the Mercury DS pre-build compatibility audit.

## Scope

- Canonical National Dex range: **#906–1025**
- First species: **Sprigatito**
- Last species: **Pecharunt**
- Expected species: **120**
- Parsed species: **120**
- Missing donor entries: **0**
- Missing required front/back/icon assets: **0**
- Unsupported raw gender-ratio encodings: **0**
- Unsupported donor types: **0**
- Unsupported held items: **0**

## CI proof

- Workflow: `PT04H Gen IX Bulk Expansion Audit`
- Run number: **1**
- Run ID: **35915053989**
- Commit: `02bd0dc90da934b6107dcdb1df80397b58fda2f8`
- Conclusion: **success**
- Artifact: `pt04h-gen9-donor-audit`
- Artifact ID: **10774837119**
- SHA-256: `b17506da214beaa59a71c770b41ec8a4fa4ab92d9e4da5cc3f34cd01d2a3c113`

## Canonical ID proof

The full architecture remains intact:

- Sprigatito National Dex #906 -> native species ID **906**
- Pecharunt National Dex #1025 -> native species ID **1025**
- `SPECIES_EGG` -> **1026**
- `SPECIES_BAD_EGG` -> **1027**

This confirms Generation IX can occupy the final contiguous canonical base-species block without colliding with sentinels.

## Compatibility findings

Already compatible with the current Mercury Platinum layer:

- all Gen IX base types used by the canonical block,
- all held-item constants used by the canonical block,
- all translated growth rates,
- all egg groups,
- all raw gender-ratio encodings,
- all required donor sprite/icon resources.

Explicit later-mechanics exceptions:

- **47 distinct ability constants** used by Gen IX are not yet present in the current mechanics layer and remain deferred.
- **44 Gen IX species** have modern base EXP values above Platinum's current one-byte field and remain part of the planned base-EXP widening phase.

Representative >255 base-EXP cases include:

- Meowscarada / Skeledirge / Quaquaval — 265
- Kingambit — 275
- Great Tusk and the other initial Paradox species — 285
- Baxcalibur — 300
- Koraidon / Miraidon — 335
- Archaludon — 300
- Pecharunt — 300

No Gen IX held-item fallback was required by the donor audit.

## Important modern ability examples still deferred

The 47 unsupported constants include modern mechanics such as:

- Protosynthesis
- Quark Drive
- Orichalcum Pulse
- Hadron Engine
- Good as Gold
- Supreme Overlord
- Zero to Hero
- Commander
- Tera Shift
- Poison Puppeteer
- Toxic Chain
- Hospitality
- Supersweet Syrup

These remain explicit later-mechanics work and do not block proving canonical base-species capacity.

## Next gate

`PT04H_GEN9_BULK_BUILD`

Resume by:

1. register the canonical base roster continuously through **Pecharunt #1025**,
2. restore the sealed generated resource layers for Gen V, VI, VII, and VIII,
3. generate/install the **120-species Gen IX batch**,
4. configure and compile the cumulative Platinum ROM,
5. verify personal, battle-sprite, icon, and height archives through #1025,
6. only after the build is sealed, run the native save/reset/load proof using **Pecharunt #1025** as the upper boundary,
7. then run native Pecharunt battle rendering proof.

Do not redo the sealed Generation V–VIII runtime proofs unless a later regression directly requires it.
