# Platinum Overlay

This directory is the Mercury Redux modification layer for the native
`pret/pokeplatinum` runtime.

## Rule

Files placed here must mirror paths inside the pinned pokeplatinum checkout.
The PT01 workflow copies this directory over the clean pinned source before
building.

HG-Engine/HGSS code is not copied here wholesale. It may be used as a donor or
reference, but every imported system must be adapted to pokeplatinum and tested
inside the Platinum runtime before it is considered integrated.

The first objective is a clean, reproducible, fully playable Platinum baseline.
Modern systems are added incrementally only after that baseline is certified.
