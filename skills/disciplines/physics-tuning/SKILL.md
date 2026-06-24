---
name: physics-tuning
description: >
  Tune game physics for stable, good-feeling motion — fixed vs variable
  timestep, render interpolation, mass/gravity/drag, continuous collision
  detection (CCD) to stop tunneling, fixing jitter, and collision layers/masks.
  Engine-neutral. Use when the user mentions physics feel, jitter, tunneling,
  fixed timestep, FixedUpdate, CCD, bouncing/unstable physics, or collision layers.
license: Apache-2.0
compatibility: Engine-agnostic concepts. Pairs with godot-physics (_physics_process) and unity-physics (FixedUpdate, Rigidbody); snippets in GDScript/C#-like pseudocode.
metadata:
  engine: none
  category: disciplines
  difficulty: intermediate
---

# Physics tuning

Most "bad physics" is not a bug in the engine — it's a mismatch between the
**fixed-timestep simulation** and the **variable-rate render loop**, or untuned
mass/drag/CCD/layer settings. This skill covers the engine-neutral knobs that
make physics stable and responsive; pair it with `godot-physics` or
`unity-physics` for the concrete APIs.

## When to use

- Use when motion jitters, objects pass through walls (tunneling), stacks
  explode, or movement feels floaty/sticky/laggy.
- Use to decide what goes in the fixed (physics) step vs the render frame, and
  how to interpolate between them.
- Use to tune gravity, mass, drag, restitution, solver iterations, sleeping, and
  collision layers/masks.

**When *not* to use:** for an engine's exact physics nodes/components and
collision callbacks, use `godot-physics` or `unity-physics`. For *movement
decisions* (when to jump, AI steering) use `input-systems` and `game-ai`. For
platformer jump-feel specifics like coyote time/jump buffering, that's input/
controller territory — see `input-systems` and the `platformer` genre.

## Core workflow

1. **Run physics on a fixed timestep.** Simulate at a constant rate (e.g. 50–60
   Hz). A fixed `dt` makes the simulation deterministic-ish and stable; a
   variable `dt` makes integration and collisions inconsistent.
2. **Put physics work in the physics callback**, not the render frame. Apply
   forces/velocities and read collisions in the fixed step (`FixedUpdate` /
   `_physics_process`), using that step's `dt`.
3. **Interpolate rendering between physics ticks.** The render frame rate ≠ the
   physics rate, so smoothly interpolate transforms toward the latest physics
   state, or enable the engine's Rigidbody interpolation, to remove visible
   stutter.
4. **Tune the body, not the scene.** Set mass for relative weight, drag for
   damping, gravity scale per object, and restitution/friction via materials.
5. **Stop tunneling with CCD** on small/fast bodies; cap maximum velocity.
6. **Stabilize stacks/joints** with more solver iterations, sane mass ratios, and
   sleeping for resting bodies.
7. **Verify by feel and stress test.** Play at low and high frame rates; throw
   fast objects at thin walls; stack and shove bodies. Report what you observed.

## Patterns

### 1. Fixed timestep for simulation, render interpolation for smoothness

```gdscript
# Physics callback: runs at the FIXED rate. Use its dt for all integration.
func _physics_process(dt):                  # Unity: void FixedUpdate()
    velocity += gravity * dt                # integrate with the FIXED dt
    move_and_slide()                        # engine resolves collisions this step
    _prev_pos = _curr_pos; _curr_pos = global_position   # record for interpolation

# Render frame: runs as fast as the display. Interpolate between physics states.
func _process(_frame_dt):                   # Unity: void Update()
    var alpha = Engine.get_physics_interpolation_fraction()  # 0..1 within the tick
    visual.global_position = _prev_pos.lerp(_curr_pos, alpha)
# RIGHT: integrate in the fixed step, render via interpolation.
# WRONG: applying forces in _process/Update with frame dt — speed and collisions
# then depend on frame rate and jitter under load.
```

Most engines offer this for you (Godot `physics_interpolation`/Rigidbody
interpolate; Unity `Rigidbody.interpolation = Interpolate`). Prefer the built-in
before hand-rolling.

### 2. Stop tunneling: CCD + a speed cap

```gdscript
# Fast, small bodies skip past thin colliders between ticks. Two fixes:
body.continuous_cd = true            # Unity: rb.collisionDetectionMode = Continuous
# Cap velocity so a single step can't move more than ~one collider thickness.
const MAX_SPEED := 40.0
if velocity.length() > MAX_SPEED:
    velocity = velocity.normalized() * MAX_SPEED
# Rule of thumb: max_distance_per_step (= speed / physics_hz) should be < the
# thinnest wall. Raise physics_hz or enable CCD when that fails.
```

### 3. Body tuning: mass, drag, gravity scale, material

```gdscript
# Mass is RELATIVE weight in collisions; it does NOT change fall speed (gravity
# accelerates all masses equally). Use drag and gravity_scale to shape feel.
body.mass = 2.0                      # heavier pushes lighter in collisions
body.linear_damp = 0.5               # air drag: higher = stops sooner (Unity: drag)
body.gravity_scale = 1.5             # per-object gravity multiplier (snappier fall)
# Bounce/slide come from the physics material, not code:
material.bounce = 0.2                # restitution 0..1 (Unity: bounciness)
material.friction = 0.8              # surface grip
```

### 4. Collision layers and masks (who collides with whom)

```gdscript
# A body is ON its layer(s) and SCANS the layers in its mask. Both directions of a
# pair must be configured for them to interact.
player.collision_layer = LAYER_PLAYER
player.collision_mask  = LAYER_WORLD | LAYER_ENEMY     # player detects world+enemies
pickup.collision_layer = LAYER_PICKUP
pickup.collision_mask  = LAYER_PLAYER                  # pickup only reacts to player
# Unity equivalent: assign GameObject layers and edit the Physics collision matrix
# (or Physics.IgnoreLayerCollision). Keep a named layer constant table, not magic numbers.
```

## Pitfalls

- **Applying forces/movement in the render frame** (`Update`/`_process`) makes
  behavior frame-rate dependent — faster PCs run faster, and collisions get
  flaky. Do simulation in the fixed step.
- **Visible jitter** even with a fixed step usually means no render
  interpolation: the physics rate and display rate beat against each other.
  Enable interpolation.
- **Tunneling** through thin walls: discrete collision misses fast movers. Enable
  CCD, cap speed, thicken walls, or raise the physics rate.
- **Expecting heavier objects to fall faster.** Gravity is acceleration; mass
  affects collision response, not fall speed. Use `gravity_scale`/drag for feel.
- **Exploding stacks / jittery joints**: mass ratios too extreme, or too few
  solver iterations. Keep mass ratios modest and raise iteration counts.
- **Bodies that never rest** burn CPU and twitch. Enable sleeping and a sensible
  sleep threshold for resting objects.
- **One-directional layer setup**: A's mask includes B but B's mask excludes A.
  Detection/collision can need both sides; verify the full matrix.
- **Huge `dt` spikes** (load hitches, breakpoints) blow up integration. Clamp the
  max physics step / substep count so a stall doesn't launch everything.

## References

- `references/timestep-and-ccd.md` — the fixed-timestep accumulator loop,
  interpolation math, substepping, CCD modes, solver/iteration tuning, sleeping,
  and a stability checklist.

## Related skills

- `godot-physics`, `unity-physics` — concrete bodies, colliders, and callbacks.
- `input-systems` — responsive controls, jump buffering, coyote time.
- `game-ai` — agent movement that must agree with the physics step.
- `platformer`, `fps-shooter` — genres whose feel depends on this tuning.
