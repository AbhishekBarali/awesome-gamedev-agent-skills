---
name: procedural-gen
description: >
  Generate game content procedurally — seeded deterministic RNG, value/Perlin/
  Simplex noise for terrain and heightmaps, grid dungeon generation (rooms +
  corridors, BSP, random walk), and weighted loot/drop tables. Engine-neutral
  algorithms. Use when the user mentions procedural generation, perlin/simplex
  noise, random seed, dungeon generator, heightmap/terrain, or loot tables.
license: Apache-2.0
compatibility: Engine-agnostic (algorithms). Snippets in Python/GDScript-like pseudocode; uses a noise library (FastNoiseLite, opensimplex, Unity.Mathematics.noise).
metadata:
  engine: none
  category: disciplines
  difficulty: advanced
---

# Procedural generation

Generate levels, terrain, and loot from compact rules and a seed. The throughline
of good procgen is **determinism**: a single seed reproduces the same world, so
bugs are repeatable and players can share seeds. This skill owns the core
algorithms — noise, seeded RNG, dungeon layout, weighted tables; genres like
`roguelike` and `survival-crafting` consume it.

## When to use

- Use to generate maps, dungeons, terrain heightmaps, item drops, or any content
  you do not want to author by hand.
- Use when results must be **reproducible from a seed** (debugging, daily
  challenges, shareable worlds).
- Use to pick weighted random outcomes (loot rarity, spawn tables).

**When *not* to use:** for the engine's tile API to *paint* the result, use
`godot-tilemap` or `unity-tilemap-2d`. For routing AI through the generated map,
use `game-ai`. For carefully hand-paced levels, use `level-design` — procgen and
authored design are complementary, not interchangeable.

## Core workflow

1. **Own your randomness.** Create one seeded RNG instance and pass it
   everywhere. Never call the global/static random in generation code — it makes
   results irreproducible and order-dependent.
2. **Pick the technique for the content.** Continuous terrain/heightmaps → noise.
   Discrete rooms/corridors → space partitioning or agent-based carving.
   Outcomes with rarities → weighted tables.
3. **Generate into a plain data grid/array first**, decoupled from rendering.
   Generation fills `int[][]` or a dict; a separate pass draws it.
4. **Validate before shipping the result to the player.** Is every room
   reachable? Is the spawn safe? Is there a path to the exit? Reject or repair
   layouts that fail; do not hand the player a broken map.
5. **Tune with the seed fixed** so each parameter change is visible in isolation,
   then sweep seeds to check the distribution, not just one lucky map.

## Patterns

### 1. Seeded, deterministic RNG (the foundation)

```python
import random
rng = random.Random(seed)        # a dedicated instance — NOT the global random.*
room_count = rng.randint(5, 12)  # same seed -> same sequence, every run
# RIGHT: thread `rng` through every function that makes a choice.
# WRONG: calling random.randint(...) (global state) — order-dependent, unseedable.
```

Engine equivalents: Godot `var rng = RandomNumberGenerator.new(); rng.seed = s`;
Unity `var rng = new System.Random(seed)` (or `UnityEngine.Random.InitState`).
Store the seed in the save file so a world can be regenerated.

### 2. Fractal (fBm) noise for heightmaps

```python
# Sum several octaves: each higher octave has higher frequency, lower amplitude.
def fbm(noise, x, y, octaves=5, lacunarity=2.0, gain=0.5):
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * noise(x * freq, y * freq)   # noise() returns ~0..1
        norm  += amp                                # track total amplitude
        amp   *= gain                               # each octave contributes less
        freq  *= lacunarity                         # ...at a higher frequency
    return total / norm                             # normalize back into 0..1

# Redistribute to carve flat valleys / sharpen peaks: higher exp -> more lowland.
elevation = pow(fbm(noise, nx, ny), 2.2)
```

Use a real noise library (`FastNoiseLite`, `opensimplex`,
`Unity.Mathematics.noise`, or `Mathf.PerlinNoise`) — do not implement gradient
noise yourself. Seed **elevation and moisture with different seeds** so a
biome lookup over both fields isn't perfectly correlated. Full biome lookup and
island shaping are in `references/noise.md`.

### 3. Weighted loot table (rarity-correct selection)

```python
# Roll proportional to weight: common drops far more often than legendary.
def weighted_pick(rng, table):           # table: list of (item, weight)
    total = sum(w for _, w in table)
    roll = rng.uniform(0, total)          # a point on the cumulative line
    upto = 0.0
    for item, w in table:
        upto += w
        if roll < upto:                   # first bucket the roll falls into
            return item
    return table[-1][0]                   # float-safety fallback

loot = weighted_pick(rng, [("common", 70), ("rare", 25), ("legendary", 5)])
```

Weights need not sum to 100 — they are relative. To prevent bad streaks, use a
"pity"/bag system (see `references/dungeon-generation.md` notes on distributions).

### 4. Rooms-and-corridors dungeon (sketch)

```python
# 1. Place non-overlapping rooms; 2. connect them; 3. carve into the grid.
rooms = []
for _ in range(attempts):
    r = Rect(rng.randint(1, W-w-1), rng.randint(1, H-h-1), w, h)
    if not any(r.intersects(o.expand(1)) for o in rooms):  # keep a 1-tile gap
        rooms.append(r)
for a, b in zip(rooms, rooms[1:]):       # connect each room to the next
    carve_l_corridor(grid, a.center, b.center, rng)   # horizontal then vertical
```

The complete generator (BSP partitioning, L-corridors, reachability check, and
random-walk caves) is in `references/dungeon-generation.md`.

## Pitfalls

- **Using the global RNG** inside generation makes worlds unreproducible and
  breaks the moment call order changes. Always pass a seeded instance.
- **Correlated noise fields**: sampling elevation and moisture from the *same*
  seed/offset produces biomes that line up in bands. Offset or reseed each field.
- **Octave artifacts**: adding octaves without renormalizing pushes values out of
  `0..1`; divide by the summed amplitude (and beware library output ranges — some
  return `-1..1`, some `0..1`).
- **No connectivity check**: rooms or caves can end up isolated. Flood-fill from
  the spawn and discard/reconnect unreachable regions before play.
- **Unbounded placement loops**: "keep trying until N rooms fit" can spin forever
  on a small grid. Cap attempts and accept fewer rooms.
- **Seeding once globally, then relying on frame timing**: any non-deterministic
  input (time, physics, hash randomization) leaking into generation destroys
  reproducibility.

## References

- `references/noise.md` — octaves/lacunarity/gain, redistribution, island
  shaping, two-axis biome lookup, blue-noise object scatter.
- `references/dungeon-generation.md` — BSP, rooms+corridors, random-walk caves,
  cellular-automata smoothing, connectivity validation, distribution/pity tables.

## Related skills

- `godot-tilemap`, `unity-tilemap-2d` — paint the generated grid into the engine.
- `game-ai` — pathfinding over the generated graph.
- `level-design` — pacing and hand-authored structure that procgen complements.
- `roguelike`, `survival-crafting` — genres that compose this skill.
