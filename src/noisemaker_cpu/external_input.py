"""CPU external-input state for the reactive (MIDI/audio) and mesh (OBJ) effects.

Port of noisemaker-cpu ``src/runtime/external-input.js`` (the reactive/mesh
import). It mirrors the rendering-relevant subset of the upstream
``MidiState``/``AudioState``: per-channel key velocities and gate,
CC/pitch-bend/pressure storage, the 24-PPQ clock counter, and the packed
128x16 note-grid texture the ``roll`` kernel samples. It is deliberately
deterministic: no Web MIDI ports, no timing — fixtures feed raw message bytes
through ``handle_message`` exactly like the authority harness does.

``parse_obj``/``pack_mesh_data_for_textures`` port the upstream obj-parser
(same file layout, same fan triangulation with reversed winding, same RGBA
texture packing) so ``render/meshLoader``/``render/meshRender`` consume
identical mesh-texture data.

Float semantics follow the JS source: parse and normal math run in float64
(Python ``float``), stored results convert to float32 exactly where the JS
code stores into a ``Float32Array``.
"""

from __future__ import annotations

import math
import re

import numpy as np

UNROUTED = 0

_F32 = np.float32


class MidiChannelState:
    def __init__(self) -> None:
        self.key = 0
        self.velocity = 0
        self.gate = 0
        self.keys = np.zeros(128, dtype=np.uint8)
        self.cc = np.zeros(128, dtype=np.uint8)
        self.pitch_bend = 8192
        self.pressure = 0
        self.poly_pressure = np.zeros(128, dtype=np.uint8)
        self.program = 0

    def note_on(self, key: int, velocity: int) -> None:
        self.key = key
        self.velocity = velocity
        self.gate = 1
        self.keys[key] = velocity

    def note_off(self, key: int | None = None) -> None:
        self.gate = 0
        if key is None:
            self.keys[:] = 0
            return
        self.keys[key] = 0
        self.poly_pressure[key] = 0

    def control_change(self, controller: int, value: int) -> None:
        if not isinstance(controller, int) or not 0 <= controller <= 127:
            return
        if not isinstance(value, int) or not 0 <= value <= 127:
            return
        self.cc[controller] = value
        if controller in (120, 123):
            self.gate = 0
            self.keys[:] = 0
        elif controller == 121:
            for cc in range(128):
                self.cc[cc] = 127 if cc == 11 else 0
            self.pitch_bend = 8192
            self.pressure = 0
            self.poly_pressure[:] = 0

    def reset(self) -> None:
        self.key = 0
        self.velocity = 0
        self.gate = 0
        self.keys[:] = 0
        self.cc[:] = 0
        self.pitch_bend = 8192
        self.pressure = 0
        self.poly_pressure[:] = 0
        self.program = 0


class MidiState:
    def __init__(self) -> None:
        self.channels = {i: MidiChannelState() for i in range(1, 17)}
        # MIDI clock pulse count (24 PPQ)
        self.clock_count = 0
        # Note grid texture data: 128 keys x 16 channels x RGBA. Row order matches
        # the upstream upload: row 0 is channel 1, R = velocity (0-1), G = gate,
        # B = A = 0. Stored as float32 like the JS Float32Array.
        self.note_grid = np.zeros(128 * 16 * 4, dtype=np.float32)

    def get_channel(self, channel) -> MidiChannelState | None:
        if not isinstance(channel, int) or not 1 <= channel <= 16:
            return None
        return self.channels[channel]

    def update_note_grid(self) -> None:
        grid = self.note_grid.reshape(16, 128, 4)
        for ch in range(16):
            keys = self.channels[ch + 1].keys
            for k in range(128):
                v = int(keys[k])
                # R: velocity (f32 division like the JS Float32Array store)
                grid[ch, k, 0] = _F32(v / 127) if v > 0 else 0.0
                # G: gate; B and A stay 0
                grid[ch, k, 1] = 1.0 if v > 0 else 0.0

    def reset(self) -> None:
        for state in self.channels.values():
            state.reset()
        self.clock_count = 0
        self.note_grid[:] = 0

    def handle_message(self, data) -> int:
        """Process a raw MIDI message ``[status, data1, data2]``. Returns 0 when
        routed, -1 when the status byte is unhandled."""
        if data is None or len(data) < 1:
            return UNROUTED
        status = data[0]
        if status == 0xF8:
            self.clock_count += 1
            return 0
        if status == 0xFF:
            self.reset()
            return 0
        # Two-byte MIDI messages (0xC0 program change, 0xD0 channel pressure)
        # carry no velocity byte: the JS oracle reads data[2] as `undefined`
        # there, so an absent third byte must not raise here.
        key = data[1] if len(data) > 1 else None
        velocity = data[2] if len(data) > 2 else None
        channel = (status & 0x0F) + 1
        message_type = status & 0xF0
        if message_type == 0xF0:
            return -1
        if not isinstance(key, int) or not 0 <= key <= 127:
            return -1
        if message_type != 0xD0 and (not isinstance(velocity, int) or not 0 <= velocity <= 127):
            return -1
        channel_state = self.get_channel(channel)
        if channel_state is None:
            return -1
        if message_type == 0x90 and velocity > 0:
            channel_state.note_on(key, velocity)
            return 0
        if message_type == 0x80 or (message_type == 0x90 and velocity == 0):
            channel_state.note_off(key)
            return 0
        if message_type == 0xA0:
            channel_state.poly_pressure[key] = velocity
            return 0
        if message_type == 0xB0:
            channel_state.control_change(key, velocity)
            return 0
        if message_type == 0xC0:
            channel_state.program = key
            return 0
        if message_type == 0xD0:
            channel_state.pressure = key
            return 0
        if message_type == 0xE0:
            channel_state.pitch_bend = key | (velocity << 7)
            return 0
        return -1


class AudioState:
    def __init__(self) -> None:
        self.waveform = np.zeros(128, dtype=np.float32)
        self.spectrum = np.zeros(128, dtype=np.float32)

    def set_waveform(self, values) -> None:
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (128,):
            raise RangeError("audio waveform requires exactly 128 samples")
        self.waveform = values.astype(np.float32)

    def set_spectrum(self, values) -> None:
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (128,):
            raise RangeError("audio spectrum requires exactly 128 bins")
        self.spectrum = values.astype(np.float32)


class RangeError(ValueError):
    pass


def _parse_float(text: str) -> float:
    """JS parseFloat semantics: leading numeric prefix, NaN -> falsy -> 0."""
    match = re.match(r"[+-]?(Infinity|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)", text.strip())
    if not match:
        return 0.0
    token = match.group(0)
    if token == "Infinity":
        return math.inf
    try:
        return float(token)
    except ValueError:
        return 0.0


def parse_obj(obj_text: str) -> dict:
    """Parse Wavefront OBJ text into de-indexed triangle-soup vertex data.

    Port of the upstream obj-parser ``parseOBJ``: fan triangulation for faces
    with more than three vertices, reversed winding (OBJ CW to GL CCW),
    per-face normal fallback when a vertex carries no ``vn`` reference, and the
    smooth vertex-normal fallback when the file declares no ``vn`` lines.
    """
    raw_positions: list[list[float]] = []
    raw_normals: list[list[float]] = []
    raw_uvs: list[list[float]] = []
    positions: list[float] = []
    normals: list[float] = []
    uvs: list[float] = []

    def add_vertex(v: dict) -> None:
        if 0 <= v["vIdx"] < len(raw_positions):
            positions.extend(raw_positions[v["vIdx"]])
        else:
            positions.extend((0.0, 0.0, 0.0))
        if 0 <= v["vnIdx"] < len(raw_normals):
            normals.extend(raw_normals[v["vnIdx"]])
        else:
            normals.extend((0.0, 0.0, 1.0))
        if 0 <= v["vtIdx"] < len(raw_uvs):
            uvs.extend(raw_uvs[v["vtIdx"]])
        else:
            uvs.extend((0.0, 0.0))

    for raw_line in obj_text.split("\n"):
        line = raw_line.strip()
        if len(line) == 0 or line.startswith("#"):
            continue
        parts = line.split()
        cmd = parts[0]
        if cmd == "v":
            raw_positions.append(
                [
                    _parse_float(parts[1]),
                    _parse_float(parts[2]),
                    _parse_float(parts[3]),
                ]
            )
        elif cmd == "vn":
            raw_normals.append(
                [
                    _parse_float(parts[1]),
                    _parse_float(parts[2]),
                    _parse_float(parts[3]),
                ]
            )
        elif cmd == "vt":
            raw_uvs.append(
                [
                    _parse_float(parts[1]),
                    _parse_float(parts[2]),
                ]
            )
        elif cmd == "f":
            face_verts = []
            for i in range(1, len(parts)):
                indices = parts[i].split("/")
                v_idx = int(indices[0], 10) - 1
                vt_idx = int(indices[1], 10) - 1 if len(indices) > 1 and indices[1] else -1
                vn_idx = int(indices[2], 10) - 1 if len(indices) > 2 and indices[2] else -1
                face_verts.append({"vIdx": v_idx, "vtIdx": vt_idx, "vnIdx": vn_idx})
            # Fan triangulation, reversed winding: OBJ CW to OpenGL CCW.
            for i in range(1, len(face_verts) - 1):
                add_vertex(face_verts[0])
                add_vertex(face_verts[i + 1])
                add_vertex(face_verts[i])

    # If no normals were provided, compute smooth vertex normals: exact port of
    # the upstream obj-parser computeFaceNormals (per-triangle face normals
    # averaged by position key, rounded to 1e-4 to merge duplicate vertices).
    if not raw_normals and positions:
        _compute_face_normals(positions, normals)

    return {
        "positions": np.asarray(positions, dtype=np.float32),
        "normals": np.asarray(normals, dtype=np.float32),
        "uvs": np.asarray(uvs, dtype=np.float32),
        "vertexCount": len(positions) // 3,
    }


def pack_mesh_data_for_textures(positions, normals, uvs, tex_width: int, tex_height: int) -> dict:
    """Pack triangle-soup mesh data into texture-sized RGBA arrays.

    Port of the upstream obj-parser ``packMeshDataForTextures``: one texel per
    vertex, position w = 1 marks a valid vertex (remaining texels keep w = 0).
    texWidth/texHeight come from the upstream mesh-texture convention (256x256).
    """
    positions = np.asarray(positions, dtype=np.float32).ravel()
    normals = np.asarray(normals, dtype=np.float32).ravel()
    uvs = np.asarray(uvs, dtype=np.float32).ravel()
    max_vertices = tex_width * tex_height
    vertex_count = positions.shape[0] // 3
    if vertex_count > max_vertices:
        # Upstream truncates with a console warning; parity fixtures stay below the cap.
        pass
    used_vertices = min(vertex_count, max_vertices)
    pixel_count = tex_width * tex_height
    position_data = np.zeros(pixel_count * 4, dtype=np.float32)
    normal_data = np.zeros(pixel_count * 4, dtype=np.float32)
    uv_data = np.zeros(pixel_count * 4, dtype=np.float32)
    for i in range(used_vertices):
        pi = i * 4
        vi3 = i * 3
        vi2 = i * 2
        position_data[pi] = positions[vi3]
        position_data[pi + 1] = positions[vi3 + 1]
        position_data[pi + 2] = positions[vi3 + 2]
        position_data[pi + 3] = 1.0
        normal_data[pi] = normals[vi3]
        normal_data[pi + 1] = normals[vi3 + 1]
        normal_data[pi + 2] = normals[vi3 + 2]
        normal_data[pi + 3] = 0.0
        uv_data[pi] = uvs[vi2]
        uv_data[pi + 1] = uvs[vi2 + 1]
        uv_data[pi + 2] = 0.0
        uv_data[pi + 3] = 0.0
    for i in range(used_vertices, pixel_count):
        position_data[i * 4 + 3] = 0.0
    return {
        "positionData": position_data,
        "normalData": normal_data,
        "uvData": uv_data,
        "vertexCount": used_vertices,
    }


def _compute_face_normals(positions: list[float], normals: list[float]) -> None:
    """Smooth vertex normals for un-normalized OBJ files: exact port of the
    upstream obj-parser computeFaceNormals (face normals from reversed-winding
    triangles, averaged per rounded position key, threshold 1e-4)."""
    vertex_count = len(positions) // 3
    triangle_count = vertex_count // 3
    face_normals = [0.0] * (triangle_count * 3)
    for tri in range(triangle_count):
        i0 = tri * 9
        i1 = i0 + 3
        i2 = i0 + 6
        ax, ay, az = positions[i0], positions[i0 + 1], positions[i0 + 2]
        bx, by, bz = positions[i1], positions[i1 + 1], positions[i1 + 2]
        cx, cy, cz = positions[i2], positions[i2 + 1], positions[i2 + 2]
        e1x, e1y, e1z = bx - ax, by - ay, bz - az
        e2x, e2y, e2z = cx - ax, cy - ay, cz - az
        nx = e1y * e2z - e1z * e2y
        ny = e1z * e2x - e1x * e2z
        nz = e1x * e2y - e1y * e2x
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length > 0.0001:
            nx /= length
            ny /= length
            nz /= length
        else:
            nx, ny, nz = 0.0, 0.0, 1.0
        face_normals[tri * 3] = nx
        face_normals[tri * 3 + 1] = ny
        face_normals[tri * 3 + 2] = nz

    def _round(v: float) -> float:
        # JS Math.round: half away from zero.
        return math.floor(v * 10000 + 0.5) / 10000

    def _key(v: float) -> str:
        r = _round(v)
        if r == 0:
            r = 0.0  # JS String(-0) is "0"
        return repr(r)

    pos_to_normal: dict[str, dict] = {}
    for v in range(vertex_count):
        px, py, pz = positions[v * 3], positions[v * 3 + 1], positions[v * 3 + 2]
        key = f"{_key(px)},{_key(py)},{_key(pz)}"
        tri_idx = v // 3
        acc = pos_to_normal.setdefault(key, {"nx": 0.0, "ny": 0.0, "nz": 0.0, "count": 0})
        acc["nx"] += face_normals[tri_idx * 3]
        acc["ny"] += face_normals[tri_idx * 3 + 1]
        acc["nz"] += face_normals[tri_idx * 3 + 2]
        acc["count"] += 1
    for acc in pos_to_normal.values():
        length = math.sqrt(acc["nx"] ** 2 + acc["ny"] ** 2 + acc["nz"] ** 2)
        if length > 0.0001:
            acc["nx"] /= length
            acc["ny"] /= length
            acc["nz"] /= length
        else:
            acc["nx"], acc["ny"], acc["nz"] = 0.0, 0.0, 1.0
    for v in range(vertex_count):
        px, py, pz = positions[v * 3], positions[v * 3 + 1], positions[v * 3 + 2]
        key = f"{_key(px)},{_key(py)},{_key(pz)}"
        acc = pos_to_normal[key]
        normals[v * 3] = acc["nx"]
        normals[v * 3 + 1] = acc["ny"]
        normals[v * 3 + 2] = acc["nz"]