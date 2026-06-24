# 3D scene & environment reference (Godot 4.3+)

Depth companion to `godot-3d-essentials`.

## Transform3D

A `Node3D` has a `Transform3D` = `Basis` (3x3 rotation/scale) + `origin` (Vector3).

```gdscript
global_position = Vector3(1, 0, 2)
rotate_y(deg_to_rad(90))                 # rotate about local Y
rotation_degrees = Vector3(0, 45, 0)
look_at(target_global_pos, Vector3.UP)   # global-space orientation
transform = transform.translated_local(Vector3.FORWARD * 2.0)  # move along local -Z
basis = basis.orthonormalized()          # fix drift after many rotations
```

Godot 3D convention: **-Z is forward**, +Y is up, +X is right.

## Camera3D

- `projection`: `PROJECTION_PERSPECTIVE` (fov) or `PROJECTION_ORTHOGONAL` (size).
- `fov`, `near`, `far`, `current`, `make_current()`, `clear_current()`.
- `project_ray_origin(screen_pos)` / `project_ray_normal(screen_pos)` for click-to-world
  picking (combine with a physics raycast).
- `unproject_position(world_pos)` → screen position (e.g. floating health bars).
- For follow/orbit, parent the camera to a pivot `Node3D` and rotate the pivot.

## Lights

| Node | Role | Key props |
|------|------|-----------|
| `DirectionalLight3D` | Sun (parallel rays) | `shadow_enabled`, `light_energy`, `directional_shadow_mode` |
| `OmniLight3D` | Point light | `omni_range`, `light_energy`, `shadow_enabled` |
| `SpotLight3D` | Cone | `spot_range`, `spot_angle`, `shadow_enabled` |

Common: `light_color`, `light_energy`, `light_indirect_energy`, shadow bias settings.
Too many shadow-casting lights hurts performance — bake static lighting where possible.

## Environment & post-processing

`WorldEnvironment.environment` (an `Environment` resource):

- **Background:** `BG_CLEAR_COLOR`, `BG_COLOR`, `BG_SKY` (with a `Sky` +
  `ProceduralSkyMaterial`/`PanoramaSkyMaterial`).
- **Ambient:** `ambient_light_source` (sky/color/disabled), `ambient_light_color`,
  `ambient_light_energy`.
- **Tonemap:** `tonemap_mode` (LINEAR, REINHARD, FILMIC, ACES), `tonemap_exposure`,
  `tonemap_white`.
- **Post:** `glow_enabled` (+ bloom/levels), `ssao_enabled`, `ssil_enabled`,
  `sdfgi_enabled` (real-time GI), `fog_enabled`/`volumetric_fog_enabled`,
  `adjustment_enabled` (brightness/contrast/saturation + color correction).

A `CameraAttributes` resource (Practical/Physical) adds DOF, auto-exposure, and exposure
controls, assigned on the camera or environment.

## Materials

`StandardMaterial3D` (PBR) key fields: `albedo_color`/`albedo_texture`, `metallic`,
`roughness`, `normal_enabled`+`normal_texture`, `emission_enabled`+`emission`,
`transparency` (`TRANSPARENCY_ALPHA`/`ALPHA_SCISSOR`), `cull_mode`, `shading_mode`
(`SHADING_MODE_PER_PIXEL` / `UNSHADED`). Apply via `MeshInstance3D.material_override` (all
surfaces) or `set_surface_override_material(i, mat)` (per surface). `ORMMaterial3D` packs
occlusion/roughness/metallic into one texture.

## GridMap & MeshLibrary

1. Build a scene where each child is a mesh + optional collision; export it as a
   `MeshLibrary` (Scene > Export As > MeshLibrary), or convert a scene in the editor.
2. Assign the `MeshLibrary` to the `GridMap.mesh_library` and set `cell_size`.
3. Paint in the editor, or from code:
   ```gdscript
   grid.set_cell_item(Vector3i(x, y, z), item_id, orientation)
   grid.get_cell_item(Vector3i(x, y, z))          # -1 if empty (GridMap.INVALID_CELL_ITEM)
   grid.get_used_cells()
   grid.clear()
   grid.map_to_local(cell) / grid.local_to_map(pos)
   ```
   Orientation comes from `GridMap.get_orthogonal_index_from_basis(basis)`.

## Baked lighting & probes

- `LightmapGI` — bake static GI into lightmaps for static geometry (mark meshes "bake").
- `ReflectionProbe` — local cubemap reflections for an area.
- `VoxelGI` / `SDFGI` — dynamic GI (heavier). Use baked lightmaps for ship-quality static
  scenes and reserve real-time GI for dynamic needs.
