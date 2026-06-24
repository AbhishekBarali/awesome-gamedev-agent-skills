---
name: unity-physics
description: >
  Set up 3D physics in Unity 6: Rigidbody movement and forces, colliders, triggers vs
  collisions, layer-based collision, raycasts, and joints. Use when adding a Rigidbody,
  handling OnCollisionEnter/OnTriggerEnter, tuning collision layers, casting rays, or when
  the user mentions Unity physics, AddForce, isKinematic, or linearVelocity.
license: Apache-2.0
compatibility: Unity 6 (6000.0 LTS), built-in PhysX. Note the velocity → linearVelocity rename.
metadata:
  engine: unity
  category: unity
  difficulty: intermediate
---

# Unity Physics (Rigidbody / PhysX)

Make objects move, collide, and detect each other with Unity 6's built-in 3D physics
(PhysX). Get the `FixedUpdate` discipline, trigger-vs-collision rules, and collision layers
right. Targets **Unity 6 (6000.0 LTS)**.

> **Unity 6 rename:** `Rigidbody.velocity` is now **`Rigidbody.linearVelocity`** (the old
> name is deprecated). Code copied from older tutorials will warn or fail to compile.

## When to use

- Use when giving an object physical motion (forces, velocity, gravity), responding to
  collisions or triggers, setting up collision layers/masks, raycasting for ground checks or
  line-of-sight, or connecting bodies with joints.
- Use when scenes/prefabs contain `Rigidbody` + `Collider` components.

**When *not* to use:** 2D physics (`Rigidbody2D`, `Collider2D`) is a separate API — adapt the
concepts but the types differ. Cross-engine *feel* tuning (timestep, jitter, tunnelling) →
`physics-tuning`. Reading input that drives movement → `unity-input-system`.

## Core workflow

1. **Add a `Rigidbody`** to anything that should be simulated; add a `Collider` to anything
   that should be hit. A collision needs a `Collider` on both, and at least one `Rigidbody`.
2. **Do all physics in `FixedUpdate`.** Read input in `Update`, store intent, then apply
   forces / set `linearVelocity` / call `MovePosition` in `FixedUpdate`.
3. **Move bodies through the physics API, not the Transform.** Use `AddForce`,
   `linearVelocity`, or `MovePosition` — never assign `transform.position` to a non-kinematic
   Rigidbody (it teleports and breaks collision resolution).
4. **Pick collision vs trigger.** A solid collision blocks and calls `OnCollisionEnter`; a
   `Collider` with `Is Trigger` checked passes through and calls `OnTriggerEnter`.
5. **Organise interactions with layers.** Put objects on layers and edit the Layer Collision
   Matrix (Project Settings → Physics) so unrelated things don't test against each other.
6. **Verify** with the Physics Debugger (Window → Analysis → Physics Debugger) and by watching
   for jitter; if fast objects pass through walls, raise Collision Detection mode.

## Patterns

### 1. Force-based movement in `FixedUpdate` (with a speed clamp)

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class Mover : MonoBehaviour
{
    [SerializeField] private float accel = 30f, maxSpeed = 8f;
    private Rigidbody _rb;
    private Vector3 _input;   // set from Update / input system

    private void Awake() => _rb = GetComponent<Rigidbody>();

    private void FixedUpdate()
    {
        _rb.AddForce(_input * accel, ForceMode.Acceleration);     // mass-independent accel
        // Unity 6: linearVelocity (was 'velocity'). Clamp horizontal speed.
        Vector3 flat = new(_rb.linearVelocity.x, 0, _rb.linearVelocity.z);
        if (flat.magnitude > maxSpeed)
        {
            flat = flat.normalized * maxSpeed;
            _rb.linearVelocity = new Vector3(flat.x, _rb.linearVelocity.y, flat.z);
        }
    }
}
```

`ForceMode`: `Force` (continuous, mass-scaled), `Acceleration` (continuous, ignores mass),
`Impulse` (instant, mass-scaled — jumps), `VelocityChange` (instant, ignores mass).

### 2. Collision vs trigger callbacks

```csharp
// Solid hit: both have colliders, this one has a (non-kinematic) Rigidbody.
private void OnCollisionEnter(Collision col)
{
    Debug.Log($"Hit {col.gameObject.name} at {col.contacts[0].point}");
}

// Overlap: one collider has 'Is Trigger' = true. Requires a Rigidbody on at least one party.
private void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Pickup")) Destroy(other.gameObject);
}
```

### 3. Ground check with a layer-masked raycast

```csharp
[SerializeField] private LayerMask groundMask;   // set to your "Ground" layer in the Inspector

private bool IsGrounded()
{
    // Cast a short ray down; only test colliders on groundMask.
    return Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit,
                           1.1f, groundMask);
}
```

### 4. Kinematic platform that still pushes bodies

```csharp
// isKinematic Rigidbody: not driven by forces, but MovePosition interpolates and carries
// resting bodies correctly (unlike moving the Transform directly).
private void FixedUpdate() => _rb.MovePosition(_rb.position + Vector3.right * (2f * Time.fixedDeltaTime));
```

## Pitfalls

- **`Rigidbody.velocity` doesn't exist in Unity 6** — use `linearVelocity` (and
  `angularVelocity` is unchanged).
- **Setting `transform.position` on a dynamic Rigidbody** — teleports it, skips collision.
  Use `MovePosition` (kinematic/interpolated) or apply forces.
- **Applying forces in `Update`** — frame-rate-dependent and jittery. Physics goes in
  `FixedUpdate`.
- **Trigger callbacks never fire** — triggers need a `Rigidbody` on at least one of the two
  colliders, and both colliders enabled; two static triggers don't report overlaps.
- **Fast objects pass through walls (tunnelling)** — set the Rigidbody's Collision Detection
  to `Continuous` (or `Continuous Dynamic`) for bullets/fast movers.
- **Non-uniform-scaled `MeshCollider`s or scaled colliders** misbehave; prefer primitive
  colliders and keep scale uniform.
- **Everything collides with everything** — wasted cost; assign layers and prune the Layer
  Collision Matrix.

## References

- For raycast variants (`SphereCast`, `RaycastAll`, `OverlapSphere`, `LayerMask` bit math) and
  joints (`FixedJoint`, `HingeJoint`, `ConfigurableJoint`, breakable joints), read
  `references/raycasting-and-joints.md`.
- Primary docs: Unity Manual "Physics" section and `ScriptReference/Rigidbody`,
  `ScriptReference/Physics.Raycast`.

## Related skills

- `physics-tuning` — engine-agnostic feel: fixed timestep, mass/drag, CCD, stability.
- `unity-csharp-scripting` — the `FixedUpdate`/`Update` split these patterns rely on.
- `unity-navmesh` — agent movement that is *not* force-driven.
