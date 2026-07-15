def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_size = U["size"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2)
        if rt.binary("<", _u_size, rt.f(1.0)):
            g.fragColor = rt.texture(_u_inputTex, uv)
            return
        pixelSize = _u_size
        dx = rt.binary("/", pixelSize, rt.swizzle(resolution, "x"), 1)
        dy = rt.binary("/", pixelSize, rt.swizzle(resolution, "y"), 1)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), resolution, 2)
        centered = rt.binary("-", globalUV, rt.f(0.5), 2)
        globalCoord = rt.construct(2, rt.binary("*", dx, rt.component_wise("floor", rt.binary("/", rt.swizzle(centered, "x"), dx, 1), width=1), 1), rt.binary("*", dy, rt.component_wise("floor", rt.binary("/", rt.swizzle(centered, "y"), dy, 1), width=1), 1))
        globalCoord = rt.binary("+", globalCoord, rt.f(0.5), 2)
        coord = rt.binary("/", rt.binary("-", rt.binary("*", globalCoord, resolution, 2), _u_tileOffset, 2), tileDims, 2)
        g.fragColor = rt.texture(_u_inputTex, coord)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
