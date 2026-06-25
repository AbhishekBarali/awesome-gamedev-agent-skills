---
name: camera-systems
description: >
  Build game cameras that feel good — 2D follow with a deadzone, look-ahead, smoothing, and
  level-bounds clamping; 3D third-person orbit with collision and first-person look; plus
  multi-target framing and a shake hook. Engine-neutral techniques that pair with the engine's
  camera node and rigs like Unity Cinemachine or Godot Camera2D/PhantomCamera. Use when the user
  mentions camera follow, follow camera, deadzone, look-ahead, camera smoothing, camera bounds/
  limits, third-person camera, orbit camera, first-person look, Cinemachine, or camera jitter.
license: Apache-2.0
compatibility: Engine-agnostic camera techniques; snippets in GDScript (Godot 4.x Camera2D/Camera3D) and C# (Unity 6 / Cinemachine 3). Pairs with godot-2d-movement, godot-3d-essentials, and game-feel.
metadata:
  engine: none
  category: disciplines
  difficulty: intermediate
---

# Camera systems

The camera is the player's window; bad camera work makes a good game feel awful. This skill
covers the engine-neutral camera techniques — smooth follow, deadzones, look-ahead, bounds
clamping, third-person orbit with collision, first-person look, and multi-target framing — and
maps them onto each engine's camera node or rig.

## When to use

- Use when a 2D camera should follow the player smoothly, stay inside the level, lead the
  player's motion, or ignore small movements (deadzone).
- Use when building a 3D third-person orbit camera (mouse/stick look, collision push-in) or a
  first-person look controller, or framing multiple targets at once.
- Use to fix camera jitter, snapping, motion sickness, or a camera that shows past the level edge.

**When *not* to use:** for the *magnitude and trigger* of screen shake and impact juice, use
`game-feel` (this skill exposes the shake offset hook it drives). For the engine's concrete
camera node/component setup, use `godot-3d-essentials` (Camera3D, environment) or the engine
skill. For player movement itself use the engine movement skill (`godot-2d-movement`). For
performance of many cameras/render targets, see `performance-optimization`.

## Core workflow

1. **Decide what the camera serves.** Platformer (lead the jump, see hazards), top-down (center
   with deadzone), third-person (orbit + collision), first-person (look only). The genre sets the
   rules.
2. **Follow smoothly and frame-rate independently.** Move the camera toward the target with
   exponential smoothing or a spring (`SmoothDamp`), not a fixed `lerp(a, b, 0.1)` — that 0.1 is
   per-frame and changes with frame rate.
3. **Add a deadzone** so tiny target movements don't nudge the camera; it only follows once the
   target leaves a box/zone. Stops nausea in twitchy games.
4. **Lead the action with look-ahead** by offsetting the camera target in the direction of
   motion or facing, eased in/out so it doesn't whip.
5. **Clamp to level bounds** so the camera never shows outside the playable area; combine with
   smoothing so it eases to a stop at the edge.
6. **For 3D, separate look from collision.** Orbit via yaw/pitch on a rig; use a spring arm /
   ray to pull the camera in when geometry blocks it; clamp pitch.
7. **Update the camera after the target moves.** Follow in the late/post step (after movement and
   physics resolve) to avoid a one-frame lag jitter.
8. **Verify by moving the target at low and high frame rates**, into corners and walls, and at
   the level edges; confirm no jitter, no peeking past bounds, smooth stops. Report what you saw.

## Patterns

### 1. Godot 2D built-in follow: smoothing + bounds (don't hand-roll first)

```gdscript
# Godot 4.x Camera2D. Engine-provided smoothing + hard limits + drag margins.
@onready var cam := $Camera2D
func _ready() -> void:
    cam.make_current()
    cam.position_smoothing_enabled = true
    cam.position_smoothing_speed = 6.0           # higher = snappier; lower = floatier
    cam.limit_left = 0; cam.limit_top = 0        # clamp to the level rect (pixels)
    cam.limit_right = level_width; cam.limit_bottom = level_height
    cam.drag_horizontal_enabled = true           # built-in deadzone via drag margins
```

### 2. Frame-rate-independent smooth follow (when you hand-roll it)

```gdscript
# RIGHT: exponential smoothing — same feel at any FPS. `rate` ~ 5..12.
func _follow(dt: float) -> void:
    var t := 1.0 - exp(-rate * dt)               # converges correctly regardless of dt
    global_position = global_position.lerp(target.global_position, t)
# WRONG: global_position = global_position.lerp(target.global_position, 0.1)
#        → faster smoothing at higher FPS; different feel on every machine.
# Unity 6: Vector3.SmoothDamp(transform.position, target.position, ref vel, smoothTime) in
# LateUpdate gives the same spring behavior with built-in frame-rate correction.
```

### 3. Deadzone + look-ahead (lead the player, ignore jitter)

```gdscript
# Camera only chases once the target leaves the deadzone box, then aims AHEAD of motion.
func _camera_target(dt: float) -> Vector2:
    var to := target.global_position - _focus
    var dz := deadzone_half_extents                  # e.g. Vector2(48, 32)
    # Only move the focus by the overflow beyond the deadzone (per axis).
    _focus.x += clampf(absf(to.x) - dz.x, 0, INF) * signf(to.x)
    _focus.y += clampf(absf(to.y) - dz.y, 0, INF) * signf(to.y)
    var lead := target.velocity.normalized() * look_ahead_dist    # aim ahead of travel
    return _focus + lead
```

### 4. 3D third-person orbit with collision push-in

```gdscript
# Godot 4.x. Yaw/pitch a pivot; a SpringArm3D auto-pulls the camera in when blocked.
func _unhandled_input(e):
    if e is InputEventMouseMotion:
        _yaw -= e.relative.x * sensitivity
        _pitch = clampf(_pitch - e.relative.y * sensitivity, -1.2, 0.4)   # clamp pitch!
func _process(_dt):
    pivot.rotation = Vector3(_pitch, _yaw, 0)
    # $SpringArm3D handles wall collision: set spring_length + collision_mask; the child
    # Camera3D slides in automatically. RIGHT: spring arm. WRONG: camera clips through walls.
# Unity 6: a Cinemachine 3 CinemachineCamera (namespace Unity.Cinemachine) with an Orbital
# Follow + Cinemachine Deoccluder; the CinemachineBrain on the Camera blends automatically.
```

### 5. Screen shake hook (owned trigger lives in `game-feel`)

```gdscript
# Expose an additive offset the game-feel trauma model writes to; follow + shake compose.
var shake_offset := Vector2.ZERO                 # set each frame by game-feel (trauma^2 * noise)
func _apply(final_focus: Vector2) -> void:
    global_position = final_focus + shake_offset  # shake rides ON TOP of smooth follow
# Unity Cinemachine: add a CinemachineBasicMultiChannelPerlin and set amplitude from trauma.
```

## Pitfalls

- **`lerp(pos, target, const)` per frame** is frame-rate dependent — floatier at 30 FPS, snappier
  at 144. Use `1 - exp(-rate*dt)` or `SmoothDamp`.
- **Following in the normal update before the target has moved** yields a one-frame lag jitter.
  Follow in `LateUpdate` / after movement/physics resolve.
- **No bounds clamp** lets the camera show black past the level edge. Clamp focus to the level
  rect (account for the viewport half-size so the *view*, not the center, stays inside).
- **No deadzone in twitchy games** makes the camera twitch with every micro-movement → nausea.
- **Unclamped pitch** in third/first-person flips the camera over the top. Clamp pitch to ~±80°.
- **Camera clipping through walls** in 3D — use a spring arm / occlusion ray to pull in.
- **Snapping on teleport/respawn** is jarring; either hard-cut intentionally (and reset
  smoothing) or fast-ease. Don't let a huge `SmoothDamp` distance whip across the level.
- **Shake driving the follow target** instead of an additive offset makes follow fight shake.
  Compose: smooth follow first, add shake offset last.
- **Per-axis vs radial deadzone confusion** — a box deadzone feels different from a circular one;
  pick deliberately.

## References

- For the exponential-smoothing/spring derivation, a complete deadzone+look-ahead+bounds 2D rig,
  3D spring-arm/orbit details, first-person look, multi-target/group framing and split-screen,
  cinematic camera blends, and the Cinemachine 3 / Godot Camera2D / PhantomCamera mapping, read
  `references/follow-and-framing.md`.

## Related skills

- `game-feel` — owns screen-shake trauma/triggers; this skill exposes the offset it writes.
- `godot-2d-movement`, `godot-3d-essentials` — the player/world the camera frames; Camera3D setup.
- `physics-tuning` — interpolate camera follow with the physics step to kill jitter.
- `platformer`, `fps-shooter` — genres whose camera rules this skill implements.
- `performance-optimization` — cost of extra cameras, render targets, and split-screen.
