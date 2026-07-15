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
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        outCoord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        inSize = rt.texture_size(_u_inputTex)
        baseCoord = rt.binary("*", outCoord, rt.i(16), 2)
        minVal = rt.f(100000.0)
        maxVal = rt.unary("-", rt.f(100000.0))
        dy = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dy = rt.binary("+", dy, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", dy, rt.i(16))):
                break
            dx = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dx = rt.binary("+", dx, rt.i(1), 1)
                _for1_first = False
                if not (rt.binary("<", dx, rt.i(16))):
                    break
                sampleCoord = rt.binary("+", baseCoord, cpu_ivec2__float_float(dx, dy), 2)
                if rt.binary("||", rt.binary(">=", rt.swizzle(sampleCoord, "x"), rt.swizzle(inSize, "x")), rt.binary(">=", rt.swizzle(sampleCoord, "y"), rt.swizzle(inSize, "y"))):
                    continue
                color = rt.texel_fetch(_u_inputTex, sampleCoord, rt.i(0))
                pixelMin = rt.component_wise("min", rt.component_wise("min", rt.swizzle(color, "r"), rt.swizzle(color, "g"), width=1), rt.swizzle(color, "b"), width=1)
                pixelMax = rt.component_wise("max", rt.component_wise("max", rt.swizzle(color, "r"), rt.swizzle(color, "g"), width=1), rt.swizzle(color, "b"), width=1)
                minVal = rt.component_wise("min", minVal, pixelMin, width=1)
                maxVal = rt.component_wise("max", maxVal, pixelMax, width=1)
        g.fragColor = rt.construct(4, minVal, maxVal, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
