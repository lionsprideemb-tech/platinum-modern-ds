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
Run ID: `36145347797`  
Conclusion: **success**

Proof artifact: `mercury-move-preflight-proof`  
Artifact ID: `10867949539`  
Artifact digest:
`sha256:c37c479a5da7659c61f79f3c89086043b01dd65332a5cd4cc33af840caa36ecd`

This main-line gate successfully validated the complete CM01-CM08 move stack at commit `a43cf7392799bad17c4c5364c93e39a033dfd9e4`.

## Policy going forward

New community-move phases must pass this preflight before the full ROM build and
emulator runtime proof are allowed to be treated as certification.

This does not make coding mistakes impossible. It moves the cheap, predictable
failure modes ahead of the expensive build so they can be corrected quickly.

**MERCURY MOVE PREFLIGHT: PASS**
