---
name: survival-crafting
description: >
  Build a survival-crafting game: resource gathering, inventory, crafting and a tech tree,
  needs (hunger/thirst/temperature), and base building. Use for a survival or crafting/base-building game.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: advanced
---

# Survival Crafting

A playbook for survival-crafting games — the gather → craft → build loop, survival needs, the
crafting/tech progression, and base building. This is a **compositional** skill: it orchestrates
inventory data, world content, persistence, and threats. It does not re-teach those primitives;
it defines the loop and the pressure systems (needs, scarcity, escalation) that make survival
tense rather than tedious.

## When to use

- Use when the player **gathers resources, crafts items/structures, manages survival needs, and
  builds a base** against escalating threats: survival sandbox, crafting/base-building game.
- Use when designing needs (hunger/thirst/temperature), a crafting tech tree, gathering loops,
  or base placement/building.

**When *not* to use:** crafting as a minor RPG feature → `rpg`. Permadeath grid dungeon →
`roguelike`. For inventory/items as data assets, use `godot-resources` /
`unity-scriptableobjects`; for world generation, `procedural-gen`.

## Core loop

**Gather raw resources → craft tools/items → build and upgrade a base → manage survival needs
→ explore farther for better resources → survive escalating threats → repeat at a higher tier.**
Each loop should unlock the *next* loop (better tools → reach new biomes → new resources →
better crafts). When that ladder breaks, the game becomes a grind.

## Must-have systems

1. **Resource nodes + gathering** — harvestable world objects; tool requirements/tiers; respawn.
2. **Inventory** — stacks, capacity (slots or weight), drop/transfer, hotbar.
3. **Crafting** — recipes (inputs → output), a crafting station/tech gate, a tech tree.
4. **Survival needs** — hunger, thirst, temperature, stamina, health, with decay + consequences.
5. **Base building** — placeable structures, a build grid/snapping, storage, crafting stations.
6. **World + day/night** — biomes/resources (often procedural); a time cycle driving threats.
7. **Threats** — hostile creatures/weather/events that escalate; combat or avoidance.
8. **Save/load** — world state, inventory, base, needs, progression; large-world persistence.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| Needs decay rates | pressure cadence | Slow enough to explore, fast enough to matter. |
| Need-failure consequence | stakes | Damage over time, not instant death. |
| Resource scarcity / respawn | exploration push | Scarce near base → travel for more. |
| Tool tiers / gating | progression ladder | Better tool → new node types. |
| Recipe complexity / tech depth | long-term goals | Multi-step chains, not flat lists. |
| Inventory limit (slots/weight) | logistics tension | Forces base trips and storage. |
| Threat escalation curve | difficulty over time | Night/seasonal/event ramps. |
| Day length | rhythm | Day = gather, night = defend. |

## Patterns

### 1. Needs decay with graded consequences

```python
# Pseudocode in the per-frame/per-tick update. dt = seconds. Needs fall; failure bleeds HP.
def update_needs(p, dt):
    p.hunger = max(0, p.hunger - HUNGER_RATE * dt)
    p.thirst = max(0, p.thirst - THIRST_RATE * dt)
    p.temp   = approach(p.temp, ambient_temperature(p), TEMP_RATE * dt)

    # Consequences are graded, not binary: warnings, then attrition — never instant death.
    if p.hunger == 0 or p.thirst == 0:
        p.hp -= STARVE_DAMAGE * dt          # damage over time creates urgency with recovery room
    if p.temp < COLD_THRESHOLD or p.temp > HEAT_THRESHOLD:
        p.hp -= EXPOSURE_DAMAGE * dt
    if p.hunger > 0 and p.thirst > 0 and not exposed(p):
        p.hp = min(p.max_hp, p.hp + REGEN_RATE * dt)   # safe + fed => heal
```

### 2. Crafting: validate, then atomically consume inputs

```python
# Pseudocode. Recipes are data: inputs -> output, with an optional station/tech requirement.
recipe = {"id": "stone_axe",
          "inputs": {"wood": 3, "stone": 2}, "output": ("stone_axe", 1),
          "station": "workbench", "requires_tech": "basic_tools"}

def can_craft(recipe, inv, tech, station):
    if recipe.get("requires_tech") and recipe["requires_tech"] not in tech: return False
    if recipe.get("station") and recipe["station"] != station: return False
    return all(inv.count(item) >= n for item, n in recipe["inputs"].items())

def craft(recipe, inv, tech, station):
    if not can_craft(recipe, inv, tech, station): return False
    for item, n in recipe["inputs"].items(): inv.remove(item, n)   # consume all, then add
    inv.add(*recipe["output"])                                     # atomic: no partial craft
    return True
```

### 3. Gathering gated by tool tier

```python
# Pseudocode. A node yields only if the held tool meets its required tier.
def harvest(node, tool):
    if tool.tier < node.required_tier:
        return notify("Need a better tool")        # e.g. stone node needs a pickaxe, not fists
    node.hp -= tool.power
    if node.hp <= 0:
        spawn_drops(node.drop_table)               # weighted drops (see roguelike loot pattern)
        node.start_respawn(node.respawn_time)      # node returns later; world isn't depleted forever
```

## Pitfalls / failure modes

- **Needs that kill instantly** → frustration and save-scumming. Make failure damage over time,
  with clear warnings and a recovery path (Pattern 1).
- **Grind without a ladder** → gathering that never unlocks new gathering. Each tier must open
  the next (better tool → new node → new resource → better craft).
- **Non-atomic crafting** → inputs consumed but output not granted on an edge case. Validate
  first, then consume-and-add as one step (Pattern 2).
- **Inventory with no limits** → no logistics tension and no reason for a base/storage. Cap by
  slots or weight.
- **Permanently depleting the world** → players strip the map and quit. Respawn nodes or
  regenerate resources over time.
- **Per-frame decay unscaled by `dt`** → needs drain at different speeds on different hardware.
  Scale by `dt`.
- **No save / fragile save of a large world** → a crash wipes hours. Persist world+base+needs
  incrementally; version it (see `save-systems`).
- **Flat threat curve** → no late-game pressure. Escalate via night/season/event tiers.

## Composition (build it from these skills)

- **Items/recipes as data:** `godot-resources` / `unity-scriptableobjects` — items, recipes, tech tree, drop tables.
- **World:** `procedural-gen` for biomes/resource placement; `level-design` for authored areas.
- **Persistence:** `save-systems` for large-world state, base, inventory, needs, and versioning.
- **Threats:** `game-ai` for creatures; the engine physics skill for melee/collision.
- **Building/placement:** `godot-tilemap` / `unity-tilemap-2d` (2D) or `godot-3d-essentials` (3D) plus UI snapping.
- **UI:** `game-ui-ux` for inventory/crafting/HUD layout and scaling; `godot-ui-control` for the concrete inventory, crafting menu, needs HUD, and build mode.

## References

- For the full needs model and thresholds, the crafting tech-tree graph, gather/respawn tuning,
  base-building grids, and threat escalation, read `references/needs-and-crafting.md`.
