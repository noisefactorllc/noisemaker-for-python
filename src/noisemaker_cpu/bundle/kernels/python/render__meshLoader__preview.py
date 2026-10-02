def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_positionsTex = T["positionsTex"]
    _u_normalsTex = T["normalsTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        pos = rt.texture(_u_positionsTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_positionsTex)), 2, "float"))
        normal = rt.texture(_u_normalsTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_normalsTex)), 2, "float"))
        color = rt.construct(3, 0.0)
        if rt.binary("<", rt.swizzle(globalUV, "x"), rt.f(0.5)):
            color[:] = rt.binary("+", rt.binary("*", rt.swizzle(pos, "xyz"), rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        else:
            color[:] = rt.binary("+", rt.binary("*", rt.swizzle(normal, "xyz"), rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        alpha = rt.f(1.0)
        g.fragColor[:] = rt.construct(4, color, alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
