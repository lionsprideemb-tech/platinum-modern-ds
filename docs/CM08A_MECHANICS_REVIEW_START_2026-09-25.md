# CM08A Mechanics Review Start — 2026-09-25

## Starting point

CM07 is certified PASS.

- CM07 workflow run: 36141083789
- CM07 checkpoint commit: 13038270dea3b00211143b68c51ca12f2cc12cb8
- 32 / 32 non-canonical source move types have canonical Mercury type resolutions.
- 18 formerly custom-type moves are now live at IDs 1258-1275.
- Total live community moves: 252.
- MAX_MOVES is 1276.

The full catalog contains 519 community moves, so 267 remain deferred after CM07.

## What is actually left

The CM06 artifact reported 285 deferred entries before CM07. CM07 promoted 18 of the 32 custom-type entries, leaving:

- 267 total deferred moves
- 18 duplicate/design decisions rather than engine mechanics
  - 9 duplicate-decision-pending
  - 9 duplicate-rejected-or-redesign
- 249 genuine mechanics / behavior candidates

Raw deferred buckets inherited from the certified CM06 selector, excluding the original 32 custom-type bucket:

- no-native-match: 76
- new-effect-family: 61
- custom-source-effect: 50
- custom-behavior-text: 15
- duplicate-decision-pending: 9
- duplicate-rejected-or-redesign: 9
- special-move-flag: 7
- custom-stat: 6
- compound-status_effects: 2
- drain-mechanic: 2
- effect-not-native: 2
- ignore-protect-mechanic: 2
- target-needs-extension: 2
- compound-drain_or_healing-field_weather_terrain_behavior: 1
- compound-field_weather_terrain_behavior: 1
- compound-multi_hit_or_duration-switching_behavior: 1
- compound-multihit: 1
- compound-stat_changes: 1
- custom-status: 1
- extra-custom-behavior: 1
- field-mechanic: 1
- multi-status: 1
- switching-mechanic: 1

## Canonicalized moves still blocked only by mechanics

The 14 former custom-type moves that remain deferred are already retyped; only their mechanics need decisions:

1. Heart Beat — 2-5 hits, then user Speed +1 and Sp. Def -1.
2. Audio Break — damaging screen break plus disabling the target's sound moves.
3. Unleashed Power — dynamic Hidden Power typing, dynamic category, screen removal, and source zero-PP/Z-move behavior.
4. Blinding Speed — dynamic user typing/category plus ally After You-style turn manipulation.
5. Domain Shift — random route-dependent field replacement.
6. Titan's Wrath — damage from user's highest non-HP stat and move type changes to user's type.
7. Queso Blast — 3-5 hit distribution not native to Platinum.
8. Hard Drive Crash — damaging attack that removes 3 PP from the target's last move.
9. Virus Inject — custom debuff increasing all damage taken by 25%.
10. Chthonic Malady — -2 Attack/-2 Sp. Atk, Torment timer, Petrification, and protection bypass.
11. Expunge — Fallout-specific accuracy behavior needs a decision after Nuclear typing removal.
12. Fallout — five-turn Fallout field/weather effect needs redesign.
13. Quantum Leap — two-turn vanish/invulnerability needs an exact Platinum-state mapping.
14. Nuclear Wind — chance to create Fallout remains a custom field mechanic.

## Fast-path order for CM08

Do not start by writing 249 bespoke mechanics.

1. Re-audit deferred moves against the already-modernized Gen 5-9 effect layer and Platinum-native effects. Any false negatives should be promoted with no new mechanic code.
2. Group the real remaining effects into shared mechanic families so one port can unlock multiple canonical and community moves.
3. Implement the highest-yield shared families first with focused battle-runtime proofs.
4. Handle one-off bespoke mechanics only after the shared families.
5. Resolve the 18 duplicate/design decisions separately from engine work.

This preserves the user's rule: implement every move that can work without new mechanics before deciding which genuinely new mechanics are worth adding.
