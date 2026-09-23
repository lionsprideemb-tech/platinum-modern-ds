# PT04C Victini Boundary-Proof Closure — 2026-09-23

## Status

**PASS / SEALED / PT04C COMPLETE**

PT04C proves that a post-Gen-IV species at the first expanded boundary slot, **SPECIES_VICTINI / National Dex 494**, can complete the native Pokémon Platinum runtime lifecycle without replacing a vanilla species.

## Sealed runtime chain

- Run #8 — native Party + Pokédex seen/caught
- Run #12 — native Summary
- Run #13 — native PC Storage
- Run #28 — native Battle
- Run #33 — native Save → system reset → native reload

Earlier gates are sealed and are not to be repeated unless a future regression directly implicates them.

## Final save/reload proof

GitHub Actions workflow run:

- Run number: **33**
- Run ID: **35890163232**
- Head commit: **f8ebba9a1937c043e15b6e09aafa3cb9ba943ddf**
- Conclusion: **success**

Artifact:

- Name: `pt04c-victini-native-save-reload-proof`
- Artifact ID: **10764533332**
- SHA-256: `f3d0af7acfed3bf9dd1d0077170bc06c24abb1a0029bf0dd6280bef15b227eb9`

## Native persistence path proven

The isolated CI harness:

1. Asserted Victini #494 was present in the native party and recorded Seen/Caught.
2. Saved through `FieldSystem_Save(fieldSystem)`.
3. Performed `OS_ResetSystem(RESET_ERROR)`.
4. Re-entered through Platinum's native `gGameStartLoadSaveAppTemplate` / `SaveData_Load` path.
5. Rebuilt the saved overworld.
6. Asserted after reload:
   - party contains `SPECIES_VICTINI`
   - Pokédex Seen flag survived
   - Pokédex Caught flag survived
   - party slot 0 species is `SPECIES_VICTINI`
   - party slot 0 level is 50
7. Opened Platinum's native Party application after reload for visual proof.

## Visual verification

Captured DeSmuME frames were manually reviewed.

- Frame 1440: pre-reset Twinleaf/player-bedroom field state is stable.
- Frame 1560: reset transition is visibly in progress.
- Frame 1800: post-reload native Party UI displays **VICTINI Lv.50, 174/174 HP**.
- Frame 3600: the same reloaded Party state remains stable with **VICTINI Lv.50, 174/174 HP**.

This is a real persistence proof, not an in-memory copy test: the system reset routes through the native saved-game loader before the post-reload assertions execute.

The clean Run #33 frame 1800 and frame 3600 captures were compared against the independently successful Run #32 captures and are byte-for-byte identical, providing a second consistency check on the visual result.

## PT04C conclusion

The boundary species lifecycle is now proven end-to-end:

**Register #494 → create → Party → Pokédex → Summary → PC → Battle → Save → Reset → Reload**

PT04C is closed.

## Next phase

Do **not** repeat the full lifecycle manually for every later Pokémon.

The next implementation phase should use the now-proven engine path for **bulk post-493 roster expansion**, with automated registry/data/resource validation and representative spot tests for special cases such as forms, regional variants, Megas, unusual evolution structures, and other nonstandard species data.
