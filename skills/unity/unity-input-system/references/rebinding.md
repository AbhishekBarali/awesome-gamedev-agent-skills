# Interactive rebinding & local multiplayer (Input System 1.x)

Depth for `unity-input-system`: runtime control rebinding and split-screen local co-op.
APIs are from `com.unity.inputsystem` 1.x (`UnityEngine.InputSystem`).

## Interactive rebinding ("press a key to rebind")

`InputActionRebindingExtensions.PerformInteractiveRebinding` listens for the next control the
player actuates and rewrites that binding as an override.

```csharp
using UnityEngine.InputSystem;

private InputActionRebindingExtensions.RebindingOperation _rebind;

public void StartRebind(InputAction action, int bindingIndex)
{
    action.Disable();                                    // must be disabled while rebinding
    _rebind = action.PerformInteractiveRebinding(bindingIndex)
        .WithControlsExcluding("<Mouse>/position")       // ignore noisy controls
        .OnMatchWaitForAnother(0.1f)
        .OnComplete(op =>
        {
            op.Dispose();                                // always dispose the operation
            action.Enable();
            SaveBindings(action.actionMap.asset);        // persist (see below)
        })
        .Start();
}
```

- Rebinds are stored as **binding overrides** on top of the asset's defaults; the asset is not
  modified on disk.
- Reset a single binding with `action.RemoveBindingOverride(bindingIndex)` or all with
  `action.actionMap.RemoveAllBindingOverrides()`.
- Show the current binding text with
  `action.GetBindingDisplayString(bindingIndex)`.

## Saving & loading rebinds

Serialize only the overrides as JSON and restore them on load:

```csharp
private const string Key = "input_rebinds";

void SaveBindings(InputActionAsset asset)
    => PlayerPrefs.SetString(Key, asset.SaveBindingOverridesAsJson());

void LoadBindings(InputActionAsset asset)
{
    if (PlayerPrefs.HasKey(Key))
        asset.LoadBindingOverridesFromJson(PlayerPrefs.GetString(Key));
}
```

`PlayerPrefs` is fine for keybinds; for larger save data use the `save-systems` approach.

## Local multiplayer with `PlayerInputManager`

For split-screen / shared-screen co-op, add a `PlayerInputManager` component and a player
prefab that has a `PlayerInput`. The manager spawns one player per joining device.

```csharp
using UnityEngine.InputSystem;

public class CoopSpawner : MonoBehaviour
{
    private void OnEnable()  => PlayerInputManager.instance.onPlayerJoined += HandleJoin;
    private void OnDisable() => PlayerInputManager.instance.onPlayerJoined -= HandleJoin;

    private void HandleJoin(PlayerInput player)
    {
        // Each PlayerInput owns its paired device(s); player.playerIndex identifies them.
        Debug.Log($"Player {player.playerIndex} joined on {player.devices[0].displayName}");
    }
}
```

- **Join Behavior** controls how players join (Join Players When Button Is Pressed, on action,
  or manually via `JoinPlayer`).
- Each `PlayerInput` is auto-assigned its own device(s), so two gamepads drive two players
  without extra wiring.
- Per-player UI needs a `MultiplayerEventSystem` + `InputSystemUIInputModule` per player.

## Gotchas

- Always `Dispose()` the `RebindingOperation` in `OnComplete`/`OnCancel`, or it leaks and
  keeps listening.
- Disable the action before rebinding it; rebinding an enabled action throws.
- Composite bindings (e.g. WASD) have multiple binding indices — rebind each part separately
  by its index, not the composite root.
