# PT04E Gen VI Bulk Build Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VI base-species block now configures and compiles cumulatively on top of the sealed Generation V resource layer.

## Scope

- Canonical National Dex range: **#650–721**
- First species: **Chespin**
- Last species: **Volcanion**
- Installed Gen VI species: **72**
- Sealed Gen V prerequisite species restored first: **156**
- Canonical native species IDs remain equal to National Dex numbers.

## Corrected CI proof

Final successful build:

- Workflow: `PT04E Gen VI Bulk Build`
- Run number: **3**
- Run ID: **35901819300**
- Commit: `87aa78505b8e73d78db061ad837322ab30397811`
- Conclusion: **success**
- Artifact: `pt04e-gen6-bulk-build-proof`
- Artifact ID: **10769432951**
- SHA-256: `e9d7de98f8e98af31f5d246603823bf95e03b6ef971b56fb8891316c38eed66f`

## Compiled archive proof

- `pl_personal.narc`: **736 members**
- `pl_pokegra.narc`: **4332 members**
- `pl_poke_icon.narc`: **775 members**
- `height.narc`: **2888 members**

These counts prove the cumulative native archives extend through Volcanion #721 while retaining existing Platinum alternate-form entries.

## Integration corrections made during this gate

Two issues were found and fixed without changing the sealed Gen V architecture:

1. HG donor gender ratio **222** maps to Platinum's `GENDER_RATIO_FEMALE_87_5` bucket.
2. Fresh Gen VI CI builds must restore the sealed Gen V generated resource directories before configuring a registry that now spans through #721.

The final successful run includes both corrections.

## Gen VI compatibility exceptions

PT04E continues the explicit compatibility policy rather than silently pretending modern mechanics are finished.

Current temporary measures:

- **11** Gen VI species have modern base EXP above 255 and are clamped to 255 pending field/runtime widening.
- **41 ability slots** fall back to `ABILITY_NONE`, representing **21 distinct modern ability constants** not yet imported.
- No Gen VI donor held-item constants required fallback in this base-species batch.
- Learnsets/evolution methods remain in their dedicated modern-mechanics phase.
- Alternate forms remain a separate form-registry pass.

## Next gate

`PT04E_GEN6_SAVE_RELOAD_RUNTIME`

Primary boundary species:

- **Volcanion #721**
- Level 50
- Party slot 0

The runtime proof will create a representative six-Pokémon Gen VI party, persist it through Platinum's native save/reset/load path, assert post-reload species/Pokédex state, and reopen the native Party UI for visual review.
