def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_METRIC = U.get("METRIC", 0)
    _u_LOOP_OFFSET = U.get("LOOP_OFFSET", 0)
    _u_DIRECTION = U.get("DIRECTION", 0)
    _u_KERNEL = U.get("KERNEL", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_wrap = U.get("wrap", False)
    _u_seed = U.get("seed", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_loopScale = U.get("loopScale", rt.f(0.0))
    _u_kaleido = U.get("kaleido", rt.f(0.0))
    _u_effectWidth = U.get("effectWidth", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.emboss = rt.new_array(rt.i(9), 1)
    g.sharpen = rt.new_array(rt.i(9), 1)
    g.blur = rt.new_array(rt.i(9), 1)
    g.edge = rt.new_array(rt.i(9), 1)
    g.edge2 = rt.new_array(rt.i(9), 1)
    def loadKernels__void():
        g.emboss[int(rt.i(0))] = rt.unary("-", rt.f(2.0))
        g.emboss[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        g.emboss[int(rt.i(2))] = rt.f(0.0)
        g.emboss[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        g.emboss[int(rt.i(4))] = rt.f(1.0)
        g.emboss[int(rt.i(5))] = rt.f(1.0)
        g.emboss[int(rt.i(6))] = rt.f(0.0)
        g.emboss[int(rt.i(7))] = rt.f(1.0)
        g.emboss[int(rt.i(8))] = rt.f(2.0)
        g.sharpen[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(1))] = rt.f(0.0)
        g.sharpen[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(3))] = rt.f(0.0)
        g.sharpen[int(rt.i(4))] = rt.f(5.0)
        g.sharpen[int(rt.i(5))] = rt.f(0.0)
        g.sharpen[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(7))] = rt.f(0.0)
        g.sharpen[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        g.blur[int(rt.i(0))] = rt.f(1.0)
        g.blur[int(rt.i(1))] = rt.f(2.0)
        g.blur[int(rt.i(2))] = rt.f(1.0)
        g.blur[int(rt.i(3))] = rt.f(2.0)
        g.blur[int(rt.i(4))] = rt.f(4.0)
        g.blur[int(rt.i(5))] = rt.f(2.0)
        g.blur[int(rt.i(6))] = rt.f(1.0)
        g.blur[int(rt.i(7))] = rt.f(2.0)
        g.blur[int(rt.i(8))] = rt.f(1.0)
        g.edge[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(4))] = rt.f(8.0)
        g.edge[int(rt.i(5))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(7))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(1))] = rt.f(0.0)
        g.edge2[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(3))] = rt.f(0.0)
        g.edge2[int(rt.i(4))] = rt.f(4.0)
        g.edge2[int(rt.i(5))] = rt.f(0.0)
        g.edge2[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(7))] = rt.f(0.0)
        g.edge2[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
    def circles__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.binary("*", dist, freq, 1, "float")
    def rings__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.component_wise("cos", rt.binary("*", rt.binary("*", dist, rt.f(3.14159265359), 1, "float"), freq, 1, "float"), width=1)
    def diamonds__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        st = rt.binary("*", st, freq, 2, "float")
        return rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.swizzle(st, "x"), rt.f(3.14159265359), 1, "float"), width=1), rt.component_wise("sin", rt.binary("*", rt.swizzle(st, "y"), rt.f(3.14159265359), 1, "float"), width=1), 1, "float")
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
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def prng2__vec2(p):
        p = rt.copy(p, "float")
        p2 = rt.construct(3, p, rt.f(0.0))
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__uvec3(rt.construct(3, p2, base="uint")), "x")), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 1, "float")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def positiveModulo__int_int(value, modulus):
        if rt.binary("==", modulus, rt.i(0)):
            return rt.i(0)
        r = rt.binary("%", value, modulus, 1, "int")
        return (rt.binary("+", r, modulus, 1, "int") if rt.binary("<", r, rt.i(0)) else r)
    def randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, offset):
        st = rt.copy(st, "float")
        offset = rt.copy(offset, "int")
        lattice = rt.binary("*", st, freq, 2, "float")
        baseFloor = rt.component_wise("floor", lattice, width=2)
        base = rt.binary("+", rt.construct(2, baseFloor, base="int"), offset, 2, "int")
        frac = rt.binary("-", lattice, baseFloor, 2, "float")
        seedInt = _u_seed
        seedFrac = rt.f(0.0)
        xCombined = rt.binary("+", rt.swizzle(frac, "x"), seedFrac, 1, "float")
        xi = rt.binary("+", rt.binary("+", rt.swizzle(base, "x"), seedInt, 1, "int"), rt.construct(1, rt.component_wise("floor", xCombined, width=1), base="int"), 1, "int")
        yi = rt.swizzle(base, "y")
        freqInt = 0
        if _u_wrap:
            freqInt = rt.construct(1, rt.binary("+", freq, rt.f(0.5), 1, "float"), base="int")
            if rt.binary(">", freqInt, rt.i(0)):
                xi = positiveModulo__int_int(xi, freqInt)
                yi = positiveModulo__int_int(yi, freqInt)
        xBits = rt.construct(1, xi, base="uint")
        yBits = rt.construct(1, yi, base="uint")
        seedBits = rt.construct(1, _u_seed, base="uint")
        fracBits = rt.float_bits_to_uint(seedFrac)
        jitter = rt.construct(3, rt.binary("^", rt.binary("*", fracBits, rt.i(374761393), 1, "uint"), rt.i(2654435769), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(668265263), 1, "uint"), rt.i(2135587861), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(2246822519), 1, "uint"), rt.i(2496678324), 1, "uint"), base="uint")
        state = rt.binary("^", rt.construct(3, xBits, yBits, seedBits, base="uint"), jitter, 3, "uint")
        prngState = pcg__uvec3(state)
        denom = rt.construct(1, rt.i(4294967295))
        return rt.construct(3, rt.binary("/", rt.construct(1, rt.swizzle(prngState, "x")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "y")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "z")), denom, 1, "float"))
    def constant__vec2_float(st, freq):
        st = rt.copy(st, "float")
        randTime = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, rt.construct(2, rt.i(40), rt.i(0), base="int"))
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1, "float")
        rand = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, rt.construct(2, rt.i(0), rt.i(0), base="int"))
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "y"), scaledTime, 1, "float"))
    def quadratic3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        B0 = rt.binary("*", rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float")
        B1 = rt.binary("*", rt.f(0.5), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1, "float"), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), 1, "float")
        B2 = rt.binary("*", rt.f(0.5), t2, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", p0, B0, 1, "float"), rt.binary("*", p1, B1, 1, "float"), 1, "float"), rt.binary("*", p2, B2, 1, "float"), 1, "float")
    def catmullRom3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("-", p2, p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t2, 1, "float"), rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t3, 1, "float"), rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", p0), rt.binary("*", rt.f(3.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float")
    def quadratic3x3Value__vec2_float(st, freq):
        st = rt.copy(st, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        f = rt.component_wise("fract", lattice, width=2)
        nd = rt.binary("/", rt.f(1.0), freq, 1, "float")
        v00 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.unary("-", nd)), 2, "float"), freq)
        v10 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), rt.unary("-", nd)), 2, "float"), freq)
        v20 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, rt.unary("-", nd)), 2, "float"), freq)
        v01 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.f(0.0)), 2, "float"), freq)
        v11 = constant__vec2_float(st, freq)
        v21 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, rt.f(0.0)), 2, "float"), freq)
        v02 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), nd), 2, "float"), freq)
        v12 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), nd), 2, "float"), freq)
        v22 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, nd), 2, "float"), freq)
        y0 = quadratic3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = quadratic3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = quadratic3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return quadratic3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def catmullRom3x3Value__vec2_float(st, freq):
        st = rt.copy(st, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        f = rt.component_wise("fract", lattice, width=2)
        nd = rt.binary("/", rt.f(1.0), freq, 1, "float")
        v00 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.unary("-", nd)), 2, "float"), freq)
        v10 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), rt.unary("-", nd)), 2, "float"), freq)
        v20 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, rt.unary("-", nd)), 2, "float"), freq)
        v01 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), rt.f(0.0)), 2, "float"), freq)
        v11 = constant__vec2_float(st, freq)
        v21 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, rt.f(0.0)), 2, "float"), freq)
        v02 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.unary("-", nd), nd), 2, "float"), freq)
        v12 = constant__vec2_float(rt.binary("+", st, rt.construct(2, rt.f(0.0), nd), 2, "float"), freq)
        v22 = constant__vec2_float(rt.binary("+", st, rt.construct(2, nd, nd), 2, "float"), freq)
        y0 = catmullRom3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = catmullRom3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = catmullRom3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return catmullRom3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def blendBicubic__float_float_float_float_float(p0, p1, p2, p3, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        B0 = rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.f(6.0), 1, "float")
        B1 = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(3.0), t3, 1, "float"), rt.binary("*", rt.f(6.0), t2, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        B2 = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(3.0)), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), rt.f(6.0), 1, "float")
        B3 = rt.binary("/", t3, rt.f(6.0), 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", p0, B0, 1, "float"), rt.binary("*", p1, B1, 1, "float"), 1, "float"), rt.binary("*", p2, B2, 1, "float"), 1, "float"), rt.binary("*", p3, B3, 1, "float"), 1, "float")
    def catmullRom4__float_float_float_float_float(p0, p1, p2, p3, t):
        return rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("+", rt.binary("-", p2, p0, 1, "float"), rt.binary("*", t, rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p3, 1, "float"), rt.binary("*", t, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(3.0), rt.binary("-", p1, p2, 1, "float"), 1, "float"), p3, 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float")
    def blendLinearOrCosine__float_float_float_int(a, b, amount, interp):
        if rt.binary("==", interp, rt.i(1)):
            return rt.component_wise("mix", a, b, amount, width=1)
        return rt.component_wise("mix", a, b, rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), amount, width=1), width=1)
    def mod289_3__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod289_2__vec2(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 2, "float"), width=2), rt.f(289.0), 2, "float"), 2, "float")
    def permute3__vec3(x):
        x = rt.copy(x, "float")
        return mod289_3__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3, "float"), rt.f(1.0), 3, "float"), x, 3, "float"))
    def simplexValue__vec2(v):
        v = rt.copy(v, "float")
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yy")), 2, "float"), width=2)
        x0 = rt.binary("+", rt.binary("-", v, i, 2, "float"), rt.dot(i, rt.swizzle(C, "xx")), 2, "float")
        i1 = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4, "float")
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2, "float"))
        i = mod289_2__vec2(i)
        p = permute3__vec3(rt.binary("+", rt.binary("+", permute3__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3, "float")), rt.swizzle(i, "x"), 3, "float"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3, "float"))
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
        return rt.binary("*", rt.f(130.0), rt.dot(m, _g), 1, "float")
    def sineNoise__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        rand = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, rt.construct(2, rt.i(20), rt.i(0), base="int"))
        waveFreq = rt.binary("*", rt.swizzle(rand, "x"), rt.f(50.0), 1, "float")
        waveAmp = rt.swizzle(rand, "y")
        wavePhase = rt.binary("*", rt.swizzle(rand, "z"), rt.f(6.28318530718), 1, "float")
        randTime = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, rt.construct(2, rt.i(40), rt.i(0), base="int"))
        phaseOffset = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1, "float")
        dist = rt.length(st)
        sineWave = rt.binary("*", rt.component_wise("sin", rt.binary("-", rt.binary("+", rt.binary("*", dist, waveFreq, 1, "float"), wavePhase, 1, "float"), phaseOffset, 1, "float"), width=1), waveAmp, 1, "float")
        return periodicFunction__float(sineWave)
    def bicubicValue__vec2_float(st, freq):
        st = rt.copy(st, "float")
        ndX = rt.binary("/", rt.f(1.0), freq, 1, "float")
        ndY = rt.binary("/", rt.f(1.0), freq, 1, "float")
        u0 = rt.binary("-", rt.swizzle(st, "x"), ndX, 1, "float")
        u1 = rt.swizzle(st, "x")
        u2 = rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float")
        u3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), ndX, 1, "float")
        v0 = rt.binary("-", rt.swizzle(st, "y"), ndY, 1, "float")
        v1 = rt.swizzle(st, "y")
        v2 = rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")
        v3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float"), ndY, 1, "float")
        x0y0 = constant__vec2_float(rt.construct(2, u0, v0), freq)
        x0y1 = constant__vec2_float(rt.construct(2, u0, v1), freq)
        x0y2 = constant__vec2_float(rt.construct(2, u0, v2), freq)
        x0y3 = constant__vec2_float(rt.construct(2, u0, v3), freq)
        x1y0 = constant__vec2_float(rt.construct(2, u1, v0), freq)
        x1y1 = constant__vec2_float(st, freq)
        x1y2 = constant__vec2_float(rt.construct(2, u1, v2), freq)
        x1y3 = constant__vec2_float(rt.construct(2, u1, v3), freq)
        x2y0 = constant__vec2_float(rt.construct(2, u2, v0), freq)
        x2y1 = constant__vec2_float(rt.construct(2, u2, v1), freq)
        x2y2 = constant__vec2_float(rt.construct(2, u2, v2), freq)
        x2y3 = constant__vec2_float(rt.construct(2, u2, v3), freq)
        x3y0 = constant__vec2_float(rt.construct(2, u3, v0), freq)
        x3y1 = constant__vec2_float(rt.construct(2, u3, v1), freq)
        x3y2 = constant__vec2_float(rt.construct(2, u3, v2), freq)
        x3y3 = constant__vec2_float(rt.construct(2, u3, v3), freq)
        uv = rt.binary("*", st, freq, 2, "float")
        y0 = blendBicubic__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y1 = blendBicubic__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y2 = blendBicubic__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y3 = blendBicubic__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        return blendBicubic__float_float_float_float_float(y0, y1, y2, y3, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1))
    def catmullRom4x4Value__vec2_float(st, freq):
        st = rt.copy(st, "float")
        ndX = rt.binary("/", rt.f(1.0), freq, 1, "float")
        ndY = rt.binary("/", rt.f(1.0), freq, 1, "float")
        u0 = rt.binary("-", rt.swizzle(st, "x"), ndX, 1, "float")
        u1 = rt.swizzle(st, "x")
        u2 = rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float")
        u3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), ndX, 1, "float")
        v0 = rt.binary("-", rt.swizzle(st, "y"), ndY, 1, "float")
        v1 = rt.swizzle(st, "y")
        v2 = rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")
        v3 = rt.binary("+", rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float"), ndY, 1, "float")
        x0y0 = constant__vec2_float(rt.construct(2, u0, v0), freq)
        x0y1 = constant__vec2_float(rt.construct(2, u0, v1), freq)
        x0y2 = constant__vec2_float(rt.construct(2, u0, v2), freq)
        x0y3 = constant__vec2_float(rt.construct(2, u0, v3), freq)
        x1y0 = constant__vec2_float(rt.construct(2, u1, v0), freq)
        x1y1 = constant__vec2_float(st, freq)
        x1y2 = constant__vec2_float(rt.construct(2, u1, v2), freq)
        x1y3 = constant__vec2_float(rt.construct(2, u1, v3), freq)
        x2y0 = constant__vec2_float(rt.construct(2, u2, v0), freq)
        x2y1 = constant__vec2_float(rt.construct(2, u2, v1), freq)
        x2y2 = constant__vec2_float(rt.construct(2, u2, v2), freq)
        x2y3 = constant__vec2_float(rt.construct(2, u2, v3), freq)
        x3y0 = constant__vec2_float(rt.construct(2, u3, v0), freq)
        x3y1 = constant__vec2_float(rt.construct(2, u3, v1), freq)
        x3y2 = constant__vec2_float(rt.construct(2, u3, v2), freq)
        x3y3 = constant__vec2_float(rt.construct(2, u3, v3), freq)
        uv = rt.binary("*", st, freq, 2, "float")
        y0 = catmullRom4__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y1 = catmullRom4__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y2 = catmullRom4__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        y3 = catmullRom4__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1))
        return catmullRom4__float_float_float_float_float(y0, y1, y2, y3, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1))
    def value__vec2_float_int(st, freq, interp):
        st = rt.copy(st, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        simplexVal = rt.f(0.0)
        if rt.binary("==", interp, rt.i(3)):
            return catmullRom3x3Value__vec2_float(st, freq)
        else:
            if rt.binary("==", interp, rt.i(4)):
                return catmullRom4x4Value__vec2_float(st, freq)
            else:
                if rt.binary("==", interp, rt.i(5)):
                    return quadratic3x3Value__vec2_float(st, freq)
                else:
                    if rt.binary("==", interp, rt.i(6)):
                        return bicubicValue__vec2_float(st, freq)
                    else:
                        if rt.binary("==", interp, rt.i(10)):
                            simplexVal = simplexValue__vec2(rt.binary("+", rt.binary("*", st, freq, 2, "float"), rt.construct(2, rt.construct(1, _u_seed)), 2, "float"))
                            return periodicFunction__float(simplexVal)
                        else:
                            if rt.binary("==", interp, rt.i(11)):
                                return sineNoise__vec2_float(st, freq)
        x1y1 = constant__vec2_float(st, freq)
        if rt.binary("==", interp, rt.i(0)):
            return x1y1
        ndX = rt.binary("/", rt.f(1.0), freq, 1, "float")
        ndY = rt.binary("/", rt.f(1.0), freq, 1, "float")
        x1y2 = constant__vec2_float(rt.construct(2, rt.swizzle(st, "x"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), freq)
        x2y1 = constant__vec2_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.swizzle(st, "y")), freq)
        x2y2 = constant__vec2_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), freq)
        uv = rt.binary("*", st, freq, 2, "float")
        a = blendLinearOrCosine__float_float_float_int(x1y1, x2y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
        b = blendLinearOrCosine__float_float_float_int(x1y2, x2y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
        return blendLinearOrCosine__float_float_float_int(a, b, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1), interp)
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
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = rt.swizzle(rgb, "r")
        _g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        max = rt.component_wise("max", r, rt.component_wise("max", _g, b, width=1), width=1)
        min = rt.component_wise("min", r, rt.component_wise("min", _g, b, width=1), width=1)
        delta = rt.binary("-", max, min, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", _g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", max, _g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, _g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", max, rt.f(0.0)) else rt.binary("/", delta, max, 1, "float"))
        v = max
        return rt.construct(3, h, s, v)
    def convolve__vec2_float_bool(uv, kernel, divide):
        uv = rt.copy(uv, "float")
        steps = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        offset = rt.new_array(rt.i(9), 2)
        offset[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(2))] = rt.construct(2, rt.swizzle(steps, "x"), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.f(0.0))
        offset[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offset[int(rt.i(5))] = rt.construct(2, rt.swizzle(steps, "x"), rt.f(0.0))
        offset[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.swizzle(steps, "y"))
        offset[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(steps, "y"))
        offset[int(rt.i(8))] = rt.construct(2, rt.swizzle(steps, "x"), rt.swizzle(steps, "y"))
        kernelWeight = rt.f(0.0)
        conv = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            color = rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", offset[int(i)], _u_effectWidth, 2, "float"), 2, "float")), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", color, kernel[int(i)], 3, "float"), 3, "float")
            kernelWeight = rt.binary("+", kernelWeight, kernel[int(i)], 1, "float")
        if divide:
            conv = rt.assign_swizzle(conv, "rgb", rt.binary("/", rt.swizzle(conv, "rgb"), kernelWeight, 3, "float"))
        return rt.component_wise("clamp", rt.swizzle(conv, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
    def desaturate__vec3(color):
        color = rt.copy(color, "float")
        avg = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
        return rt.construct(3, avg)
    def derivatives__vec3_vec2_bool(color, uv, divide):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        deriv_x = rt.new_array(rt.i(9), 1)
        deriv_x[int(rt.i(0))] = rt.f(0.0)
        deriv_x[int(rt.i(1))] = rt.f(0.0)
        deriv_x[int(rt.i(2))] = rt.f(0.0)
        deriv_x[int(rt.i(3))] = rt.f(0.0)
        deriv_x[int(rt.i(4))] = rt.f(1.0)
        deriv_x[int(rt.i(5))] = rt.unary("-", rt.f(1.0))
        deriv_x[int(rt.i(6))] = rt.f(0.0)
        deriv_x[int(rt.i(7))] = rt.f(0.0)
        deriv_x[int(rt.i(8))] = rt.f(0.0)
        deriv_y = rt.new_array(rt.i(9), 1)
        deriv_y[int(rt.i(0))] = rt.f(0.0)
        deriv_y[int(rt.i(1))] = rt.f(0.0)
        deriv_y[int(rt.i(2))] = rt.f(0.0)
        deriv_y[int(rt.i(3))] = rt.f(0.0)
        deriv_y[int(rt.i(4))] = rt.f(1.0)
        deriv_y[int(rt.i(5))] = rt.f(0.0)
        deriv_y[int(rt.i(6))] = rt.f(0.0)
        deriv_y[int(rt.i(7))] = rt.unary("-", rt.f(1.0))
        deriv_y[int(rt.i(8))] = rt.f(0.0)
        s1 = convolve__vec2_float_bool(uv, deriv_x, divide)
        s2 = convolve__vec2_float_bool(uv, deriv_y, divide)
        dist = rt.distance(s1, s2)
        color = rt.binary("*", color, dist, 3, "float")
        return color
    def sobel__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        s1 = convolve__vec2_float_bool(uv, sobel_x, False)
        s2 = convolve__vec2_float_bool(uv, sobel_y, False)
        dist = rt.distance(s1, s2)
        color = rt.binary("*", color, dist, 3, "float")
        return color
    def outline__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        s1 = convolve__vec2_float_bool(uv, sobel_x, False)
        s2 = convolve__vec2_float_bool(uv, sobel_y, False)
        dist = rt.distance(s1, s2)
        outcolor = rt.binary("-", color, dist, 3, "float")
        return rt.component_wise("max", outcolor, rt.f(0.0), width=3)
    def shadow__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        color = rgb2hsv__vec3(color)
        x = convolve__vec2_float_bool(uv, sobel_x, False)
        y = convolve__vec2_float_bool(uv, sobel_y, False)
        shade = rt.distance(x, y)
        highlight = rt.binary("*", shade, shade, 1, "float")
        shade = rt.binary("*", rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(color, "z"), 1, "float"), rt.binary("-", rt.f(1.0), highlight, 1, "float"), 1, "float"), 1, "float"), shade, 1, "float")
        alpha = rt.f(0.75)
        color = rt.construct(3, rt.swizzle(color, "x"), rt.swizzle(color, "y"), rt.component_wise("mix", rt.swizzle(color, "z"), shade, alpha, width=1))
        return hsv2rgb__vec3(color)
    def convolutionKernel__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        if rt.binary("==", _u_KERNEL, rt.i(1)):
            return convolve__vec2_float_bool(uv, g.blur, True)
        else:
            if rt.binary("==", _u_KERNEL, rt.i(2)):
                return derivatives__vec3_vec2_bool(color, uv, True)
            else:
                if rt.binary("==", _u_KERNEL, rt.i(120)):
                    return rt.component_wise("clamp", rt.binary("*", derivatives__vec3_vec2_bool(color, uv, False), rt.f(2.5), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
                else:
                    if rt.binary("==", _u_KERNEL, rt.i(3)):
                        return rt.binary("*", color, convolve__vec2_float_bool(uv, g.edge2, True), 3, "float")
                    else:
                        if rt.binary("==", _u_KERNEL, rt.i(4)):
                            return convolve__vec2_float_bool(uv, g.emboss, False)
                        else:
                            if rt.binary("==", _u_KERNEL, rt.i(5)):
                                return outline__vec3_vec2(color, uv)
                            else:
                                if rt.binary("==", _u_KERNEL, rt.i(6)):
                                    return shadow__vec3_vec2(color, uv)
                                else:
                                    if rt.binary("==", _u_KERNEL, rt.i(7)):
                                        return convolve__vec2_float_bool(uv, g.sharpen, False)
                                    else:
                                        if rt.binary("==", _u_KERNEL, rt.i(8)):
                                            return sobel__vec3_vec2(color, uv)
                                        else:
                                            return color
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st, "float")
        if rt.binary("<", sides, rt.i(2)):
            return rt.distance(st, rt.construct(2, rt.f(0.5)))
        st = rt.binary("-", rt.binary("*", rt.construct(2, rt.swizzle(st, "x"), rt.binary("-", rt.f(1.0), rt.swizzle(st, "y"), 1, "float")), rt.f(2.0), 2, "float"), rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float"), blend, 1, "float")
    def posterize__vec3_float(color, lev):
        color = rt.copy(color, "float")
        if rt.binary("==", lev, rt.f(0.0)):
            return color
        else:
            if rt.binary("==", lev, rt.f(1.0)):
                lev = rt.f(2.0)
        color = rt.component_wise("clamp", color, rt.f(0.0), rt.f(0.99), width=3)
        color = rt.binary("*", color, lev, 3, "float")
        color = rt.binary("+", rt.component_wise("floor", color, width=3), rt.f(0.5), 3, "float")
        color = rt.binary("/", color, lev, 3, "float")
        return color
    def pixellate__vec2_float(uv, size):
        uv = rt.copy(uv, "float")
        dx = rt.binary("*", size, rt.binary("/", rt.f(1.0), rt.swizzle(_u_resolution, "x"), 1, "float"), 1, "float")
        dy = rt.binary("*", size, rt.binary("/", rt.f(1.0), rt.swizzle(_u_resolution, "y"), 1, "float"), 1, "float")
        coord = rt.construct(2, rt.binary("*", dx, rt.component_wise("floor", rt.binary("/", rt.swizzle(uv, "x"), dx, 1, "float"), width=1), 1, "float"), rt.binary("*", dy, rt.component_wise("floor", rt.binary("/", rt.swizzle(uv, "y"), dy, 1, "float"), width=1), 1, "float"))
        return rt.swizzle(rt.texture(_u_inputTex, coord), "rgb")
    def getMetric__vec2(st):
        st = rt.copy(st, "float")
        diff = rt.binary("-", rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), st, 2, "float")
        if rt.binary("==", _u_METRIC, rt.i(0)):
            return rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        else:
            if rt.binary("==", _u_METRIC, rt.i(1)):
                return rt.binary("+", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), 1, "float")
            else:
                if rt.binary("==", _u_METRIC, rt.i(2)):
                    return rt.component_wise("max", rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.unary("-", rt.f(0.5)), 1, "float"), 1, "float"), rt.binary("*", rt.unary("-", rt.f(1.0)), rt.swizzle(diff, "y"), 1, "float"), width=1), rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.f(0.5), 1, "float"), 1, "float"), rt.binary("*", rt.f(1.0), rt.swizzle(diff, "y"), 1, "float"), width=1), width=1)
                else:
                    if rt.binary("==", _u_METRIC, rt.i(3)):
                        return rt.component_wise("max", rt.binary("/", rt.binary("+", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), 1, "float"), rt.component_wise("sqrt", rt.f(2.0), width=1), 1, "float"), rt.component_wise("max", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), width=1), width=1)
                    else:
                        if rt.binary("==", _u_METRIC, rt.i(4)):
                            return rt.component_wise("max", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), width=1)
                        else:
                            if rt.binary("==", _u_METRIC, rt.i(5)):
                                return rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.unary("-", rt.f(0.5)), 1, "float"), 1, "float"), rt.binary("*", rt.unary("-", rt.f(1.0)), rt.swizzle(diff, "y"), 1, "float"), width=1)
                            else:
                                return rt.f(1.0)
    def offset__vec2_float(st, freq):
        st = rt.copy(st, "float")
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(10)):
            return circles__vec2_float(st, freq)
        else:
            if rt.binary("==", _u_LOOP_OFFSET, rt.i(20)):
                return shape__vec2_int_float(st, rt.i(3), rt.binary("*", freq, rt.f(0.5), 1, "float"))
            else:
                if rt.binary("==", _u_LOOP_OFFSET, rt.i(30)):
                    return rt.binary("*", rt.binary("*", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), rt.f(0.5), 1, "float"), width=1), 1, "float"), freq, 1, "float"), rt.f(0.5), 1, "float")
                else:
                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(40)):
                        return shape__vec2_int_float(st, rt.i(4), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                    else:
                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(50)):
                            return shape__vec2_int_float(st, rt.i(5), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                        else:
                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(60)):
                                return shape__vec2_int_float(st, rt.i(6), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                            else:
                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(70)):
                                    return shape__vec2_int_float(st, rt.i(7), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                else:
                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(80)):
                                        return shape__vec2_int_float(st, rt.i(8), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(90)):
                                            return shape__vec2_int_float(st, rt.i(9), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                        else:
                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(100)):
                                                return shape__vec2_int_float(st, rt.i(10), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                            else:
                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(110)):
                                                    return shape__vec2_int_float(st, rt.i(11), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                                else:
                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(120)):
                                                        return shape__vec2_int_float(st, rt.i(12), rt.binary("*", freq, rt.f(0.5), 1, "float"))
                                                    else:
                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(200)):
                                                            return rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.f(0.5), 1, "float")
                                                        else:
                                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(210)):
                                                                return rt.binary("*", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), rt.f(0.5), 1, "float")
                                                            else:
                                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(300)):
                                                                    return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(0)), 1, "float")
                                                                else:
                                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(310)):
                                                                        return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(1)), 1, "float")
                                                                    else:
                                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(320)):
                                                                            return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(2)), 1, "float")
                                                                        else:
                                                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(330)):
                                                                                return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(3)), 1, "float")
                                                                            else:
                                                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(340)):
                                                                                    return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(4)), 1, "float")
                                                                                else:
                                                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(350)):
                                                                                        return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(5)), 1, "float")
                                                                                    else:
                                                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(360)):
                                                                                            return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(6)), 1, "float")
                                                                                        else:
                                                                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(370)):
                                                                                                return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(10)), 1, "float")
                                                                                            else:
                                                                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(380)):
                                                                                                    return rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, rt.i(11)), 1, "float")
                                                                                                else:
                                                                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(400)):
                                                                                                        return rt.binary("-", rt.f(1.0), rings__vec2_float(st, freq), 1, "float")
                                                                                                    else:
                                                                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(410)):
                                                                                                            return rt.binary("-", rt.f(1.0), diamonds__vec2_float(st, freq), 1, "float")
    def kaleidoscope__vec2_float_float(st, sides, blendy):
        st = rt.copy(st, "float")
        r = rt.binary("+", getMetric__vec2(st), blendy, 1, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        a = rt.component_wise("atan", rt.swizzle(st, "y"), rt.swizzle(st, "x"), width=1)
        dir = rt.f(0.0)
        if rt.binary("==", _u_DIRECTION, rt.i(1)):
            dir = rt.unary("-", _u_time)
        else:
            if rt.binary("==", _u_DIRECTION, rt.i(2)):
                dir = rt.f(1.0)
            else:
                dir = _u_time
        ma = rt.component_wise("mod", rt.binary("-", rt.binary("+", a, rt.component_wise("radians", rt.f(90.0), width=1), 1, "float"), rt.component_wise("radians", rt.binary("*", rt.binary("/", rt.f(360.0), sides, 1, "float"), dir, 1, "float"), width=1), 1, "float"), rt.binary("/", rt.f(6.28318530718), sides, 1, "float"), width=1)
        ma = rt.component_wise("abs", rt.binary("-", ma, rt.binary("/", rt.f(3.14159265359), sides, 1, "float"), 1, "float"), width=1)
        st = rt.binary("*", r, rt.construct(2, rt.component_wise("cos", ma, width=1), rt.component_wise("sin", ma, width=1)), 2, "float")
        st = rt.component_wise("fract", st, width=2)
        return st
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        color = rt.construct(4, rt.f(0.0))
        loadKernels__void()
        lf = map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        if _u_wrap:
            lf = rt.component_wise("floor", lf, width=1)
        t = rt.binary("+", _u_time, rt.binary("*", rt.binary("*", offset__vec2_float(uv, lf), _u_speed, 1, "float"), rt.f(0.01), 1, "float"), 1, "float")
        blendy = rt.binary("*", periodicFunction__float(t), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0)), 1, "float")
        uv = kaleidoscope__vec2_float_float(uv, _u_kaleido, blendy)
        color = rt.texture(_u_inputTex, uv)
        if rt.binary("!=", _u_KERNEL, rt.i(0)):
            if rt.binary("!=", _u_effectWidth, rt.f(0.0)):
                if rt.binary("==", _u_KERNEL, rt.i(10)):
                    color = rt.assign_swizzle(color, "rgb", pixellate__vec2_float(uv, rt.binary("*", _u_effectWidth, rt.f(4.0), 1, "float")))
                else:
                    if rt.binary("==", _u_KERNEL, rt.i(110)):
                        color = rt.assign_swizzle(color, "rgb", posterize__vec3_float(rt.swizzle(color, "rgb"), rt.component_wise("floor", map__float_float_float_float_float(_u_effectWidth, rt.f(0.0), rt.f(10.0), rt.f(0.0), rt.f(20.0)), width=1)))
                    else:
                        color = rt.assign_swizzle(color, "rgb", convolutionKernel__vec3_vec2(rt.swizzle(color, "rgb"), uv))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
