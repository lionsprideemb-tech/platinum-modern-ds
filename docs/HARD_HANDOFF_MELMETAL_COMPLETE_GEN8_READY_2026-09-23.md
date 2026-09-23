# Mercury DS Hard Handoff Checkpoint — Melmetal Complete / Gen VIII Audit Ready — 2026-09-23

## Purpose

This is the recovery checkpoint requested before continuing farther past Melmetal testing.

If a chat, stream, or Work session is lost, resume from this document and the snapshot branch created from its commit. Do **not** restart PT04C/PT04D/PT04E/PT04F runtime work.

---

## Current authoritative state

Active development branch at checkpoint creation:

- `feature/pt04g-gen8-bulk-expansion`

Pre-checkpoint head:

- `c1fe60d1a16f0c7062bbf54b4458b06482782f10`

Canonical base-species architecture remains:

- native species ID == National Dex number,
- canonical base species remain contiguous,
- full target remains #1–1025,
- Egg/Bad Egg remain after the full canonical roster.

---

# PT04F — Generation VII / Melmetal

## Status

**COMPLETE / SEALED**

Generation VII canonical base range:

- Rowlet #722
- through Melmetal #809
- 88 species total

Cumulative canonical coverage after PT04F:

- **#1–809**

### Sealed Gen VII bulk build

- Workflow: `PT04F Gen VII Bulk Build`
- Run: **#1**
- Run ID: **35904711207**
- Commit: `0b5e3d231654687d296e5e9b239ce7172f4fe325`
- Conclusion: **success**
- Artifact: `pt04f-gen7-bulk-build-proof`
- Artifact ID: **10770922035**
- Artifact SHA-256: `b1ff7c2e7ce34b1de2e41af30101f58b2dd398775bd593764930fa923f2eae6a`

Compiled cumulative archive proof:

- `pl_personal.narc`: **824**
- `pl_pokegra.narc`: **4860**
- `pl_poke_icon.narc`: **863**
- `height.narc`: **3240**

### Sealed Melmetal save/reset/load proof

- Workflow: `PT04F Gen VII Save Reload Runtime`
- Run: **#1**
- Run ID: **35905367563**
- Commit: `207dec993afb2275dd6dad6becc8167bfb10ce47`
- Conclusion: **success**
- Artifact: `pt04f-gen7-save-reload-runtime-proof`
- Artifact ID: **10770249475**
- Artifact SHA-256: `45903e99f2a8e21a29c0bd6bde722515269f55ced428adbf4ab52d68570a8bd0`

Primary persistence boundary:

- **Melmetal #809**
- Lv.50
- party slot 0

Representative post-reload party:

1. Melmetal #809
2. Rowlet #722
3. Oricorio #741
4. Salazzle #758
5. Silvally #773
6. Mimikyu #778

Visual proof remained stable through frame 4800.

Observed Melmetal after reload:

- `MELMETAL`
- Lv.50
- **202/202 HP**

All six representative icons rendered correctly.

### Sealed Melmetal native battle proof

- Workflow: `PT04F Melmetal Battle Runtime`
- Run: **#1**
- Run ID: **35906269308**
- Commit: `65085da755f21be046c28302f4b048fa1a2ec76d`
- Conclusion: **success**
- Artifact: `pt04f-melmetal-battle-runtime-proof`
- Artifact ID: **10770929667**
- Artifact SHA-256: `dcccce7a87e2796813a45b7f4c06b8c9b8fa796ca98f725c7c03509171f81373`

Battle boundary:

- Player: **Melmetal #809**, Lv.50
- Opponent: native **Bidoof Lv.5**

Visual proof confirmed:

- Melmetal player-side back sprite,
- `MELMETAL` name,
- Lv.50,
- **199/199 HP**,
- native battle command UI,
- stable battle through frame 4000,
- no invalid instruction,
- no assertion failure,
- no emulator stop.

### PT04F completion commit

Generation VII / Melmetal work was formally closed at:

- `9ba0fedd51edbc97edd9e2603be661cb783c3388`

Existing sealed docs:

- `docs/PT04F_GEN7_DONOR_AUDIT_CHECKPOINT_2026-09-23.md`
- `docs/PT04F_GEN7_BULK_BUILD_CHECKPOINT_2026-09-23.md`
- `docs/PT04F_GEN7_SAVE_RELOAD_RUNTIME_CHECKPOINT_2026-09-23.md`
- `docs/PT04F_MELMETAL_BATTLE_RUNTIME_CHECKPOINT_2026-09-23.md`
- `docs/PT04F_COMPLETE_CHECKPOINT_2026-09-23.md`

## Critical recovery instruction

**Do not rerun or rebuild Melmetal-specific proof unless a later regression directly requires it.**

Melmetal #809 has already passed:

`bulk build -> native party/Pokédex -> save -> DS reset -> native reload -> Party render -> native battle render`

---

# PT04G — Generation VIII

## Current state

PT04G has already begun on:

- `feature/pt04g-gen8-bulk-expansion`

Canonical Generation VIII base range:

- **Grookey #810**
- through **Enamorus #905**
- **96 species**

### Gen VIII donor audit Run #1

Initial Gen VIII audit:

- Run ID: **35909015359**
- Conclusion: **failure**

The failure was not a roster architecture regression. It exposed a donor-art assumption for Enamorus: Enamorus uses the female donor sprite path.

### Enamorus donor fix

Fix commit:

- `c1fe60d1a16f0c7062bbf54b4458b06482782f10`
- Commit purpose: **Use Enamorus female donor asset in Gen VIII audit**

### Gen VIII donor audit Run #2

Corrected audit:

- Workflow: `PT04G Gen VIII Bulk Expansion Audit`
- Run: **#2**
- Run ID: **35909127545**
- Commit: `c1fe60d1a16f0c7062bbf54b4458b06482782f10`
- Conclusion: **success**
- Artifact: `pt04g-gen8-donor-audit`
- Artifact ID: **10771444482**
- Artifact SHA-256: `5e70f85b1b470e7f8a841d86306d949db7db782d2d8ca68b7f351aca08236e90`

Audit result:

- expected species: **96**
- parsed species: **96**
- missing donor entries: **0**
- missing required front/back/icon assets: **0**
- unsupported gender ratios: **0**
- unsupported types: **0**
- unsupported held items: **0**
- unsupported translated growth rates: **0**
- unsupported egg groups: **0**
- unsupported modern abilities: **35 distinct constants**
- modern base EXP >255: **14 species**

The 14 >255 base-EXP species are:

- Rillaboom
- Cinderace
- Inteleon
- Obstagoon
- Dragapult
- Zacian
- Zamazenta
- Eternatus
- Urshifu
- Zarude
- Regieleki
- Regidrago
- Glastrier
- Spectrier

Boundary proof points from the corrected audit:

- Grookey #810 parsed correctly.
- Enamorus #905 parsed correctly.
- Enamorus uses the female-only donor resource path correctly.
- Fairy/Flying typing for Enamorus maps into the current Mercury type layer.

---

# Exact next unfinished step

The next task is **not Melmetal testing**.

The next unfinished gate is:

`PT04G_GEN8_BULK_BUILD`

Resume by:

1. Seal/document the successful corrected Gen VIII donor audit if a dedicated PT04G audit checkpoint has not yet been committed.
2. Register canonical base species continuously through **Enamorus #905**.
3. Restore sealed generated prerequisite resource batches:
   - Gen V #494–649,
   - Gen VI #650–721,
   - Gen VII #722–809.
4. Generate/install the Gen VIII canonical batch:
   - #810–905,
   - 96 species.
5. Configure and compile the cumulative Platinum ROM.
6. Verify compiled personal/battle-sprite/icon/height archives extend through #905.
7. Only after the bulk build is sealed:
   - native save/reset/load proof with **Enamorus #905** as the upper boundary,
   - representative Gen VIII Party visual review,
   - native Enamorus battle proof.

Do not start Generation IX until Gen VIII bulk build + persistence + battle gates are independently sealed.

---

## Deferred mechanics remain unchanged

The canonical roster-capacity phases continue to defer later mechanics rather than silently approximating them:

- modern abilities not yet imported,
- modern moves/learnsets,
- modern evolution methods,
- base EXP field widening,
- cries/footprints,
- localized Pokédex text,
- alternate/regional/form semantics,
- Mercury-specific custom forms/Megas.

Those remain separate from proving canonical base-species capacity.

---

## Recovery rule

If work must resume from this checkpoint:

- treat PT04F / Melmetal as **finished and immutable**,
- treat corrected PT04G Gen VIII donor audit Run #2 as **passed**,
- resume at the **Gen VIII cumulative bulk-build gate**,
- do not repeat Victini, Genesect, Volcanion, or Melmetal runtime proofs unless a later change directly breaks one of their sealed assumptions.
