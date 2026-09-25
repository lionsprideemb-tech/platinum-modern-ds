# CM02 Community Moves — Native Platinum PASS

Date: 2026-09-24

## Result

CM02 passed the complete native `pokeplatinum` build and runtime proof.

The proof run was GitHub Actions Run #1 for **CM02 Community Moves Native Platinum**
(run ID `36067457275`), conclusion **success**.

## Installed community moves

CM01 remains installed at IDs 2048-2050.

| ID | Move | Native mechanics | Platinum animation donor |
|---:|---|---|---|
| 2051 | Lightning Bullet | Electric / Physical / 90 BP / 100% / 15 PP / 10% paralysis | Zap Cannon |
| 2052 | Venom Bolt | Poison / Physical / 75 BP / 100% / 10 PP / high critical ratio + 20% poison | Poison Sting |
| 2053 | Smolder Bash | Fire / Physical / 80 BP / 100% / 15 PP / 10% burn | Flare Blitz |

## Runtime proof

Lightning Bullet was injected into move slot 1 of the native Platinum battle
harness and exercised in DeSmuME from the compiled `pokeplatinum` ROM.

The workflow also compared every CM02 animation script byte-for-byte against its
selected native Platinum donor before the ROM build.

Proof artifact:
`cm02-community-moves-native-platinum-proof`

## Certification

**CM02: PASS**

CM01 + CM02 prove that the cumulative community-move lane can append multiple
batches, retain earlier custom IDs, compile the complete modernized Platinum
build, and execute a selected custom move in the actual battle runtime.

## Next

CM03 increases the batch size from three moves to six. The full batch is
compile/data/animation-source validated, while one representative move receives
the expensive emulator/video runtime proof. This keeps the reliability gate
without requiring a full visual capture for every individual move.
