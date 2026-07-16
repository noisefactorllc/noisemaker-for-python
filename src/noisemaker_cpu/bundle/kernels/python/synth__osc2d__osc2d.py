def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_aspect = U.get("aspect", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_oscType = U.get("oscType", 0)
    _u_frequency = U.get("frequency", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.141592653589793)
    g.TAU = rt.f(6.283185307179586)
    def hash11__float_float(p, s):
        p = rt.component_wise("fract", rt.binary("+", rt.binary("*", p, rt.f(234.34), 1, "float"), rt.binary("*", s, rt.f(0.7183), 1, "float"), 1, "float"), width=1)
        p = rt.binary("+", p, rt.binary("*", p, rt.binary("+", p, rt.f(34.23), 1, "float"), 1, "float"), 1, "float")
        return rt.component_wise("fract", rt.binary("*", p, p, 1, "float"), width=1)
    def tilingNoise1D__float_float_float(x, freq, s):
        p = rt.binary("*", x, freq, 1, "float")
        i = rt.component_wise("floor", p, width=1)
        f = rt.component_wise("fract", p, width=1)
        f = rt.binary("*", rt.binary("*", f, f, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 1, "float"), 1, "float"), 1, "float")
        i0 = rt.component_wise("mod", i, freq, width=1)
        i1 = rt.component_wise("mod", rt.binary("+", i, rt.f(1.0), 1, "float"), freq, width=1)
        a = hash11__float_float(i0, s)
        b = hash11__float_float(i1, s)
        return rt.component_wise("mix", a, b, f, width=1)
    def periodicValue__float_float(t, v):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.binary("-", t, v, 1, "float"), g.TAU, 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float")
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p, "float")
        s = rt.component_wise("sin", angle, width=1)
        c = rt.component_wise("cos", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), c, 1, "float"), 1, "float"))
    def oscSine__float(t):
        return rt.component_wise("sin", rt.binary("*", rt.component_wise("fract", t, width=1), g.PI, 1, "float"), width=1)
    def oscLinear__float(t):
        t = rt.component_wise("fract", t, width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", t, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float")
    def oscSawtooth__float(t):
        return rt.component_wise("fract", t, width=1)
    def oscSawtoothInv__float(t):
        return rt.binary("-", rt.f(1.0), rt.component_wise("fract", t, width=1), 1, "float")
    def oscSquare__float(t):
        return rt.component_wise("step", rt.f(0.5), rt.component_wise("fract", t, width=1), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        res = _u_fullResolution
        if rt.binary("<", rt.swizzle(res, "x"), rt.f(1.0)):
            res = rt.construct(2, rt.f(1024.0), rt.f(1024.0))
        st = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), res, 2, "float")
        st = rt.binary("-", st, rt.f(0.5), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        rotRad = rt.binary("/", rt.binary("*", _u_rotation, g.PI, 1, "float"), rt.f(180.0), 1, "float")
        st = rotate2D__vec2_float(st, rotRad)
        spatialPos = rt.binary("+", rt.swizzle(st, "y"), rt.f(0.5), 1, "float")
        freq = rt.construct(1, _u_frequency)
        spatialPhase = rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float")
        timePhase = rt.binary("*", _u_time, _u_speed, 1, "float")
        t = rt.binary("+", spatialPhase, timePhase, 1, "float")
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
                                scrollOffset = rt.component_wise("fract", rt.binary("*", _u_time, _u_speed, 1, "float"), width=1)
                                scrolledPos = rt.component_wise("fract", rt.binary("+", spatialPos, scrollOffset, 1, "float"), width=1)
                                timeNoise = tilingNoise1D__float_float_float(scrolledPos, freq, rt.binary("+", rt.construct(1, _u_seed), rt.f(12345.0), 1, "float"))
                                valueNoise = tilingNoise1D__float_float_float(scrolledPos, freq, rt.construct(1, _u_seed))
                                scaledTime = rt.binary("*", periodicValue__float_float(rt.f(0.0), timeNoise), _u_speed, 1, "float")
                                val = periodicValue__float_float(scaledTime, valueNoise)
                            else:
                                timeNoise = tilingNoise1D__float_float_float(spatialPos, freq, rt.binary("+", rt.construct(1, _u_seed), rt.f(12345.0), 1, "float"))
                                valueNoise = tilingNoise1D__float_float_float(spatialPos, freq, rt.construct(1, _u_seed))
                                scaledTime = rt.binary("*", periodicValue__float_float(_u_time, timeNoise), _u_speed, 1, "float")
                                val = periodicValue__float_float(scaledTime, valueNoise)
        g.fragColor = rt.construct(4, rt.construct(3, val), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
