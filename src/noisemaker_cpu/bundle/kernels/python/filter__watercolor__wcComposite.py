def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_simplifiedTex = T["simplifiedTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_shadowIntensity = U["shadowIntensity"]
    _u_paperTexture = U["paperTexture"]
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3)), 3)
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1), rt.swizzle(p3, "z"), 1), width=1)
    def vnoise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2), 2), 2)
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2)), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2)), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2)), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lumGradientSimplified__vec2(uv):
        uv = rt.copy(uv)
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        tl = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2), 2)), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2), 2)), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2), 2)), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2), 2)), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2), 2)), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_simplifiedTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2), 2)), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1), 1), br, 1), tl, 1), rt.binary("*", rt.f(2.0), l, 1), 1), bl, 1), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1), 1), tr, 1), bl, 1), rt.binary("*", rt.f(2.0), b, 1), 1), br, 1))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        src = rt.texture(_u_inputTex, uv)
        simplified = rt.swizzle(rt.texture(_u_simplifiedTex, uv), "rgb")
        edge = rt.length(lumGradientSimplified__vec2(uv))
        pool = rt.binary("*", rt.binary("*", rt.binary("/", _u_shadowIntensity, rt.f(100.0), 1), rt.f(0.7), 1), rt.component_wise("smoothstep", rt.f(0.05), rt.f(0.4), edge, width=1), 1)
        c = rt.binary("*", simplified, rt.binary("-", rt.f(1.0), pool, 1), 3)
        gc = rt.binary("+", rt.component_wise("floor", rt.swizzle(ctx.frag_coord, "xy"), width=2), _u_tileOffset, 2)
        c = rt.binary("*", c, rt.component_wise("mix", rt.f(1.0), rt.binary("+", rt.f(0.92), rt.binary("*", rt.f(0.08), vnoise__vec2(rt.binary("/", gc, rt.f(3.5), 2)), 1), 1), rt.binary("/", rt.component_wise("clamp", _u_paperTexture, rt.f(0.0), rt.f(100.0), width=1), rt.f(100.0), 1), width=1), 3)
        c = rt.component_wise("mix", c, rt.binary("*", c, rt.construct(3, rt.f(1.02), rt.f(1.0), rt.f(0.95)), 3), rt.binary("/", _u_paperTexture, rt.f(100.0), 1), width=3)
        flatness = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.15), edge, width=1), 1)
        c = rt.component_wise("mix", c, rt.construct(3, lum__vec3(c)), rt.binary("*", flatness, rt.f(0.12), 1), width=3)
        c = rt.binary("*", c, rt.binary("+", rt.f(1.0), rt.binary("*", flatness, rt.f(0.05), 1), 1), 3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", c, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
