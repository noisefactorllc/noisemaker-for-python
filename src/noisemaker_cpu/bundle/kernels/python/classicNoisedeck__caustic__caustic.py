def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_NOISE_TYPE = U.get("NOISE_TYPE", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_wrap = U.get("wrap", False)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_noiseScale = U.get("noiseScale", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def brightnessContrast__vec3(color):
        color = rt.copy(color, "float")
        bright = map__float_float_float_float_float(_u_intensity, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.4)), rt.f(0.4))
        cont = rt.f(1.0)
        if rt.binary("<", _u_intensity, rt.f(0.0)):
            cont = map__float_float_float_float_float(_u_intensity, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.5), rt.f(1.0))
        else:
            cont = map__float_float_float_float_float(_u_intensity, rt.f(0.0), rt.f(100.0), rt.f(1.0), rt.f(1.5))
        color = rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", color, rt.f(0.5), 3, "float"), cont, 3, "float"), rt.f(0.5), 3, "float"), bright, 3, "float")
        return color
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if (bool(rt.binary("<=", rt.f(0.0), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")))):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                rgb = rt.construct(3, c, rt.f(0.0), x)
                            else:
                                rgb = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3, "float")
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def mod289__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod289__vec2(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 2, "float"), width=2), rt.f(289.0), 2, "float"), 2, "float")
    def permute__vec3(x):
        x = rt.copy(x, "float")
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3, "float"), rt.f(1.0), 3, "float"), x, 3, "float"))
    def simplexValue__vec2_float_float_float_float(st, xFreq, yFreq, s, blend):
        st = rt.copy(st, "float")
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), s, 1, "float"))
        i = rt.component_wise("floor", rt.binary("+", uv, rt.dot(uv, rt.swizzle(C, "yy")), 2, "float"), width=2)
        x0 = rt.binary("+", rt.binary("-", uv, i, 2, "float"), rt.dot(i, rt.swizzle(C, "xx")), 2, "float")
        i1 = rt.construct(2, 0.0)
        i1 = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4, "float")
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2, "float"))
        i = mod289__vec2(i)
        p = permute__vec3(rt.binary("+", rt.binary("+", permute__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3, "float")), rt.swizzle(i, "x"), 3, "float"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3, "float"))
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(3, rt.dot(x0, x0), rt.dot(rt.swizzle(x12, "xy"), rt.swizzle(x12, "xy")), rt.dot(rt.swizzle(x12, "zw"), rt.swizzle(x12, "zw"))), 3, "float"), rt.f(0.0), width=3)
        m = rt.binary("*", m, m, 3, "float")
        m = rt.binary("*", m, m, 3, "float")
        x = rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", p, rt.swizzle(C, "www"), 3, "float"), width=3), 3, "float"), rt.f(1.0), 3, "float")
        h = rt.binary("-", rt.component_wise("abs", x, width=3), rt.f(0.5), 3, "float")
        ox = rt.component_wise("floor", rt.binary("+", x, rt.f(0.5), 3, "float"), width=3)
        a0 = rt.binary("-", x, ox, 3, "float")
        m = rt.binary("*", m, rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), rt.binary("+", rt.binary("*", a0, a0, 3, "float"), rt.binary("*", h, h, 3, "float"), 3, "float"), 3, "float"), 3, "float"), 3, "float")
        _g = rt.construct(3, 0.0)
        _g = rt.assign_swizzle(_g, "x", rt.binary("+", rt.binary("*", rt.swizzle(a0, "x"), rt.swizzle(x0, "x"), 1, "float"), rt.binary("*", rt.swizzle(h, "x"), rt.swizzle(x0, "y"), 1, "float"), 1, "float"))
        _g = rt.assign_swizzle(_g, "yz", rt.binary("+", rt.binary("*", rt.swizzle(a0, "yz"), rt.swizzle(x12, "xz"), 2, "float"), rt.binary("*", rt.swizzle(h, "yz"), rt.swizzle(x12, "yw"), 2, "float"), 2, "float"))
        v = rt.binary("*", rt.f(130.0), rt.dot(m, _g), 1, "float")
        return periodicFunction__float(rt.binary("-", map__float_float_float_float_float(v, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0)), blend, 1, "float"))
    def sineNoise__vec2_float_float_float_float(st, xFreq, yFreq, s, blend):
        st = rt.copy(st, "float")
        uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), s, 1, "float"))
        a = blend
        b = blend
        c = rt.binary("-", rt.f(1.0), blend, 1, "float")
        r1 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, s, rt.f(0.0), rt.f(0.0))), rt.f(0.75), 3, "float"), rt.f(0.125), 3, "float")
        r2 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, rt.binary("+", s, rt.f(10.0), 1, "float"), rt.f(0.0), rt.f(0.0))), rt.f(0.75), 3, "float"), rt.f(0.125), 3, "float")
        x = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r1, "x"), rt.swizzle(uv, "y"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "y"), rt.swizzle(uv, "x"), 1, "float"), a, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "z"), rt.swizzle(uv, "x"), 1, "float"), b, 1, "float"), width=1), 1, "float"), c, 1, "float"), width=1)
        y = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r2, "x"), rt.swizzle(uv, "x"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "y"), rt.swizzle(uv, "y"), 1, "float"), b, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "z"), rt.swizzle(uv, "y"), 1, "float"), c, 1, "float"), width=1), 1, "float"), a, 1, "float"), width=1)
        return rt.binary("+", rt.binary("*", rt.binary("+", x, y, 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
    def positiveModulo__int_int(value, modulus):
        if rt.binary("==", modulus, rt.i(0)):
            return rt.i(0)
        r = rt.binary("%", value, modulus, 1, "int")
        return (rt.binary("+", r, modulus, 1, "int") if rt.binary("<", r, rt.i(0)) else r)
    def randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, offset):
        st = rt.copy(st, "float")
        offset = rt.copy(offset, "int")
        lattice = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        baseFloor = rt.component_wise("floor", lattice, width=2)
        base = rt.binary("+", rt.construct(2, baseFloor, base="int"), offset, 2, "int")
        frac = rt.binary("-", lattice, baseFloor, 2, "float")
        seedInt = rt.construct(1, rt.component_wise("floor", s, width=1), base="int")
        seedFrac = rt.component_wise("fract", s, width=1)
        xCombined = rt.binary("+", rt.swizzle(frac, "x"), seedFrac, 1, "float")
        xi = rt.binary("+", rt.binary("+", rt.swizzle(base, "x"), seedInt, 1, "int"), rt.construct(1, rt.component_wise("floor", xCombined, width=1), base="int"), 1, "int")
        yi = rt.swizzle(base, "y")
        if _u_wrap:
            freqXInt = rt.construct(1, rt.binary("+", xFreq, rt.f(0.5), 1, "float"), base="int")
            freqYInt = rt.construct(1, rt.binary("+", yFreq, rt.f(0.5), 1, "float"), base="int")
            if rt.binary(">", freqXInt, rt.i(0)):
                xi = positiveModulo__int_int(xi, freqXInt)
            if rt.binary(">", freqYInt, rt.i(0)):
                yi = positiveModulo__int_int(yi, freqYInt)
        xBits = rt.construct(1, xi, base="uint")
        yBits = rt.construct(1, yi, base="uint")
        seedBits = rt.construct(1, _u_seed, base="uint")
        fracBits = rt.float_bits_to_uint(seedFrac)
        jitter = rt.construct(3, rt.binary("^", rt.binary("*", fracBits, rt.i(374761393), 1, "uint"), rt.i(2654435769), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(668265263), 1, "uint"), rt.i(2135587861), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(2246822519), 1, "uint"), rt.i(2496678324), 1, "uint"), base="uint")
        state = rt.binary("^", rt.construct(3, xBits, yBits, seedBits, base="uint"), jitter, 3, "uint")
        prngState = pcg__uvec3(state)
        denom = rt.construct(1, rt.i(4294967295))
        return rt.construct(3, rt.binary("/", rt.construct(1, rt.swizzle(prngState, "x")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "y")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "z")), denom, 1, "float"))
    def constant__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        rand = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(0), base="int"))
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(rand, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.25)), 1, "float")
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "y"), scaledTime, 1, "float"))
    def constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, offset):
        st = rt.copy(st, "float")
        offset = rt.copy(offset, "int")
        rand = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, offset)
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(rand, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.25)), 1, "float")
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "y"), scaledTime, 1, "float"))
    def quadratic3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", p0, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", p1, rt.f(0.5), 1, "float"), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1, "float"), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", p2, rt.f(0.5), 1, "float"), t2, 1, "float"), 1, "float")
    def catmullRom3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("-", p2, p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t2, 1, "float"), rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t3, 1, "float"), rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", p0), rt.binary("*", rt.f(3.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float")
    def quadratic3x3Value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        lattice = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        f = rt.component_wise("fract", lattice, width=2)
        v00 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        v10 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        v20 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        v01 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        v11 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
        v21 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        v02 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        v12 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        v22 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        y0 = quadratic3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = quadratic3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = quadratic3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return quadratic3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def catmullRom3x3Value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        lattice = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        f = rt.component_wise("fract", lattice, width=2)
        v00 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        v10 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        v20 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        v01 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        v11 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
        v21 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        v02 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        v12 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        v22 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        y0 = catmullRom3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = catmullRom3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = catmullRom3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return catmullRom3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def blendBicubic__float_float_float_float_float(p0, p1, p2, p3, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        b0 = rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.f(6.0), 1, "float")
        b1 = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(3.0), t3, 1, "float"), rt.binary("*", rt.f(6.0), t2, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        b2 = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(3.0)), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), rt.f(6.0), 1, "float")
        b3 = rt.binary("/", t3, rt.f(6.0), 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", p0, b0, 1, "float"), rt.binary("*", p1, b1, 1, "float"), 1, "float"), rt.binary("*", p2, b2, 1, "float"), 1, "float"), rt.binary("*", p3, b3, 1, "float"), 1, "float")
    def catmullRom4__float_float_float_float_float(p0, p1, p2, p3, t):
        return rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("+", rt.binary("-", p2, p0, 1, "float"), rt.binary("*", t, rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p3, 1, "float"), rt.binary("*", t, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(3.0), rt.binary("-", p1, p2, 1, "float"), 1, "float"), p3, 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float")
    def blendLinearOrCosine__float_float_float_int(a, b, amount, nType):
        if rt.binary("==", nType, rt.i(1)):
            return rt.component_wise("mix", a, b, amount, width=1)
        return rt.component_wise("mix", a, b, rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), amount, width=1), width=1)
    def bicubicValue__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        f = rt.component_wise("fract", uv, width=2)
        x0y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        x0y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        x0y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        x0y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(2), base="int"))
        x1y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        x1y1 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
        x1y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        x1y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(2), base="int"))
        x2y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        x2y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        x2y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        x2y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(2), base="int"))
        x3y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.unary("-", rt.i(1)), base="int"))
        x3y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(0), base="int"))
        x3y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(1), base="int"))
        x3y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(2), base="int"))
        y0 = blendBicubic__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.swizzle(f, "x"))
        y1 = blendBicubic__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.swizzle(f, "x"))
        y2 = blendBicubic__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.swizzle(f, "x"))
        y3 = blendBicubic__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.swizzle(f, "x"))
        return rt.component_wise("clamp", blendBicubic__float_float_float_float_float(y0, y1, y2, y3, rt.swizzle(f, "y")), rt.f(0.0), rt.f(1.0), width=1)
    def catmullRom4x4Value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        f = rt.component_wise("fract", uv, width=2)
        x0y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        x0y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        x0y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        x0y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(2), base="int"))
        x1y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        x1y1 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
        x1y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        x1y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(2), base="int"))
        x2y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        x2y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        x2y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        x2y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(2), base="int"))
        x3y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.unary("-", rt.i(1)), base="int"))
        x3y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(0), base="int"))
        x3y2 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(1), base="int"))
        x3y3 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(2), rt.i(2), base="int"))
        y0 = catmullRom4__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.swizzle(f, "x"))
        y1 = catmullRom4__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.swizzle(f, "x"))
        y2 = catmullRom4__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.swizzle(f, "x"))
        y3 = catmullRom4__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.swizzle(f, "x"))
        return rt.component_wise("clamp", catmullRom4__float_float_float_float_float(y0, y1, y2, y3, rt.swizzle(f, "y")), rt.f(0.0), rt.f(1.0), width=1)
    def value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        if rt.binary("==", _u_NOISE_TYPE, rt.i(0)):
            return constant__vec2_float_float_float(st, xFreq, yFreq, s)
        else:
            if rt.binary("==", _u_NOISE_TYPE, rt.i(3)):
                return catmullRom3x3Value__vec2_float_float_float(st, xFreq, yFreq, s)
            else:
                if rt.binary("==", _u_NOISE_TYPE, rt.i(4)):
                    return catmullRom4x4Value__vec2_float_float_float(st, xFreq, yFreq, s)
                else:
                    if rt.binary("==", _u_NOISE_TYPE, rt.i(5)):
                        return quadratic3x3Value__vec2_float_float_float(st, xFreq, yFreq, s)
                    else:
                        if rt.binary("==", _u_NOISE_TYPE, rt.i(6)):
                            return bicubicValue__vec2_float_float_float(st, xFreq, yFreq, s)
                        else:
                            if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
                                scaledTime10 = rt.binary("*", rt.binary("*", simplexValue__vec2_float_float_float_float(st, xFreq, yFreq, rt.binary("+", s, rt.f(50.0), 1, "float"), _u_time), _u_speed, 1, "float"), rt.f(0.0025), 1, "float")
                                return simplexValue__vec2_float_float_float_float(st, xFreq, yFreq, s, scaledTime10)
                            else:
                                if rt.binary("==", _u_NOISE_TYPE, rt.i(11)):
                                    scaledTime11 = rt.binary("*", rt.binary("*", sineNoise__vec2_float_float_float_float(st, xFreq, yFreq, rt.binary("+", s, rt.f(50.0), 1, "float"), _u_time), _u_speed, 1, "float"), rt.f(0.0025), 1, "float")
                                    return sineNoise__vec2_float_float_float_float(st, xFreq, yFreq, s, scaledTime11)
                                else:
                                    uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
                                    f = rt.component_wise("fract", uv, width=2)
                                    x0y0 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
                                    x1y0 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(0), base="int"))
                                    x0y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(1), base="int"))
                                    x1y1 = constantOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(1), rt.i(1), base="int"))
                                    a = blendLinearOrCosine__float_float_float_int(x0y0, x1y0, rt.swizzle(f, "x"), _u_NOISE_TYPE)
                                    b = blendLinearOrCosine__float_float_float_int(x0y1, x1y1, rt.swizzle(f, "x"), _u_NOISE_TYPE)
                                    return rt.component_wise("clamp", blendLinearOrCosine__float_float_float_int(a, b, rt.swizzle(f, "y"), _u_NOISE_TYPE), rt.f(0.0), rt.f(1.0), width=1)
    def noise__vec2_float(st, s):
        st = rt.copy(st, "float")
        freq = rt.f(1.0)
        if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
            freq = map__float_float_float_float_float(_u_noiseScale, rt.f(1.0), rt.f(100.0), rt.f(1.0), rt.f(0.5))
        else:
            if _u_wrap:
                freq = rt.component_wise("floor", map__float_float_float_float_float(_u_noiseScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(2.0)), width=1)
            else:
                freq = map__float_float_float_float_float(_u_noiseScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        color = rt.construct(3, value__vec2_float_float_float(st, freq, freq, rt.binary("+", rt.f(0.0), s, 1, "float")), value__vec2_float_float_float(st, freq, freq, rt.binary("+", rt.f(10.0), s, 1, "float")), value__vec2_float_float_float(st, freq, freq, rt.binary("+", rt.f(20.0), s, 1, "float")))
        color = rt.assign_swizzle(color, "r", rt.binary("*", rt.binary("*", rt.swizzle(color, "r"), _u_hueRange, 1, "float"), rt.f(0.01), 1, "float"))
        color = rt.assign_swizzle(color, "r", rt.binary("+", rt.swizzle(color, "r"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"))
        color = rt.assign_swizzle(color, "g", rt.binary("*", rt.swizzle(color, "g"), rt.f(0.333), 1, "float"))
        color = rt.assign_swizzle(color, "b", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.swizzle(color, "b"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"))
        color = hsv2rgb__vec3(color)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        leftColor = noise__vec2_float(st, rt.construct(1, _u_seed))
        rightColor = noise__vec2_float(st, rt.binary("+", rt.construct(1, _u_seed), rt.f(10.0), 1, "float"))
        left = rt.component_wise("min", rt.binary("/", rt.binary("*", leftColor, rightColor, 3, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rightColor, leftColor, 3, "float"), 3, "float"), 3, "float"), rt.construct(3, rt.f(1.0)), width=3)
        right = rt.component_wise("min", rt.binary("/", rt.binary("*", rightColor, leftColor, 3, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", leftColor, rightColor, 3, "float"), 3, "float"), 3, "float"), rt.construct(3, rt.f(1.0)), width=3)
        color = rt.assign_swizzle(color, "rgb", brightnessContrast__vec3(rt.component_wise("mix", left, right, rt.f(0.5), width=3)))
        color = rt.assign_swizzle(color, "a", rt.f(1.0))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
