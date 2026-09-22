# Platinum Overlay

This directory contains **project-owned modifications applied directly to the pinned native `pret/pokeplatinum` source tree** during CI.

Directory structure should mirror upstream paths.

Examples:

- `include/...`
- `src/...`
- `res/...`

The CI workflow rsyncs this directory over the pinned Platinum checkout before building.

Do not place commercial ROM files here.
