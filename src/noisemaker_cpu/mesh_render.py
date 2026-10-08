"""CPU triangle-mesh rasterizer for ``drawMode: 'triangles'`` passes
(``render/meshRender``).

Port of noisemaker-cpu ``src/effects/cpu/mesh-render.js`` (the reactive/mesh
import). The canonical pass executor cannot run these through the per-pixel
fragment-kernel machinery (they rasterize a variable number of triangles rather
than filling every destination pixel exactly once), so — like the scatter draw
ops in ``draw_ops.py`` — this is a hand-ported function dispatched by
``renderer.py``, keyed by ``${effectId}:${pass.program}``. The port follows the
upstream draw exactly (shaders/src/runtime/backends/webgl2.js triangle-mesh
mode):

- drawArrays(TRIANGLES) over one texel per vertex of the mesh positions texture,
  consecutive texel triples forming a de-indexed triangle soup (``parse_obj``
  packs exactly that order, so no index buffer exists on either side);
- depth test LESS against a per-pass depth buffer cleared to 1.0, back-face
  culling with CCW = front, blending disabled;
- the vertex stage is ``render.vert`` (mesh texture fetch, scale/offset,
  Rz*Ry*Rx rotation in degrees, orthographic projection with viewScale and
  aspect divide, z mapped to [0, 1] over nearZ -10 / farZ 10) and the fragment
  stage is ``render.frag`` (Blinn-Phong diffuse/specular, ambient, Fresnel rim,
  optional wireframe discard via screen-space normal derivatives, gamma 1/2.2).

Floating point follows the JS source's GLSL-f32 emulation: every elementary op
computes in float64 and rounds with ``Math.fround`` (here ``_f32``). Where the
JS code leaves a value unrounded (the barycentric edge-function division into
``b0``/``b1``), the port leaves it in float64 too.
"""

from __future__ import annotations

import math

import numpy as np

_F32 = np.float32


def _f32(x) -> float:
    return float(_F32(x))


def _vec3(x, y, z):
    return [_f32(x), _f32(y), _f32(z)]


def _vec3_normalize(v):
    len_sq = _f32(_f32(_f32(v[0] * v[0]) + _f32(v[1] * v[1])) + _f32(v[2] * v[2]))
    if len_sq == 0:
        return _vec3(0, 0, 0)
    inv_len = _f32(1 / math.sqrt(len_sq))
    return _vec3(_f32(v[0] * inv_len), _f32(v[1] * inv_len), _f32(v[2] * inv_len))


def _vertex_stage(pos_data, normal_data, uniforms):
    position = _vec3(pos_data[0], pos_data[1], pos_data[2])
    normal = _vec3(normal_data[0], normal_data[1], normal_data[2])
    mesh_scale = uniforms["meshScale"]
    position = _vec3(_f32(position[0] * mesh_scale), _f32(position[1] * mesh_scale), _f32(position[2] * mesh_scale))
    position = _vec3(
        _f32(position[0] + uniforms["meshOffsetX"]),
        _f32(position[1] + uniforms["meshOffsetY"]),
        _f32(position[2] + uniforms["meshOffsetZ"]),
    )
    deg2rad = _f32(3.14159265 / 180.0)
    rx = _f32(uniforms["rotateX"] * deg2rad)
    ry = _f32(uniforms["rotateY"] * deg2rad)
    rz = _f32(uniforms["rotateZ"] * deg2rad)
    cx, sx = _f32(math.cos(rx)), _f32(math.sin(rx))
    cy, sy = _f32(math.cos(ry)), _f32(math.sin(ry))
    cz, sz = _f32(math.cos(rz)), _f32(math.sin(rz))
    # mat3 rotationZ * rotationY * rotationX (GLSL column-major constructor values inlined).
    rot_x = [1, 0, 0, 0, cx, sx, 0, -sx, cx]
    rot_y = [cy, 0, sy, 0, 1, 0, -sy, 0, cy]
    rot_z = [cz, -sz, 0, sz, cz, 0, 0, 0, 1]

    def mul(a, b):
        # a * b with column-major mat3 layout: out[col*3+row] = sum a[k*3+row]*b[col*3+k]
        out = [0.0] * 9
        for col in range(3):
            for row in range(3):
                out[col * 3 + row] = _f32(
                    _f32(a[row] * b[col * 3]) + _f32(a[3 + row] * b[col * 3 + 1]) + _f32(a[6 + row] * b[col * 3 + 2])
                )
        return out

    def apply(m, v):
        return _vec3(
            _f32(_f32(m[0] * v[0]) + _f32(m[3] * v[1]) + _f32(m[6] * v[2])),
            _f32(_f32(m[1] * v[0]) + _f32(m[4] * v[1]) + _f32(m[7] * v[2])),
            _f32(_f32(m[2] * v[0]) + _f32(m[5] * v[1]) + _f32(m[8] * v[2])),
        )

    rotation = mul(mul(rot_z, rot_y), rot_x)
    rotated_pos = apply(rotation, position)
    rotated_normal = apply(rotation, normal)
    rotated_pos[0] = _f32(rotated_pos[0] + uniforms["posX"])
    rotated_pos[1] = _f32(rotated_pos[1] + uniforms["posY"])
    clip_x = _f32(rotated_pos[0] * uniforms["viewScale"])
    clip_y = _f32(rotated_pos[1] * uniforms["viewScale"])
    clip_x = _f32(clip_x / uniforms["aspect"])
    near_z = -10.0
    far_z = 10.0
    ndc_z = _f32(_f32(rotated_pos[2] - near_z) / _f32(far_z - near_z))
    return {"clipX": clip_x, "clipY": clip_y, "ndcZ": ndc_z, "rotatedNormal": rotated_normal, "rotatedPos": rotated_pos}


def _fragment_stage(v_normal, _v_position, uniforms):
    normal = _vec3_normalize(v_normal)
    light_dir = _vec3_normalize(
        _vec3(uniforms["lightDirection"][0], uniforms["lightDirection"][1], uniforms["lightDirection"][2])
    )
    view_dir = _vec3(0, 0, 1)
    mesh_color = _vec3(uniforms["meshColor"][0], uniforms["meshColor"][1], uniforms["meshColor"][2])
    ambient = _vec3(
        _f32(uniforms["ambientColor"][0] * mesh_color[0]),
        _f32(uniforms["ambientColor"][1] * mesh_color[1]),
        _f32(uniforms["ambientColor"][2] * mesh_color[2]),
    )
    diffuse_factor = max(_f32(normal[0] * light_dir[0] + normal[1] * light_dir[1] + normal[2] * light_dir[2]), 0)
    diffuse = _vec3(
        _f32(_f32(uniforms["diffuseColor"][0] * diffuse_factor) * mesh_color[0] * uniforms["diffuseIntensity"]),
        _f32(_f32(uniforms["diffuseColor"][1] * diffuse_factor) * mesh_color[1] * uniforms["diffuseIntensity"]),
        _f32(_f32(uniforms["diffuseColor"][2] * diffuse_factor) * mesh_color[2] * uniforms["diffuseIntensity"]),
    )
    half_dir = _vec3_normalize(_vec3(_f32(light_dir[0] + view_dir[0]), _f32(light_dir[1] + view_dir[1]), _f32(light_dir[2] + view_dir[2])))
    spec_angle = max(_f32(half_dir[0] * normal[0] + half_dir[1] * normal[1] + half_dir[2] * normal[2]), 0)
    specular_factor = 1 if spec_angle == 0 and uniforms["shininess"] == 0 else math.pow(spec_angle, uniforms["shininess"])
    specular = _vec3(
        _f32(_f32(uniforms["specularColor"][0] * _f32(specular_factor)) * uniforms["specularIntensity"]),
        _f32(_f32(uniforms["specularColor"][1] * _f32(specular_factor)) * uniforms["specularIntensity"]),
        _f32(_f32(uniforms["specularColor"][2] * _f32(specular_factor)) * uniforms["specularIntensity"]),
    )
    rim_base = _f32(1 - max(_f32(normal[0] * view_dir[0] + normal[1] * view_dir[1] + normal[2] * view_dir[2]), 0))
    rim = 1 if rim_base == 0 and uniforms["rimPower"] == 0 else math.pow(rim_base, uniforms["rimPower"])
    rim_light = _vec3(_f32(rim * uniforms["rimIntensity"]), _f32(rim * uniforms["rimIntensity"]), _f32(rim * uniforms["rimIntensity"]))
    color = _vec3(
        _f32(_f32(ambient[0] + diffuse[0]) + _f32(specular[0] + rim_light[0])),
        _f32(_f32(ambient[1] + diffuse[1]) + _f32(specular[1] + rim_light[1])),
        _f32(_f32(ambient[2] + diffuse[2]) + _f32(specular[2] + rim_light[2])),
    )
    if uniforms["wireframe"] == 1:
        # dFdx/dFdy of the interpolated normal, evaluated analytically per triangle by
        # the caller (screen-space derivatives are per-triangle-constant here up to the
        # GPU's 2x2 helper-quad mixing at edges). Caller passes them via uniforms.
        ndx = uniforms["_dFdxNormal"]
        ndy = uniforms["_dFdyNormal"]
        normal_edge = _f32(
            _f32(math.hypot(_f32(ndx[0]), _f32(ndx[1]), _f32(ndx[2])) + math.hypot(_f32(ndy[0]), _f32(ndy[1]), _f32(ndy[2])))
        )
        if normal_edge < 0.1:
            return None  # discard: interior pixel
        color = _vec3(mesh_color[0], mesh_color[1], mesh_color[2])
    # Gamma correction: pow(color, 1/2.2)
    gamma = _f32(1 / 2.2)
    return _vec3(_f32(math.pow(color[0], gamma)), _f32(math.pow(color[1], gamma)), _f32(math.pow(color[2], gamma)))


MESH_DRAW_OPS = {"render/meshRender:render"}


def get_mesh_op(effect_id, program):
    return mesh_render_triangles_draw if f"{effect_id}:{program}" in MESH_DRAW_OPS else None


def mesh_render_triangles_draw(inputs, destination, uniforms, _render_pass, external_inputs=None):
    mesh_data = (external_inputs or {}).get("meshData")
    if not mesh_data:
        raise ValueError("render/meshRender requires external mesh data (externalInputs.meshData)")
    positions = mesh_data.get("positions")
    if positions is None:
        positions = mesh_data["positionData"]
    normals = mesh_data["normalData"]
    tex_width = mesh_data["texWidth"]
    tex_height = mesh_data["texHeight"]
    width = destination.width
    height = destination.height
    data = destination.data
    full_resolution = uniforms.get("fullResolution")
    if full_resolution is not None:
        aspect = _f32(float(full_resolution[0]) / float(full_resolution[1]))
    else:
        aspect = _f32(width / height)
    wireframe = uniforms.get("wireframe")
    wireframe = 0 if wireframe is None else int(wireframe)
    resolved = dict(uniforms)
    resolved["aspect"] = aspect
    resolved["wireframe"] = wireframe
    # Per-pixel depth buffer cleared to 1.0 (gl.clear(DEPTH_BUFFER_BIT) each pass).
    depth = np.ones(width * height, dtype=np.float32)
    covered = 0
    vertex_count = tex_width * tex_height
    triangle_count = vertex_count // 3
    for tri in range(triangle_count):
        verts = []
        all_invalid = True
        for v in range(3):
            texel = tri * 3 + v
            x = texel % tex_width
            y = texel // tex_width
            pi = (y * tex_width + x) * 4
            pos_data = [positions[pi], positions[pi + 1], positions[pi + 2], positions[pi + 3]]
            normal_data = [normals[pi], normals[pi + 1], normals[pi + 2], normals[pi + 3]]
            if pos_data[3] != 0:
                all_invalid = False
            stage = _vertex_stage(pos_data, normal_data, resolved)
            # Window coordinates, GL bottom-up: px = (ndcX + 1) / 2 * width.
            px = _f32(_f32(_f32(stage["clipX"] + 1) * 0.5) * width)
            py = _f32(_f32(_f32(stage["clipY"] + 1) * 0.5) * height)
            verts.append({"px": px, "py": py, "z": stage["ndcZ"], "normal": stage["rotatedNormal"], "position": stage["rotatedPos"]})
        if all_invalid:
            continue
        v0, v1, v2 = verts
        # Signed area in GL window space (y-up); CCW = front face.
        area = _f32(_f32(_f32(v1["px"] - v0["px"]) * _f32(v2["py"] - v0["py"])) - _f32(_f32(v2["px"] - v0["px"]) * _f32(v1["py"] - v0["py"])))
        if not area > 0:
            continue  # back face or degenerate: culled
        # Analytic screen-space derivatives of the interpolated normal (wireframe).
        det = _f32(
            _f32(_f32(v0["px"] * _f32(v1["py"] - v2["py"])) + _f32(v1["px"] * _f32(v2["py"] - v0["py"])))
            + _f32(v2["px"] * _f32(v0["py"] - v1["py"]))
        )
        d_fdx_normal = [0, 0, 0]
        d_fdy_normal = [0, 0, 0]
        if resolved["wireframe"] == 1 and det != 0:
            # dFdx(vNormal) and dFdy(vNormal): standard barycentric-gradient numerators
            # with the full determinant dividing the SUM (the det division applies to
            # the complete edge-function numerator, not just its last term).

            def dndx(comp):
                return _f32(
                    (
                        _f32(_f32(v0["normal"][comp] * _f32(v1["py"] - v2["py"])) + _f32(v1["normal"][comp] * _f32(v2["py"] - v0["py"])))
                        + _f32(v2["normal"][comp] * _f32(v0["py"] - v1["py"]))
                    )
                    / det
                )

            def dndy(comp):
                return _f32(
                    (
                        _f32(_f32(v0["normal"][comp] * _f32(v2["px"] - v1["px"])) + _f32(v1["normal"][comp] * _f32(v0["px"] - v2["px"])))
                        + _f32(v2["normal"][comp] * _f32(v1["px"] - v0["px"]))
                    )
                    / det
                )

            d_fdx_normal = [dndx(0), dndx(1), dndx(2)]
            d_fdy_normal = [dndy(0), dndy(1), dndy(2)]
        frag_uniforms = dict(resolved)
        if resolved["wireframe"] == 1:
            frag_uniforms["_dFdxNormal"] = d_fdx_normal
            frag_uniforms["_dFdyNormal"] = d_fdy_normal
        # Bounding box of the triangle, clamped to the viewport.
        min_x = max(0, math.floor(min(v0["px"], v1["px"], v2["px"]) - 0.5))
        max_x = min(width - 1, math.ceil(max(v0["px"], v1["px"], v2["px"]) - 0.5))
        min_y_gl = max(0, math.floor(min(v0["py"], v1["py"], v2["py"]) - 0.5))
        max_y_gl = min(height - 1, math.ceil(max(v0["py"], v1["py"], v2["py"]) - 0.5))
        for py_gl in range(min_y_gl, max_y_gl + 1):
            # Surface rows are top-down; GL window y is bottom-up.
            row = height - 1 - py_gl
            cy = _f32(py_gl + 0.5)
            for px_gl in range(min_x, max_x + 1):
                cx = _f32(px_gl + 0.5)
                # Barycentric coordinates via edge functions (CCW, positive area).
                b0 = _f32(_f32(_f32(v1["px"] - v0["px"]) * _f32(cy - v0["py"])) - _f32(_f32(v1["py"] - v0["py"]) * _f32(cx - v0["px"]))) / area
                b1 = _f32(_f32(_f32(v2["px"] - v1["px"]) * _f32(cy - v1["py"])) - _f32(_f32(v2["py"] - v1["py"]) * _f32(cx - v1["px"]))) / area
                b2 = 1 - _f32(b0 + b1)
                if not (b0 >= 0 and b1 >= 0 and b2 >= 0):
                    continue
                z = _f32(_f32(_f32(b0 * v0["z"]) + _f32(b1 * v1["z"])) + _f32(b2 * v2["z"]))
                depth_index = row * width + px_gl
                if not z < depth[depth_index]:
                    continue  # depthFunc LESS
                depth[depth_index] = z
                v_normal = [
                    _f32(_f32(_f32(b0 * v0["normal"][0]) + _f32(b1 * v1["normal"][0])) + _f32(b2 * v2["normal"][0])),
                    _f32(_f32(_f32(b0 * v0["normal"][1]) + _f32(b1 * v1["normal"][1])) + _f32(b2 * v2["normal"][1])),
                    _f32(_f32(_f32(b0 * v0["normal"][2]) + _f32(b1 * v1["normal"][2])) + _f32(b2 * v2["normal"][2])),
                ]
                v_position = [
                    _f32(_f32(_f32(b0 * v0["position"][0]) + _f32(b1 * v1["position"][0])) + _f32(b2 * v2["position"][0])),
                    _f32(_f32(_f32(b0 * v0["position"][1]) + _f32(b1 * v1["position"][1])) + _f32(b2 * v2["position"][1])),
                    _f32(_f32(_f32(b0 * v0["position"][2]) + _f32(b1 * v1["position"][2])) + _f32(b2 * v2["position"][2])),
                ]
                color = _fragment_stage(v_normal, v_position, frag_uniforms)
                if color is None:
                    continue  # wireframe discard
                out_index = depth_index * 4
                data[out_index] = color[0]
                data[out_index + 1] = color[1]
                data[out_index + 2] = color[2]
                data[out_index + 3] = 1
                covered += 1
    return covered