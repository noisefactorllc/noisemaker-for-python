def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_smoothness = U["smoothness"]
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        sum = rt.construct(4, rt.f(0.0))
        wsum = rt.f(0.0)
        y = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                w = rt.binary("*", rt.binary("-", rt.f(2.0), rt.component_wise("abs", rt.construct(1, x), width=1), 1, "float"), rt.binary("-", rt.f(2.0), rt.component_wise("abs", rt.construct(1, y), width=1), 1, "float"), 1, "float")
                sum = rt.binary("+", sum, rt.binary("*", rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), texel, 2, "float"), 2, "float")), w, 4, "float"), 4, "float")
                wsum = rt.binary("+", wsum, w, 1, "float")
        blurred = rt.binary("/", sum, wsum, 4, "float")
        g.fragColor = rt.component_wise("mix", src, blurred, rt.component_wise("clamp", rt.binary("/", _u_smoothness, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
