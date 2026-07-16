def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_inputTex = T["inputTex"]
    _u_blurTex = T["blurTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_detail = U["detail"]
    _u_lightAngle = U["lightAngle"]
    _u_balance = U["balance"]
    _u_graininess = U["graininess"]
    _u_inkColor = U["inkColor"]
    _u_paperColor = U["paperColor"]
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def reliefShade__float_float_float_float_float(hC, hR, hT, strength, lightAngleDeg):
        grad = rt.binary("*", rt.construct(2, rt.binary("-", hR, hC, 1, "float"), rt.binary("-", hT, hC, 1, "float")), strength, 2, "float")
        n = rt.normalize(rt.construct(3, rt.unary("-", grad), rt.f(1.0)))
        a = rt.component_wise("radians", lightAngleDeg, width=1)
        L = rt.normalize(rt.construct(3, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1), rt.f(0.75)))
        return rt.component_wise("clamp", rt.dot(n, L), rt.f(0.0), rt.f(1.0), width=1)
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink)
        paper = rt.copy(paper)
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        hC = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, uv), "rgb"))
        hR = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "rgb"))
        hT = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "rgb"))
        strength = rt.binary("*", _u_detail, rt.f(0.2), 1, "float")
        outColor = rt.construct(3, 0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            shade = reliefShade__float_float_float_float_float(hC, hR, hT, strength, _u_lightAngle)
            outColor = tonemap2__float_vec3_vec3(rt.component_wise("mix", hC, shade, rt.f(0.75), width=1), _u_inkColor, _u_paperColor)
        else:
            if rt.binary("==", _u_MODE, rt.i(1)):
                hhC = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.35), rt.f(0.65), hC, width=1), 1, "float")
                hhR = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.35), rt.f(0.65), hR, width=1), 1, "float")
                hhT = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.35), rt.f(0.65), hT, width=1), 1, "float")
                shade = reliefShade__float_float_float_float_float(hhC, hhR, hhT, strength, _u_lightAngle)
                glossy = rt.component_wise("pow", shade, rt.f(2.0), width=1)
                outColor = tonemap2__float_vec3_vec3(rt.component_wise("mix", hhC, glossy, rt.f(0.75), width=1), _u_inkColor, _u_paperColor)
            else:
                if rt.binary("==", _u_MODE, rt.i(2)):
                    threshold = rt.binary("/", _u_balance, rt.f(100.0), 1, "float")
                    m = rt.component_wise("step", threshold, hC, width=1)
                    sheet = rt.component_wise("mix", rt.binary("+", rt.binary("*", _u_inkColor, rt.f(0.9), 3, "float"), rt.f(0.1), 3, "float"), _u_paperColor, m, width=3)
                    shade = reliefShade__float_float_float_float_float(hC, hR, hT, strength, _u_lightAngle)
                    gradMag = rt.length(rt.construct(2, rt.binary("-", hR, hC, 1, "float"), rt.binary("-", hT, hC, 1, "float")))
                    bandHeight = rt.component_wise("max", rt.binary("*", gradMag, rt.f(2.0), 1, "float"), rt.f(1e-05), width=1)
                    edge = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), bandHeight, rt.component_wise("abs", rt.binary("-", hC, threshold, 1, "float"), width=1), width=1), 1, "float")
                    beveled = rt.component_wise("clamp", rt.binary("*", sheet, rt.component_wise("mix", rt.f(0.6), rt.f(1.4), shade, width=1), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
                    sheetOut = rt.component_wise("mix", sheet, beveled, edge, width=3)
                    globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
                    grain = rt.binary("*", rt.binary("*", rt.binary("-", hash12__vec2(rt.component_wise("floor", globalCoord, width=2)), rt.f(0.5), 1, "float"), rt.binary("/", _u_graininess, rt.f(100.0), 1, "float"), 1, "float"), rt.f(0.15), 1, "float")
                    outColor = rt.component_wise("clamp", rt.binary("+", sheetOut, rt.construct(3, grain), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        g.fragColor = rt.construct(4, outColor, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
