---
name: roguelike
description: >
  Build a roguelike: turn-based grid movement, procedural dungeons, permadeath, field-of-view,
  and loot tables. Use for a roguelike/roguelite or turn-based grid dungeon crawler with procedural levels.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: advanced
---

# Roguelike

A playbook for roguelikes — the turn engine, procedural dungeons, field-of-view, permadeath,
and run economy. This is a **compositional** skill: it orchestrates procedural generation,
tilemaps, save handling, and AI into a run-based game. It does not re-teach noise/RNG or
tilemap APIs; it defines the loop and the systems that make a *run* compelling.

## When to use

- Use when building a **turn-based, grid-based** dungeon crawler where each death ends the
  run and the world is regenerated — a roguelike or "roguelite" (with meta-progression).
- Use when designing procedural dungeons, FOV/fog-of-war, permadeath stakes, or loot tables.

**When *not* to use:** real-time action with roguelike *dressing* → build the action genre
(`platformer`/`fps-shooter`) and layer `procedural-gen`. Deep stats/quests/dialogue without
permadeath → `rpg`. Open-world needs/crafting → `survival-crafting`.

## What makes it a roguelike (design anchor)

The community reference is the **Berlin Interpretation** (RogueBasin, IRDC 2008): a set of
"roguelikeness" factors, not a checklist. The high-value ones are the design targets:
**random environment generation, permadeath, turn-based, grid-based, non-modal** (all actions
in one mode), **complexity** (many item/monster interactions), **resource management**,
**hack-and-slash**, and **exploration & discovery**. Lean into these to feel roguelike; pick
which to keep deliberately. "Roguelite" usually relaxes permadeath with meta-progression.

## Core loop

**Take a turn (move / fight / use) → the world resolves its turn → see new state → descend /
loot / survive → die and restart with a fresh dungeon.** Replayability comes from the *world*
changing each run, not the player memorizing a fixed layout.

## Must-have systems

1. **Turn scheduler** — energy/initiative system so fast actors act more often (Pattern 2).
2. **Grid map + movement** — tile coordinates; bump-to-attack; blocked/walkable queries.
3. **Procedural dungeon generator** — rooms + corridors, or BSP/cellular; guarantee connectivity.
4. **Field of view + explored memory** — what's visible now vs. seen-before (Pattern 3 / refs).
5. **Combat + entities** — HP, attack/defense, status; monsters obey the same rules as the player.
6. **Loot + drop tables** — weighted, depth-scaled item/monster spawning (refs).
7. **Permadeath + (optional) meta-progression** — wipe the run; persist only unlocks/score.
8. **Message log + clear UI** — the player reasons from text/state; surface numbers and events.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| Dungeon size / room count | run length, density | Scale with depth. |
| Connectivity guarantee | no unreachable rooms | Always verify reachability after generation. |
| Monster density / depth curve | difficulty ramp | Spawn by depth-weighted table. |
| Loot rarity weights | power variance | Rarer = bigger swing; identify adds discovery. |
| FOV radius / lighting | tension, information | Smaller radius = scarier, slower. |
| Resource scarcity (food/HP/ammo) | pressure to descend | Core tension lever in classic RLs. |
| Permadeath vs meta-progression | run stakes vs. retention | Roguelite softens the wall. |
| Identification / unknowns | exploration value | Unidentified items reward experimentation. |
| Seedable RNG | daily runs, debugging | Always allow a fixed seed (see `procedural-gen`). |

## Patterns

### 1. Deterministic, seedable run RNG

```python
# Pseudocode. One seeded RNG per run makes dungeons reproducible (daily runs, bug repro).
run_seed = chosen_seed or random_seed()
rng = Rng(run_seed)                 # use your engine's seedable RNG, not global random
dungeon = generate_dungeon(rng, depth)   # same seed + depth => same dungeon
# Persist run_seed in the save so a crash can resume the same world (see save-systems).
```

### 2. Energy-based turn scheduler (speeds differ)

```python
# Pseudocode. Each actor gains energy each tick and acts when it has enough.
# Faster actors gain more per tick, so they act more often — no fixed "player then enemies".
TURN_COST = 100
def next_actor(actors):
    while True:
        for a in actors:                 # stable order avoids ties favoring one side
            a.energy += a.speed          # e.g. speed 100 = normal, 150 = hasted
            if a.energy >= TURN_COST:
                a.energy -= TURN_COST
                return a                 # this actor takes exactly one action now
```

### 3. Field of view + explored memory

```python
# Pseudocode. Recompute visibility from the player each time they move.
visible = compute_fov(map, player.pos, radius=8)   # symmetric shadowcasting (see refs)
for cell in visible:
    explored.add(cell)                  # remember it forever (dim "fog of war")
# Render: visible -> lit; explored-but-not-visible -> dim; never-seen -> hidden.
```

Use a proven FOV algorithm (recursive shadowcasting or symmetric shadowcasting). Do not
roll a naive raycast-per-cell — it produces asymmetric, "blinking" vision. See refs.

## Pitfalls / failure modes

- **Disconnected dungeons** → rooms the player can't reach. Always run a connectivity/flood-fill
  pass and carve corridors until every walkable cell is reachable.
- **Naive FOV** → vision that flickers or is asymmetric (you see them, they don't see you).
  Use shadowcasting; test symmetry.
- **Real-time loop pretending to be turn-based** → input races and double-moves. Resolve one
  discrete turn at a time; queue input.
- **Flat difficulty** → no descent pressure. Scale monsters/loot by depth and keep resources scarce.
- **Permadeath that wipes meta-unlocks** → frustration. Separate *run* state (wiped) from
  *profile* state (unlocks, scores) when saving (see `save-systems`).
- **Save-scumming a "permadeath" game** → delete or invalidate the run save on load if you want
  true permadeath; keep only the profile.
- **Unreadable state** → the player can't plan. Show HP, turn results, and a message log.

## Composition (build it from these skills)

- **Generation:** `procedural-gen` (noise, seeded RNG, dungeon/room algorithms) — the engine of replayability.
- **Map rendering:** `godot-tilemap` / `unity-tilemap-2d` for the grid; `level-design` for set-piece rooms/vaults.
- **Enemies:** `game-ai` for monster decision-making (often simple on a grid: seek/flee/patrol).
- **Persistence:** `save-systems` for run-resume, profile/meta-progression, and true permadeath wipes.
- **Scripting/data:** `godot-resources` / `unity-scriptableobjects` to define items, monsters, and drop tables as data.
- **UI:** `godot-ui-control` for the message log, inventory, and HUD.
- **Feel:** `game-feel` for hit/death juice — screen shake and hit-stop that sell impacts on a turn-based grid.

## References

- For dungeon-generation algorithms (rooms-and-corridors, BSP, cellular automata, connectivity),
  FOV (shadowcasting), and weighted loot/spawn tables, read `references/generation-fov-loot.md`.
