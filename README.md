<!-- markdownlint-disable MD033 MD041 -->

# awesome-gamedev-agent-skills

An open, original collection of high-quality game-development **Agent Skills**
(`SKILL.md` files) plus a **master router** skill for AI coding agents.

<!-- badges -->
<!-- TODO: add badges (license, validator CI, skill count) once CI is set up -->
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Format](https://img.shields.io/badge/format-Agent%20Skills-informational)

> Status: early scaffolding. Skills are authored across multiple sessions; see
> [`docs/progress/INDEX.md`](docs/progress/INDEX.md) for the current build state.

## What this is

[Agent Skills](docs/SKILL-FORMAT.md) are small, focused capability files an AI coding
agent can load on demand. This repository provides:

- **Specialized skills** for major engines (Godot, Unity, Unreal), web engines, and
  other frameworks, plus cross-cutting **disciplines**, **genres**, and **workflows**.
- A **master router** skill that detects the engine and task from a request and points
  the agent at the right specialized skill — so you install once and let it route itself.

Every skill is written from primary documentation, version-pinned, and verified.

## Quick start (router)

> The router is authored in a later session. Once available:

1. Install the collection into your agent's skills directory (see
   [`docs/INSTALLATION.md`](docs/INSTALLATION.md)).
2. Ask your agent a game-dev question (e.g. "add a double jump to my Godot player").
3. The router detects the engine + task and loads the matching skill automatically.

## Catalog

> Tables are filled in as skills land. See [`skills/`](skills/) and
> [`docs/progress/INDEX.md`](docs/progress/INDEX.md) for current contents.

### Engines

| Engine | Skills | Folder |
|--------|:------:|--------|
| Godot | _pending_ | [`skills/godot/`](skills/godot/) |
| Unity | _pending_ | [`skills/unity/`](skills/unity/) |
| Unreal | _pending_ | [`skills/unreal/`](skills/unreal/) |
| Web engines | _pending_ | [`skills/web-engines/`](skills/web-engines/) |
| Other engines | _pending_ | [`skills/other-engines/`](skills/other-engines/) |

### Disciplines / Genres / Workflows

| Category | Skills | Folder |
|----------|:------:|--------|
| Disciplines | _pending_ | [`skills/disciplines/`](skills/disciplines/) |
| Genres | _pending_ | [`skills/genres/`](skills/genres/) |
| Workflows | _pending_ | [`skills/workflows/`](skills/workflows/) |

## Compatibility

The portable core is the `SKILL.md` open standard, which works across multiple AI coding
agents. A compatibility matrix lives in [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and the authoring
standard in [`docs/SKILL-FORMAT.md`](docs/SKILL-FORMAT.md). Every skill must pass the
validator (`scripts/validate-skills.py`) and the rubric before merge.

## Repository layout

```
skills/        specialized skills, grouped by engine / discipline / genre / workflow
router/        the master router skill
docs/          authoring standard, installation, compatibility, build log
templates/     SKILL.md template
scripts/       validator and tooling
```

## License

[Apache-2.0](LICENSE). See [`NOTICE`](NOTICE) for attribution and trademark notes.
