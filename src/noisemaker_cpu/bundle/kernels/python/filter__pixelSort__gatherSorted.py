def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_preparedTex = T["preparedTex"]
    _u_rankTex = T["rankTex"]
    _u_brightestTex = T["brightestTex"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        size = rt.texture_size(_u_preparedTex)
        x = rt.swizzle(coord, "x")
        y = rt.swizzle(coord, "y")
        width = rt.swizzle(size, "x")
        brightestXNorm = rt.swizzle(rt.texel_fetch(_u_brightestTex, cpu_ivec2__float_float(rt.i(0), y), rt.i(0)), "r")
        brightestX = rt.construct(1, rt.component_wise("round", rt.binary("*", brightestXNorm, rt.construct(1, rt.binary("-", width, rt.i(1), 1)), 1), width=1))
        sortedIndex = rt.binary("%", rt.binary("+", rt.binary("-", x, brightestX, 1), width, 1), width, 1)
        targetRank = rt.binary("/", sortedIndex, rt.construct(1, rt.binary("-", width, rt.i(1), 1)), 1)
        NUM_SAMPLES = rt.i(64)
        bestDiff = rt.f(2.0)
        bestX = x
        s = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                s = rt.binary("+", s, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", s, NUM_SAMPLES)):
                break
            sampleX = rt.binary("/", rt.binary("*", s, width, 1), NUM_SAMPLES, 1)
            rankData = rt.texel_fetch(_u_rankTex, cpu_ivec2__float_float(sampleX, y), rt.i(0))
            pixelRank = rt.swizzle(rankData, "r")
            diff = rt.component_wise("abs", rt.binary("-", pixelRank, targetRank, 1), width=1)
            if rt.binary("<", diff, bestDiff):
                bestDiff = diff
                bestX = sampleX
        result = rt.texel_fetch(_u_preparedTex, cpu_ivec2__float_float(bestX, y), rt.i(0))
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
