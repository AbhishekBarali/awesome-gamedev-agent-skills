# Export presets & CLI reference (Godot 4.3+)

Depth companion to `godot-export`.

## export_presets.cfg

Generated/edited by *Project > Export*; commit it so CI and teammates share presets. It is
an INI-style file with a `[preset.N]` block per preset and a matching `[preset.N.options]`
block. Example shape (do not hand-author from scratch — let the editor create it):

```ini
[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
export_path="build/windows/game.exe"
custom_features=""
exclude_filter=""
include_filter=""

[preset.0.options]
binary_format/embed_pck=false
application/icon="res://icon.ico"
application/product_name="My Game"
codesign/enable=false
```

Sensitive values (keystore passwords, encryption keys) live in `export_presets.cfg` too —
keep them out of public repos or inject them in CI rather than committing.

## Useful command-line flags

```
godot --headless                      run without a window/GPU
      --path <dir>                    project directory (where project.godot is)
      --export-release "<preset>" <out>   export a release build
      --export-debug "<preset>" <out>     export a debug build
      --export-pack "<preset>" <out>      export only the .pck/.zip data
      --quit-after <frames|seconds>   auto-quit (smoke tests)
      --main-pack <file.pck>          run a specific data pack
      --verbose                       detailed logging
      -- <args>                       pass args to your game (OS.get_cmdline_user_args())
```

Use the exact preset `name` (case/space-sensitive). Run from the project dir or pass
`--path`. Exit code is non-zero on export failure — check it in CI.

## Custom feature tags

Add tags under a preset's *Features* (or `custom_features`) and branch at runtime with
`OS.has_feature("tag")`. Common built-ins: `web`, `windows`, `macos`, `linux`, `android`,
`ios`, `mobile`, `pc`, `debug`, `release`, `editor`, `template`, `dedicated_server`,
`64`/`32`. Use a `demo` tag to ship a content-limited build from the same project.

## Web (HTML5) specifics

- Output is `index.html` + `.js`/`.wasm`/`.pck`. Serve over HTTP(S).
- Threaded builds need **cross-origin isolation**:
  - `Cross-Origin-Opener-Policy: same-origin`
  - `Cross-Origin-Embedder-Policy: require-corp`
  Without these, `SharedArrayBuffer` is unavailable and the engine errors or falls back.
- itch.io: enable "This file will be played in the browser" and the SharedArrayBuffer
  support option. GitHub Pages can't set the headers — use a host that can, or a service
  worker shim.
- Reduce size: enable compression, trim unused features, and consider the
  "Extensions Support" toggle only if needed.

## Android

- Set Android SDK + OpenJDK paths in Editor Settings > Export > Android.
- Install the Android build template (Project > Install Android Build Template) for custom
  Gradle builds / plugins.
- Provide a **debug keystore** (auto for debug) and a **release keystore** for store
  builds. Add the `INTERNET` permission for networked games.
- Choose architectures (arm64-v8a is standard for modern devices).

## macOS / iOS

- macOS distribution: enable codesign, provide an Apple Developer ID, and notarize the
  `.app`/`.dmg`; otherwise Gatekeeper blocks it.
- iOS: exports an Xcode project; build/sign/submit through Xcode.

## PCK patching & DLC

Export extra content as a separate `.pck` and load it at runtime:

```gdscript
var ok := ProjectSettings.load_resource_pack("user://dlc1.pck")  # mounts into res://
```

A patch pack can override or add files. Use `--export-pack` to produce packs in CI.

## Encryption

Set a 64-hex-char script encryption key (Project > Export, or `GODOT_SCRIPT_ENCRYPTION_KEY`
env for CLI) and enable "Encrypt Exported PCK". Note: client-side encryption deters casual
inspection but cannot fully protect assets on a user's machine — don't store true secrets
in the build.
