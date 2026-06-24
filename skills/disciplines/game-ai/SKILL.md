---
name: game-ai
description: >
  Design NPC and enemy decision-making with finite state machines, behavior
  trees, steering behaviors, and A* pathfinding — engine-neutral algorithms
  that pair with the detected engine's navigation API. Use when building enemy
  AI, an FSM or behavior tree, steering/flocking, or pathfinding, or when the
  user mentions state machine, behavior tree, blackboard, A*, navmesh, seek, or
  patrol/chase.
license: Apache-2.0
compatibility: Engine-agnostic (algorithms). Concrete snippets in GDScript-like / Python pseudocode; pairs with unity-navmesh, unreal-behavior-trees, or Godot NavigationServer.
metadata:
  engine: none
  category: disciplines
  difficulty: advanced
---

# Game AI: decisions, steering, and pathfinding

Build believable NPC behavior from three separable layers: **decide** (what to
do), **steer** (how to move there), and **path** (how to route around the map).
Keep them decoupled — a behavior tree picks a target, the pathfinder produces
waypoints, steering follows them. This skill teaches the engine-neutral
algorithms; bind them to your engine via the related skills below.

## When to use

- Use when implementing enemy/NPC logic: patrols, chase/flee, guard states,
  group movement, or "find a path to the player".
- Use to choose between an **FSM** (few clear states), a **behavior tree** (many
  reactive behaviors with priorities), or **steering** (smooth local movement).
- Use when integrating pathfinding: A* on a grid/graph, or driving an engine
  navmesh agent.

**When *not* to use:** for the engine's concrete navmesh/agent API and baking,
use `unity-navmesh`, `unreal-behavior-trees`, or Godot's `NavigationAgent2D/3D`
(see that engine skill). For movement/collision feel, use `physics-tuning`. For
spawning waves along lanes, see the `tower-defense` genre skill.

## Core workflow

1. **Pick the decision model by complexity.** 2–5 states with obvious
   transitions → FSM. Many behaviors, priorities, interruption, reuse → behavior
   tree. Continuous "how strongly do I want each option" → utility scoring.
2. **Separate decision from motion.** The decision layer outputs an *intent*
   (target position, action). Steering or pathfinding turns intent into motion.
3. **Path on the right graph.** Grid tiles, waypoint graph, or a baked navmesh.
   Fewer nodes = faster A*. Prefer the engine's navmesh for 3D; A* on a grid for
   tile games.
4. **Steer along the path**, not straight to the goal — follow the next waypoint,
   advancing when close, so agents round corners.
5. **Recompute paths sparingly.** Pathfind on a timer or when the goal moves a
   tile, not every frame. Cache the path; only the waypoint index advances.
6. **Verify by observation.** Watch the agent: does it reach the goal, get stuck
   on corners, oscillate between states? Draw the path and current state on
   screen while tuning.

## Patterns

### 1. Finite state machine (one state object, explicit transitions)

```gdscript
# Each state is a small object with enter/update/exit. The machine owns "current".
class_name State
func enter(agent): pass
func update(agent, dt) -> State: return null   # return a new state to transition
func exit(agent): pass

# --- Chase state: returns Patrol when the player escapes sight range ---
class Chase extends State:
    func update(agent, dt) -> State:
        if not agent.can_see(agent.target):
            return Patrol.new()                 # transition by returning next state
        agent.move_toward(agent.target.position, dt)
        return null                             # null = stay in this state

# --- Driver: call once per frame ---
func tick(dt):
    var next = current.update(self, dt)
    if next != null:
        current.exit(self); next.enter(self); current = next
```

Keep transition logic *inside* states (or in a table), never as a growing pile
of `if` flags. One state owns one behavior; that is what keeps an FSM readable.

### 2. Behavior tree tick (composite nodes return a status)

```gdscript
# A node's tick() returns SUCCESS, FAILURE, or RUNNING (still working this frame).
enum Status { SUCCESS, FAILURE, RUNNING }

# Sequence: run children in order; stop at the first non-SUCCESS (logical AND).
func sequence_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.SUCCESS:
            return s                 # FAILURE or RUNNING short-circuits the sequence
    return Status.SUCCESS

# Selector: try children until one succeeds or is RUNNING (logical OR / fallback).
func selector_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.FAILURE:
            return s                 # SUCCESS or RUNNING stops the search
    return Status.FAILURE
```

A guard AI reads top-down: `Selector[ Sequence[CanSeePlayer?, Chase], Patrol ]`
— chase if visible, otherwise patrol. See `references/behavior-trees.md` for
leaf nodes, decorators (Inverter, Cooldown), and a blackboard.

### 3. Steering: seek and arrive (smooth, frame-rate independent)

```gdscript
# Seek: accelerate toward a target at full speed. Steering = desired - current.
func seek(pos, vel, target, max_speed, max_force) -> Vector2:
    var desired = (target - pos).normalized() * max_speed
    return (desired - vel).limit_length(max_force)   # a force, not a teleport

# Arrive: like seek, but ramp speed down inside slow_radius so it stops cleanly.
func arrive(pos, vel, target, max_speed, max_force, slow_radius) -> Vector2:
    var offset = target - pos
    var dist = offset.length()
    if dist < 0.001: return -vel                      # already there: kill drift
    var ramped = max_speed * min(dist / slow_radius, 1.0)
    var desired = offset / dist * ramped
    return (desired - vel).limit_length(max_force)

# Per frame: vel += steering * dt; pos += vel * dt   (always scale by dt)
```

### 4. A* heuristic must not overestimate (or paths stop being shortest)

```python
# Match the heuristic to the movement. An ADMISSIBLE heuristic (never larger
# than the true remaining cost) keeps A* optimal.
def heuristic(a, b):
    dx, dy = abs(a.x - b.x), abs(a.y - b.y)
    # return dx + dy             # Manhattan: 4-direction grids (no diagonals)
    return (dx + dy) + (1.414 - 2) * min(dx, dy)   # octile: 8-direction grids
# f(n) = g(n) + h(n): g = cost from start, h = heuristic to goal.
# Overestimating h is faster but no longer guarantees the shortest path.
```

The full A* loop (priority queue, `came_from` reconstruction, grid + waypoint
graphs) is in `references/pathfinding.md`.

## Pitfalls

- **Pathfinding every frame** tanks the frame rate. Recompute on a timer or only
  when the target moves to a new tile; follow the cached waypoints in between.
- **Steering straight to the goal** instead of to the next waypoint makes agents
  hug walls and corners. Follow the path; advance the waypoint when within radius.
- **Inadmissible A\* heuristic** (e.g. Euclidean distance scaled up, or Manhattan
  on a diagonal grid) returns fast but *non-shortest* paths. Pick the heuristic
  that matches your allowed moves.
- **Behavior tree leaves that never return RUNNING** for multi-frame actions
  (walking, playing an animation) cause the tree to restart the action every
  tick. Return RUNNING until the action completes.
- **FSM transition spaghetti**: scattering `if state == ...` checks everywhere
  recreates the mess an FSM exists to prevent. Keep transitions in the state.
- **No line-of-sight or stuck check** → agents grind into walls forever. Add a
  timeout that forces a repath or a state change.

## References

- `references/pathfinding.md` — complete A* (priority queue, reconstruction),
  grid vs waypoint graphs, when to defer to an engine navmesh.
- `references/behavior-trees.md` — node taxonomy, leaf/decorator implementations,
  blackboard, and FSM-vs-BT selection.

## Related skills

- `unity-navmesh`, `unreal-behavior-trees` — concrete engine AI/navigation APIs.
- `physics-tuning` — movement, collision response, and agent radius.
- `procedural-gen` — generating the graph/level the AI navigates.
- `tower-defense`, `fps-shooter` — genres that compose this skill.
