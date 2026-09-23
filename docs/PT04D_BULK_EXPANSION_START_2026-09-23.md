# PT04D Bulk Expansion Start Checkpoint — 2026-09-23

## Status

**ACTIVE — Gen V batch audit started**

PT04C is sealed and must not be repeated. PT04D scales the proven Platinum-native species path from the single #494 boundary proof into controlled generation-sized batches.

## Authoritative base-species numbering

Mercury DS uses contiguous canonical base-species IDs:

- Bulbasaur = 1
- Arceus = 493
- Victini = 494
- Genesect = 649
- Volcanion = 721
- Melmetal = 809
- Enamorus = 905
- Pecharunt = 1025
- Egg sentinel = 1026
- Bad Egg sentinel = 1027

For canonical base species, **native species ID equals National Dex number**.

HG-Engine's donor constants place Victini at 544 because HG-Engine preserves legacy HGSS form/resource slots in its own species-numbering scheme. Those donor numeric IDs are not authoritative for Mercury DS. Donor data and assets must be translated by species constant/name and canonical National Dex position, never by copying HG-Engine's raw numeric species ID.

Legacy forms, regional forms, Megas, and Mercury custom species remain separate from the canonical base-species numbering architecture.

## First PT04D batch

Initial controlled batch:

- National Dex #494–649
- Victini through Genesect
- 156 canonical Gen V base species

The batch process is diagnostic-first:

1. Parse every target species from the pinned HG-Engine donor by species constant.
2. Verify required front sprite, back sprite, and icon assets.
3. Inventory donor type, ability, held-item, growth-rate, egg-group, and base-EXP values.
4. Report unsupported/overflow modern fields explicitly.
5. Only after the audit passes, generate Platinum-compatible per-species resource directories.
6. Build expanded archives for the whole batch.
7. Use representative runtime spot tests and the generation boundary, rather than repeating PT04C's full lifecycle for all 156 species.

## PT05 boundary

PT04D establishes canonical species/data/resource capacity. It must not silently solve later mechanics by inventing substitutions.

Items that require engine widening or modern battle-system work remain PT05 concerns, including:

- modern abilities not yet present in Platinum,
- post-Gen-IV moves and complete modern learnsets,
- base EXP values above Platinum's current one-byte personal-data field,
- new evolution methods not yet implemented,
- extended form semantics.

Temporary compatibility values, if required for a PT04D build gate, must be explicit in the audit/report and later replaced by PT05.

## Current implementation

- Branch: `feature/pt04d-bulk-expansion`
- PT04C base commit: `a0a98d16e8b492dcf92b34aef58d2fb168a56b15`
- Corrected contiguous ID-map tool committed.
- Gen V donor audit tool: `tools/audit_pt04d_species_batch.py`
- CI workflow: `.github/workflows/pt04d-gen5-bulk-audit.yml`

## Next gate

The immediate next gate is:

`PT04D_GEN5_DONOR_AUDIT`

It must account for all 156 canonical species and all required donor battle sprites/icons before the generator phase begins.
