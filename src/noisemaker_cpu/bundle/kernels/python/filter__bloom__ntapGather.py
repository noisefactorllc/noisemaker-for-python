def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_radius = U["radius"]
    _u_renderScale = U["renderScale"]
    _u_taps = U["taps"]
    g.MAX_TAPS = rt.i(64)
    g.GOLDEN_ANGLE = rt.f(2.39996323)
    g.PI = rt.f(3.14159265359)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2)
        texelSize = rt.binary("/", rt.f(1.0), texSize, 2)
        radiusUV = rt.binary("*", rt.binary("*", _u_radius, _u_renderScale, 1), texelSize, 2)
        tapCount = rt.component_wise("clamp", _u_taps, rt.i(1), g.MAX_TAPS, width=1)
        bloomAccum = rt.construct(3, rt.f(0.0))
        weightSum = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, g.MAX_TAPS)):
                break
            if rt.binary(">=", i, tapCount):
                break
            t = rt.binary("/", i, tapCount, 1)
            r = rt.component_wise("sqrt", t, width=1)
            theta = rt.binary("*", i, g.GOLDEN_ANGLE, 1)
            offset = rt.binary("*", rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), r, 2)
            sigma = rt.f(0.4)
            weight = rt.component_wise("exp", rt.binary("/", rt.binary("*", rt.unary("-", rt.f(0.5)), rt.binary("*", r, r, 1), 1), rt.binary("*", sigma, sigma, 1), 1), width=1)
            sampleUV = rt.component_wise("clamp", rt.binary("+", uv, rt.binary("*", offset, radiusUV, 2), 2), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.f(1.0)), width=2)
            sampleColor = rt.swizzle(rt.texture(_u_inputTex, sampleUV), "rgb")
            bloomAccum = rt.binary("+", bloomAccum, rt.binary("*", sampleColor, weight, 3), 3)
            weightSum = rt.binary("+", weightSum, weight, 1)
        if rt.binary(">", weightSum, rt.f(0.0)):
            bloomAccum = rt.binary("/", bloomAccum, weightSum, 3)
        g.fragColor = rt.construct(4, bloomAccum, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
