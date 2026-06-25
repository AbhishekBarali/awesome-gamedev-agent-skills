---
name: performance-optimization
description: >
  Find and fix game performance problems methodically — measure with the engine profiler first,
  reason about the frame-time budget, locate the CPU-vs-GPU bottleneck, then apply the right fix:
  object pooling, draw-call batching, fewer allocations/GC spikes, and asset budgets. Engine-
  neutral method that pairs with each engine's profiler. Use when the user mentions performance,
  optimize, low/dropping FPS, frame drops, stutter, lag, profiler, frame budget, draw calls,
  batching, garbage collection/GC spikes, object pooling, or "the game runs slow".
license: Apache-2.0
compatibility: Engine-agnostic methodology; profiler/tooling notes for Godot 4.x, Unity 6, and Unreal 5. Pairs with physics-tuning and the engine skills.
metadata:
  engine: none
  category: disciplines
  difficulty: advanced
---

# Performance optimization

Performance work is a measurement discipline, not a bag of tricks. The method is always the
same: **profile → find the one bottleneck → fix that → measure again**. This skill teaches that
loop and the highest-leverage fixes (pooling, batching, allocation control, asset budgets), and
points you at each engine's profiler. It pairs with `physics-tuning` for simulation cost.

## When to use

- Use when the frame rate is low or uneven, the game stutters/hitches, or it must hit a target
  (60 FPS desktop, 30/60 mobile) and currently doesn't.
- Use to decide *what* to optimize: profile, read the frame budget, and identify whether the CPU
  or GPU is the bottleneck before changing any code.
- Use to apply specific fixes: object pooling, draw-call/batch reduction, removing per-frame
  allocations and GC spikes, and setting asset budgets.

**When *not* to use:** for physics jitter/tunneling/timestep specifically, use `physics-tuning`.
For the engine's concrete profiler UI and rendering settings, use that
engine skill (`godot-export` covers some build settings; engine cores cover the rest). This skill
is the cross-engine method and the shared fixes.

## The golden rule: measure first, never guess

Most performance "fixes" applied without profiling target the wrong thing and add complexity for
no gain. **Do not optimize code you have not measured.** Open the profiler, find the single
biggest cost in a representative scene on representative hardware, and fix that. Re-measure to
confirm the fix helped before moving on. Profile a **release/optimized build** where it matters —
editor and debug builds lie (editor overhead, no compiler optimization).

## Core workflow

1. **Define the target and reproduce.** State the goal (e.g. 60 FPS = 16.67 ms/frame) and find a
   repeatable worst-case scene. "Sometimes slow" is unfixable; a reproducible spike is fixable.
2. **Profile before touching code.** Run the engine profiler and read the frame: total frame
   time, and the split between CPU (game logic, physics, scripts) and GPU (rendering).
3. **Find the bottleneck — CPU or GPU.** If GPU time ≫ CPU, attack draw calls/overdraw/shaders/
   resolution. If CPU time dominates, attack scripts/physics/allocations. Fixing the wrong side
   does nothing.
4. **Fix the single biggest cost.** Prefer an **algorithmic** win (do less work, cache, spatial
   partition, run less often) over micro-optimizing a hot line. Apply the matching shared fix
   (pooling, batching, allocation removal).
5. **Re-measure on the same scene/hardware.** Confirm the number moved. Keep or revert based on
   data, not intuition.
6. **Set budgets so it stays fixed.** Per-frame ms budgets per subsystem, plus asset budgets
   (texture sizes, triangle counts, draw-call ceilings); add a perf check to verification.
7. **Report measured numbers.** State before/after frame time, the bottleneck found, and the fix
   — never "should be faster". If you could only measure in-editor, say so.

## Patterns

### 1. Frame budget math (turn "feels slow" into a number)

```text
target FPS → frame budget:   60 FPS = 16.67 ms   |   30 FPS = 33.3 ms   |   120 FPS = 8.33 ms
The WHOLE frame (CPU sim + render submit + GPU) must fit the budget; the GPU runs in parallel,
so the slower of CPU-frame and GPU-frame sets your FPS. Allocate sub-budgets, e.g. @60 FPS:
  gameplay/scripts ~5 ms · physics ~3 ms · rendering(CPU submit) ~4 ms · UI/other ~2 ms · slack.
If one subsystem blows its slice, that's your target — not whatever you assumed.
```

### 2. Measure with the engine profiler (do this before any fix)

```text
Godot 4.x : Debugger ▸ Profiler (script/physics time) and Monitors tab (FPS, draw calls, memory).
            In code: Performance.get_monitor(Performance.TIME_PROCESS) and
            Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME).
Unity 6   : Profiler window (CPU/GPU/Memory/Rendering modules) + Frame Debugger for draw calls.
            In code: a ProfilerRecorder tracking "CPU Main Thread Frame Time" for a HUD/log.
Unreal 5  : `stat unit` (Frame/Game/Draw/GPU ms), `stat fps`, `stat scenerendering` (draw calls);
            Unreal Insights for deep traces.
# Read the split: is the Draw/GPU line the biggest, or the Game/CPU line? That decides the fix.
```

### 3. Object pooling (stop allocating/freeing in hot loops)

```gdscript
# Bullets, particles, enemies, damage numbers: reuse a fixed set instead of instantiate()/free()
# every frame — that thrashes memory and (in C#) feeds the GC.
var _pool: Array[Node] = []
func acquire() -> Node:
    var n: Node = _pool.pop_back() if not _pool.is_empty() else bullet_scene.instantiate()
    n.set_process(true); n.visible = true
    return n
func release(n: Node) -> void:
    n.set_process(false); n.visible = false       # disable + hide; DON'T free
    _pool.append(n)                                # back to the pool for reuse
# RIGHT: pre-warm the pool at load; reuse. WRONG: instantiate()/queue_free() per shot.
```

### 4. Cut draw calls (the most common GPU-side win)

```text
Each unique material/texture/state change is roughly a draw call; thousands of them stall the GPU.
- Atlas textures and share materials so sprites/meshes batch into one call.
- Identical meshes → GPU instancing (Unity), MultiMesh / MultiMeshInstance (Godot), Instanced
  Static Mesh (Unreal).
- Static geometry → static batching / baking; mark non-moving objects static.
- Reduce overdraw: limit large overlapping transparent/particle layers (they re-shade pixels).
- Fewer real-time lights/shadows; bake lighting where it doesn't move.
Measure draw calls before and after — the count should drop, and so should GPU frame time.
```

### 5. Kill per-frame allocations (GC spikes = stutter)

```csharp
// Unity 6 (C#). Allocating every frame fills the managed heap; the GC then stalls a frame.
// WRONG (allocates each call): foreach (var e in FindObjectsOfType<Enemy>()) ...  // + LINQ, new[]
// RIGHT: cache references once, reuse buffers, avoid LINQ/boxing in Update.
void Update() {
    _hits = Physics.RaycastNonAlloc(ray, _hitBuffer);   // reuse a preallocated array
    for (int i = 0; i < _hits; i++) { /* ... */ }       // no per-frame allocation
}
// Godot/GDScript: avoid building new arrays/dictionaries every frame in _process; reuse them.
```

## Pitfalls

- **Optimizing without profiling.** The intuitive culprit is usually wrong. Measure first, every
  time.
- **Profiling the editor / a debug build.** Editor overhead and unoptimized code mislead. Profile
  a release build on target hardware for real numbers.
- **Fixing the wrong side.** Micro-optimizing CPU code when the GPU is the bottleneck (or vice
  versa) changes nothing. Check the CPU-vs-GPU split first.
- **Micro-optimizing over algorithm.** Shaving a function when an O(n²) loop or a per-frame
  full-scene query is the real cost. Reduce the work, don't polish it.
- **Instantiate/free in hot loops.** Spawning and destroying bullets/particles every frame causes
  fragmentation and GC spikes. Pool them.
- **Per-frame allocations / LINQ / boxing in `Update`** (C#) feed the GC → periodic hitches.
  Cache and reuse.
- **Draw-call explosion** from unique materials and unbatched sprites/meshes. Atlas, share
  materials, instance, batch.
- **Overdraw** from stacked transparents/particles/full-screen effects re-shading pixels.
- **No budgets.** Without per-subsystem ms and asset ceilings, performance silently regresses;
  enforce them in your build/CI checks.
- **Optimizing too early.** Don't contort a prototype for performance before it's fun or measured.

## References

- For per-engine profiler walkthroughs, the CPU-vs-GPU triage flowchart, a complete pooling
  manager, batching/instancing rules per engine, allocation/GC guidance, LOD/culling, and asset
  budgets (texture sizes, triangle counts, audio, mobile thermals), read
  `references/profiling-and-budgets.md`.

## Related skills

- `physics-tuning` — simulation cost, fixed-step budget, sleeping bodies, broadphase layers.
- `godot-export` — release/build settings that affect measured performance.
- `procedural-gen`, `game-ai` — common CPU hotspots (generation, pathfinding) to budget and defer.
- `roguelike`, `tower-defense`, `survival-crafting` — entity-heavy genres that need pooling/budgets.
