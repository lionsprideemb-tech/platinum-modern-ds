# PT04G Gen VIII Bulk Build Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VIII base-species block now configures and compiles cumulatively on top of the sealed Generation V, VI, and VII resource layers.

## Scope

- Canonical National Dex range: **#810–905**
- First species: **Grookey**
- Last species: **Enamorus**
- Installed Gen VIII species: **96**
- Sealed Gen V prerequisite species restored first: **156**
- Sealed Gen VI prerequisite species restored next: **72**
- Sealed Gen VII prerequisite species restored next: **88**
- Canonical native species IDs remain equal to National Dex numbers.
- Egg and Bad Egg remain immediately after the cumulative canonical roster.

## CI proof

- Workflow: `PT04G Gen VIII Bulk Build`
- Run number: **1**
- Run ID: **35909339161**
- Commit: `556a8c3314bc981b4c40ddb68e85aab50092a7fd`
- Conclusion: **success**
- Artifact: `pt04g-gen8-bulk-build-proof`
- Artifact ID: **10772850579**
- SHA-256: `43e1dba37b24df6c991d5972c3817535dcbf38ba990f185b14b7f84761728151`

All workflow steps completed successfully, including donor re-audit, prerequisite restoration, Gen VIII batch installation, Platinum configuration, ROM compilation, cumulative archive verification, and proof upload.

## Compiled archive proof

- `pl_personal.narc`: **920 members**
- `pl_pokegra.narc`: **5436 members**
- `pl_poke_icon.narc`: **959 members**
- `height.narc`: **3624 members**

These are the exact cumulative counts expected after extending the sealed Gen VII build through Enamorus #905.

## Resource import status

The Gen VIII batch installed all 96 canonical base species and their donor-derived DS resources.

Representative boundary and stress proof points:

- Grookey #810 — first Gen VIII canonical species.
- Toxtricity — representative modern species resource path.
- Morpeko — representative form-sensitive base resource path.
- Zacian — legendary resource/data path.
- Enamorus #905 — upper Gen VIII boundary using the corrected female donor sprite path.

## Explicit compatibility exceptions

PT04G preserves the existing explicit compatibility policy rather than silently approximating later mechanics:

- **14** Gen VIII species have modern base EXP values above 255 and are temporarily clamped to 255.
- **61 ability slots** fall back to `ABILITY_NONE`, representing **35 distinct modern ability constants** not yet imported.
- **0 held-item fallbacks** were required for the Gen VIII canonical batch.
- modern learnsets and evolution methods remain deferred to their dedicated mechanics phase,
- alternate/regional/form semantics remain a separate form-registry pass,
- cries, footprints, localized Pokédex text, and Mercury-specific custom forms/Megas remain later dedicated passes.

## Next gate

`PT04G_GEN8_SAVE_RELOAD_RUNTIME`

Primary persistence boundary:

- **Enamorus #905**
- Level 50
- Party slot 0

The runtime phase must use Platinum's native save -> DS reset -> native reload path, then visually verify a representative six-species Generation VIII party before proceeding to the Enamorus native battle gate.

Do **not** begin Generation IX until the Gen VIII persistence and battle gates are independently sealed.
