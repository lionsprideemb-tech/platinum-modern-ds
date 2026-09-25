# PB04 First Playable Seal — 2026-09-25

## Status

**SEALED / COMPLETE PLATINUM FOUNDATION**

PB04 converts the successful PB03 structural full-game certification into the
permanent playable baseline milestone.

The project is no longer doing room-by-room or end-to-end replay testing for
this baseline. The user explicitly approved the faster structural path.

## Parent proof

- PB03 workflow run: `36154284177`
- PB03 conclusion: **success**
- PB03 artifact: `mercury-redux-pb03-complete-platinum-baseline`
- PB03 artifact ID: `10872483436`
- PB03 artifact digest:
  `sha256:edaf470fadfe6f9b269e7f995afd0ea4d05c0f50cb5e6df53c9052ab55df7684`

## Sealed ROM

The sealed binary is the already-proven PB01 game ROM, re-certified by PB03:

- Size: `134217728` bytes
- SHA-256:
  `87a8f97f884b5496a16fa7b1b85ea6589e9e9e1cf4a03e9110ecdc09dfe91f16`

## Why this is the full-game baseline

The ROM keeps Platinum's native maps, world progression, story scripts,
trainers, mandatory events, League, Cynthia, credits, and save flow. PB03
proved that the playable-alpha work after PB01 did not change ROM-relevant
source and that the Mercury overlay contains no replacement world/story/map/
event resources.

Runtime smoke work additionally reached Route 202 through normal game flow and
proved a normal wild battle command menu.

## Development rule from here

Do not modify this checkpoint.

All modernization now branches from PB04. Modern learnsets, evolutions, moves,
abilities, and later Mercury systems must be added in separate reversible
passes.

**PB04 FIRST PLAYABLE SEAL: PASS**
