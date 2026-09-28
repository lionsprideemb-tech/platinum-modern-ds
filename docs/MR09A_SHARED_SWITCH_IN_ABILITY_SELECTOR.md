# MR09A Shared Switch-In Choice Architecture

Status: DESIGN LOCK / IMPLEMENTATION-READY  
Branch: `planning/mr09-custom-ability-redesigns`  
Date: 2026-09-28

## Purpose

Storm Sequence and Field Commissioner both need the same DS-native battle flow:

1. Ability activates on switch-in.
2. The battle pauses before the next switch-in ability in the queue.
3. The player receives a forced three-option choice on the bottom screen.
4. The choice resolves immediately.
5. Battle processing resumes from the same switch-in queue position.

Do not build two independent menu systems. MR09A defines one reusable selector.

## Player-facing selector

### Visual shell

Use the existing Platinum battle message/window vocabulary rather than the MR07 Summary editor shell.

Top/battle screen:
- normal battle scene remains visible;
- standard ability activation message is shown first;
- no full-screen transition.

Bottom screen:
- temporarily replaces the normal command panel with a compact three-row choice window;
- D-pad Up/Down changes selection;
- A confirms;
- B does not cancel because the ability requires a resolved choice;
- selected row uses the native Platinum cursor/highlight treatment;
- after confirmation the choice window closes and the standard battle bottom screen is restored.

The selector must not alter the locked MR07 Summary / EV / Nature / Ability visuals.

### Generic state

The selector should be ability-agnostic and store only the minimum battle state needed to suspend and resume:

- active flag;
- requesting battler;
- selector kind;
- three option IDs;
- current cursor row;
- optional follow-up target selection requirement;
- resume point / callback result;
- AI-resolved flag.

Suggested logical interface:

`Mercury_BeginAbilityChoice(battler, selectorKind, option0, option1, option2)`

`Mercury_ResolveAbilityChoice(battler, selectorKind, selectedOption)`

The exact C interface may follow the existing battle-controller conventions when implementation begins.

## Switch-in ordering

The selector must preserve Platinum's current switch-in Ability order.

- When an entering battler reaches Storm Sequence or Field Commissioner in the normal switch-in Ability queue, that battler owns the selector.
- The queue pauses only for that one decision.
- After resolution, processing resumes at the next switch-in Ability exactly once.
- A double switch can therefore produce two sequential prompts if two player-controlled holders activate.
- An AI-controlled holder never opens the human UI; its choice is resolved synchronously through an AI choice function.
- No choice may retrigger simply because the queue resumes.

## Storm Sequence provider

Activation message:
`<Pokémon>'s Storm Sequence activated!`

Prompt:
`Choose a weather.`

Options:
1. Rain
2. Sun
3. Sandstorm

Resolution:
- installs the selected normal weather for 4 turns;
- records which Storm Sequence mode belongs to the holder for its weather-specific bonus;
- replaces ordinary temporary weather rather than stacking a second weather layer;
- later weather replacement by another legal weather setter works normally;
- the holder's Storm Sequence bonus is active only while its selected weather is actually the field weather.

Weather-specific bonus values remain data constants so balance can be changed without rebuilding selector logic.

Current approved identities:
- Rain: passive recovery while the selected Rain is active.
- Sun: holder gains an additional Fire/Grass offensive bonus while the selected Sun is active.
- Sandstorm: holder is immune to sand chip and receives +1 Defense when Sandstorm is selected.

### Storm Sequence AI selection

AI choice must be deterministic from visible battle state, never random.

Score the three choices using:
- damaging moves that benefit from the resulting weather;
- holder typing/weather-chip interaction;
- current HP and the Rain sustain value;
- whether replacing the current weather helps or harms the holder;
- known ally synergy in doubles.

Choose the highest score. Resolve ties in fixed order Rain -> Sun -> Sandstorm so identical battle states are reproducible.

The scoring layer may be improved later without touching the selector.

## Field Commissioner provider

Activation message:
`<Pokémon>'s Field Commissioner activated!`

Prompt:
`Choose a command.`

Options:
1. Advance
2. Fortify
3. Disrupt

Resolution:
- Advance: +1 Speed to the holder.
- Fortify: +1 Defense to the holder.
- Disrupt: applies bounded Torment for 2 turns to one opposing battler.

### Disrupt target selection

Singles:
- the only active opponent is selected automatically.

Doubles:
- after Disrupt is chosen, hand off to the existing legal-opponent target cursor;
- only living opposing battlers are legal targets;
- A confirms;
- B returns to the three-command selector rather than canceling the Ability;
- once a target is confirmed, apply the 2-turn Torment and resume the switch-in queue.

This target step is specific to Field Commissioner and is not part of the generic three-option selector itself.

### Field Commissioner AI selection

AI choice is deterministic.

Suggested scoring:
- Advance: prefer when +1 Speed changes an unfavorable speed relation or improves an offensive line.
- Fortify: prefer against a primarily physical active opponent or when physical damage is the largest immediate threat.
- Disrupt: prefer when an opponent has a high-value repeatable move, especially setup/recovery/status or a move the AI strongly expects to be repeated.

For doubles Disrupt targeting, choose the opponent with the highest Disrupt score; use fixed battler-order tie breaking.

## Suppression and copying rules

Both abilities use Mercury's normal effective-Ability layer.

- If the Ability is suppressed when the switch-in trigger would occur, no selector opens.
- Neutralizing Gas and equivalent suppression should therefore naturally prevent activation through the same checks used by MR08.
- A selector already confirmed is not undone if the Ability becomes suppressed later that turn.
- Ability-changing effects must not leave an orphaned open selector; if the requesting battler is no longer valid before confirmation, close the selector and resume the queue safely.

Final copy/swap/Trace restrictions are decided per Ability during the custom distribution pass, not by the generic selector.

## Battle-state safety

The selector state is battle-local only.

Clear it on:
- battle initialization;
- successful resolution;
- requesting battler becoming invalid/fainted before confirmation;
- battle end;
- hard battle-controller reset.

Do not serialize the open selector into the normal save file.

## Validation gates

MR09A implementation is not considered complete until deterministic checks cover:

- player Storm Sequence opens exactly one 3-choice prompt;
- all three weather choices resolve and return control;
- player Field Commissioner opens exactly one 3-choice prompt;
- Advance and Fortify resolve once;
- Disrupt resolves in singles;
- Disrupt hands off to legal target selection in doubles;
- B from the doubles target step returns to command choice;
- AI-controlled holders never open a player prompt;
- simultaneous switch-ins resume in correct Ability order;
- suppression prevents activation;
- invalid requester cleanup cannot softlock;
- no MR07 locked Summary/editor assets are modified.

## Next implementation units

MR09A-1: generic three-option battle selector state + controller pause/resume.  
MR09A-2: Storm Sequence provider + weather-mode state.  
MR09A-3: Field Commissioner provider + Disrupt target handoff.  
MR09A-4: deterministic AI choice functions + validation harness.
