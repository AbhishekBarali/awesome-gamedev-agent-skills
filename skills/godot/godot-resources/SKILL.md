---
name: godot-resources
description: >
  Design data-driven Godot 4.x games with custom Resource classes: define typed
  data with class_name + @export, save/load .tres/.res files, instance and duplicate
  resources, and load on demand with ResourceLoader (incl. threaded loading). Use
  when modeling items/stats/configs as data in a Godot project, creating .tres
  resources, or working with custom Resource subclasses and ResourceLoader/ResourceSaver.
license: Apache-2.0
compatibility: Godot 4.3+
metadata:
  engine: godot
  category: godot
  difficulty: intermediate
---

# Godot Resources (4.x)

Model game data as reusable, Inspector-editable `Resource` objects instead of hard-coded
values, and load/save them as `.tres`/`.res`. Targets **Godot 4.3+**.

## When to use

- Use when representing items, stats, enemy configs, dialogue lines, or level metadata as
  data; authoring `.tres` files in the Inspector; or loading/saving custom resources.

**When *not* to use:** nodes/scene structure → `godot-nodes-scenes`; saving the player's
*runtime progress* (engine-agnostic save format/slots) → `save-systems`; the C# variant of
this pattern → `godot-csharp`.

## Core workflow

1. **Subclass `Resource`** with `class_name` and `@export` fields. It now appears in the
   "New Resource" dialog and as an `@export` type, editable in the Inspector.
2. **Create instances as `.tres`** files in the FileSystem dock (text, diff-friendly) or
   `.res` (binary, smaller/faster). Edit their fields in the Inspector — no code needed.
3. **Reference resources from nodes** via `@export var data: ItemResource`, or arrays
   `@export var loot: Array[ItemResource]`.
4. **Load at runtime** with `preload` (constant path) or `load`/`ResourceLoader.load`
   (variable path). Use threaded loading for large assets.
5. **Duplicate before mutating** a shared resource at runtime, or every node using it
   changes too (resources are shared references).
6. **Save generated/edited resources** with `ResourceSaver.save`.

## Patterns

### 1. A custom data resource

```gdscript
# item.gd
extends Resource
class_name ItemResource

@export var id: StringName = &""
@export var display_name: String = "Item"
@export_multiline var description: String = ""
@export var icon: Texture2D
@export var max_stack: int = 99
@export var value: int = 0
```

Create `sword.tres` from this class in the FileSystem dock and fill it in the Inspector.

### 2. Consume resources from a node

```gdscript
extends Node
@export var starting_items: Array[ItemResource] = []   # drag .tres files in the Inspector

func _ready() -> void:
    for item in starting_items:
        print("Have: %s (x%d max)" % [item.display_name, item.max_stack])
```

### 3. Duplicate before mutating shared data

```gdscript
func give_unique_copy(template: ItemResource) -> ItemResource:
    # true = deep copy sub-resources too; false = shallow (shares sub-resources).
    var copy: ItemResource = template.duplicate(true)
    copy.value += 5                # mutating the copy won't touch the template .tres
    return copy
```

### 4. Save and load a resource at runtime

```gdscript
func save_config(cfg: Resource) -> void:
    ResourceSaver.save(cfg, "user://config.tres")   # user:// = writable app data dir

func load_config() -> Resource:
    if ResourceLoader.exists("user://config.tres"):
        return ResourceLoader.load("user://config.tres")
    return null
```

## Pitfalls

- **Resources are shared by reference.** A single `.tres` assigned to many nodes is the
  *same* object — mutating it changes all of them (and re-saving the file). Call
  `duplicate(true)` for per-instance state.
- **`class_name` required to instance from the editor.** Without it the class won't appear
  in the "New Resource" dialog or as an `@export` type.
- **`res://` is read-only in exported games.** Write runtime data to `user://`, never
  `res://`. `ResourceSaver.save` to `res://` only works in the editor.
- **Storing nodes in a Resource doesn't serialize them.** Resources hold data, not live
  scene nodes. Reference scenes via `PackedScene`, not node instances.
- **Cyclic resource references** (A holds B holds A) can fail to save/load cleanly — keep
  data graphs acyclic or use IDs/lookups.
- **`preload` vs `load`.** `preload` needs a constant path and loads with the script;
  `load` accepts a variable path at runtime. Use `ResourceLoader.exists()` before `load`
  to avoid errors on missing files.
- **Don't put secrets in `.tres`** — they ship in plain text inside the export.

## References

- For threaded/background loading (`load_threaded_request`), `@tool` resources with custom
  setup, custom `ResourceFormatLoader`/`Saver`, resource-local-to-scene, and resource UIDs,
  read `references/resource-patterns.md`.

## Related skills

- `godot-gdscript` — `@export` annotations used to define resource fields.
- `godot-nodes-scenes` — instancing scenes vs. sharing resource data.
- `save-systems` — persisting runtime progress (separate from static data).
- `unity-scriptableobjects` — the equivalent data-asset pattern in Unity.
