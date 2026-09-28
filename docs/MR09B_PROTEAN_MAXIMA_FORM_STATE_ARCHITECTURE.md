# MR09B Protean Maxima Form-State Architecture

Status: DESIGN LOCK / IMPLEMENTATION-READY  
Branch: `planning/mr09-custom-ability-redesigns`  
Date: 2026-09-28

## Scope

Protean Maxima is a species-specific mechanic for Mercury's Mega Eevee
(`SPECIES_EEVEE_PARTNER_MEGA`). It must not become a generally distributable
Ability.

Mercury intentionally changes the source timing. The source concept changes
Mega Eevee from the selected move before actions resolve; Mercury changes form
only **after a successful damaging move has finished resolving** so the next
battle state is visible and plan-able.

## Eligibility

Protean Maxima has eight eligible result types, matching the standard Eeveelutions:

- Water -> Vaporeon
- Electric -> Jolteon
- Fire -> Flareon
- Psychic -> Espeon
- Dark -> Umbreon
- Grass -> Leafeon
- Ice -> Glaceon
- Fairy -> Sylveon

Damaging moves of any other type do not change the current Protean Maxima form.
Status moves never trigger the mechanic.

This mapping uses the standard Eeveelution species entries, not Mercury's Delta,
Platinum Redux, or other alternate Eeveelution variants.

## Trigger timing

A Protean Maxima transformation is checked once after the user's entire damaging
move resolves.

Qualifying requirements:

- user is the real Mega Eevee holder, not a transformed copy;
- Mega Eevee is still active and not fainted;
- the move is damaging;
- the move successfully resolves;
- the move has one of the eight eligible Eeveelution types.

Do not trigger on:

- status moves;
- moves that fail before execution;
- fully protected/blocked moves that never successfully resolve;
- self-KO where Mega Eevee is no longer active after resolution;
- Struggle or another unsupported/non-Eeveelution result type;
- a transformed Pokémon merely copying Mega Eevee.

Multi-hit moves transform only once, after the complete move has resolved.
Spread moves transform only once, not once per target.

Use the **effective move type at execution** after ordinary move-type conversion,
not merely the move's static database type. The form the opponent sees therefore
matches the type that actually resolved.

## Battle-state model

Protean Maxima needs a controller state separate from the holder's currently
displayed/effective form Ability.

Suggested state:

- `mercuryProteanMaximaActive[battler]`
- `mercuryProteanMaximaForm[battler]`
- `mercuryProteanMaximaPendingForm[battler]`
- party-slot identity guard for switch/reload safety

Suggested form enum:

- BASE
- VAPOREON
- JOLTEON
- FLAREON
- ESPEON
- UMBREON
- LEAFEON
- GLACEON
- SYLVEON

The controller is enabled only when the battler is the genuine Mega Eevee
species with Protean Maxima. A copied species/Transform state does not gain the
controller.

## Form application

Each result form changes only battle-facing properties:

- type;
- Attack;
- Defense;
- Sp. Atk;
- Sp. Def;
- Speed;
- designated Protean Maxima form Ability;
- battle sprite/icon presentation where the battle engine supports it.

Current HP and max HP remain Mega Eevee's own values.

This is deliberate. Recalculating max HP every time Mega Eevee changes form
would create healing/damage exploits and unnecessary party-data mutation.
Stat stages also remain unchanged across transformations.

The five non-HP stat values should be read from the current standard Mercury
Eeveelution species data rather than duplicated as hard-coded numbers inside
Protean Maxima. This keeps the mechanic synchronized if an Eeveelution is later
rebalanced.

## Form Ability layer

Protean Maxima's controller cannot rely on `Battler_Ability()` continuing to
return Protean Maxima after a form change, because the transformed state is
supposed to gain the matched Eeveelution's designated Ability.

Therefore:

- the hidden Protean Maxima controller remains species/form-state driven;
- the normal effective-Ability resolver returns the current Eeveelution form
  Ability while transformed;
- the post-move Protean Maxima trigger checks the hidden controller, not the
  current visible/effective Ability.

Each Eeveelution receives one explicit Protean Maxima form Ability entry in a
small data table. Do not dynamically copy whichever Primary/Innate combination
a normal party Eeveelution happens to have.

The exact eight form Ability assignments remain a balance/data decision and are
not hard-coded by MR09B architecture.

Changing Protean Maxima form does **not** count as switching in. A newly gained
Ability does not receive a switch-in trigger merely because the form changed.
Continuous, on-hit, move-power, immunity, and later end-turn behavior becomes
active normally from the completed transformation onward.

## Visual presentation

No new Mega-Eeveelution artwork is required for the first implementation.

Battle presentation may reuse the existing standard battle sprite for the
matched Eeveelution while keeping the underlying party member as Mega Eevee.

Recommended sequence:

1. Mega Eevee's move fully resolves.
2. Standard Ability activation message announces Protean Maxima.
3. Short form-change flash/transition.
4. Battle sprite changes to the matched standard Eeveelution.
5. Message identifies the new form.
6. The next battler action begins.

Party/Summary data outside the active battle remains Mega Eevee. The form is a
battle state, not a permanent species mutation.

If sprite swapping is not ready when mechanics are first installed, mechanics
may ship behind a development gate using the Mega Eevee sprite plus explicit
form text. Player-facing release certification still requires clear visible
form feedback.

## Switching and reset behavior

When Mega Eevee leaves the field:

- clear its current Protean Maxima battle form;
- retain normal Mega-Evolution status for the party member;
- on its next switch-in it begins in BASE Mega Eevee state.

Fainting also clears the active form state.

This makes every field appearance begin from one predictable baseline and
prevents a hidden off-field type/Ability from carrying between appearances.

## Suppression and Ability-changing interactions

Protean Maxima is species-specific and should use the same protected-copy model
as other identity/form Abilities.

- Trace cannot copy it.
- Role Play cannot copy it.
- Skill Swap cannot exchange it.
- Receiver/Power of Alchemy cannot inherit it.
- Worry Seed/Gastro Acid and similar permanent Ability replacement should be
  blocked against the Protean Maxima controller.

Neutralizing Gas may suppress Protean Maxima activation:

- while suppressed, Mega Eevee keeps its already-visible current form;
- no new Protean Maxima transformation occurs;
- the currently mapped form Ability is also suppressed through normal effective-
  Ability handling;
- when suppression ends, later qualifying moves can transform Mega Eevee again.

Suppression never retroactively changes the result of a move that has already
finished resolving.

## Transform interaction

If Mega Eevee itself is under the normal Transform volatile state, Protean
Maxima does not activate until that state is gone.

A different Pokémon transformed into Mega Eevee does not gain Protean Maxima's
hidden controller even if its copied visible data resembles Mega Eevee.

## Same-form use

If the qualifying move maps to the form Mega Eevee already has:

- do not replay the transformation animation;
- do not reset stats/stages;
- do not retrigger any form Ability entry behavior;
- simply remain in the existing form.

## Battle ordering

Transformation occurs after the user's complete move but before the next
battler action.

This means a faster Mega Eevee can attack as one form, visibly transform, then
receive a later opponent's attack using the new form's type/stats/Ability in the
same turn. That behavior is intentional and is the main fairness improvement
over transforming from a hidden move choice before the action.

KO, recoil, drain, secondary effects, contact reactions, and other consequences
of the move finish before Protean Maxima commits the new form.

## Data table

MR09B should use a single table similar to:

`effectiveMoveType -> targetSpecies -> formAbility -> formEnum`

The target species points to the standard Mercury entries:

- `SPECIES_VAPOREON`
- `SPECIES_JOLTEON`
- `SPECIES_FLAREON`
- `SPECIES_ESPEON`
- `SPECIES_UMBREON`
- `SPECIES_LEAFEON`
- `SPECIES_GLACEON`
- `SPECIES_SYLVEON`

This keeps all eight mappings auditable and avoids a large conditional spread
across the battle engine.

## Validation gates

MR09B is not complete until tests cover:

- Mega Eevee begins each switch-in in BASE form;
- each of the eight eligible damaging move types maps to the correct Eeveelution;
- unsupported damaging types do not transform;
- status moves do not transform;
- failed/protected moves do not transform;
- multi-hit moves transform exactly once after the complete move;
- effective converted move type controls the result;
- current/max HP are unchanged by transformation;
- stat stages are preserved;
- five non-HP battle stats change to the target form profile;
- current effective type changes correctly;
- current form Ability changes correctly;
- switch-in effects are not spuriously fired by transformation;
- same-form use does not replay form entry;
- switch-out resets to BASE for the next appearance;
- Neutralizing Gas suppression prevents new transformations without corrupting state;
- Transform copies cannot activate the controller;
- copy/swap/replacement interactions cannot steal Protean Maxima;
- battle sprite/text feedback matches the visible form;
- locked MR07 Summary/editor visuals remain untouched.

## Implementation units

MR09B-1: Protean Maxima form enum, mapping table, controller state, reset rules.  
MR09B-2: post-move qualifying trigger + effective-type capture.  
MR09B-3: type/stat/effective-Ability remap with HP/stage preservation.  
MR09B-4: battle sprite/form feedback.  
MR09B-5: copy/suppression/Transform restrictions + deterministic validation harness.
