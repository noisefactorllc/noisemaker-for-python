def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_statsTex = T["statsTex"]
    g.F32_MAX = rt.f(3.402823466e38)
    g.F32_MIN = rt.unary("-", rt.f(3.402823466e38))
    g.TILE_SIZE = rt.i(8)
    g.MAX_TILE_DIM = rt.i(512)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        if rt.binary("||", rt.binary("!=", rt.construct(1, rt.swizzle(ctx.frag_coord, "x")), rt.i(0)), rt.binary("!=", rt.construct(1, rt.swizzle(ctx.frag_coord, "y")), rt.i(0))):
            g.fragColor = rt.construct(4, rt.f(0.0))
            return
        statsTexSize = rt.texture_size(_u_statsTex)
        tileCount = cpu_ivec2__float_float(rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(statsTexSize, "x"), g.TILE_SIZE, 1), rt.i(1), 1), g.TILE_SIZE, 1), rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(statsTexSize, "y"), g.TILE_SIZE, 1), rt.i(1), 1), g.TILE_SIZE, 1))
        globalMin = g.F32_MAX
        globalMax = g.F32_MIN
        ty = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                rt.unary("++", ty)
            _for0_first = False
            if not (rt.binary("<", ty, g.MAX_TILE_DIM)):
                break
            if rt.binary(">=", ty, rt.swizzle(tileCount, "y")):
                break
            tx = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    rt.unary("++", tx)
                _for1_first = False
                if not (rt.binary("<", tx, g.MAX_TILE_DIM)):
                    break
                if rt.binary(">=", tx, rt.swizzle(tileCount, "x")):
                    break
                sampleCoord = cpu_ivec2__float_float(rt.binary("*", tx, g.TILE_SIZE, 1), rt.binary("*", ty, g.TILE_SIZE, 1))
                tileStats = rt.swizzle(rt.texel_fetch(_u_statsTex, sampleCoord, rt.i(0)), "xy")
                globalMin = rt.component_wise("min", globalMin, rt.swizzle(tileStats, "x"), width=1)
                globalMax = rt.component_wise("max", globalMax, rt.swizzle(tileStats, "y"), width=1)
        g.fragColor = rt.construct(4, globalMin, globalMax, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
