# MonoBehaviour lifecycle & coroutines (Unity 6)

Depth for the `unity-csharp-scripting` skill: the full execution order and the coroutine
patterns that don't fit in the main playbook. Verified against the Unity Manual
"Event function execution order" page and `ScriptReference/MonoBehaviour`.

## Execution order (the parts that matter for gameplay)

Per object, the engine calls these in this order:

| Phase | Callback | Runs | Use for |
|-------|----------|------|---------|
| Load | `Awake` | once, when the object loads (even if disabled) | cache `GetComponent`, set up self |
| Enable | `OnEnable` | each time the object/script enables | subscribe to events, re-arm coroutines |
| Init | `Start` | once, before first `Update`, after every `Awake` | wiring that depends on other objects |
| Physics | `FixedUpdate` | every fixed step (default 0.02s) | rigidbody forces, `MovePosition` |
| Physics | `OnTriggerXXX` / `OnCollisionXXX` | during the physics step | collision/trigger response |
| Frame | `Update` | once per rendered frame | input polling, non-physics logic |
| Frame | `LateUpdate` | once per frame, after all `Update`s | camera follow, IK fix-up |
| Disable | `OnDisable` | each time the object/script disables | unsubscribe from events |
| Teardown | `OnDestroy` | once, when destroyed | release native handles, save |

Key consequences:

- `FixedUpdate` may run zero, one, or several times per frame depending on frame rate. Never
  read raw "per frame" input there — read it in `Update`, consume it in `FixedUpdate`.
- All `Awake` calls finish before any `Start`. Order *among* `Awake`s (and among `Start`s) is
  undefined unless you set a Script Execution Order in Project Settings.
- `OnEnable` runs after `Awake` on first enable, then again on every re-enable. Pair every
  `OnEnable` subscription with an `OnDisable` unsubscription to avoid duplicate handlers.

## Coroutine yield instructions

```csharp
yield return null;                          // resume at the start of the next frame
yield return new WaitForSeconds(2f);        // wait 2s of scaled game time (affected by Time.timeScale)
yield return new WaitForSecondsRealtime(2f);// wait 2s of real time (ignores timeScale; good for pause menus)
yield return new WaitForFixedUpdate();      // resume after the next physics step
yield return new WaitUntil(() => isReady);  // resume once the predicate is true
yield return new WaitWhile(() => isLoading);// resume once the predicate is false
yield return StartCoroutine(OtherRoutine());// run a nested coroutine to completion first
```

## Stopping coroutines deterministically

Keep the handle so you can stop exactly the right routine:

```csharp
private Coroutine _spawnLoop;

private void OnEnable()  => _spawnLoop = StartCoroutine(SpawnLoop());
private void OnDisable() { if (_spawnLoop != null) StopCoroutine(_spawnLoop); }

private System.Collections.IEnumerator SpawnLoop()
{
    var wait = new WaitForSeconds(1f);      // allocate once, reuse — avoids per-iteration GC
    while (true)
    {
        Spawn();
        yield return wait;
    }
}
```

`StopAllCoroutines()` stops every coroutine on the MonoBehaviour — convenient but blunt;
prefer stopping by handle when multiple routines run on one object.

## Custom yield instruction

When you want a reusable wait condition:

```csharp
public class WaitForAnimationEnd : CustomYieldInstruction
{
    private readonly Animator _a;
    private readonly int _layer;
    public WaitForAnimationEnd(Animator a, int layer = 0) { _a = a; _layer = layer; }
    // keepWaiting == true means "keep yielding"; false resumes the coroutine.
    public override bool keepWaiting => _a.GetCurrentAnimatorStateInfo(_layer).normalizedTime < 1f;
}
```

## Gotchas

- Coroutines are killed when the GameObject is **deactivated** (`SetActive(false)`) or the
  script is destroyed — but *not* when only the script component is disabled while the object
  stays active. Re-arm in `OnEnable` if needed.
- A coroutine started from `Awake` will not advance past its first `yield` until the object is
  active and the script enabled. Prefer starting loops in `OnEnable`/`Start`.
- Allocating `new WaitForSeconds(x)` every loop iteration creates garbage; cache the instance.
