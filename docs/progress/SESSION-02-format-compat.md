# Session 02 — Format & Cross-Agent Compatibility

> Public build-log entry. Value-focused only.

- **Session:** S02
- **Wave:** 1
- **Date (UTC):** 2026-06-24
- **Depends on:** none
- **Status:** complete
- **Branch / commits:** none (Wave-1 research session — no git performed)

## Objective
Establish the definitive compatibility + packaging reference for the collection: confirm the
portable `SKILL.md` open standard and document exactly how each target AI coding agent discovers,
installs, and triggers a skill — so our skills install everywhere and the validator checks the
right things.

## What was produced
- **Cross-agent compatibility reference** (full per-agent breakdown + matrix + portable-core rule
  + install snippets + validator spec). Feeds the public `docs/COMPATIBILITY.md` (published in S05)
  and `docs/INSTALLATION.md` (S14).
- **Compatibility matrix** covering Claude Code, Claude Agent SDK, Claude.ai, Kiro, Gemini CLI,
  Codex CLI, Cursor, Windsurf, Cline (native-skills? × format × install path × trigger × adapter?).
- **Validator check-list** (26 checks, ERROR/WARN severities) specifying S04's `scripts/validate-skills`.
- **Adapter strategy** for the three rules-based editors (generated, never hand-forked).

## Key decisions
- **The portable core is the Agent Skills open standard `SKILL.md`** — only `name`, `description`,
  and the optional `license`/`compatibility`/`metadata` fields live in a committed skill. No
  agent-specific frontmatter is ever baked into the source.
- **Five surfaces consume our `SKILL.md` natively:** Claude Code, Claude Agent SDK, Claude.ai
  (zip upload), Kiro, Gemini CLI, Codex CLI. The cross-client drop-in directory is
  `.agents/skills/<name>/SKILL.md` (read natively by Codex and Gemini); Claude Code uses
  `.claude/skills/`, Kiro uses `.kiro/skills/`.
- **Cursor, Windsurf, and Cline are rules-based** (`.mdc` / `.md` rules), not skill-based. We
  **generate** a rules file per skill into `scripts/adapters/<target>/` rather than forking skills.
  Cline has no description-driven trigger, so its adapter folds the description into the body.
- **`name` must equal its folder name** and match `^[a-z0-9]+(-[a-z0-9]+)*$`; `description` ≤1024,
  but a soft ≤200-char target keeps skills uploadable to Claude.ai.
- **Steering ≠ skills (Kiro):** steering is Kiro-only persistent project context; skills are the
  portable, on-demand, model-invoked capability packages — our product is skills.

## Verification
- Open-standard frontmatter fields/limits, directory rules, and progressive-disclosure tiers were
  verified directly against the canonical specification (`agentskills.io/specification`).
- Kiro's skill mechanism (`.kiro/skills/` + `~/.kiro/skills/`, `skill://` resources, `/skill-name`,
  frontmatter fields) was verified directly against the primary Kiro CLI docs (updated 2026-05-12).
- Remaining agents were researched in parallel against their primary/official docs; each claim in
  the reference carries a source URL, and items not re-verified in-session are flagged for a
  direct re-check at S05.
- Skills authored: 0 (research session). No code changed; nothing to build.

## Sources consulted (primary docs)
- `https://agentskills.io/specification` — open-standard frontmatter, limits, disclosure (verified).
- `https://kiro.dev/docs/cli/skills/` — Kiro skill paths, `skill://`, triggers (verified).
- `https://docs.claude.com/en/docs/claude-code/skills` and `/en/api/agent-sdk/skills` — Claude Code + SDK.
- `support.claude.com` skills articles — Claude.ai zip upload + limits.
- `https://docs.cursor.com/context/rules`, `https://docs.windsurf.com/plugins/cascade/memories`,
  `https://docs.cline.bot/customization/cline-rules` — rules formats.
- `github.com/google-gemini/gemini-cli` docs and `https://developers.openai.com/codex/skills` — Gemini + Codex.

## Handoff to next sessions
- **S04** implements the validator check-list as `scripts/validate-skills.*` and builds the adapter
  generator + install helper under `scripts/`.
- **S05** publishes `docs/COMPATIBILITY.md` from this reference and folds format refinements
  (e.g. the Claude.ai 200-char portability note) into `docs/SKILL-FORMAT.md`.
- **S14** finalizes the per-agent install snippets into `docs/INSTALLATION.md`.

## If partial — remaining work
- Not partial. Follow-up (non-blocking) flags for downstream sessions:
  - [ ] Re-verify Claude Code / Gemini / Codex install paths directly at S05.
  - [ ] Confirm Windsurf's current per-file character cap against live docs.
  - [ ] Decide whether generated adapters are committed or treated as build artifacts.
