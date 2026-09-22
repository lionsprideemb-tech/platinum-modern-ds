# DS02 Pokédex Audit Tooling

This branch contains read-only tooling for auditing HG-Engine's canonical National Dex coverage.

The audit derives the canonical #001–1025 order from HG-Engine's own `sPokedexSort_NationalNum` table and checks each species across major data surfaces.

It does **not** change HG-Engine.

## Initial coverage surfaces

- master species data
- base experience
- Hidden Ability table entry
- icon palette
- learnset
- battle graphics mapping
- follower properties
- evolution entry (informational only)

The first seven surfaces form the initial `minimum_complete` coverage signal. This is intentionally not treated as proof that special mechanics such as form changes, signature abilities, or unusual evolution conditions are fully functional.

## Usage

```bash
python3 tools/audit_hg_pokedex.py --hg-engine /path/to/hg-engine
```

Outputs:

- `audits/pokedex_1025.csv`
- `audits/pokedex_1025_summary.json`

A later DS02 behavior audit will separately track mechanics/forms that cannot be certified by static file presence.
