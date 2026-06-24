---
name: shader-programming
description: >
  Write game shaders from cross-engine fundamentals — the vertex→fragment
  pipeline, coordinate spaces, UV math, and common 2D/3D effects (tint, UV
  scroll, dissolve, outline, fresnel rim, vignette) in GLSL with HLSL
  equivalents. Use when the user mentions shaders, fragment/pixel shader, vertex
  shader, UV, GLSL, HLSL, or effects like dissolve, outline, or rim light.
license: Apache-2.0
compatibility: Concepts engine-agnostic; examples in GLSL-style (Godot gdshader / OpenGL) with HLSL (Unity/Unreal) equivalents noted. Pairs with godot-shaders.
metadata:
  engine: none
  category: disciplines
  difficulty: advanced
---

# Shader programming (cross-engine)

Shaders are small programs that run **per vertex** and **per pixel** on the GPU.
The concepts — the pipeline, coordinate spaces, UVs, and how common effects are
built — port across engines; only the language dialect and built-in variable
names change. This skill teaches those portable fundamentals in GLSL with HLSL
equivalents; use `godot-shaders` (or Unity/Unreal material docs) for the exact
engine syntax and built-ins.

## When to use

- Use to understand or write vertex/fragment shaders and to reason about UVs,
  coordinate spaces, and the GPU pipeline.
- Use to build common effects: tint/recolor, scrolling textures, dissolve,
  outlines, fresnel/rim light, vignette, color grading.
- Use to translate a shader concept between GLSL and HLSL, or between engines.

**When *not* to use:** for an engine's exact shader language and built-ins, use
`godot-shaders` (Godot shading language) or the engine's material docs. For full
particle VFX systems, see `unreal-niagara`. For post-process *stacks*, defer to
the engine's renderer settings.

## Core workflow

1. **Know which stage you're in.** The **vertex** shader transforms each vertex
   into clip space and passes data (UVs, normals) onward; the **fragment/pixel**
   shader runs per rasterized pixel and outputs a color. Most game effects live
   in the fragment stage.
2. **Track coordinate spaces.** Positions move model → world → view → clip space;
   normals belong in world or view space. Mixing spaces is the most common bug.
3. **Drive effects with UVs and time.** UVs are `0..1` texture coordinates;
   offset, scale, or distort them, and animate with a `time` uniform.
4. **Work per pixel, branch-light.** Prefer `mix`, `step`, `smoothstep`, and
   `clamp` over `if` where possible; GPUs run pixels in lockstep and dislike
   divergent branches.
5. **Pass data via uniforms** (constant per draw) and **varyings** (interpolated
   vertex→fragment). Keep texture samples few; they dominate cost.
6. **Verify visually and on target hardware.** Shaders that look right on desktop
   can break on mobile (precision, missing features). Test where it ships.

## Patterns

GLSL-style fragment snippets (close to Godot's `canvas_item`/`spatial`
shaders and OpenGL). See `references/effects.md` for the HLSL equivalents and
the full outline/fresnel/vignette shaders.

### 1. Fragment basics: sample, tint, and combine

```glsl
// Per-pixel: read the texture at this UV, multiply by a color (tint), keep alpha.
uniform sampler2D tex;
uniform vec4 tint;          // e.g. (1,0,0,1) reddens; multiply is non-destructive
in vec2 uv;                 // interpolated 0..1 texture coordinate (a "varying")
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);   // HLSL: tex.Sample(samp, uv)
    frag = c * tint;             // component-wise multiply tints without clipping
}
```

### 2. Scrolling UVs (animated texture) — frame-rate independent

```glsl
// Add time * speed to the UV to scroll. fract() wraps it into 0..1 so it tiles.
uniform sampler2D tex;
uniform float time;          // seconds, supplied by the engine
uniform vec2 scroll_speed;   // UV units per second, e.g. (0.1, 0.0)
in vec2 uv;
out vec4 frag;
void main() {
    vec2 scrolled = fract(uv + scroll_speed * time);  // HLSL: frac(...)
    frag = texture(tex, scrolled);
}
// Drive with a real time uniform, not a per-frame accumulator, so speed is stable.
```

### 3. Dissolve (threshold a noise map, glow the edge)

```glsl
// Hide pixels where noise < threshold; tint a thin band at the boundary.
uniform sampler2D tex;
uniform sampler2D noise_tex;     // grayscale noise, 0..1
uniform float amount;            // 0 = fully visible, 1 = fully dissolved
uniform float edge = 0.05;       // width of the glowing edge band
uniform vec4 edge_color;
in vec2 uv;
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);
    float n = texture(noise_tex, uv).r;
    if (n < amount) discard;                 // cut away dissolved pixels
    float e = smoothstep(amount, amount + edge, n);  // 0 at the edge -> 1 inside
    frag = mix(edge_color, c, e);            // HLSL: lerp(edge_color, c, e)
}
```

### 4. Fresnel rim light (3D) — brighten glancing angles

```glsl
// Rim = 1 where the surface faces away from the camera (silhouette glow).
in vec3 world_normal;        // normalized, world space (from the vertex stage)
in vec3 view_dir;            // normalized, surface -> camera, world space
uniform float power = 3.0;
uniform vec3 rim_color;
out vec4 frag;
void main() {
    float f = pow(1.0 - clamp(dot(world_normal, view_dir), 0.0, 1.0), power);
    frag = vec4(rim_color * f, 1.0);   // add to lighting; f peaks at the silhouette
}
// Correctness: normal and view_dir MUST be in the same space and normalized.
```

## Pitfalls

- **Mixing coordinate spaces** (lighting a world-space normal against a
  view-space light) yields subtly wrong shading. Pick one space and convert
  everything into it.
- **Forgetting to normalize** interpolated normals/directions: interpolation
  shortens vectors, so `dot()` results drift. `normalize()` in the fragment stage.
- **UV assumptions across engines.** Some engines flip V (top-left vs bottom-left
  origin); a texture may appear upside-down. Know your engine's convention.
- **Heavy branching / dynamic loops** stall GPUs. Prefer `step`/`smoothstep`/
  `mix`; reserve `if`/`discard` for genuinely cheap early-outs.
- **`discard` defeats early-Z** and can hurt performance on tiled mobile GPUs;
  prefer alpha blending where you can.
- **Precision on mobile**: `highp` vs `mediump` matters; large UVs or time values
  in low precision shimmer. Use adequate precision for coordinates and time.
- **Assuming GLSL == HLSL.** `mix`↔`lerp`, `fract`↔`frac`, `texture()`↔`.Sample()`,
  `vec2`↔`float2`, column- vs row-major matrices. See the reference mapping.

## References

- `references/effects.md` — full outline (2D sprite + 3D), vignette, and color
  grading shaders; the GLSL↔HLSL function/type mapping table; per-engine notes
  (Godot `canvas_item`/`spatial`, Unity ShaderLab/HLSL, Unreal material nodes).

## Related skills

- `godot-shaders` — Godot shading language syntax, built-ins, and screen-reading.
- `unreal-niagara` — GPU particle VFX (a different shader use).
- `procedural-gen` — the noise that drives dissolve and procedural texturing.
