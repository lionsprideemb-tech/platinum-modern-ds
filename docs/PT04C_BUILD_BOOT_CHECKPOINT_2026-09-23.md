# PT04C build and automated boot checkpoint — 2026-09-23

## Source of truth

- Repository: https://github.com/lionsprideemb-tech/platinum-modern-ds
- Branch: `feature/pt04c-victini-runtime`
- Tested commit: `1d8d63ede967ddf3f879cd7a42ea3e8f5e9cc0ce`
- Passing workflow run #5: https://github.com/lionsprideemb-tech/platinum-modern-ds/actions/runs/35873566079
- Proof artifact: https://github.com/lionsprideemb-tech/platinum-modern-ds/actions/runs/35873566079/artifacts/10756196067
- Artifact expires 2026-10-07; source and this checkpoint remain in Git.

## Verified from the completed CI job and logs

The pinned native Platinum source built a ROM with Victini registered at species ID 494, before Egg and Bad Egg. The existing Mercury overlay and title generator were applied.

| Check | Result |
| --- | --- |
| ROM compile/link | Passed |
| Personal-data archive | 509 members |
| Battle-sprite archive | 2970 members (495 x 6) |
| Icon archive | 548 members |
| DeSmuME automated boot smoke test | Passed |
| Proof artifact upload | Passed; seven files |

The boot smoke test advances to frames 14800, 15600, and 16000 and requires at least one nonblank capture. This proves only that the automated boot gate passed; it does not certify playable progression, sprite appearance, party, battle, PC, or Pokédex behavior. Screenshot visual review remains pending: the artifact download returned HTTP 403 in the recovery workspace.

## Fixes recovered during this continuation

1. Use a documented temporary base experience reward of 255 because the native field accepts only 0–255; intended value 300 requires later field/runtime expansion.
2. Remove an unsupported straight apostrophe from the temporary Pokédex entry.
3. Supply and register the required footprint resource using the native NONE footprint while `footprint.has` is false.
4. Copy the pinned donor's front/back PNG key files alongside the sprite files.
5. Write JASC palettes with CRLF line endings required by nitrogfx.

The earlier run #4 produced a ROM but correctly failed archive verification: sprite conversion errors left only 2966 battle-sprite members. Run #5 restored all 2970 expected members. Do not treat run #4 as the successful checkpoint.

## Temporary data still outstanding

- Synchronize in place of Victory Star.
- Gen IV compatible subset of moves.
- Native Mew cry placeholder.
- Normal palette mirrored into the shiny slot.
- Experience reward 255 in place of intended 300.
- Native NONE footprint in place of authentic Victini footprint art.
- Template-derived sprite animation/offset metadata still needs runtime review.

## Next authorized implementation step

Build a temporary native runtime harness placing Victini into a party and battle. Verify summary, front/back graphics and palette, icon, moves, battle participation, PC deposit/withdrawal, Pokédex seen/caught, and save/reload. Inspect the boot captures as part of that work. Do not certify PT04C in full or expand the Gen V batch until these runtime checks pass.
