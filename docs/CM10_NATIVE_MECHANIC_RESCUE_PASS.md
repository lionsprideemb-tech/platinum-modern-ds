# CM10 Native Mechanic Rescue — PASS / MOVE WORK FREEZE

Date: 2026-09-25

## Result

CM10 is certified and the community-move expansion is frozen here while the
project returns to the complete-playable-game path.

CM10 deliberately adds only moves whose complete battle behavior can be mapped
to mechanics already present in native Platinum. No new battle effect, field
state, status system, or persistent battle-state storage was introduced.

## Added moves

- ID 1284 — **Bad Egg**
  - Poison / Special
  - 40 BP / 100 accuracy / 10 PP
  - Guaranteed badly-poison effect on a successful hit
  - Uses native Platinum `BATTLE_EFFECT_BADLY_POISON_HIT`
  - Uses Egg Bomb as the source-backed native animation donor

- ID 1285 — **Cheap Shot**
  - Dark / Physical
  - 120 BP / 100 accuracy / 20 PP
  - Two-turn vanish / strike behavior
  - Uses native Platinum `BATTLE_EFFECT_SHADOW_FORCE`
  - Uses Shadow Force as the source-backed native animation donor

## Namespace at freeze

- Live community moves before CM10: **260**
- Added in CM10: **2**
- Total live community moves after CM10: **262**
- Last live community move ID: **1285**
- `MAX_MOVES`: **1286**

## Fast preflight

Workflow: **Mercury Move Preflight**  
Run ID: `36146852257`  
Conclusion: **success**

The preflight passed metadata, canonical-type, namespace, Platinum charmap,
installed-resource, effect-registration, animation-donor, and targeted
move-resource compilation checks before the full ROM certification was allowed
to run.

## Native certification

Workflow: **Mercury Move Certification**  
Run ID: `36147142166`  
Conclusion: **success**

The workflow:

- rebuilt the complete modern Platinum foundation,
- restored the full CM01-CM09 community stack,
- installed CM10,
- re-ran the installed-resource preflight,
- compiled the complete native Platinum ROM,
- booted that ROM in DeSmuME,
- executed the representative Cheap Shot runtime proof,
- uploaded the certification evidence.

Proof artifact: `mercury-move-certification-36147142166`  
Artifact ID: `10869858766`  
Artifact digest:
`sha256:9fe3d5e6218a2066c725ed152e378cbacea936c37d80a5f638c8230366282249`

## Freeze decision

Do **not** start CM11 yet.

The next project priority is the already-started playable-game certification.
Community-move work resumes only after the complete Platinum adventure has been
certified and frozen as the playable / modern baseline.

**CM10: PASS**  
**COMMUNITY MOVE WORK: FROZEN AT 262 MOVES / ID 1285**
