# MR04 Mercury Player Build — 2026-09-26

## Status

**PASS / SEALED / MR04 COMPLETE**

MR04 converts the sealed MR03F integration into a normal player-facing Mercury ROM.

## Parent checkpoint

MR03F sealed parent:

`f087afa9b06746a4689457f38b64cd9ca6c58f58`

Locked MR03F design retained:

- TOP: vanilla Platinum Summary Screen renderer
- BOTTOM: Mercury Move Learner
- four visible learner rows
- expanded move-description panel
- no CI-only direct-launch behavior in player builds

## MR04 branch

`feature/mr04-player-build`

Workflow:

`MR04 Mercury Player Build`

Successful run:

- Run ID: **36258632897**
- Job: `build-normal-boot-rom`
- Conclusion: **success**

## Proved gates

- pinned Platinum and HG-Engine sources restored
- sealed Mercury Platinum overlay applied
- MP05 canonical ability architecture restored
- canonical species registry built through #1025 Pecharunt
- modern Gen 5-9 species resources installed
- 16-bit move namespace restored
- modern learnsets/evolutions installed
- production Mercury Move Learner installed
- sealed MR03F dual-screen UI installed
- CI-only Garchomp/direct-launch harness confirmed absent
- Mercury title resources generated
- normal-boot ROM compiled successfully
- real DeSmuME normal boot captured successfully
- player ROM artifact uploaded

## Normal-boot proof

Captured frames:

- 14800
- 15200
- 15600
- 16000

All captures were nonblank and the emulator remained running.

Boot metadata:

- `normal_story_boot: true`
- `ci_move_learner_direct_launch: false`
- `stopped_at: null`
- expected title prompt: `PRESS START`

The real emulator captures show the Mercury Redux title screen rendering and animating normally with the native title flow intact.

## Player ROM

Artifact:

`mercury-mr04-player-build`

Artifact ID:

`10911921230`

ROM filename:

`Pokemon_Mercury_MR04_Player_Build.nds`

SHA-256:

`775c075446a9d0f0a5bc10cc3c32f7e0353eeeaac9725d6c489808808bcbaf2b`

## Lock

Do not restart MR03F or rebuild the Summary/Move Learner design unless a later regression directly implicates it.

Future Mercury work should branch forward from this MR04 player-build checkpoint.

**MR04 is closed.**
