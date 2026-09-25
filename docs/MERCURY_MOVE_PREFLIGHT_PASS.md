# Mercury Move Preflight — PASS

Date: 2026-09-25

## Purpose

The Mercury move pipeline now has a reusable fast gate that runs before an
expensive full ROM compile.

Its job is to catch small deterministic failures early instead of discovering
them several minutes into a complete Platinum build.

## Gates

The preflight now verifies:

- Python importer / installer syntax
- JSON validity
- Community move ID contiguity and collisions
- Community move token collisions
- Locked community ID range
- Canonical Pokémon move types only
- Valid move classes and Platinum targets
- Effect registration, including Mercury custom-effect extensions
- Stable custom effect IDs and declared installers
- Platinum charmap compatibility for every static community move name and
  description
- Installed move registry positions
- Installed move data against source batch metadata
- Animation donor existence and byte-for-byte donor copies

After the metadata checks, the workflow reconstructs the move namespace without
building the whole game, then compiles only the move-sensitive resources:

- move data
- move descriptions
- battle move text
- battle effect scripts
- move scripts
- move animation scripts

The sound-data index is built first because Platinum battle scripts include its
generated constants.

## Proof

GitHub Actions workflow: **Mercury Move Preflight**  
Run ID: `36144865066`  
Conclusion: **success**

Proof artifact: `mercury-move-preflight-proof`  
Artifact ID: `10869008671`  
Artifact digest:
`sha256:7a52dcda9e342d593c019a6a4b7aef7b328b6f06e32811991ecbb5df8edd3d9c`

This gate successfully validated the complete CM01-CM08 move stack.

## Policy going forward

New community-move phases must pass this preflight before the full ROM build and
emulator runtime proof are allowed to be treated as certification.

This does not make coding mistakes impossible. It moves the cheap, predictable
failure modes ahead of the expensive build so they can be corrected quickly.

**MERCURY MOVE PREFLIGHT: PASS**
