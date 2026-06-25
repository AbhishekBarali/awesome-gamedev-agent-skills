---
name: rpg
description: >
  Build an RPG: stats and leveling, inventory and equipment, quests, branching dialogue, save/load,
  and combat. Use for an RPG/JRPG, or designing stat, inventory, quest, or combat systems.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: advanced
---

# RPG

A playbook for role-playing games — stats and progression, inventory/equipment, quests,
dialogue, and combat. This is a **compositional** skill: it ties data-driven content,
dialogue, and saving together. It does not re-teach those primitives; it defines the systems
that make growth and choice feel meaningful, and points to the skills that implement each.

## When to use

- Use when building an RPG/JRPG/action-RPG: the player has **stats that grow**, an
  **inventory**, **quests**, **dialogue**, and persistent progress.
- Use when designing a leveling curve, a damage formula, an inventory/equipment model, or a
  quest state machine.

**When *not* to use:** permadeath dungeon runs with no persistent character → `roguelike`.
Pure conversation/branching story → `visual-novel`. Open-world needs/crafting/base-building →
`survival-crafting`. For the dialogue engine itself, use `dialogue-systems`.

## Core loop

**Explore → encounter (fight / talk / solve) → earn rewards (XP, loot, story) → grow
(level up, gear up, unlock) → take on harder content.** The fantasy is *getting stronger and
shaping who your character is*; every system should feed that growth-and-choice loop.

## Must-have systems

1. **Stats + leveling** — base attributes, derived combat stats, XP curve, level-up gains.
2. **Inventory + equipment** — data-defined items, stacking, slots, stat modifiers.
3. **Combat** — turn-based or action; damage formula, status effects, win/loss.
4. **Quests** — objectives, state machine (available→active→complete→turned-in), rewards.
5. **Dialogue** — branching lines, conditions on game state, choices that matter.
6. **Save/load** — persist character, inventory, quest progress, world flags, with versioning.
7. **Economy + progression gating** — gold/shops; gate power behind level/quest/region.
8. **UI** — HUD, inventory, quest log, dialogue box, character sheet.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| XP curve shape | pacing of power | Fast early, slow late (see refs). |
| Stat→derived scaling | build diversity | One attribute shouldn't dominate. |
| Damage formula | tactical feel | Subtractive vs. ratio mitigation (refs). |
| Random variance / crit | swinginess | ±10% and ~1.5× crit are safe defaults. |
| Drop rates / economy | reward cadence | Avoid trivializing shops with loot. |
| Power gating | difficulty gating | Level/region/quest locks. |
| Reversible modifiers | buff/gear correctness | Layer mods; never edit base stats. |
| Choice consequence | role-play weight | Quest/dialogue flags should branch outcomes. |

## Patterns

### 1. Derived stats from base attributes (recompute, never store as truth)

```python
# Pseudocode. Base attributes are the only "truth"; combat stats are derived each time.
def derive(base, mods):
    s = apply_modifiers(base, mods)          # base + flat adds + percent, then clamp
    return {
        "max_hp":  20 + s["VIT"] * 8,
        "attack":  s["STR"] * 2,
        "defense": s["VIT"] + s["AGI"] * 0.5,
    }
# Equipping pushes a modifier; unequipping pops it. HP/attack recompute automatically.
```

### 2. XP curve + level-up

```python
# Pseudocode. Quadratic curve: fast early levels, long late ones.
def xp_to_next(level, base=100): return base * level * level

def gain_xp(actor, amount):
    actor.xp += amount
    while actor.xp >= xp_to_next(actor.level):
        actor.xp -= xp_to_next(actor.level)
        actor.level += 1
        actor.base["STR"] += 2; actor.base["VIT"] += 2   # grant gains / skill points
        on_level_up(actor)                                # heal, unlock, notify
```

### 3. Quest objective update driven by game events

```python
# Pseudocode. Game events advance matching objectives; completion grants rewards.
def on_event(kind, data):
    for q in active_quests:
        for obj in q.objectives:
            if obj.event == kind and matches(obj, data) and not obj.done:
                obj.count += 1
                if obj.count >= obj.needed: obj.done = True
        if all(o.done for o in q.objectives):
            q.state = "complete"                # turn-in grants xp/gold/items
```

## Pitfalls / failure modes

- **Editing base stats for buffs/gear** → values drift and corrupt on save/reload. Keep a
  modifier layer; push/pop it (Pattern 1).
- **Storing derived stats as truth** → desync after a stat change. Recompute from base.
- **Runaway XP/damage numbers** → either an exponential curve with no cap or a subtractive
  formula at huge values. Pick a curve and a formula family deliberately (refs).
- **Content as code** → every item/quest hardcoded. Define items, enemies, and quests as
  **data** (`godot-resources` / `unity-scriptableobjects`).
- **Save format with no version field** → old saves break on update. Add a `version` and a
  migration path from day one (see `save-systems`).
- **Choices without consequences** → dialogue branches that reconverge immediately feel hollow.
  Set flags that actually change later quests/world state.
- **Quest progress not persisted** → reloading loses mid-quest state. Save quest state, not
  just completion.

## Composition (build it from these skills)

- **Dialogue:** `dialogue-systems` (Yarn Spinner / Ink) — branching lines, conditions, variables.
- **Persistence:** `save-systems` — character, inventory, quest flags, world state, versioning.
- **Content data:** `godot-resources` / `unity-scriptableobjects` — items, enemies, quests, skills as assets.
- **Combat AI:** `game-ai` for enemy behavior; for turn order reuse the scheduler idea in `roguelike`.
- **UI:** `game-ui-ux` for HUD/menu layout, resolution scaling, and controller/keyboard nav; `godot-ui-control` for the concrete inventory, quest log, character sheet, and dialogue box.
- **World:** `level-design` plus your engine's tilemap/3D skill (`godot-tilemap`, `godot-3d-essentials`).

## References

- For stat/damage formulas, leveling curves, turn-vs-action combat timelines, inventory/equipment
  data shapes, and the quest state model, read `references/stats-combat-quests.md`.
