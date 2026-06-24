# Session S03 — Domain Taxonomy & Source Map

> Public build-log entry. Value-focused only.

- **Session:** S03
- **Wave:** 1
- **Date (UTC):** 2026-06-24
- **Depends on:** none
- **Status:** complete
- **Branch / commits:** none this session (Wave-1 writes files only; S04 initializes git, S05 commits Wave-1 outputs)

## Objective
Freeze the v1 skill catalog (62 skills across 8 categories, Godot deepest) and build an
authoritative source map of **verified official-documentation URLs** so authoring sessions
never have to re-discover where to learn each topic.

## What was produced
- `plan/research/03-taxonomy-sources.md` — the catalog + source map: one table per category
  with each skill's final name, one-line scope, target version, difficulty, 2–4 verified
  primary-doc URLs, and router signals (file detection + phrase triggers); plus an
  overlaps/composition section and per-category counts.

## Key decisions
- **62 skills, quality-first**, distributed godot 15 · unity 8 · unreal 6 · web-engines 6 ·
  other-engines 5 · disciplines 9 · genres 9 · workflows 4. Counts chosen for
  single-responsibility coverage, not totals.
- **Engine vs concept split.** Engine skills teach the engine's API; `disciplines/*` teach
  the portable concept and defer to the detected engine skill (e.g. `godot-audio` ↔
  `audio-design`, `unity-input-system`/`unreal-enhanced-input` ↔ `input-systems`).
- **Genres are compositional** — they orchestrate engine + discipline skills into a working
  template and never re-teach primitives; the router composes them.
- **Version pinning** captured per skill: Godot 4.x stable, Unity 6 LTS, Unreal 5.4+,
  Phaser 3.90, PixiJS v8, three.js r165+, Bevy 0.16+ (pin hard), pygame 2.6, LÖVE 11.5.
- Dropped a separate `godot-save-load` in favour of cross-engine `save-systems`; gave Roblox
  a dedicated `roblox-datastores` skill because its persistence model is distinct.

## Verification
- Primary-doc URLs checked with **Firecrawl** (`firecrawl_map` + `firecrawl_scrape`) on
  2026-06-24. Every domain's canonical root and a representative set of cited deep links
  returned **HTTP 200** / valid index. A small number of pages are cited by their
  identical, confirmed slug pattern (marked **†** in the catalog) for later re-verification.
- Correction surfaced and recorded: **Bevy's official site is now `bevy.org`** (not
  `bevyengine.org`); Unity docs serve the 6.5 manual; Unreal docs serve UE 5.8.
- Skills authored: 0 (this is a taxonomy/source-map session). All 62 names validated as
  spec-compliant: lowercase-hyphen, ≤64 chars, unique, equal to folder names.

## Sources consulted (primary docs)
- `https://docs.godotengine.org/en/stable/` — Godot class reference + tutorials + getting-started.
- `https://docs.unity3d.com/Manual/` — Unity 6 manual (input, physics, animation, data, build).
- `https://dev.epicgames.com/documentation/en-us/unreal-engine/` — UE 5.8 (Blueprints, C++, Enhanced Input, Behavior Trees, Niagara, packaging).
- `https://docs.phaser.io/`, `https://pixijs.com/8.x/guides/`, `https://threejs.org/manual` — web engines.
- `https://bevy.org/learn/`, `https://www.pygame.org/docs/`, `https://love2d.org/wiki/love`, `https://create.roblox.com/docs` — other engines.
- `https://docs.yarnspinner.dev/`, `https://www.inklestudios.com/ink/` — dialogue tooling.
- `https://partner.steamgames.com/doc/home`, `https://itch.io/docs/creators/getting-started`, `https://itch.io/docs/butler` — publishing workflows.

## Handoff to next sessions
- **S05** can freeze the 62 names into `skills/<category>/<name>/` and draft the router spec
  directly from the *Router signals* columns.
- **S06–S11** author from the *Primary sources* columns (re-verify the exact page and pin to
  the listed version before writing code).
- **S12** uses the overlaps/composition rules to build the master router.

## If partial — remaining work
- None. Catalog and source map complete. (No git this session by Wave-1 rule.)
