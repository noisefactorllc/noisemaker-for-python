"""Mirror of the sibling's landscape-edge-ties rendered test.

A voxel ray that passes through the edge shared by two cell boundaries
crosses both at one distance and enters the cell beyond the edge. Whether
the two crossings compare equal depends on rounding. On the center column
of an odd-width orthographic frame the ray's x and z crossings are equal at
every step, so the cell there must show the first face its neighbors leave
exposed, not the first crossed axis in y, x, z order. A white cliff lit
only from +z shows this: every face the pixels beside the center column
show, the center column must show too.
"""

from noisemaker_cpu import renderer

_CHAIN = (
    "search synth, filter, synth3d, render\n"
    "gradient(type: linear, color1: #000000, color2: #ffffff)"
    ".threshold(level: 0.5, sharpness: 1).write(o1)\n"
    "solid(color: #ffffff).write(o2)\n"
    "heightmap3d(heightTex: read(o1), tex: read(o2), volumeSize: x16,"
    " heightScale: 1, baseHeight: 0)"
    ".renderLandscape3d(lightDirection: vec3(0, 0, 1), ambient: 0,"
    " diffuseIntensity: 1, specularIntensity: 0, bgAlpha: 0).write(o0)\n"
    "render(o0)"
)

_WIDTH = 129
_HEIGHT = 129
_WHITE = "255,255,255,255"


def test_a_voxel_ray_through_an_edge_shows_the_face_its_neighbors_leave_exposed():
    frame = renderer.render_dsl(_CHAIN, width=_WIDTH, height=_HEIGHT).to_rgba8()

    def pixel(x, y):
        offset = (y * _WIDTH + x) * 4
        return ",".join(str(channel) for channel in frame[offset : offset + 4])

    middle = (_WIDTH - 1) // 2
    face_rows = [
        y
        for y in range(_HEIGHT)
        if pixel(middle - 1, y) == _WHITE and pixel(middle + 1, y) == _WHITE
    ]
    assert face_rows, "the center column must cross lit faces through voxel edges"
    off_face = [y for y in face_rows if pixel(middle, y) != _WHITE]
    assert not off_face, (
        f"the center column looks at lit faces through voxel edges, and"
        f" {len(off_face)} of its {len(face_rows)} pixels there show"
        f" {pixel(middle, off_face[0])}"
    )
