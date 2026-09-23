# PT04G Enamorus Battle Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VIII upper-boundary species renders and remains stable inside Platinum's native battle engine.

## CI proof

- Workflow: `PT04G Enamorus Battle Runtime`
- Run number: **1**
- Run ID: **35914335957**
- Commit: `391fead55d4a12d79ccfbbce720cded3398a5813`
- Conclusion: **success**
- Artifact: `pt04g-enamorus-battle-runtime-proof`
- Artifact ID: **10774751962**
- SHA-256: `236c0d6553a572bdde14d5f92c1c15f357bca267c0f48a2151e89e9a2105016c`

## Boundary under test

Player species:

- **Enamorus**
- National Dex / native species ID: **905**
- Level: **50**

Opponent:

- **Bidoof**
- Level: **5**

## Runtime result

The battle proof completed through frame **4000** with no emulator stop.

All workflow stages passed:

- cumulative species registration through #905,
- sealed Gen V, VI, and VII prerequisite restoration,
- sealed Gen VIII resource installation,
- native PT04C battle-entry harness installation,
- Enamorus conversion,
- Platinum configuration,
- ROM compilation,
- DeSmuME runtime,
- proof upload.

## Visual review

Captured frames were reviewed from battle entry through frame 4000.

Observed:

- native wild-battle scene entered successfully,
- Enamorus player-side back sprite rendered correctly,
- `ENAMORUS` rendered correctly,
- Lv.50 rendered correctly,
- HP rendered as **134/134**,
- native battle command UI appeared normally,
- Bidoof Lv.5 rendered normally as the opponent,
- battle remained visually stable through frame 4000,
- no invalid instruction, assertion failure, or emulator stop occurred.

## What this proves

Together with the sealed PT04G donor audit, cumulative bulk build, and native save/reset/load checkpoint, this proves the canonical Generation VIII base roster extends Platinum natively through species ID #905 across:

`compiled data/resources -> persistence -> post-reload Party/icon rendering -> native battle rendering`

## Next gate

PT04G / Generation VIII is ready to close.

Only after sealing PT04G complete should the next canonical batch begin:

- **Generation IX**
- Sprigatito #906
- through Pecharunt #1025
- **120 canonical species**
