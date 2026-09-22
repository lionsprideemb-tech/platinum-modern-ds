# DS04 Checkpoint — Twinleaf Transplant Staging

**Status:** CHECKPOINTED / PRE-RUNTIME-INTEGRATION

This checkpoint preserves the first real Twinleaf transplant staging layer before the heavier HG-Engine build integration begins.

## Completed

- DS03 world-compatibility checkpoint is the certified base.
- Append-only NARC writer added at `tools/narc_append.py`.
- Synthetic NARC regression test added at `tests/test_narc_append.py`.
- DS04 staging tool added at `tools/stage_ds04_twinleaf.py`.
- Twinleaf visual/land resources are staged append-only from pinned Platinum source.
- Reserved target archive counts are enforced before modification.
- Six converted Platinum land-data members are appended at target IDs 676–681.
- Twinleaf AreaData members are generated at target IDs 106–107.
- Compact Twinleaf prop sets are generated at target IDs 104–105.
- Twinleaf map textures are appended at target IDs 106–107.
- Twinleaf prop textures are appended at target IDs 104–105.
- Four exterior prop models are appended at target IDs 340–343.
- Twenty-two interior prop models are appended at target IDs 222–243.
- Six isolated 1×1 Twinleaf matrices are generated at IDs 288–293.
- Seven Twinleaf map constants are reserved at IDs 540–546.
- `MAP_ID_MAX` is expanded from 540 to 547.
- Seven source-level map-header entries are generated.
- Project-owned no-op script and init banks are staged at IDs 965 and 966.
- Optional controlled test-start patch targets imported Player House 2F.
- Staging verification checks archive counts, constants, headers, matrices, and output IDs.

## Deliberate safety choices

- No normal New Game redirect is committed yet.
- No Platinum story scripts are executed yet.
- No Johto story script is reused for the proof room.
- No existing HGSS archive member is overwritten.
- No commercial ROM is stored in the repository.
- Every imported source is derived from pinned public source trees.

## Next runtime gates

1. Add DS04 CI that stages Twinleaf into a clean pinned pokeheartgold checkout.
2. Build pokeheartgold successfully with the staged resources.
3. Feed the staged HeartGold build into pinned HG-Engine.
4. Compile HG-Engine successfully.
5. Produce a controlled test build starting in Platinum Player House 2F.
6. Validate static render, collision, camera, and player placement.
7. Add the Player House 2F → 1F warp only after the room itself renders correctly.
8. Expand to Player House 1F → Twinleaf Town.
9. Only after that, begin NPC sprite/script/message translation.

## Recovery

This checkpoint is intended as a clean restart point if the DS04 runtime integration becomes unstable.

Do not modify the DS03 certified checkpoint. Continue runtime work from the DS04 feature branch or a child branch of this checkpoint.
