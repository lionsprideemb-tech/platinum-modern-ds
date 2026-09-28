# MR09 Custom Ability Health Redesigns

Status: APPROVED DESIGN / IMPLEMENTATION PLANNING  
Parent: `feature/mr08-canonical-abilities`  
Date: 2026-09-28

This document records the approved Mercury redesigns for the 11 custom/non-canon abilities that failed or required special handling in the game-health audit. It does not modify the canonical MR08 ability pass.

## Approved redesigns

### Prismatic Pelt
Formerly: Prismatic Fur

- On switch-in, gains **Prismatic Veil** for 3 turns.
- While active, super-effective damage taken is reduced by 25%.
- The first super-effective damaging hit received during that switch-in raises:
  - Defense by 1 stage if the hit was physical, or
  - Sp. Def by 1 stage if the hit was special.
- The defensive stat reaction may trigger only once per switch-in.
- Typing never changes.

Implementation notes:
- Reuse the existing super-effective/final-damage lane used by Prism Armor.
- Add per-battler veil turn state plus one per-switch activation flag.
- Reset both on switch-in.

### Lockdown Protocol
Formerly: Stop \\PN

- On switch-in, marks one opposing battler for 3 turns.
- Singles: the only opposing battler is marked.
- Doubles: mark the opposing slot directly across from the holder.
- While marked:
  - the target's damaging moves deal 10% less damage;
  - the target cannot select the same status move twice consecutively.
- Switching the marked Pokémon out ends Lockdown immediately.
- Only one target may be marked by a given holder at once.
- No ability, type, or move deletion occurs.

Implementation notes:
- Reuse Torment-style move-choice validation only for repeated status moves.
- Apply the 0.9 outgoing-damage modifier in the normal attacker damage path.
- Track target battler/party-slot identity and remaining turns to avoid state leaking across switches.

### Storm Sequence
Formerly: Storm-9

- On switch-in, player chooses Rain, Sun, or Sandstorm.
- Chosen weather lasts 4 turns.
- Weather-specific holder bonus:
  - Rain: passive HP recovery each turn.
  - Sun: holder's Fire- and Grass-type moves receive a modest power boost.
  - Sandstorm: holder is immune to sand chip and gains +1 Defense when the weather is selected.
- No random weather changes or automatic cycling.

Implementation notes:
- Build one reusable switch-in choice selector and share it with Field Commissioner.
- Use Mercury's existing weather state rather than a new weather subsystem.

### Field Commissioner
Formerly: Commissioner

On switch-in, choose one command:
- **Advance**: +1 Speed.
- **Fortify**: +1 Defense.
- **Disrupt**: target opponent is Tormented for 2 turns.

No random outcomes and no forced switching.

Implementation notes:
- Reuse the same switch-in choice selector built for Storm Sequence.
- Advance/Fortify reuse normal stat-stage scripts.
- Disrupt reuses Torment state with a bounded two-turn duration.

### Controlled Fury
Formerly: Berserk Fury

- First time the holder falls to 50% HP or less in a battle:
  - +1 Attack;
  - +1 Speed;
  - enters Fury state for 3 turns.
- During Fury, damaging moves deal 10% more damage.
- Direct attacks used during Fury inflict recoil equal to 10% of the damage dealt.
- Player always retains move choice.
- Triggers once per battle.

### Eternal Life
Complete redesign of the original delayed-revival concept.

- First time the holder falls to 50% HP or less:
  - restores 25% max HP;
  - cures any major status condition;
  - removes all negative stat stages.
- Triggers once per battle.
- Does not revive a fainted Pokémon.

### Hollow Shell
- If the holder is KO'd by a direct damaging move, the attacker loses 25% of its maximum HP.
- The retaliation cannot reduce the attacker below 1 HP.
- Does not trigger from poison, burn, weather, entry hazards, recoil, self-KO, or other indirect damage.
- Revival effects cannot retrigger the faint event.

### Mind Games
Formerly: Mind Game

- On switch-in, seals the opponent's last-used move for 2 turns.
- The sealed move cannot be selected.
- Does nothing if the target has not yet used a move.
- Switching clears the seal.
- Only one move is sealed at a time.

### Adaptive Genome
Formerly: Bioengineering

- The first time the holder takes a super-effective damaging hit during a switch-in, it adapts after damage resolves.
- Physical hit -> **Bulwark Form**, +1 Defense.
- Special hit -> **Vector Form**, +1 Sp. Def.
- Can adapt only once per switch-in.
- No typing rewrite.
- Until dedicated form artwork exists, the form may be represented as battle state + message rather than a species-form asset.

### Protean Maxima
Mega Eevee exclusive. Provisionally approved.

- After Mega Eevee successfully uses a damaging move, it transforms into the Eeveelution corresponding to that move's type.
- Transformation occurs after the attack, not before it.
- The next state gains that Eeveelution's:
  - typing;
  - stat profile;
  - designated Mercury ability.
- Status moves do not trigger it.
- Transformation remains visible and persists until another qualifying damaging move is successfully used.
- Keep isolated from the general custom-ability implementation because it requires form/stat/type/ability presentation and state handling.

### The Look
Keep unchanged mechanically.

- While the holder is active, opposing Pokémon cannot use the same move twice consecutively.

## Implementation order

1. Fast existing-hook group:
   - Controlled Fury
   - Hollow Shell
   - Mind Games
   - Eternal Life
   - The Look

2. Stateful group:
   - Prismatic Pelt
   - Lockdown Protocol
   - Adaptive Genome

3. Shared selector group:
   - Storm Sequence
   - Field Commissioner

4. Heavy isolated form mechanic:
   - Protean Maxima

## Branch policy

- MR08 remains the canonical/mainline ability implementation lane.
- This MR09 planning branch exists so custom-ability design can be finalized without contaminating the canonical pass.
- No custom ability should be added to the implemented registry until its battle hook is actually installed and validated.
- Preserve the locked MR07 Summary / EV / Nature / Ability visual design.
