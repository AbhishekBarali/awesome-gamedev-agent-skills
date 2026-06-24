# Resource patterns reference (Godot 4.3+)

Depth companion to `godot-resources`.

## File formats

- `.tres` — text resource. Human-readable, merges/diffs well in version control. Default
  for hand-authored data.
- `.res` — binary resource. Smaller and faster to load; use for large/generated data.
- Convert by re-saving with the desired extension via `ResourceSaver.save`.

## Threaded (background) loading

Avoid frame hitches when loading large scenes/assets:

```gdscript
const PATH := "res://levels/big_level.tscn"

func begin_load() -> void:
    ResourceLoader.load_threaded_request(PATH)

func _process(_delta: float) -> void:
    var progress := []
    match ResourceLoader.load_threaded_get_status(PATH, progress):
        ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            update_bar(progress[0])           # 0.0–1.0
        ResourceLoader.THREAD_LOAD_LOADED:
            var res := ResourceLoader.load_threaded_get(PATH)
            _on_loaded(res)
        ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
            push_error("Load failed")
```

## resource_local_to_scene

By default a `.tres` is shared by every scene that references it. Tick **Local to Scene**
(or set `resource_local_to_scene = true`) so each scene instance gets its own copy at load
time — useful for per-instance materials/state without manual `duplicate()`.

## @tool resources

Add `@tool` to a Resource script to run setup in the editor (e.g. validate fields, derive
values). Guard with `Engine.is_editor_hint()` where needed. Combine with `@export_tool_button`
(4.4+) or a custom inspector plugin for editor actions.

## Custom ResourceFormatLoader / Saver

To load a non-Godot file format as a Resource (e.g. a custom `.deck` text format), register
a `ResourceFormatLoader` (and optionally `ResourceFormatSaver`) and add it with
`ResourceLoader.add_resource_format_loader(loader)`. Override `_get_recognized_extensions`,
`_handles_type`, and `_load`. This lets `load("res://x.deck")` return your resource type.

## Resource UIDs

Godot 4 assigns each imported resource a stable UID (`uid://...`). Scenes can reference by
UID so moving/renaming files doesn't break links. Get one with `ResourceUID`. Prefer
letting the editor manage UIDs; avoid hand-editing `.uid` files.

## Data-driven design tips

- Keep resources **pure data**; put behavior in nodes/systems that read them. This keeps
  data hot-swappable and testable.
- Use `StringName` (`&"id"`) for identifiers/keys — faster comparisons than `String`.
- Model registries (all items, all enemies) as an `Array[YourResource]` exported on an
  autoload, or a directory of `.tres` files loaded at startup.
- A typed export array (`@export var loot: Array[ItemResource]`) enforces element type in
  the Inspector and prevents dragging the wrong resource type.

## Common API

```gdscript
res.duplicate(deep := false)      # copy; deep also copies sub-resources
res.take_over_path("res://x.tres")
res.resource_path                 # where it loaded from ("" if in-memory)
ResourceLoader.exists(path, type_hint := "")
ResourceLoader.load(path, type_hint := "", cache_mode := CACHE_MODE_REUSE)
ResourceSaver.save(res, path, flags := 0)   # FLAG_COMPRESS, FLAG_BUNDLE_RESOURCES, ...
```
