# PB03 Complete Platinum Baseline — Structural PASS

Date: 2026-09-25

## Decision

The project is switching from slow room-by-room playthrough certification to a
faster structural certification path.

The user explicitly approved skipping exhaustive play testing in order to reach
a finished-game baseline faster.

## What was proven

PB03 reuses the already certified PB01 ROM and proves that the 156 commits made
after PB01 on the playable-alpha branch did not alter any ROM-relevant game
source. They added only QA workflows, QA helper scripts, and checkpoint
documentation.

PB03 also verifies that the Mercury Platinum overlay contains no replacement
world, map, field, event, or story-script resources. The native Platinum
adventure therefore remains the inherited progression from New Game through the
League and credits.

## PB01 ROM identity

- Source run: `35919890042`
- Source commit: `78b2fd48f78a9af725877fae7890b9d7db8f8fdc`
- ROM size: `134217728` bytes
- ROM SHA-256:
  `87a8f97f884b5496a16fa7b1b85ea6589e9e9e1cf4a03e9110ecdc09dfe91f16`

The PB03 workflow downloaded that exact artifact and verified the binary before
re-sealing it under the complete-baseline name.

## Runtime smoke coverage retained

The same PB01 binary was already exercised through normal player-facing
progression from the title screen through the opening sequence, Twinleaf,
Route 201, Lake Verity, Sandgem, Rowan's lab, the family Parcel return, Route
202, the catching tutorial, restored field control, and a normal Route 202 wild
battle command menu.

Latest normal-battle proof:

- Run: `36151347403`
- Result: **success**

No further end-to-end replay is required for this baseline.

## PB03 proof

Workflow: **PB03 Fast Full Story Inheritance Seal**  
Run ID: `36154284177`  
Conclusion: **success**

Artifact: `mercury-redux-pb03-complete-platinum-baseline`  
Artifact ID: `10872483436`  
Artifact digest:
`sha256:edaf470fadfe6f9b269e7f995afd0ea4d05c0f50cb5e6df53c9052ab55df7684`

The artifact contains the re-sealed complete Platinum baseline ROM plus the
machine-readable structural proof.

## Scope

PB03 certifies the **complete native Platinum adventure as the inherited game
baseline without requiring an end-to-end manual playthrough**.

It does not claim that future Mercury gameplay modifications are automatically
safe. Those changes must continue to build from this frozen baseline in
separate, reversible phases.

**PB03 COMPLETE PLATINUM BASELINE: PASS**
