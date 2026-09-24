# CM01 Community Moves — Native Platinum PASS

Date: 2026-09-24

## Result

CM01 passed the complete native `pokeplatinum` build and runtime proof.

The proof run was GitHub Actions Run #1 for **CM01 Community Moves Native Platinum**
(run ID `36066480130`), conclusion **success**.

## Installed community moves

| ID | Move | Native mechanics | Platinum animation donor |
|---:|---|---|---|
| 2048 | Draconic Fangs | Dragon / Physical / 85 BP / 100% / 15 PP / 20% flinch | Bite |
| 2049 | Aqua Bash | Water / Physical / 80 BP / 100% / 15 PP / 20% flinch | Aqua Tail |
| 2050 | Atomic Fire | Fire / Special / 120 BP / 100% / 10 PP / 1/3 recoil | Fire Blast |

IDs 920-2047 remain protected for future official moves. The first community move
lane begins at 2048.

## Runtime proof

Draconic Fangs was injected into move slot 1 of the native Platinum battle harness
and executed in DeSmuME from the compiled `pokeplatinum` ROM.

The captured proof shows:
- native Platinum battle UI
- battle text: **BIDOOF used Draconic Fangs!**
- the copied native Bite animation visibly playing on the target
- target damage/faint flow completing normally
- emulator returning to the native field after the battle

Proof artifact:
`cm01-community-moves-native-platinum-proof`

The recorded MP4 was 256×192 at 15 fps, 85 seconds, 1,275 frames.

## Certification

**CM01: PASS**

This is the first community/fan-made move batch proven playable inside the actual
native Platinum runtime rather than merely compiling as data.

## Next

CM02 continues with another small batch, prioritizing straightforward effects that
already exist natively in Platinum so failures can be isolated quickly.
