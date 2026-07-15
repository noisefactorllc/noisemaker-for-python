def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_LOOP_A_OFFSET = U["LOOP_A_OFFSET"]
    _u_LOOP_B_OFFSET = U["LOOP_B_OFFSET"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_seed = U["seed"]
    _u_wrap = U["wrap"]
    _u_loopAScale = U["loopAScale"]
    _u_loopBScale = U["loopBScale"]
    _u_speedA = U["speedA"]
    _u_speedB = U["speedB"]
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def cpu_umul__int_int(left, right):
        return rt.binary("*", left, right, 1)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
    def positiveModulo__int_int(a, b):
        result = rt.binary("-", a, rt.binary("*", rt.binary("/", a, b, 1), b, 1), 1)
        if rt.binary("<", result, rt.i(0)):
            result = rt.binary("+", result, b, 1)
        return result
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)):
            p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1))
        else:
            p = rt.assign_swizzle(p, "x", rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1))
        if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)):
            p = rt.assign_swizzle(p, "y", rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1))
        else:
            p = rt.assign_swizzle(p, "y", rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1))
        if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)):
            p = rt.assign_swizzle(p, "z", rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1))
        else:
            p = rt.assign_swizzle(p, "z", rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1))
        u = pcg__vec3(cpu_uvec3__vec3(p))
        return rt.binary("/", rt.construct(3, u), rt.f(4294967295.0), 3)
    def periodicFunction__float(p):
        x = rt.binary("*", g.TAU, p, 1)
        return map__float_float_float_float_float(rt.component_wise("sin", x, width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, xyOffset):
        st = rt.copy(st)
        xyOffset = rt.copy(xyOffset)
        scaled = rt.binary("*", st, freq, 2)
        base = rt.binary("+", cpu_ivec2__vec2(rt.component_wise("floor", scaled, width=2)), xyOffset, 2)
        frac = rt.component_wise("fract", scaled, width=2)
        seedInt = _u_seed
        seedFrac = rt.f(0.0)
        xCombined = rt.binary("+", rt.swizzle(frac, "x"), seedFrac, 1)
        xi = rt.binary("+", rt.binary("+", rt.swizzle(base, "x"), seedInt, 1), rt.construct(1, rt.component_wise("floor", xCombined, width=1)), 1)
        yi = rt.swizzle(base, "y")
        if _u_wrap:
            freqInt = rt.construct(1, rt.binary("+", freq, rt.f(0.5), 1))
            if rt.binary(">", freqInt, rt.i(0)):
                xi = positiveModulo__int_int(xi, freqInt)
                yi = positiveModulo__int_int(yi, freqInt)
        xBits = rt.construct(1, xi)
        yBits = rt.construct(1, yi)
        seedBits = rt.construct(1, _u_seed)
        fracBits = rt.i(0)
        jitter = cpu_uvec3__float_float_float(rt.binary("^", cpu_umul__int_int(fracBits, rt.i(374761393)), rt.f(0x9E3779B9), 1), rt.binary("^", cpu_umul__int_int(fracBits, rt.i(668265263)), rt.i(0x7F4A7C15), 1), rt.binary("^", cpu_umul__int_int(fracBits, rt.i(2246822519)), rt.i(0x94D049B4), 1))
        state = rt.binary("^", cpu_uvec3__float_float_float(xBits, yBits, seedBits), jitter, 3)
        prngState = pcg__vec3(state)
        denom = rt.f(4294967295.0)
        return rt.construct(3, rt.binary("/", rt.swizzle(prngState, "x"), denom, 1), rt.binary("/", rt.swizzle(prngState, "y"), denom, 1), rt.binary("/", rt.swizzle(prngState, "z"), denom, 1))
    def constant__vec2_float_float(st, freq, speed):
        st = rt.copy(st)
        randTime = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, cpu_ivec2__float_float(rt.i(40), rt.i(0)))
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1)), map__float_float_float_float_float(rt.component_wise("abs", speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.33)), 1)
        rand = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, cpu_ivec2__float_float(rt.i(0), rt.i(0)))
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "y"), scaledTime, 1))
    def quadratic3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1)
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", p0, rt.f(0.5), 1), rt.binary("-", rt.f(1.0), t, 1), 1), rt.binary("-", rt.f(1.0), t, 1), 1), rt.binary("*", rt.binary("*", p1, rt.f(0.5), 1), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1), rt.binary("*", rt.f(2.0), t, 1), 1), rt.f(1.0), 1), 1), 1), rt.binary("*", rt.binary("*", p2, rt.f(0.5), 1), t2, 1), 1)
    def catmullRom3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1)
        t3 = rt.binary("*", t2, t, 1)
        return rt.binary("+", rt.binary("+", rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1), rt.binary("-", p2, p0, 1), 1), 1), rt.binary("*", rt.binary("*", rt.f(0.5), t2, 1), rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1), rt.binary("*", rt.f(5.0), p1, 1), 1), rt.binary("*", rt.f(4.0), p2, 1), 1), p0, 1), 1), 1), rt.binary("*", rt.binary("*", rt.f(0.5), t3, 1), rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", p0), rt.binary("*", rt.f(3.0), p1, 1), 1), rt.binary("*", rt.f(3.0), p2, 1), 1), p0, 1), 1), 1)
    def quadratic3x3Value__vec2_float_float(st, freq, speed):
        st = rt.copy(st)
        lattice = rt.binary("*", st, freq, 2)
        f = rt.component_wise("fract", lattice, width=2)
        nd = rt.binary("/", rt.f(1.0), freq, 1)
        v00 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.unary("-", nd)), 2), freq, speed)
        v10 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), rt.unary("-", nd)), 2), freq, speed)
        v20 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, rt.unary("-", nd)), 2), freq, speed)
        v01 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.f(0.0)), 2), freq, speed)
        v11 = constant__vec2_float_float(st, freq, speed)
        v21 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, rt.f(0.0)), 2), freq, speed)
        v02 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), nd), 2), freq, speed)
        v12 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), nd), 2), freq, speed)
        v22 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, nd), 2), freq, speed)
        y0 = quadratic3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = quadratic3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = quadratic3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return quadratic3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def catmullRom3x3Value__vec2_float_float(st, freq, speed):
        st = rt.copy(st)
        lattice = rt.binary("*", st, freq, 2)
        f = rt.component_wise("fract", lattice, width=2)
        nd = rt.binary("/", rt.f(1.0), freq, 1)
        v00 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.unary("-", nd)), 2), freq, speed)
        v10 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), rt.unary("-", nd)), 2), freq, speed)
        v20 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, rt.unary("-", nd)), 2), freq, speed)
        v01 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.f(0.0)), 2), freq, speed)
        v11 = constant__vec2_float_float(st, freq, speed)
        v21 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, rt.f(0.0)), 2), freq, speed)
        v02 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), nd), 2), freq, speed)
        v12 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), nd), 2), freq, speed)
        v22 = constant__vec2_float_float(rt.binary("+", st, rt.construct(2, nd, nd), 2), freq, speed)
        y0 = catmullRom3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = catmullRom3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = catmullRom3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return catmullRom3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def blendBicubic__float_float_float_float_float(p0, p1, p2, p3, t):
        t2 = rt.binary("*", t, t, 1)
        t3 = rt.binary("*", t2, t, 1)
        b0 = rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("-", rt.f(1.0), t, 1), rt.binary("-", rt.f(1.0), t, 1), 1), rt.binary("-", rt.f(1.0), t, 1), 1), rt.f(6.0), 1)
        b1 = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(3.0), t3, 1), rt.binary("*", rt.f(6.0), t2, 1), 1), rt.f(4.0), 1), rt.f(6.0), 1)
        b2 = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(3.0)), t3, 1), rt.binary("*", rt.f(3.0), t2, 1), 1), rt.binary("*", rt.f(3.0), t, 1), 1), rt.f(1.0), 1), rt.f(6.0), 1)
        b3 = rt.binary("/", t3, rt.f(6.0), 1)
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", p0, b0, 1), rt.binary("*", p1, b1, 1), 1), rt.binary("*", p2, b2, 1), 1), rt.binary("*", p3, b3, 1), 1)
    def catmullRom4__float_float_float_float_float(p0, p1, p2, p3, t):
        return rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1), rt.binary("+", rt.binary("-", p2, p0, 1), rt.binary("*", t, rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1), rt.binary("*", rt.f(5.0), p1, 1), 1), rt.binary("*", rt.f(4.0), p2, 1), 1), p3, 1), rt.binary("*", t, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(3.0), rt.binary("-", p1, p2, 1), 1), p3, 1), p0, 1), 1), 1), 1), 1), 1), 1)
    def blendLinearOrCosine__float_float_float_int(a, b, amount, interp):
        if rt.binary("==", interp, rt.i(1)):
            return rt.component_wise("mix", a, b, amount, width=1)
        return rt.component_wise("mix", a, b, rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), amount, width=1), width=1)
    def mod289__vec3(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 3), width=3), rt.f(289.0), 3), 3)
    def mod289__vec2(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 2), width=2), rt.f(289.0), 2), 2)
    def permute__vec3(x):
        x = rt.copy(x)
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3), rt.f(1.0), 3), x, 3))
    def simplexValue__vec2_float_float_float(st, freq, s, blend):
        st = rt.copy(st)
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        uv = rt.binary("*", st, freq, 2)
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), s, 1))
        i = rt.component_wise("floor", rt.binary("+", uv, rt.dot(uv, rt.swizzle(C, "yy")), 2), width=2)
        x0 = rt.binary("+", rt.binary("-", uv, i, 2), rt.dot(i, rt.swizzle(C, "xx")), 2)
        i1 = rt.construct(2, 0.0)
        i1 = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4)
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2))
        i = mod289__vec2(i)
        p = permute__vec3(rt.binary("+", rt.binary("+", permute__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3)), rt.swizzle(i, "x"), 3), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3))
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(3, rt.dot(x0, x0), rt.dot(rt.swizzle(x12, "xy"), rt.swizzle(x12, "xy")), rt.dot(rt.swizzle(x12, "zw"), rt.swizzle(x12, "zw"))), 3), rt.f(0.0), width=3)
        m = rt.binary("*", m, m, 3)
        m = rt.binary("*", m, m, 3)
        x = rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", p, rt.swizzle(C, "www"), 3), width=3), 3), rt.f(1.0), 3)
        h = rt.binary("-", rt.component_wise("abs", x, width=3), rt.f(0.5), 3)
        ox = rt.component_wise("floor", rt.binary("+", x, rt.f(0.5), 3), width=3)
        a0 = rt.binary("-", x, ox, 3)
        m = rt.binary("*", m, rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), rt.binary("+", rt.binary("*", a0, a0, 3), rt.binary("*", h, h, 3), 3), 3), 3), 3)
        g = rt.construct(3, 0.0)
        g = rt.assign_swizzle(g, "x", rt.binary("+", rt.binary("*", rt.swizzle(a0, "x"), rt.swizzle(x0, "x"), 1), rt.binary("*", rt.swizzle(h, "x"), rt.swizzle(x0, "y"), 1), 1))
        g = rt.assign_swizzle(g, "yz", rt.binary("+", rt.binary("*", rt.swizzle(a0, "yz"), rt.swizzle(x12, "xz"), 2), rt.binary("*", rt.swizzle(h, "yz"), rt.swizzle(x12, "yw"), 2), 2))
        v = rt.binary("*", rt.f(130.0), rt.dot(m, g), 1)
        return periodicFunction__float(rt.binary("-", map__float_float_float_float_float(v, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0)), blend, 1))
    def sineNoise__vec2_float_float_float(st, freq, s, blend):
        st = rt.copy(st)
        st = rt.binary("*", st, freq, 2)
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), s, 1))
        a = blend
        b = blend
        c = rt.binary("-", rt.f(1.0), blend, 1)
        r1 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, s)), rt.f(0.75), 3), rt.f(0.125), 3)
        r2 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, rt.binary("+", s, rt.f(10.0), 1))), rt.f(0.75), 3), rt.f(0.125), 3)
        x = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r1, "x"), rt.swizzle(st, "y"), 1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "y"), rt.swizzle(st, "x"), 1), a, 1), width=1), 1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "z"), rt.swizzle(st, "x"), 1), b, 1), width=1), 1), c, 1), width=1)
        y = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r2, "x"), rt.swizzle(st, "x"), 1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "y"), rt.swizzle(st, "y"), 1), b, 1), width=1), 1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "z"), rt.swizzle(st, "y"), 1), c, 1), width=1), 1), a, 1), width=1)
        return rt.binary("+", rt.binary("*", rt.binary("+", x, y, 1), rt.f(0.5), 1), rt.f(0.5), 1)
    def bicubicValue__vec2_float_float(st, freq, speed):
        st = rt.copy(st)
        ndX = rt.binary("/", rt.f(1.0), freq, 1)
        ndY = rt.binary("/", rt.f(1.0), freq, 1)
        u0 = rt.binary("-", rt.swizzle(st, "x"), ndX, 1)
        u1 = rt.swizzle(st, "x")
        u2 = rt.binary("+", rt.swizzle(st, "x"), ndX, 1)
        u3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "x"), ndX, 1), ndX, 1)
        v0 = rt.binary("-", rt.swizzle(st, "y"), ndY, 1)
        v1 = rt.swizzle(st, "y")
        v2 = rt.binary("+", rt.swizzle(st, "y"), ndY, 1)
        v3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "y"), ndY, 1), ndY, 1)
        x0y0 = constant__vec2_float_float(rt.construct(2, u0, v0), freq, speed)
        x0y1 = constant__vec2_float_float(rt.construct(2, u0, v1), freq, speed)
        x0y2 = constant__vec2_float_float(rt.construct(2, u0, v2), freq, speed)
        x0y3 = constant__vec2_float_float(rt.construct(2, u0, v3), freq, speed)
        x1y0 = constant__vec2_float_float(rt.construct(2, u1, v0), freq, speed)
        x1y1 = constant__vec2_float_float(st, freq, speed)
        x1y2 = constant__vec2_float_float(rt.construct(2, u1, v2), freq, speed)
        x1y3 = constant__vec2_float_float(rt.construct(2, u1, v3), freq, speed)
        x2y0 = constant__vec2_float_float(rt.construct(2, u2, v0), freq, speed)
        x2y1 = constant__vec2_float_float(rt.construct(2, u2, v1), freq, speed)
        x2y2 = constant__vec2_float_float(rt.construct(2, u2, v2), freq, speed)
        x2y3 = constant__vec2_float_float(rt.construct(2, u2, v3), freq, speed)
        x3y0 = constant__vec2_float_float(rt.construct(2, u3, v0), freq, speed)
        x3y1 = constant__vec2_float_float(rt.construct(2, u3, v1), freq, speed)
        x3y2 = constant__vec2_float_float(rt.construct(2, u3, v2), freq, speed)
        x3y3 = constant__vec2_float_float(rt.construct(2, u3, v3), freq, speed)
        uv = rt.binary("*", st, freq, 2)
        y0 = blendBicubic__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y1 = blendBicubic__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y2 = blendBicubic__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y3 = blendBicubic__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        return blendBicubic__float_float_float_float_float(y0, y1, y2, y3, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1))
    def catmullRom4x4Value__vec2_float_float(st, freq, speed):
        st = rt.copy(st)
        ndX = rt.binary("/", rt.f(1.0), freq, 1)
        ndY = rt.binary("/", rt.f(1.0), freq, 1)
        u0 = rt.binary("-", rt.swizzle(st, "x"), ndX, 1)
        u1 = rt.swizzle(st, "x")
        u2 = rt.binary("+", rt.swizzle(st, "x"), ndX, 1)
        u3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "x"), ndX, 1), ndX, 1)
        v0 = rt.binary("-", rt.swizzle(st, "y"), ndY, 1)
        v1 = rt.swizzle(st, "y")
        v2 = rt.binary("+", rt.swizzle(st, "y"), ndY, 1)
        v3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "y"), ndY, 1), ndY, 1)
        x0y0 = constant__vec2_float_float(rt.construct(2, u0, v0), freq, speed)
        x0y1 = constant__vec2_float_float(rt.construct(2, u0, v1), freq, speed)
        x0y2 = constant__vec2_float_float(rt.construct(2, u0, v2), freq, speed)
        x0y3 = constant__vec2_float_float(rt.construct(2, u0, v3), freq, speed)
        x1y0 = constant__vec2_float_float(rt.construct(2, u1, v0), freq, speed)
        x1y1 = constant__vec2_float_float(st, freq, speed)
        x1y2 = constant__vec2_float_float(rt.construct(2, u1, v2), freq, speed)
        x1y3 = constant__vec2_float_float(rt.construct(2, u1, v3), freq, speed)
        x2y0 = constant__vec2_float_float(rt.construct(2, u2, v0), freq, speed)
        x2y1 = constant__vec2_float_float(rt.construct(2, u2, v1), freq, speed)
        x2y2 = constant__vec2_float_float(rt.construct(2, u2, v2), freq, speed)
        x2y3 = constant__vec2_float_float(rt.construct(2, u2, v3), freq, speed)
        x3y0 = constant__vec2_float_float(rt.construct(2, u3, v0), freq, speed)
        x3y1 = constant__vec2_float_float(rt.construct(2, u3, v1), freq, speed)
        x3y2 = constant__vec2_float_float(rt.construct(2, u3, v2), freq, speed)
        x3y3 = constant__vec2_float_float(rt.construct(2, u3, v3), freq, speed)
        uv = rt.binary("*", st, freq, 2)
        y0 = catmullRom4__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y1 = catmullRom4__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y2 = catmullRom4__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y3 = catmullRom4__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        return catmullRom4__float_float_float_float_float(y0, y1, y2, y3, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1))
    def value__vec2_float_int_float(st, freq, interp, speed):
        st = rt.copy(st)
        if rt.binary("==", interp, rt.i(3)):
            return catmullRom3x3Value__vec2_float_float(st, freq, speed)
        else:
            if rt.binary("==", interp, rt.i(4)):
                return catmullRom4x4Value__vec2_float_float(st, freq, speed)
            else:
                if rt.binary("==", interp, rt.i(5)):
                    return quadratic3x3Value__vec2_float_float(st, freq, speed)
                else:
                    if rt.binary("==", interp, rt.i(6)):
                        return bicubicValue__vec2_float_float(st, freq, speed)
                    else:
                        if rt.binary("==", interp, rt.i(10)):
                            scaledTime = rt.binary("*", periodicFunction__float(_u_time), map__float_float_float_float_float(rt.component_wise("abs", speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1)
                            return simplexValue__vec2_float_float_float(st, freq, _u_seed, scaledTime)
                        else:
                            if rt.binary("==", interp, rt.i(11)):
                                scaledTime = rt.binary("*", periodicFunction__float(_u_time), map__float_float_float_float_float(rt.component_wise("abs", speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1)
                                return sineNoise__vec2_float_float_float(st, freq, _u_seed, scaledTime)
        x1y1 = constant__vec2_float_float(st, freq, speed)
        if rt.binary("==", interp, rt.i(0)):
            return x1y1
        ndX = rt.binary("/", rt.f(1.0), freq, 1)
        ndY = rt.binary("/", rt.f(1.0), freq, 1)
        x1y2 = constant__vec2_float_float(rt.construct(2, rt.swizzle(st, "x"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1)), freq, speed)
        x2y1 = constant__vec2_float_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1), rt.swizzle(st, "y")), freq, speed)
        x2y2 = constant__vec2_float_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1), rt.binary("+", rt.swizzle(st, "y"), ndY, 1)), freq, speed)
        uv = rt.binary("*", st, freq, 2)
        a = blendLinearOrCosine__float_float_float_int(x1y1, x2y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
        b = blendLinearOrCosine__float_float_float_int(x1y2, x2y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
        return blendLinearOrCosine__float_float_float_int(a, b, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1), interp)
    def circles__vec2_float(st, freq):
        st = rt.copy(st)
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(0.5), g.aspectRatio, 1), rt.f(0.5)), 2))
        return rt.binary("*", dist, freq, 1)
    def rings__vec2_float(st, freq):
        st = rt.copy(st)
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(0.5), g.aspectRatio, 1), rt.f(0.5)), 2))
        return rt.component_wise("cos", rt.binary("*", rt.binary("*", dist, g.PI, 1), freq, 1), width=1)
    def diamonds__vec2_float(st, freq):
        st = rt.copy(st)
        stLocal = rt.binary("/", g.globalCoord, rt.swizzle(_u_fullResolution, "y"), 2)
        stLocal = rt.binary("-", stLocal, rt.construct(2, rt.binary("*", rt.f(0.5), g.aspectRatio, 1), rt.f(0.5)), 2)
        stLocal = rt.binary("*", stLocal, freq, 2)
        return rt.binary("+", rt.component_wise("cos", rt.binary("*", rt.swizzle(stLocal, "x"), g.PI, 1), width=1), rt.component_wise("cos", rt.binary("*", rt.swizzle(stLocal, "y"), g.PI, 1), width=1), 1)
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st)
        st = rt.binary("-", rt.binary("*", st, rt.f(2.0), 2), rt.construct(2, g.aspectRatio, rt.f(1.0)), 2)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), g.PI, 1)
        r = rt.binary("/", g.TAU, sides, 1)
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1), 1), width=1), r, 1), a, 1), width=1), rt.length(st), 1), blend, 1)
    def offset__vec2_float_int_float_float(st, freq, loopOffset, speed, seedVal):
        st = rt.copy(st)
        if rt.binary("==", loopOffset, rt.i(10)):
            return circles__vec2_float(st, freq)
        else:
            if rt.binary("==", loopOffset, rt.i(20)):
                return shape__vec2_int_float(st, rt.i(3), rt.binary("*", freq, rt.f(0.5), 1))
            else:
                if rt.binary("&&", rt.binary(">=", loopOffset, rt.i(40)), rt.binary("<=", loopOffset, rt.i(120))):
                    sides = rt.binary("/", loopOffset, rt.i(10), 1)
                    return shape__vec2_int_float(st, sides, rt.binary("*", freq, rt.f(0.5), 1))
                else:
                    if rt.binary("==", loopOffset, rt.i(30)):
                        return rt.binary("*", rt.binary("*", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), rt.binary("*", rt.f(0.5), g.aspectRatio, 1), 1), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), rt.f(0.5), 1), width=1), 1), freq, 1), rt.f(0.5), 1)
                    else:
                        if rt.binary("==", loopOffset, rt.i(200)):
                            return rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), freq, 1), rt.f(0.5), 1)
                        else:
                            if rt.binary("==", loopOffset, rt.i(210)):
                                return rt.binary("*", rt.binary("*", rt.swizzle(st, "y"), freq, 1), rt.f(0.5), 1)
                            else:
                                if rt.binary("&&", rt.binary(">=", loopOffset, rt.i(300)), rt.binary("<=", loopOffset, rt.i(380))):
                                    idx = rt.binary("/", rt.binary("-", loopOffset, rt.i(300), 1), rt.i(10), 1)
                                    interp = (idx if rt.binary("<=", idx, rt.i(6)) else rt.binary("+", idx, rt.i(3), 1))
                                    f = (map__float_float_float_float_float(freq, rt.f(1.0), rt.f(6.0), rt.f(1.0), rt.f(20.0)) if rt.binary("==", loopOffset, rt.i(300)) else freq)
                                    return rt.binary("-", rt.f(1.0), value__vec2_float_int_float(rt.binary("+", st, seedVal, 2), f, interp, speed), 1)
                                else:
                                    if rt.binary("==", loopOffset, rt.i(400)):
                                        return rt.binary("-", rt.f(1.0), rings__vec2_float(st, freq), 1)
                                    else:
                                        if rt.binary("==", loopOffset, rt.i(410)):
                                            return rt.binary("-", rt.f(1.0), diamonds__vec2_float(st, freq), 1)
        return rt.f(0.0)
    def main__void():
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        g.globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", g.globalCoord, rt.swizzle(_u_fullResolution, "y"), 2)
        g.aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        lf1 = map__float_float_float_float_float(_u_loopAScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        if _u_wrap:
            lf1 = rt.component_wise("floor", lf1, width=1)
            if rt.binary("&&", rt.binary(">=", _u_LOOP_A_OFFSET, rt.i(200)), rt.binary("<", _u_LOOP_A_OFFSET, rt.i(300))):
                lf1 = rt.binary("*", lf1, rt.f(2.0), 1)
        amp1 = map__float_float_float_float_float(rt.component_wise("abs", _u_speedA, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        t1 = rt.f(1.0)
        if rt.binary("<", _u_speedA, rt.f(0.0)):
            t1 = rt.binary("+", _u_time, offset__vec2_float_int_float_float(st, lf1, _u_LOOP_A_OFFSET, amp1, _u_seed), 1)
        else:
            if rt.binary(">", _u_speedA, rt.f(0.0)):
                t1 = rt.binary("-", _u_time, offset__vec2_float_int_float_float(st, lf1, _u_LOOP_A_OFFSET, amp1, _u_seed), 1)
        lf2 = map__float_float_float_float_float(_u_loopBScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        if _u_wrap:
            lf2 = rt.component_wise("floor", lf2, width=1)
            if rt.binary("&&", rt.binary(">=", _u_LOOP_B_OFFSET, rt.i(200)), rt.binary("<", _u_LOOP_B_OFFSET, rt.i(300))):
                lf2 = rt.binary("*", lf2, rt.f(2.0), 1)
        amp2 = map__float_float_float_float_float(rt.component_wise("abs", _u_speedB, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        t2 = rt.f(1.0)
        if rt.binary("<", _u_speedB, rt.f(0.0)):
            t2 = rt.binary("+", _u_time, offset__vec2_float_int_float_float(st, lf2, _u_LOOP_B_OFFSET, amp2, rt.binary("+", _u_seed, rt.f(10.0), 1)), 1)
        else:
            if rt.binary(">", _u_speedB, rt.f(0.0)):
                t2 = rt.binary("-", _u_time, offset__vec2_float_int_float_float(st, lf2, _u_LOOP_B_OFFSET, amp2, rt.binary("+", _u_seed, rt.f(10.0), 1)), 1)
        a = rt.binary("*", periodicFunction__float(t1), amp1, 1)
        b = rt.binary("*", periodicFunction__float(t2), amp2, 1)
        d = rt.component_wise("abs", rt.binary("-", rt.binary("+", a, b, 1), rt.f(1.0), 1), width=1)
        color = rt.assign_swizzle(color, "rgb", rt.construct(3, d))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
