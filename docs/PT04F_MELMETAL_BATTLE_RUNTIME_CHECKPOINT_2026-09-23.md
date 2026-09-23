# PT04F Melmetal Battle Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VII upper-boundary species renders and remains stable inside Platinum's native battle engine.

## CI proof

- Workflow: `PT04F Melmetal Battle Runtime`
- Run number: **1**
- Run ID: **35906269308**
- Commit: `65085da755f21be046c28302f4b048fa1a2ec76d`
- Conclusion: **success**
- Artifact: `pt04f-melmetal-battle-runtime-proof`
- Artifact ID: **10770929667**
- SHA-256: `dcccce7a87e2796813a45b7f4c06b8c9b8fa796ca98f725c7c03509171f81373`

## Boundary under test

Player species:

- **Melmetal**
- National Dex / native species ID: **809**
- Level: **50**

Opponent:

- **Bidoof**
- Level: **5**

## Visual review

Captured frames were reviewed through frame 4000.

Observed:

- native wild-battle scene entered successfully,
- Melmetal player-side back sprite rendered correctly,
- `MELMETAL` rendered correctly,
- Lv.50 rendered correctly,
- HP rendered as **199/199**,
- native battle command UI appeared normally,
- battle remained stable through frame 4000,
- no emulator stop, invalid instruction, or assertion failure occurred.

## What this proves

Together with the sealed PT04F donor, build, and save/reload checkpoints, this proves the canonical Gen VII base roster can extend Platinum natively through species ID #809 across compiled data/resources, persistence, party/icon rendering, and native battle rendering.

## Next gate

PT04F Gen VII is ready to close. The next canonical batch begins with **Grookey #810** and runs through **Enamorus #905**.
