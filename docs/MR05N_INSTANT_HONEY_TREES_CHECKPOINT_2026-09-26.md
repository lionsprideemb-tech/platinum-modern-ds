# Mercury DS — MR05N Instant Honey Trees

Date: 2026-09-26

## Status

**PASS / SEALED / MR05N COMPLETE**

MR05N locks the approved Mercury Honey Tree behavior on top of the completed encounter sweep and certified encounter-chart export.

## Certified workflow

- Workflow: `MR05B Authored Encounters`
- Run: `36282723838`
- Head commit: `69b62cf3783a701f1aac820def845430e568e6a0`
- Result: **PASS**
- Player artifact: `mercury-mr05n-instant-honey-trees`
- Artifact ID: `10919323155`
- Artifact size: `57,117,918 bytes`
- Artifact digest: `sha256:61ff2f9e8a51b8146a1767ce076d6290fea630f64da37387eb1bce92ec0d0186`

## Locked Honey Tree behavior

- Spend exactly 1 Honey.
- The encounter starts immediately after slathering.
- No six-hour real-world wait.
- No post-battle cooldown.
- The same tree can be used again immediately with another Honey.
- No trainer-ID special-tree lottery.
- No failed Honey roll.
- Every Honey Tree uses the Mercury premium pool.
- Tier roll: Common 70% / Uncommon 20% / Rare 10%.
- Slot roll inside each tier remains 40% / 20% / 20% / 10% / 5% / 5%.
- Burmy remains removed from the premium Honey Tree pool.

## Encounter state retained

MR05N does not rebalance the already-sealed route/cave/lake encounter tables. It preserves:

- 144 full Morning / Day / Evening / Night land resources.
- 6,912 full time-of-day land slots.
- all authored Surf and fishing tables.
- Great Marsh no-daily-gate behavior.
- MR05M complete encounter chart export.
- static/story encounter separation.
- MR05A HM-free traversal.
- MR03F dual-screen Move Learner.

## Runtime proof

The MR05N ROM compiled successfully and passed the real DeSmuME normal-boot capture.

Player ROM filename:

`Pokemon_Mercury_MR05N_Instant_Honey.nds`

## Lock

Do not reopen Honey Tree timing, cooldown, special-tree lottery, failure rolls, or premium-pool policy unless a later regression directly implicates MR05N.

The next phase is the DS-native Encounter Chart runtime/browser foundation.
