# MR05A HM-Free Traversal — 2026-09-26

## Status

**PASS / SEALED / MR05A COMPLETE**

MR05A adds Mercury's HM-free traversal foundation on top of the sealed MR04 player build.

## Parent checkpoint

MR04 sealed parent:

`a227026dd546ce600dc5679c048b195aa558ff57`

MR04 remains locked:
- normal player-facing Mercury boot
- 1025-species modern foundation
- sealed MR03F dual-screen Move Learner
- no CI direct-launch harness

## MR05A branch

`feature/mr05a-hm-free-traversal`

Authoritative proved head:

`77fa9c98fe653adf5a34b268900bdc8762c8382f`

Workflow:

`MR05A HM-Free Traversal`

Successful authoritative run:

- Run ID: **36260666040**
- Job ID: **108455715758**
- Conclusion: **success**

## HM-free policy

Traversal no longer requires an HM to occupy one of the Pokemon's four move slots.

A compatible, non-Egg party Pokemon is still required.

Compatibility uses the same legal learnset data as Mercury's universal Move Learner rather than a separate hand-maintained compatibility table.

Existing progression restrictions remain intact:
- badge checks preserved
- story checks preserved
- map/location checks preserved
- partner restrictions preserved
- vanilla `FindPartySlotWithMove` remains unchanged for unrelated story logic

Mercury uses the previously unused script opcode `SCRCMD_UNUSED_09C` for the isolated compatibility lookup command.

## HM-free traversal coverage

Field interaction paths:
- Cut
- Rock Smash
- Strength
- Surf
- Rock Climb
- Waterfall
- direct Defog script path

Party-menu compatibility paths:
- Fly
- Defog
- Flash

The party menu's dynamic field-move label capacity was safely expanded from four to seven to support compatible-but-not-learned field moves.

MR05A report:
- `status: PASS`
- `deferred_same_phase: []`
- `vanilla_find_party_slot_command_modified: false`

## Proved gates

The authoritative workflow proved:
- pinned Platinum/HG-Engine sources restored
- sealed Mercury overlay applied
- modern ability/species/move foundation rebuilt
- sealed MR03F player-facing Move Learner restored
- MR05A HM-free traversal installer passed
- original badge gates remain present
- unrelated Canalave Strength story check remains move-based
- CI-only direct-launch harness remains absent
- full normal-player ROM compiled successfully
- real DeSmuME normal boot completed successfully
- final player artifact uploaded

The boot proof confirms normal runtime stability. MR05A was not sealed on the basis of generated concept art.

## Normal-boot proof

Captured frames:
- 14800
- 15200
- 15600
- 16000

All captures were nonblank and show the Mercury Redux title flow running normally.

## Player ROM

Artifact:

`mercury-mr05a-hm-free-traversal`

Artifact ID:

`10911768220`

ROM filename:

`Pokemon_Mercury_MR05A_HM_Free.nds`

SHA-256:

`bbbf1ba872fe141cc626fbd46d236d947233bdf6d3674cb030e766bc7df53ca1`

## Lock

Do not reopen MR03F, MR04, or MR05A unless a later regression directly implicates them.

Future Mercury work should branch forward from the MR05A checkpoint.

**MR05A is closed.**
