# PB02 Route 202 Tutorial Checkpoint — 2026-09-25

## Status

**PASS / SEALED CONTINUATION POINT**

The normal PB01 playable candidate has now progressed through the post-Parcel
return to Route 202 and completed Dawn's vanilla catching tutorial.

This remains the stock Platinum story/world baseline. No custom move-mechanics
work is being layered into this playable certification path.

## Proven progression

The certified chain now includes:

- Rowan intro and naming
- Twinleaf opening
- Barry THUD / rival house progression
- Route 201 and Lake Verity opening
- starter selection and first rival battle
- Sandgem / Rowan Lab / Pokédex progression
- Dawn's Sandgem tour
- return to Twinleaf and Parcel handoff
- return through Route 201 to Sandgem
- Route 202 entry
- Dawn catching tutorial
- field control restored after the tutorial

## Key Route 202 proof

Trigger discovery:
- A13F run ID: `36149969353`
- The tutorial trigger fires when moving from **(181,825)** to **(180,825)**.
- Visual proof shows Dawn intercepting the player with:
  `Dawn: Oh, that's right!`

Tutorial completion:
- A13G run ID: `36150353863`
- Visual proof includes Dawn's scripted Piplup vs Bidoof demonstration.
- Post-event screenshot shows Dawn gone and the player returned to Route 202.

Control proof:
- A13H run ID: `36151070809`
- Starting coordinate: **(178,825)**
- A right step moved the player to **(179,825)**.
- Field control after the tutorial is therefore independently proven.

A13H artifact:
- Name: `mercury-phase-a13h-route202-control-proof`
- Artifact ID: `10871896931`
- Digest: `sha256:25d876aec3e21d7fb98a04f95f906415c71af6fc5f35685978871af6cc2ff2d6`
- Continuation state: `phase-a13h-route202-control-confirmed.dst`

## Next gate

**PB02 / A14 — first normal Route 202 wild battle and capture**

After capture proof:
1. save normally,
2. reset / continue,
3. finish Route 202 to Jubilife,
4. continue the complete Platinum progression certification.

**PLAYABLE BASELINE PRIORITY REMAINS ACTIVE.**
