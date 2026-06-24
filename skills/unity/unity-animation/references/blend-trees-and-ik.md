# Blend trees, layers & humanoid IK (Unity 6)

Depth for `unity-animation`. Verified against the Unity Manual Animation section and
`ScriptReference/Animator`.

## Blend trees

A Blend Tree blends several clips by one or two `Float` parameters, so continuous motion
(idle → walk → run, or 8-direction movement) is one node instead of many states.

- **1D** — one parameter (e.g. `Speed`). Place clips along the axis (0 idle, 2 walk, 6 run);
  the tree cross-fades by where the parameter sits.
- **2D Simple Directional** — clips at distinct directions (forward, back, strafe).
- **2D Freeform Directional / Cartesian** — arbitrary clip placement in a 2D field
  (`MoveX`, `MoveY`); Freeform Cartesian suits non-directional pairs (speed × turn).

Drive it from script exactly like any float parameter, ideally damped:

```csharp
_anim.SetFloat("Speed", speed, 0.1f, Time.deltaTime);   // dampTime smooths the blend
_anim.SetFloat("MoveX", moveX);
_anim.SetFloat("MoveY", moveY);
```

Tip: keep blend thresholds matched to the clips' real root speed so feet don't slide.

## Animation layers + Avatar Masks

Layers let an upper-body action (aim, throw) play over a base locomotion layer.

- Each layer has a **weight** (0–1) and a **Blend mode**: `Override` (replaces) or `Additive`
  (adds on top of the base pose).
- An **Avatar Mask** restricts a layer to selected bones (e.g. spine + arms), so the legs keep
  walking while the arms aim.

```csharp
int aimLayer = _anim.GetLayerIndex("UpperBody");
_anim.SetLayerWeight(aimLayer, isAiming ? 1f : 0f);   // fade the layer in/out
```

## Humanoid IK (`OnAnimatorIK`)

IK adjusts hands/feet/look toward targets *after* the animation pose is sampled. Requirements:
Humanoid Avatar, and **IK Pass** enabled on the layer.

```csharp
[SerializeField] private Transform lookTarget, rightHandTarget;

// Called by the Animator once per frame, per layer, when IK Pass is on.
private void OnAnimatorIK(int layerIndex)
{
    if (lookTarget)
    {
        _anim.SetLookAtWeight(1f);                 // overall look-at weight
        _anim.SetLookAtPosition(lookTarget.position);
    }
    if (rightHandTarget)
    {
        _anim.SetIKPositionWeight(AvatarIKGoal.RightHand, 1f);   // 0..1 blend toward target
        _anim.SetIKRotationWeight(AvatarIKGoal.RightHand, 1f);
        _anim.SetIKPosition(AvatarIKGoal.RightHand, rightHandTarget.position);
        _anim.SetIKRotation(AvatarIKGoal.RightHand, rightHandTarget.rotation);
    }
}
```

`AvatarIKGoal` values: `LeftFoot`, `RightFoot`, `LeftHand`, `RightHand`. Set the weight back
toward 0 to release the IK smoothly.

### Foot IK for sloped ground

- Enable **Foot IK** on the locomotion states.
- Raycast down from each foot, then `SetIKPosition`/`SetIKRotation` to the surface point and
  normal so feet plant on slopes instead of clipping or floating.

## Gotchas

- IK calls outside `OnAnimatorIK` are ignored.
- `SetLookAtWeight` has extra body/head/eyes/clamp parameters — the single-arg overload is a
  shortcut for the common case.
- Layer weights and IK weights are not auto-reset; lerp them toward 0 when disengaging or the
  pose stays stuck.
- Additive layers need a reference pose set on the clip's import settings, or they drift.
