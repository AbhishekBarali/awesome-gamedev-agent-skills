# AGENTS.md

Orientation for AI coding agents working **in this repository** (authoring or editing
skills). If you are an end user trying to *use* these skills, see
[`README.md`](README.md) and [`docs/INSTALLATION.md`](docs/INSTALLATION.md) instead.

## What this repo is

An original, cross-engine collection of game-development Agent Skills (`SKILL.md` files)
plus a master router skill. The portable core is the `SKILL.md` open standard.

## Before you write or edit a skill

1. Read [`docs/SKILL-FORMAT.md`](docs/SKILL-FORMAT.md) — the authoring standard.
2. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) — the rubric and commit conventions.
3. Check [`docs/progress/INDEX.md`](docs/progress/INDEX.md) to see what already exists;
   do not redo finished work.
4. Start from [`templates/SKILL.template.md`](templates/SKILL.template.md).

## Rules

- **Originality.** Write from primary documentation. Never copy text/code from other
  repos or skill collections — study for patterns only.
- **Spec compliance.** `name` ≤64 chars (lowercase/digits/hyphens, no leading/trailing
  hyphen, equals the folder name). `description` ≤1024 chars and says *what it does and
  when to use it*. Keep `SKILL.md` under ~500 lines; push depth into `references/`.
- **Verify code.** Examples must be correct, idiomatic, and version-pinned. State the
  engine/runtime version. Do not invent APIs.
- **No growth/marketing language** in any committed file.

## Layout

```
skills/<category>/<skill-name>/SKILL.md   the skills
router/SKILL.md                           the master router
docs/                                     authoring standard, install, compatibility
templates/SKILL.template.md               starting point for a new skill
scripts/validate-skills.py                frontmatter/size/link validator
```

## Verify before committing

```bash
python scripts/validate-skills.py
```

Fix every reported failure before you commit. Use conventional commits
(`feat(<category>): …`, `docs: …`, `chore: …`) and stage only the files you changed.
