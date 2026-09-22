# DS02 Static Pokédex Coverage Result

## Result

**PASS — 1,025 / 1,025 canonical National Dex species have the required static coverage surfaces.**

Audit source:
- HG-Engine commit: `5157c501dc0e6f88ef1654ab121352a5cc9ed7de`
- Project audit workflow run: `35759037182`
- Audit branch commit: `cb9b6380aed75f595d8d1d051fba641be0310158`

Canonical boundaries:
- Count: **1025**
- First: `SPECIES_BULBASAUR`
- Last: `SPECIES_PECHARUNT`

## Missing counts

| Surface | Missing |
|---|---:|
| Master species data | 0 |
| Base experience | 0 |
| Hidden Ability table entry | 0 |
| Icon palette | 0 |
| Learnset | 0 |
| Battle front/back graphics | 0 |
| Follower properties | 0 |

Initial `minimum_complete_count`: **1025**

Initial `needs_review_count`: **0** for static coverage.

## What this proves

HG-Engine already contains a static data/art foundation for the entire canonical National Dex #001–1025 on the pinned revision.

This means Platinum Modern DS does **not** need a bulk species expansion/import merely to establish the 1,025 canonical Pokémon in species data, learnsets, basic graphics, icon palettes, Hidden Ability entries, follower properties, and experience data.

## What this does not prove

Static coverage does not certify every unusual modern behavior.

The next DS02 pass must audit:
- special form/state changes
- signature abilities
- signature move behavior
- unusual Gen VIII/IX evolution methods
- form persistence through party/PC/save/load
- cries and any other media not covered by this first audit
- cases where an existing asset is a placeholder rather than final-quality art

Those checks are tracked in `audits/DS02_BEHAVIOR_QUEUE.md`.

## Audit correction history

Run #1 incorrectly reported battle graphics missing for all 1,025 because the first detector searched generated `pokegra.mk` for species constants.

The corrected detector verifies the real source files at:

`data/graphics/sprites/<species>/male/front.png`
`data/graphics/sprites/<species>/male/back.png`

After that correction, battle graphics coverage is **1,025 / 1,025**.
