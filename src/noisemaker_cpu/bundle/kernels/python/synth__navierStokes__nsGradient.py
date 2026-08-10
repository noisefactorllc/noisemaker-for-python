def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_velTex = T["velTex"]
    _u_pressureTex = T["pressureTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_velTex)
        fragCoord = rt.swizzle(ctx.frag_coord, "xy")
        texel = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
        uv = rt.binary("/", fragCoord, rt.construct(2, texSize), 2, "float")
        pR = rt.swizzle(rt.texture(_u_pressureTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "r")
        pL = rt.swizzle(rt.texture(_u_pressureTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "r")
        pT = rt.swizzle(rt.texture(_u_pressureTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "r")
        pB = rt.swizzle(rt.texture(_u_pressureTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "r")
        grad = rt.binary("*", rt.f(0.5), rt.construct(2, rt.binary("-", pR, pL, 1, "float"), rt.binary("-", pT, pB, 1, "float")), 2, "float")
        here = rt.texture(_u_velTex, uv)
        u = rt.binary("-", rt.swizzle(here, "rg"), grad, 2, "float")
        g.fragColor[:] = rt.construct(4, u, rt.swizzle(here, "b"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
