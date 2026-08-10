def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_velTex = T["velTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_velTex)
        fragCoord = rt.swizzle(ctx.frag_coord, "xy")
        texel = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
        uv = rt.binary("/", fragCoord, rt.construct(2, texSize), 2, "float")
        uR = rt.swizzle(rt.texture(_u_velTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "rg")
        uL = rt.swizzle(rt.texture(_u_velTex, rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "rg")
        uT = rt.swizzle(rt.texture(_u_velTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "rg")
        uB = rt.swizzle(rt.texture(_u_velTex, rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "rg")
        if rt.binary("<", rt.swizzle(fragCoord, "x"), rt.f(1.0)):
            uL = rt.assign_swizzle(uL, "x", rt.unary("-", rt.swizzle(uR, "x")))
        if rt.binary(">", rt.swizzle(fragCoord, "x"), rt.binary("-", rt.construct(1, rt.swizzle(texSize, "x")), rt.f(1.0), 1, "float")):
            uR = rt.assign_swizzle(uR, "x", rt.unary("-", rt.swizzle(uL, "x")))
        if rt.binary("<", rt.swizzle(fragCoord, "y"), rt.f(1.0)):
            uB = rt.assign_swizzle(uB, "y", rt.unary("-", rt.swizzle(uT, "y")))
        if rt.binary(">", rt.swizzle(fragCoord, "y"), rt.binary("-", rt.construct(1, rt.swizzle(texSize, "y")), rt.f(1.0), 1, "float")):
            uT = rt.assign_swizzle(uT, "y", rt.unary("-", rt.swizzle(uB, "y")))
        div = rt.binary("*", rt.f(0.5), rt.binary("+", rt.binary("-", rt.swizzle(uR, "x"), rt.swizzle(uL, "x"), 1, "float"), rt.binary("-", rt.swizzle(uT, "y"), rt.swizzle(uB, "y"), 1, "float"), 1, "float"), 1, "float")
        g.fragColor[:] = rt.construct(4, rt.f(0.0), div, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
