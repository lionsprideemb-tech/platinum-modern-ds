# DS01 Certification Record

## Milestone

DS01 — Reproducible HG-Engine Foundation

**Status: CERTIFIED — 2026-09-22**

## Certified project commit

- Tested project commit: `8ff19397f6099110643a421c96a3799fb6d73eb4`
- Permanent checkpoint branch: `checkpoint/ds01-certified`
- Project workflow run: `35755920648` (DS01 Engine Build run #2)

## Upstream revisions

- HG-Engine: `5157c501dc0e6f88ef1654ab121352a5cc9ed7de`
- pokeheartgold: `9d8b7591f09b65804da2fb2dfd56f320633e0d36`
- pokeplatinum reference: `c248fb3f8cc9934ded800e489567c5c0eeee92eb`
- Elite Redux reference: `5f730d8835f3c96d15195f2ac9f126981c3a331b`

## Repository safety

Repository Guard: PASS

Verified:
- no tracked `.nds`, `.sav`, ROM archives, or split archive parts
- pinned upstream revisions are exact 40-character commit hashes
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
- HG-Engine automated test command: PASS
- generated build fingerprint step: PASS

The workflow records the generated `test.nds` SHA-256 and byte size in its GitHub Actions step summary. The ROM itself is not uploaded or committed.

## Regression test result

- tests passed: **401**
- unexpected test failures: **0**
- upstream-known failing tests: **8**
- skipped tests: **3**

The known-failing/skipped cases are tracked separately and are not regressions introduced by Platinum Modern DS.

## Independent upstream evidence

The exact pinned HG-Engine commit also has a successful upstream full CI run (upstream run #1294 / GitHub Actions run `35654224823`).

## Certification decision

DS01 is complete.

The project now has a reproducible, recoverable Nintendo DS foundation that can be rebuilt from pinned public source inputs without storing a clean commercial ROM.

Future engine changes must preserve this checkpoint and should be developed on feature branches before promotion to `main`.
