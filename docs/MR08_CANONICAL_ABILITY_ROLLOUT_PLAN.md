# MR08 Canonical Ability Rollout Plan

Status: LOCKED PROJECT DIRECTION
Branch: feature/mr08-canonical-abilities
Date: 2026-09-27

## Scope

MR08 first completes the official vanilla/canonical Pokemon Ability mechanics
already represented by Mercury's canonical namespace through Generation 9.

During this phase:
- use the official canonical effect of each Ability;
- do not substitute Elite Redux custom behavior for an official Ability;
- do not rebalance, rewrite, or "improve" canonical Ability effects;
- hg-engine and other public repositories may be used as implementation donors
  or references, but the resulting behavior must match the official mechanic;
- Elite Redux custom Abilities are a separate later phase after the canonical
  Ability pass is substantially complete.

## Batch size

Do not port modern Abilities only a few at a time unless a mechanic is unusually
stateful or risky.

Target batch sizes:
- 20-40 Abilities for straightforward/shared-hook mechanics;
- 12-24 Abilities for moderate mechanics with several battle hooks;
- smaller exception batches only for genuinely stateful mechanics such as form
  changes, persistent battle state, move transformation, or unusual turn-order
  behavior.

Abilities should be grouped by shared engine hook rather than arbitrary ID
ranges whenever possible. Examples:
- stat-stage modification / stat-drop prevention;
- move-power and type boosts;
- weather / terrain speed and stat modifiers;
- immunities / absorption;
- contact and on-hit triggers;
- entry effects;
- end-of-turn effects;
- priority / accuracy / critical-hit modifications;
- switching / trapping;
- item interactions;
- form/state-changing mechanics.

## Certification rule

An Ability is added to Mercury's implemented-Ability registry only after its
actual battle hook is installed. Species import may then assign it normally.
Unported modern Abilities continue to fall back safely instead of pretending to
work.

Every batch must preserve:
- Mercury's expanded Ability-ID width;
- normal save compatibility strategy;
- current species importer safety;
- the locked MR07 Summary / EV / Nature / Ability visual design.

## Custom Ability phase

After the vanilla Gen 1-9 mechanics pass, begin the custom Ability library.
Elite Redux is the primary custom-Ability source, with DS-native public projects
used when they provide useful implementation patterns.

Custom Abilities are audited for:
- duplicate mechanics;
- suitability as Primary Ability and/or Innate;
- interaction with Mercury's multi-Ability system;
- message/animation needs;
- statefulness and save/battle-state requirements.

The canonical pass and the custom pass remain separate so vanilla Abilities keep
their real mechanics.
