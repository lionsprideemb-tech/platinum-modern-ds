# MR07 Summary / Skills UI — VISUAL LOCK

**Status:** APPROVED / LOCKED  
**Approved:** 2026-09-27  
**Branch:** `feature/mr07-summary-skills`

The current Pokémon Summary / Skills visual treatment is the approved Mercury Redux DS design baseline.

## Locked screens

- EV Training editor
- Primary Ability editor
- Nature editor
- Existing top-screen Pokémon Skills / Summary layout

## Locked visual language

Preserve the current Platinum-style presentation:

- warm cream / tan lower-screen panels
- dark-blue section title bars
- blue dividers and blue selection markers
- native-style menu arrows and Platinum window framing
- alternating cream rows where currently used
- separate pale-gold information / description panel in the Ability editor
- current typography, spacing, row heights, and information hierarchy
- current top-screen stat / Nature / Ability / Innate layout

The current blue treatment replaces the earlier purple-looking text/highlight treatment and is the approved version.

## Screen-specific lock notes

### EV Training
Keep the current six-stat list, alternating row treatment, blue cursor, EV-per-stat display, TOTAL readout, and dedicated control-help panel.

### Primary Ability
Keep the current cream ability-choice area and the separate pale-gold description panel beneath it. Do not collapse this back into a single white field.

### Nature
Keep the current list-based selector with the Nature name and stat-effect notation, using the approved Platinum palette and selection treatment.

## Change-control rule

Do **not** redesign the surrounding Summary / editor UI during normal feature work. New functionality must be fitted into this approved visual system.

A visual redesign should happen only when the project owner explicitly requests one.

## Next implementation phase

Build the remaining functionality into the locked UI, beginning with the Innate Ability rows / editor behavior and associated persistence/runtime logic.

This file is the project marker that the MR07 Summary / Skills visual pass is complete and approved.
