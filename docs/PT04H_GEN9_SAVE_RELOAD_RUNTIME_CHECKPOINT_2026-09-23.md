# PT04H Gen IX Save/Reload Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The final canonical National Dex boundary now survives Platinum's native save/reset/load path, and the representative Generation IX party renders stably after reload.

## CI proof

- Workflow: `PT04H Gen IX Save Reload Runtime`
- Run number: **1**
- Run ID: **35916432761**
- Commit: `48e29677827896051c24c282e4057654785ad84f`
- Conclusion: **success**
- Artifact: `pt04h-gen9-save-reload-runtime-proof`
- Artifact ID: **10775860259**
- SHA-256: `e8cc911a1d56b8830b3fecfe0655297c637b28d6f744ef348feedaf81ab2ae8f`

## Primary persistence boundary

- **Pecharunt**
- National Dex / native species ID: **1025**
- Party slot: **0**
- Level: **50**

## Representative Gen IX party

1. Pecharunt #1025 — final canonical National Dex boundary
2. Sprigatito #906 — first Gen IX species / starter
3. Palafin #964 — form-sensitive modern species base path
4. Kingambit #983 — late-generation evolution-line path
5. Koraidon #1007 — legendary / Paradox-era base path
6. Terapagos #1024 — form-heavy penultimate canonical species

The harness uses Platinum's native save, DS reset, and native load-save startup path before reopening the Party application.

## Runtime assertions passed

The runtime completed through frame **4800** with no emulator stop.

The installed harness asserts:

- party count after reload == 6,
- slot 0 species == `SPECIES_PECHARUNT`,
- slot 0 level == 50,
- all six representative species remain in party,
- Pecharunt seen/caught state survives reload through the sealed PT04C persistence path,
- Palafin, Kingambit, and Terapagos caught flags survive reload,
- native Party application reopens after reload.

## Visual review

Post-reload Party captures were visually reviewed through frame 4800.

Observed:

- `PECHARUNT` Lv.50 — **148/148 HP**
- `SPRIGATITO` Lv.50 — **101/101 HP**
- `PALAFIN` Lv.50 — **161/161 HP**
- `KINGAMBIT` Lv.50 — **170/170 HP**
- `KORAIDON` Lv.50 — **170/170 HP**
- `TERAPAGOS` Lv.50 — **154/154 HP**
- all six party icons rendered correctly,
- displayed gender markers were sensible for the generated base data,
- Party UI remained stable from the post-reload open through frame 4800,
- no invalid instruction, assertion failure, or emulator stop occurred.

## What this proves

Together with the sealed PT04H donor audit and full #1–1025 cumulative build checkpoint, this proves the complete canonical National Dex base roster survives native Platinum persistence at the final species boundary.

The proven path now spans:

`full #1–1025 compiled roster -> native save -> DS reset -> native reload -> six-slot Gen IX Party rendering`

## Exact next gate

`PT04H_GEN9_PECHARUNT_BATTLE_RUNTIME`

Use Pecharunt #1025 as the player's Lv.50 lead against a low-risk native Bidoof and visually verify:

- Pecharunt player-side back sprite,
- `PECHARUNT` player name,
- Lv.50 and sane HP,
- native battle command UI,
- stable battle rendering through the proof window.

Do not close PT04H until this final native battle gate passes.
