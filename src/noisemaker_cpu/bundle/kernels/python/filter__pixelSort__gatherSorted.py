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
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        size = rt.texture_size(_u_preparedTex)
        x = rt.swizzle(coord, "x")
        y = rt.swizzle(coord, "y")
        width = rt.swizzle(size, "x")
        brightestXNorm = rt.swizzle(rt.texel_fetch(_u_brightestTex, rt.construct(2, rt.i(0), y, base="int"), rt.i(0)), "r")
        brightestX = rt.construct(1, rt.component_wise("round", rt.binary("*", brightestXNorm, rt.construct(1, rt.binary("-", width, rt.i(1), 1, "int")), 1, "float"), width=1), base="int")
        sortedIndex = rt.binary("%", rt.binary("+", rt.binary("-", x, brightestX, 1, "int"), width, 1, "int"), width, 1, "int")
        targetRank = rt.binary("/", rt.construct(1, sortedIndex), rt.construct(1, rt.binary("-", width, rt.i(1), 1, "int")), 1, "float")
        NUM_SAMPLES = rt.i(64)
        bestDiff = rt.f(2.0)
        bestX = x
        s = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                s = rt.binary("+", s, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", s, NUM_SAMPLES)):
                break
            sampleX = rt.binary("/", rt.binary("*", s, width, 1, "int"), NUM_SAMPLES, 1, "int")
            rankData = rt.texel_fetch(_u_rankTex, rt.construct(2, sampleX, y, base="int"), rt.i(0))
            pixelRank = rt.swizzle(rankData, "r")
            diff = rt.component_wise("abs", rt.binary("-", pixelRank, targetRank, 1, "float"), width=1)
            if rt.binary("<", diff, bestDiff):
                bestDiff = diff
                bestX = sampleX
        result = rt.texel_fetch(_u_preparedTex, rt.construct(2, bestX, y, base="int"), rt.i(0))
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
