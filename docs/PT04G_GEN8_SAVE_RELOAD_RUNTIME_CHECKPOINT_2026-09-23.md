# PT04G Gen VIII Save/Reload Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VIII upper boundary survives Platinum's native save/reset/load path and the representative Gen VIII party renders stably after reload.

## CI proof

- Workflow: `PT04G Gen VIII Save Reload Runtime`
- Run number: **1**
- Run ID: **35910244548**
- Commit: `552d5d8fc3b54ca017248fb6710c39eeed3bb425`
- Conclusion: **success**
- Artifact: `pt04g-gen8-save-reload-runtime-proof`
- Artifact ID: **10773790221**
- SHA-256: `0a6748f8f4a81e141237021a58cb6492161c682fdc78e40a04f086ee066c138a`

## Primary persistence boundary

- **Enamorus**
- National Dex / native species ID: **905**
- Party slot: **0**
- Level: **50**

## Representative Gen VIII party

1. Enamorus #905 — upper Gen VIII boundary / female-only resource path
2. Grookey #810 — first Gen VIII species / starter
3. Toxtricity #849 — form-sensitive base resource path
4. Indeedee #876 — gender/form-sensitive data path
5. Morpeko #877 — form-heavy base resource path
6. Zacian #888 — item/form-sensitive legendary base data

The harness uses Platinum's native save, DS reset, and native load-save startup path before reopening the Party application.

## Runtime assertions

The runtime completed through frame **4800** with no emulator stop.

The installed harness asserts:

- party count after reload == 6,
- slot 0 species == `SPECIES_ENAMORUS`,
- slot 0 level == 50,
- all six representative species remain in party,
- Enamorus seen/caught flags survive reload,
- Toxtricity, Indeedee, and Zacian caught flags survive reload,
- native Party application reopens after reload.

## Visual review

Post-reload Party captures were reviewed through frame 4800.

Observed:

- `ENAMORUS` Lv.50 — **138/138 HP**
- `GROOKEY` Lv.50 — **122/122 HP**
- `TOXTRICITY` Lv.50 — **140/140 HP**
- `INDEEDEE` Lv.50 — **126/126 HP**
- `MORPEKO` Lv.50 — **131/131 HP**
- `ZACIAN` Lv.50 — **167/167 HP**
- all six party icons rendered,
- Enamorus displayed with the female marker,
- representative gender markers rendered sensibly,
- Party UI remained stable from the post-reload open through frame 4800,
- no invalid instruction, assertion failure, or emulator stop occurred.

## What this proves

Together with the sealed PT04G donor audit and cumulative bulk-build checkpoint, this proves Generation VIII canonical IDs through #905 survive Platinum persistence and post-reload Party rendering.

## Next gate

`PT04G_GEN8_ENAMORUS_BATTLE_RUNTIME`

Use Enamorus #905 as the player's Lv.50 lead against a low-risk native Bidoof and visually verify the player-side sprite, name, HP, and stable native battle UI before closing PT04G.
