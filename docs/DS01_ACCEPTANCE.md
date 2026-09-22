# DS01 Acceptance Criteria

DS01 is complete only when all of the following are true:

- [x] `pokeheartgold` is pinned to an exact commit.
- [x] HG-Engine is pinned to an exact commit.
- [x] GitHub Actions reconstructs the HeartGold base from source.
- [x] No clean commercial ROM is stored in this repository.
- [x] HG-Engine compiles successfully against the generated base.
- [x] HG-Engine automated tests pass.
- [x] The workflow records a SHA-256 fingerprint and byte size for the resulting build.
- [x] The exact upstream revisions used are recorded in `upstream/LOCK.json`.
- [x] A known-good DS01 checkpoint commit/tag is recorded.
- [x] The next milestone can begin without requiring a local source archive.

## Non-goals

DS01 does **not** modify Sinnoh, Pokémon data, encounters, UI, or game balance.

Its only purpose is to establish a reproducible, recoverable, known-good DS development foundation.
