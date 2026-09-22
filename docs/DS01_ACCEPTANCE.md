# DS01 Acceptance Criteria

DS01 is complete only when all of the following are true:

- [ ] `pokeheartgold` is pinned to an exact commit.
- [ ] HG-Engine is pinned to an exact commit.
- [ ] GitHub Actions reconstructs the HeartGold base from source.
- [ ] No clean commercial ROM is stored in this repository.
- [ ] HG-Engine compiles successfully against the generated base.
- [ ] HG-Engine automated tests pass.
- [ ] The workflow records a SHA-256 fingerprint and byte size for the resulting build.
- [ ] The exact upstream revisions used are recorded in `upstream/LOCK.json`.
- [ ] A known-good DS01 checkpoint commit/tag is recorded.
- [ ] The next milestone can begin without requiring a local source archive.

## Non-goals

DS01 does **not** modify Sinnoh, Pokémon data, encounters, UI, or game balance.

Its only purpose is to establish a reproducible, recoverable, known-good DS development foundation.
