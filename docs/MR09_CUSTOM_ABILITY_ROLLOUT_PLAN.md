# MR09 Custom Ability Rollout Plan

Status: ACTIVE
Branch: feature/mr09-custom-abilities
Date: 2026-09-28

## Entry condition

MR09 begins only after Mercury's official Gen 5-9 Ability mechanics are complete.
MR08 covers IDs 124..310, 187 modern canonical mechanics total. The MR08 final
certification gate remains separate and must stay green.

## Source library

The research library contains 959 non-canon source records compiled from
Pokémon Exceeded, Elite Redux, Radical Red Showdown, CAP/test sources,
Insurgence, Rejuvenation, Inclement Emerald, and other documented projects.
Duplicate/near-duplicate review is complete. Source records remain preserved;
Mercury does not blindly import every source row as a live Ability.

## First reserved custom namespace

MR09A reserves IDs 311..321 for the 11 Game Health redesign decisions:

| ID | Ability | Source name | Current implementation status |
|---:|---|---|---|
| 311 | Controlled Fury | Berserk Fury | Hold until recoil basis is locked |
| 312 | Eternal Life | Eternal Life | Ready |
| 313 | Hollow Shell | Hollow Shell | Ready |
| 314 | Mind Games | Mind Game | Ready |
| 315 | The Look | The Look | Ready |
| 316 | Prismatic Pelt | Prismatic Fur | Ready |
| 317 | Lockdown Protocol | Stop \PN | Ready; target selector required |
| 318 | Adaptive Genome | Bioengineering | Ready |
| 319 | Storm Sequence | Storm-9 | Ready; choice selector required |
| 320 | Field Commissioner | Commissioner | Ready; choice/target selector required |
| 321 | Protean Maxima | Protean Maxima | Hold until Eeveelution Ability mapping is locked |

Namespace reservation alone never makes an Ability assignable. A custom Ability
is added to Mercury's implemented-Ability registry only in the same gate that
installs and validates its real battle mechanics.

## Locked mechanics ready for implementation

### Eternal Life
Once per battle, the first time the user reaches 50% HP or less, restore 25%
max HP, cure any major status condition, and remove all negative stat stages.

### Hollow Shell
If the user is knocked out by a direct damaging move, the attacker loses 25% of
its max HP. The retaliation cannot reduce the attacker below 1 HP. Indirect,
self-KO, and revival cases do not trigger it.

### Mind Games
On entry, seal one opponent's last-used move for 2 turns. If that opponent has
no previously used move, nothing is sealed. Switching clears the seal.

### The Look
While the user is active, opposing Pokémon cannot use the same move twice in a
row.

### Prismatic Pelt
On entry, gain Prismatic Veil for 3 turns. Super-effective damage is reduced by
25%. The first qualifying hit per switch-in grants +1 Defense for a physical
hit or +1 Sp. Def for a special hit. Typing never changes.

### Lockdown Protocol
On entry, mark one opposing target for 3 turns. The marked target's damaging
moves deal 10% less damage and it cannot use the same status move twice
consecutively. Switching clears the mark. Only one target is marked.

### Adaptive Genome
The first time per switch-in the user is hit super effectively, a physical hit
grants +1 Defense and a special hit grants +1 Sp. Def.

### Storm Sequence
On entry choose Rain, Sun, or Sandstorm for 4 turns. Rain provides the approved
user healing passive, Sun boosts the user's Fire- and Grass-type moves, and
Sandstorm grants sand-chip immunity plus +1 Defense on entry. No random cycling.

### Field Commissioner
On entry, once per switch-in, choose Advance (+1 Speed), Fortify (+1 Defense),
or Disrupt (Torment one opposing target for 2 turns). In doubles, Disrupt uses
the normal opponent-target cursor. AI choice is deterministic.

## Held mechanics

### Controlled Fury
Approved core: first fall below half HP, once per battle, +1 Attack and +1
Speed, then a 3-turn offensive state with +10% damaging-move power and a 10%
recoil drawback on direct attacks. Do not implement until the recoil basis and
turn-expiry convention are locked.

### Protean Maxima
Mega Eevee only. After a successful damaging move, transform into the
Eeveelution matching that move's type. The form uses the corresponding effective
type and stat profile and persists until another qualifying damaging move.
Status moves do not trigger it. Do not implement until the designated Ability
for every Eeveelution form is locked.

## Batch strategy

Implement by reusable engine hook, not by arbitrary source order. Prefer batches
large enough to reuse shared code while keeping state-heavy mechanics isolated.

Initial order:
1. MR09A — namespace reservation only.
2. MR09B — threshold/reaction mechanics: Eternal Life, Hollow Shell,
   Prismatic Pelt, Adaptive Genome.
3. MR09C — move-lock control mechanics: Mind Games, The Look.
4. MR09D — player/AI choice architecture: Lockdown Protocol, Storm Sequence,
   Field Commissioner.
5. MR09E — held mechanics once their remaining exact decisions are locked:
   Controlled Fury and Protean Maxima.

## Non-canon implementation rules

- Preserve the approved Mercury mechanic exactly.
- Do not replace custom effects with vaguely similar vanilla mechanics when the
  difference matters.
- Reuse canonical MR08 hooks where behavior is genuinely identical.
- Record per-switch, per-turn, and once-per-battle state explicitly.
- Support doubles behavior and deterministic AI where a choice is required.
- Keep Primary Ability and Innate compatibility in mind, but do not force an
  Ability onto a species merely because it exists in the library.
- Keep locked MR07 Summary/editor visuals unchanged unless explicitly requested.
- Every mechanics batch must compile in the full ROM workflow before it is
  called implemented.
