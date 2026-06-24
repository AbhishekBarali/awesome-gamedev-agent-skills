# Godot C# setup & interop reference (Godot 4.3+ .NET)

Depth companion to `godot-csharp`.

## Project setup

- Use the **Godot .NET** editor build (labeled ".NET"/"Mono").
- Install the matching **.NET SDK** (Godot 4.3 targets **.NET 8**).
- The first C# script creates `<Project>.csproj` and `<Project>.sln`. The `.csproj` sets
  `<TargetFramework>net8.0</TargetFramework>` and references `GodotSharp`.
- Build via the editor (it builds on play) or `dotnet build`. Editor Settings let you pick
  an external editor (VS, VS Code, Rider).
- Add NuGet packages by editing the `.csproj` `<ItemGroup>` and rebuilding.

## Export attributes

```csharp
[Export] public int Lives = 3;
[Export(PropertyHint.Range, "0,100,1")] public int Percent;
[Export(PropertyHint.Range, "0,1,0.01,or_greater")] public float Gain = 1f;
[Export(PropertyHint.File, "*.json")] public string DataPath;
[Export(PropertyHint.Enum, "Idle,Walk,Run")] public string State;
[Export] public Godot.Collections.Array<PackedScene> Waves = new();
[Export] public NodePath TargetPath;

[ExportGroup("Movement")]
[Export] public float Speed = 200f;
[ExportSubgroup("Air")]
[Export] public float AirControl = 0.4f;

[ExportCategory("Debug")]
[Export] public bool ShowGizmos;
```

`[ExportGroup]`/`[ExportSubgroup]`/`[ExportCategory]` organize the Inspector.

## Collections: Godot vs System

- `Godot.Collections.Array` and `Godot.Collections.Dictionary` (and generic
  `Array<T>`/`Dictionary<TKey,TValue>`) are Variant-backed and can be `[Export]`ed, passed
  to engine APIs, and shared with GDScript.
- `System.Collections.Generic.List<T>`/`Dictionary<,>` are normal C#; faster for pure C#
  logic but **cannot** be exported or passed directly to engine calls expecting Variants.
- Convert as needed: `new Godot.Collections.Array<int>(myList)`.

## Async with signals

```csharp
public async void OpenChest()
{
    var anim = GetNode<AnimationPlayer>("AnimationPlayer");
    anim.Play("open");
    await ToSignal(anim, AnimationPlayer.SignalName.AnimationFinished);
    SpawnLoot();
}

// Timer await:
await ToSignal(GetTree().CreateTimer(0.5), SceneTreeTimer.SignalName.Timeout);
```

`ToSignal(obj, SignalName.X)` is the C# equivalent of GDScript `await obj.x`.

## Custom Resource in C#

```csharp
using Godot;

[GlobalClass]                              // makes it appear in the New Resource dialog
public partial class ItemResource : Resource
{
    [Export] public string DisplayName { get; set; } = "Item";
    [Export] public int Value { get; set; }
    [Export] public Texture2D Icon { get; set; }
}
```

`[GlobalClass]` is the C# analog of GDScript `class_name`. Load/duplicate as usual:
`GD.Load<ItemResource>("res://sword.tres")`, `resource.Duplicate(true)`.

## Calling C# from GDScript

A C# `[GlobalClass]` or any C# node is usable from GDScript by its node/class. GDScript
calls C# methods/properties directly when the C# member is `public`. Conversely C# calls
GDScript via `Call`/`Get`/`Set` and connects with `Callable.From(method)` or
`new Callable(this, MethodName.OnFoo)`.

## Common Godot C# API equivalents

| GDScript | C# |
|----------|-----|
| `print(x)` | `GD.Print(x)` |
| `preload`/`load` | `GD.Load<T>("res://...")` |
| `instantiate()` | `packed.Instantiate<T>()` |
| `$Path` / `get_node` | `GetNode<T>("Path")` |
| `%Unique` | `GetNode<T>("%Unique")` |
| `queue_free()` | `QueueFree()` |
| `emit_signal("x", a)` | `EmitSignal(SignalName.X, a)` |
| `randf()` / `randi()` | `GD.Randf()` / `GD.Randi()` |
| `deg_to_rad(d)` | `Mathf.DegToRad(d)` |
| `is_instance_valid(o)` | `GodotObject.IsInstanceValid(o)` |

## Build/export notes

- Release exports compile C# ahead-of-time per target. Some platforms (web, mobile) have
  extra .NET export requirements/steps — check the current .NET export docs for your
  target before shipping.
- Keep generated `obj/`, `bin/`, and `.godot/` out of version control (`.gitignore`).
