# PT02 — Native Platinum Visible Modification Proof

**Status:** ACTIVE

## Goal

Prove that project-owned source changes are actually appearing in the running native Pokémon Platinum build.

## Proof change

The title-screen text resource is replaced through the project overlay:

- Upstream: `PRESS START`
- PT02 proof: `MERCURY DS`

This is intentionally small and reversible. It changes a native Platinum resource without changing the Sinnoh world engine.

## Acceptance gates

PT02 passes only when:

1. The pinned native Platinum source builds with the overlay.
2. The resulting ROM differs from the clean PT01 baseline by design.
3. DeSmuME boots the modified build.
4. Runtime screenshots are captured from the actual built ROM.
5. At least one captured frame visibly shows the modified `MERCURY DS` title-screen text.
6. The proof screenshots are retained as a short-lived GitHub Actions artifact.

After this gate, large modernization work can begin without questioning whether our source modifications are actually reaching the game.
