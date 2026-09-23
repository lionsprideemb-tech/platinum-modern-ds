# PT04G Generation VIII Complete Checkpoint — 2026-09-23

## Status

**COMPLETE / SEALED**

The canonical Generation VIII base roster is now proven end-to-end in Mercury DS through Enamorus #905.

## Canonical coverage

- Previous sealed boundary: Melmetal #809
- Gen VIII start: **Grookey #810**
- Gen VIII end: **Enamorus #905**
- Gen VIII species added: **96**
- Cumulative canonical native range: **#1–905**
- Native species ID continues to equal National Dex number.
- Egg and Bad Egg remain after the cumulative canonical roster.

## Sealed PT04G gates

### Donor audit

- Workflow: `PT04G Gen VIII Bulk Expansion Audit`
- Run ID: **35909127545**
- Commit: `c1fe60d1a16f0c7062bbf54b4458b06482782f10`
- Result: **success**
- 96/96 canonical Gen VIII species parsed
- missing required donor assets: **0**
- Enamorus female-only donor path verified

Checkpoint:

- `docs/PT04G_GEN8_DONOR_AUDIT_CHECKPOINT_2026-09-23.md`

### Cumulative bulk build

- Workflow: `PT04G Gen VIII Bulk Build`
- Run ID: **35909339161**
- Commit: `556a8c3314bc981b4c40ddb68e85aab50092a7fd`
- Result: **success**
- Artifact: `pt04g-gen8-bulk-build-proof`
- Artifact ID: **10772850579**

Compiled cumulative archives:

- `pl_personal.narc`: **920**
- `pl_pokegra.narc`: **5436**
- `pl_poke_icon.narc`: **959**
- `height.narc`: **3624**

Checkpoint:

- `docs/PT04G_GEN8_BULK_BUILD_CHECKPOINT_2026-09-23.md`

### Native save/reset/load proof

- Workflow: `PT04G Gen VIII Save Reload Runtime`
- Run ID: **35910244548**
- Commit: `552d5d8fc3b54ca017248fb6710c39eeed3bb425`
- Result: **success**
- Artifact: `pt04g-gen8-save-reload-runtime-proof`
- Artifact ID: **10773790221**
- Runtime stable through frame **4800**

Primary persisted boundary:

- Enamorus #905
- Lv.50
- party slot 0

Representative party:

1. Enamorus #905
2. Grookey #810
3. Toxtricity #849
4. Indeedee #876
5. Morpeko #877
6. Zacian #888

Checkpoint:

- `docs/PT04G_GEN8_SAVE_RELOAD_RUNTIME_CHECKPOINT_2026-09-23.md`

### Native Enamorus battle proof

- Workflow: `PT04G Enamorus Battle Runtime`
- Run ID: **35914335957**
- Commit: `391fead55d4a12d79ccfbbce720cded3398a5813`
- Result: **success**
- Artifact: `pt04g-enamorus-battle-runtime-proof`
- Artifact ID: **10774751962**
- Runtime stable through frame **4000**

Observed:

- Enamorus player-side back sprite rendered
- `ENAMORUS` name rendered
- Lv.50 rendered
- HP: **134/134**
- native battle command UI stable
- native Bidoof Lv.5 opponent stable

Checkpoint:

- `docs/PT04G_ENAMORUS_BATTLE_RUNTIME_CHECKPOINT_2026-09-23.md`

## Deferred mechanics remain intentionally separate

PT04G proves canonical base-species capacity. It does not silently approximate later mechanics.

Still deferred:

- modern abilities,
- modern moves and learnsets,
- modern evolution methods,
- base EXP field widening,
- alternate/regional/form semantics,
- cries and footprints final pass,
- localized Pokédex text,
- Mercury-specific custom forms and Megas.

Gen VIII compatibility observations remain explicit:

- **35 distinct modern ability constants** are not yet imported,
- **61 Gen VIII ability slots** currently use the explicit fallback path,
- **14 Gen VIII species** currently require the temporary >255 base-EXP compatibility handling,
- **0 Gen VIII held-item fallbacks** were required in the canonical batch.

## Recovery rule

If work resumes from this checkpoint:

- treat PT04C Victini testing as sealed,
- treat PT04D Generation V / Genesect as sealed,
- treat PT04E Generation VI / Volcanion as sealed,
- treat PT04F Generation VII / Melmetal as sealed,
- treat PT04G Generation VIII / Enamorus as sealed,
- do **not** rerun those runtime proofs unless a later regression directly invalidates one of their assumptions.

## Exact next unfinished gate

`PT04H_GEN9_DONOR_AUDIT`

Next canonical block:

- **Sprigatito #906**
- through **Pecharunt #1025**
- **120 species**

The next phase should first audit the complete Generation IX donor block and its required DS-compatible assets before creating the cumulative #1–1025 build.
