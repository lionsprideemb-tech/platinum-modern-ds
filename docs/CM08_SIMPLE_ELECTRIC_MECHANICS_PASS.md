# CM08 Simple Electric Mechanics — PASS

Date: 2026-09-25

## Result

CM08 is certified in native `pokeplatinum`.

This phase introduced the first two community moves that required new battle
mechanics rather than only reusing existing Platinum effects.

## Added effects

- Effect 277: `BATTLE_EFFECT_RAISE_SPEED_HIT`
  - Damaging move
  - Uses the move's effect chance to raise the user's Speed by 1 stage
- Effect 278: `BATTLE_EFFECT_DOUBLE_POWER_IF_TARGET_PARALYZED`
  - Damaging move
  - Doubles power when the target is paralyzed

Both extensions are battle-script-only. No new status, field state, weather,
terrain, type, or C-side battle-state storage was required.

## Added moves

- ID 1276 — `MOVE_LIGHTNING_STRIKE`
  - Electric / Physical
  - 70 BP / 100 accuracy / 20 PP
  - 20% chance to raise the user's Speed by 1 stage
  - Provisional native DS animation donor: Thunder Punch
- ID 1277 — `MOVE_VOLT_BOLT`
  - Electric / Physical
  - 70 BP / 100 accuracy / 20 PP
  - Doubles power if the target is paralyzed
  - Source-backed native DS animation donor: Volt Tackle

After CM08:

- Total live community moves: **254**
- Last live community move ID: **1277**
- `MAX_MOVES`: **1278**

## Native proof

GitHub Actions workflow: **CM08 Simple Electric Mechanics**  
Run ID: `36143437317`  
Conclusion: **success**

The workflow rebuilt the complete modern Platinum move foundation, restored
CM01-CM07, installed both new effects and moves, compiled the full native
Platinum ROM, and completed a DeSmuME battle runtime proof using Volt Bolt.

Proof artifact: `cm08-simple-electric-mechanics-proof`  
Artifact ID: `10869251698`  
Artifact digest:
`sha256:94715becd58c45955db809528ea8bc595b2db4a76afdadb34e2433a9c567db91`

**CM08: PASS**
