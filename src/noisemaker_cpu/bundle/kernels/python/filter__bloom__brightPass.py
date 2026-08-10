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
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_softKnee = U.get("softKnee", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        luma = rt.dot(rt.swizzle(color, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        knee = _u_softKnee
        threshLow = rt.binary("-", _u_threshold, knee, 1, "float")
        threshHigh = rt.binary("+", _u_threshold, knee, 1, "float")
        bloomFactor = rt.f(0.0)
        t = rt.f(0.0)
        if rt.binary("<=", luma, threshLow):
            bloomFactor = rt.f(0.0)
        else:
            if rt.binary(">=", luma, threshHigh):
                bloomFactor = rt.f(1.0)
            else:
                t = rt.binary("/", rt.binary("-", luma, threshLow, 1, "float"), rt.binary("-", threshHigh, threshLow, 1, "float"), 1, "float")
                bloomFactor = rt.binary("*", rt.binary("*", t, t, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), 1, "float")
        brightColor = rt.binary("*", rt.swizzle(color, "rgb"), bloomFactor, 3, "float")
        g.fragColor[:] = rt.construct(4, brightColor, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
