# DS01 Full Sprite Similarity Audit Checkpoint — 2026-09-28

Status: **AUDIT CERTIFIED / ASSETS STILL QUARANTINED**

The staged DS01 sprite library has now been checked as a complete library rather than as isolated downloads. This checkpoint is analysis-only: no sprite has been installed, deleted, replaced, renamed, or recolored.

## Coverage

- Source archive SHA-256: `6f676782799cb206d55a00260a693fccc25f5f59c8fc6b2819aeceaf1beb38f0`
- 11,365 HG-engine-ready images checked
- 2,455 DS-ready male/front design representatives compared
- 11,341 images inside the five nested downloaded source packs checked
- 22,738 image occurrences examined when staged + nested source material are counted together
- 8,956 nested Pokémon-style source images received palette-topology comparison

## Exact duplicate result

There are 22 exact-render duplicate groups among the 2,455 DS-ready male/front designs.

Most are intentional storage/form relationships: Scatterbug/Spewpa pattern labels, Minior meteor shells, Zygarde Power Construct state aliases, Rockruff/Own Tempo, Greninja/Battle Bond, and the shared Toxtricity G-Max design.

The important unrelated failure is the four-way question-mark placeholder collision:

- `darkrai_mega`
- `heatran_mega`
- `slate`
- `zeraora_mega`

Mega Latias and Mega Latios are also held for fidelity review because their staged front renders are exact matches even though high visual similarity is expected canonically.

## Recolor result

Thirteen DS-ready palette-topology duplicate groups were found.

Twelve belong to expected palette-form families (Silvally RKS forms and Alcremie cream/flavor forms). The exception is `lapras_mega`, whose artwork is the Lapras G-Max design with a palette change. It is blocked as distinct Mega art.

## Custom Mega versus G-Max result

Every staged custom Mega with a G-Max counterpart was compared: 46 pair comparisons.

Twenty-seven custom Mega targets crossed the strong similarity threshold and were visually reviewed. They are quarantined because they reuse, recolor, or too closely mirror the corresponding G-Max pose/silhouette/concept:

`blastoise_mega_x`, `butterfree_mega`, `centiskorch_mega`, `charizard_mega_z`, `cinderace_mega`, `coalossal_mega`, `copperajah_mega`, `corviknight_mega`, `drednaw_mega`, `garbodor_mega`, `gengar_mega_x`, `grimmsnarl_mega`, `hatterene_mega`, `inteleon_mega`, `kingler_mega`, `lapras_mega`, `machamp_mega`, `melmetal_mega`, `meowth_partner_mega`, `orbeetle_mega`, `pikachu_partner_mega`, `rillaboom_mega`, `sandaconda_mega`, `snorlax_mega`, `toxtricity_mega`, `urshifu_mega`, and `urshifu_rapid_strike_style_mega`.

## Cross-species near-copy result

A conservative perceptual + silhouette scan across all 2,455 front designs found no additional unrelated near-copy family beyond the four-way placeholder collision.

Finizen/Palafin-Zero is an expected canonical similarity. Mega Latias/Mega Latios remains a fidelity review item rather than an unrelated-copy finding.

## Raw downloaded source packs

The nested source material was also checked rather than ignored.

The only cross-species exact Pokémon family in the reusable raw packs is Appletun/Flapple G-Max, which intentionally share one canonical Gigantamax design. Cross-root palette matches were explainable by Mega Latias/Latios, Appletun/Flapple G-Max, and normal/shiny follower naming in the Earthretha pack. No second unrelated placeholder family was found.

## Existing replacement leads

Three broken placeholder entries already have clearly distinct same-concept DS-style candidates in the staged library:

- `darkrai_mega` → `darkrai-mega`
- `heatran_mega` → `heatran-mega`
- `zeraora_mega` → `zeraora-mega`

Several G-Max-derived custom Megas also have distinct alternate custom art already staged, including `lapras_mega_x`, `machamp_mega_redux`, `kingler_redux_mega`, the Toxtricity Redux Megas, and several CPF alternate-form candidates.

No replacement is authorized by this checkpoint. The detailed mapping is in `data/ds01_sprite_replacement_candidates.json`.

## Certification

The permanent certification gate validates the archive identity, coverage totals, the 27 strong G-Max-derived quarantine targets, the four-way placeholder collision, and the three recovered same-concept candidates.

Current certification result: **PASS, 0 errors**.
