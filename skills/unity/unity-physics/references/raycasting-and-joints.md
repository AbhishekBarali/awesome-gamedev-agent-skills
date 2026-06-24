# Raycasting variants & joints (Unity 6 PhysX)

Depth for `unity-physics`. All types are in `UnityEngine`. Verified against
`ScriptReference/Physics` and the joint component pages.

## LayerMask bit math

A `LayerMask` is a 32-bit set of layers. Common constructions:

```csharp
int mask = LayerMask.GetMask("Ground", "Enemy");   // by name (recommended)
int onlyGround = 1 << LayerMask.NameToLayer("Ground");  // single layer by index
int everythingButPlayer = ~(1 << LayerMask.NameToLayer("Player"));  // invert
```

`Physics.Raycast(..., layerMask)` tests only layers whose bit is set. To *ignore* triggers
in a cast, pass `QueryTriggerInteraction.Ignore` as the last argument.

## Cast variants

```csharp
// Single nearest hit along a ray.
if (Physics.Raycast(origin, dir, out RaycastHit hit, maxDistance, mask)) { /* hit.point, hit.normal, hit.collider */ }

// Thick ray — good for "can a character-sized body pass?".
if (Physics.SphereCast(origin, radius, dir, out RaycastHit sHit, maxDistance, mask)) { }

// All hits along the ray (unordered) — e.g. shoot-through targets.
RaycastHit[] hits = Physics.RaycastAll(origin, dir, maxDistance, mask);

// Non-allocating versions write into a buffer you own (no GC each call) — prefer in hot paths.
private readonly RaycastHit[] _buffer = new RaycastHit[8];
int count = Physics.RaycastNonAlloc(origin, dir, _buffer, maxDistance, mask);

// Overlap tests (no direction): what is inside this volume right now?
Collider[] inRange = Physics.OverlapSphere(center, radius, mask);
```

Tips:
- `RaycastHit.normal` is the surface normal at the hit — use it to align decals or compute
  slope angle (`Vector3.Angle(hit.normal, Vector3.up)`).
- Prefer the `NonAlloc` / buffer overloads in per-frame code to avoid garbage.
- A ray starting *inside* a collider does not report that collider unless
  `Physics.queriesHitBackfaces` / start outside it.

## Joints

Joints connect two Rigidbodies (or a body to the world if `Connected Body` is empty).

| Joint | Constrains | Typical use |
|-------|-----------|-------------|
| `FixedJoint` | all 6 DOF (rigidly attaches) | weld parts that can break apart |
| `HingeJoint` | rotation about one axis, with motor/limits/spring | doors, wheels, pendulums |
| `SpringJoint` | distance via a spring | bungee, soft tethers |
| `ConfigurableJoint` | any combination of the 6 DOF | custom ragdoll/vehicle constraints |

```csharp
// A motorised hinge (e.g. a powered door).
var hinge = gameObject.AddComponent<HingeJoint>();
hinge.axis = Vector3.up;
hinge.useMotor = true;
hinge.motor = new JointMotor { force = 100f, targetVelocity = 90f /* deg/s */ };
```

### Breakable joints

```csharp
fixedJoint.breakForce  = 500f;     // newtons before the joint snaps
fixedJoint.breakTorque = 500f;
// When it breaks, the engine calls this on the GameObject:
private void OnJointBreak(float breakForce) => Debug.Log($"Joint broke at {breakForce}");
```

## Gotchas

- Joints simulate in `FixedUpdate`; setting joint properties is fine from `Update` but effects
  apply on the next physics step.
- A `ConfigurableJoint`'s locked/limited axes are relative to the joint's initial orientation —
  set up the bodies in their rest pose before adding the joint.
- Very stiff joints + high mass ratios are unstable; increase `Default Solver Iterations`
  (Project Settings → Physics) before fighting it with bigger forces.
