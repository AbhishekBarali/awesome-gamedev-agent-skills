---
name: fps-shooter
description: >
  Build a first-person shooter: move+mouse-look controller, hitscan or projectile shooting, weapons,
  health, and enemy AI. Use for an FPS, or tuning aim feel, time-to-kill, recoil, or spread.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: advanced
---

# FPS Shooter

A playbook for first-person shooters — the look/move controller, the shooting model, weapon
feel, and combat. This is a **compositional** skill: it wires a 3D controller, input, and AI
into a shooter. It does not re-teach 3D nodes or raycasts; it defines the shooting model and
the feel knobs (TTK, recoil, spread) that decide whether the guns feel good.

## When to use

- Use when building a first-person game whose core verb is **aim and shoot** — arena shooter,
  tactical FPS, PvE shooter, boomer-shooter.
- Use when deciding hitscan vs. projectile, tuning time-to-kill, recoil, spread, or aim feel.

**When *not* to use:** third-person/2D shooting → reuse the shooting model here but build the
camera/controller from the relevant genre. Wave survival with towers → `tower-defense`.
For the camera/character body itself, use `godot-3d-essentials` / `unreal-cpp-gameplay`.

## Core loop

**Scan → acquire a target → aim and fire → confirm the kill (feedback) → reposition / reload
/ advance.** The whole experience rests on the *aim-and-fire* micro-loop feeling crisp:
responsive look, clear hit feedback, and a death that reads instantly.

## Must-have systems

1. **First-person controller** — move (WASD/stick) + mouse/stick look, gravity, jump/crouch.
2. **Camera** — eye-height view, configurable FOV and sensitivity, recoil kick.
3. **Shooting model** — hitscan raycast and/or projectile spawn; one impact path for feedback.
4. **Weapons + ammo** — damage, fire rate, magazine, reload, switching.
5. **Health + damage** — HP, hit/headshot multipliers, death; player and enemy share the model.
6. **Enemy AI** — perceive → alert → attack → search; cover and reaction delays (`game-ai`).
7. **Feedback** — hitmarkers, impact decals/particles, hit sounds, screen shake, kill confirms.
8. **Objectives** — what you do besides shoot: clear, capture, survive, escort.

## Design knobs

| Knob | Effect | Sane default |
|------|--------|--------------|
| Time-to-kill (TTK) | lethality, forgiveness | Tune dmg × fire-rate × HP together (refs). |
| Hitscan vs projectile | aim skill type | Hitscan = flick; projectile = lead/dodge. |
| Damage falloff | range limiting | Full to ~20 m, floor by ~60 m. |
| Headshot multiplier | skill reward | ~1.5–2.0×. |
| Recoil pattern | learnable kick | Fixed pattern > pure random. |
| Spread (bloom) | suppress laser-accuracy | First shot accurate; grows while firing. |
| Fire rate / magazine / reload | rhythm, downtime | Reload = vulnerability window. |
| Mouse sensitivity / FOV | comfort, readability | Always expose both as options. |
| Aim assist (pad) | controller parity | Magnetism/slowdown near targets. |

## Patterns

### 1. Hitscan shot (instant ray, the workhorse)

```python
# Pseudocode. Cast from the camera; first hit takes damage scaled by range + headshot.
direction = apply_spread(camera.forward, current_spread)
hit = raycast(camera.world_position, direction, max_dist=RANGE, mask=SHOOTABLE)
if hit:
    dmg = base_damage * falloff(hit.distance)
    if hit.is_head: dmg *= HEADSHOT_MULT
    hit.actor.take_damage(dmg)
    spawn_impact_fx(hit.point, hit.normal)        # decal + sound + hitmarker
```

### 2. Projectile shot (dodgeable, leads the target)

```python
# Pseudocode. Spawn a moving body; it deals damage on its own collision.
p = spawn(projectile_scene, at=muzzle.world_position)
p.velocity = camera.forward * PROJECTILE_SPEED
p.on_hit   = lambda other, point: (other.take_damage(base_damage), explode_fx(point))
p.lifetime = RANGE / PROJECTILE_SPEED             # despawn so shots don't live forever
```

### 3. Time-to-kill (balance the trio together)

```python
# Pseudocode. TTK falls out of HP, per-shot damage, and fire rate — tune as one system.
shots_to_kill = ceil(target_hp / damage_per_shot)
ttk_seconds   = (shots_to_kill - 1) / fire_rate_per_second   # first shot at t=0
```

## Pitfalls / failure modes

- **Look tied to frame rate or unscaled by `dt`** → sensitivity changes with FPS. Look should
  be driven by raw mouse delta; movement integration uses `dt` (see `physics-tuning`).
- **Pure random recoil/spread** → feels uncontrollable and unfair. Use a learnable recoil
  pattern; keep the first shot accurate.
- **Hitscan with no falloff** → pistols snipe across the map. Add range-based damage falloff.
- **No hit feedback** → players can't tell if shots land. Always show hitmarkers, impact FX, and
  a distinct kill confirm.
- **Mismatched TTK** → too low feels twitchy/unfair; too high feels spongy. Tune damage,
  fire rate, and HP as one system (Pattern 3).
- **Trusting the client in multiplayer** → cheating and "I shot first" disputes. Keep authority
  server-side; use lag compensation (refs) and defer netcode to the engine multiplayer skill.
- **No FOV / sensitivity options** → motion sickness and accessibility failures. Always expose them.

## Composition (build it from these skills)

- **Controller + camera:** `godot-3d-essentials` (Godot) or `unreal-cpp-gameplay` / `unreal-blueprints`; Unity uses `unity-physics` + a character controller.
- **Input:** `input-systems` (or `unreal-enhanced-input`) for look/move, rebinding, and gamepad aim assist.
- **Shooting physics:** `godot-physics` / `unity-physics` for raycasts and projectile collision.
- **Enemies:** `game-ai` with `unity-navmesh` / `unreal-behavior-trees` / Godot navigation.
- **Camera & feel:** `camera-systems` for FOV/recoil kick and look smoothing; `game-feel` for hit-stop, screen shake, and impact juice.
- **Polish:** `audio-design` for weapon/impact sound; `shader-programming` for muzzle/impact VFX.
- **Process:** `prototype-fast` to validate aim feel before building content.

## References

- For hitscan vs. projectile trade-offs, damage falloff, recoil/spread, TTK math, hit
  registration/lag compensation, and enemy AI states, read `references/shooting-and-feel.md`.
