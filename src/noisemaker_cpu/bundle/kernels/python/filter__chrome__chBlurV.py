def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_smoothness = U.get("smoothness", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        dirPx = rt.construct(2, rt.f(0.0), rt.f(1.0))
        radius = rt.component_wise("mix", rt.f(1.0), rt.f(16.0), rt.binary("/", _u_smoothness, rt.f(100.0), 1, "float"), width=1)
        sigma = rt.component_wise("max", rt.binary("*", radius, rt.f(0.5), 1, "float"), rt.f(0.001), width=1)
        fTaps = rt.component_wise("min", radius, rt.f(32.0), width=1)
        sum = rt.texture(_u_inputTex, uv)
        wsum = rt.f(1.0)
        i = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", i, rt.i(32))):
                break
            if rt.binary(">", rt.construct(1, i), fTaps):
                break
            w = rt.component_wise("exp", rt.binary("/", rt.unary("-", rt.construct(1, rt.binary("*", i, i, 1, "int"))), rt.binary("*", rt.binary("*", rt.f(2.0), sigma, 1, "float"), sigma, 1, "float"), 1, "float"), width=1)
            o = rt.binary("/", rt.binary("*", dirPx, rt.construct(1, i), 2, "float"), _u_resolution, 2, "float")
            sum[:] = rt.binary("+", sum, rt.binary("*", rt.binary("+", rt.texture(_u_inputTex, rt.binary("+", uv, o, 2, "float")), rt.texture(_u_inputTex, rt.binary("-", uv, o, 2, "float")), 4, "float"), w, 4, "float"), 4, "float")
            wsum = rt.binary("+", wsum, rt.binary("*", rt.f(2.0), w, 1, "float"), 1, "float")
        g.fragColor[:] = rt.binary("/", sum, wsum, 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
