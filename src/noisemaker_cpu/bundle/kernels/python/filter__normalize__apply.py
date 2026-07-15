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
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        stats = rt.texel_fetch(_u_statsTex, cpu_ivec2__float_float(rt.i(0), rt.i(0)), rt.i(0))
        minVal = rt.swizzle(stats, "r")
        maxVal = rt.swizzle(stats, "g")
        if rt.binary("<", rt.binary("-", maxVal, minVal, 1), rt.f(0.00001)):
            g.fragColor = color
            return
        normalized = rt.binary("/", rt.binary("-", rt.swizzle(color, "rgb"), minVal, 3), rt.binary("-", maxVal, minVal, 1), 3)
        g.fragColor = rt.construct(4, normalized, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
