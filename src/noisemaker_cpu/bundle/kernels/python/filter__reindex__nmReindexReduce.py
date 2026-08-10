def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_statsTex = T["statsTex"]
    g.F32_MAX = rt.f(3.402823466e+38)
    g.F32_MIN = rt.unary("-", rt.f(3.402823466e+38))
    g.TILE_SIZE = rt.i(8)
    g.MAX_TILE_DIM = rt.i(512)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        if (bool(rt.binary("!=", rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="int"), rt.i(0))) or bool(rt.binary("!=", rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="int"), rt.i(0)))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        statsTexSize = rt.texture_size(_u_statsTex)
        tileCount = rt.construct(2, rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(statsTexSize, "x"), g.TILE_SIZE, 1, "int"), rt.i(1), 1, "int"), g.TILE_SIZE, 1, "int"), rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(statsTexSize, "y"), g.TILE_SIZE, 1, "int"), rt.i(1), 1, "int"), g.TILE_SIZE, 1, "int"), base="int")
        globalMin = g.F32_MAX
        globalMax = g.F32_MIN
        ty = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                ty = rt.binary("+", ty, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", ty, g.MAX_TILE_DIM)):
                break
            if rt.binary(">=", ty, rt.swizzle(tileCount, "y")):
                break
            tx = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    tx = rt.binary("+", tx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<", tx, g.MAX_TILE_DIM)):
                    break
                if rt.binary(">=", tx, rt.swizzle(tileCount, "x")):
                    break
                sampleCoord = rt.construct(2, rt.binary("*", tx, g.TILE_SIZE, 1, "int"), rt.binary("*", ty, g.TILE_SIZE, 1, "int"), base="int")
                tileStats = rt.swizzle(rt.texel_fetch(_u_statsTex, sampleCoord, rt.i(0)), "xy")
                globalMin = rt.component_wise("min", globalMin, rt.swizzle(tileStats, "x"), width=1)
                globalMax = rt.component_wise("max", globalMax, rt.swizzle(tileStats, "y"), width=1)
        g.fragColor[:] = rt.construct(4, globalMin, globalMax, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
