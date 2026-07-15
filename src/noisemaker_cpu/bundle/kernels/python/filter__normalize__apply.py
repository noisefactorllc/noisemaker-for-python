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
    _u_statsTex = T["statsTex"]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        stats = rt.texel_fetch(_u_statsTex, rt.construct(2, rt.i(0), rt.i(0), base="int"), rt.i(0))
        minVal = rt.swizzle(stats, "r")
        maxVal = rt.swizzle(stats, "g")
        if rt.binary("<", rt.binary("-", maxVal, minVal, 1, "float"), rt.f(1e-05)):
            g.fragColor = color
            return
        normalized = rt.binary("/", rt.binary("-", rt.swizzle(color, "rgb"), minVal, 3, "float"), rt.binary("-", maxVal, minVal, 1, "float"), 3, "float")
        g.fragColor = rt.construct(4, normalized, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
