# PT04E Volcanion Battle Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VI upper-boundary species now renders and remains stable inside Platinum's native battle engine.

## CI proof

- Workflow: `PT04E Volcanion Battle Runtime`
- Run number: **1**
- Run ID: **35903566072**
- Commit: `2fddada17e2ace45f69518cff03e11a44730ddd8`
- Conclusion: **success**
- Artifact: `pt04e-volcanion-battle-runtime-proof`
- Artifact ID: **10770710564**
- SHA-256: `7f147a164fb6a922a289b80764d4c12e3c5d86b27f4162ce1997fde5563fba43`

## Boundary under test

Player species:

- **Volcanion**
- National Dex / native species ID: **721**
- Level: **50**

Opponent:

- **Bidoof**
- Level: **5**

The runtime path uses Platinum's native scripted encounter entrypoint.

## Visual review

Captured frames were reviewed through frame 4000.

Observed:

- native wild-battle scene entered successfully,
- Volcanion player-side back sprite rendered correctly,
- `VOLCANION` name rendered correctly,
- Lv.50 rendered correctly,
- HP rendered as **147/147**,
- native battle command UI appeared normally,
- the battle remained stable through frame 4000,
- no emulator stop, invalid instruction, or assertion failure occurred.

## What this proves

Together with the sealed PT04E donor, build, and save/reload checkpoints, this proves the canonical Gen VI base roster can extend Platinum natively through species ID #721 across:

- compiled personal data,
- battle sprite archives,
- icon archives,
- height/sprite metadata,
- native party creation,
- Pokédex flags,
- native save serialization,
- native load reconstruction,
- party/icon rendering,
- and native battle rendering.

## Next gate

PT04E Gen VI is ready to close. The next canonical batch begins with **Rowlet #722** and runs through **Melmetal #809**.
