# DS01 Runbook

## Purpose

DS01 establishes a reproducible Nintendo DS development baseline for Platinum Modern DS.

It must prove that a clean GitHub runner can:

1. Check out this project.
2. Read exact upstream revisions from `upstream/LOCK.json`.
3. Reconstruct Pokémon HeartGold from the public `pret/pokeheartgold` source project.
4. Use the reconstructed HeartGold ROM only as an ephemeral build input.
5. Check out the pinned HG-Engine revision.
6. Apply files from `engine-overlay/`.
7. Build HG-Engine.
8. Run HG-Engine's automated tests.
9. Record the resulting build SHA-256 and byte size.

No commercial ROM image is committed to this repository.

## Source of truth

Pinned revisions are stored in:

`upstream/LOCK.json`

Project-specific HG-Engine changes belong in:

`engine-overlay/`

The CI definition is:

`.github/workflows/ds01-build.yml`

## Recovery

If a future change breaks the project:

1. Inspect the most recent successful DS01 workflow run.
2. Compare `upstream/LOCK.json` against the successful checkpoint.
3. Compare `engine-overlay/` against the successful checkpoint.
4. Revert only the offending project commit rather than replacing the source tree with an archive.

## Run history

### Run #1
Result: FAILED during pinned pokeheartgold checkout.

Cause:
The workflow wrote revision values to GitHub step outputs, but the later checkout received an empty value and executed an empty `git checkout`.

Resolution:
Removed the fragile intermediate output and changed checkout commands to read the pinned commit directly from `upstream/LOCK.json`.

Fix commit:
`8ff19397f6099110643a421c96a3799fb6d73eb4`

### Run #2
Status at creation of this runbook: active.

This run is the first attempt using direct lock-file revision reads.

## Certification

Do not mark DS01 complete simply because `make` creates a ROM.

Certification requires every item in `docs/DS01_ACCEPTANCE.md` to pass.
