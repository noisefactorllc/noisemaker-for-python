def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_simplifiedTex = T["simplifiedTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_shadowIntensity = U.get("shadowIntensity", rt.f(0.0))
    _u_paperTexture = U.get("paperTexture", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def vnoise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradientSimplified__vec2(uv):
        uv = rt.copy(uv, "float")
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        tl = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1, "float"), 1, "float"), br, 1, "float"), tl, 1, "float"), rt.binary("*", rt.f(2.0), l, 1, "float"), 1, "float"), bl, 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), b, 1, "float"), 1, "float"), br, 1, "float"))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        simplified = rt.swizzle(rt.texture(_u_simplifiedTex, uv), "rgb")
        edge = rt.length(lumGradientSimplified__vec2(uv))
        pool = rt.binary("*", rt.binary("*", rt.binary("/", _u_shadowIntensity, rt.f(100.0), 1, "float"), rt.f(0.7), 1, "float"), rt.component_wise("smoothstep", rt.f(0.05), rt.f(0.4), edge, width=1), 1, "float")
        c = rt.binary("*", simplified, rt.binary("-", rt.f(1.0), pool, 1, "float"), 3, "float")
        gc = rt.binary("+", rt.component_wise("floor", rt.swizzle(ctx.frag_coord, "xy"), width=2), _u_tileOffset, 2, "float")
        c[:] = rt.binary("*", c, rt.component_wise("mix", rt.f(1.0), rt.binary("+", rt.f(0.92), rt.binary("*", rt.f(0.08), vnoise__vec2(rt.binary("/", gc, rt.f(3.5), 2, "float")), 1, "float"), 1, "float"), rt.binary("/", rt.component_wise("clamp", _u_paperTexture, rt.f(0.0), rt.f(100.0), width=1), rt.f(100.0), 1, "float"), width=1), 3, "float")
        c[:] = rt.component_wise("mix", c, rt.binary("*", c, rt.construct(3, rt.f(1.02), rt.f(1.0), rt.f(0.95)), 3, "float"), rt.binary("/", _u_paperTexture, rt.f(100.0), 1, "float"), width=3)
        flatness = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.15), edge, width=1), 1, "float")
        c[:] = rt.component_wise("mix", c, rt.construct(3, lum__vec3(c)), rt.binary("*", flatness, rt.f(0.12), 1, "float"), width=3)
        c[:] = rt.binary("*", c, rt.binary("+", rt.f(1.0), rt.binary("*", flatness, rt.f(0.05), 1, "float"), 1, "float"), 3, "float")
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", c, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
