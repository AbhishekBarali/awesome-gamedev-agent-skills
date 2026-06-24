# Session 09 — Author: Disciplines

> Public build-log entry. Value-focused only. No growth/marketing/strategy language.

- **Session:** S09
- **Wave:** 3
- **Date (UTC):** 2026-06-24
- **Depends on:** S05 (standards lock, catalog, golden skill)
- **Status:** complete
- **Branch / commits:** `session/S09-disciplines` (isolated git worktree)

## Objective
Author the nine cross-engine **discipline** skills from the frozen catalog —
the portable concepts/algorithms that route alongside the detected engine skill —
each as a lean `SKILL.md` plus `references/` for depth, following the S05
authoring standard and the `love2d-core` golden shape.

## What was produced
All under `skills/disciplines/`, each a `SKILL.md` (144–179 lines) with one or two
`references/` files (85–131 lines):

- `game-ai` — FSM, behavior trees, steering (seek/arrive), A* pathfinding.
  Refs: `pathfinding.md` (full A* + heuristics + navmesh deferral + flow fields),
  `behavior-trees.md` (node taxonomy, stateful composites, blackboard, FSM-vs-BT).
- `procedural-gen` — seeded deterministic RNG, fBm noise, weighted loot tables,
  dungeon layout. Refs: `noise.md`, `dungeon-generation.md`.
- `dialogue-systems` — branching graph, conditions/variables, localization, and
  build-vs-buy. Refs: `ink-and-yarn.md` (verified Ink + Yarn Spinner syntax),
  `runner.md` (sandboxed expression eval + runner state machine).
- `save-systems` — serialize data not objects, atomic writes, schema versioning &
  migration, slots/autosave. Ref: `versioning-and-migration.md`.
- `audio-design` — bus mixing, dB gain, sidechain ducking, SFX variation, beat
  sync. Ref: `adaptive-music.md` (vertical layering + horizontal re-sequencing).
- `shader-programming` — vertex→fragment pipeline, UVs, common effects in GLSL.
  Ref: `effects.md` (outline/vignette/grading + GLSL↔HLSL mapping + per-engine).
- `physics-tuning` — fixed timestep + render interpolation, CCD/tunneling, mass/
  drag/gravity, layers/masks. Ref: `timestep-and-ccd.md`.
- `level-design` — metrics-first blockout→playable workflow, pacing curve, gating
  and the critical path. Ref: `pacing-and-flow.md`.
- `input-systems` — action mapping, rebinding with conflict detection, deadzones,
  input buffering + coyote time, accessibility. Ref: `buffering-and-accessibility.md`.

## Key decisions
- **Concept-owns-the-algorithm, engine-owns-the-API.** Each skill teaches the
  portable algorithm/practice and cross-links the engine skill for concrete
  syntax (e.g. `game-ai` → `unity-navmesh`/`unreal-behavior-trees`/Godot
  `NavigationAgent`; `shader-programming` → `godot-shaders`). Keeps disciplines
  additive to the exclusive engine selection, per the catalog's composition rules.
- **Algorithm-heavy skills grounded in primary sources first** (A*, noise, Ink,
  Yarn) so example code is correct, not recalled. Engine-neutral practice skills
  cite the catalog's already-verified engine docs and stay API-agnostic.
- **Pseudocode + one concrete dialect.** Snippets are GDScript-/Python-like with
  explicit RIGHT/WRONG contrasts; shader code is GLSL with an HLSL mapping table.
- **Depth in `references/`** to keep every `SKILL.md` lean and within budget.
- **`dialogue-systems` owns Ink/Yarn**; `procedural-gen` owns noise/RNG — matching
  the locked de-duplication decisions so genres consume rather than re-teach.

## Verification
- `python scripts/validate-skills.py` → **"Validated 10 skill file(s). All checks
  passed."** (the golden `love2d-core` + the 9 new disciplines).
- All `SKILL.md` are 144–179 lines (< 500); every `references/` link resolves;
  frontmatter has no forbidden keys; `name` equals folder for all nine.
- Manual rubric pass: each skill has when-to-use / when-not (naming the sibling
  skill), a numbered workflow, ≥3 version-pinned patterns, pitfalls, references,
  and related-skills cross-links.
- Skills authored: 9; all pass the rubric in `docs/SKILL-FORMAT.md`: yes.

## Sources consulted (primary docs)
- Red Blob Games — *Introduction to the A\* Algorithm* (pathfinding, heuristics).
- Red Blob Games — *Making maps with noise functions* (octaves, redistribution,
  biomes, islands).
- inkle — *Writing with ink* (official Ink language documentation).
- Yarn Spinner docs — *Scripting Fundamentals* (nodes/lines, logic & variables).
- Engine docs referenced via the catalog for cross-links (Godot, Unity, Unreal
  audio/physics/input/navigation pages) — used to keep concepts API-accurate
  without re-teaching the engine APIs the engine skills own.

## Handoff to next sessions
- The router session (S12) can route all nine disciplines: descriptions embed the
  trigger vocabulary (`says:`) and each skill names the engine skills it pairs
  with for composition.
- Genre skills (S10) can compose these directly: `roguelike`/`survival-crafting`
  → `procedural-gen`; `rpg`/`visual-novel` → `dialogue-systems` + `save-systems`;
  `platformer`/`fps-shooter` → `input-systems` + `physics-tuning` + `game-ai`.
- Cross-links point outward to engine skills (S06–S08) by bare name; those skills
  need no changes to satisfy the references.

## If partial — remaining work
- None for S09. (Validation of cross-links *into* engine skills is naturally
  deferred to S13 QA, once those skills exist on the integration branch.)
