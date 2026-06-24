# router/

Home of the **master router** skill (`SKILL.md`), authored in a later session.

The router auto-detects the engine and task from a request and points the agent to the
right specialized skill in [`../skills/`](../skills/), so the collection installs once
and routes itself instead of requiring manual skill selection.

See [`../docs/SKILL-FORMAT.md`](../docs/SKILL-FORMAT.md) for the authoring standard.
