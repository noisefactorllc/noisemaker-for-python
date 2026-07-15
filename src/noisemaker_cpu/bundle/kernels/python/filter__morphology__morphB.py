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
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        acc = rt.texture(_u_inputTex, uv)
        if rt.binary("==", _u_SHAPE, rt.i(0)):
            texel = rt.binary("/", rt.f(1.0), _u_resolution, 2)
            r = rt.component_wise("min", _u_radius, rt.f(32.0), width=1)
            i = rt.i(1)
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    i = rt.binary("+", i, rt.i(1), 1)
                _for0_first = False
                if not (rt.binary("<=", i, rt.i(32))):
                    break
                if rt.binary(">", i, r):
                    break
                o = rt.binary("*", rt.construct(2, rt.f(0.0), i), texel, 2)
                sD = rt.texture(_u_inputTex, rt.binary("-", uv, o, 2))
                sU = rt.texture(_u_inputTex, rt.binary("+", uv, o, 2))
                hi = rt.component_wise("max", acc, rt.component_wise("max", sD, sU, width=4), width=4)
                lo = rt.component_wise("min", acc, rt.component_wise("min", sD, sU, width=4), width=4)
                acc = rt.component_wise("mix", hi, lo, _u_mode, width=4)
        g.fragColor = acc
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
