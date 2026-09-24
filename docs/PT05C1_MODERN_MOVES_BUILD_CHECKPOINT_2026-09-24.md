# PT05C1 Modern Moves Build Checkpoint — 2026-09-24

## Status

**PASS**

GitHub Actions run: **#18**  
Run ID: `36046032172`

The PT05C1 normal ROM build completed successfully and uploaded the
`mercury-redux-pt05c1-modern-moves` artifact.

Artifact digest:

`sha256:6c215943cc426328c684c20db9a9a1523ebe4843184ecb31699119ff70791f2d`

## What is now proven

- 16-bit level-up move IDs compile in the normal Platinum build.
- The permanent move-ID namespace audit passes.
- HG-Engine's three compatibility/dummy slots are normalized out of the
  canonical Mercury numbering.
- Canonical Gen 5-9 move IDs installed by this donor pass are **468-919**.
- Hone Claws is canonical ID 468.
- Malignant Chain is canonical ID 919.
- 452 post-Gen-IV canonical moves are represented.
- 308 modern moves can currently reuse existing Platinum battle-effect support
  and are eligible for imported learnsets.
- 144 modern moves remain deliberately deferred until their effect and/or
  targeting support is ported.
- 532 post-Gen-IV species received compatible imported learnsets.
- The successful build reported 7,014 supported level-up move entries and 722
  currently unsupported/deferred level-up entries.
- Modern move text now preserves Platinum-supported Unicode correctly.
- Composite all-adjacent-plus-user targets are tracked explicitly and are not
  silently treated as complete.

## Important donor-numbering note

The pinned HG-Engine source keeps three inaccessible compatibility entries at
donor IDs 468-470. Its Hone Claws is donor ID 471 and Malignant Chain is donor
ID 922. Mercury translates donor IDs 471-922 down by three to the official
canonical range 468-919.

The 16-bit architecture remains much larger than this current canonical floor;
future official and Mercury-specific moves do not require another learnset
format migration.

## Next gate

**PT05C2 — modern battle-effect ports.**

The compatibility audit currently identifies:

- 141 modern moves requiring engine-extension effects,
- 117 unique new effect families,
- plus three moves whose composite target semantics require explicit target
  support before they can be enabled naturally.

Port effects in shared families first so one implementation unlocks multiple
moves, with focused battle tests after each batch.
