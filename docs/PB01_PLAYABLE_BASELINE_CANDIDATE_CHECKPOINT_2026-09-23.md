# PB01 Playable Baseline Candidate Checkpoint — 2026-09-23

## Status

**PASS / CANDIDATE SEALED**

Mercury DS now has its first normal, non-harness playable ROM candidate built on the completed #1–1025 canonical roster foundation.

This is deliberately a conservative game build: native Platinum world/story progression is retained while Mercury title branding, Fairy/type infrastructure, and the complete canonical species-capacity layer remain present.

## CI proof

- Workflow: `PB01 Playable Baseline Candidate`
- Run number: **1**
- Run ID: **35919890042**
- Commit: `78b2fd48f78a9af725877fae7890b9d7db8f8fdc`
- Conclusion: **success**
- Playable artifact: `mercury-redux-pb01-playable-candidate`
- Artifact ID: **10776204522**
- Build proof artifact: `mercury-redux-pb01-build-proof`
- Artifact ID: **10776593203**

## ROM identity

- Candidate filename: `Pokemon_Mercury_Redux_PB01.nds`
- ROM size: **134,217,728 bytes**
- SHA-256: `87a8f97f884b5496a16fa7b1b85ea6589e9e9e1cf4a03e9110ecdc09dfe91f16`

## Normal-game safeguards

PB01 explicitly verified:

- no PT04 runtime harness was installed,
- no CI battle-entry injection was present,
- no map/script/event files were replaced by the Mercury overlay,
- native Platinum world and story resources remain the baseline progression,
- complete #1–1025 resource capacity was regenerated before compile.

## Full-roster archive proof

- `pl_personal.narc`: **1040**
- `pl_pokegra.narc`: **6156**
- `pl_poke_icon.narc`: **1079**
- `height.narc`: **4104**

## Native runtime proof

The normal ROM booted in DeSmuME.

Visual review confirmed:

1. the live Mercury Redux title screen rendered correctly,
2. native Start input was accepted,
3. the game left the title screen and entered Professor Rowan's normal new-game introduction,
4. native A input advanced the introduction to **"Welcome to the world of Pokémon!"**,
5. the ROM remained stable and nonblank after additional runtime.

This is the first proof in the project that the full-roster Mercury build is running through normal player-facing game flow rather than a dedicated test harness.

## What PB01 does not claim yet

PB01 is a playable **candidate**, not the final gold seal.

It does not yet certify an uninterrupted player journey from New Game through Cynthia/credits. The next phases certify that normal progression in increasingly large chunks while preserving this candidate.

## Exact next gate

`PB02_EARLY_GAME_PLAYABLE_CERTIFICATION`

Target progression:

`Rowan intro -> naming -> Twinleaf -> Route 201/Lake Verity -> Sandgem -> starter/Pokédex -> first wild battle/capture -> save/reset/continue`

Advanced mechanics remain deferred until the complete playable baseline is sealed.
