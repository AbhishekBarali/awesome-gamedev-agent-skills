# Build log — awesome-gamedev-agent-skills

How this collection was built: the decisions that shaped it, what each phase produced,
and how every claim was verified. This is the consolidated, value-focused narrative;
the per-phase detail lives in [`progress/`](progress/INDEX.md).

> Value-focused only. No growth or marketing material lives anywhere in this repository.

## What shipped

An original, cross-engine collection of **62 game-development Agent Skills** plus a
**master router** skill, in the portable `SKILL.md` open-standard format, for AI coding
agents (Claude Code, Claude Agent SDK, Claude.ai, Kiro, Gemini CLI, Codex CLI, and — via
generated adapters — Cursor, Windsurf, Cline).

| Category | Count | Coverage |
|----------|:-----:|----------|
| Godot | 15 | GDScript & C#, nodes/scenes, 2D/3D, physics, UI, animation, shaders, audio, multiplayer, export |
| Unity | 8 | C# scripting, Input System, physics, animation, ScriptableObjects, 2D tilemap, NavMesh, build pipeline |
| Unreal | 6 | Blueprints, C++ gameplay, Enhanced Input, Behavior Trees, Niagara, packaging |
| Web engines | 6 | Phaser 3 (core + arcade physics), PixiJS v8, three.js (scene, glTF, materials/lighting) |
| Other engines | 5 | Bevy ECS, pygame, LÖVE, Roblox (Luau + DataStores) |
| Disciplines | 9 | game-ai, procedural-gen, dialogue-systems, save-systems, audio-design, shader-programming, physics-tuning, level-design, input-systems |
| Genres | 9 | platformer, roguelike, rpg, fps-shooter, tower-defense, card-game, visual-novel, survival-crafting, puzzle |
| Workflows | 4 | game-jam, prototype-fast, steam-publish, itch-publish |
| **Total** | **62** | **+ 1 master router** |

The differentiator is the router: every skill is independently useful, but the router
detects a project's engine and the user's task and composes the right minimal set —
install once, and it routes itself.

## How it was built

Work ran as a directed graph of self-contained sessions across six waves. Research and
authoring fanned out in parallel; integration, QA, and release happened at single
sequential sessions. Each session committed its own files and left a public progress entry.

### Wave 1 — Research & scaffolding (S01–S04)

Four parallel research/setup sessions established the foundation before any skill was written.

- **Landscape & skill-craft teardown (S01).** Studied 40+ existing skill collections (19 in
  depth) for *patterns only*, never copying, and distilled ten authoring lessons. The
  highest-leverage finding: a skill's `description` is its routing rule — it must say what the
  skill does, when to use it, and the exact words a developer types. A second: a master router
  is a high-value capability no existing collection offered.
- **Format & cross-agent compatibility (S02).** Confirmed the `SKILL.md` open standard as the
  portable core and mapped how nine agent surfaces discover, install, and trigger skills.
  Decided the committed skill carries only `name`/`description`/optional `license` — never
  agent-specific frontmatter — and that the three rules-based editors are reached through
  *generated* adapters rather than hand-forked copies.
- **Domain taxonomy & source map (S03).** Froze a 62-skill catalog across eight categories
  (Godot deepest) and built a source map of verified primary-documentation URLs so authoring
  sessions never had to rediscover where to learn each topic. Counts were chosen for
  single-responsibility coverage, not for a round number.
- **Repo scaffolding & infrastructure (S04).** Stood up the directory layout, Apache-2.0
  `LICENSE` + `NOTICE`, contributor docs, and a dependency-free Python validator
  (`scripts/validate-skills.py`) checking frontmatter limits, `name`==folder, the <500-line
  budget, and reference-link integrity. Established the rule that only public paths are ever
  staged; orchestration and strategy files stay local via `.gitignore`.

### Wave 2 — Standards lock & router spec (S05, the gate)

A single gate session turned the research into frozen, committed standards so the six
authoring sessions could run from committed files alone:

- `docs/SKILL-FORMAT.md` — the locked authoring standard (frontmatter limits, the rubric
  tied to the validator, the forbidden agent-specific keys, the claude.ai 200-char note).
- `docs/COMPATIBILITY.md` and `docs/INSTALLATION.md` — the 9-surface support matrix and
  per-agent install steps.
- `docs/skill-catalog.md` — the frozen v1 catalog: the single source of truth for the 62
  names, versions, sources, and router signals.
- `router/ROUTER-SPEC.md` — the router contract (engine detection, task classification,
  routing-table format, progressive-disclosure protocol, composition, fallback).
- A **golden reference skill**, `love2d-core`, authored end-to-end to prove the standard works
  and give the authoring sessions a concrete shape to match.

### Wave 3 — Authoring the skills (S06–S11)

Six parallel sessions, each on its own branch/worktree with disjoint paths, authored the
catalog. Every skill was written from primary documentation, version-pinned to a stated
release, and shaped after the golden skill (routing-rule description, when-to-use boundary,
core workflow, version-pinned patterns, pitfalls, and a `references/` file for depth).

- **Godot — 15 (S06)**, pinned to Godot 4.3+, with explicit 3.x→4.x migration traps per skill
  (`move_and_slide()` signature, `@export`, `Callable` signals, `TileMapLayer`, etc.).
- **Unity 8 + Unreal 6 (S07)**, Unity 6 (6000.0 LTS) and UE 5.4+, calling out the
  version breaks that silently defeat copied code (`Rigidbody.linearVelocity`, the AI
  Navigation package, 2D Tilemap Extras, Enhanced Input as default, Niagara over Cascade).
- **Web + other engines — 6 + 4 (S08)**: Phaser 3.90, PixiJS v8, three.js r165+, Bevy 0.16+
  (restricted to the ECS core stable across 0.16→0.19), pygame-ce, and Roblox
  (server-authoritative by construction).
- **Disciplines — 9 (S09)**: portable concepts/algorithms (A*, noise, Ink/Yarn, fixed
  timestep) that each defer the engine API to the detected engine skill.
- **Genres — 9 (S10)**: compositional playbooks that orchestrate engine + discipline skills
  and never re-teach primitives.
- **Workflows — 4 (S11)**: decision-first shipping playbooks, with the Steam/itch publishing
  steps verified command-by-command against the official tooling docs.

### Wave 4 — Router & integration (S12)

The six authoring branches were merged into `main` conflict-free (disjoint paths), and the
master router was built from its spec: `router/SKILL.md` (the six-step algorithm + routing
table) plus `references/engine-detection.md` and `references/routing-table.md`. An 18-case
engine×task matrix exercised all five engine families, all four categories, file-signal
detection, the unknown-engine fallback, and honest binding-gap cases — every prompt resolved
to a skill that exists.

### Wave 5 — QA, validation & originality (S13)

A full audit against the frozen standard: validator green on all 63 files; rubric checked
across every category; an originality pass confirming no copied prose or code (citations are
primary documentation only); technical spot-checks against primary docs that fixed **22
issues across 14 skills** (2 major: a Godot ray-query `exclude` type and the Godot-C# .NET
version-by-release; 10 minor API corrections; plus trigger and doc fixes). The routing matrix
was re-run with 8 added edge cases (26 total), and the router + one skill per engine family
were smoke-tested in Kiro and Claude Code.

### Wave 6 — Docs polish, consolidation & release (S14–S15)

- **Docs polish (S14).** Rewrote the README around the router with accurate, tree-generated
  catalog tables (counts matching the frozen catalog exactly), real badges (no false CI badge),
  a compatibility summary, and an honest demo placeholder. Added a CONTRIBUTING section on
  updating the router when adding a skill, and corrected the install docs to include the router
  itself as a skill.
- **Final consolidation & release (S15).** This consolidated build log; a final audit
  (validator, link integrity, license/originality, and a separation check confirming no
  orchestration or strategy file is tracked and no growth language is committed); a final
  router integrity pass (all 62 skills reachable, the one missing name is the documented Unity
  2D-movement binding gap); and the tagged **v1.0.0** release.

## Key decisions

- **Quality over quantity.** ~62 correct, lean, verified skills rather than hundreds of generic
  ones; the collection grows by contribution afterward.
- **The catalog is the single source of truth for names.** Authoring sessions built to the
  frozen catalog, not to illustrative placeholder names in their prompts.
- **Engine API vs portable concept.** Engine skills teach the engine's API; discipline skills
  teach the portable algorithm and defer to the detected engine skill; genres compose both and
  never re-teach primitives. The router selects exactly one engine set and adds concepts
  additively.
- **Portable core, generated adapters.** The committed skill is agent-neutral; rules-based
  editors are served by generated adapters, never hand-forked skills.
- **Verify, then pin.** Every load-bearing API was checked against primary docs before writing,
  with the target version stated and the major-version traps called out. No invented APIs.
- **Honesty over coverage.** Where an engine lacks a slot a genre composes, the router states
  the gap and binds to the closest real skills rather than inventing a name.
- **Strict public/local separation.** Product + craft are public; orchestration + strategy are
  local-only and gitignored. No growth motive appears in any committed file.

## Verification & quality gates

| Gate | Result |
|------|--------|
| Validator (`scripts/validate-skills.py`) | 63 files — all checks pass (frontmatter limits, `name`==folder, <500 lines, resolved reference links) |
| Skill count | 62 skills (+ router); per-category counts match `docs/skill-catalog.md` and the README |
| License | All 63 `SKILL.md` declare `Apache-2.0`; repo `LICENSE` + `NOTICE` present and accurate |
| Originality | No copied prose or code; primary-documentation citations only |
| Internal links | No broken internal links across README + docs + skills |
| Router integrity | All 62 skills reachable; the only non-existent name referenced is the explicitly documented Unity 2D-movement binding gap |
| Separation | `plan/`, `*.local.md`, `GAMEDEV-SKILLS-PLAN.md` are gitignored and absent from the tracked set; no growth/marketing language committed |
| Cross-agent | Router + one skill per engine family load in Kiro and Claude Code |

## Session index

The full per-session record (objective, output, decisions, verification, sources) is in
[`docs/progress/`](progress/INDEX.md):

S01 landscape · S02 format & compatibility · S03 taxonomy & sources · S04 scaffolding ·
S05 standards lock & router spec (gate) · S06 Godot · S07 Unity + Unreal · S08 web + other
engines · S09 disciplines · S10 genres · S11 workflows · S12 router + integration ·
S13 QA & originality · S14 README & docs polish · S15 final consolidation & release.
