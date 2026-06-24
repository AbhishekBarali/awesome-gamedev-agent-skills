# Session 01 — Landscape & Skill-Craft Teardown

> Public build-log entry. Value-focused only. No growth/marketing/strategy language.

- **Session:** S01
- **Wave:** 1
- **Date (UTC):** 2026-06-24
- **Depends on:** none
- **Status:** complete
- **Branch / commits:** none this session — S01 only writes files; Wave-1 outputs are
  committed later in the build process (no git performed here).

## Objective
Study how existing AI-agent **Agent Skills** collections are built — game-dev ones plus the
strongest general collections — and distil concrete, primary-source-grounded principles for
what makes a skill excellent versus weak, to sharpen our authoring standard and catalog.
Research only: no skills authored, patterns studied but never copied.

## What was produced
- `plan/research/01-landscape.md` — full teardown: a multi-group sources table, in-depth
  studies of the strongest collections, "what great skills do", anti-patterns, repo/README
  conventions, gaps & opportunities, and a publishable "lessons for our authoring standard"
  (L1–L10) that S05 can fold into `docs/SKILL-FORMAT.md`.
- `plan/research/_scratch-sources.md` — raw triage notes and the complete source list.
- This progress entry.

## Coverage
- **40+ sources triaged**; **19 studied in depth** across four areas: the open standard and
  runtime docs, general-collection flagships, Godot game-dev collections, and
  multi-engine/studio collections plus curation sites.
- Findings cross-checked: every headline repository statistic was verified against the
  authoritative GitHub API rather than taken from page estimates.

## Key decisions / takeaways
- **Description is the routing rule.** The single highest-leverage line in a skill is the
  `description`: it must state what the skill does, when to use it, and the exact words a
  developer types (engine + version, node/class names, file types, genre), lead with the
  primary use case, and fit the retrieval budget.
- **Progressive disclosure with explicit budgets.** Tiny always-loaded metadata; a lean
  `SKILL.md` body (target <500 lines) focused on how to act; depth in `references/`,
  deterministic helpers in `scripts/`, templates in `assets/`.
- **One responsibility per skill**, split by gameplay system and node/class, composed by a
  catalog/router rather than collapsed into broad mega-skills.
- **Pin versions and verify against primary docs**; note API changes across engine versions;
  never invent APIs. For games, **verify by running/observing** (headless runs, screenshots,
  playtests), not by assuming compilation implies correctness.
- **Enforce the standard mechanically** (validator + CI: `name` == folder, required
  frontmatter, description quality, size/token budget, resolved cross-references,
  originality) and keep the `SKILL.md` core agent-neutral for portability.
- **A master router is a high-value capability.** Existing collections require hand-picking
  skills or rely on orchestrators / studio hierarchies / static index skills. An
  install-once router that detects the engine and task and dispatches to the right
  specialized skill is a worthwhile architecture for our collection.

## Verification
- Source-coverage check: ≥40 sources triaged and ≥15 studied in depth — met (40+ / 19).
- Repository statistics verified against `api.github.com` (2026-06-24).
- Deliverable check: sources table + distilled lessons + opportunities + a publishable,
  value-only lessons section all present in `plan/research/01-landscape.md`.
- Skills authored: 0 (research-only session); rubric in `docs/SKILL-FORMAT.md` not
  applicable this session.

## Sources consulted (primary docs)
- agentskills.io/specification — the Agent Skills open standard: frontmatter fields, naming
  grammar, and the three-tier progressive-disclosure budgets.
- code.claude.com/docs/en/skills — Claude Code authoring/runtime: description retrieval
  budget, `when_to_use`, invocation-control fields, subagent dispatch, discovery rules.
- platform.claude.com — Agent Skills overview (API view of skills as modular capabilities).
- developers.openai.com/codex/skills — Codex CLI skill discovery and cross-agent layout.
- anthropic.com/engineering — design rationale for progressive disclosure and
  description-driven activation.

## Handoff to next sessions
- **S05 (standards lock & router spec):** adopt the open standard as the floor and layer
  lessons L1–L10 into `docs/SKILL-FORMAT.md`; treat the master router as the headline
  architecture; turn the anti-patterns list into validator/QA checks.
- **S03 (taxonomy & source map):** use the sources table as a starting map of the space.
- **S04 (scaffolding/validator):** the anti-patterns and conventions define concrete
  validator rules (naming, frontmatter, size/token budget, link integrity, originality).

## If partial — remaining work
- None. Session complete.
