def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_ditherType = U["ditherType"]
    _u_threshold = U["threshold"]
    _u_matrixScale = U["matrixScale"]
    _u_renderScale = U["renderScale"]
    _u_palette = U["palette"]
    _u_levels = U["levels"]
    _u_time = U["time"]
    _u_mixAmount = U["mixAmount"]
    g.DITHER_BAYER_2X2 = rt.i(0)
    g.DITHER_BAYER_4X4 = rt.i(1)
    g.DITHER_BAYER_8X8 = rt.i(2)
    g.DITHER_DOT = rt.i(3)
    g.DITHER_LINE = rt.i(4)
    g.DITHER_CROSSHATCH = rt.i(5)
    g.DITHER_NOISE = rt.i(6)
    g.DITHER_ERROR_DIFFUSION = rt.i(7)
    g.PALETTE_INPUT = rt.i(0)
    g.PALETTE_MONOCHROME = rt.i(1)
    g.PALETTE_DOT_MATRIX_GREEN = rt.i(2)
    g.PALETTE_AMBER = rt.i(3)
    g.PALETTE_PICO8 = rt.i(4)
    g.PALETTE_C64 = rt.i(5)
    g.PALETTE_CGA = rt.i(6)
    g.PALETTE_ZX_SPECTRUM = rt.i(7)
    g.PALETTE_APPLE_II = rt.i(8)
    g.PALETTE_EGA = rt.i(9)
    g.bayer2x2 = rt.construct(16, rt.binary("/", rt.f(0.0), rt.f(4.0), 1), rt.binary("/", rt.f(2.0), rt.f(4.0), 1), rt.binary("/", rt.f(0.0), rt.f(4.0), 1), rt.binary("/", rt.f(2.0), rt.f(4.0), 1), rt.binary("/", rt.f(3.0), rt.f(4.0), 1), rt.binary("/", rt.f(1.0), rt.f(4.0), 1), rt.binary("/", rt.f(3.0), rt.f(4.0), 1), rt.binary("/", rt.f(1.0), rt.f(4.0), 1), rt.binary("/", rt.f(0.0), rt.f(4.0), 1), rt.binary("/", rt.f(2.0), rt.f(4.0), 1), rt.binary("/", rt.f(0.0), rt.f(4.0), 1), rt.binary("/", rt.f(2.0), rt.f(4.0), 1), rt.binary("/", rt.f(3.0), rt.f(4.0), 1), rt.binary("/", rt.f(1.0), rt.f(4.0), 1), rt.binary("/", rt.f(3.0), rt.f(4.0), 1), rt.binary("/", rt.f(1.0), rt.f(4.0), 1))
    g.bayer4x4 = rt.construct(16, rt.binary("/", rt.f(0.0), rt.f(16.0), 1), rt.binary("/", rt.f(8.0), rt.f(16.0), 1), rt.binary("/", rt.f(2.0), rt.f(16.0), 1), rt.binary("/", rt.f(10.0), rt.f(16.0), 1), rt.binary("/", rt.f(12.0), rt.f(16.0), 1), rt.binary("/", rt.f(4.0), rt.f(16.0), 1), rt.binary("/", rt.f(14.0), rt.f(16.0), 1), rt.binary("/", rt.f(6.0), rt.f(16.0), 1), rt.binary("/", rt.f(3.0), rt.f(16.0), 1), rt.binary("/", rt.f(11.0), rt.f(16.0), 1), rt.binary("/", rt.f(1.0), rt.f(16.0), 1), rt.binary("/", rt.f(9.0), rt.f(16.0), 1), rt.binary("/", rt.f(15.0), rt.f(16.0), 1), rt.binary("/", rt.f(7.0), rt.f(16.0), 1), rt.binary("/", rt.f(13.0), rt.f(16.0), 1), rt.binary("/", rt.f(5.0), rt.f(16.0), 1))
    g.FS_BLOCK = rt.i(4)
    g.FS_APRON_MIN = rt.i(4)
    g.FS_APRON_MAX = rt.i(11)
    g.FS_RPAD = rt.i(2)
    g.FS_ERR_W = rt.binary("+", rt.binary("+", rt.binary("+", g.FS_BLOCK, g.FS_APRON_MAX, 1), g.FS_RPAD, 1), rt.i(1), 1)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def getBayer8x8__int_int(x, y):
        x = rt.binary("&", x, rt.i(7), 1)
        y = rt.binary("&", y, rt.i(7), 1)
        if rt.binary("==", y, rt.i(0)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(0.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(32.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(8.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(40.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(2.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(34.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(10.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(42.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(1)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(48.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(16.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(56.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(24.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(50.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(18.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(58.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(26.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(2)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(12.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(44.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(4.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(36.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(14.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(46.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(6.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(38.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(3)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(60.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(28.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(52.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(20.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(62.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(30.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(54.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(22.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(4)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(3.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(35.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(11.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(43.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(1.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(33.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(9.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(41.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(5)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(51.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(19.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(59.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(27.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(49.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(17.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(57.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(25.0), rt.f(64.0), 1)
        if rt.binary("==", y, rt.i(6)):
            if rt.binary("==", x, rt.i(0)):
                return rt.binary("/", rt.f(15.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(1)):
                return rt.binary("/", rt.f(47.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(2)):
                return rt.binary("/", rt.f(7.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(3)):
                return rt.binary("/", rt.f(39.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(4)):
                return rt.binary("/", rt.f(13.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(5)):
                return rt.binary("/", rt.f(45.0), rt.f(64.0), 1)
            if rt.binary("==", x, rt.i(6)):
                return rt.binary("/", rt.f(5.0), rt.f(64.0), 1)
            return rt.binary("/", rt.f(37.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(0)):
            return rt.binary("/", rt.f(63.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(1)):
            return rt.binary("/", rt.f(31.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(2)):
            return rt.binary("/", rt.f(55.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(3)):
            return rt.binary("/", rt.f(23.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(4)):
            return rt.binary("/", rt.f(61.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(5)):
            return rt.binary("/", rt.f(29.0), rt.f(64.0), 1)
        if rt.binary("==", x, rt.i(6)):
            return rt.binary("/", rt.f(53.0), rt.f(64.0), 1)
        return rt.binary("/", rt.f(21.0), rt.f(64.0), 1)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def hash__vec2(p):
        p = rt.copy(p)
        v = pcg__vec3(cpu_uvec3__float_float_float(rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.i(0)))
        return rt.binary("/", rt.swizzle(v, "x"), rt.f(4294967295.0), 1)
    def dotPattern__vec2_float(uv, scale):
        uv = rt.copy(uv)
        p = rt.binary("*", uv, scale, 2)
        c = rt.binary("+", rt.component_wise("floor", p, width=2), rt.f(0.5), 2)
        d = rt.length(rt.binary("-", rt.component_wise("fract", p, width=2), rt.f(0.5), 2))
        return rt.component_wise("smoothstep", rt.f(0.5), rt.f(0.0), d, width=1)
    def linePattern__vec2_float(uv, scale):
        uv = rt.copy(uv)
        p = rt.binary("*", rt.swizzle(uv, "y"), scale, 1)
        return rt.binary("*", rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", p, width=1), rt.f(0.5), 1), width=1), rt.f(2.0), 1)
    def crosshatchPattern__vec2_float(uv, scale):
        uv = rt.copy(uv)
        p = rt.binary("*", uv, scale, 2)
        line1 = rt.binary("*", rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1), width=1), rt.f(0.5), 1), width=1), rt.f(2.0), 1)
        line2 = rt.binary("*", rt.component_wise("abs", rt.binary("-", rt.component_wise("fract", rt.binary("-", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1), width=1), rt.f(0.5), 1), width=1), rt.f(2.0), 1)
        return rt.component_wise("min", line1, line2, width=1)
    def getDitherThreshold__vec2_int_float(pixelCoord, type, scale):
        pixelCoord = rt.copy(pixelCoord)
        scaledCoord = rt.component_wise("floor", rt.binary("/", pixelCoord, scale, 2), width=2)
        x = rt.construct(1, rt.swizzle(scaledCoord, "x"))
        y = rt.construct(1, rt.swizzle(scaledCoord, "y"))
        if rt.binary("==", type, g.DITHER_BAYER_2X2):
            return g.bayer2x2[int(rt.binary("&", y, rt.i(1), 1))][int(rt.binary("&", x, rt.i(1), 1))]
        else:
            if rt.binary("==", type, g.DITHER_BAYER_4X4):
                return g.bayer4x4[int(rt.binary("&", y, rt.i(3), 1))][int(rt.binary("&", x, rt.i(3), 1))]
            else:
                if rt.binary("==", type, g.DITHER_BAYER_8X8):
                    return getBayer8x8__int_int(x, y)
                else:
                    if rt.binary("==", type, g.DITHER_DOT):
                        return dotPattern__vec2_float(pixelCoord, rt.binary("/", rt.f(1.0), rt.binary("*", rt.f(8.0), scale, 1), 1))
                    else:
                        if rt.binary("==", type, g.DITHER_LINE):
                            return linePattern__vec2_float(pixelCoord, rt.binary("/", rt.f(1.0), rt.binary("*", rt.f(8.0), scale, 1), 1))
                        else:
                            if rt.binary("==", type, g.DITHER_CROSSHATCH):
                                return crosshatchPattern__vec2_float(pixelCoord, rt.binary("/", rt.f(1.0), rt.binary("*", rt.f(8.0), scale, 1), 1))
                            else:
                                if rt.binary("==", type, g.DITHER_NOISE):
                                    return hash__vec2(rt.binary("+", scaledCoord, rt.binary("*", _u_time, rt.f(0.001), 1), 2))
        return rt.f(0.5)
    def quantizeWithDither__vec3_float_float_float(color, levels, ditherValue, thresh):
        color = rt.copy(color)
        adjustedDither = rt.binary("+", rt.binary("-", ditherValue, rt.f(0.5), 1), thresh, 1)
        dithered = rt.binary("+", color, rt.binary("/", adjustedDither, levels, 1), 3)
        return rt.binary("/", rt.component_wise("floor", rt.binary("*", dithered, levels, 3), width=3), rt.binary("-", levels, rt.f(1.0), 1), 3)
    def findClosestPaletteColor__vec3_int(color, paletteType):
        color = rt.copy(color)
        pass
    def colorDistance__vec3_vec3(a, b):
        a = rt.copy(a)
        b = rt.copy(b)
        diff = rt.binary("-", a, b, 3)
        return rt.dot(diff, diff)
    def findClosest4__vec3_vec3(color, pal):
        color = rt.copy(color)
        pal = rt.copy(pal)
        closest = pal[int(rt.i(0))]
        minDist = colorDistance__vec3_vec3(color, pal[int(rt.i(0))])
        i = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            dist = colorDistance__vec3_vec3(color, pal[int(i)])
            if rt.binary("<", dist, minDist):
                minDist = dist
                closest = pal[int(i)]
        return closest
    def findClosest15__vec3_vec3(color, pal):
        color = rt.copy(color)
        pal = rt.copy(pal)
        closest = pal[int(rt.i(0))]
        minDist = colorDistance__vec3_vec3(color, pal[int(rt.i(0))])
        i = rt.i(1)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<", i, rt.i(15))):
                break
            dist = colorDistance__vec3_vec3(color, pal[int(i)])
            if rt.binary("<", dist, minDist):
                minDist = dist
                closest = pal[int(i)]
        return closest
    def findClosest16__vec3_vec3(color, pal):
        color = rt.copy(color)
        pal = rt.copy(pal)
        closest = pal[int(rt.i(0))]
        minDist = colorDistance__vec3_vec3(color, pal[int(rt.i(0))])
        i = rt.i(1)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<", i, rt.i(16))):
                break
            dist = colorDistance__vec3_vec3(color, pal[int(i)])
            if rt.binary("<", dist, minDist):
                minDist = dist
                closest = pal[int(i)]
        return closest
    def findClosestPaletteColor__vec3_int(color, paletteType):
        color = rt.copy(color)
        if rt.binary("==", paletteType, g.PALETTE_MONOCHROME):
            luma = rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
            return rt.construct(3, (rt.f(1.0) if rt.binary(">", luma, rt.f(0.5)) else rt.f(0.0)))
        else:
            if rt.binary("==", paletteType, g.PALETTE_DOT_MATRIX_GREEN):
                return findClosest4__vec3_vec3(color, g.DOT_MATRIX)
            else:
                if rt.binary("==", paletteType, g.PALETTE_AMBER):
                    return findClosest4__vec3_vec3(color, g.AMBER)
                else:
                    if rt.binary("==", paletteType, g.PALETTE_PICO8):
                        return findClosest16__vec3_vec3(color, g.PICO8)
                    else:
                        if rt.binary("==", paletteType, g.PALETTE_C64):
                            return findClosest16__vec3_vec3(color, g.C64)
                        else:
                            if rt.binary("==", paletteType, g.PALETTE_CGA):
                                return findClosest4__vec3_vec3(color, g.CGA)
                            else:
                                if rt.binary("==", paletteType, g.PALETTE_ZX_SPECTRUM):
                                    return findClosest15__vec3_vec3(color, g.ZX_SPECTRUM)
                                else:
                                    if rt.binary("==", paletteType, g.PALETTE_APPLE_II):
                                        return findClosest16__vec3_vec3(color, g.APPLE_II)
                                    else:
                                        if rt.binary("==", paletteType, g.PALETTE_EGA):
                                            return findClosest16__vec3_vec3(color, g.EGA)
        return color
    def ditherWithPalette__vec3_float_float_int(color, ditherValue, thresh, paletteType):
        color = rt.copy(color)
        dithered = rt.binary("+", color, rt.binary("*", rt.binary("+", rt.binary("-", ditherValue, rt.f(0.5), 1), thresh, 1), rt.f(0.25), 1), 3)
        dithered = rt.component_wise("clamp", dithered, rt.f(0.0), rt.f(1.0), width=3)
        return findClosestPaletteColor__vec3_int(dithered, paletteType)
    def fsQuantize__vec3(v):
        v = rt.copy(v)
        if rt.binary("==", _u_palette, g.PALETTE_INPUT):
            maxLevel = rt.binary("-", _u_levels, rt.f(1.0), 1)
            return rt.binary("/", rt.component_wise("floor", rt.binary("+", rt.binary("*", v, maxLevel, 3), rt.f(0.5), 3), width=3), maxLevel, 3)
        return findClosestPaletteColor__vec3_int(v, _u_palette)
    def fsScale__void():
        if rt.binary("==", _u_palette, g.PALETTE_INPUT):
            return rt.binary("/", rt.f(1.0), _u_levels, 1)
        return rt.f(0.25)
    def fsSeedNoise__ivec2_int(blockOrigin, lane):
        blockOrigin = rt.copy(blockOrigin)
        v = pcg__vec3(cpu_uvec3__float_float_float(rt.construct(1, rt.binary("+", rt.swizzle(blockOrigin, "x"), rt.i(1), 1)), rt.construct(1, rt.binary("+", rt.swizzle(blockOrigin, "y"), rt.i(1), 1)), rt.construct(1, rt.binary("+", lane, rt.i(1), 1))))
        return rt.binary("-", rt.binary("/", rt.construct(3, v), rt.f(4294967295.0), 3), rt.f(0.5), 3)
    def fsFetchCell__ivec2_float_ivec2(cell, cellSize, texSize):
        cell = rt.copy(cell)
        texSize = rt.copy(texSize)
        pGlobal = rt.binary("*", rt.binary("+", rt.construct(2, cell), rt.f(0.5), 2), cellSize, 2)
        pLocal = rt.binary("-", cpu_ivec2__vec2(rt.component_wise("floor", pGlobal, width=2)), cpu_ivec2__vec2(_u_tileOffset), 2)
        pLocal = rt.component_wise("clamp", pLocal, cpu_ivec2__float(rt.i(0)), rt.binary("-", texSize, rt.i(1), 2), width=2)
        return rt.swizzle(rt.texel_fetch(_u_inputTex, pLocal, rt.i(0)), "rgb")
    def errorDiffusion__vec2_float_ivec2(globalCoord, cellSize, texSize):
        globalCoord = rt.copy(globalCoord)
        texSize = rt.copy(texSize)
        cell = cpu_ivec2__vec2(rt.component_wise("floor", rt.binary("/", globalCoord, cellSize, 2), width=2))
        blockOrigin = rt.binary("*", rt.binary("/", cell, g.FS_BLOCK, 2), g.FS_BLOCK, 2)
        lx = rt.binary("-", rt.swizzle(cell, "x"), rt.swizzle(blockOrigin, "x"), 1)
        ly = rt.binary("-", rt.swizzle(cell, "y"), rt.swizzle(blockOrigin, "y"), 1)
        jitterHash = pcg__vec3(cpu_uvec3__float_float_float(rt.construct(1, rt.binary("+", rt.swizzle(blockOrigin, "x"), rt.i(1), 1)), rt.construct(1, rt.binary("+", rt.swizzle(blockOrigin, "y"), rt.i(1), 1)), rt.i(0x517cc1b7)))
        apronX = rt.binary("+", g.FS_APRON_MIN, rt.construct(1, rt.binary("%", rt.swizzle(jitterHash, "x"), rt.construct(1, rt.binary("+", rt.binary("-", g.FS_APRON_MAX, g.FS_APRON_MIN, 1), rt.i(1), 1)), 1)), 1)
        apronY = rt.binary("+", g.FS_APRON_MIN, rt.construct(1, rt.binary("%", rt.swizzle(jitterHash, "y"), rt.construct(1, rt.binary("+", rt.binary("-", g.FS_APRON_MAX, g.FS_APRON_MIN, 1), rt.i(1), 1)), 1)), 1)
        stepScale = fsScale__void()
        bias = rt.construct(3, rt.binary("*", _u_threshold, stepScale, 1))
        errRow = rt.construct(3, 0.0)
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for3_first = False
            if not (rt.binary("<", i, g.FS_ERR_W)):
                break
            errRow[int(i)] = rt.binary("*", fsSeedNoise__ivec2_int(blockOrigin, i), stepScale, 3)
        carried = rt.construct(3, rt.f(0.0))
        r = rt.unary("-", g.FS_APRON_MAX)
        _for4_first = True
        for _for4 in range(1048576):
            if not _for4_first:
                r = rt.binary("+", r, rt.i(1), 1)
            _for4_first = False
            if not (rt.binary("<=", r, ly)):
                break
            if rt.binary("<", r, rt.unary("-", apronY)):
                continue
            lastRow = rt.binary("==", r, ly)
            rightErr = rt.binary("*", fsSeedNoise__ivec2_int(blockOrigin, rt.binary("+", rt.binary("+", g.FS_ERR_W, g.FS_APRON_MAX, 1), r, 1)), stepScale, 3)
            diag = rt.construct(3, rt.f(0.0))
            c = rt.unary("-", g.FS_APRON_MAX)
            _for5_first = True
            for _for5 in range(1048576):
                if not _for5_first:
                    c = rt.binary("+", c, rt.i(1), 1)
                _for5_first = False
                if not (rt.binary("<", c, rt.binary("+", g.FS_BLOCK, g.FS_RPAD, 1))):
                    break
                if rt.binary("&&", rt.binary(">=", c, rt.unary("-", apronX)), rt.unary("!", rt.binary("&&", lastRow, rt.binary(">=", c, lx)))):
                    src = fsFetchCell__ivec2_float_ivec2(rt.binary("+", blockOrigin, cpu_ivec2__float_float(c, r), 2), cellSize, texSize)
                    v = rt.component_wise("clamp", rt.binary("+", rt.binary("+", rt.binary("+", src, errRow[int(rt.binary("+", rt.binary("+", c, g.FS_APRON_MAX, 1), rt.i(1), 1))], 3), rightErr, 3), bias, 3), rt.f(0.0), rt.f(1.0), width=3)
                    err = rt.binary("-", v, fsQuantize__vec3(v), 3)
                    rightErr = rt.binary("*", err, rt.binary("/", rt.f(7.0), rt.f(16.0), 1), 3)
                    errRow[int(rt.binary("+", c, g.FS_APRON_MAX, 1))] = rt.binary("+", errRow[int(rt.binary("+", c, g.FS_APRON_MAX, 1))], rt.binary("*", err, rt.binary("/", rt.f(3.0), rt.f(16.0), 1), 3), 1)
                    errRow[int(rt.binary("+", rt.binary("+", c, g.FS_APRON_MAX, 1), rt.i(1), 1))] = rt.binary("+", diag, rt.binary("*", err, rt.binary("/", rt.f(5.0), rt.f(16.0), 1), 3), 3)
                    diag = rt.binary("*", err, rt.binary("/", rt.f(1.0), rt.f(16.0), 1), 3)
            if lastRow:
                incoming = errRow[int(rt.binary("+", g.FS_APRON_MAX, rt.i(1), 1))]
                if rt.binary("==", lx, rt.i(1)):
                    incoming = errRow[int(rt.binary("+", g.FS_APRON_MAX, rt.i(2), 1))]
                if rt.binary("==", lx, rt.i(2)):
                    incoming = errRow[int(rt.binary("+", g.FS_APRON_MAX, rt.i(3), 1))]
                if rt.binary("==", lx, rt.i(3)):
                    incoming = errRow[int(rt.binary("+", g.FS_APRON_MAX, rt.i(4), 1))]
                carried = rt.binary("+", incoming, rightErr, 3)
        src = rt.swizzle(rt.texel_fetch(_u_inputTex, cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy")), rt.i(0)), "rgb")
        v = rt.component_wise("clamp", rt.binary("+", rt.binary("+", src, carried, 3), bias, 3), rt.f(0.0), rt.f(1.0), width=3)
        return fsQuantize__vec3(v)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        color = rt.texture(_u_inputTex, uv)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        result = rt.construct(3, 0.0)
        if rt.binary("==", _u_ditherType, g.DITHER_ERROR_DIFFUSION):
            result = errorDiffusion__vec2_float_ivec2(globalCoord, rt.binary("*", _u_matrixScale, _u_renderScale, 1), texSize)
        else:
            ditherValue = getDitherThreshold__vec2_int_float(globalCoord, _u_ditherType, rt.binary("*", _u_matrixScale, _u_renderScale, 1))
            if rt.binary("==", _u_palette, g.PALETTE_INPUT):
                result = quantizeWithDither__vec3_float_float_float(rt.swizzle(color, "rgb"), _u_levels, ditherValue, _u_threshold)
            else:
                result = ditherWithPalette__vec3_float_float_int(rt.swizzle(color, "rgb"), ditherValue, _u_threshold, _u_palette)
        result = rt.component_wise("mix", rt.swizzle(color, "rgb"), result, _u_mixAmount, width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
