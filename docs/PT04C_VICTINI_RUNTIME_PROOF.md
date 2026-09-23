# PT04C — Victini Native Platinum Build/Boot Proof

PT04A proved that Platinum's core species ID and Pokédex sizing can exceed the original 493-species boundary. PT04B added and validated Mercury DS's canonical #1–#1025 base-species registry.

PT04C now crosses the first real engine boundary: **National Dex #494 Victini is registered as a native species entry immediately after Arceus and before the Egg/Bad Egg sentinels, and the ROM must still build and boot.**

## What this gate proves

- `SPECIES_VICTINI == 494` in the generated Platinum enum.
- Egg and Bad Egg safely shift upward instead of occupying fixed IDs.
- Platinum's per-species data compiler accepts a post-Gen-IV data slot.
- `pl_personal`, evolutions, learnset, height/sprite metadata, icon, battle sprite and Pokédex-text pipelines all receive the new base species.
- The final NDS still boots under DeSmuME with the previously certified Mercury/Platinum modifications applied.
- Graphics are sourced reproducibly from the pinned HG-Engine donor already recorded in `upstream/LOCK.json`.

## Intentionally temporary PT04 compatibility data

PT04 is about **species architecture**, not yet the full PT05 battle-data import. The first Victini build therefore uses several explicit smoke-test placeholders rather than silently pretending the modern data layer is finished:

- Synchronize stands in until Victory Star is added with the expanded ability system.
- The learnset uses a small set of moves Platinum already knows.
- A known-good native cry pair is used until modern cry assets are imported.
- The normal palette is mirrored into the shiny slot until the bulk sprite/palette pass.

The visible normal front/back sprite and icon are the actual Victini donor graphics, not a substituted Gen-IV Pokémon.

## Certification sequence

1. Build the current Mercury DS Platinum base with Victini at #494.
2. Boot the produced ROM and capture real emulator output.
3. After build/boot is clean, add a temporary PT04 runtime harness that places Victini into a native party/battle path.
4. Certify party, summary, battle, PC and Pokédex encounter/capture behavior before expanding the Gen V batch.
