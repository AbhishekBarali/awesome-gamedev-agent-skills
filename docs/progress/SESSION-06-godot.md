# Session 06 — Author: Godot Skills

> Public build-log entry. Value-focused only. No growth/marketing/strategy language.

- **Session:** S06
- **Wave:** 3 (parallel authoring)
- **Date (UTC):** 2026-06-24
- **Depends on:** S05 (frozen standard, catalog, router spec, golden skill)
- **Status:** complete
- **Branch / commits:** `session/S06-godot` → 5 `feat(godot): …` commits (one per batch) + this docs commit

## Objective
Author all **15 Godot skills** from the frozen catalog's `godot` section as
`skills/godot/<name>/SKILL.md`, each pinned to **Godot 4.3+**, verified against the primary
Godot documentation, following `docs/SKILL-FORMAT.md` and the `love2d-core` golden shape.

## What was produced
Each skill has a routing-rule `description`, a when-to-use boundary (naming sibling skills),
a numbered core workflow, 4 version-pinned GDScript (or shader/C#) patterns, a pitfalls list
(including 3.x→4.x traps), and a `references/*.md` for progressive disclosure.

- **`godot-gdscript`** — GDScript 2.0: static typing, node lifecycle, `@export`/`@onready`,
  signals, `await`. (+ `references/annotations-and-typing.md`)
- **`godot-nodes-scenes`** — scene tree, composition, `instantiate()`, autoloads,
  `PackedScene`, safe node access. (+ `references/tree-and-instancing.md`)
- **`godot-signals-groups`** — custom signals, Callable connections, `bind`/one-shot,
  groups/`call_group`, global event bus. (+ `references/signal-patterns.md`)
- **`godot-2d-movement`** — `CharacterBody2D` + argument-less `move_and_slide()`, platformer
  and top-down controllers, slopes, slide collisions, coyote time. (+ `references/controller-recipes.md`)
- **`godot-tilemap`** — `TileMapLayer` + `TileSet`, set/erase cells, custom data, autotiling
  with terrains, runtime tile-data overrides. (+ `references/tileset-and-terrains.md`)
- **`godot-physics`** — body types, collision layers vs masks, `Area` overlaps, forces/
  impulses, RayCast nodes and space-state queries. (+ `references/bodies-and-queries.md`)
- **`godot-ui-control`** — `Control` anchors/offsets, Container layout, size flags, Theme/
  StyleBox, focus navigation, HUD CanvasLayer. (+ `references/layout-and-theming.md`)
- **`godot-animation`** — `AnimationPlayer`, `AnimationTree` state machines/blend spaces,
  `create_tween()` Tweens. (+ `references/animation-tree-and-tween.md`)
- **`godot-shaders`** — `canvas_item` + `spatial` shaders, uniforms (`source_color`,
  `hint_range`), `TIME`/`UV`, screen reading via `hint_screen_texture`. (+ `references/shading-language.md`)
- **`godot-3d-essentials`** — `Node3D` transforms, `Camera3D`, lights, `WorldEnvironment`
  post, `StandardMaterial3D`, `GridMap`. (+ `references/scene-and-environment.md`)
- **`godot-resources`** — custom `Resource` classes, `.tres`/`.res`, `duplicate`,
  `ResourceLoader`/`ResourceSaver`, `user://`. (+ `references/resource-patterns.md`)
- **`godot-audio`** — `AudioStreamPlayer` (2D/3D), buses via `AudioServer`, dB vs linear,
  crossfade, beat-accurate timing. (+ `references/buses-and-effects.md`)
- **`godot-multiplayer`** — `ENetMultiplayerPeer`, `@rpc` + `rpc()`/`rpc_id()`, per-node
  authority, `MultiplayerSpawner`/`Synchronizer`, server-authoritative design.
  (+ `references/replication-and-rpc.md`)
- **`godot-export`** — export templates/presets, headless CLI export, web COOP/COEP,
  dedicated-server/headless builds, `user://` write paths. (+ `references/presets-and-cli.md`)
- **`godot-csharp`** — `partial` node classes, PascalCase lifecycle, `[Export]`, `[Signal]`
  delegates as C# events, `GetNode<T>`, GDScript interop. (+ `references/csharp-setup-and-interop.md`)

## Key decisions
- **Pin to Godot 4.3+ stable.** Every snippet targets the 4.x API surface; 3.x→4.x traps are
  called out per skill (e.g. `move_and_slide()` signature, `yield`→`await`, `export`→`@export`,
  `connect(str,self,str)`→`sig.connect(Callable)`, `instance()`→`instantiate()`,
  `SCREEN_TEXTURE`→`hint_screen_texture`, `hint_color`→`source_color`, Tween node removed).
- **`godot-tilemap` is built on `TileMapLayer`**, not the deprecated `TileMap` node, with a
  migration note — the catalog already specified 4.3+ for this skill.
- **Engine API vs cross-engine concept** boundaries respected: each skill's when-not-to-use
  defers shader theory to `shader-programming`, audio practice to `audio-design`, physics feel
  to `physics-tuning`, input architecture to `input-systems`, and saves to `save-systems`,
  per the catalog's composition rules.
- **Depth pushed to `references/`** so every `SKILL.md` stays well under 500 lines while
  remaining code-forward.

## Verification
- **Version-sensitive APIs verified against primary docs** (`docs.godotengine.org/en/stable`)
  before writing: `CharacterBody2D.move_and_slide()` is argument-less and reads/writes the
  `velocity` property; high-level multiplayer `@rpc` defaults/`rpc()`/`rpc_id()`/
  `get_remote_sender_id()`/`ENetMultiplayerPeer`; `TileMapLayer` (`set_cell`,
  `get_cell_tile_data().get_custom_data()`, `local_to_map`, `set_cells_terrain_connect`,
  TileMap node deprecated). Remaining APIs drawn from the Godot 4.x class reference and
  tutorials cited below.
- **Validator:** `python scripts/validate-skills.py` → "All checks passed." (exit 0) after each
  batch. All 15 `SKILL.md` are < 500 lines, names equal their folders, descriptions ≤ 1024
  chars, and every `references/` link resolves.
- **Skills authored:** 15; all follow the rubric in `docs/SKILL-FORMAT.md` (routing-rule
  description, when-to-use boundary, core workflow, ≥2 version-pinned patterns, pitfalls,
  references): yes.
- **Originality:** all prose and code written from scratch from the primary docs; no content
  copied from other repos/skills.

## Sources consulted (primary docs)
All under `https://docs.godotengine.org/en/stable/`:
- `classes/class_characterbody2d.html`, `tutorials/physics/physics_introduction.html`,
  `tutorials/physics/ray-casting.html` — 2D movement & physics.
- `classes/class_tilemaplayer.html`, `tutorials/2d/using_tilemaps.html`,
  `tutorials/2d/using_tilesets.html` — tilemaps & terrains.
- `tutorials/scripting/gdscript/gdscript_basics.html`, `tutorials/best_practices/` — GDScript.
- `getting_started/step_by_step/nodes_and_scenes.html`, `.../instancing.html`,
  `classes/class_packedscene.html`, `.../signals.html`, `tutorials/scripting/groups.html`.
- `classes/class_control.html`, `tutorials/ui/size_and_anchors.html`,
  `tutorials/ui/gui_navigation.html` — UI.
- `tutorials/animation/introduction.html`, `.../animation_tree.html`,
  `classes/class_animationplayer.html` — animation.
- `tutorials/shaders/your_first_shader/your_first_3d_shader.html`,
  `tutorials/shaders/screen-reading_shaders.html` — shaders.
- `tutorials/3d/introduction_to_3d.html`, `.../using_gridmaps.html`,
  `.../environment_and_post_processing.html` — 3D.
- `tutorials/scripting/resources.html`, `classes/class_resource.html` — resources.
- `tutorials/audio/audio_buses.html`, `.../audio_streams.html`, `.../sync_with_audio.html`.
- `tutorials/networking/high_level_multiplayer.html` — multiplayer/RPC.
- `tutorials/export/exporting_for_web.html`, `tutorials/editor/command_line_tutorial.html`,
  `tutorials/export/exporting_for_dedicated_servers.html` — export.
- `tutorials/scripting/c_sharp/index.html`, `.../c_sharp_basics.html`,
  `.../c_sharp_signals.html` — C#/.NET.

## Handoff to next sessions
- **S12 (router):** all 15 `godot` skill folders/names match the catalog exactly and are ready
  to route from; router signals in each `description` use the catalog's `says:`/`files:` cues.
- **S10/S09 (genres/disciplines):** genre and discipline skills can compose these via the
  "Related skills" hand-offs already embedded (e.g. `platformer` → `godot-2d-movement` +
  `godot-tilemap`; `fps-shooter` → `godot-3d-essentials`).
- **S13 (QA):** descriptions favor coverage of trigger vocabulary and exceed the 200-char soft
  target (like the golden skill); QA may trim for claude.ai portability if desired.
- Shared files (`docs/progress/INDEX.md`, `README.md`, `docs/skill-catalog.md`) were left
  untouched per session scope — S12 integrates and updates `INDEX.md`.

## If partial — remaining work
- None. All 15 catalog skills authored, validated, and committed.
