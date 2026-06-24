# Behavior trees, FSMs, and the blackboard

A **behavior tree** (BT) is a tree of nodes ticked from the root each frame.
Every node's `tick()` returns one of three statuses:

- `SUCCESS` — the node finished its job this frame.
- `FAILURE` — the node could not do its job.
- `RUNNING` — the node needs more frames (a walk, an animation, a wait).

Control flows down from the root; status flows back up. The shape of the tree
*is* the priority logic, which is why BTs scale to many behaviors far better than
a flat FSM.

## Node taxonomy

| Category | Node | Behavior |
|---|---|---|
| Composite | **Sequence** | Tick children left→right; return on first non-`SUCCESS`. Logical AND. |
| Composite | **Selector** (Fallback) | Tick children left→right; return on first non-`FAILURE`. Logical OR. |
| Composite | **Parallel** | Tick all children; succeed/fail on a policy (e.g. N must succeed). |
| Decorator | **Inverter** | Swap `SUCCESS`↔`FAILURE`; pass `RUNNING` through. |
| Decorator | **Repeat / RepeatUntilFail** | Re-tick a child a number of times. |
| Decorator | **Cooldown / Timeout** | Gate or time-limit a child. |
| Leaf | **Condition** | Test the world/blackboard → `SUCCESS`/`FAILURE` (no side effects). |
| Leaf | **Action** | Do something; return `RUNNING` until complete. |

## Stateful composites and RUNNING

Naive composites restart from the first child every tick. For multi-frame
actions, a composite must **remember which child was RUNNING** and resume there:

```gdscript
class Sequence:
    var children = []
    var _running = 0                 # index of the child that returned RUNNING

    func tick(agent, dt) -> int:
        while _running < children.size():
            var s = children[_running].tick(agent, dt)
            if s == Status.RUNNING:
                return Status.RUNNING        # resume here next frame
            if s == Status.FAILURE:
                _running = 0                 # whole sequence fails; reset
                return Status.FAILURE
            _running += 1                    # child SUCCESS -> advance
        _running = 0                         # reached the end -> sequence succeeds
        return Status.SUCCESS
```

A Selector is the mirror image: it advances on `FAILURE`, returns on `SUCCESS`
or `RUNNING`, and resets its index when a child succeeds.

## Leaf examples

```gdscript
# Condition leaf: pure test, no side effects.
class CanSeePlayer:
    func tick(agent, dt) -> int:
        return Status.SUCCESS if agent.can_see(agent.blackboard.player) else Status.FAILURE

# Action leaf: multi-frame, returns RUNNING until it arrives.
class MoveTo:
    var key  # blackboard key holding the destination
    func tick(agent, dt) -> int:
        var dest = agent.blackboard.get(key)
        if dest == null: return Status.FAILURE
        agent.move_toward(dest, dt)
        return Status.SUCCESS if agent.position.distance_to(dest) < 4.0 else Status.RUNNING
```

A complete guard, as a tree:

```
Selector
├── Sequence            # attack branch (highest priority)
│   ├── CanSeePlayer
│   ├── MoveTo(player)
│   └── Attack
└── Patrol              # fallback when nothing else applies
```

## The blackboard

The **blackboard** is the shared memory that decouples nodes: conditions read it,
actions write it, and no node holds a hard reference to another. Store the
current target, last-known position, home point, path, and timers there. This is
what lets the same `MoveTo` action serve chase, patrol, and flee subtrees.

```gdscript
# A blackboard is just a typed key/value store on the agent.
agent.blackboard = {
    "player": null,            # set by perception each tick
    "home": Vector2(100, 100),
    "path": [],                # filled by the pathfinder
}
```

## FSM vs behavior tree — choosing

| Use an FSM when… | Use a behavior tree when… |
|---|---|
| 2–5 clearly named states | Many behaviors with priorities |
| Transitions are obvious and few | Behaviors interrupt/preempt each other |
| Behavior rarely changes | You want to reuse subtrees across enemies |
| You want the simplest thing | You need designer-tunable, data-driven AI |

Many shipping games use **both**: an FSM for top-level mode (Idle / Combat /
Dead) and a behavior tree inside the Combat state. Start with an FSM; graduate a
state to a behavior tree when its `if` logic outgrows a few transitions.

## Utility AI (brief)

When "how *much* do I want each option" matters more than discrete states, score
each candidate action with a utility function and pick the highest:

```
score(action) = sum of weighted considerations, each a 0..1 curve of a fact
choose the action with the maximum score (optionally softmax for variety)
```

Utility scales to nuanced trade-offs (heal vs attack vs flee by health/ammo/
distance) but is harder to debug than a tree. Reach for it when a BT's branching
becomes a thicket of conditions.
