# MR09C Fast-Hook Custom Ability Implementation Spec

Status: IMPLEMENTATION-READY  
Branch: `planning/mr09-custom-ability-redesigns`  
Date: 2026-09-28

This pass implements the first five approved custom abilities after MR09's
custom namespace has been installed.

Reserved IDs:
- 315 — CONTROLLED FURY
- 316 — ETERNAL LIFE
- 317 — HOLLOW SHELL
- 318 — MIND GAMES
- 320 — THE LOOK

## Shared rules

- Use Mercury's effective Ability resolver, so ordinary suppression works.
- Primary/Innate routing must continue to work through the same effective layer.
- Once-per-battle state is keyed by side + party slot, not battler slot.
- Temporary active-state is cleared when the holder leaves the field.
- None of this pass changes MR07 Summary/editor visuals.
- All custom hooks remain outside the canonical MR08 implementation registry
  until this pass is actually installed and validated.

## 315 — Controlled Fury

Trigger:
- The first time in a battle that the holder's HP changes from above 50% to
  50% or below while the holder remains alive.
- The crossing may be caused by direct damage, recoil, status, weather, hazards,
  or another legal HP-loss source.
- A lethal drop to 0 HP does not trigger it.

On activation:
- +1 Attack.
- +1 Speed.
- Starts Fury for the next 3 full turns after the activation turn.

While Fury is active and Controlled Fury is not suppressed:
- damaging moves deal 1.10x damage;
- after a successful damaging move, the holder loses 10% max HP as recoil,
  minimum 1 HP where applicable;
- ordinary recoil rules may stack with the move's own recoil.

Once-per-battle guard:
- party-persistent bitmask per side.
- Switching cannot reset the once-per-battle trigger.
- Switching does clear the active Fury turn counter.

Engine plan:
- detect the HP threshold from the common HP-value update path rather than only
  the on-hit Ability dispatcher;
- mark the party-slot bit before launching the activation response, preventing
  recursive activation from later HP updates;
- apply the 1.10x modifier in the normal damaging-move power/final-damage lane;
- use an after-move state for Fury recoil so multi-hit moves recoil once after
  the complete move rather than once per hit.

## 316 — Eternal Life

Trigger:
- The first time in a battle that the holder's HP changes from above 50% to
  50% or below while it remains alive.
- A lethal hit ending at 0 HP does not trigger; Eternal Life is not a revival.

On activation:
- restore 25% max HP, capped at max HP;
- clear the major status condition;
- clear Nightmare if it is present because the former status was sleep;
- every negative stat stage returns to the neutral/default stage;
- positive stat stages are preserved.

Once-per-battle guard:
- party-persistent bitmask per side.

Engine plan:
- share the same battle-wide half-HP threshold detector used by Controlled Fury;
- mark used state before applying healing;
- use the normal HP-bar update path for the 25% heal;
- refresh the health-box status icon after curing status;
- do not use the old 15-turn revival logic anywhere.

## 317 — Hollow Shell

Trigger:
- holder is KO'd by a direct damaging move;
- defender must be the current fainted battler;
- the attack must actually have connected and caused direct HP damage.

Does not trigger from:
- poison/burn;
- weather;
- entry hazards;
- recoil/self-KO;
- Destiny Bond-style effects;
- other indirect damage.

Effect:
- attacker loses 25% max HP;
- attacker cannot be reduced below 1 HP;
- if attacker is already at 1 HP, announce Hollow Shell but deal 0 HP;
- contact is not required.

Engine plan:
- share the defender on-hit/faint lane currently used by Aftermath-style
  mechanics, but do not inherit Aftermath's contact requirement;
- calculate loss as min(maxHP / 4, currentHP - 1);
- use the existing Aftermath damage subscript because its message already
  references the fainted defender's actual Ability dynamically;
- treat Hollow Shell as an ignorable defensive Ability for Mold Breaker-family
  attacks.

## 318 — Mind Games

Trigger:
- on switch-in, once for that field appearance.

Target:
- Singles: the only living opposing battler.
- Doubles: the living opposing battler directly across from the holder; if that
  slot is empty, use the other living opponent.

Effect:
- read that target's `movePrevByBattler`;
- if it is MOVE_NONE, Struggle, or no longer present in the target's moveset,
  Mind Games has no seal to apply;
- otherwise store the exact move and seal it for 2 turns;
- the sealed move cannot be selected while the timer is active;
- switching the target clears the seal immediately.

Engine plan:
- store sealed move, remaining turns, and target party-slot identity in
  BattleContext;
- add Mind Games to the same invalid-move-selection path that already handles
  Disable/Torment/Imprison;
- use the existing "sealed move" selection-error message;
- decrement the timer once at end of turn;
- AI move selection uses the same invalid-move mask, so no separate AI rule is
  required.

## 320 — The Look

Effect:
- while at least one opposing active battler has The Look, a battler may not
  select the same move it used immediately previously;
- applies to both damaging and status moves;
- ends immediately when all opposing The Look holders leave the field or lose
  the effective Ability.

Engine plan:
- do not apply the Torment volatile status;
- in `BattleSystem_CheckInvalidMoves`, treat a candidate matching
  `movePrevByBattler[battler]` as invalid when an opposing active effective
  Ability is The Look;
- reuse the existing Torment selection-error text;
- because the restriction is checked dynamically, switching the holder out
  removes the restriction without cleanup state;
- doubles naturally work if either opposing active battler has The Look.

## Validation gates

MR09C cannot be marked implemented until tests confirm:

- custom IDs 315, 316, 317, 318, and 320 exist exactly;
- Controlled Fury triggers once per party Pokémon per battle;
- Controlled Fury does not trigger from a lethal HP drop;
- Fury lasts three full post-activation turns and clears on switch;
- Fury boost is 1.10x and recoil occurs once per successful damaging move;
- Eternal Life triggers once, heals exactly 25%, cures status, and clears only
  negative stages;
- Eternal Life does not revive from 0 HP;
- Hollow Shell triggers only on direct damaging KOs;
- Hollow Shell cannot reduce attacker below 1 HP;
- Mind Games seals exactly the last-used legal move for two turns;
- Mind Games clears on target switch;
- The Look blocks immediate repetition while active and stops immediately when
  no opposing holder remains;
- player and AI move legality agree for Mind Games and The Look;
- suppression behavior uses the effective Ability layer;
- multi-hit and spread moves do not double-trigger pass-local reactions;
- MR07 locked visuals are untouched.
