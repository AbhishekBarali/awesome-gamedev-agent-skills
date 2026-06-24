# Contributing

Thanks for your interest in improving **awesome-gamedev-agent-skills**. This collection
values correct, lean, original skills over volume. Please read this guide and the
authoring standard in [`docs/SKILL-FORMAT.md`](docs/SKILL-FORMAT.md) before opening a PR.

## What a skill is

A skill is a directory containing a `SKILL.md` file (and optionally a `references/`
folder for depth). It lives under the matching category in `skills/`:

```
skills/<category>/<skill-name>/
├── SKILL.md
└── references/        # optional, for deeper material
```

The directory name **must equal** the skill's `name` frontmatter field.

Start from [`templates/SKILL.template.md`](templates/SKILL.template.md).

## Originality (non-negotiable)

Write everything from scratch from **primary documentation** (engine/framework docs,
language references, platform specs). You may study other skills or articles for general
patterns, but never copy their text or code. State the engine/runtime version your
examples target, and verify code is correct and idiomatic — do not invent APIs.

## PR checklist (the rubric)

A skill is ready to merge when all of the following are true:

- [ ] **Frontmatter valid.** `name` is ≤64 chars, lowercase letters/digits/hyphens only,
      no leading/trailing hyphen, and equals the folder name.
- [ ] **Description is a trigger.** `description` is non-empty, ≤1024 chars, and states
      both *what the skill does* and *when to use it*.
- [ ] **Lean body.** `SKILL.md` is under ~500 lines; deeper material is pushed into
      `references/`.
- [ ] **Progressive disclosure.** Name + description are enough to decide relevance; the
      body is loaded on demand.
- [ ] **Correct, version-pinned code.** Examples are tested/idiomatic and name the
      engine/runtime version. No invented APIs.
- [ ] **Original.** No copied text or code; written from primary docs.
- [ ] **Links resolve.** Any `references/` links in the skill point at real files.
- [ ] **Validator passes** (see below).
- [ ] **No growth/marketing language** anywhere in committed files.

## Validator

Run the validator before pushing. It checks every `skills/**/SKILL.md` and
`router/SKILL.md` for frontmatter limits, `name`==folder, file length, and that internal
`references/` links resolve:

```bash
python scripts/validate-skills.py
```

It exits non-zero and prints a report if anything fails.

## Commits & PRs

- Use **conventional commits**: `feat(<category>): …`, `docs: …`, `chore: …`,
  `fix: …`, `refactor: …`. Example: `feat(godot): add godot-tilemap skill`.
- Keep PRs focused — ideally one skill (or one coherent change) per PR.
- Describe what you added/changed and how you verified the example code.

## Code of conduct

Be respectful and constructive. Assume good faith and keep reviews focused on the work.
