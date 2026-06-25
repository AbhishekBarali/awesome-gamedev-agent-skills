---
name: card-game
description: >
  Build a card game: card data, deck/hand/discard zones, draw/shuffle/reshuffle, a turn structure,
  costs, and effect resolution. Use for a deckbuilder, TCG/CCG, or roguelike deckbuilder.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: intermediate
---

# Card Game

A playbook for card games — card data, the deck/hand/discard zones, the turn structure, and
how card effects resolve. This is a **compositional** skill: it models cards as data and wires
them to UI. It does not re-teach data assets or UI nodes; it defines the zone model, the draw
machinery, and the effect-resolution rules that keep a card game correct and bug-free.

## When to use

- Use when building any game where the core objects are **cards** moving between zones
  (deck → hand → play → discard): deckbuilder, TCG/CCG, solitaire, roguelike deckbuilder.
- Use when designing draw/shuffle/reshuffle, turn structure, card costs, or how effects resolve.

**When *not* to use:** board/tile state with matching rules → `puzzle`. RPG with an
incidental card battler → start from `rpg`. For defining cards as assets, use `godot-resources`
/ `unity-scriptableobjects`; for the hand/drag UI, use `godot-ui-control`.

## Core loop

**Draw to your hand → spend resources to play cards → effects resolve and change the board →
end the turn (cleanup/discard) → opponent/next phase → repeat until a win condition.** Depth
comes from the *combinations* a hand allows; the engine's job is to resolve them unambiguously.

## Must-have systems

1. **Card data** — id, name, cost, type, text, and an effect spec (data, not code).
2. **Zones** — deck (draw pile), hand, play/board, discard, exile/removed; cards live in exactly one.
3. **Draw + shuffle + reshuffle** — draw from deck to hand; reshuffle discard into deck when empty.
4. **Turn structure** — phases (untap/draw/main/combat/end) as a state machine.
5. **Resource system** — mana/energy/actions that gate how much you do per turn.
6. **Effect resolution** — apply a card's effects in a defined order; handle targets and triggers.
7. **Win/loss condition** — life total, deck-out, objective.
8. **UI** — hand layout, drag/drop or tap-to-play, zone counts, targeting affordances.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| Starting hand / draw-per-turn | tempo, consistency | More draw = less variance. |
| Hand size limit | hoarding vs. use | Discard down at end of turn. |
| Deck size (min) | consistency | Smaller = more reliable combos. |
| Resource curve | what's playable when | "Mana curve" paces power. |
| Card rarity / power budget | balance | Stronger cards cost more / are rarer. |
| Determinism vs. randomness | skill vs. swing | Shuffle + random effects add variance. |
| Reshuffle rules | deck-out, fatigue | Reshuffle discard, or punish empty deck. |
| Removal / answers | counterplay | Every threat needs an answer in the pool. |

## Patterns

### 1. Zones + draw with automatic reshuffle

```python
# Pseudocode. A card is in exactly one zone at a time; moving = remove here, add there.
def draw(n):
    for _ in range(n):
        if not deck:
            if not discard:          # truly empty: deck-out (lose, or take fatigue)
                on_deck_out(); return
            deck.extend(discard)     # reshuffle discard into deck
            discard.clear()
            shuffle(deck, rng)       # use a seeded RNG (see save-systems for replays)
        hand.append(deck.pop())
```

### 2. Card as data + effect resolution

```python
# Pseudocode. Effects are a data list interpreted by the engine — not bespoke code per card.
card = {
    "id": "fireball", "cost": 3, "type": "spell",
    "effects": [ {"op": "damage", "amount": 6, "target": "chosen_enemy"} ],
}
def play(card, caster):
    if resources[caster] < card.cost: return False     # can't afford
    resources[caster] -= card.cost
    move(card, from_zone=hand, to_zone=play_or_discard(card))
    for fx in card.effects:
        resolve_effect(fx, caster)                      # one interpreter handles every card
    return True
```

### 3. Turn structure as a phase machine

```python
# Pseudocode. Fixed phases keep timing windows (triggers, priority) unambiguous.
PHASES = ["untap", "draw", "main", "combat", "end"]
def take_turn(player):
    for phase in PHASES:
        enter_phase(player, phase)        # fire "on_phase" triggers here
        if phase == "draw":   draw(1)
        if phase == "main":   await player_plays_cards()
        if phase == "combat": resolve_combat()
        if phase == "end":    discard_to_hand_limit(player); clear_temporary_effects()
```

## Pitfalls / failure modes

- **A card existing in two zones at once** → duplication/loss bugs. Enforce "exactly one zone";
  move = remove-then-add, and assert no card appears twice.
- **Forgetting to reshuffle** → draws silently fail or crash on empty deck. Reshuffle discard,
  or define deck-out/fatigue explicitly (Pattern 1).
- **One function per card** → unmaintainable and untestable. Make effects **data** interpreted
  by a small set of operations (Pattern 2).
- **Ambiguous effect order / simultaneous triggers** → nondeterministic outcomes. Resolve in a
  defined order (a queue or stack); document LIFO vs. FIFO (refs).
- **Unseeded shuffle in a game that needs replays/undo** → can't reproduce. Use a seeded RNG.
- **No hand limit / no answers** → degenerate hoarding or unbeatable threats. Add a hand cap and
  ensure removal exists for every threat archetype.
- **Targeting state leaks** → a cancelled play leaves the board mid-targeting. Make play
  atomic: validate cost + targets first, then commit.

## Composition (build it from these skills)

- **Card content:** `godot-resources` / `unity-scriptableobjects` — define each card as a data asset.
- **UI:** `game-ui-ux` for layout, scaling, and focus navigation; `godot-ui-control` for hand layout, drag/drop, zone counts, and targeting prompts.
- **Persistence/replays:** `save-systems` for collection, run state (roguelike deckbuilder), and seeded replays.
- **Opponent AI:** `game-ai` for an AI that evaluates playable cards and picks targets.
- **Animation/feedback:** the engine animation skill for card movement; `audio-design` for cues.
- **Scripting:** `godot-gdscript` / `unity-csharp-scripting` for the effect interpreter.

## References

- For the effect queue/stack, keywords/triggers, targeting, deckbuilder vs. constructed
  archetypes, and shuffle fairness, read `references/effect-resolution.md`.
