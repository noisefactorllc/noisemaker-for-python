def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_size = U.get("size", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2, "float")
        if rt.binary("<", _u_size, rt.f(1.0)):
            g.fragColor[:] = rt.texture(_u_inputTex, uv)
            return
        pixelSize = _u_size
        dx = rt.binary("/", pixelSize, rt.swizzle(resolution, "x"), 1, "float")
        dy = rt.binary("/", pixelSize, rt.swizzle(resolution, "y"), 1, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), resolution, 2, "float")
        centered = rt.binary("-", globalUV, rt.f(0.5), 2, "float")
        globalCoord = rt.construct(2, rt.binary("*", dx, rt.component_wise("floor", rt.binary("/", rt.swizzle(centered, "x"), dx, 1, "float"), width=1), 1, "float"), rt.binary("*", dy, rt.component_wise("floor", rt.binary("/", rt.swizzle(centered, "y"), dy, 1, "float"), width=1), 1, "float"))
        globalCoord[:] = rt.binary("+", globalCoord, rt.f(0.5), 2, "float")
        coord = rt.binary("/", rt.binary("-", rt.binary("*", globalCoord, resolution, 2, "float"), _u_tileOffset, 2, "float"), tileDims, 2, "float")
        g.fragColor[:] = rt.texture(_u_inputTex, coord)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
