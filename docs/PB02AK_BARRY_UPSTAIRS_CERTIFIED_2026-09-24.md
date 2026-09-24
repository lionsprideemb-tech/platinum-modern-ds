# PB02AK Barry Upstairs Certified — 2026-09-24

## Status

**PASS / SEALED**

The opening Twinleaf rival-house progression is now visually proven through Barry's upstairs departure.

## Proven chain

Starting from the already sealed PB02AA Twinleaf checkpoint:

- Barry THUD event completed,
- Barry house 1F entered normally,
- native 1F stair approach reached,
- the correct stair transition was identified:
  - from the verified near-stair position: **UP x3 -> RIGHT x1**
- Barry house 2F loaded correctly,
- native automatic upstairs dialogue appeared,
- Barry's first message displayed:
  - "...I'd better take my Bag and Journal, too..."
- second message displayed:
  - "Oh, hey, MERCURY!"
  - "I'll be waiting on the road!"
  - "It's a $10 million fine if you're late!"
- Barry left the room,
- the final screenshot shows the player alone in Barry's 2F bedroom after the departure sequence.

## CI proof

- Workflow: `PB02AK Barry Stair Horizontal Probe`
- Run ID: **35990192376**
- Commit: `c2e2eb5ccd936a876a26a9c8a9c4db2d5760feba`
- Result: **success**
- Artifact: `pb02ak-barry-stair-horizontal-proof`
- Artifact ID: **10803922585**
- Artifact SHA-256: `f9833fd063b87a12aa3f7929c120a3a5336ea73ec8e11f86718aaa9e14205ad6`

## Continuation state

The artifact contains:

`pb02ak-horizontal-probe.dst`

This state is after Barry's upstairs dialogue/departure and is the preferred continuation point for the playable test.

## Exact next gate

### PB02AL — Exit Barry house -> Route 201 / Lake Verity

Resume from `pb02ak-horizontal-probe.dst`.

Use the faster risk-based test policy:

- verify field control after Barry leaves,
- exit Barry house,
- move north out of Twinleaf,
- verify Route 201,
- follow Barry toward Lake Verity,
- verify Rowan/Dawn encounter and starter-selection progression,
- capture milestone screenshots rather than every tile.

Do not replay Rowan, naming, player house, Twinleaf THUD, or Barry upstairs unless a later regression invalidates them.
