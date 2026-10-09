def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_deltaTime = U.get("deltaTime", rt.f(0.0))
    _u_lineColor = U.get("lineColor", rt.construct(3, 0.0))
    _u_gain = U.get("gain", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_midiClockCount = U.get("midiClockCount", rt.f(0.0))
    _u_feedbackTex = T["feedbackTex"]
    _u_noteGridTex = T["noteGridTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        uv = rt.construct(2, rt.binary("/", globalCoord, _u_fullResolution, 2, 'float'))
        scrollAmount = rt.binary("*", rt.binary("*", _u_speed, _u_deltaTime, 1, "float"), rt.f(0.5), 1, "float")
        scrollUv = rt.construct(2, rt.binary("-", rt.swizzle(uv, "x"), scrollAmount, 1, "float"), rt.swizzle(uv, "y"))
        prev = rt.construct(4, rt.f(0.0))
        if rt.binary(">=", rt.swizzle(scrollUv, "x"), rt.f(0.0)):
            prev[:] = rt.texture(_u_feedbackTex, scrollUv)
            prev[:] = rt.binary("*", prev, rt.f(0.997), 4, "float")
        laneF = rt.binary("*", rt.swizzle(uv, "y"), rt.f(16.0), 1, "float")
        channel = rt.construct(1, rt.component_wise("floor", laneF, width=1), base="int")
        laneLocal = rt.component_wise("fract", laneF, width=1)
        keyLow = rt.i(36)
        keyRange = rt.i(48)
        keyExact = rt.binary("+", rt.construct(1, keyLow), rt.binary("*", laneLocal, rt.construct(1, keyRange), 1, "float"), 1, "float")
        key = rt.construct(1, rt.component_wise("floor", keyExact, width=1), base="int")
        keyFrac = rt.component_wise("fract", keyExact, width=1)
        maxVel = rt.f(0.0)
        lanePixels = rt.binary("/", rt.swizzle(_u_fullResolution, "y"), rt.f(16.0), 1, "float")
        keysPerPixel = rt.binary("/", rt.construct(1, keyRange), lanePixels, 1, "float")
        spread = rt.component_wise("max", rt.i(1), rt.construct(1, rt.component_wise("ceil", keysPerPixel, width=1), base="int"), width=1)
        dk = rt.unary("-", spread)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dk = rt.binary("+", dk, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dk, spread)):
                break
            k = rt.component_wise("clamp", rt.binary("+", key, dk, 1, "int"), rt.i(0), rt.i(127), width=1)
            gridUv = rt.construct(2, rt.binary("/", rt.binary("+", rt.construct(1, k), rt.f(0.5), 1, "float"), rt.f(128.0), 1, "float"), rt.binary("/", rt.binary("+", rt.construct(1, channel), rt.f(0.5), 1, "float"), rt.f(16.0), 1, "float"))
            noteData = rt.texture(_u_noteGridTex, gridUv)
            if rt.binary(">", rt.swizzle(noteData, "g"), rt.f(0.5)):
                maxVel = rt.component_wise("max", maxVel, rt.swizzle(noteData, "r"), width=1)
        edgeWidth = rt.binary("/", rt.f(4.0), rt.swizzle(_u_fullResolution, "x"), 1, "float")
        noteVal = rt.f(0.0)
        if (bool(rt.binary("<", rt.swizzle(uv, "x"), edgeWidth)) and bool(rt.binary(">", maxVel, rt.f(0.0)))):
            noteVal = rt.binary("*", maxVel, _u_gain, 1, "float")
        laneSep = rt.f(0.0)
        laneEdge = rt.component_wise("fract", rt.binary("*", rt.swizzle(uv, "y"), rt.f(16.0), 1, "float"), width=1)
        if (bool(rt.binary("<", laneEdge, rt.f(0.02))) or bool(rt.binary(">", laneEdge, rt.f(0.98)))):
            laneSep = rt.f(0.2)
        prevBright = rt.component_wise("max", rt.swizzle(prev, "r"), rt.component_wise("max", rt.swizzle(prev, "g"), rt.swizzle(prev, "b"), width=1), width=1)
        brightness = rt.component_wise("max", prevBright, rt.component_wise("max", noteVal, laneSep, width=1), width=1)
        col = rt.construct(3, rt.binary("*", _u_lineColor, brightness, 3, 'float'))
        g.fragColor[:] = rt.construct(4, col, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
