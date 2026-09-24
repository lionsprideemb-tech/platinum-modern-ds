# HARD HANDOFF — PB02AA Barry THUD Confirmed — 2026-09-24

## Status

**HARD RECOVERY CHECKPOINT / SAFE TO RESUME**

This is the canonical restart point for the Mercury DS playable-baseline playthrough.

Do **not** restart PB02 from the title screen, Rowan intro, naming, player house, or the first Twinleaf exterior checkpoint. Those sections have already been exercised and visually checked.

## Current project phase

- Branch: `feature/playable-baseline`
- Goal: certify a complete normal playable game before adding more large mechanics/content systems.
- Source playable ROM: `Pokemon_Mercury_Redux_PB01.nds`
- PB01 ROM SHA-256: `87a8f97f884b5496a16fa7b1b85ea6589e9e9e1cf4a03e9110ecdc09dfe91f16`
- Full canonical species capacity #1–1025 remains the sealed foundation.

## Last canonical test completed

### PB02AA — Exact Barry THUD Route

**PASS**

- Workflow: `PB02AA Exact Barry THUD Route`
- Run ID: **35956698776**
- Source commit: `6dd9bdcf163a4ae53f57ad50c3b0725fb85fb4c1`
- Result: **success**
- Artifact: `pb02aa-exact-barry-thud-proof`
- Artifact ID: **10790910656**
- Artifact digest: `sha256:488a0c7deb4a7444663f0c24ebe5ee0e94a6ae3c002b56d270428d1c4e9bf9cf`

## Exact in-game placement

The player has reached and completed the native Twinleaf **Barry THUD** event using the verified central-road path.

Native Twinleaf coordinates used:

- Player-house warp: `(116, 885)`
- Barry THUD coord event: `(105, 876)`
- Barry-house warp: `(105, 875)`

Verified route from the sealed Twinleaf exterior state:

`LEFT x4 -> UP x10 -> LEFT x6 -> final LEFT into (105,876)`

The native Barry collision/THUD sequence was then advanced and the game remained stable.

## Recovery savestate

The PB02AA proof artifact contains the exact continuation state:

`post-barry-thud-confirmed.dst`

**Resume from this savestate.**

This is preferable to replaying the earlier route probes because it was created after the corrected, coordinate-backed Twinleaf route and successful native THUD event.

## Already certified before this point

Do not redo these unless a future code change directly invalidates them:

- Mercury Redux live title screen
- native Start input
- Professor Rowan opening
- advice menu / Poké Ball touch sequence
- player gender selection
- player-name keyboard
- player name `MERCURY`
- rival name `BARRY`
- opening TV sequence
- Twinleaf bedroom
- player-house stairs / first floor
- mother dialogue
- exit from player house into Twinleaf
- stable Twinleaf exterior field control
- exact central-road approach to Barry
- Barry THUD event at `(105,876)`

Earlier Barry-house/stair workflows were exploratory probes. When there is a conflict, PB02AA and its savestate are the canonical state.

## Exact next unfinished step

### PB02AB — Barry House / Upstairs Event

Load:

`post-barry-thud-confirmed.dst`

Then continue with native player input:

1. Move one tile north from the post-THUD exterior position onto Barry-house warp `(105,875)`.
2. Verify Barry house 1F renders correctly.
3. Navigate to the native 1F -> 2F stair warp.
   - Barry house 1F stair warp coordinates in source: `(2,3)`.
4. Enter Barry house 2F.
5. Verify the automatic Barry upstairs sequence:
   - Barry takes bag and Journal,
   - notices the player,
   - says he will be waiting on the road,
   - leaves,
   - `FLAG_RIVAL_LEFT_HOME` is set by the native script.
6. Capture screenshots before, during, and after that sequence.
7. Preserve a new savestate only after the upstairs sequence is visibly confirmed and field control is restored.

After that, the playthrough should continue toward **Route 201 / Lake Verity** rather than restarting any earlier PB02 section.

## Visual-testing rule

Continue the existing policy:

- play using native DS inputs,
- capture screenshots at important states,
- visually inspect before declaring a gate passed,
- stop and fix visual/progression problems before advancing,
- keep periodic savestate + Git branch checkpoints so conversation interruptions cannot force a replay.
