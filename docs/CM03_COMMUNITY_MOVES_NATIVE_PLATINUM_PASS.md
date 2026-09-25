# CM03 Community Moves — Native Platinum PASS

Date: 2026-09-24

## Result

CM03 passed the complete compact-ID native `pokeplatinum` build and runtime
proof.

Proof run: GitHub Actions Run #3 for **CM03 Community Moves Native Platinum**
(run ID `36081748917`), conclusion **success**.

| ID | Move | Native mechanics | Platinum animation donor |
|---:|---|---|---|
| 1030 | Shocking Edge | Electric / Physical / 80 BP / 100% / 10 PP / 10% paralysis | Slash |
| 1031 | Kinetic Barrage | Psychic / Physical / 90 BP / 100% / 20 PP / 30% confusion | Strength |
| 1032 | Fairy Spheres | Fairy / Physical / 20 BP / 100% / 10 PP / 2-5 hits | DoubleSlap |
| 1033 | Zephyr Rush | Flying / Physical / 100 BP / 95% / 10 PP / crash on miss | Jump Kick |
| 1034 | Seismic Fist | Ground / Physical / 85 BP / 100% / 15 PP / 20% Defense drop | Rock Smash |
| 1035 | Primal Beam | Dragon / Physical / 90 BP / 100% / 10 PP / 20% Attack raise | Dragon Pulse |

The workflow restored CM01 and CM02 first, installed all six CM03 moves, verified
all six animation scripts against native Platinum donors, compiled the full ROM,
then executed Shocking Edge in DeSmuME.

Proof artifact: `cm03-community-moves-native-platinum-proof`  
Artifact digest:
`sha256:65a67a2889200b5d141f19aabbd82f5c41390179347bdf99789610325723b490`

After CM03, the community lane contains **12 live moves at IDs 1024-1035** and
`MAX_MOVES` is **1036**.

**CM03: PASS**
