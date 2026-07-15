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
    _u_targetColor = U["targetColor"]
    _u_replaceColor = U["replaceColor"]
    _u_sensitivity = U["sensitivity"]
    _u_smoothing = U["smoothing"]
    _u_colorMix = U["colorMix"]
    _u_replaceAlpha = U["replaceAlpha"]
    _u_keepAlpha = U["keepAlpha"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.component_wise("max", rt.texture_size(_u_inputTex), cpu_ivec2__float(rt.i(1)), width=2)), 2)
        src = rt.texture(_u_inputTex, st)
        dist = rt.binary("/", rt.length(rt.binary("-", rt.swizzle(src, "rgb"), _u_targetColor, 3)), rt.f(1.7320508), 1)
        halfBand = rt.binary("*", _u_smoothing, rt.f(0.5), 1)
        edge0 = rt.component_wise("max", rt.binary("-", _u_sensitivity, halfBand, 1), rt.f(0.0), width=1)
        edge1 = rt.binary("+", _u_sensitivity, halfBand, 1)
        match = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", edge0, edge1, dist, width=1), 1)
        outRgb = rt.component_wise("mix", rt.swizzle(src, "rgb"), _u_replaceColor, rt.binary("*", match, _u_colorMix, 1), width=3)
        outA = rt.binary("*", rt.swizzle(src, "a"), rt.component_wise("mix", _u_keepAlpha, _u_replaceAlpha, match, width=1), 1)
        g.fragColor = rt.construct(4, outRgb, outA)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
