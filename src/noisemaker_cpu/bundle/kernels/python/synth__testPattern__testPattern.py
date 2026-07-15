def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_gridSize = U["gridSize"]
    _u_pattern = U["pattern"]
    g.GLYPH = rt.array([rt.i(31599), rt.i(9362), rt.i(29671), rt.i(29391), rt.i(23497), rt.i(31183), rt.i(31215), rt.i(29257), rt.i(31727), rt.i(31695)])
    def sampleGlyph__int_int_int(digit, x, y):
        if (bool((bool((bool((bool((bool(rt.binary("<", digit, rt.i(0))) or bool(rt.binary(">", digit, rt.i(9))))) or bool(rt.binary("<", x, rt.i(0))))) or bool(rt.binary(">", x, rt.i(2))))) or bool(rt.binary("<", y, rt.i(0))))) or bool(rt.binary(">", y, rt.i(4)))):
            return False
        bitIndex = rt.binary("+", rt.binary("*", y, rt.i(3), 1, "int"), rt.binary("-", rt.i(2), x, 1, "int"), 1, "int")
        return rt.binary("==", rt.binary("&", rt.binary(">>", g.GLYPH[int(digit)], bitIndex, 1, "int"), rt.i(1), 1, "int"), rt.i(1))
    def renderNumber__int_vec2(number, cellUV):
        cellUV = rt.copy(cellUV)
        numDigits = rt.i(1)
        if rt.binary(">=", number, rt.i(10)):
            numDigits = rt.i(2)
        if rt.binary(">=", number, rt.i(100)):
            numDigits = rt.i(3)
        glyphWidth = rt.f(0.15)
        glyphHeight = rt.f(0.35)
        spacing = rt.f(0.05)
        totalWidth = rt.binary("+", rt.binary("*", rt.construct(1, numDigits), glyphWidth, 1, "float"), rt.binary("*", rt.construct(1, rt.binary("-", numDigits, rt.i(1), 1, "int")), spacing, 1, "float"), 1, "float")
        startX = rt.binary("-", rt.f(0.5), rt.binary("*", totalWidth, rt.f(0.5), 1, "float"), 1, "float")
        startY = rt.binary("-", rt.f(0.5), rt.binary("*", glyphHeight, rt.f(0.5), 1, "float"), 1, "float")
        if (bool(rt.binary("<", rt.swizzle(cellUV, "y"), startY)) or bool(rt.binary(">=", rt.swizzle(cellUV, "y"), rt.binary("+", startY, glyphHeight, 1, "float")))):
            return False
        digits = rt.new_array(rt.i(3), 1)
        temp = number
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            digits[int(i)] = rt.binary("%", temp, rt.i(10), 1, "int")
            temp = rt.binary("/", temp, rt.i(10), 1, "int")
        d = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                d = rt.binary("+", d, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", d, numDigits)):
                break
            digitX = rt.binary("+", startX, rt.binary("*", rt.construct(1, d), rt.binary("+", glyphWidth, spacing, 1, "float"), 1, "float"), 1, "float")
            if (bool(rt.binary(">=", rt.swizzle(cellUV, "x"), digitX)) and bool(rt.binary("<", rt.swizzle(cellUV, "x"), rt.binary("+", digitX, glyphWidth, 1, "float")))):
                localX = rt.binary("/", rt.binary("-", rt.swizzle(cellUV, "x"), digitX, 1, "float"), glyphWidth, 1, "float")
                localY = rt.binary("/", rt.binary("-", rt.swizzle(cellUV, "y"), startY, 1, "float"), glyphHeight, 1, "float")
                gx = rt.construct(1, rt.binary("*", localX, rt.f(3.0), 1, "float"), base="int")
                gy = rt.construct(1, rt.binary("*", localY, rt.f(5.0), 1, "float"), base="int")
                digit = digits[int(rt.binary("-", rt.binary("-", numDigits, rt.i(1), 1, "int"), d, 1, "int"))]
                return sampleGlyph__int_int_int(digit, gx, gy)
        return False
    def checkerboard__vec2(uv):
        uv = rt.copy(uv)
        n = rt.component_wise("max", _u_gridSize, rt.i(1), width=1)
        cellX = rt.binary("%", rt.construct(1, rt.binary("*", rt.swizzle(uv, "x"), rt.construct(1, n), 1, "float"), base="int"), n, 1, "int")
        cellY = rt.binary("%", rt.construct(1, rt.binary("*", rt.swizzle(uv, "y"), rt.construct(1, n), 1, "float"), base="int"), n, 1, "int")
        cellNum = rt.binary("+", rt.binary("*", rt.binary("-", rt.binary("-", n, rt.i(1), 1, "int"), cellY, 1, "int"), n, 1, "int"), cellX, 1, "int")
        isWhiteCell = rt.binary("==", rt.binary("%", rt.binary("+", cellX, cellY, 1, "int"), rt.i(2), 1, "int"), rt.i(0))
        cellUV = rt.component_wise("fract", rt.binary("*", uv, rt.construct(1, n), 2, "float"), width=2)
        isGlyph = renderNumber__int_vec2(cellNum, cellUV)
        cellColor = (rt.f(1.0) if isWhiteCell else rt.f(0.0))
        glyphColor = (rt.f(0.0) if isWhiteCell else rt.f(1.0))
        finalColor = (glyphColor if isGlyph else cellColor)
        return rt.construct(4, rt.construct(3, finalColor), rt.f(1.0))
    def colorBars__vec2(uv):
        uv = rt.copy(uv)
        bar = rt.construct(1, rt.binary("*", rt.swizzle(uv, "x"), rt.f(8.0), 1, "float"), base="int")
        bar = rt.component_wise("clamp", bar, rt.i(0), rt.i(7), width=1)
        colors = rt.array([rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(1.0)), rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(0.0)), rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(1.0)), rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(1.0)), rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(0.0)), rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0)), rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))])
        return rt.construct(4, colors[int(bar)], rt.f(1.0))
    def gradient__vec2(uv):
        uv = rt.copy(uv)
        return rt.construct(4, rt.construct(3, rt.swizzle(uv, "x")), rt.f(1.0))
    def uvMap__vec2(uv):
        uv = rt.copy(uv)
        return rt.construct(4, rt.swizzle(uv, "x"), rt.swizzle(uv, "y"), rt.f(0.0), rt.f(1.0))
    def gridLines__vec2(uv):
        uv = rt.copy(uv)
        n = rt.component_wise("max", _u_gridSize, rt.i(1), width=1)
        cellUV = rt.component_wise("fract", rt.binary("*", uv, rt.construct(1, n), 2, "float"), width=2)
        edge = rt.component_wise("min", cellUV, rt.binary("-", rt.f(1.0), cellUV, 2, "float"), width=2)
        fw = rt.binary("*", rt.binary("/", rt.construct(2, rt.f(1.0)), _u_fullResolution, 2, "float"), rt.construct(1, n), 2, "float")
        line = rt.binary("-", rt.f(1.0), rt.binary("*", rt.component_wise("smoothstep", rt.f(0.0), rt.binary("*", rt.f(2.0), rt.swizzle(fw, "x"), 1, "float"), rt.swizzle(edge, "x"), width=1), rt.component_wise("smoothstep", rt.f(0.0), rt.binary("*", rt.f(2.0), rt.swizzle(fw, "y"), 1, "float"), rt.swizzle(edge, "y"), width=1), 1, "float"), 1, "float")
        return rt.construct(4, rt.construct(3, line), rt.f(1.0))
    def hue2rgb__float(h):
        r = rt.binary("-", rt.component_wise("abs", rt.binary("-", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(3.0), 1, "float"), width=1), rt.f(1.0), 1, "float")
        g = rt.binary("-", rt.f(2.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), 1, "float"), width=1), 1, "float")
        b = rt.binary("-", rt.f(2.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(4.0), 1, "float"), width=1), 1, "float")
        return rt.component_wise("clamp", rt.construct(3, r, g, b), rt.f(0.0), rt.f(1.0), width=3)
    def colorGrid__vec2(uv):
        uv = rt.copy(uv)
        n = rt.component_wise("max", _u_gridSize, rt.i(1), width=1)
        cellX = rt.binary("%", rt.construct(1, rt.binary("*", rt.swizzle(uv, "x"), rt.construct(1, n), 1, "float"), base="int"), n, 1, "int")
        cellY = rt.binary("%", rt.construct(1, rt.binary("*", rt.swizzle(uv, "y"), rt.construct(1, n), 1, "float"), base="int"), n, 1, "int")
        cellIndex = rt.binary("+", rt.binary("*", cellY, n, 1, "int"), cellX, 1, "int")
        hue = rt.component_wise("fract", rt.binary("*", rt.construct(1, cellIndex), rt.f(0.618033988749895), 1, "float"), width=1)
        return rt.construct(4, hue2rgb__float(hue), rt.f(1.0))
    def dotGrid__vec2(uv):
        uv = rt.copy(uv)
        n = rt.component_wise("max", _u_gridSize, rt.i(1), width=1)
        scaled = rt.binary("*", uv, rt.construct(1, n), 2, "float")
        nearest = rt.component_wise("round", scaled, width=2)
        dist = rt.length(rt.binary("-", scaled, nearest, 2, "float"))
        dot = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.12), rt.f(0.15), dist, width=1), 1, "float")
        return rt.construct(4, rt.construct(3, dot), rt.f(1.0))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        if rt.binary("==", _u_pattern, rt.i(1)):
            g.fragColor = colorBars__vec2(uv)
        else:
            if rt.binary("==", _u_pattern, rt.i(2)):
                g.fragColor = gradient__vec2(uv)
            else:
                if rt.binary("==", _u_pattern, rt.i(3)):
                    g.fragColor = uvMap__vec2(uv)
                else:
                    if rt.binary("==", _u_pattern, rt.i(4)):
                        g.fragColor = gridLines__vec2(uv)
                    else:
                        if rt.binary("==", _u_pattern, rt.i(5)):
                            g.fragColor = colorGrid__vec2(uv)
                        else:
                            if rt.binary("==", _u_pattern, rt.i(6)):
                                g.fragColor = dotGrid__vec2(uv)
                            else:
                                g.fragColor = checkerboard__vec2(uv)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
