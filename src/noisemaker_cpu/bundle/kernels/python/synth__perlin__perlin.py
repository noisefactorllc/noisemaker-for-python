def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_DIMENSIONS = U["DIMENSIONS"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_aspect = U["aspect"]
    _u_time = U["time"]
    _u_scale = U["scale"]
    _u_seed = U["seed"]
    _u_octaves = U["octaves"]
    _u_colorMode = U["colorMode"]
    _u_ridges = U["ridges"]
    _u_warpIterations = U["warpIterations"]
    _u_warpScale = U["warpScale"]
    _u_warpIntensity = U["warpIntensity"]
    _u_speed = U["speed"]
    g.TAU = rt.f(6.283185307179586)
    g.Z_PERIOD = rt.f(4.0)
    def cpu_ivec3__float(value):
        return rt.construct(3, value)
    def cpu_ivec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_ivec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525)), 3), rt.construct(1, rt.i(1013904223)), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16)), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1)))
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def hash3__vec3(p):
        p = rt.copy(p)
        p = rt.binary("+", p, rt.binary("*", _u_seed, rt.f(0.1), 1), 3)
        q = cpu_uvec3__vec3(rt.binary("+", cpu_ivec3__vec3(rt.binary("*", p, rt.f(1000.0), 3)), rt.i(65536), 3))
        q = rt.binary("+", rt.binary("*", q, rt.i(1664525), 3), rt.i(1013904223), 3)
        q = rt.assign_swizzle(q, "x", rt.binary("+", rt.swizzle(q, "x"), rt.binary("*", rt.swizzle(q, "y"), rt.swizzle(q, "z"), 1), 1))
        q = rt.assign_swizzle(q, "y", rt.binary("+", rt.swizzle(q, "y"), rt.binary("*", rt.swizzle(q, "z"), rt.swizzle(q, "x"), 1), 1))
        q = rt.assign_swizzle(q, "z", rt.binary("+", rt.swizzle(q, "z"), rt.binary("*", rt.swizzle(q, "x"), rt.swizzle(q, "y"), 1), 1))
        q = rt.binary("^", q, rt.binary(">>", q, rt.i(16), 3), 3)
        q = rt.assign_swizzle(q, "x", rt.binary("+", rt.swizzle(q, "x"), rt.binary("*", rt.swizzle(q, "y"), rt.swizzle(q, "z"), 1), 1))
        q = rt.assign_swizzle(q, "y", rt.binary("+", rt.swizzle(q, "y"), rt.binary("*", rt.swizzle(q, "z"), rt.swizzle(q, "x"), 1), 1))
        q = rt.assign_swizzle(q, "z", rt.binary("+", rt.swizzle(q, "z"), rt.binary("*", rt.swizzle(q, "x"), rt.swizzle(q, "y"), 1), 1))
        return rt.binary("/", rt.construct(1, rt.binary("^", rt.binary("^", rt.swizzle(q, "x"), rt.swizzle(q, "y"), 1), rt.swizzle(q, "z"), 1)), rt.f(4294967295.0), 1)
    def grad3__vec3(p):
        p = rt.copy(p)
        h1 = hash3__vec3(p)
        h2 = hash3__vec3(rt.binary("+", p, rt.f(127.1), 3))
        h3 = hash3__vec3(rt.binary("+", p, rt.f(269.5), 3))
        g = rt.construct(3, rt.binary("-", rt.binary("*", h1, rt.f(2.0), 1), rt.f(1.0), 1), rt.binary("-", rt.binary("*", h2, rt.f(2.0), 1), rt.f(1.0), 1), rt.binary("-", rt.binary("*", h3, rt.f(2.0), 1), rt.f(1.0), 1))
        return rt.normalize(g)
    def quintic__float(t):
        return rt.binary("*", rt.binary("*", rt.binary("*", t, t, 1), t, 1), rt.binary("+", rt.binary("*", t, rt.binary("-", rt.binary("*", t, rt.f(6.0), 1), rt.f(15.0), 1), 1), rt.f(10.0), 1), 1)
    def smoothlerp__float_float_float(x, a, b):
        return rt.binary("+", a, rt.binary("*", quintic__float(x), rt.binary("-", b, a, 1), 1), 1)
    def wrapZ__float(z):
        return rt.component_wise("mod", z, g.Z_PERIOD, width=1)
    def grid2D__vec2_vec2_float_float(st, cell, timeAngle, channelOffset):
        st = rt.copy(st)
        cell = rt.copy(cell)
        angle = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, rt.binary("+", cell, _u_seed, 2), rt.f(1.0))), "r"), g.TAU, 1)
        angle = rt.binary("+", angle, rt.binary("+", timeAngle, rt.binary("*", channelOffset, g.TAU, 1), 1), 1)
        gradient = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
        dist = rt.binary("-", st, cell, 2)
        return rt.dot(gradient, dist)
    def noise2D__vec2_float_float(st, timeAngle, channelOffset):
        st = rt.copy(st)
        cell = rt.component_wise("floor", st, width=2)
        f = rt.component_wise("fract", st, width=2)
        tl = grid2D__vec2_vec2_float_float(st, cell, timeAngle, channelOffset)
        tr = grid2D__vec2_vec2_float_float(st, rt.construct(2, rt.binary("+", rt.swizzle(cell, "x"), rt.f(1.0), 1), rt.swizzle(cell, "y")), timeAngle, channelOffset)
        bl = grid2D__vec2_vec2_float_float(st, rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.f(1.0), 1)), timeAngle, channelOffset)
        br = grid2D__vec2_vec2_float_float(st, rt.binary("+", cell, rt.f(1.0), 2), timeAngle, channelOffset)
        upper = smoothlerp__float_float_float(rt.swizzle(f, "x"), tl, tr)
        lower = smoothlerp__float_float_float(rt.swizzle(f, "x"), bl, br)
        val = smoothlerp__float_float_float(rt.swizzle(f, "y"), upper, lower)
        return val
    def noise3D__vec3(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=3)
        f = rt.component_wise("fract", p, width=3)
        u = rt.construct(3, quintic__float(rt.swizzle(f, "x")), quintic__float(rt.swizzle(f, "y")), quintic__float(rt.swizzle(f, "z")))
        iz0 = wrapZ__float(rt.swizzle(i, "z"))
        iz1 = wrapZ__float(rt.binary("+", rt.swizzle(i, "z"), rt.f(1.0), 1))
        n000 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz0), rt.construct(3, rt.i(0), rt.i(0), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(0), rt.i(0), rt.i(0)), 3))
        n100 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz0), rt.construct(3, rt.i(1), rt.i(0), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(1), rt.i(0), rt.i(0)), 3))
        n010 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz0), rt.construct(3, rt.i(0), rt.i(1), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(0), rt.i(1), rt.i(0)), 3))
        n110 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz0), rt.construct(3, rt.i(1), rt.i(1), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(1), rt.i(1), rt.i(0)), 3))
        n001 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz1), rt.construct(3, rt.i(0), rt.i(0), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(0), rt.i(0), rt.i(1)), 3))
        n101 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz1), rt.construct(3, rt.i(1), rt.i(0), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(1), rt.i(0), rt.i(1)), 3))
        n011 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz1), rt.construct(3, rt.i(0), rt.i(1), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(0), rt.i(1), rt.i(1)), 3))
        n111 = rt.dot(grad3__vec3(rt.binary("+", rt.construct(3, rt.swizzle(i, "xy"), iz1), rt.construct(3, rt.i(1), rt.i(1), rt.i(0)), 3)), rt.binary("-", f, rt.construct(3, rt.i(1), rt.i(1), rt.i(1)), 3))
        nx00 = rt.component_wise("mix", n000, n100, rt.swizzle(u, "x"), width=1)
        nx10 = rt.component_wise("mix", n010, n110, rt.swizzle(u, "x"), width=1)
        nx01 = rt.component_wise("mix", n001, n101, rt.swizzle(u, "x"), width=1)
        nx11 = rt.component_wise("mix", n011, n111, rt.swizzle(u, "x"), width=1)
        nxy0 = rt.component_wise("mix", nx00, nx10, rt.swizzle(u, "y"), width=1)
        nxy1 = rt.component_wise("mix", nx01, nx11, rt.swizzle(u, "y"), width=1)
        return rt.component_wise("mix", nxy0, nxy1, rt.swizzle(u, "z"), width=1)
    def fbm2D__vec2_float_float_int(st, timeAngle, channelOffset, ridgedMode):
        st = rt.copy(st)
        MAX_OCT = rt.i(8)
        amplitude = rt.f(0.5)
        frequency = rt.f(1.0)
        sum = rt.f(0.0)
        maxVal = rt.f(0.0)
        oct = _u_octaves
        if rt.binary("<", oct, rt.i(1)):
            oct = rt.i(1)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, MAX_OCT)):
                break
            if rt.binary(">=", i, oct):
                break
            n = noise2D__vec2_float_float(rt.binary("*", st, frequency, 2), timeAngle, channelOffset)
            n = rt.component_wise("clamp", rt.binary("*", n, rt.f(1.5), 1), rt.unary("-", rt.f(1.0)), rt.f(1.0), width=1)
            if rt.binary("==", ridgedMode, rt.i(1)):
                n = rt.binary("-", rt.f(1.0), rt.component_wise("abs", n, width=1), 1)
            else:
                n = rt.binary("*", rt.binary("+", n, rt.f(1.0), 1), rt.f(0.5), 1)
            sum = rt.binary("+", sum, rt.binary("*", n, amplitude, 1), 1)
            maxVal = rt.binary("+", maxVal, amplitude, 1)
            frequency = rt.binary("*", frequency, rt.f(2.0), 1)
            amplitude = rt.binary("*", amplitude, rt.f(0.5), 1)
        return rt.binary("/", sum, maxVal, 1)
    def fbm3D__vec2_float_float_int(st, timeAngle, channelOffset, ridgedMode):
        st = rt.copy(st)
        MAX_OCT = rt.i(8)
        amplitude = rt.f(0.5)
        frequency = rt.f(1.0)
        sum = rt.f(0.0)
        maxVal = rt.f(0.0)
        oct = _u_octaves
        if rt.binary("<", oct, rt.i(1)):
            oct = rt.i(1)
        z = rt.binary("+", rt.binary("*", rt.binary("/", timeAngle, g.TAU, 1), g.Z_PERIOD, 1), channelOffset, 1)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<", i, MAX_OCT)):
                break
            if rt.binary(">=", i, oct):
                break
            p = rt.construct(3, rt.binary("*", st, frequency, 2), z)
            n = noise3D__vec3(p)
            n = rt.component_wise("clamp", rt.binary("*", n, rt.f(1.5), 1), rt.unary("-", rt.f(1.0)), rt.f(1.0), width=1)
            if rt.binary("==", ridgedMode, rt.i(1)):
                n = rt.binary("-", rt.f(1.0), rt.component_wise("abs", n, width=1), 1)
            else:
                n = rt.binary("*", rt.binary("+", n, rt.f(1.0), 1), rt.f(0.5), 1)
            sum = rt.binary("+", sum, rt.binary("*", n, amplitude, 1), 1)
            maxVal = rt.binary("+", maxVal, amplitude, 1)
            frequency = rt.binary("*", frequency, rt.f(2.0), 1)
            amplitude = rt.binary("*", amplitude, rt.f(0.5), 1)
        return rt.binary("/", sum, maxVal, 1)
    def warpNoise2D__vec2_float(p, timeAngle):
        p = rt.copy(p)
        return noise2D__vec2_float_float(p, timeAngle, rt.f(0.0))
    def domainWarp2D__vec2_float_int_float_float(st, timeAngle, iterations, wScale, wIntensity):
        st = rt.copy(st)
        wFreq = rt.component_wise("max", rt.f(0.1), rt.binary("/", rt.f(100.0), rt.component_wise("max", wScale, rt.f(0.01), width=1), 1), width=1)
        disp = rt.binary("*", wIntensity, rt.f(0.02), 1)
        p = st
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            if rt.binary(">=", i, iterations):
                break
            fi = i
            nx = warpNoise2D__vec2_float(rt.binary("+", rt.binary("*", p, wFreq, 2), rt.construct(2, rt.binary("+", rt.binary("*", fi, rt.f(5.2), 1), rt.f(1.7), 1), rt.binary("+", rt.binary("*", fi, rt.f(1.3), 1), rt.f(13.7), 1)), 2), timeAngle)
            ny = warpNoise2D__vec2_float(rt.binary("+", rt.binary("*", p, wFreq, 2), rt.construct(2, rt.binary("+", rt.binary("*", fi, rt.f(2.8), 1), rt.f(7.3), 1), rt.binary("+", rt.binary("*", fi, rt.f(4.1), 1), rt.f(3.9), 1)), 2), timeAngle)
            p = rt.binary("+", p, rt.binary("*", rt.construct(2, nx, ny), disp, 2), 2)
        return p
    def warpNoise3D__vec2_float(p, z):
        p = rt.copy(p)
        return noise3D__vec3(rt.construct(3, p, z))
    def domainWarp3D__vec2_float_int_float_float(st, z, iterations, wScale, wIntensity):
        st = rt.copy(st)
        wFreq = rt.component_wise("max", rt.f(0.1), rt.binary("/", rt.f(100.0), rt.component_wise("max", wScale, rt.f(0.01), width=1), 1), width=1)
        disp = rt.binary("*", wIntensity, rt.f(0.02), 1)
        p = st
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for3_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            if rt.binary(">=", i, iterations):
                break
            fi = i
            nx = warpNoise3D__vec2_float(rt.binary("+", rt.binary("*", p, wFreq, 2), rt.construct(2, rt.binary("+", rt.binary("*", fi, rt.f(5.2), 1), rt.f(1.7), 1), rt.binary("+", rt.binary("*", fi, rt.f(1.3), 1), rt.f(13.7), 1)), 2), z)
            ny = warpNoise3D__vec2_float(rt.binary("+", rt.binary("*", p, wFreq, 2), rt.construct(2, rt.binary("+", rt.binary("*", fi, rt.f(2.8), 1), rt.f(7.3), 1), rt.binary("+", rt.binary("*", fi, rt.f(4.1), 1), rt.f(3.9), 1)), 2), z)
            p = rt.binary("+", p, rt.binary("*", rt.construct(2, nx, ny), disp, 2), 2)
        return p
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        res = _u_fullResolution
        if rt.binary("<", rt.swizzle(res, "x"), rt.f(1.0)):
            res = rt.construct(2, rt.f(1024.0), rt.f(1024.0))
        st = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), res, 2)
        st = rt.binary("-", st, rt.f(0.5), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1))
        freq = rt.component_wise("max", rt.f(0.1), rt.binary("/", rt.f(100.0), rt.component_wise("max", _u_scale, rt.f(0.01), width=1), 1), width=1)
        st = rt.binary("*", st, freq, 2)
        st = rt.binary("+", st, rt.f(1000.0), 2)
        timeAngle = rt.binary("*", rt.binary("*", _u_time, _u_speed, 1), g.TAU, 1)
        if rt.binary("==", _u_DIMENSIONS, rt.i(2)):
            if rt.binary(">", _u_warpIterations, rt.i(0)):
                st = domainWarp2D__vec2_float_int_float_float(st, timeAngle, _u_warpIterations, _u_warpScale, _u_warpIntensity)
        else:
            zWarp = rt.binary("*", rt.binary("/", timeAngle, g.TAU, 1), g.Z_PERIOD, 1)
            if rt.binary(">", _u_warpIterations, rt.i(0)):
                st = domainWarp3D__vec2_float_int_float_float(st, zWarp, _u_warpIterations, _u_warpScale, _u_warpIntensity)
        r = rt.f(0.0)
        g = rt.f(0.0)
        b = rt.f(0.0)
        if rt.binary("==", _u_DIMENSIONS, rt.i(2)):
            r = fbm2D__vec2_float_float_int(st, timeAngle, rt.f(0.0), _u_ridges)
            g = fbm2D__vec2_float_float_int(st, timeAngle, rt.f(0.333), _u_ridges)
            b = fbm2D__vec2_float_float_int(st, timeAngle, rt.f(0.667), _u_ridges)
        else:
            r = fbm3D__vec2_float_float_int(st, timeAngle, rt.f(0.0), _u_ridges)
            g = fbm3D__vec2_float_float_int(st, timeAngle, rt.f(1.33), _u_ridges)
            b = fbm3D__vec2_float_float_int(st, timeAngle, rt.f(2.67), _u_ridges)
        col = rt.construct(3, 0.0)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            col = rt.construct(3, r)
        else:
            col = rt.construct(3, r, g, b)
        g.fragColor = rt.construct(4, col, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
