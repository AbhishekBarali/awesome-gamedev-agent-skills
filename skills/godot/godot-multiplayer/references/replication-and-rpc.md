# Replication & RPC reference (Godot 4.3+)

Depth companion to `godot-multiplayer`.

## The @rpc annotation in full

```gdscript
@rpc(mode, sync, transfer_mode, transfer_channel)
```

Defaults — `@rpc` is equivalent to `@rpc("authority", "call_remote", "reliable", 0)`:

- **mode**: `"authority"` (only the node's multiplayer authority may call remotely) or
  `"any_peer"` (any client may call — needed for player input).
- **sync**: `"call_remote"` (does not run on the local/sending peer) or `"call_local"`
  (also runs locally — use when the host is a player).
- **transfer_mode**: `"reliable"` (acknowledged, ordered, slower), `"unreliable"`
  (fire-and-forget, may drop/reorder — good for frequent position updates), or
  `"unreliable_ordered"` (drops late packets to preserve order).
- **transfer_channel**: integer channel index; the first three args can be in any order
  but the channel must be last. Use separate channels to keep unrelated streams from
  blocking each other.

Call forms (on a `Callable` for the method):

```gdscript
my_method.rpc(args...)            # call on all peers (per mode/sync rules)
my_method.rpc_id(peer_id, args)   # call on one peer (1 = server)
multiplayer.get_remote_sender_id()  # inside the method: who invoked it
```

## MultiplayerSpawner

Auto-instantiates scenes on remote peers when the authority spawns them.

1. Add a `MultiplayerSpawner` node; set its **Spawn Path** to the parent that will hold
   spawned instances.
2. Add the scenes it may spawn to its **Auto Spawn List** (or use a custom spawn function
   via `spawn_function`).
3. On the authority, call `spawner.spawn(data)` or simply `add_child()` a scene under the
   spawn path — the spawner replicates it to clients with a matching name.

```gdscript
@onready var spawner: MultiplayerSpawner = $MultiplayerSpawner

func server_spawn_player(id: int) -> void:
    var p := preload("res://player.tscn").instantiate()
    p.name = str(id)                 # deterministic name = authority id
    $Players.add_child(p, true)      # true = readable, replicated name
```

## MultiplayerSynchronizer

Replicates chosen properties from the authority to other peers each network tick.

- Add it as a child of the node to sync. In the **Replication** dock, add property paths
  (e.g. `:position`, `:velocity`, `Sprite2D:modulate`).
- Per property: **Spawn** (sent once at spawn) and **Sync** (sent continuously) flags, plus
  a replication interval.
- `replication_interval` / `delta_interval` tune bandwidth.
- Visibility filtering for per-peer data:
  ```gdscript
  sync.set_visibility_for(peer_id, true)
  sync.add_visibility_filter(func(peer): return _can_see(peer))
  sync.update_visibility()
  ```

Only the authority's values are sent; remote peers receive read-only updates. Combine with
per-node authority so each player's synchronizer pushes that player's state.

## SceneMultiplayer authentication

Protect RPCs from unauthenticated peers using the built-in handshake:

```gdscript
# Server, after assigning the peer:
multiplayer.auth_timeout = 3.0
multiplayer.auth_callback = func(peer_id: int, data: PackedByteArray):
    var info := JSON.parse_string(data.get_string_from_utf8())
    if _valid(info):
        multiplayer.complete_auth(peer_id)

# Client:
multiplayer.peer_authenticating.connect(func(peer_id: int):
    var payload := JSON.stringify({"token": _token}).to_utf8_buffer()
    multiplayer.send_auth(1, payload)
)
```

`connected_to_server` / `peer_connected` only fire once both sides call `complete_auth()`.

## Transfer mode guidance

- **Player input / commands** → reliable (must not be lost).
- **Position/rotation updates** → unreliable or unreliable_ordered via a
  `MultiplayerSynchronizer` (frequent, latest-wins).
- **Chat / state changes** → reliable, possibly on a dedicated channel.

## Dedicated server export

Export a **headless** build (no GPU) for servers; see `godot-export`. Modify the lobby so
the server is not counted as a player and the first joining client can start the match. Run
with the server feature tag and `--headless`.

## Minimal lobby flow

1. Host: `create_server`; add self to `players` keyed by id 1.
2. On `peer_connected(id)`: send your player info to that id via `rpc_id`.
3. Each peer registers others (`@rpc("any_peer")` register function using
   `get_remote_sender_id()`).
4. On `peer_disconnected(id)`: erase from `players`, emit a UI signal.
5. Server starts the game by RPC'ing a `load_game(path)` (`@rpc("call_local","reliable")`)
   so all peers `change_scene_to_file` together.
