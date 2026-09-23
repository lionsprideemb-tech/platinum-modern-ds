# PT04F Gen VII Save/Reload Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VII upper boundary now survives Platinum's real native save/reset/load path.

## CI proof

- Workflow: `PT04F Gen VII Save Reload Runtime`
- Run number: **1**
- Run ID: **35905367563**
- Commit: `207dec993afb2275dd6dad6becc8167bfb10ce47`
- Conclusion: **success**
- Artifact: `pt04f-gen7-save-reload-runtime-proof`
- Artifact ID: **10770249475**
- SHA-256: `45903e99f2a8e21a29c0bd6bde722515269f55ced428adbf4ab52d68570a8bd0`

## Primary persistence boundary

- **Melmetal**
- National Dex / native species ID: **809**
- Party slot: **0**
- Level: **50**

## Representative Gen VII party

1. Melmetal #809 — upper Gen VII boundary
2. Rowlet #722 — first Gen VII species / starter
3. Oricorio #741 — multi-form base resource path
4. Salazzle #758 — female-only species path
5. Silvally #773 — type/form-sensitive base data
6. Mimikyu #778 — form-heavy base resource path

The harness uses Platinum's native save, DS reset, and native load-save startup path before reopening the Party application.

## Runtime assertions passed

- Party count after reload == 6
- Slot 0 species == `SPECIES_MELMETAL`
- Slot 0 level == 50
- all six representative species remained in party
- Melmetal seen/caught flags survived reload
- Oricorio caught flag survived reload
- Salazzle caught flag survived reload
- Mimikyu caught flag survived reload

## Visual review

The post-reload Party screen was visually reviewed through frame 4800.

Observed:

- `MELMETAL` Lv.50 — **202/202 HP**
- `ROWLET` Lv.50 — **136/136 HP**
- `ORICORIO` Lv.50 — **143/143 HP**
- `SALAZZLE` Lv.50 — **129/129 HP**
- `SILVALLY` Lv.50 — **156/156 HP**
- `MIMIKYU` Lv.50 — **126/126 HP**
- all six party icons rendered correctly,
- gender markers rendered sensibly,
- Party UI remained stable through frame 4800,
- no emulator stop or assertion failure occurred.

## Next gate

`PT04F_GEN7_MELMETAL_BATTLE_RUNTIME`

Use Melmetal #809 as the player's lead against a low-risk native Bidoof and visually verify player-side sprite/name/HP plus stable native battle UI.
