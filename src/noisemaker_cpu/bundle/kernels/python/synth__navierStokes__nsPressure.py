def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_bufTex = T["bufTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_bufTex)
        fragCoord = rt.swizzle(ctx.frag_coord, "xy")
        texel = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
        uv = rt.binary("/", fragCoord, rt.construct(2, texSize), 2, "float")
        pR = rt.swizzle(rt.texture(_u_bufTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "r")
        pL = rt.swizzle(rt.texture(_u_bufTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "r")
        pT = rt.swizzle(rt.texture(_u_bufTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "r")
        pB = rt.swizzle(rt.texture(_u_bufTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "r")
        div = rt.swizzle(rt.texture(_u_bufTex, uv), "g")
        p = rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("+", rt.binary("+", pR, pL, 1, "float"), pT, 1, "float"), pB, 1, "float"), div, 1, "float"), rt.f(0.25), 1, "float")
        g.fragColor[:] = rt.construct(4, p, div, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
