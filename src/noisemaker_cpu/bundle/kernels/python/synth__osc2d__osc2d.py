def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_aspect = U["aspect"]
    _u_time = U["time"]
    _u_oscType = U["oscType"]
    _u_frequency = U["frequency"]
    _u_speed = U["speed"]
    _u_rotation = U["rotation"]
    _u_seed = U["seed"]
    g.PI = rt.f(3.141592653589793)
    g.TAU = rt.f(6.283185307179586)
    def hash11__float_float(p, s):
        p = rt.component_wise("fract", rt.binary("+", rt.binary("*", p, rt.f(234.34), 1), rt.binary("*", s, rt.f(0.7183), 1), 1), width=1)
        p = rt.binary("+", p, rt.binary("*", p, rt.binary("+", p, rt.f(34.23), 1), 1), 1)
        return rt.component_wise("fract", rt.binary("*", p, p, 1), width=1)
    def tilingNoise1D__float_float_float(x, freq, s):
        p = rt.binary("*", x, freq, 1)
        i = rt.component_wise("floor", p, width=1)
        f = rt.component_wise("fract", p, width=1)
        f = rt.binary("*", rt.binary("*", f, f, 1), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 1), 1), 1)
        i0 = rt.component_wise("mod", i, freq, width=1)
        i1 = rt.component_wise("mod", rt.binary("+", i, rt.f(1.0), 1), freq, width=1)
        a = hash11__float_float(i0, s)
        b = hash11__float_float(i1, s)
        return rt.component_wise("mix", a, b, f, width=1)
    def periodicValue__float_float(t, v):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.binary("-", t, v, 1), g.TAU, 1), width=1), rt.f(1.0), 1), rt.f(0.5), 1)
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p)
        s = rt.component_wise("sin", angle, width=1)
        c = rt.component_wise("cos", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1), rt.binary("*", rt.swizzle(p, "y"), s, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1), rt.binary("*", rt.swizzle(p, "y"), c, 1), 1))
    def oscSine__float(t):
        return rt.component_wise("sin", rt.binary("*", rt.component_wise("fract", t, width=1), g.PI, 1), width=1)
    def oscLinear__float(t):
        t = rt.component_wise("fract", t, width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", t, rt.f(2.0), 1), rt.f(1.0), 1), width=1), 1)
    def oscSawtooth__float(t):
        return rt.component_wise("fract", t, width=1)
    def oscSawtoothInv__float(t):
        return rt.binary("-", rt.f(1.0), rt.component_wise("fract", t, width=1), 1)
    def oscSquare__float(t):
        return rt.component_wise("step", rt.f(0.5), rt.component_wise("fract", t, width=1), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        res = _u_fullResolution
        if rt.binary("<", rt.swizzle(res, "x"), rt.f(1.0)):
            res = rt.construct(2, rt.f(1024.0), rt.f(1024.0))
        st = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), res, 2)
        st = rt.binary("-", st, rt.f(0.5), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1))
        rotRad = rt.binary("/", rt.binary("*", _u_rotation, g.PI, 1), rt.f(180.0), 1)
        st = rotate2D__vec2_float(st, rotRad)
        spatialPos = rt.binary("+", rt.swizzle(st, "y"), rt.f(0.5), 1)
        freq = _u_frequency
        spatialPhase = rt.binary("*", rt.swizzle(st, "y"), freq, 1)
        timePhase = rt.binary("*", _u_time, _u_speed, 1)
        t = rt.binary("+", spatialPhase, timePhase, 1)
        val = rt.f(0.0)
        if rt.binary("==", _u_oscType, rt.i(0)):
            val = oscSine__float(t)
        else:
            if rt.binary("==", _u_oscType, rt.i(1)):
                val = oscLinear__float(t)
            else:
                if rt.binary("==", _u_oscType, rt.i(2)):
                    val = oscSawtooth__float(t)
                else:
                    if rt.binary("==", _u_oscType, rt.i(3)):
                        val = oscSawtoothInv__float(t)
                    else:
                        if rt.binary("==", _u_oscType, rt.i(4)):
                            val = oscSquare__float(t)
                        else:
                            if rt.binary("==", _u_oscType, rt.i(5)):
                                scrollOffset = rt.component_wise("fract", rt.binary("*", _u_time, _u_speed, 1), width=1)
                                scrolledPos = rt.component_wise("fract", rt.binary("+", spatialPos, scrollOffset, 1), width=1)
                                timeNoise = tilingNoise1D__float_float_float(scrolledPos, freq, rt.binary("+", _u_seed, rt.f(12345.0), 1))
                                valueNoise = tilingNoise1D__float_float_float(scrolledPos, freq, _u_seed)
                                scaledTime = rt.binary("*", periodicValue__float_float(rt.f(0.0), timeNoise), _u_speed, 1)
                                val = periodicValue__float_float(scaledTime, valueNoise)
                            else:
                                timeNoise = tilingNoise1D__float_float_float(spatialPos, freq, rt.binary("+", _u_seed, rt.f(12345.0), 1))
                                valueNoise = tilingNoise1D__float_float_float(spatialPos, freq, _u_seed)
                                scaledTime = rt.binary("*", periodicValue__float_float(_u_time, timeNoise), _u_speed, 1)
                                val = periodicValue__float_float(scaledTime, valueNoise)
        g.fragColor = rt.construct(4, rt.construct(3, val), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
