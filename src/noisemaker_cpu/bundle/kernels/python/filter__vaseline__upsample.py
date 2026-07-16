def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_renderScale = U["renderScale"]
    _u_alpha = U["alpha"]
    g.fragColor = rt.construct(4, 0.0)
    g.TAP_COUNT = rt.i(32)
    g.RADIUS = rt.f(48.0)
    g.GOLDEN_ANGLE = rt.f(2.39996323)
    g.BRIGHTNESS_ADJUST = rt.f(0.15)
    def clamp01__vec3(v):
        v = rt.copy(v)
        return rt.component_wise("clamp", v, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
    def chebyshev_mask__vec2(uv):
        uv = rt.copy(uv)
        centered = rt.binary("*", rt.component_wise("abs", rt.binary("-", uv, rt.construct(2, rt.f(0.5)), 2, "float"), width=2), rt.f(2.0), 2, "float")
        return rt.component_wise("max", rt.swizzle(centered, "x"), rt.swizzle(centered, "y"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        original = rt.texel_fetch(_u_inputTex, rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int"), rt.i(0))
        a = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", a, rt.f(0.0)):
            g.fragColor = rt.construct(4, clamp01__vec3(rt.swizzle(original, "rgb")), rt.swizzle(original, "a"))
            return
        texelSize = rt.binary("/", rt.f(1.0), _u_fullResolution, 2, "float")
        radiusUV = rt.binary("*", rt.binary("*", g.RADIUS, _u_renderScale, 1, "float"), texelSize, 2, "float")
        blurAccum = rt.construct(3, rt.f(0.0))
        weightSum = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.TAP_COUNT)):
                break
            t = rt.binary("/", rt.construct(1, i), rt.construct(1, g.TAP_COUNT), 1, "float")
            r = rt.component_wise("sqrt", t, width=1)
            theta = rt.binary("*", rt.construct(1, i), g.GOLDEN_ANGLE, 1, "float")
            offset = rt.binary("*", rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), r, 2, "float")
            sigma = rt.f(0.4)
            weight = rt.component_wise("exp", rt.binary("/", rt.binary("*", rt.unary("-", rt.f(0.5)), rt.binary("*", r, r, 1, "float"), 1, "float"), rt.binary("*", sigma, sigma, 1, "float"), 1, "float"), width=1)
            sampleGlobalUV = rt.component_wise("clamp", rt.binary("+", uv, rt.binary("*", offset, radiusUV, 2, "float"), 2, "float"), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.f(1.0)), width=2)
            sampleLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", sampleGlobalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
            blurAccum = rt.binary("+", blurAccum, rt.binary("*", rt.swizzle(rt.texture(_u_inputTex, sampleLocalUV), "rgb"), weight, 3, "float"), 3, "float")
            weightSum = rt.binary("+", weightSum, weight, 1, "float")
        blurred = rt.binary("/", blurAccum, weightSum, 3, "float")
        boosted = clamp01__vec3(rt.binary("+", blurred, rt.construct(3, g.BRIGHTNESS_ADJUST), 3, "float"))
        edgeMask = chebyshev_mask__vec2(globalUV)
        edgeMask = rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.8), edgeMask, width=1)
        sourceClamped = clamp01__vec3(rt.swizzle(original, "rgb"))
        bloomed = clamp01__vec3(rt.binary("*", rt.binary("+", sourceClamped, boosted, 3, "float"), rt.f(0.5), 3, "float"))
        edgeBlended = rt.component_wise("mix", sourceClamped, bloomed, edgeMask, width=3)
        finalRgb = clamp01__vec3(rt.component_wise("mix", sourceClamped, edgeBlended, a, width=3))
        g.fragColor = rt.construct(4, finalRgb, rt.swizzle(original, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
