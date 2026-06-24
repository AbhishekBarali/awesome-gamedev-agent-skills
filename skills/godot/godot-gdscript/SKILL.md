---
name: godot-gdscript
description: >
  Write idiomatic GDScript for Godot 4.x: static typing, the node lifecycle
  (_ready/_process/_physics_process), @export/@onready/@tool annotations,
  signals, and await for asynchronous flow. Use when editing .gd scripts in a
  Godot project (project.godot), writing or debugging GDScript, or porting 3.x
  GDScript to 4.x (func signatures, yield -> await, export -> @export).
license: Apache-2.0
compatibility: Godot 4.3+ (GDScript 2.0)
metadata:
  engine: godot
  category: godot
  difficulty: beginner
---

# Godot GDScript (4.x)

Write correct, statically typed GDScript and use the node lifecycle and signal
system the way the engine intends. Targets **Godot 4.3+** (GDScript 2.0).

## When to use

- Use when writing or fixing `.gd` files: declaring variables, functions, classes,
  using `@export`/`@onready`, connecting signals, or awaiting coroutines/signals.
- Use when porting Godot 3.x scripts to 4.x and the script no longer parses.

**When *not* to use:** scene/node structure and instancing questions →
`godot-nodes-scenes`; signal *architecture*/decoupling patterns →
`godot-signals-groups`; using C# instead of GDScript → `godot-csharp`.

## Core workflow

1. **Type everything you can.** GDScript 2.0 supports static types
   (`var hp: int = 10`, `func add(a: int, b: int) -> int:`). Types catch errors at
   parse time and speed up the VM. Use `:=` for inferred types.
2. **Use the lifecycle callbacks for their purpose:** `_ready()` once when the node
   and its children enter the tree; `_process(delta)` every rendered frame;
   `_physics_process(delta)` on the fixed physics tick (use it for movement/physics).
3. **Grab node references with `@onready`**, not in `_init()` — children do not exist
   until the node enters the tree.
4. **Expose tunables with `@export`** so designers edit them in the Inspector.
5. **React to events with signals + `await`**, not polling, where it reads cleanly.
6. **Run and read errors.** The Debugger panel prints typed errors with line numbers;
   fix the first error first (later ones are often cascades).

## Patterns

### 1. A typed script with lifecycle, @export, and @onready

```gdscript
extends Node2D
class_name Spinner            # registers a global type usable in other scripts

@export var speed: float = 90.0          # editable in the Inspector (degrees/sec)
@export_range(0, 10, 0.5) var wobble := 2.0
@onready var sprite: Sprite2D = $Sprite2D # resolved when the node enters the tree

func _ready() -> void:
    # Runs once, after children are ready. Safe to touch $Sprite2D here.
    sprite.modulate = Color.AQUA

func _process(delta: float) -> void:
    # delta is seconds since last frame; multiply rates by it for FPS independence.
    rotation_degrees += speed * delta
```

### 2. Signals: declare, emit, connect (4.x Callable syntax)

```gdscript
extends Node

signal health_changed(current: int, maximum: int)   # typed signal params

var health := 100

func take_damage(amount: int) -> void:
    health = max(health - amount, 0)
    health_changed.emit(health, 100)     # 4.x: emit as a method on the signal

func _ready() -> void:
    # 4.x: connect with a Callable, not a string method name.
    health_changed.connect(_on_health_changed)

func _on_health_changed(current: int, maximum: int) -> void:
    print("HP: %d/%d" % [current, maximum])
```

### 3. await — pause until a timer or signal fires (replaces 3.x yield)

```gdscript
func flash_then_continue() -> void:
    modulate = Color.RED
    await get_tree().create_timer(0.2).timeout   # resume after 0.2s
    modulate = Color.WHITE
    # await any signal: var result = await some_node.some_signal
```

### 4. Lambdas, typed arrays, and safe access

```gdscript
var enemies: Array[Node] = []                    # typed array

func cull_dead() -> void:
    enemies = enemies.filter(func(e): return e.is_inside_tree())

func get_first_name(d: Dictionary) -> String:
    return d.get("name", "unknown")              # default avoids missing-key errors
```

## Pitfalls

- **3.x → 4.x signal API changed.** `emit_signal("x")` still works but prefer
  `x.emit(...)`; `connect("x", self, "_on_x")` is gone — use `x.connect(_on_x)` with a
  Callable. `yield(obj, "sig")` is now `await obj.sig`.
- **`export var` is now `@export var`** (annotation). Likewise `onready`→`@onready`,
  `tool`→`@tool`, `remote`/`master` RPC keywords → the `@rpc(...)` annotation.
- **`@onready` and `$NodePath` in `_init()` fail** — the node isn't in the tree yet.
  Initialize node references in `_ready()` or with `@onready`.
- **Integer division truncates.** `5 / 2 == 2`. Use `5.0 / 2` or cast to `float`.
- **`_process` vs `_physics_process`.** Put `move_and_slide()` and physics in
  `_physics_process(delta)`; using `_process` makes motion frame-rate dependent.
- **`class_name` must be unique** project-wide and is required to use the type name in
  other scripts or as an Inspector type.

## References

- For the full annotation list, advanced typing, and style conventions, read
  `references/annotations-and-typing.md`.

## Related skills

- `godot-nodes-scenes` — the scene tree, instancing, and autoloads.
- `godot-signals-groups` — event-driven architecture with signals and groups.
- `godot-resources` — data-driven design with custom `Resource` types.
- `godot-csharp` — the same engine concepts using C#/.NET.
