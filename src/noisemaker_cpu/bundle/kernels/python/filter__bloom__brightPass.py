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
    _u_threshold = U["threshold"]
    _u_softKnee = U["softKnee"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        luma = rt.dot(rt.swizzle(color, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        knee = _u_softKnee
        threshLow = rt.binary("-", _u_threshold, knee, 1)
        threshHigh = rt.binary("+", _u_threshold, knee, 1)
        bloomFactor = rt.f(0.0)
        if rt.binary("<=", luma, threshLow):
            bloomFactor = rt.f(0.0)
        else:
            if rt.binary(">=", luma, threshHigh):
                bloomFactor = rt.f(1.0)
            else:
                t = rt.binary("/", rt.binary("-", luma, threshLow, 1), rt.binary("-", threshHigh, threshLow, 1), 1)
                bloomFactor = rt.binary("*", rt.binary("*", t, t, 1), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1), 1), 1)
        brightColor = rt.binary("*", rt.swizzle(color, "rgb"), bloomFactor, 3)
        g.fragColor = rt.construct(4, brightColor, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
