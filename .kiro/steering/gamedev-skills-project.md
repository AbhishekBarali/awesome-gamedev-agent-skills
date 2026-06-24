---
inclusion: always
---

# Project: awesome-gamedev-agent-skills

An open, original collection of high-quality **game-development Agent Skills**
(`SKILL.md` files) plus a **master router** skill, for AI coding agents
(Claude Code, Kiro, Gemini CLI, Codex, Cursor). Built across many sessions.

## At the start of EVERY session
1. Read `docs/progress/INDEX.md` and run `git log --oneline -10` to learn what is done.
2. If you will author or edit skills, read `docs/SKILL-FORMAT.md` (the authoring standard).
3. Work only within the scope of the session prompt you were given.

## Non-negotiable rules
- **Originality.** Never copy text or code from other repos/skills. Study sources for
  *patterns only*, then write everything from scratch from primary documentation.
- **Quality over quantity.** A correct, tested, lean skill beats five generic ones.
- **Follow the spec.** `name` ≤64 chars (lowercase, digits, hyphens; no leading/trailing
  hyphen; equals its folder name). `description` ≤1024 chars, says *what it does AND when
  to use it*. Keep each `SKILL.md` under ~500 lines; push depth into `references/`.
- **Verify code.** Example code must be correct, idiomatic, and version-pinned. State the
  engine/runtime version. Do not invent APIs.
- **No growth/marketing motive in any committed file.** No "stars", launch, or
  "beat competitor X" language in the repo. That lives only in local `plan/` files.
- **Web research = Firecrawl** (per global rule). Use `firecrawl-research-index` /
  `firecrawl_research_*` for docs/papers; `firecrawl_search`/`firecrawl_scrape` for the web.
- **Fan out with subagents** for independent work (research N sources, author N skills),
  then validate and commit from the main session.

## Git & progress (details in plan/00-MASTER-PLAN.md, which is local-only)
- Conventional commits: `feat(godot): add godot-tilemap skill`, `docs: ...`, `chore: ...`.
- Stage only your own files (`git add <paths>`) — never `git add .` during parallel waves.
- Each session updates `docs/progress/SESSION-XX-*.md` and `docs/progress/INDEX.md`, then commits & pushes.
- Sessions are **resumable**: check what already exists and continue; don't redo finished work.
