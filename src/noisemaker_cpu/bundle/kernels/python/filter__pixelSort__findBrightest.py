def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_lumTex = T["lumTex"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        size = rt.texture_size(_u_lumTex)
        y = rt.swizzle(coord, "y")
        width = rt.swizzle(size, "x")
        NUM_SAMPLES = rt.i(32)
        maxLum = rt.unary("-", rt.f(1.0))
        brightestX = rt.i(0)
        s = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                s = rt.binary("+", s, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", s, NUM_SAMPLES)):
                break
            sampleX = rt.binary("/", rt.binary("*", s, width, 1), NUM_SAMPLES, 1)
            lum = rt.swizzle(rt.texel_fetch(_u_lumTex, cpu_ivec2__float_float(sampleX, y), rt.i(0)), "r")
            if rt.binary(">", lum, maxLum):
                maxLum = lum
                brightestX = sampleX
        g.fragColor = rt.construct(4, rt.binary("/", brightestX, rt.construct(1, rt.binary("-", width, rt.i(1), 1)), 1), maxLum, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
