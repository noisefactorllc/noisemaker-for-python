def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_radius = U.get("radius", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_taps = U.get("taps", 0)
    g.fragColor = rt.construct(4, 0.0)
    g.MAX_TAPS = rt.i(64)
    g.GOLDEN_ANGLE = rt.f(2.39996323)
    g.PI = rt.f(3.14159265359)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), texSize, 2, "float")
        radiusUV = rt.binary("*", rt.binary("*", _u_radius, _u_renderScale, 1, "float"), texelSize, 2, "float")
        tapCount = rt.component_wise("clamp", _u_taps, rt.i(1), g.MAX_TAPS, width=1)
        bloomAccum = rt.construct(3, rt.f(0.0))
        weightSum = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.MAX_TAPS)):
                break
            if rt.binary(">=", i, tapCount):
                break
            t = rt.binary("/", rt.construct(1, i), rt.construct(1, tapCount), 1, "float")
            r = rt.component_wise("sqrt", t, width=1)
            theta = rt.binary("*", rt.construct(1, i), g.GOLDEN_ANGLE, 1, "float")
            offset = rt.binary("*", rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), r, 2, "float")
            sigma = rt.f(0.4)
            weight = rt.component_wise("exp", rt.binary("/", rt.binary("*", rt.unary("-", rt.f(0.5)), rt.binary("*", r, r, 1, "float"), 1, "float"), rt.binary("*", sigma, sigma, 1, "float"), 1, "float"), width=1)
            sampleUV = rt.component_wise("clamp", rt.binary("+", uv, rt.binary("*", offset, radiusUV, 2, "float"), 2, "float"), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.f(1.0)), width=2)
            sampleColor = rt.swizzle(rt.texture(_u_inputTex, sampleUV), "rgb")
            bloomAccum = rt.binary("+", bloomAccum, rt.binary("*", sampleColor, weight, 3, "float"), 3, "float")
            weightSum = rt.binary("+", weightSum, weight, 1, "float")
        if rt.binary(">", weightSum, rt.f(0.0)):
            bloomAccum = rt.binary("/", bloomAccum, weightSum, 3, "float")
        g.fragColor = rt.construct(4, bloomAccum, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
