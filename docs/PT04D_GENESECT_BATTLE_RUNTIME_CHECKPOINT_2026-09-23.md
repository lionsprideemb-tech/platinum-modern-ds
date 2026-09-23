# PT04D Genesect Battle Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The upper Generation V boundary species now renders and remains stable inside Platinum's native battle engine.

## CI proof

- Workflow: `PT04D Genesect Battle Runtime`
- Run number: **1**
- Run ID: **35895198907**
- Commit: `452b886b8360acaeb8ca21303657c3ee33b90ae0`
- Conclusion: **success**
- Artifact: `pt04d-genesect-battle-runtime-proof`
- Artifact ID: **10766487324**
- SHA-256: `802daffbfc2f504d83a858e7d7b6eb7eb72fc1177a7ced4f9bb37f4486c37d18`

## Boundary under test

Player species:

- **Genesect**
- National Dex / native species ID: **649**
- Level: **50**

Opponent:

- **Bidoof**
- Level: **5**

The runtime path uses Platinum's native scripted encounter entrypoint.

## Visual review

Captured frames were reviewed through frame 4000.

Observed:

- native wild-battle scene entered successfully,
- Genesect player-side back sprite rendered correctly,
- `GENESECT` name rendered correctly,
- Lv.50 rendered correctly,
- HP rendered as **142/142**,
- Genesect's compatible **Download** ability message rendered,
- the native battle command UI appeared normally,
- the battle remained stable through frame 4000,
- no emulator stop, invalid instruction, or assertion failure occurred.

## What this proves

Together with the sealed PT04D bulk-build and save/reload checkpoints, this proves the canonical Gen V base roster can extend Platinum natively through species ID #649 across:

- compiled personal data,
- battle sprite archives,
- icon archives,
- height/sprite metadata,
- native party creation,
- Pokédex flags,
- native save serialization,
- native load reconstruction,
- party/icon rendering,
- and native battle rendering above the 511/512 boundary.

## Next gate

PT04D Gen V is ready to close. The next canonical roster batch begins with **Chespin #650** and runs through **Volcanion #721**.
