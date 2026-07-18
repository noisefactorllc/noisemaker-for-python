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
    _u_targetColor = U.get("targetColor", rt.construct(3, 0.0))
    _u_replaceColor = U.get("replaceColor", rt.construct(3, 0.0))
    _u_sensitivity = U.get("sensitivity", rt.f(0.0))
    _u_smoothing = U.get("smoothing", rt.f(0.0))
    _u_colorMix = U.get("colorMix", rt.f(0.0))
    _u_replaceAlpha = U.get("replaceAlpha", rt.f(0.0))
    _u_keepAlpha = U.get("keepAlpha", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.component_wise("max", rt.texture_size(_u_inputTex), rt.construct(2, rt.i(1), base="int"), width=2)), 2, "float")
        src = rt.texture(_u_inputTex, st)
        dist = rt.binary("/", rt.length(rt.binary("-", rt.swizzle(src, "rgb"), _u_targetColor, 3, "float")), rt.f(1.7320508), 1, "float")
        halfBand = rt.binary("*", _u_smoothing, rt.f(0.5), 1, "float")
        edge0 = rt.component_wise("max", rt.binary("-", _u_sensitivity, halfBand, 1, "float"), rt.f(0.0), width=1)
        edge1 = rt.binary("+", _u_sensitivity, halfBand, 1, "float")
        match = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", edge0, edge1, dist, width=1), 1, "float")
        outRgb = rt.component_wise("mix", rt.swizzle(src, "rgb"), _u_replaceColor, rt.binary("*", match, _u_colorMix, 1, "float"), width=3)
        outA = rt.binary("*", rt.swizzle(src, "a"), rt.component_wise("mix", _u_keepAlpha, _u_replaceAlpha, match, width=1), 1, "float")
        g.fragColor[:] = rt.construct(4, outRgb, outA)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
