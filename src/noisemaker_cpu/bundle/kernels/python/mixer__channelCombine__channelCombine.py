def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_rTex = T["rTex"]
    _u_gTex = T["gTex"]
    _u_bTex = T["bTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_rLevel = U["rLevel"]
    _u_gLevel = U["gLevel"]
    _u_bLevel = U["bLevel"]
    def luminance__vec4(c):
        c = rt.copy(c)
        return rt.dot(rt.swizzle(c, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        r = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_rTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_rTex)), 2))), _u_rLevel, 1), rt.f(100.0), 1)
        g = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_gTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_gTex)), 2))), _u_gLevel, 1), rt.f(100.0), 1)
        b = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_bTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_bTex)), 2))), _u_bLevel, 1), rt.f(100.0), 1)
        g.fragColor = rt.construct(4, r, g, b, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
