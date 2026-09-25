# CM08 Simple Electric Mechanics — PASS

Date: 2026-09-25

## Result

CM08 is certified on the main Mercury DS line.

This pass begins the custom-mechanics stage with two small, reusable
battle-script-only effects selected to improve physical Electric move variety
without introducing a new type, status, weather, terrain, or persistent battle
state.

## New battle effects

- Effect 277: `BATTLE_EFFECT_RAISE_SPEED_HIT`
  - Damages normally.
  - Uses the move's effect chance to raise the attacker's Speed by one stage.
- Effect 278: `BATTLE_EFFECT_DOUBLE_POWER_IF_TARGET_PARALYZED`
  - Uses normal power against a non-paralyzed target.
  - Uses 2x power when the defender is paralyzed.

Both effects are implemented as native Platinum battle scripts. No C-side
battle-state extension was required.

## New community moves

### ID 1276 — Lightning Strike

- Type: Electric
- Category: Physical
- Power: 70
- Accuracy: 100
- PP: 20
- Effect: 20% chance to raise the user's Speed by one stage
- Animation: provisional native Platinum `Thunder Punch` donor
- Source: Pokemon Elite Redux

### ID 1277 — Volt Bolt

- Type: Electric
- Category: Physical
- Power: 70
- Accuracy: 100
- PP: 20
- Effect: doubles in power if the target is paralyzed
- Animation: source-certified native Platinum `Volt Tackle` donor
- Source: Pokemon Elite Redux

## Namespace

- Live community moves before CM08: **252**
- Added in CM08: **2**
- Total live community moves after CM08: **254**
- Last live community move ID: **1277**
- `MAX_MOVES`: **1278**

## Main-line native proof

GitHub Actions workflow: **CM08 Simple Electric Mechanics**  
Run ID: `36144313192`  
Commit under test: `988e84b1a8c0a17ffe34d986915c40c92b6262d8`  
Conclusion: **success**

The main-line workflow rebuilt the complete 1025-species Platinum foundation,
restored the certified Gen 5-9 move layer and CM01-CM07, installed both new
battle effects and both CM08 moves, compiled the full native Platinum ROM,
executed Volt Bolt in the DeSmuME battle runtime, and uploaded the proof bundle.

Proof artifact: `cm08-simple-electric-mechanics-proof`  
Artifact ID: `10869078029`  
Artifact digest:
`sha256:fa2ff26adccdbc5bece31363d6ead599bdbd0a596aee0f0dc35504dcf79169e0`

The runtime proof executes Volt Bolt safely in native battle. The workflow also
statically verifies the paralyzed-target branch (condition check and 2x power
multiplier); the representative runtime opponent is not forcibly pre-paralyzed,
so the doubled-damage branch is not claimed as a visual damage-comparison test.

Lightning Strike's effect script and 20% Speed-boost wiring are build-verified;
its current animation is intentionally provisional and can be revisited during
the later visual-animation polish pass.

**CM08: PASS**
