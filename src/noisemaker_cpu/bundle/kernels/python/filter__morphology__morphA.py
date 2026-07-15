def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_SHAPE = U["SHAPE"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_mode = U["mode"]
    _u_radius = U["radius"]
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        acc = rt.texture(_u_inputTex, uv)
        if rt.binary("==", _u_SHAPE, rt.i(1)):
            r = rt.component_wise("min", _u_radius, rt.f(12.0), width=1)
            r2 = rt.binary("*", r, r, 1, "float")
            y = rt.unary("-", rt.i(12))
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    y = rt.binary("+", y, rt.i(1), 1, "int")
                _for0_first = False
                if not (rt.binary("<=", y, rt.i(12))):
                    break
                x = rt.unary("-", rt.i(12))
                _for1_first = True
                for _for1 in range(1048576):
                    if not _for1_first:
                        x = rt.binary("+", x, rt.i(1), 1, "int")
                    _for1_first = False
                    if not (rt.binary("<=", x, rt.i(12))):
                        break
                    if (bool(rt.binary("==", x, rt.i(0))) and bool(rt.binary("==", y, rt.i(0)))):
                        continue
                    d = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                    if rt.binary(">", rt.dot(d, d), r2):
                        continue
                    s = rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", d, texel, 2, "float"), 2, "float"))
                    hi = rt.component_wise("max", acc, s, width=4)
                    lo = rt.component_wise("min", acc, s, width=4)
                    acc = rt.component_wise("mix", hi, lo, rt.construct(1, _u_mode), width=4)
        else:
            r = rt.component_wise("min", _u_radius, rt.f(32.0), width=1)
            i = rt.i(1)
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    i = rt.binary("+", i, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<=", i, rt.i(32))):
                    break
                if rt.binary(">", rt.construct(1, i), r):
                    break
                o = rt.binary("*", rt.construct(2, rt.construct(1, i), rt.f(0.0)), texel, 2, "float")
                sL = rt.texture(_u_inputTex, rt.binary("-", uv, o, 2, "float"))
                sR = rt.texture(_u_inputTex, rt.binary("+", uv, o, 2, "float"))
                hi = rt.component_wise("max", acc, rt.component_wise("max", sL, sR, width=4), width=4)
                lo = rt.component_wise("min", acc, rt.component_wise("min", sL, sR, width=4), width=4)
                acc = rt.component_wise("mix", hi, lo, rt.construct(1, _u_mode), width=4)
        g.fragColor = acc
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
