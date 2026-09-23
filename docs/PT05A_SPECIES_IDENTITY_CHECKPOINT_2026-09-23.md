# PT05A Species Identity Layer — Checkpoint 2026-09-23

## Status

**PASS / SEALED**

PT05A establishes the production Mercury DS identity model for the full canonical roster. National Dex numbers are now explicitly separated from DS internal species IDs so Platinum/HG-Engine reserved slots remain stable.

## Production ID contract

- SPECIES_NONE: internal 0
- National Dex 1-493: internal IDs 1-493
- SPECIES_EGG: internal 494
- SPECIES_BAD_EGG: internal 495
- legacy/reserved DS IDs: 496-543
- National Dex 494-1025: internal ID = National Dex + 50
- Victini: NatDex 494 -> internal 544
- Genesect: NatDex 649 -> internal 699
- Pecharunt: NatDex 1025 -> internal 1075

## CI proof

- Workflow: `PT05A Species Identity Layer`
- Run number: **1**
- Run ID: **35891492739**
- Head commit: `edbf92762f4bb228866a2d0887b25155c66ea859`
- Conclusion: **success**

Artifact:
- Name: `pt05a-species-identity-proof`
- Artifact ID: **10765835558**
- SHA-256: `43b82b82072c93c948ec1c4e7b1712864da93e0a3be20eb273c8435189fdf1cf`

## Proven checks

- Exactly 1,025 canonical National Dex species are present.
- All canonical National Dex numbers map to unique internal species IDs.
- All 1,025 NatDex -> internal -> NatDex round trips pass.
- Egg, Bad Egg and IDs 496-543 map to canonical NatDex 0.
- Pinned HG-Engine constants match the Mercury DS production mapping.
- Generated C lookup tables and a JSON identity map are produced for later engine integration.

## Added infrastructure

- `tools/generate_ds_species_identity_tables.py`
- `.github/workflows/pt05a-species-identity.yml`
- Existing `tools/build_ds_species_id_map.py` is retained as the authoritative mapping model.

## Why this differs from PT04C

PT04C intentionally used Victini directly at the first post-Arceus boundary to prove that pokeplatinum could carry a species beyond Gen IV through Party, Pokédex, Summary, PC, Battle and Save/Reload.

Production Mercury DS must also remain compatible with the HG-Engine/DS reserved internal-ID layout. PT05A therefore formalizes Victini as internal ID 544 while retaining National Dex 494.

PT04C remains a valid engine-boundary proof; PT05A defines the production identity architecture.

## Next gate

`PT05B_DECOUPLE_POKEPLATINUM_DEX_AND_INTERNAL_SPECIES_INDEXING`

PT05B must audit and patch engine/build paths that currently assume internal species ID and National Dex number are the same value.
