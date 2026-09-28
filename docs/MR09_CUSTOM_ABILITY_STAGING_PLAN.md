# MR09 Custom Ability Staging Plan

Status: STAGING ONLY — NO CUSTOM ABILITY MECHANICS MAY BE INSTALLED YET
Branch: feature/mr09-custom-ability-staging
Date: 2026-09-28

## Starting point

MR08 is complete and certified for all 187 official Gen 5–9 Ability mechanics.
MR09 begins from that sealed canonical baseline.

The custom/non-canon library is still being compiled and audited separately.
This branch therefore prepares the intake and validation layer only. It must not
change battle mechanics, species assignments, Ability IDs, Summary visuals, or
the locked MR07 editor UI until an entry is explicitly finalized.

## Intake rules

Every candidate custom Ability must arrive with:

- symbolic Ability name;
- source project / source URL or Mercury-authored provenance;
- exact effect text;
- trigger timing;
- restrictions / exclusions;
- known users, if any;
- mechanic family;
- duplicate / near-duplicate group;
- implementation class:
  - existing_hook
  - light_extension
  - new_engine_system
- approval state:
  - locked
  - provisional
  - redesign
  - verify
  - rejected

## Hard gate

An Ability may become implementation-ready only when:

1. approval_state is exactly "locked";
2. exact_effect is non-empty;
3. trigger is non-empty;
4. mechanic_family is non-empty;
5. implementation_class is assigned;
6. duplicate resolution is complete;
7. it has no unresolved redesign or verification flag.

No numeric Mercury Ability ID is assigned during staging. IDs are allocated only
when an implementation batch is approved, and symbolic names remain the merge
key.

## Canonical isolation

MR09 must not modify the certified MR08 canonical range or ownership. Official
Gen 5–9 mechanics remain frozen at 187/187.

## UI lock

The MR07 Summary / EV / Nature / Primary Ability editor visuals remain locked.
Custom Ability staging is data-only until a later explicitly approved runtime
integration pass.
