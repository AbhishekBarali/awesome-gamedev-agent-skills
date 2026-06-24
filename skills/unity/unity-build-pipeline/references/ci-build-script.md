# CI / headless build script (Unity 6)

Depth for `unity-build-pipeline`: a reusable editor build script that takes command-line
arguments, switches platform, stamps a version, and returns a proper exit code. Verified
against `ScriptReference/BuildPipeline.BuildPlayer` and the editor command-line arguments.

## A parameterised build method

```csharp
using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class CIBuild
{
    // Invoke with: -executeMethod CIBuild.Run -buildTarget Win64 -out Builds/Game.exe -version 1.2.3
    public static void Run()
    {
        string[] args = Environment.GetCommandLineArgs();

        string targetArg = ArgValue(args, "-buildTarget", "Win64");
        string outPath   = ArgValue(args, "-out", "Builds/Game.exe");
        string version   = ArgValue(args, "-version", PlayerSettings.bundleVersion);
        bool   dev       = args.Contains("-dev");

        BuildTarget target = targetArg switch
        {
            "Win64" => BuildTarget.StandaloneWindows64,
            "Mac"   => BuildTarget.StandaloneOSX,
            "Linux" => BuildTarget.StandaloneLinux64,
            "Android" => BuildTarget.Android,
            _ => throw new ArgumentException($"Unknown -buildTarget {targetArg}")
        };

        // Switch the active target so the right platform defines/assets are used.
        EditorUserBuildSettings.SwitchActiveBuildTarget(
            BuildPipeline.GetBuildTargetGroup(target), target);

        PlayerSettings.bundleVersion = version;   // stamp the version into the player

        var options = new BuildPlayerOptions
        {
            scenes = EnabledScenes(),
            locationPathName = outPath,
            target = target,
            options = dev ? BuildOptions.Development : BuildOptions.None,
        };

        BuildReport report = BuildPipeline.BuildPlayer(options);
        BuildSummary s = report.summary;

        if (s.result == BuildResult.Succeeded)
        {
            Debug.Log($"[CIBuild] OK {version} -> {outPath} ({s.totalSize} bytes)");
            EditorApplication.Exit(0);            // explicit success exit code for CI
        }
        else
        {
            Debug.LogError($"[CIBuild] FAILED: {s.totalErrors} errors, result={s.result}");
            EditorApplication.Exit(1);            // non-zero fails the pipeline
        }
    }

    private static string[] EnabledScenes() =>
        EditorBuildSettings.scenes.Where(sc => sc.enabled).Select(sc => sc.path).ToArray();

    private static string ArgValue(string[] args, string key, string fallback)
    {
        int i = Array.IndexOf(args, key);
        return (i >= 0 && i + 1 < args.Length) ? args[i + 1] : fallback;
    }
}
```

## Invoking from CI

```bash
# Use -quit so the editor exits; the method itself also calls EditorApplication.Exit for clarity.
Unity -batchmode -nographics \
  -projectPath "$CI_PROJECT_DIR" \
  -executeMethod CIBuild.Run \
  -buildTarget Win64 -out "Builds/Win/Game.exe" -version "1.2.$BUILD_NUMBER" \
  -logFile - || exit 1
```

- Pipe `-logFile -` to stdout so the CI captures the Unity log.
- `EditorApplication.Exit(code)` inside the method is the reliable way to set the exit code;
  `-quit` alone returns 0 even after a logged error.
- Activate the Unity license in batch mode (`-username`/`-password`/`-serial` or a license
  file) as a separate step before building on a clean runner.

## Addressables content build (when used)

```csharp
using UnityEditor.AddressableAssets.Settings;

// Build the Addressables content bundles BEFORE the player build, or runtime loads fail.
public static void BuildContent()
{
    AddressableAssetSettings.BuildPlayerContent(out var result);
    if (!string.IsNullOrEmpty(result.Error))
        throw new Exception($"Addressables build failed: {result.Error}");
}
```

## Gotchas

- `SwitchActiveBuildTarget` can take time and triggers a reimport; do it once per target, not
  per build.
- Reading args via `Environment.GetCommandLineArgs()` includes Unity's own flags — match on
  your custom keys only.
- A build server needs the platform module installed (e.g. IL2CPP toolchain, Android SDK/NDK)
  or the build fails late with a toolchain error.
