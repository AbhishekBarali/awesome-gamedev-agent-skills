---
name: unity-build-pipeline
description: >
  Build and ship Unity 6 players: build settings and scenes, player/quality settings, the
  IL2CPP vs Mono scripting backend, managed code stripping, scripted BuildPipeline.BuildPlayer,
  and CI/headless builds. Use when configuring or automating a build, choosing a scripting
  backend, shrinking build size, or when the user mentions Unity build, player settings,
  IL2CPP, code stripping, or Addressables.
license: Apache-2.0
compatibility: Unity 6 (6000.0 LTS); UnityEditor.BuildPipeline. Addressables is a separate package.
metadata:
  engine: unity
  category: unity
  difficulty: intermediate
---

# Unity Build Pipeline

Configure, script, and automate Unity 6 player builds: scenes, platform target, scripting
backend, stripping, and headless/CI builds. Targets **Unity 6 (6000.0 LTS)**.

## When to use

- Use when setting up Build Settings/Profiles, choosing a platform and scripting backend
  (Mono vs IL2CPP), reducing build size with managed stripping, scripting a repeatable build
  with `BuildPipeline.BuildPlayer`, or wiring a CI/headless build.
- Use when the project has `ProjectSettings/EditorBuildSettings.asset` or a CI build script.

**When *not* to use:** authoring a CI service config end-to-end is DevOps; this skill covers
the Unity-side build API and settings. Console/platform certification specifics are
platform-NDA territory. Storefront submission → `steam-publish` / `itch-publish`.

## Core workflow

1. **List the scenes to build** (File → Build Profiles/Settings → Scene List, or
   `EditorBuildSettings.scenes`). Only listed, enabled scenes ship; scene 0 is the start scene.
2. **Pick the platform target** and switch the active build target if needed
   (`BuildTarget` / `EditorUserBuildSettings`).
3. **Choose the scripting backend** (Player Settings): **Mono** (fast iteration, desktop) vs
   **IL2CPP** (AOT C++; required for many platforms, better perf, harder to reverse). IL2CPP
   needs the platform's C++ toolchain installed.
4. **Tune size/perf:** set Managed Stripping Level (Disabled → Minimal → Low → Medium → High)
   and protect reflection-only code with a `link.xml`. Set Quality Settings per platform.
5. **Script the build** with `BuildPipeline.BuildPlayer(BuildPlayerOptions)` and **inspect the
   returned `BuildReport`** — a non-`Succeeded` result must fail your pipeline.
6. **Run headless** for CI with `-batchmode -quit -executeMethod`, and check the exit code.
7. **Verify** the actual output runs (launch the player), not just that the build returned
   without throwing.

## Patterns

### 1. Scripted build with a result check

```csharp
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class BuildScript
{
    [MenuItem("Build/Windows x64")]
    public static void BuildWindows()
    {
        var options = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/Main.unity", "Assets/Scenes/Level1.unity" },
            locationPathName = "Builds/Windows/Game.exe",
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None,            // add BuildOptions.Development for a dev build
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary summary = report.summary;

        if (summary.result != BuildResult.Succeeded)
            throw new System.Exception($"Build failed: {summary.totalErrors} errors");
        Debug.Log($"Build OK: {summary.totalSize} bytes in {summary.totalTime}");
    }
}
```

### 2. Headless / CI invocation

```bash
# Exit code is 0 on success; -quit ensures the editor closes; -nographics for build servers.
Unity -batchmode -quit -nographics \
  -projectPath "/path/to/Project" \
  -executeMethod BuildScript.BuildWindows \
  -logFile -
```

### 3. Protect stripped code with `link.xml`

```xml
<!-- Assets/link.xml — keep types the linker can't see are used (reflection, JSON, plugins). -->
<linker>
  <assembly fullname="MyGameRuntime" preserve="all"/>
</linker>
```

## Pitfalls

- **A scene loads in the Editor but is missing in the build** — it isn't in the Build Settings
  scene list (or is disabled). `SceneManager.LoadScene` only sees listed scenes.
- **IL2CPP build fails on a fresh machine** — the platform C++ toolchain (e.g. Windows build
  tools, Android NDK) isn't installed. Mono has no such requirement.
- **`MissingMethodException`/`TypeLoadException` only in the build** — managed stripping removed
  reflection-only code. Lower the stripping level or add a `link.xml` preserve entry.
- **Treating "BuildPlayer returned" as success** — always check `BuildReport.summary.result`;
  it can return with errors.
- **Addressables content is stale/missing** — Addressables (`com.unity.addressables`) need a
  *separate* content build (Build → Addressables) and a profile pointing at the right load
  path; a player build alone doesn't rebuild them.
- **Shipping a Development build** — `BuildOptions.Development` enables the profiler/debugging
  and is slower; use `BuildOptions.None` for release.

## References

- For a complete **multi-platform CI build script** (target switching, version stamping,
  argument parsing, exit codes) and an Addressables content-build call, read
  `references/ci-build-script.md`.
- Primary docs: `ScriptReference/BuildPipeline.BuildPlayer`, Unity Manual build sections
  (player settings, managed code stripping).

## Related skills

- `steam-publish` / `itch-publish` — distributing the player you just built.
- `unity-csharp-scripting` — editor scripting conventions used by build scripts.
