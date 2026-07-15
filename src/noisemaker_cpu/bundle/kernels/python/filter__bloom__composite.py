def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_bloomTex = T["bloomTex"]
    _u_intensity = U["intensity"]
    _u_tint = U["tint"]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        sceneColor = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        bloom = rt.swizzle(rt.texel_fetch(_u_bloomTex, coord, rt.i(0)), "rgb")
        bloom = rt.binary("*", bloom, _u_tint, 3, "float")
        finalRgb = rt.binary("+", rt.swizzle(sceneColor, "rgb"), rt.binary("*", _u_intensity, bloom, 3, "float"), 3, "float")
        g.fragColor = rt.construct(4, finalRgb, rt.swizzle(sceneColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
