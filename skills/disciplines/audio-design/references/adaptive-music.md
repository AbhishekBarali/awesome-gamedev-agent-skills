# Adaptive (dynamic) music

Adaptive music changes with gameplay instead of looping one track. Two techniques
dominate, and they combine:

- **Vertical layering (re-orchestration)** — several stems (drums, bass, melody,
  tension pad) play in sync; you fade layers in/out to change intensity without
  changing the underlying loop. Seamless because all layers share the same
  timeline.
- **Horizontal re-sequencing** — the track is split into segments (intro, loop A,
  loop B, combat, outro); you switch which segment plays next, transitioning at
  musical boundaries (bar/phrase) so the change lands on beat.

## Vertical layering

All layers are the same length and start together; only their volumes change.

```gdscript
# Keep N stem players in sync (same position), and fade volumes by intensity.
var layers := { "base": p_base, "drums": p_drums, "tension": p_tension }

func start_layers() -> void:
    for p in layers.values():
        p.volume_db = -80.0       # start silent
        p.play()                  # all begin together -> stay sample-aligned
    layers["base"].volume_db = 0.0

func set_intensity(level: int) -> void:   # 0 calm .. 2 combat
    _fade(layers["drums"],   0.0 if level >= 1 else -80.0)
    _fade(layers["tension"], 0.0 if level >= 2 else -80.0)

func _fade(p, target_db: float, t := 0.8) -> void:
    create_tween().tween_property(p, "volume_db", target_db, t)
```

Tips: author stems at the same BPM/length and bounce them aligned. Fades of
~0.5–1.5 s feel musical; instant cuts feel mechanical. Because layers never
restart, intensity can change any time without losing sync.

## Horizontal re-sequencing

Switch segments at safe musical points so transitions don't sound abrupt.

```gdscript
# Request a section change; apply it only at the next bar boundary.
var pending_section := ""
const BPM := 120.0
const BEATS_PER_BAR := 4
var sec_per_bar := 60.0 / BPM * BEATS_PER_BAR

func request_section(name: String) -> void:
    pending_section = name        # don't switch mid-bar; queue it

func on_bar_boundary(pos: float) -> void:
    if pending_section != "":
        crossfade_to(pending_section, 0.2)   # short crossfade across the seam
        pending_section = ""
```

Transition strategies, roughly increasing in polish:

- **Immediate crossfade** — quick volume blend; fine for low-stakes changes.
- **Quantized switch** — wait for the next beat/bar/phrase, then switch. The
  default for music that should stay "in time".
- **Transition segments** — short bridge clips written to connect A→B musically.
- **Stingers** — one-shot musical accents layered over the bed for events (boss
  appears, secret found) without altering the loop.

## Mapping gameplay to intensity

Drive the music from a small, smoothed intensity value rather than raw events:

```gdscript
# Combine signals into 0..1, smooth it, then map to layers/sections with hysteresis.
func intensity_from_state(enemies_near: int, player_hp01: float) -> float:
    var raw = clamp(enemies_near / 5.0, 0.0, 1.0) * (1.0 - 0.4 * player_hp01)
    intensity = lerp(intensity, raw, 0.05)   # smooth so it doesn't flicker
    return intensity

# Hysteresis: require crossing different thresholds up vs down so the music
# doesn't oscillate when intensity hovers at a boundary.
func level_from_intensity(i: float, current: int) -> int:
    if current < 1 and i > 0.6: return 1
    if current >= 1 and i < 0.4: return 0
    return current
```

## Practical notes

- **Drive timing from the audio clock**, not frame delta, and account for output
  latency when scheduling.
- **Loop points** must be sample-accurate; gaps or clicks betray the seam. Author
  loops to bar boundaries and test the wrap.
- **Middleware** (FMOD, Wwise) implements layering, quantized transitions, and
  parameter-driven intensity natively — reach for it when the music system grows
  beyond a handful of stems/segments.
- **Budget**: many simultaneous stems cost voices and memory. Stream long music;
  keep stem counts modest on low-end targets.
