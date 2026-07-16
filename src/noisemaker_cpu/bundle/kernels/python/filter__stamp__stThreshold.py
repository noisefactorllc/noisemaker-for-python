def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blurTex = T["blurTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_balance = U["balance"]
    _u_roughness = U["roughness"]
    _u_inkColor = U["inkColor"]
    _u_paperColor = U["paperColor"]
    g.fragColor = rt.construct(4, 0.0)
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def vnoise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbm__vec2(p):
        p = rt.copy(p)
        v = rt.f(0.0)
        a = rt.f(0.5)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(5))):
                break
            v = rt.binary("+", v, rt.binary("*", a, vnoise__vec2(p), 1, "float"), 1, "float")
            p = rt.binary("*", p, rt.f(2.03), 2, "float")
            a = rt.binary("*", a, rt.f(0.5), 1, "float")
        return v
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink)
        paper = rt.copy(paper)
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        blur = rt.texture(_u_blurTex, uv)
        globalCoord = rt.binary("+", rt.component_wise("floor", rt.swizzle(ctx.frag_coord, "xy"), width=2), _u_tileOffset, 2, "float")
        lumBlur = lum__vec3(rt.swizzle(blur, "rgb"))
        grain = rt.binary("*", rt.binary("*", rt.binary("-", fbm__vec2(rt.binary("/", globalCoord, rt.f(3.0), 2, "float")), rt.f(0.5), 1, "float"), rt.binary("/", _u_roughness, rt.f(100.0), 1, "float"), 1, "float"), rt.f(0.35), 1, "float")
        t = rt.binary("+", lumBlur, grain, 1, "float")
        b = rt.binary("/", _u_balance, rt.f(100.0), 1, "float")
        aa = rt.binary("+", rt.component_wise("max", rt.fwidth(t), rt.f(0.01), width=1), rt.binary("*", rt.binary("/", _u_roughness, rt.f(100.0), 1, "float"), rt.f(0.05), 1, "float"), 1, "float")
        m = rt.component_wise("smoothstep", rt.binary("-", b, aa, 1, "float"), rt.binary("+", b, aa, 1, "float"), t, width=1)
        outColor = tonemap2__float_vec3_vec3(m, _u_inkColor, _u_paperColor)
        g.fragColor = rt.construct(4, outColor, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
