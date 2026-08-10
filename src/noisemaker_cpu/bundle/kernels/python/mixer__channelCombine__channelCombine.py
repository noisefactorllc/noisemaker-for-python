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
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_rLevel = U.get("rLevel", rt.f(0.0))
    _u_gLevel = U.get("gLevel", rt.f(0.0))
    _u_bLevel = U.get("bLevel", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def luminance__vec4(c):
        c = rt.copy(c, "float")
        return rt.dot(rt.swizzle(c, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        r = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_rTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_rTex)), 2, "float"))), _u_rLevel, 1, "float"), rt.f(100.0), 1, "float")
        _g = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_gTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_gTex)), 2, "float"))), _u_gLevel, 1, "float"), rt.f(100.0), 1, "float")
        b = rt.binary("/", rt.binary("*", luminance__vec4(rt.texture(_u_bTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_bTex)), 2, "float"))), _u_bLevel, 1, "float"), rt.f(100.0), 1, "float")
        g.fragColor[:] = rt.construct(4, r, _g, b, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
