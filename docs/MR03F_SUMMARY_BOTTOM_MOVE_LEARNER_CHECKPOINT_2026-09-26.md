# MR03F Summary Bottom Move Learner — 2026-09-26

## Status

**PASS / SEALED / MR03F COMPLETE**

MR03F proves the locked dual-screen design in the native Pokémon Platinum Summary application:

- **TOP:** vanilla Platinum Summary Screen renderer
- **BOTTOM:** Mercury Move Learner browser on the Summary SUB engine

Completed work before this checkpoint is not to be restarted or redone unless a future regression directly implicates MR03F.

## Original failed capture

Branch:

`feature/mr03f-summary-bottom-learner`

Original checkpoint commit:

`f1ac0c709373f5be4fef052e4c7796f3374f4632`

GitHub Actions workflow:

- Name: `MR03F Summary Bottom Move Learner`
- Run ID: **36247126383**
- Job: `prove-summary-bottom-learner`
- ROM build step: **PASS**
- Failed step: `Capture full DS Move Learner proof`

The built ROM launched in DeSmuME, but the runtime stopped near **frame 4275** during the transition into the Move Learner. DeSmuME reported:

`ARM9: Undefined instruction: 0x1D090000 PC=0x05000000`

This was a runtime memory failure, not a ROM-build failure.

## Root cause and fix

Commit:

`76fb466f29471e769bf153f4bf65a844152181f9`

Change:

- Increased the native Summary application heap from `0x40000` to `0x50000`.

The bottom Move Learner adds four window pixel buffers, a 512-entry move pool, and an additional message loader. The original Summary heap did not leave enough safe headroom for the added MR03F runtime state.

The first workflow run containing only this heap-headroom fix already passed the complete build and capture path:

- Workflow run ID: **36247642924**
- `Install Summary host and bottom learner`: **PASS**
- `Build one MR03F proof ROM`: **PASS**
- `Capture full DS Move Learner proof`: **PASS**

Therefore the heap increase is the isolated fix for the original frame-4275 runtime crash.

## Later MR03F cleanup

Subsequent MR03F work preserved the architecture and added only targeted cleanup/diagnostics, including:

- corrected bottom learner window bounds
- combined Move Learner / Available Moves heading
- diagnostic workflows
- an earlier pre-open capture breadcrumb

These later changes were not required to stop the original crash.

Pre-checkpoint branch head after diagnostics:

`1998fe67a54649c70f390dc80123567cc4d07d08`

The only change after the successful MR03F proof commit was diagnostic-workflow-only; no gameplay or renderer code was altered.

## Final runtime proof

Successful full proof workflow:

- Run ID: **36251147467**
- Job: `prove-summary-bottom-learner`
- Conclusion: **success**
- Artifact: `mercury-mr03f-summary-bottom-move-learner`
- Artifact ID: **10909415926**

Proof ROM SHA-256:

`642fca962a2ebc75c91ec59940b42ebbf224b63154229d847e5b15c1a66e5d49`

## Visual verification

The successful artifact was manually reviewed.

Captured runtime states:

1. frame **4096** — Pokémon context menu with **MOVE LEARNER** selected
2. frame **4250** — Move Learner browse state
3. frame **4508** — scrolled Move Learner browse state
4. frame **4732** — native replacement-selection state
5. frame **4996** — cancel returns to Move Learner
6. frame **5140** — another vanilla Summary top page while the Mercury Move Learner remains on the bottom

The proof therefore continues well beyond the original frame-4275 crash boundary.

## Locked MR03F behavior

- top screen stays the vanilla Platinum Summary renderer
- bottom screen owns the Mercury Move Learner browser
- Up/Down browses learner moves
- L/R changes the vanilla top Summary page
- A enters the native move replacement path
- B cancels replacement back to the learner
- closing the Move Learner returns to the party flow
- do not restore the rejected MR03C custom top renderer

## MR03F conclusion

The failed capture was diagnosed, the runtime memory issue was corrected, the full proof path was rerun successfully, and the intended dual-screen UI was visually verified.

**MR03F is closed.**

Any next work should build forward from this sealed state rather than rebuilding the Summary/Move Learner integration.
