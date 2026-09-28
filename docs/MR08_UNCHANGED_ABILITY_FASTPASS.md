# MR08 — Unchanged Canonical Ability Fast Pass

Date: 2026-09-27
Branch: `feature/mr08-canonical-abilities`

## Rule

This pass is for official Pokémon Abilities whose core battle mechanic remains
canonical in the pinned Elite Redux source. Mercury may reuse DS-native code
patterns from hg-engine or another public DS project, but the resulting mechanic
must remain the official/mainline mechanic.

An Ability with an Elite Redux buff, rewrite, expanded move list, altered
multiplier, or ambiguous/conflicting Redux documentation is **not** eligible for
this fast pass. Those Abilities go to the separate modified-Ability review.

## MR08B — first large unchanged-mechanics family

The following 12 Abilities are moved together as one implementation family:

- Heavy Metal
- Light Metal
- Multiscale
- Sand Force
- Fur Coat
- Gale Wings
- Tough Claws
- Water Bubble
- Fluffy
- Neuroforce
- Ice Scales
- Power Spot

Shared implementation hooks cover effective weight, move power,
physical/special/final damage modifiers, weather chip immunity, move priority,
super-effective damage, ally damage support, and burn immunity.

## MR08C — interaction family

MR08C adds 10 more unchanged canonical mechanics:

- Healer
- Telepathy
- Regenerator
- Moxie
- Justified
- Prankster
- Gooey
- Berserk
- Gorilla Tactics
- Screen Cleaner

This raises the implemented modern-Ability mechanics total to **25**. The batch
uses Platinum-native switch-out, end-turn, priority, immunity, on-hit, KO,
choice-lock, and switch-in screen-clearing hooks.

## MR08D — shared battle-hook family

MR08D adds another 10 unchanged canonical mechanics:

- Iron Barbs
- Wonder Skin
- Analytic
- Bulletproof
- Queenly Majesty
- Battery
- Dazzling
- Tangling Hair
- Shadow Shield
- Prism Armor

This raises the implemented modern-Ability mechanics total to **35**. The batch
reuses Platinum's existing Rough Skin/Gooey-style on-hit lanes, accuracy
calculation, current-turn state, pre-damage immunity lane, ally-power helper,
full-HP damage reduction, and super-effective damage reduction.

Bulletproof uses the pinned hg-engine projectile list through Gen 9, including
modern entries such as Pollen Puff, Pyro Ball, and Syrup Bomb. Queenly Majesty
and Dazzling use the same canonical team-wide priority protection behavior.

The implementation source of truth for DS hooks is the pinned hg-engine commit.
Elite Redux is used as the comparison source so Redux-specific rebalances are
not silently imported.

## Next unchanged candidates

These remain in the fast-pass lane but need broader or stateful hooks before
entering the implemented registry:

- Magic Bounce
- Aroma Veil
- Flower Veil
- Cheek Pouch
- Competitive
- Sweet Veil
- Symbiosis
- Cotton Down
- Mirror Armor
- Sand Spit
- Ripen
- Perish Body
- Pastel Veil

These are not marked implemented merely because their names/descriptions exist.
Each is promoted only when its complete battle hook is installed and certified.

## Modified / review lane

Examples that must not be swept into the unchanged fast pass include:

- Big Pecks — Elite Redux rewrites it into a contact-move damage boost instead
  of the canonical Defense-drop protection.
- Strong Jaw — Elite Redux expands the affected move list.
- Friend Guard — Elite Redux uses a 50% partner reduction rather than the
  canonical 25% reduction.
- Sand Rush / Slush Rush — the pinned Redux source uses 1.5× Speed rather than
  the canonical 2× multiplier.
- Long Reach, Liquid Voice, Triage, Water Compaction, Merciless, Steelworker,
  and similar Abilities with explicit Redux-added damage/effect changes remain
  review-only until Mercury chooses the final behavior.
- Any Ability whose Redux constants/comments and player-facing description
  disagree about its multiplier or effect is held for review instead of guessed.

The already-installed canonical Big Pecks hook from MR08A remains technically
valid for the official mechanic, but its final Mercury behavior is provisional
until the modified-Ability review decides whether Mercury keeps canonical Big
Pecks or adopts the Redux rewrite.

## Batch policy

Fast-pass work should normally move in double-digit mechanic families rather
than tiny 2-3 Ability commits. Stateful/form-changing mechanics remain eligible
for smaller exception batches when required for correctness.

The locked MR07 Summary / EV / Nature / Ability visual design remains untouched.
