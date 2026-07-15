def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        inSize = rt.texture_size(_u_inputTex)
        minVal = rt.f(100000.0)
        maxVal = rt.unary("-", rt.f(100000.0))
        y = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", y, rt.swizzle(inSize, "y"))):
                break
            x = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1)
                _for1_first = False
                if not (rt.binary("<", x, rt.swizzle(inSize, "x"))):
                    break
                color = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(x, y), rt.i(0))
                minVal = rt.component_wise("min", minVal, rt.swizzle(color, "r"), width=1)
                maxVal = rt.component_wise("max", maxVal, rt.swizzle(color, "g"), width=1)
        g.fragColor = rt.construct(4, minVal, maxVal, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
