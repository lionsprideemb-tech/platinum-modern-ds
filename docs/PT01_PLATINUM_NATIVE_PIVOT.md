# PT01 — Platinum-Native Architecture Pivot

**Decision date:** 2026-09-22  
**Status:** ACTIVE

## Why we pivoted

The HG-Engine experiment proved that Platinum map/resources could be converted and compiled into an HGSS-derived runtime, but runtime behavior still depended heavily on HGSS assumptions. The DS04 proof build compiled successfully yet did not reliably enter/render the intended imported Platinum room.

Continuing that route would require repeated world-engine compatibility work before normal Sinnoh development could begin.

## New rule

**Do not rebuild Sinnoh inside another engine. Upgrade Platinum in place.**

Platinum already provides the exact world systems this project cares most about:

- Sinnoh map geometry
- Twinleaf and every native interior
- scripts and progression
- warps
- camera behavior
- map rendering
- music
- story sequencing
- save integration

Those remain native unless a specific Mercury feature deliberately changes them.

## What we keep from the HG-Engine experiment

Nothing is deleted.

Useful prior work remains available as reference:

- modern Pokémon/mechanics research
- #1025 roster planning
- asset/sprite collections
- Elite Redux ability/move donor research
- CI/checkpoint practices
- HG-Engine implementation examples
- DS04 compatibility findings

## PT01 acceptance gates

PT01 is complete only when:

1. GitHub checks out the pinned `pret/pokeplatinum` revision.
2. The upstream-compatible toolchain installs reproducibly.
3. `make configure` succeeds.
4. `make check` succeeds.
5. The workflow records the pinned commit and build fingerprint.
6. No commercial ROM is committed or uploaded as a persistent project artifact.

After PT01, PT02 must prove we can change native Platinum source and see that exact change at runtime before any large-scale modernization begins.

## Anti-repeat rule

We will not spend multiple phases fighting a foundation that cannot visibly demonstrate project-owned changes. Every major systems phase must produce a concrete build/runtime proof before the next large phase starts.
