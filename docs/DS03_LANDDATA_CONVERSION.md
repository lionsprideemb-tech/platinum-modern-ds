# Platinum → HGSS Land-Data Conversion

Current DSPRE source documents a shared Gen IV map member structure for DPPt/HGSS:

- four u32 section lengths
- movement permissions
- building/map-prop placements
- untextured NSBMD map model
- BDHC terrain/height data

HGSS adds a BGS (Background Sound / sound-plate) block immediately after the 16-byte size header.

For a normal imported Platinum map, a blank HGSS BGS block is:

`34 12 00 00`

This shifts movement permissions from Platinum offset `0x10` to HGSS offset `0x14` while leaving the four section lengths and all section payloads unchanged.

The converter in `tools/convert_platinum_landdata.py` validates:
- permissions section is 0x800 bytes,
- total size agrees with the four section lengths,
- NSBMD section begins with `BMD0`,
- converted BGS signature/length are valid,
- converted NSBMD remains correctly aligned.

This means the Twinleaf `MAP_000`, `MAP_180`, `MAP_184`, `MAP_185`, `MAP_186`, and `MAP_187` visual map members can be converted mechanically rather than recreated.
