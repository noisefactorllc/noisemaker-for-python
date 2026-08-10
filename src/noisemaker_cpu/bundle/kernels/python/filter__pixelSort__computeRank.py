def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_lumTex = T["lumTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        size = rt.texture_size(_u_lumTex)
        x = rt.swizzle(coord, "x")
        y = rt.swizzle(coord, "y")
        width = rt.swizzle(size, "x")
        myLum = rt.swizzle(rt.texel_fetch(_u_lumTex, coord, rt.i(0)), "r")
        NUM_SAMPLES = rt.i(32)
        brighterCount = rt.i(0)
        s = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                s = rt.binary("+", s, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", s, NUM_SAMPLES)):
                break
            sampleX = rt.binary("/", rt.binary("*", s, width, 1, "int"), NUM_SAMPLES, 1, "int")
            if rt.binary("==", sampleX, x):
                continue
            otherLum = rt.swizzle(rt.texel_fetch(_u_lumTex, rt.construct(2, sampleX, y, base="int"), rt.i(0)), "r")
            if (bool(rt.binary(">", otherLum, myLum)) or bool((bool(rt.binary("==", otherLum, myLum)) and bool(rt.binary("<", sampleX, x))))):
                brighterCount = rt.binary("+", brighterCount, rt.i(1), 1, "int")
        estimatedRank = rt.binary("/", rt.construct(1, brighterCount), rt.construct(1, NUM_SAMPLES), 1, "float")
        g.fragColor[:] = rt.construct(4, estimatedRank, myLum, rt.binary("/", rt.construct(1, x), rt.construct(1, rt.binary("-", width, rt.i(1), 1, "int")), 1, "float"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
