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
    _u_detail = U["detail"]
    _u_distortion = U["distortion"]
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        texel = rt.binary("/", rt.f(1.0), _u_resolution, 2)
        hL = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2)), "rgb"))
        hR = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2)), "rgb"))
        hB = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2)), "rgb"))
        hT = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2)), "rgb"))
        grad = rt.construct(2, rt.binary("-", hR, hL, 1), rt.binary("-", hT, hB, 1))
        uv2 = rt.binary("+", uv, rt.binary("*", rt.binary("*", grad, rt.binary("/", _u_distortion, rt.f(100.0), 1), 2), rt.f(0.5), 2), 2)
        h2 = lum__vec3(rt.swizzle(rt.texture(_u_blurTex, uv2), "rgb"))
        cycles = rt.component_wise("mix", rt.f(1.0), rt.f(7.0), rt.binary("/", _u_detail, rt.f(100.0), 1), width=1)
        v = rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", h2, cycles, 1), rt.f(6.28318530718), 1), rt.binary("*", h2, rt.f(3.0), 1), 1), width=1), 1), 1)
        v = rt.binary("+", v, rt.binary("*", rt.component_wise("pow", v, rt.f(8.0), width=1), rt.f(0.5), 1), 1)
        v = rt.component_wise("clamp", v, rt.f(0.0), rt.f(1.0), width=1)
        outColor = rt.component_wise("clamp", rt.binary("*", rt.construct(3, v), rt.construct(3, rt.f(0.96), rt.f(0.98), rt.f(1.02)), 3), rt.f(0.0), rt.f(1.0), width=3)
        src = rt.texture(_u_inputTex, uv)
        g.fragColor = rt.construct(4, outColor, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
