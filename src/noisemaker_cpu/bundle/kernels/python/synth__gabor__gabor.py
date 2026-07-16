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
    _u_time = U["time"]
    _u_seed = U["seed"]
    _u_scale = U["scale"]
    _u_orientation = U["orientation"]
    _u_bandwidth = U["bandwidth"]
    _u_isotropy = U["isotropy"]
    _u_density = U["density"]
    _u_octaves = U["octaves"]
    _u_speed = U["speed"]
    g.fragColor = rt.construct(4, 0.0)
    def pcg__uvec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.i(4294967295)), 3, "float")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def gaborNoise__vec2_float_float_float_float_int_float_float(st, freq, sigma, baseAngle, iso, impulses, t, sd):
        st = rt.copy(st)
        cell = rt.component_wise("floor", st, width=2)
        frac = rt.component_wise("fract", st, width=2)
        sum = rt.f(0.0)
        dy = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dy, rt.i(1))):
                break
            dx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", dx, rt.i(1))):
                    break
                neighbor = rt.construct(2, rt.construct(1, dx), rt.construct(1, dy))
                cellId = rt.binary("+", cell, neighbor, 2, "float")
                k = rt.i(0)
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        k = rt.binary("+", k, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<", k, rt.i(8))):
                        break
                    if rt.binary(">=", k, impulses):
                        break
                    r1 = prng__vec3(rt.construct(3, cellId, rt.binary("+", sd, rt.binary("*", rt.construct(1, k), rt.f(7.0), 1, "float"), 1, "float")))
                    r2 = prng__vec3(rt.construct(3, rt.binary("+", sd, rt.binary("*", rt.construct(1, k), rt.f(13.0), 1, "float"), 1, "float"), cellId))
                    impulsePos = rt.swizzle(r1, "xy")
                    impulsePos = rt.binary("+", impulsePos, rt.binary("*", rt.construct(2, rt.component_wise("sin", rt.binary("+", t, rt.binary("*", rt.swizzle(r2, "x"), rt.f(6.28318530718), 1, "float"), 1, "float"), width=1), rt.component_wise("cos", rt.binary("+", t, rt.binary("*", rt.swizzle(r2, "y"), rt.f(6.28318530718), 1, "float"), 1, "float"), width=1)), rt.f(0.15), 2, "float"), 2, "float")
                    delta = rt.binary("-", rt.binary("+", neighbor, impulsePos, 2, "float"), frac, 2, "float")
                    angle = rt.component_wise("mix", baseAngle, rt.binary("*", rt.swizzle(r2, "z"), rt.f(6.28318530718), 1, "float"), iso, width=1)
                    dir = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
                    weight = (rt.unary("-", rt.f(1.0)) if rt.binary("<", rt.swizzle(r1, "z"), rt.f(0.5)) else rt.f(1.0))
                    envelope = rt.component_wise("exp", rt.binary("/", rt.unary("-", rt.dot(delta, delta)), rt.binary("*", rt.binary("*", rt.f(2.0), sigma, 1, "float"), sigma, 1, "float"), 1, "float"), width=1)
                    phase = rt.binary("*", rt.binary("*", rt.f(6.28318530718), freq, 1, "float"), rt.dot(dir, delta), 1, "float")
                    sum = rt.binary("+", sum, rt.binary("*", rt.binary("*", weight, envelope, 1, "float"), rt.component_wise("cos", phase, width=1), 1, "float"), 1, "float")
        return sum
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        freq = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(1.0))
        sigma = map__float_float_float_float_float(_u_bandwidth, rt.f(1.0), rt.f(100.0), rt.f(0.05), rt.f(0.35))
        baseAngle = rt.binary("/", rt.binary("*", _u_orientation, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        iso = rt.binary("/", _u_isotropy, rt.f(100.0), 1, "float")
        impulses = rt.construct(1, _u_density, base="int")
        oct = rt.construct(1, _u_octaves, base="int")
        spd = rt.component_wise("floor", _u_speed, width=1)
        t = rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float")
        p = rt.binary("*", st, freq, 2, "float")
        value = rt.f(0.0)
        amplitude = rt.f(1.0)
        totalAmp = rt.f(0.0)
        pOct = p
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for3_first = False
            if not (rt.binary("<", i, rt.i(5))):
                break
            if rt.binary(">=", i, oct):
                break
            octFreq = rt.binary("+", rt.f(1.0), rt.binary("*", rt.construct(1, i), rt.f(0.5), 1, "float"), 1, "float")
            octSigma = rt.binary("/", sigma, rt.binary("+", rt.f(1.0), rt.binary("*", rt.construct(1, i), rt.f(0.5), 1, "float"), 1, "float"), 1, "float")
            fi = rt.construct(1, i)
            value = rt.binary("+", value, rt.binary("*", amplitude, gaborNoise__vec2_float_float_float_float_int_float_float(pOct, octFreq, octSigma, baseAngle, iso, impulses, rt.binary("+", t, rt.binary("*", fi, rt.f(3.7), 1, "float"), 1, "float"), rt.binary("+", _u_seed, rt.binary("*", fi, rt.f(17.0), 1, "float"), 1, "float")), 1, "float"), 1, "float")
            totalAmp = rt.binary("+", totalAmp, amplitude, 1, "float")
            amplitude = rt.binary("*", amplitude, rt.f(0.5), 1, "float")
            pOct = rt.binary("*", pOct, rt.f(2.0), 2, "float")
        value = rt.binary("/", value, totalAmp, 1, "float")
        n = rt.binary("/", rt.f(1.0), rt.binary("+", rt.f(1.0), rt.component_wise("exp", rt.binary("*", rt.unary("-", value), rt.f(3.0), 1, "float"), width=1), 1, "float"), 1, "float")
        g.fragColor = rt.construct(4, rt.construct(3, n), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
