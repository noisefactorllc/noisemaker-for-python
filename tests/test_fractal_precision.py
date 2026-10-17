import hashlib

import pytest

from noisemaker_cpu.renderer import render_dsl


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ("mode: 1", "7a99dfb06ea81eab7b301bfe870c873afbf945c6846fa09e492ac57f9164a5f8"),
        ("rotation: 30, iterations: 10, mode: 1", "e8582e26dda5b6e9581a33b73a3958b9d7127e728fdd2bde55f7de89e88692d8"),
        ("rotation: 30, iterations: 10", "8c7c7406e5039802b2266d64ae43f477b128e16bb4d2c95f18e1b7f1b5825f97"),
    ],
)
def test_fractal_julia_matches_cpu_precision_receipts(params, expected):
    source = f"search classicNoisedeck\nfractal({params}).write(o0)\nrender(o0)"
    result = render_dsl(source, width=64, height=64, seed=1, time=0.25)
    assert hashlib.sha256(result.to_rgba8()).hexdigest() == expected


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        (
            'mode: 1, zoomAmt: 37, centerX: 21, centerY: -13, rotation: 30',
            '62e44460ecf67595fe1db6357913c525a7a137beeaac7e1ad3651531d1b58d92',
        ),
        (
            'mode: 1, speed: 37, offsetX: 14, offsetY: -18, iterations: 37',
            '8f8747044ec4da6cb9bc6b1acc9c7e0585417e7089b1e3bb92215b0ae2fc80e6',
        ),
        (
            'palette: 0, mode: 1, colorMode: 4, paletteMode: 0, rotatePalette: 17, repeatPalette: 3, cyclePalette: 1',
            '64ab37bd2b7c88a7fe0a009b5af169acf8fd7a7b3508a2366d442aa9877f97e5',
        ),
        (
            'palette: 0, mode: 1, colorMode: 4, paletteMode: 1, rotatePalette: 17, repeatPalette: 3, cyclePalette: -1',
            'eab20b654e9d6f6804028f70d9ef4ec3d7ec146b0f03312c73457e0e8ff2a3b3',
        ),
        (
            'palette: 0, mode: 1, colorMode: 4, paletteMode: 2, rotatePalette: 17, repeatPalette: 3',
            '91b3c23a223ac7aaf9413726a23cdd12ca5dc8f14714292b7a6e381691ed15a3',
        ),
        (
            'mode: 1, colorMode: 6, hueRange: 37, levels: 8',
            '02dcba8963f06bd88224403b798ec5616f43757f81e9223ee3bd7b51098a0ed1',
        ),
        (
            'mode: 1, bgAlpha: 37, cutoff: 10',
            '0d5282ccd4ffdcbef7c48a16a389b8ad7ed6c5c8f00eeea2705e4a7497f3d5de',
        ),
        (
            'type: 1, mode: 1, colorMode: 4, levels: 8',
            '67717df7951ff4670ebeb9a95a3b4e664e194a54d508e7d5a10a7cd7d622cbfc',
        ),
        (
            'type: 2, mode: 1, speed: 12, colorMode: 6',
            '5af302190e284252afe453372db1480e09d319e56464d321059fff845aa98336',
        ),
    ],
)
def test_fractal_transform_and_color_matches_cpu(params, expected):
    source = f"search classicNoisedeck\nfractal({params}).write(o0)\nrender(o0)"
    result = render_dsl(source, width=64, height=48, seed=1, time=0.25)
    assert hashlib.sha256(result.to_rgba8()).hexdigest() == expected
