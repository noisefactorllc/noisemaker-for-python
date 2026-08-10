def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blurTex = T["blurTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_darkness = U.get("darkness", rt.f(0.0))
    _u_inkColor = U.get("inkColor", rt.construct(3, 0.0))
    _u_paperColor = U.get("paperColor", rt.construct(3, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink, "float")
        paper = rt.copy(paper, "float")
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        blur = rt.texture(_u_blurTex, uv)
        lumSrc = lum__vec3(rt.swizzle(src, "rgb"))
        lumBlur = lum__vec3(rt.swizzle(blur, "rgb"))
        band = rt.binary("-", lumSrc, lumBlur, 1, "float")
        edgeGain = rt.component_wise("mix", rt.f(4.0), rt.f(18.0), rt.binary("/", _u_darkness, rt.f(100.0), 1, "float"), width=1)
        edgeInk = rt.component_wise("clamp", rt.binary("*", rt.component_wise("abs", band, width=1), edgeGain, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        toneHi = rt.component_wise("mix", rt.f(0.35), rt.f(0.68), rt.binary("/", _u_darkness, rt.f(100.0), 1, "float"), width=1)
        toneLo = rt.binary("-", toneHi, rt.f(0.26), 1, "float")
        toneInk = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", toneLo, toneHi, lumSrc, width=1), 1, "float")
        ink = rt.component_wise("clamp", rt.component_wise("max", edgeInk, toneInk, width=1), rt.f(0.0), rt.f(1.0), width=1)
        outColor = tonemap2__float_vec3_vec3(rt.binary("-", rt.f(1.0), ink, 1, "float"), _u_inkColor, _u_paperColor)
        g.fragColor[:] = rt.construct(4, outColor, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
