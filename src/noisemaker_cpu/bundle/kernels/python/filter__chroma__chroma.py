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
    _u_targetHue = U.get("targetHue", rt.f(0.0))
    _u_range = U.get("range", rt.f(0.0))
    _u_feather = U.get("feather", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def rgb2hsv__vec3(c):
        c = rt.copy(c, "float")
        K = rt.construct(4, rt.f(0.0), rt.binary("/", rt.unary("-", rt.f(1.0)), rt.f(3.0), 1, "float"), rt.binary("/", rt.f(2.0), rt.f(3.0), 1, "float"), rt.unary("-", rt.f(1.0)))
        p = rt.component_wise("mix", rt.construct(4, rt.swizzle(c, "bg"), rt.swizzle(K, "wz")), rt.construct(4, rt.swizzle(c, "gb"), rt.swizzle(K, "xy")), rt.component_wise("step", rt.swizzle(c, "b"), rt.swizzle(c, "g"), width=1), width=4)
        q = rt.component_wise("mix", rt.construct(4, rt.swizzle(p, "xyw"), rt.swizzle(c, "r")), rt.construct(4, rt.swizzle(c, "r"), rt.swizzle(p, "yzx")), rt.component_wise("step", rt.swizzle(p, "x"), rt.swizzle(c, "r"), width=1), width=4)
        d = rt.binary("-", rt.swizzle(q, "x"), rt.component_wise("min", rt.swizzle(q, "w"), rt.swizzle(q, "y"), width=1), 1, "float")
        e = rt.f(1e-10)
        return rt.construct(3, rt.component_wise("abs", rt.binary("+", rt.swizzle(q, "z"), rt.binary("/", rt.binary("-", rt.swizzle(q, "w"), rt.swizzle(q, "y"), 1, "float"), rt.binary("+", rt.binary("*", rt.f(6.0), d, 1, "float"), e, 1, "float"), 1, "float"), 1, "float"), width=1), rt.binary("/", d, rt.binary("+", rt.swizzle(q, "x"), e, 1, "float"), 1, "float"), rt.swizzle(q, "x"))
    def hueDistance__float_float(h1, h2):
        d = rt.component_wise("abs", rt.binary("-", h1, h2, 1, "float"), width=1)
        return rt.component_wise("min", d, rt.binary("-", rt.f(1.0), d, 1, "float"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        color = rt.texture(_u_inputTex, uv)
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hue = rt.swizzle(hsv, "x")
        sat = rt.swizzle(hsv, "y")
        dist = hueDistance__float_float(hue, _u_targetHue)
        inner = _u_range
        outer = rt.binary("+", _u_range, _u_feather, 1, "float")
        mask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", inner, outer, dist, width=1), 1, "float")
        mask = rt.binary("*", mask, sat, 1, "float")
        g.fragColor[:] = rt.construct(4, rt.construct(3, mask), rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
