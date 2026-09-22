# DS01 Certification Record

## Milestone

DS01 — Reproducible HG-Engine Foundation

## Upstream revisions

- HG-Engine: `5157c501dc0e6f88ef1654ab121352a5cc9ed7de`
- pokeheartgold: `9d8b7591f09b65804da2fb2dfd56f320633e0d36`
- pokeplatinum reference: `c248fb3f8cc9934ded800e489567c5c0eeee92eb`
- Elite Redux reference: `5f730d8835f3c96d15195f2ac9f126981c3a331b`

## Repository safety

Repository Guard run #1: PASS

Verified:
- no tracked `.nds`, `.sav`, ROM archives, or split archive parts
- all pinned upstream revisions are full 40-character commit hashes
- required DS01 documentation exists

## Engine build evidence

DS01 Engine Build run #2:
- HeartGold source checkout: PASS
- HeartGold toolchain bootstrap: PASS
- HeartGold reconstruction: PASS
- pinned HG-Engine checkout: PASS
- project overlay application: PASS
- generated HeartGold input preparation: PASS
- HG-Engine compile: PASS
- HG-Engine automated tests: RUNNING at last certification update
- generated build fingerprint: PENDING tests

## Independent upstream evidence

HG-Engine upstream build for the exact pinned commit `5157c501dc0e6f88ef1654ab121352a5cc9ed7de` completed successfully in upstream run #1294 (GitHub Actions run 35654224823), including the full automated test suite.

This is supporting evidence only; our project run #2 remains the local certification gate.

## Current status

**PROVISIONAL — NOT YET CERTIFIED**

The engine and source reconstruction compile successfully. DS01 becomes certified only after the automated HG-Engine test suite completes successfully and the build fingerprint step runs.

## Build policy

A successful compile alone is not enough to close DS01.

The full certification gate is defined in `docs/DS01_ACCEPTANCE.md`.
