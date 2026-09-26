# MR05B Encounter Table Framework Checkpoint — 2026-09-26

## Status

**PASS / SEALED / MR05B COMPLETE**

## Sealed source

- Source commit: `aaf000f8be2d6699d4b1c69fb67cc1d8bbc23436`
- Checkpoint branch: `checkpoint/mr05b-encounter-table-framework-2026-09-26`
- Successful workflow run: `36262560851`
- Artifact: `mercury-mr05b-encounter-framework`
- Artifact ID: `10912418211`

## ROM proof

- Player ROM: `Pokemon_Mercury_MR05B_Encounter_Framework.nds`
- SHA-256: `60705d297bf71e98558c6122424651d8c95cfc6dbe926edd59e4c83e6e9a6d3c`
- Full normal-player ROM compile: PASS
- Real DeSmuME normal boot: PASS
- CI direct-launch harness absent: PASS

## Encounter framework proof

- Total centralized encounter resources: **185**
- Standard encounter tables: **183**
- Honey Tree special resources: **1**
- Great Marsh Lookout special resources: **1**
- Changed encounter areas in MR05B baseline: **0**
- Baseline preserved: **true**
- Baseline dataset SHA-256: `c366edfc32237e3df88c761226b78fef6e9a085a44e22958a8a3316037955691`
- Output dataset SHA-256: `c366edfc32237e3df88c761226b78fef6e9a085a44e22958a8a3316037955691`

The framework centralizes and validates land, swarm, day/night, Poké Radar,
GBA dual-slot, Surf, Old/Good/Super Rod, Honey Tree, Trophy Garden daily,
Great Marsh daily/binocular, and Mt. Coronet elusive-rod encounter data.

## Locked behavior

MR05B intentionally changes **no wild encounter content**. It provides the
single Mercury encounter-control layer that future encounter edits and the
randomizer must use.

MR03F, MR04, MR05A, and MR05B are closed unless a later regression directly
implicates them.

## Next phase

MR05C — Randomizer Framework, branching from this sealed checkpoint.
