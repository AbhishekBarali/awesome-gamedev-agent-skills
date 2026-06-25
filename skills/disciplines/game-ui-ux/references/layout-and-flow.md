# Layout, scaling & flow — depth for `game-ui-ux`

Detail the `game-ui-ux` body defers here: per-engine scaling modes, safe-area math, a complete
focus + screen-stack pattern, diegetic UI, accessibility, and localization-ready layout. Snippets
target **Godot 4.x** and **Unity 6**.

## 1. Scaling modes per engine

**Godot 4.x** (Project Settings → Display → Window → Stretch):

| Setting | Choose | Effect |
|---------|--------|--------|
| Mode | `canvas_items` | UI scales with the window (vs `viewport` = pixel-exact, `disabled` = none) |
| Aspect | `expand` | shows more world/UI space on odd ratios; `keep` letterboxes |
| Scale | `1.0`+ | global UI multiplier |

Anchor HUD corners so `expand` puts the extra space where you want it. `keep_width`/`keep_height`
pin one axis for hard 16:9 designs.

**Unity 6** (`CanvasScaler` on each Canvas):

- `UI Scale Mode = Scale With Screen Size`.
- `Reference Resolution = 1920×1080` (or your art's design size).
- `Screen Match Mode = Match Width Or Height`, `Match = 0.5` (blend). Use `1.0` if vertical
  layout must never clip, `0.0` if horizontal must not.
- `Reference Pixels Per Unit = 100` for sprite-based UI.

## 2. Safe-area math

The OS reports a safe rectangle inside the screen (excludes notch, rounded corners, and — on TVs
— overscan margins). Inset only **critical** UI (health, timers, prompts); decorative art can
bleed to the edge.

```text
# Normalized anchors from a pixel safe rect (engine-neutral):
anchorMin = (safe.x / screenW,                 safe.y / screenH)
anchorMax = ((safe.x + safe.w) / screenW,       (safe.y + safe.h) / screenH)
# Re-apply on resolution change / orientation change, not once at startup.
```

- **Godot:** `DisplayServer.get_display_safe_area()` → `Rect2i` in pixels; reapply on
  `size_changed`.
- **Unity:** `Screen.safeArea` → `Rect` in pixels; recompute when `Screen.width/height` or
  `Screen.orientation` changes (cache the last applied rect to avoid per-frame work).

## 3. Focus navigation (full pattern)

Requirements for controller/keyboard usability:

1. **Initial focus** on every screen open (`grab_focus()` / `EventSystem.SetSelectedGameObject`).
2. **Explicit neighbors** for predictable movement (Godot `focus_neighbor_*`; Unity `Navigation`
   = Explicit with up/down/left/right, or Automatic for simple grids).
3. **Visible focus style** distinct from hover (theme focus stylebox / Unity Selectable
   transition). Never rely on color alone (see accessibility).
4. **Wrap or stop** intentionally at list ends; trap focus inside modal dialogs.
5. **Device coexistence:** moving the mouse can update selection; a gamepad press acts on the
   focused control. Don't clear focus when the mouse moves.

```gdscript
# Godot 4.x: trap focus inside a modal so the stick can't escape to the game behind it.
func open_modal() -> void:
    _prev_focus = get_viewport().gui_get_focus_owner()
    $Modal.show(); $Modal/OK.grab_focus()
func close_modal() -> void:
    $Modal.hide()
    if is_instance_valid(_prev_focus): _prev_focus.grab_focus()
```

## 4. Screen/menu stack

Model screens as a stack of UI states; the top owns input and is visible. Push for overlays,
pop for "back". This generalizes pause, settings-over-pause, and confirm dialogs.

```gdscript
# Godot 4.x sketch (a CanvasLayer per screen; pausing the tree under an overlay):
var _stack: Array[Control] = []
func push(screen: Control) -> void:
    if _stack.size() > 0: _stack.back().set_process_input(false)
    _stack.append(screen); add_child(screen); screen.grab_focus_default()
func pop() -> void:
    var top := _stack.pop_back(); top.queue_free()
    if _stack.size() > 0:
        _stack.back().set_process_input(true); _stack.back().grab_focus_default()
# Pause overlay: get_tree().paused = true and set the overlay's process_mode = ALWAYS.
```

This mirrors the state-stack idea in `love2d-core`'s `references/state-stack.md`, applied to UI.

## 5. Diegetic vs non-diegetic UI

- **Non-diegetic:** drawn on the screen plane, outside the fiction (most HUDs). Cheapest, clearest.
- **Diegetic:** UI that exists in the world (ammo counter on the gun, health on the suit). More
  immersive, more work, can hurt readability. Use for key elements, keep a non-diegetic fallback.
- **Spatial/world-space:** floating health bars, damage numbers — anchor to world position,
  clamp to screen edges when off-screen, and scale with distance (3D).

## 6. Accessibility (bake in, don't bolt on)

- **Text size option** and never hardcode tiny fonts; size to a percentage of reference height.
- **Contrast & color independence:** don't encode state in color alone — add icon/shape/text.
  Provide colorblind-safe palettes.
- **Scalable hit targets** for touch (≥ ~9 mm); padding around small buttons.
- **Reduce-motion / reduce-flashing** toggles (coordinate with `game-feel`).
- **Full keyboard + gamepad** reachability (section 3); don't gate actions behind mouse-only.

## 7. Localization-ready layout

- Externalize strings (Godot `tr()` + translation CSV/PO; Unity Localization package). Never bake
  display text into layout logic.
- Let containers **size to content** so longer translations (German is ~30% longer) don't clip.
  Avoid fixed-width buttons sized to English.
- Leave room for RTL mirroring and different number/date formats.
- Keep icons separate from text so only strings need translating.
