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
    _u_highlight = U["highlight"]
    _u_smoothness = U["smoothness"]
    _u_lightDirection = U["lightDirection"]
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        src = rt.texture(_u_inputTex, uv)
        hC = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, uv), "rgb"))
        hL = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2)), "rgb"))
        hR = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2)), "rgb"))
        hB = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2)), "rgb"))
        hT = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2)), "rgb"))
        grad = rt.construct(2, rt.binary("-", hR, hL, 1), rt.binary("-", hT, hB, 1))
        strength = rt.f(10.0)
        n = rt.normalize(rt.construct(3, rt.binary("*", rt.unary("-", grad), strength, 2), rt.f(1.0)))
        lightLengthSq = rt.dot(_u_lightDirection, _u_lightDirection)
        operatorLight = (_u_lightDirection if rt.binary(">", lightLengthSq, rt.f(0.000001)) else rt.construct(3, rt.unary("-", rt.f(0.4)), rt.f(0.6), rt.f(0.7)))
        controlledLight = rt.construct(3, rt.unary("-", rt.swizzle(operatorLight, "xy")), rt.swizzle(operatorLight, "z"))
        L = rt.normalize(controlledLight)
        V = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0))
        halfVector = rt.binary("+", L, V, 3)
        halfLengthSq = rt.dot(halfVector, halfVector)
        defaultL = rt.normalize(rt.construct(3, rt.f(0.4), rt.unary("-", rt.f(0.6)), rt.f(0.7)))
        defaultHalf = rt.normalize(rt.binary("+", defaultL, V, 3))
        H = (rt.normalize(halfVector) if rt.binary(">", halfLengthSq, rt.f(0.000001)) else defaultHalf)
        gloss = rt.component_wise("mix", rt.f(24.0), rt.f(6.0), rt.binary("/", _u_smoothness, rt.f(100.0), 1), width=1)
        flatSpec = rt.component_wise("pow", rt.swizzle(H, "z"), gloss, width=1)
        rawSpec = rt.component_wise("pow", rt.component_wise("clamp", rt.dot(n, H), rt.f(0.0), rt.f(1.0), width=1), gloss, width=1)
        spec = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rawSpec, flatSpec, 1), rt.component_wise("max", rt.binary("-", rt.f(1.0), flatSpec, 1), rt.f(0.0001), width=1), 1), rt.f(0.0), rt.f(1.0), width=1)
        curv = rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("*", rt.f(4.0), hC, 1), hL, 1), hR, 1), hB, 1), hT, 1)
        ridge = rt.component_wise("clamp", rt.binary("*", rt.binary("*", curv, strength, 1), rt.f(2.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        spec = rt.component_wise("clamp", rt.binary("+", rt.binary("*", spec, rt.f(1.35), 1), rt.binary("*", ridge, rt.f(0.75), 1), 1), rt.f(0.0), rt.f(1.0), width=1)
        specColor = rt.component_wise("clamp", rt.binary("*", rt.construct(3, spec), rt.binary("/", _u_highlight, rt.f(100.0), 1), 3), rt.f(0.0), rt.f(1.0), width=3)
        outc = rt.binary("-", rt.construct(3, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.construct(3, rt.f(1.0)), rt.swizzle(src, "rgb"), 3), rt.binary("-", rt.construct(3, rt.f(1.0)), specColor, 3), 3), 3)
        g.fragColor = rt.construct(4, outc, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
