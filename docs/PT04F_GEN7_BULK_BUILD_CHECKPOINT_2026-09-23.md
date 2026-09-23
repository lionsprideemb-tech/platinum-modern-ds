# PT04F Gen VII Bulk Build Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VII base-species block now configures and compiles cumulatively on top of the sealed Generation V and Generation VI resource layers.

## Scope

- Canonical National Dex range: **#722–809**
- First species: **Rowlet**
- Last species: **Melmetal**
- Installed Gen VII species: **88**
- Sealed Gen V prerequisite species restored first: **156**
- Sealed Gen VI prerequisite species restored next: **72**
- Canonical native species IDs remain equal to National Dex numbers.

## CI proof

- Workflow: `PT04F Gen VII Bulk Build`
- Run number: **1**
- Run ID: **35904711207**
- Commit: `0b5e3d231654687d296e5e9b239ce7172f4fe325`
- Conclusion: **success**
- Artifact: `pt04f-gen7-bulk-build-proof`
- Artifact ID: **10770922035**
- SHA-256: `b1ff7c2e7ce34b1de2e41af30101f58b2dd398775bd593764930fa923f2eae6a`

## Compiled archive proof

- `pl_personal.narc`: **824 members**
- `pl_pokegra.narc`: **4860 members**
- `pl_poke_icon.narc`: **863 members**
- `height.narc`: **3240 members**

These are the exact cumulative counts expected after adding 88 Gen VII canonical base species to the sealed Gen VI build.

## Resource import status

The Gen VII batch preserves donor-derived base data and DS resources for all 88 canonical species.

Representative proof points:

- Rowlet #722 — Grass/Flying, donor sprites/icons/data installed.
- Melmetal #809 — Steel, donor resources installed at the upper boundary.

## Explicit compatibility exceptions

PT04F continues the explicit compatibility policy:

- **26** Gen VII species have modern base EXP values above 255 and are temporarily clamped to 255.
- **60 ability slots** fall back to `ABILITY_NONE`, representing **39 distinct modern abilities** not yet imported.
- **6 held-item slots** fall back to `ITEM_NONE`, representing:
  - `ITEM_CELL_BATTERY`
  - `ITEM_ELECTRIC_SEED`
  - `ITEM_GRASSY_SEED`
  - `ITEM_MISTY_SEED`
- modern learnsets/evolution methods remain deferred to their dedicated mechanics phase,
- alternate forms remain a separate form-registry pass.

## Next gate

`PT04F_GEN7_SAVE_RELOAD_RUNTIME`

Primary boundary species:

- **Melmetal #809**
- Level 50
- Party slot 0

The representative persistence party is:

1. Melmetal #809 — upper Gen VII boundary
2. Rowlet #722 — first Gen VII species / starter
3. Oricorio #741 — multi-form base resource path
4. Salazzle #758 — female-only species path
5. Silvally #773 — type/form-sensitive base data
6. Mimikyu #778 — form-heavy base resource path

The test must use Platinum's native save/reset/load path and visually review the post-reload Party screen before proceeding to battle.
