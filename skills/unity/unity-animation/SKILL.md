---
name: unity-animation
description: >
  Drive Unity 6 character animation with Animator Controllers: states, transitions,
  parameters, blend trees, animation layers, and humanoid Avatar IK. Use when wiring an
  Animator, setting parameters from script (SetFloat/SetBool/SetTrigger), building blend
  trees, or when the user mentions Animator, Mecanim, state machine, blend tree, or .controller.
license: Apache-2.0
compatibility: Unity 6 (6000.0 LTS); Animator / Mecanim, humanoid Avatars
metadata:
  engine: unity
  category: unity
  difficulty: intermediate
---

# Unity Animation (Animator / Mecanim)

Control animation state with Unity 6's `Animator` and Animator Controllers: parameters,
transitions, blend trees, layers, and humanoid IK. Targets **Unity 6 (6000.0 LTS)**.

## When to use

- Use when connecting animation clips into a state machine, driving them from script via
  parameters, blending locomotion (idle→walk→run), layering an upper-body action over
  movement, or adding foot/hand IK on a humanoid rig.
- Use when the project has `*.controller` (Animator Controller) and `*.anim` assets, or a
  rigged model with an Avatar.

**When *not* to use:** simple non-skeletal value tweens (UI fades, position lerps) are better
done with a tween/coroutine — see `unity-csharp-scripting`. Timeline cutscenes are a separate
tool. 2D sprite frame animation also uses the Animator but with sprite keyframes.

## Core workflow

1. **Add an `Animator`** to the model and assign an Animator Controller; for a humanoid model,
   set its rig to **Humanoid** so it has an Avatar (enables retargeting and IK).
2. **Define parameters** on the controller — `Float` (Speed), `Bool` (IsGrounded), `Int`,
   `Trigger` (Jump) — and states with transitions whose *conditions* read those parameters.
3. **Set parameters from script**, never poke states directly: `SetFloat`, `SetBool`,
   `SetInteger`, `SetTrigger`. The state machine resolves transitions for you.
4. **Blend continuous motion with a Blend Tree** (one `Float` like Speed drives idle↔walk↔run)
   instead of many discrete states + transitions.
5. **Layer additive/override motion** (e.g. an upper-body "aim" layer with an Avatar Mask) and
   control its `layerWeight`.
6. **Verify** in the Animator window during Play mode — the live state highlights and parameter
   values update, so you can see exactly which transition fired (or didn't).

## Patterns

### 1. Drive locomotion + a one-shot action from script

```csharp
using UnityEngine;

[RequireComponent(typeof(Animator))]
public class CharacterAnim : MonoBehaviour
{
    private Animator _anim;
    // Cache parameter hashes — faster and typo-proof vs string lookups every frame.
    private static readonly int Speed     = Animator.StringToHash("Speed");
    private static readonly int IsGrounded= Animator.StringToHash("IsGrounded");
    private static readonly int Jump      = Animator.StringToHash("Jump");

    private void Awake() => _anim = GetComponent<Animator>();

    public void Tick(float planarSpeed, bool grounded)
    {
        _anim.SetFloat(Speed, planarSpeed);     // drives a 1D blend tree (idle/walk/run)
        _anim.SetBool(IsGrounded, grounded);    // gates a falling/landing transition
    }

    public void DoJump() => _anim.SetTrigger(Jump);  // fire-and-forget; auto-resets after use
}
```

### 2. Smooth a noisy input into a blend parameter

```csharp
// dampTime smooths Speed so the blend tree doesn't snap; great for analog sticks.
_anim.SetFloat(Speed, targetSpeed, 0.1f /* dampTime */, Time.deltaTime);
```

### 3. Play / cross-fade a state directly (bypassing parameter conditions)

```csharp
// Useful for hit reactions where you want an immediate, explicit transition.
_anim.CrossFade("Hit", 0.1f);                    // blend over 0.1s normalized
// Or jump instantly:  _anim.Play("Hit");
```

### 4. Wait until the current state finishes

```csharp
private System.Collections.IEnumerator AfterAttack()
{
    var info = _anim.GetCurrentAnimatorStateInfo(0);   // layer 0
    yield return new WaitForSeconds(info.length);      // approximate clip length
    // ...follow-up logic
}
```

## Pitfalls

- **`SetTrigger` missed or "sticks"** — triggers are consumed by the next satisfied transition
  and auto-reset; if no transition consumes it, it can fire later unexpectedly. Use
  `ResetTrigger` to clear, or prefer a `Bool` when the condition is a sustained state.
- **String parameter typos fail silently** — a misspelled name just does nothing. Use
  `Animator.StringToHash` and cache the int hashes.
- **Transition feels laggy** — `Has Exit Time` makes the transition wait for the clip to reach
  a normalized time. Uncheck it for responsive, condition-driven transitions (jump, hit).
- **Character slides or won't move** — `Apply Root Motion` is on but your code also moves the
  transform (or vice versa). Decide: root motion *or* scripted movement, not both.
- **Upper-body layer overrides the whole body** — set the layer's Blend mode (Override vs
  Additive), assign an Avatar Mask, and tune `layerWeight` (0–1).
- **IK does nothing** — IK only applies inside `OnAnimatorIK`, requires "IK Pass" enabled on
  the layer, and needs a Humanoid Avatar.

## References

- For **blend trees** (1D vs 2D Freeform/Directional), **animation layers + Avatar Masks**,
  and **humanoid IK** (`OnAnimatorIK`, `SetIKPositionWeight`, `SetIKPosition`, look-at), read
  `references/blend-trees-and-ik.md`.
- Primary docs: Unity Manual "Animation" section and `ScriptReference/Animator`.

## Related skills

- `unity-csharp-scripting` — the MonoBehaviour and coroutine timing used above.
- `unity-physics` — moving the body that the animation visualises.
- `game-ai` — deciding *when* to play which animation state.
