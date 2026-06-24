---
name: unity-csharp-scripting
description: >
  Write Unity 6 C# gameplay scripts: the MonoBehaviour lifecycle
  (Awake/OnEnable/Start/Update/FixedUpdate/LateUpdate), GameObject and component
  access, coroutines, and Inspector serialization. Use when creating or editing .cs
  scripts in a Unity project, or when the user mentions MonoBehaviour, Start/Update,
  GetComponent, SerializeField, coroutines, or "Unity script".
license: Apache-2.0
compatibility: Unity 6 (6000.0 LTS); also valid for 2022 LTS
metadata:
  engine: unity
  category: unity
  difficulty: beginner
---

# Unity C# Scripting (MonoBehaviour)

Write correct, idiomatic gameplay scripts in Unity 6. Get the lifecycle, component
access, serialization, and coroutines right so behaviour is deterministic and the
Inspector stays useful. Targets **Unity 6 (6000.0 LTS)**, C# / .NET Standard 2.1.

## When to use

- Use when authoring or fixing a `MonoBehaviour`: choosing the right lifecycle callback,
  reading/caching components, exposing fields to the Inspector, or running timed logic
  with coroutines.
- Use when the project has `*.cs` files, an `Assembly-CSharp` or `*.asmdef`, and a
  `ProjectSettings/` folder.

**When *not* to use:** moving rigidbodies / collision response → `unity-physics`; reading
player input → `unity-input-system`; shared data assets / config → `unity-scriptableobjects`;
Animator parameters → `unity-animation`. This skill owns the *script lifecycle and C#
plumbing*, not those subsystems.

## Core workflow

1. **Pick the callback by purpose, not habit.** `Awake` (cache references, runs once on
   load), `OnEnable` (subscribe to events), `Start` (init that depends on other objects'
   `Awake`), `Update` (per-frame logic/input polling), `FixedUpdate` (physics), `LateUpdate`
   (camera follow after movement), `OnDisable`/`OnDestroy` (unsubscribe/cleanup).
2. **Cache component lookups in `Awake`** — never call `GetComponent` every frame.
3. **Expose tunables with `[SerializeField] private`**, not public fields, so other code
   can't mutate them but designers can edit them in the Inspector.
4. **Scale per-frame values by `Time.deltaTime`** in `Update` (and `Time.fixedDeltaTime`
   semantics are automatic in `FixedUpdate`).
5. **Use coroutines for time-sequenced logic** (delays, tweens, "do X then wait then Y");
   start them with `StartCoroutine` and stop them deterministically.
6. **Verify in Play mode**: check the Console for null-reference exceptions, confirm values
   in the Inspector update as expected, and watch the Profiler if `Update` is hot.

## Patterns

### 1. Lifecycle + cached components (the canonical skeleton)

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]      // auto-adds the dependency, prevents null refs
public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 6f;   // editable in Inspector, private in code
    private Rigidbody _rb;                            // cached, not fetched per frame

    private void Awake() => _rb = GetComponent<Rigidbody>();  // cache once on load

    private void Update()
    {
        // Per-frame, non-physics work. Scale by deltaTime so it is frame-rate independent.
        transform.Rotate(0f, 90f * Time.deltaTime, 0f);
    }

    private void FixedUpdate()
    {
        // Physics work belongs here (fixed timestep). See the unity-physics skill.
        _rb.MovePosition(_rb.position + transform.forward * moveSpeed * Time.fixedDeltaTime);
    }
}
```

### 2. Safe component access with `TryGetComponent`

```csharp
// Avoids allocating a null and is clearer than GetComponent + null check.
if (other.TryGetComponent<Health>(out var health))
    health.Apply(-10);
```

### 3. Serialization that shows up correctly in the Inspector

```csharp
[SerializeField, Range(0f, 1f)] private float volume = 0.8f;  // slider
[SerializeField] private string playerName = "Hero";          // private but serialized

[System.Serializable]                 // REQUIRED for a plain class to serialize/show
public class Stats { public int hp = 100; public int mana = 50; }

[SerializeField] private Stats stats = new();  // nested struct-like data in the Inspector
```

### 4. Coroutines for time-sequenced logic

```csharp
private void Start() => StartCoroutine(FlashThenHide());

private System.Collections.IEnumerator FlashThenHide()
{
    yield return new WaitForSeconds(0.5f);   // wait half a second of game time
    GetComponent<Renderer>().enabled = false;
    yield return null;                       // resume next frame
}
```

## Pitfalls

- **`GetComponent` in `Update`** — it searches every frame and tanks performance. Cache the
  reference in `Awake`/`Start`.
- **Physics in `Update`** — moving a `Rigidbody` with forces or `MovePosition` outside
  `FixedUpdate` causes jitter and timestep-dependent behaviour. Read input in `Update`,
  apply physics in `FixedUpdate`.
- **Relying on `Start` order across objects** — `Start` runs after *all* `Awake`s, but order
  among `Start`s is undefined. Do cross-object wiring in `Start`, self-setup in `Awake`.
- **`public` fields just to show them in the Inspector** — that also lets any script mutate
  them. Use `[SerializeField] private` instead.
- **`gameObject.tag == "Enemy"`** allocates a string and is slower; use
  `gameObject.CompareTag("Enemy")`.
- **Coroutines stop when the GameObject is disabled** — a disabled object's coroutines are
  killed; re-`StartCoroutine` in `OnEnable` if it must survive toggling.
- **`Update` runs before `Start` never happens, but the *first* `Update` can run the same
  frame as `Start`** — guard against not-yet-initialised fields if you split setup oddly.

## References

- For the full event-execution-order table and advanced coroutine patterns (custom
  `CustomYieldInstruction`, stopping by handle, `WaitUntil`/`WaitWhile`), read
  `references/lifecycle-and-coroutines.md`.
- Primary docs: Unity Manual "Event function execution order"
  (`https://docs.unity3d.com/Manual/execution-order.html`) and `ScriptReference/MonoBehaviour`.

## Related skills

- `unity-physics` — `Rigidbody`, collisions, and `FixedUpdate` motion.
- `unity-input-system` — reading player input into these scripts.
- `unity-scriptableobjects` — sharing data/config between scripts without singletons.
