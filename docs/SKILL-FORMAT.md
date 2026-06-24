# Skill Authoring Standard

This is the canonical standard for every skill in this repository. It is the
contract that keeps 60+ skills, written across many sessions, consistent and
high quality. Read it fully before authoring or reviewing a skill.

> Format basis: the **Agent Skills open standard** (agentskills.io) used by Claude
> Code, the Claude Agent SDK, Kiro, and compatible agents.

---

## 1. What a skill is

A skill is a **directory** containing a `SKILL.md` file and, optionally,
supporting folders. The agent pre-loads only the `name` + `description` of every
skill; it reads the body **on demand**, and reads bundled files **only when
needed**. This is *progressive disclosure* — design for it.

```
skills/<category>/<skill-name>/
├── SKILL.md            # required — the playbook (keep < 500 lines)
├── references/         # optional — deep docs the agent reads on demand
│   └── *.md
├── scripts/            # optional — runnable, deterministic helpers
│   └── *.{py,sh,gd,...}
└── assets/             # optional — templates, configs, sample files
```

---

## 2. Frontmatter (required + optional fields)

```yaml
---
name: godot-tilemap                # REQUIRED. ≤64 chars. lowercase a-z, 0-9, hyphens.
                                   #   No leading/trailing hyphen. MUST equal the folder name.
description: >                     # REQUIRED. ≤1024 chars. Third person.
  Build and edit TileMaps/TileSets in Godot 4 — terrain autotiling, collision and
  navigation layers, custom tile data, and runtime tile updates. Use when the user
  is building 2D levels, tile-based worlds, or asks about TileMap/TileSet in Godot.
license: Apache-2.0                # optional
compatibility: Godot 4.2+          # optional, ≤500 chars (engine/runtime/network needs)
metadata:                          # optional, arbitrary key/values
  engine: godot
  category: godot
  difficulty: intermediate
# allowed-tools: ...               # optional, experimental — usually omit
---
```

### Writing the `description` (this is the most important line you write)
The agent decides whether to trigger the skill almost entirely from `name` +
`description`. A weak description = a skill that never fires or fires wrongly.

- Lead with **what it does**, then **when to use it** ("Use when …").
- Include the concrete **trigger vocabulary** a user would actually type
  (engine name, node/class names, genre words, file types).
- Be specific and disambiguating. `godot-2d-platformer` should not fire for a 3D FPS.
- Third person, no "I". No marketing adjectives ("amazing", "best").

---

## 3. Body structure (the SKILL.md playbook)

Keep it scannable, imperative, and lean. Recommended sections:

1. **Title + one-line purpose.**
2. **When to use / when not to use** — sharpen the trigger boundary.
3. **Core workflow** — numbered, decision-oriented steps the agent follows.
4. **Key patterns / recipes** — short, correct, idiomatic code blocks for the
   most common tasks. Show the *right* way; name the *wrong* way to avoid.
5. **Pitfalls & gotchas** — version traps, performance footguns, common bugs.
6. **References** — point to `references/*.md` for depth ("For X, read references/x.md").
   Push long tables, API dumps, and rarely-needed detail into `references/`.

Principles:
- **Procedural, not encyclopedic.** Tell the agent *how to act*, not everything known.
- **Decisions first.** Help the agent choose between approaches for the situation.
- **One responsibility per skill.** If it sprawls, split it and let the router compose.
- **< 500 lines.** If you exceed it, move detail into `references/`.

---

## 4. Code & technical accuracy

- Code must be **correct and idiomatic** for the stated engine version. Do not invent
  APIs, signals, or methods. When unsure, verify against **primary docs** (official
  engine documentation) via Firecrawl before writing.
- **Pin versions.** State the engine/runtime version the patterns target
  (e.g., "Godot 4.3", "Unity 6 / 2022 LTS", "Unreal 5.4", "Bevy 0.14").
- Prefer **minimal, runnable** snippets over large dumps. Each snippet should make one point.
- Note breaking changes between major versions where it matters (e.g., Godot 3 → 4).
- `scripts/` are for **deterministic** helpers the agent can run (generators, validators,
  converters). Make them self-contained and documented at the top.

---

## 5. Originality & licensing (mandatory)

- **Write from scratch from primary sources.** Other repos/skills may be studied for
  *structure and ideas only*. Never paste their prose or code.
- Cite **primary documentation** (official engine/framework docs) as the source of truth,
  not third-party skills.
- All skills are licensed **Apache-2.0** (repo default). If a pattern is genuinely derived
  from a permissively licensed source, attribute it in `NOTICE`.
- The QA session runs an originality pass; anything resembling copied content is rewritten.

---

## 6. Quality rubric (a skill ships only if every box is true)

- [ ] Folder name = `name` = lowercase/hyphen, ≤64 chars, unique in the repo.
- [ ] `description` ≤1024 chars; states what + when; contains real trigger words; disambiguated.
- [ ] `SKILL.md` < 500 lines; depth pushed to `references/`.
- [ ] Body has: when-to-use, core workflow, ≥2 correct code patterns, pitfalls, references.
- [ ] All code is version-pinned, idiomatic, and verified against primary docs (no invented APIs).
- [ ] Original prose & code — no copied content; primary sources cited.
- [ ] No growth/marketing language. No secrets. No external network calls in scripts unless documented.
- [ ] Renders cleanly as Markdown; valid YAML frontmatter; internal links resolve.
- [ ] Passes the validator (`scripts/validate-skills.*` — added in the scaffolding session).

---

## 7. Cross-agent compatibility

The `SKILL.md` open standard is the portable core. Notes:
- **Claude Code / Kiro / Claude Agent SDK:** consume `SKILL.md` natively.
- **Cursor / Windsurf / Cline / Gemini CLI / Codex:** support varies; we ship a thin
  compatibility doc (`docs/COMPATIBILITY.md`) and, where useful, generated adapters
  (e.g., rules files) rather than forking each skill. Never embed agent-specific hacks
  in the core `SKILL.md`.

---

## 8. Example: a minimal, correct skill

```markdown
---
name: love2d-core
description: >
  Structure a LÖVE (Love2D) game in Lua — the love.load/update/draw loop, delta-time
  movement, input handling, and state stacks. Use when building or debugging a Love2D
  (.love) game or when the user mentions LÖVE, love.run, or main.lua.
license: Apache-2.0
compatibility: LÖVE 11.x (Lua 5.1/LuaJIT)
metadata: { engine: love2d, category: other-engines, difficulty: beginner }
---

# Love2D Core

Use when starting or debugging a LÖVE game. Not for asset art or shader work
(see `disciplines/shader-programming`).

## Core workflow
1. Confirm `main.lua` defines `love.load`, `love.update(dt)`, `love.draw`.
2. Drive all motion by `dt` (frame-rate independence). ...

## Patterns
... correct, version-pinned Lua snippets ...

## Pitfalls
- Forgetting `dt` → speed varies with FPS. ...

## References
- For state management, read `references/state-stack.md`.
```
