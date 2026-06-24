# Shader effects and GLSL↔HLSL mapping

Full versions of the effects sketched in `SKILL.md`, plus the dialect mapping you
need to port a shader between engines. Examples are GLSL-style; the mapping table
shows the HLSL form.

## GLSL ↔ HLSL quick reference

| GLSL | HLSL | Note |
|---|---|---|
| `vec2/3/4`, `mat3/4` | `float2/3/4`, `float3x3/4x4` | vectors and matrices |
| `mix(a, b, t)` | `lerp(a, b, t)` | linear interpolation |
| `fract(x)` | `frac(x)` | fractional part |
| `mod(a, b)` | `fmod(a, b)` | sign differs for negatives — verify |
| `texture(samp, uv)` | `tex.Sample(samp, uv)` | sampler is a separate object in HLSL |
| `inversesqrt(x)` | `rsqrt(x)` | |
| `mat * vec` (column-major) | `mul(vec, mat)` (row-major) | matrix order/convention differs |
| `gl_Position` / `out` color | `SV_Position` / `SV_Target` | stage outputs via semantics |
| `dFdx/dFdy` | `ddx/ddy` | screen-space derivatives |

Also watch: clip-space depth range (OpenGL `-1..1` vs D3D `0..1`) and UV/clip Y
orientation differ between APIs — engines usually normalize this for you, but it
surfaces when porting raw shaders.

## 2D sprite outline (sample the alpha neighborhood)

```glsl
// Draw an outline where a transparent pixel is adjacent to an opaque one.
uniform sampler2D tex;
uniform vec2 texel_size;     // (1/width, 1/height) of the texture
uniform vec4 outline_color;
in vec2 uv;
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);
    if (c.a > 0.5) { frag = c; return; }          // inside the sprite: unchanged
    // sample 4 neighbors; if any is opaque, this empty pixel is on the border
    float a = max(max(texture(tex, uv + vec2( texel_size.x, 0)).a,
                      texture(tex, uv + vec2(-texel_size.x, 0)).a),
                  max(texture(tex, uv + vec2(0,  texel_size.y)).a,
                      texture(tex, uv + vec2(0, -texel_size.y)).a));
    frag = (a > 0.5) ? outline_color : vec4(0.0);  // border pixel -> outline
}
```

For thicker or smoother outlines, sample 8 neighbors (include diagonals) or do a
small distance-field pass. In 3D, outlines are usually done differently: render
back-faces scaled outward along normals, or detect edges from depth/normal
discontinuities in a post-process.

## Vignette (darken the screen edges) — post-process

```glsl
// Darken pixels by distance from screen center. screen_uv is 0..1 across the view.
uniform sampler2D screen_tex;
uniform float strength = 0.6;   // 0 = none, 1 = strong
uniform float radius = 0.75;    // where darkening begins
in vec2 screen_uv;
out vec4 frag;
void main() {
    vec3 c = texture(screen_tex, screen_uv).rgb;
    float d = distance(screen_uv, vec2(0.5));      // 0 center .. ~0.707 corner
    float v = smoothstep(radius, radius * 0.5, d); // 1 in center, ->0 at edges
    frag = vec4(c * mix(1.0 - strength, 1.0, v), 1.0);
}
```

## Color grading via a curve (brightness/contrast/saturation)

```glsl
// Order matters: contrast around 0.5, then saturation, then brightness.
uniform sampler2D screen_tex;
uniform float brightness = 0.0;   // additive
uniform float contrast   = 1.0;   // multiplicative around mid-gray
uniform float saturation = 1.0;
in vec2 screen_uv;
out vec4 frag;
void main() {
    vec3 c = texture(screen_tex, screen_uv).rgb;
    c = (c - 0.5) * contrast + 0.5;                       // contrast
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));    // Rec.709 luminance
    c = mix(vec3(luma), c, saturation);                   // saturation
    c += brightness;                                      // brightness
    frag = vec4(clamp(c, 0.0, 1.0), 1.0);
}
```

The luminance weights `(0.2126, 0.7152, 0.0722)` are the Rec.709 coefficients —
green dominates perceived brightness. For LUT-based grading, sample a color
lookup texture indexed by the pixel's RGB instead.

## Per-engine notes

- **Godot (4.x) — `gdshader`.** Godot's shading language is GLSL-like with a
  `shader_type` (`canvas_item` for 2D, `spatial` for 3D). It provides built-ins:
  `UV`, `COLOR`, `TIME`, `TEXTURE`, `SCREEN_TEXTURE`, `NORMAL`, `VIEW`. Write
  `fragment()` / `vertex()` functions. Map the GLSL examples here onto those
  built-ins. See `godot-shaders`.
- **Unity — ShaderLab + HLSL.** Shaders live in `.shader` files (ShaderLab
  blocks) or Shader Graph. Code is HLSL: `float4`, `lerp`, `tex2D`/`.Sample`,
  `SV_Target`. URP/HDRP supply include files for lighting and transforms.
- **Unreal — Material Editor (node graph) + HLSL.** Most authoring is visual
  nodes; Custom nodes embed HLSL. Concepts (UVs, fresnel via a Fresnel node,
  panner for UV scroll) map directly to the patterns here.

## Performance checklist

- Minimize texture samples; they are the dominant cost. Reuse a sample instead of
  re-reading.
- Prefer math (`smoothstep`, `mix`) to branches and `discard`.
- Compute heavy values per vertex (then interpolate) when per-pixel precision
  isn't required.
- Use appropriate precision on mobile (`mediump` for color, higher for UV/time).
- Avoid dependent texture reads (sampling using a value read from another texture)
  on low-end GPUs where possible.
