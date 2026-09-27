# Mercury DS — MR06A Encounter Chart Runtime Foundation

Date: 2026-09-26

## Status

**PASS / SEALED / MR06A COMPLETE**

MR06A builds the native DS encounter-data browser foundation on top of the sealed Mercury encounter sweep and MR05N instant Honey Trees.

## Certified workflow

- Workflow: `MR05B Authored Encounters`
- Run: `36283896982`
- Head commit: `a00eb8c9f5e9320eb51fd07afb67ed01121db862`
- Result: **PASS**
- Player artifact: `mercury-mr06a-encounter-chart-runtime`
- Artifact ID: `10920355413`
- Artifact size: `57,119,946 bytes`
- Artifact digest: `sha256:06b84180baaf8e83a27f28511ec8fb5c7e4c139fd30c290ff9c72ae2388ca8ff`

## Runtime foundation now locked

- 158 standard player-facing encounter resources are browsable from native DS runtime data.
- 144 resources expose complete Morning / Day / Evening / Night land tables.
- The browser API exposes Surf, Old Rod, Good Rod, and Super Rod data.
- Slot output includes species, exact slot odds, and min/max level ranges.
- Current-area lookup resolves through the live Platinum map-header / encounter-NARC relationship.
- No second hand-authored runtime encounter database was created.
- The 25 orphan `unknown_533` through `unknown_557` members remain excluded.
- Turnback Cave's three authored-but-disconnected runtime links are repaired.
- Giratina's terminal room intentionally remains no-random.

## Exact Mercury clock windows retained

- Morning: 05:00-09:59
- Day: 10:00-16:59
- Evening: 17:00-20:59
- Night: 21:00-04:59

MR06A uses the same RTC selector as MR05O, including 04:00 = Night and 20:00 = Evening.

## Build correction during certification

The first MR06A compile exposed one invalid sentinel name in the new browser helper: `MAP_HEADER_MYSTERY_ZONE` does not exist in Platinum's generated map-header namespace. It was replaced with the valid neutral sentinel `MAP_HEADER_NOTHING`.

The corrected rerun passed the full ROM compile and the real DeSmuME normal-boot capture.

## Preserved sealed systems

MR06A retains:

- MR05N instant reusable Honey Trees and premium pool.
- MR05M complete encounter-chart export.
- all authored route, cave, lake, Great Marsh, Surf, and fishing tables.
- MR05O exact four-period encounter timing.
- MR05A HM-free traversal.
- MR03F dual-screen Move Learner.
- the 1025-species modern foundation.
- the pre-League Regi loop and legendary-static safety pass.

## Next phase

**MR06B — native DS Encounter Chart presentation.**

Build the actual player-facing dual-screen browser on top of the MR06A runtime API. The UI pass should also add dedicated Honey Tree and Great Marsh lookout adapters rather than duplicating those resources into the standard encounter database.

## Lock

Do not reopen MR06A data lookup, exact period windows, Turnback runtime-link policy, or orphan-resource classification unless a later regression directly implicates them.
