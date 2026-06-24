---
name: save-systems
description: >
  Design save/load for game state — choosing what to serialize, file formats,
  save slots, atomic crash-safe writes, schema versioning and migration, and
  autosave. Engine-neutral. Use when the user mentions save system, save/load,
  game state persistence, save slots, autosave, save file corruption, or
  migrating old saves to a new version.
license: Apache-2.0
compatibility: Engine-agnostic. Snippets in GDScript-like / Python pseudocode; pairs with Godot FileAccess/ResourceSaver, Unity serialization, or roblox-datastores.
metadata:
  engine: none
  category: disciplines
  difficulty: intermediate
---

# Save systems

A save file is a **serialized snapshot of game state** that survives restarts.
The hard parts aren't writing bytes — they're choosing *what* to save, writing it
so a crash mid-save can't corrupt it, and reading *old* saves after you ship a
patch. Get those three right and the rest is plumbing.

## When to use

- Use to persist progress: player stats, inventory, world flags, settings,
  positions — across sessions and game updates.
- Use to design save slots, quicksave/autosave, and crash-safe writes.
- Use when old save files break after a content/code change (versioning &
  migration).

**When *not* to use:** for Roblox cloud persistence specifics, use
`roblox-datastores`. For the data model the save serializes (resources/SOs), use
`godot-resources` / `unity-scriptableobjects`. For Godot's `FileAccess`/
`ResourceSaver` and `user://` paths, defer to the Godot engine skill while
applying the patterns here.

## Core workflow

1. **Decide what state is authoritative.** Save the *data* (hp, position, seed,
   unlocked flags), not engine objects or scene nodes. You will reconstruct
   objects from data on load — never serialize live node references.
2. **Define a versioned schema.** Every save embeds a `version` integer. This is
   the single most important field for a game you intend to patch.
3. **Pick a format.** JSON/text for readability and debuggability; a binary
   format for size/speed or mild tamper-resistance. Start with JSON.
4. **Write atomically.** Serialize to a temp file, flush, then rename over the
   real file. A crash leaves either the old save or the new one — never a
   half-written one.
5. **Load defensively.** Read version → migrate up to current → validate →
   instantiate. Keep a backup of the last good save and fall back on parse error.
6. **Autosave on safe boundaries** (level change, checkpoint), throttled, and to a
   separate slot so it can't clobber a manual save.
7. **Verify**: save, fully quit, relaunch, load — and confirm by inspection that
   state matches. Test loading a save from the previous version.

## Patterns

### 1. Serialize state as plain data (not engine objects)

```gdscript
# Build a dictionary of pure data. Each savable object reports its own state.
func capture_state() -> Dictionary:
    return {
        "version": SAVE_VERSION,                 # ALWAYS stamp the schema version
        "player": { "hp": player.hp, "pos": [player.position.x, player.position.y] },
        "inventory": player.inventory.to_array(),  # ids + counts, not Item nodes
        "flags": world.flags,                    # e.g. {"met_guard": true}
        "seed": world.seed,                      # regenerate procedural content
    }

# On load, RECONSTRUCT objects from the data — do not expect live references back.
func apply_state(data: Dictionary) -> void:
    player.hp = data["player"]["hp"]
    player.position = Vector2(data["player"]["pos"][0], data["player"]["pos"][1])
    player.inventory.from_array(data["inventory"])
    world.flags = data["flags"]
```

### 2. Atomic, crash-safe write (temp + rename)

```gdscript
# RIGHT: write to a temp file, then atomically rename over the target.
func save_atomic(path: String, data: Dictionary) -> void:
    var tmp := path + ".tmp"
    var f := FileAccess.open(tmp, FileAccess.WRITE)
    f.store_string(JSON.stringify(data))
    f.flush()                                    # ensure bytes hit disk
    f.close()
    DirAccess.rename_absolute(tmp, path)         # rename is atomic on one volume
# WRONG: opening `path` directly and writing in place — a crash mid-write leaves a
# truncated, unloadable save and destroys the player's progress.
```

Rename-over-target is atomic on the same volume on every major OS — this is the
core trick behind a corruption-resistant save. Keep the previous file as
`path + ".bak"` before the rename for a second layer of safety.

### 3. Versioned load with migration

```python
SAVE_VERSION = 3

def load_save(raw_bytes):
    data = parse(raw_bytes)                  # JSON/binary -> dict
    v = data.get("version", 0)
    if v > SAVE_VERSION:
        raise NewerSaveError(v)              # save is from a newer build; refuse
    while v < SAVE_VERSION:                   # apply migrations in order, v -> v+1
        data = MIGRATIONS[v](data)
        v += 1
        data["version"] = v
    validate(data)                            # check required keys / ranges
    return data

# Each migration is a pure function from one version's shape to the next.
def migrate_1_to_2(d):
    d["flags"] = {k: True for k in d.pop("completed_quests", [])}  # list -> set-map
    return d
MIGRATIONS = {1: migrate_1_to_2, 2: migrate_2_to_3}
```

### 4. Save slots + throttled autosave

```gdscript
const SLOT_PATH := "user://save_%d.json"      # manual slots 0..N
const AUTOSAVE_PATH := "user://autosave.json"  # separate file: never clobbers a slot
var _autosave_cooldown := 0.0

func autosave_if_due(dt: float) -> void:
    _autosave_cooldown -= dt
    if _autosave_cooldown <= 0.0:
        save_atomic(AUTOSAVE_PATH, capture_state())
        _autosave_cooldown = 60.0             # throttle: at most once a minute
# Trigger an immediate autosave on checkpoints/level transitions, not mid-combat.
```

## Pitfalls

- **Serializing engine objects/node paths** ties saves to scene structure;
  renaming a node breaks every old save. Save data, rebuild objects on load.
- **No version field.** The day you ship a patch, every existing save is a
  guessing game. Stamp `version` from version 1.
- **In-place writes** corrupt saves on crash/power loss. Always temp-write then
  rename; keep a `.bak`.
- **Trusting the file blindly.** Saves get truncated, hand-edited, or
  cloud-synced stale. Validate on load and fall back to backup on failure.
- **Floats and locale.** Text serializers can drop precision or use comma
  decimal separators in some locales. Use a locale-invariant serializer.
- **Autosave clobbering manual saves**, or firing mid-action and saving an
  inconsistent state. Use a dedicated autosave slot and save on safe boundaries.
- **Storing secrets or trusting client saves in multiplayer.** A local save is
  player-controlled; never treat it as authoritative for online state. For cloud,
  handle the device's data limits and conflicts (`roblox-datastores`).

## References

- `references/versioning-and-migration.md` — schema evolution strategies, the
  migration chain, backups/rollback, format trade-offs (JSON vs binary), and a
  load-time validation checklist.

## Related skills

- `roblox-datastores` — cloud persistence, request limits, session locking.
- `godot-resources`, `unity-scriptableobjects` — the data model you serialize.
- `procedural-gen` — store the seed to regenerate worlds instead of saving them.
- `rpg`, `survival-crafting`, `visual-novel` — genres that compose this skill.
