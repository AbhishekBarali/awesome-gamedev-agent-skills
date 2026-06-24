# Save versioning, migration, and robustness

Saves outlive the code that wrote them. A player who saved in v1.0 expects to
load in v1.4 after an update. Plan for schema evolution from the first release.

## The version field is non-negotiable

Stamp every save with an integer `version` (or a structured `{major, minor}` if
you need it). On load:

1. Read `version`.
2. If it is **newer** than the running build → refuse with a clear message
   ("This save is from a newer version"). Do not guess at fields you don't know.
3. If it is **older** → run migrations in sequence until it matches the current
   version.
4. Validate, then instantiate.

Prefer a single monotonic integer. Semantic two-part versions are only worth it
if you genuinely branch save compatibility across release lines.

## The migration chain

Write each migration as a **pure function** `vN -> vN+1` and apply them in order.
This keeps any version reachable to current with small, testable steps — never a
giant "convert anything to latest" function.

```python
SAVE_VERSION = 4

MIGRATIONS = {
    1: migrate_1_to_2,   # added "flags" map
    2: migrate_2_to_3,   # split "name" into first/last
    3: migrate_3_to_4,   # inventory items gained a "durability" field
}

def upgrade(data):
    v = data.get("version", 1)
    while v < SAVE_VERSION:
        data = MIGRATIONS[v](data)
        v += 1
        data["version"] = v
    return data
```

Guidelines:

- **Additive changes are easy**: new field with a default. The migration just
  inserts the default for old saves.
- **Renames/restructures**: move/transform in the migration; never read both old
  and new names in game code.
- **Removed fields**: drop them in the migration so later steps see a clean shape.
- **Keep old migrations forever.** Deleting `migrate_1_to_2` strands every v1
  save. They are cheap to keep and must remain a faithful record.
- **Test the chain**: keep a corpus of real saves from each shipped version and
  assert they load after every change (this is your regression net).

## Backups and rollback

- Before overwriting, copy the current save to `*.bak`. On a failed load of the
  primary, try the backup automatically.
- For autosaves, rotate a small ring (autosave_0..2) so a bad autosave doesn't
  destroy the only recent state.
- Consider a checksum/hash of the payload to detect truncation or corruption
  (distinct from anti-tamper, which a determined local player can always defeat).

## Format trade-offs

| Format | Pros | Cons | Use when |
|---|---|---|---|
| JSON / text | Human-readable, debuggable, diff-able, easy migration | Larger, slower, trivially editable | Default; most games |
| Binary (engine) | Compact, fast, mildly opaque | Hard to debug/migrate, version-fragile | Large state, perf-critical |
| Key/value store | Simple, robust per-key | No structure, manual schema | Settings, small flag sets |
| Cloud KV (e.g. DataStore) | Cross-device | Quotas, latency, conflicts | Online/cross-device saves |

Whatever the on-disk format, keep an **in-memory dictionary/struct** as the
canonical shape and (de)serialize at the boundary. Migrations then operate on
that neutral shape, not on format-specific bytes.

## Load-time validation checklist

- Required keys present; types correct (string vs number vs bool).
- Numbers within sane ranges (no NaN/Infinity; hp ≥ 0; indices in bounds).
- Enum/id values still exist in current content (an item id removed in a patch
  must be handled — drop it or substitute, don't crash).
- References resolve (a quest id points to a known quest).
- On any failure: log, fall back to backup, and if all else fails, fail *loudly*
  to the player rather than silently loading a broken state.

## What to store vs recompute

- **Store** authoritative, non-derivable state: choices, unlocked flags, RNG
  seed, inventory, positions.
- **Recompute** derived data on load (full stat tables from base + modifiers,
  procedural maps from the seed). Saving derived data invites desync when the
  formula changes in a patch — and bloats the file.
