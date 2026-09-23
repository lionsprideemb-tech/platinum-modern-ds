# PT04D Gen V Save/Reload Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The Gen V batch has now crossed the important native runtime persistence boundary beyond species ID 511.

## CI proof

- Workflow: `PT04D Gen V Save Reload Runtime`
- Run number: **1**
- Run ID: **35894277217**
- Commit: `96da38a47e6e877c0aa8b6e89066e2e62fcc3da4`
- Conclusion: **success**
- Artifact: `pt04d-gen5-save-reload-runtime-proof`
- Artifact ID: **10766576690**
- SHA-256: `26a4320c07c10f6034e95992a4c43829acb6a843864b4aec6c2bd9a0f8c9431e`

## Boundary under test

Primary persisted species:

- **Genesect**
- National Dex / native species ID: **649**
- Party slot: **0**
- Level: **50**

This is intentionally stronger than PT04C's Victini #494 proof because #649 crosses the 511/512 boundary.

## Representative party

The native gift-mon path created six Gen V representatives before saving:

1. Genesect #649 — upper Gen V / >511 boundary
2. Victini #494 — first post-Gen-IV species
3. Snivy #495 — ordinary Gen V starter
4. Cottonee #546 — Fairy-enabled modern typing
5. Deerling #585 — dual-gender resource path
6. Mandibuzz #630 — female-only resource path

The harness then used Platinum's native `FieldSystem_Save`, reset through `RESET_ERROR`, reloaded through `gGameStartLoadSaveAppTemplate -> SaveData_Load`, asserted the party/Pokédex state, and reopened the native Party application.

## Runtime assertions passed

- Party count after reload == 6
- Slot 0 species == `SPECIES_GENESECT`
- Slot 0 level == 50
- Genesect seen/caught flags survived reload
- Victini remained in party
- Snivy remained in party
- Cottonee remained in party
- Deerling remained in party
- Mandibuzz remained in party
- Cottonee caught flag survived reload
- Mandibuzz caught flag survived reload

## Visual review

The post-reload Party screen was visually reviewed at frames 1800, 2400, and 4800.

Observed:

- `GENESECT` Lv.50, 142/142 HP
- `VICTINI` Lv.50, 163/163 HP
- `SNIVY` Lv.50, 117/117 HP
- `COTTONEE` Lv.50, 113/113 HP
- `DEERLING` Lv.50, 124/124 HP
- `MANDIBUZZ` Lv.50, 176/176 HP
- all six party icons rendered
- gender markers behaved sensibly, including female-only Mandibuzz
- screen remained stable through the final 4800-frame capture
- no emulator stop or assertion failure occurred

## What this proves

PT04D now has native evidence for:

- canonical species IDs through #649,
- whole-Gen-V compiled data/resources,
- party creation for multiple Gen V species,
- native Pokédex capture flags above #511,
- native save serialization above #511,
- native load/reconstruction above #511,
- native party/icon rendering for representative Gen V species.

## Next gate

`PT04D_GEN5_GENESECT_BATTLE_RUNTIME`

Use Genesect #649 as the player's lead and enter Platinum's native battle engine against a low-risk vanilla opponent. The proof must visually confirm Genesect's player-side battle sprite/name/HP and remain stable long enough to rule out an archive-index or sprite-metadata failure.
