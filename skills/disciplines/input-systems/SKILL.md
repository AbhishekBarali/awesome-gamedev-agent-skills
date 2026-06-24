---
name: input-systems
description: >
  Architect game input — action mapping (abstracting keys into named actions),
  rebinding with conflict detection and persistence, multi-device support
  (keyboard, gamepad, touch), analog deadzones, and feel features like input
  buffering and coyote time, plus accessibility. Engine-neutral. Use when the
  user mentions input mapping, rebind controls, gamepad support, deadzone, input
  buffering, coyote time, or accessible controls.
license: Apache-2.0
compatibility: Engine-agnostic. Pairs with unity-input-system, unreal-enhanced-input, and Godot InputMap; snippets in GDScript-like pseudocode.
metadata:
  engine: none
  category: disciplines
  difficulty: intermediate
---

# Input systems

Never wire gameplay to raw keys. Map physical inputs (a key, a button, a touch)
to named **actions** (`jump`, `interact`, `move`), and let gameplay read actions.
That one indirection gives you rebinding, multi-device support, and accessibility
almost for free. This skill is the engine-neutral architecture; bind it to
`unity-input-system`, `unreal-enhanced-input`, or Godot's `InputMap`.

## When to use

- Use to design an input layer: actions, bindings, multiple devices, and a
  rebinding UI with conflict detection and saved bindings.
- Use to add analog handling (deadzones, sensitivity) and game-feel features
  (input buffering, coyote time).
- Use to make controls accessible (full remapping, hold-vs-toggle, sensitivity,
  no required simultaneous presses).

**When *not* to use:** for an engine's concrete input package/API, use
`unity-input-system`, `unreal-enhanced-input`, or Godot's InputMap. For the
movement/jump *physics* the buffer feeds, see `physics-tuning` and the engine
movement skill. Persisting bindings to disk is `save-systems`.

## Core workflow

1. **Define actions, not keys.** Gameplay asks "is `jump` pressed?", never "is
   Space pressed?". Actions are the stable contract; bindings are data.
2. **Bind per device.** Each action holds bindings for keyboard, gamepad, and
   touch. The active device is whichever last sent input; swap UI prompts to match.
3. **Read the right edge.** Use *pressed-this-frame* (edge) for discrete actions
   (jump, interact) and *held* (level) for continuous ones (move, aim). Confusing
   the two causes double-fires or missed presses.
4. **Filter analog input.** Apply a deadzone to sticks/triggers so resting drift
   reads as zero, and scale sensitivity/curve to taste.
5. **Buffer for feel.** Remember a pressed action for a short window so a slightly
   early press still fires (input buffering); allow a jump shortly after leaving a
   ledge (coyote time).
6. **Make rebinding first-class.** A UI that captures the next input, detects
   conflicts, and persists bindings — and a reset-to-default. Save via
   `save-systems`.
7. **Verify on every device** and with rebinds: keyboard, gamepad, touch; rebind
   an action mid-game and confirm gameplay and prompts follow.

## Patterns

### 1. Actions over raw keys; edge vs held

```gdscript
# Gameplay reads ACTIONS. The mapping from key/button to action lives in data.
# Discrete (edge): fire once on the press frame.
if Input.is_action_just_pressed("jump"):
    try_jump()
# Continuous (held): read every frame as an axis.
var move := Input.get_axis("move_left", "move_right")   # -1..1
player.velocity.x = move * RUN_SPEED
# RIGHT: name actions ("jump"); rebinding/devices just change the binding data.
# WRONG: `if Input.is_key_pressed(KEY_SPACE)` — unrebindable, keyboard-only,
# and `is_key_pressed` is a held check that would re-fire jump every frame.
```

Engine equivalents: Godot `InputMap` + `Input.is_action_just_pressed`; Unity
Input System `InputAction` / action maps; Unreal Enhanced Input `Input Actions` +
`Input Mapping Contexts`.

### 2. Analog deadzone and sensitivity

```gdscript
# Raw sticks never rest at exactly zero. Apply a RADIAL deadzone (on the vector
# length), not per-axis, so diagonals aren't clipped into the axes.
func apply_deadzone(stick: Vector2, dead := 0.2, sens := 1.0) -> Vector2:
    var mag := stick.length()
    if mag < dead:
        return Vector2.ZERO                      # inside deadzone -> no movement
    # Rescale so motion ramps from 0 at the edge of the deadzone, not from `dead`.
    var scaled := (mag - dead) / (1.0 - dead)
    return stick.normalized() * pow(scaled, sens)  # sens>1 = finer near center
# WRONG: clamping each axis separately — it carves a square hole and snaps to axes.
```

### 3. Input buffering + coyote time (forgiving, responsive feel)

```gdscript
# Buffer: a jump pressed slightly BEFORE landing still triggers on touchdown.
# Coyote: a jump pressed slightly AFTER walking off a ledge still works.
const BUFFER := 0.12   # seconds an early press stays "remembered"
const COYOTE := 0.10   # seconds after leaving ground you can still jump
var _buffer_timer := 0.0
var _coyote_timer := 0.0

func _physics_process(dt):
    _buffer_timer -= dt
    _coyote_timer = COYOTE if is_on_floor() else _coyote_timer - dt
    if Input.is_action_just_pressed("jump"):
        _buffer_timer = BUFFER                  # remember the press
    if _buffer_timer > 0.0 and _coyote_timer > 0.0:
        velocity.y = JUMP_VELOCITY
        _buffer_timer = 0.0; _coyote_timer = 0.0  # consume both so it fires once
```

### 4. Rebinding with conflict detection

```gdscript
# Capture the next physical input, reject duplicates, then persist.
func rebind(action: String, event: InputEvent) -> bool:
    for other in actions:                        # conflict check across actions
        if other != action and binding_of(other) == event:
            return false                         # already used -> let UI warn/swap
    set_binding(action, event)                   # engine: erase old + add new event
    save_bindings()                              # persist (see save-systems)
    return true
# Always provide "reset to defaults", and never let the player unbind a key they
# need to reach the menu without an alternative.
```

## Pitfalls

- **Hardcoding keys** in gameplay blocks rebinding, locks out gamepad/touch, and
  scatters input logic. Read named actions only.
- **Edge vs held confusion**: using a held check for jump re-fires every frame;
  using an edge check for movement drops held input. Match the check to the action.
- **Per-axis deadzones** clip diagonal stick input and snap movement to the axes.
  Use a radial deadzone on the vector magnitude.
- **No buffering/coyote time** makes tight platformers feel unfair even when the
  physics are correct — players "clearly pressed jump". Add small windows.
- **Rebinding without conflict handling** lets two actions share a key, or strands
  the player by unbinding menu access. Detect conflicts; guarantee a way back.
- **Not swapping prompts on device change** shows "Press Space" to a gamepad
  player. Track the last-used device and switch glyphs.
- **Ignoring accessibility**: required simultaneous presses, no remap, fixed
  sensitivity, hold-only actions. Offer remap, toggle-vs-hold, and sensitivity.
- **Reading input in the wrong loop**: poll held state in the physics step for
  consistent movement; capture discrete presses so none are missed between frames.

## References

- `references/buffering-and-accessibility.md` — buffering/coyote tuning, jump feel
  (variable height, apex), device detection and prompt swapping, touch controls,
  and an accessibility checklist (remap, toggle/hold, sensitivity, latency).

## Related skills

- `unity-input-system`, `unreal-enhanced-input` — concrete engine input APIs
  (Godot uses `InputMap` + the `Input` singleton).
- `save-systems` — persist custom key bindings and input settings.
- `physics-tuning` — the movement the buffer/coyote windows feed into.
- `platformer`, `fps-shooter` — genres whose feel depends on input handling.
