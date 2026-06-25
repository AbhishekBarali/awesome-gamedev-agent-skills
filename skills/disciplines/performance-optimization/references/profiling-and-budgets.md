# Profiling & budgets — depth for `performance-optimization`

Detail the body defers here: per-engine profiler walkthroughs, the CPU-vs-GPU triage flow, a
pooling manager, batching/instancing rules, allocation/GC guidance, LOD/culling, and asset
budgets. Targets **Godot 4.x**, **Unity 6**, **Unreal 5**.

## 1. CPU-vs-GPU triage (decide before you fix)

```text
1. Read total frame time vs your budget (16.67 ms @60).
2. Compare CPU-frame time and GPU-frame time:
     GPU >> CPU  → GPU-bound  → draw calls, overdraw, shader cost, resolution, lights/shadows.
     CPU >> GPU  → CPU-bound  → scripts, physics, pathfinding, allocations/GC, too many nodes.
     Both high / alternating → find the per-frame spike in the timeline (one function/system).
3. Within the bound side, sort costs descending and attack the top one only.
4. Re-measure. If it didn't move the frame time, you fixed the wrong thing — revert and re-triage.
```

A GPU-bound game won't speed up from faster C#; a CPU-bound game won't speed up from fewer draw
calls. This split is the single most important decision in performance work.

## 2. Per-engine profiler quick start

**Godot 4.x**
- Editor: **Debugger ▸ Profiler** (per-function script + physics time, frame time), and the
  **Monitors** tab (FPS, draw calls, video/static memory, object/node counts).
- Code: `Performance.get_monitor(Performance.TIME_PROCESS)` (process ms),
  `Performance.TIME_PHYSICS_PROCESS`, `Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME`,
  `Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME`, `Performance.MEMORY_STATIC`.
- Visual debugging: viewport **View Information / View Frame Time** overlays.

**Unity 6**
- **Profiler** window: CPU Usage, GPU Usage, Rendering, Memory modules. Use **Deep Profile**
  sparingly (high overhead, skews numbers).
- **Frame Debugger** to step draw calls and see what breaks batching (SetPass calls, batches).
- Code: `ProfilerRecorder` tracking `"CPU Main Thread Frame Time"` (Unity 6000 manual) for an
  in-build HUD/CSV; `FrameTimingManager` for CPU/GPU frame times.
- **Profile a Development build on device** (`Autoconnect Profiler`), not just the editor.

**Unreal 5**
- Console: `stat unit` (Frame / Game / Draw / GPU ms), `stat fps`, `stat scenerendering`
  (draw calls, primitives), `stat game`, `stat gpu`.
- **Unreal Insights** for full timeline traces; `ProfileGPU` (Ctrl+Shift+,) for a GPU breakdown.

## 3. Pooling manager (generic)

```text
class Pool<T>:
    free: list
    create_fn, reset_fn
    prewarm(n):  for n → free.push(create_fn())          # allocate up front, off the hot path
    acquire():   t = free.pop() or create_fn(); activate(t); return t
    release(t):  reset_fn(t); deactivate(t); free.push(t)  # never destroy; recycle
```

Pool anything spawned frequently and briefly: bullets, shells, particles, damage numbers,
enemies in waves, audio one-shots. Pre-warm at load to avoid first-use hitches. Cap the pool and
decide an overflow policy (grow, or recycle the oldest).

## 4. Batching & instancing rules

- **What breaks a batch:** a different material, texture, or render state between objects. Share
  materials and **atlas** textures so runs of objects submit as one draw call.
- **Identical meshes, many instances** → GPU instancing: Unity (enable *GPU Instancing* on the
  material) / Godot `MultiMesh` + `MultiMeshInstance2D/3D` / Unreal Instanced Static Mesh or
  Hierarchical ISM.
- **Static geometry** → static batching (Unity), mark static; bake where possible.
- **2D** → texture atlases + a shared material batch sprites; avoid per-sprite materials.
- **UI** → minimize canvas rebuilds (Unity: split static/dynamic canvases); a changing element
  shouldn't dirty the whole canvas.
- **Lights/shadows** → bake static lighting; cap real-time shadow casters; cull small shadows.

## 5. Allocation / GC guidance

- **C# (Unity):** no per-frame `new`, no LINQ in `Update`, avoid boxing (e.g. `enum` as dictionary
  key), use `NonAlloc` physics queries, reuse `List`/arrays (`Clear()` not realloc), prefer
  structs for small hot data, cache `GetComponent`/`Find` results. The goal is **0 B GC.Alloc per
  frame** in steady state.
- **GDScript (Godot):** don't build new `Array`/`Dictionary` each `_process`; reuse; prefer typed
  arrays; avoid heavy work in `_process` that belongs on a timer/signal.
- **General:** strings are a classic hidden allocator (concatenation, formatting) — build them
  rarely, cache results.

## 6. Do-less techniques (algorithmic wins)

- **Run less often:** update AI/HUD/expensive checks on a timer or every N frames, not every
  frame; stagger across frames (time-slicing).
- **Spatial partition:** grid/quadtree/octree so queries touch nearby objects only, not all N.
- **LOD & culling:** lower detail at distance; frustum/occlusion culling; despawn off-screen
  far entities.
- **Cache results:** memoize pathfinding, line-of-sight, and derived data; invalidate on change.
- **Defer/Amortize:** spread procedural generation and loading across frames to avoid spikes.

## 7. Asset budgets (prevent regressions at the source)

| Asset | Typical desktop budget | Mobile budget | Notes |
|-------|------------------------|---------------|-------|
| Texture max size | 2048–4096 | 1024–2048 | use mipmaps; compress (BCn / ASTC) |
| Character triangles | 30k–80k | 5k–20k | LODs for distance |
| Draw calls / frame | low thousands | a few hundred | the count that matters most on mobile |
| Real-time lights | a few | 1–2 + baked | bake the rest |
| Audio | streamed music, short SFX in memory | same | don't decompress everything at load |

Mobile adds **thermal throttling**: a game that hits 60 FPS for 2 minutes then drops is
overheating — target headroom, cap frame rate, and reduce sustained GPU load.
