# CM09 Shared Speed Boost Family — PASS

Date: 2026-09-25

## Result

CM09 is certified on the main Mercury DS line.

This pass reused the battle-script effect introduced in CM08 instead of adding
six one-off mechanics. Six previously deferred community moves now share
`BATTLE_EFFECT_RAISE_SPEED_HIT`, with each move keeping its audited 50% or
100% activation rate.

## Added moves

- ID 1278 — **Zap Jive**
  - Electric / Special
  - 80 BP / 100 accuracy / 10 PP
  - 50% chance to raise the user’s Speed by one stage
  - Dance trait retained as metadata
  - Provisional native Platinum Thunderbolt animation

- ID 1279 — **Hex Trot**
  - Ghost / Special
  - 80 BP / 100 accuracy / 10 PP
  - 50% chance to raise the user’s Speed by one stage
  - Dance trait retained as metadata
  - Provisional native Platinum Shadow Ball animation

- ID 1280 — **Frost Walker**
  - Ice / Physical
  - 50 BP / 100 accuracy / 20 PP
  - Always raises the user’s Speed by one stage
  - Makes contact
  - Provisional native Platinum Ice Punch animation
  - The source game’s out-of-battle water-freezing traversal rider is not part
    of the battle move implementation.

- ID 1281 — **Enigmatic Dash**
  - Fairy / Physical
  - 50 BP / 100 accuracy / 20 PP
  - Always raises the user’s Speed by one stage
  - Makes contact
  - Provisional native Platinum Quick Attack animation

- ID 1282 — **Rain of Fists**
  - Fighting / Physical
  - 70 BP / 90 accuracy / 15 PP
  - 50% chance to raise the user’s Speed by one stage
  - Contact + punch traits retained
  - Provisional native Platinum Mach Punch animation

- ID 1283 — **Sea Breeze**
  - Water / Physical
  - 70 BP / 100 accuracy / 20 PP
  - Always raises the user’s Speed by one stage
  - Makes contact
  - Provisional native Platinum Aqua Jet animation

## Namespace

- Live community moves before CM09: **254**
- Added in CM09: **6**
- Total live community moves after CM09: **260**
- Last live community move ID: **1283**
- `MAX_MOVES`: **1284**

## Fast preflight proof

GitHub Actions workflow: **Mercury Move Preflight**  
Run ID: `36146098329`  
Commit under test: `1ccf7e4c64907b18798bf19ff7676251a91dc6de`  
Conclusion: **success**

The preflight verified metadata, ID contiguity, canonical types, Platinum
charmap compatibility, effect registration, installed move resources, animation
donors, and the targeted move-sensitive resource build before the expensive
full ROM compile.

Preflight artifact: `mercury-move-preflight-proof`  
Artifact ID: `10870010981`  
Artifact digest:
`sha256:397c7491c83aa4993ac808cd1e7729e337bb5719ca5f9b5bcd9a0fe73f996c52`

## Main-line native proof

GitHub Actions workflow: **CM09 Shared Speed Boost Family**  
Run ID: `36146098227`  
Commit under test: `1ccf7e4c64907b18798bf19ff7676251a91dc6de`  
Conclusion: **success**

The main-line workflow rebuilt the complete 1025-species Platinum foundation,
restored CM01-CM08, installed all six CM09 moves, compiled the full native
Platinum ROM, executed Frost Walker in the DeSmuME battle runtime, and uploaded
the proof bundle.

Proof artifact: `cm09-shared-speed-boost-family-proof`  
Artifact ID: `10869951439`  
Artifact digest:
`sha256:c0431f763a7ddbc831e1868beac215aad39a66dfbcd6f114cb0460b09f2df749`

The representative emulator proof confirms Frost Walker executes through the
native battle runtime without stopping the game. The shared effect registration,
per-move effect chances, and all six animation donor copies are independently
verified by the workflow.

**CM09: PASS**
