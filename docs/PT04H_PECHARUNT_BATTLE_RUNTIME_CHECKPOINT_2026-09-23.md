# PT04H Pecharunt Battle Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The final canonical National Dex species renders and remains stable inside Platinum's native battle engine.

## CI proof

- Workflow: `PT04H Pecharunt Battle Runtime`
- Run number: **1**
- Run ID: **35918975641**
- Commit: `9c9e90913c952d403f6f77fdd875ea6b981d2a7e`
- Conclusion: **success**
- Artifact: `pt04h-pecharunt-battle-runtime-proof`
- Artifact ID: **10775934139**
- SHA-256: `42876d4f1c74bdbda8292f7421db41d2867784f7100d8a8865444ba19a9e694c`

## Boundary under test

Player species:

- **Pecharunt**
- National Dex / native species ID: **1025**
- Level: **50**
- HP observed: **148/148**

Opponent:

- **Bidoof**
- Level: **5**

## Visual review

Captured frames were reviewed through frame **4000**.

Observed:

- native wild-battle scene entered successfully,
- Pecharunt player-side back sprite rendered correctly,
- `PECHARUNT` rendered correctly,
- Lv.50 rendered correctly,
- HP rendered as **148/148**,
- native battle command UI appeared normally,
- Bidoof Lv.5 rendered normally,
- battle remained stable through frame 4000,
- no emulator stop, invalid instruction, or assertion failure occurred.

## What this proves

Together with the sealed PT04H donor, cumulative build, and save/reset/load checkpoints, this proves the complete canonical base roster through species ID #1025 across:

`compiled resources -> persistence -> post-reload Party rendering -> native battle rendering`

## Next gate

PT04H is ready to close.

Per project direction, the next phase is **not** another mechanics expansion. The next phase is a complete playable-baseline build based on the finished Platinum adventure, preserving the #1–1025 capacity foundation and leaving advanced Mercury systems for later branches.
