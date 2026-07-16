def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_NOISE_TYPE = U.get("NOISE_TYPE", 0)
    _u_REFRACT_MODE = U.get("REFRACT_MODE", 0)
    _u_LOOP_OFFSET = U.get("LOOP_OFFSET", 0)
    _u_METRIC = U.get("METRIC", 0)
    _u_COLOR_MODE = U.get("COLOR_MODE", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_xScale = U.get("xScale", rt.f(0.0))
    _u_yScale = U.get("yScale", rt.f(0.0))
    _u_octaves = U.get("octaves", 0)
    _u_ridges = U.get("ridges", False)
    _u_refractAmt = U.get("refractAmt", rt.f(0.0))
    _u_kaleido = U.get("kaleido", rt.f(0.0))
    _u_loopScale = U.get("loopScale", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_wrap = U.get("wrap", False)
    g.fragColor = rt.construct(4, 0.0)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
    g.invB = rt.construct(9, rt.f(0.412165612), rt.f(0.211859107), rt.f(0.0883097947), rt.f(0.536275208), rt.f(0.6807189584), rt.f(0.2818474174), rt.f(0.0514575653), rt.f(0.107406579), rt.f(0.6302613616))
    g.invA = rt.construct(9, rt.f(0.2104542553), rt.f(1.9779984951), rt.f(0.0259040371), rt.f(0.793617785), rt.unary("-", rt.f(2.428592205)), rt.f(0.7827717662), rt.unary("-", rt.f(0.0040720468)), rt.f(0.4505937099), rt.unary("-", rt.f(0.808675766)))
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
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.swizzle(prng__vec3(rt.construct(3, st, rt.f(0.0))), "x")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("cos", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def positiveModulo__int_int(value, modulus):
        if rt.binary("==", modulus, rt.i(0)):
            return rt.i(0)
        r = rt.binary("%", value, modulus, 1, "int")
        return (rt.binary("+", r, modulus, 1, "int") if rt.binary("<", r, rt.i(0)) else r)
    def constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, offset):
        lattice = rt.copy(lattice, "float")
        freq = rt.copy(freq, "float")
        offset = rt.copy(offset, "int")
        baseFloor = rt.component_wise("floor", lattice, width=2)
        base = rt.binary("+", rt.construct(2, baseFloor, base="int"), offset, 2, "int")
        frac = rt.binary("-", lattice, baseFloor, 2, "float")
        seedInt = rt.construct(1, rt.component_wise("floor", s, width=1), base="int")
        sFrac = rt.component_wise("fract", s, width=1)
        xCombined = rt.binary("+", rt.swizzle(frac, "x"), sFrac, 1, "float")
        xi = rt.binary("+", rt.swizzle(base, "x"), rt.construct(1, rt.component_wise("floor", xCombined, width=1), base="int"), 1, "int")
        yi = rt.swizzle(base, "y")
        if _u_wrap:
            freqX = rt.construct(1, rt.binary("+", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"), base="int")
            freqY = rt.construct(1, rt.binary("+", rt.swizzle(freq, "y"), rt.f(0.5), 1, "float"), base="int")
            if rt.binary(">", freqX, rt.i(0)):
                xi = positiveModulo__int_int(xi, freqX)
            if rt.binary(">", freqY, rt.i(0)):
                yi = positiveModulo__int_int(yi, freqY)
        xBits = rt.construct(1, xi, base="uint")
        yBits = rt.construct(1, yi, base="uint")
        seedBits = rt.construct(1, seedInt, base="uint")
        fracBits = rt.float_bits_to_uint(sFrac)
        jitter = rt.construct(3, rt.binary("^", rt.binary("*", fracBits, rt.i(374761393), 1, "uint"), rt.i(2654435769), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(668265263), 1, "uint"), rt.i(2135587861), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(2246822519), 1, "uint"), rt.i(2496678324), 1, "uint"), base="uint")
        state = rt.binary("^", rt.construct(3, xBits, yBits, seedBits, base="uint"), jitter, 3, "uint")
        prngState = pcg__uvec3(state)
        noiseValue = rt.binary("/", rt.construct(1, rt.swizzle(prngState, "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
        return periodicFunction__float(rt.binary("-", noiseValue, blend, 1, "float"))
    def constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend):
        lattice = rt.copy(lattice, "float")
        freq = rt.copy(freq, "float")
        return constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(0), base="int"))
    def constant__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        return constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
    def cubic__float(t):
        return rt.binary("*", rt.binary("*", t, t, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), 1, "float")
    def quadratic3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", p0, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", p1, rt.f(0.5), 1, "float"), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1, "float"), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", p2, rt.f(0.5), 1, "float"), t2, 1, "float"), 1, "float")
    def latticeValue__vec2_vec2_float_float(lattice, freq, s, blend):
        lattice = rt.copy(lattice, "float")
        freq = rt.copy(freq, "float")
        return constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
    def cubic3x3ValueNoise__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        f = rt.component_wise("fract", lattice, width=2)
        v00 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        v10 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        v20 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        v01 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        v11 = constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
        v21 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        v02 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        v12 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        v22 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        y0 = quadratic3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = quadratic3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = quadratic3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return quadratic3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def blendBicubic__float_float_float_float_float(p0, p1, p2, p3, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        b0 = rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.f(6.0), 1, "float")
        b1 = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(3.0), t3, 1, "float"), rt.binary("*", rt.f(6.0), t2, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        b2 = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(3.0)), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), rt.f(6.0), 1, "float")
        b3 = rt.binary("/", t3, rt.f(6.0), 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", p0, b0, 1, "float"), rt.binary("*", p1, b1, 1, "float"), 1, "float"), rt.binary("*", p2, b2, 1, "float"), 1, "float"), rt.binary("*", p3, b3, 1, "float"), 1, "float")
    def catmullRom3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("-", p2, p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t2, 1, "float"), rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(0.5), t3, 1, "float"), rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", p0), rt.binary("*", rt.f(3.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), p2, 1, "float"), 1, "float"), p0, 1, "float"), 1, "float"), 1, "float")
    def catmullRom4__float_float_float_float_float(p0, p1, p2, p3, t):
        return rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("+", rt.binary("-", p2, p0, 1, "float"), rt.binary("*", t, rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 1, "float"), rt.binary("*", rt.f(5.0), p1, 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), p2, 1, "float"), 1, "float"), p3, 1, "float"), rt.binary("*", t, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(3.0), rt.binary("-", p1, p2, 1, "float"), 1, "float"), p3, 1, "float"), p0, 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float")
    def blendLinearOrCosine__float_float_float_int(a, b, amount, nType):
        if rt.binary("==", nType, rt.i(1)):
            return rt.component_wise("mix", a, b, amount, width=1)
        return rt.component_wise("mix", a, b, rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), amount, width=1), width=1)
    def constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, offset):
        lattice = rt.copy(lattice, "float")
        freq = rt.copy(freq, "float")
        offset = rt.copy(offset, "int")
        return constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, offset)
    def bicubicValue__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        x0y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        x0y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        x0y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        x0y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(2), base="int"))
        x1y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        x1y1 = constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
        x1y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        x1y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(2), base="int"))
        x2y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        x2y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        x2y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        x2y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(2), base="int"))
        x3y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.unary("-", rt.i(1)), base="int"))
        x3y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(0), base="int"))
        x3y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(1), base="int"))
        x3y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(2), base="int"))
        frac = rt.component_wise("fract", lattice, width=2)
        y0 = blendBicubic__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.swizzle(frac, "x"))
        y1 = blendBicubic__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.swizzle(frac, "x"))
        y2 = blendBicubic__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.swizzle(frac, "x"))
        y3 = blendBicubic__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.swizzle(frac, "x"))
        return blendBicubic__float_float_float_float_float(y0, y1, y2, y3, rt.swizzle(frac, "y"))
    def catmullRom3x3ValueNoise__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        f = rt.component_wise("fract", lattice, width=2)
        v00 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        v10 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        v20 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        v01 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        v11 = constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
        v21 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        v02 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        v12 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        v22 = constantFromLatticeWithOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        y0 = catmullRom3__float_float_float_float(v00, v10, v20, rt.swizzle(f, "x"))
        y1 = catmullRom3__float_float_float_float(v01, v11, v21, rt.swizzle(f, "x"))
        y2 = catmullRom3__float_float_float_float(v02, v12, v22, rt.swizzle(f, "x"))
        return catmullRom3__float_float_float_float(y0, y1, y2, rt.swizzle(f, "y"))
    def catmullRom4x4ValueNoise__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        lattice = rt.binary("*", st, freq, 2, "float")
        x0y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"))
        x0y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"))
        x0y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"))
        x0y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(2), base="int"))
        x1y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"))
        x1y1 = constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
        x1y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(1), base="int"))
        x1y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(2), base="int"))
        x2y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"))
        x2y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(0), base="int"))
        x2y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(1), base="int"))
        x2y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(2), base="int"))
        x3y0 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.unary("-", rt.i(1)), base="int"))
        x3y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(0), base="int"))
        x3y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(1), base="int"))
        x3y3 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(2), rt.i(2), base="int"))
        frac = rt.component_wise("fract", lattice, width=2)
        y0 = catmullRom4__float_float_float_float_float(x0y0, x1y0, x2y0, x3y0, rt.swizzle(frac, "x"))
        y1 = catmullRom4__float_float_float_float_float(x0y1, x1y1, x2y1, x3y1, rt.swizzle(frac, "x"))
        y2 = catmullRom4__float_float_float_float_float(x0y2, x1y2, x2y2, x3y2, rt.swizzle(frac, "x"))
        y3 = catmullRom4__float_float_float_float_float(x0y3, x1y3, x2y3, x3y3, rt.swizzle(frac, "x"))
        return catmullRom4__float_float_float_float_float(y0, y1, y2, y3, rt.swizzle(frac, "y"))
    def mod289__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod289__vec2(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 2, "float"), width=2), rt.f(289.0), 2, "float"), 2, "float")
    def permute__vec3(x):
        x = rt.copy(x, "float")
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3, "float"), rt.f(1.0), 3, "float"), x, 3, "float"))
    def simplexValue__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        uv = rt.binary("*", st, freq, 2, "float")
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), s, 1, "float"))
        i = rt.component_wise("floor", rt.binary("+", uv, rt.dot(uv, rt.swizzle(C, "yy")), 2, "float"), width=2)
        x0 = rt.binary("+", rt.binary("-", uv, i, 2, "float"), rt.dot(i, rt.swizzle(C, "xx")), 2, "float")
        i1 = rt.construct(2, rt.f(0.0))
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
    def sineNoise__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        st = rt.binary("*", st, freq, 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), s, 1, "float"))
        a = blend
        b = blend
        c = rt.binary("-", rt.f(1.0), blend, 1, "float")
        r1 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, s)), rt.f(0.75), 3, "float"), rt.f(0.125), 3, "float")
        r2 = rt.binary("+", rt.binary("*", prng__vec3(rt.construct(3, rt.binary("+", s, rt.f(10.0), 1, "float"))), rt.f(0.75), 3, "float"), rt.f(0.125), 3, "float")
        x = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r1, "x"), rt.swizzle(st, "y"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "y"), rt.swizzle(st, "x"), 1, "float"), a, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "z"), rt.swizzle(st, "x"), 1, "float"), b, 1, "float"), width=1), 1, "float"), c, 1, "float"), width=1)
        y = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r2, "x"), rt.swizzle(st, "x"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "y"), rt.swizzle(st, "y"), 1, "float"), b, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "z"), rt.swizzle(st, "y"), 1, "float"), c, 1, "float"), width=1), 1, "float"), a, 1, "float"), width=1)
        return rt.binary("+", rt.binary("*", rt.binary("+", x, y, 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
    def value__vec2_vec2_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        if rt.binary("==", _u_NOISE_TYPE, rt.i(3)):
            return catmullRom3x3ValueNoise__vec2_vec2_float_float(st, freq, s, blend)
        else:
            if rt.binary("==", _u_NOISE_TYPE, rt.i(4)):
                return catmullRom4x4ValueNoise__vec2_vec2_float_float(st, freq, s, blend)
            else:
                if rt.binary("==", _u_NOISE_TYPE, rt.i(5)):
                    return cubic3x3ValueNoise__vec2_vec2_float_float(st, freq, s, blend)
                else:
                    if rt.binary("==", _u_NOISE_TYPE, rt.i(6)):
                        return bicubicValue__vec2_vec2_float_float(st, freq, s, blend)
                    else:
                        if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
                            return simplexValue__vec2_vec2_float_float(st, freq, s, blend)
                        else:
                            if rt.binary("==", _u_NOISE_TYPE, rt.i(11)):
                                return sineNoise__vec2_vec2_float_float(st, freq, s, blend)
                            else:
                                if rt.binary("==", _u_NOISE_TYPE, rt.i(0)):
                                    return constantFromLattice__vec2_vec2_float_float(rt.binary("*", st, freq, 2, "float"), freq, s, blend)
                                else:
                                    lattice = rt.binary("*", st, freq, 2, "float")
                                    x1y1 = constantFromLattice__vec2_vec2_float_float(lattice, freq, s, blend)
                                    x2y1 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(0), base="int"))
                                    x1y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(0), rt.i(1), base="int"))
                                    x2y2 = constantOffset__vec2_vec2_float_float_ivec2(lattice, freq, s, blend, rt.construct(2, rt.i(1), rt.i(1), base="int"))
                                    frac = rt.component_wise("fract", lattice, width=2)
                                    a = blendLinearOrCosine__float_float_float_int(x1y1, x2y1, rt.swizzle(frac, "x"), _u_NOISE_TYPE)
                                    b = blendLinearOrCosine__float_float_float_int(x1y2, x2y2, rt.swizzle(frac, "x"), _u_NOISE_TYPE)
                                    return blendLinearOrCosine__float_float_float_int(a, b, rt.swizzle(frac, "y"), _u_NOISE_TYPE)
    def circles__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.binary("*", dist, freq, 1, "float")
    def rings__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.component_wise("cos", rt.binary("*", rt.binary("*", dist, rt.f(3.14159265359), 1, "float"), freq, 1, "float"), width=1)
    def concentric__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.component_wise("cos", rt.binary("*", rt.binary("*", dist, rt.f(3.14159265359), 1, "float"), freq, 1, "float"), width=1)
    def diamonds__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), rt.swizzle(_u_fullResolution, "y"), 2, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.binary("*", st, freq, 2, "float")
        return rt.binary("+", rt.component_wise("cos", rt.binary("*", rt.swizzle(st, "x"), rt.f(3.14159265359), 1, "float"), width=1), rt.component_wise("cos", rt.binary("*", rt.swizzle(st, "y"), rt.f(3.14159265359), 1, "float"), width=1), 1, "float")
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st, "float")
        st = rt.binary("-", rt.binary("*", st, rt.f(2.0), 2, "float"), rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float"), blend, 1, "float")
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
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        return st
    def kaleidoscope__vec2_float_float(st, sides, blendy):
        st = rt.copy(st, "float")
        if rt.binary("==", sides, rt.f(1.0)):
            return st
        r = rt.binary("+", getMetric__vec2(st), blendy, 1, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rotate2D__vec2_float(st, rt.f(0.5))
        a = rt.component_wise("atan", rt.swizzle(st, "y"), rt.swizzle(st, "x"), width=1)
        ma = rt.component_wise("mod", rt.binary("-", a, rt.component_wise("radians", rt.binary("/", rt.f(360.0), sides, 1, "float"), width=1), 1, "float"), rt.binary("/", rt.f(6.28318530718), sides, 1, "float"), width=1)
        ma = rt.component_wise("abs", rt.binary("-", ma, rt.binary("/", rt.f(3.14159265359), sides, 1, "float"), 1, "float"), width=1)
        st = rt.binary("*", r, rt.construct(2, rt.component_wise("cos", ma, width=1), rt.component_wise("sin", ma, width=1)), 2, "float")
        return st
    def offset__vec2_vec2(st, freq):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(10)):
            return circles__vec2_float(st, rt.swizzle(freq, "x"))
        else:
            if rt.binary("==", _u_LOOP_OFFSET, rt.i(20)):
                return shape__vec2_int_float(st, rt.i(3), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
            else:
                if rt.binary("==", _u_LOOP_OFFSET, rt.i(30)):
                    return rt.binary("*", rt.binary("*", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), rt.f(0.5), 1, "float"), width=1), 1, "float"), rt.swizzle(freq, "x"), 1, "float"), rt.f(0.5), 1, "float")
                else:
                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(40)):
                        return shape__vec2_int_float(st, rt.i(4), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                    else:
                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(50)):
                            return shape__vec2_int_float(st, rt.i(5), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                        else:
                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(60)):
                                return shape__vec2_int_float(st, rt.i(6), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                            else:
                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(70)):
                                    return shape__vec2_int_float(st, rt.i(7), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                else:
                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(80)):
                                        return shape__vec2_int_float(st, rt.i(8), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(90)):
                                            return shape__vec2_int_float(st, rt.i(9), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                        else:
                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(100)):
                                                return shape__vec2_int_float(st, rt.i(10), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                            else:
                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(110)):
                                                    return shape__vec2_int_float(st, rt.i(11), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                                else:
                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(120)):
                                                        return shape__vec2_int_float(st, rt.i(12), rt.binary("*", rt.swizzle(freq, "x"), rt.f(0.5), 1, "float"))
                                                    else:
                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(200)):
                                                            return rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), rt.swizzle(freq, "x"), 1, "float"), rt.f(0.5), 1, "float")
                                                        else:
                                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(210)):
                                                                return rt.binary("*", rt.binary("*", rt.swizzle(st, "y"), rt.swizzle(freq, "x"), 1, "float"), rt.f(0.5), 1, "float")
                                                            else:
                                                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(300)):
                                                                    st = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
                                                                    return value__vec2_vec2_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.f(50.0), 1, "float"), rt.f(0.0))
                                                                else:
                                                                    if rt.binary("==", _u_LOOP_OFFSET, rt.i(400)):
                                                                        return rt.binary("-", rt.f(1.0), rings__vec2_float(st, rt.swizzle(freq, "x")), 1, "float")
                                                                    else:
                                                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(410)):
                                                                            return rt.binary("-", rt.f(1.0), diamonds__vec2_float(st, rt.swizzle(freq, "x")), 1, "float")
                                                                        else:
                                                                            return rt.f(0.0)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, rt.f(0.0))
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
    def linearToSrgb__vec3(linear):
        linear = rt.copy(linear, "float")
        srgb = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", linear[int(i)], rt.f(0.0031308)):
                srgb[int(i)] = rt.binary("*", linear[int(i)], rt.f(12.92), 1, "float")
            else:
                srgb[int(i)] = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear[int(i)], rt.binary("/", rt.f(1.0), rt.f(2.4), 1, "float"), width=1), 1, "float"), rt.f(0.055), 1, "float")
        return srgb
    def srgbToLinear__vec3(srgb):
        srgb = rt.copy(srgb, "float")
        linear = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", srgb[int(i)], rt.f(0.04045)):
                linear[int(i)] = rt.binary("/", srgb[int(i)], rt.f(12.92), 1, "float")
            else:
                linear[int(i)] = rt.component_wise("pow", rt.binary("/", rt.binary("+", srgb[int(i)], rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
        return linear
    def oklab_from_linear_srgb__vec3(c):
        c = rt.copy(c, "float")
        lms = rt.matrix_mult(g.invB, c, 3)
        return rt.matrix_mult(g.invA, rt.binary("*", rt.component_wise("sign", lms, width=3), rt.component_wise("pow", rt.component_wise("abs", lms, width=3), rt.construct(3, rt.f(0.3333333333333)), width=3), 3, "float"), 3)
    def linear_srgb_from_oklab__vec3(c):
        c = rt.copy(c, "float")
        lms = rt.matrix_mult(g.fwdA, c, 3)
        return rt.matrix_mult(g.fwdB, rt.binary("*", rt.binary("*", lms, lms, 3, "float"), lms, 3, "float"), 3)
    def pal__float(t):
        a = _u_paletteOffset
        b = _u_paletteAmp
        c = _u_paletteFreq
        d = _u_palettePhase
        t = rt.binary("+", rt.binary("*", t, _u_repeatPalette, 1, "float"), rt.binary("*", _u_rotatePalette, rt.f(0.01), 1, "float"), 1, "float")
        color = rt.binary("+", a, rt.binary("*", b, rt.component_wise("cos", rt.binary("*", rt.f(6.28318), rt.binary("+", rt.binary("*", c, t, 3, "float"), d, 3, "float"), 3, "float"), width=3), 3, "float"), 3, "float")
        if rt.binary("==", _u_paletteMode, rt.i(1)):
            color = hsv2rgb__vec3(color)
        else:
            if rt.binary("==", _u_paletteMode, rt.i(2)):
                color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
                color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
                color = linear_srgb_from_oklab__vec3(color)
                color = linearToSrgb__vec3(color)
        return color
    def generate_octave__vec2_vec2_float_float_float(st, freq, s, blend, octave):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        layer = rt.construct(3, value__vec2_vec2_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.binary("*", rt.f(10.0), octave, 1, "float"), 1, "float"), blend), value__vec2_vec2_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.binary("*", rt.f(20.0), octave, 1, "float"), 1, "float"), blend), value__vec2_vec2_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.binary("*", rt.f(30.0), octave, 1, "float"), 1, "float"), blend))
        if rt.binary("==", _u_COLOR_MODE, rt.i(6)):
            if _u_ridges:
                layer = rt.assign_swizzle(layer, "b", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.swizzle(layer, "b"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"))
        return layer
    def multires__vec2_vec2_int_float_float(st, freq, octaves, s, blend):
        st = rt.copy(st, "float")
        freq = rt.copy(freq, "float")
        color = rt.construct(3, rt.f(0.0))
        multiplicand = rt.f(0.0)
        if rt.binary("==", _u_NOISE_TYPE, rt.i(11)):
            nominalBase11 = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(40.0), rt.f(1.0))
            nominalFreq = rt.construct(2, nominalBase11)
        else:
            if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
                nominalBase10 = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(0.5))
                nominalFreq = rt.construct(2, nominalBase10)
            else:
                nominalBaseV = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(3.0))
                nominalFreq = rt.construct(2, nominalBaseV)
        i = rt.i(1)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", i, octaves)):
                break
            multiplier = rt.component_wise("pow", rt.f(2.0), rt.construct(1, i), width=1)
            baseFreq = rt.binary("*", rt.binary("*", freq, rt.f(0.5), 2, "float"), multiplier, 2, "float")
            nominalBase = rt.binary("*", rt.binary("*", rt.swizzle(nominalFreq, "x"), rt.f(0.5), 1, "float"), multiplier, 1, "float")
            multiplicand = rt.binary("+", multiplicand, rt.binary("/", rt.f(1.0), multiplier, 1, "float"), 1, "float")
            if (bool(rt.binary("==", _u_REFRACT_MODE, rt.i(1))) or bool(rt.binary("==", _u_REFRACT_MODE, rt.i(2)))):
                xRefractFreq = rt.construct(2, rt.swizzle(baseFreq, "x"), nominalBase)
                yRefractFreq = rt.construct(2, nominalBase, rt.swizzle(baseFreq, "y"))
                xRef = rt.binary("-", value__vec2_vec2_float_float(st, xRefractFreq, rt.binary("+", s, rt.binary("*", rt.f(10.0), rt.construct(1, i), 1, "float"), 1, "float"), blend), rt.f(0.5), 1, "float")
                yRef = rt.binary("-", value__vec2_vec2_float_float(st, yRefractFreq, rt.binary("+", s, rt.binary("*", rt.f(20.0), rt.construct(1, i), 1, "float"), 1, "float"), blend), rt.f(0.5), 1, "float")
                ref = rt.binary("/", map__float_float_float_float_float(_u_refractAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), multiplier, 1, "float")
                st = rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", xRef, ref, 1, "float"), 1, "float"), rt.binary("+", rt.swizzle(st, "y"), rt.binary("*", yRef, ref, 1, "float"), 1, "float"))
            layer = generate_octave__vec2_vec2_float_float_float(st, baseFreq, rt.binary("+", s, rt.binary("*", rt.f(10.0), rt.construct(1, i), 1, "float"), 1, "float"), blend, rt.construct(1, i))
            if (bool(rt.binary("==", _u_REFRACT_MODE, rt.i(0))) or bool(rt.binary("==", _u_REFRACT_MODE, rt.i(2)))):
                xOff = rt.binary("+", rt.binary("*", rt.component_wise("cos", rt.swizzle(layer, "b"), width=1), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
                yOff = rt.binary("+", rt.binary("*", rt.component_wise("sin", rt.swizzle(layer, "b"), width=1), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
                ref = generate_octave__vec2_vec2_float_float_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), xOff, 1, "float"), rt.binary("+", rt.swizzle(st, "y"), yOff, 1, "float")), baseFreq, rt.binary("+", s, rt.binary("*", rt.f(15.0), rt.construct(1, i), 1, "float"), 1, "float"), blend, rt.construct(1, i))
                layer = rt.component_wise("mix", layer, ref, map__float_float_float_float_float(_u_refractAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=3)
            color = rt.assign_swizzle(color, "rgb", rt.binary("+", rt.swizzle(color, "rgb"), rt.binary("/", layer, multiplier, 3, "float"), 3, "float"))
        color = rt.assign_swizzle(color, "rgb", rt.binary("/", rt.swizzle(color, "rgb"), multiplicand, 3, "float"))
        if rt.binary("==", _u_COLOR_MODE, rt.i(0)):
            if _u_ridges:
                color = rt.assign_swizzle(color, "b", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.swizzle(color, "b"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"))
            return rt.construct(3, rt.swizzle(color, "b"))
        else:
            if rt.binary("==", _u_COLOR_MODE, rt.i(1)):
                color = srgbToLinear__vec3(color)
            else:
                if rt.binary("==", _u_COLOR_MODE, rt.i(2)):
                    pass
                else:
                    if rt.binary("==", _u_COLOR_MODE, rt.i(3)):
                        color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
                        color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
                        color = linear_srgb_from_oklab__vec3(color)
                        color = linearToSrgb__vec3(color)
                    else:
                        if rt.binary("==", _u_COLOR_MODE, rt.i(4)):
                            if _u_ridges:
                                color = rt.assign_swizzle(color, "b", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.swizzle(color, "b"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"))
                            d = rt.swizzle(color, "b")
                            if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                                d = rt.binary("+", d, _u_time, 1, "float")
                            else:
                                if rt.binary("==", _u_cyclePalette, rt.i(1)):
                                    d = rt.binary("-", d, _u_time, 1, "float")
                            color = pal__float(d)
                        else:
                            color = rt.assign_swizzle(color, "r", rt.binary("*", rt.binary("*", rt.swizzle(color, "r"), _u_hueRange, 1, "float"), rt.f(0.01), 1, "float"))
                            color = rt.assign_swizzle(color, "r", rt.binary("+", rt.swizzle(color, "r"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"))
                            color = hsv2rgb__vec3(color)
        if (bool((bool(rt.binary("!=", _u_COLOR_MODE, rt.i(4))) and bool(rt.binary("!=", _u_COLOR_MODE, rt.i(6))))) and bool(rt.binary("!=", _u_COLOR_MODE, rt.i(0)))):
            color = rgb2hsv__vec3(color)
            color = rt.assign_swizzle(color, "r", rt.binary("+", rt.swizzle(color, "r"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"))
            color = rt.assign_swizzle(color, "r", rt.component_wise("fract", rt.swizzle(color, "r"), width=1))
            if (bool((bool(rt.binary("==", _u_COLOR_MODE, rt.i(1))) or bool(rt.binary("==", _u_COLOR_MODE, rt.i(2))))) or bool(rt.binary("==", _u_COLOR_MODE, rt.i(3)))):
                if _u_ridges:
                    color = rt.assign_swizzle(color, "b", rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.swizzle(color, "b"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), 1, "float"))
            color = hsv2rgb__vec3(color)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        st = kaleidoscope__vec2_float_float(st, _u_kaleido, rt.f(0.5))
        centered = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        freq = rt.construct(2, rt.f(1.0))
        lf = rt.construct(2, rt.f(1.0))
        if rt.binary("==", _u_NOISE_TYPE, rt.i(11)):
            freq = rt.assign_swizzle(freq, "x", map__float_float_float_float_float(_u_xScale, rt.f(1.0), rt.f(100.0), rt.f(40.0), rt.f(1.0)))
            freq = rt.assign_swizzle(freq, "y", map__float_float_float_float_float(_u_yScale, rt.f(1.0), rt.f(100.0), rt.f(40.0), rt.f(1.0)))
            lf = rt.construct(2, map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(10.0), rt.f(1.0)))
        else:
            if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
                freq = rt.assign_swizzle(freq, "x", map__float_float_float_float_float(_u_xScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(0.5)))
                freq = rt.assign_swizzle(freq, "y", map__float_float_float_float_float(_u_yScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(0.5)))
                lf = rt.construct(2, map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(0.5)))
            else:
                freq = rt.assign_swizzle(freq, "x", map__float_float_float_float_float(_u_xScale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(3.0)))
                freq = rt.assign_swizzle(freq, "y", map__float_float_float_float_float(_u_yScale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(3.0)))
                lf = rt.construct(2, map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(12.0), rt.f(3.0)))
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(300)):
            if rt.binary("==", _u_NOISE_TYPE, rt.i(11)):
                baseLoop = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(40.0), rt.f(1.0))
            else:
                if rt.binary("==", _u_NOISE_TYPE, rt.i(10)):
                    baseLoop = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(0.5))
                else:
                    baseLoop = map__float_float_float_float_float(rt.f(75.0), rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(3.0))
            nominalFreq = rt.construct(2, baseLoop)
            lf = rt.binary("*", lf, rt.binary("/", freq, nominalFreq, 2, "float"), 2, "float")
        if (bool(rt.binary("!=", _u_NOISE_TYPE, rt.i(4))) and bool(rt.binary("!=", _u_NOISE_TYPE, rt.i(10)))):
            if _u_wrap:
                freq = rt.component_wise("floor", freq, width=2)
                if rt.binary("==", _u_LOOP_OFFSET, rt.i(300)):
                    lf = rt.component_wise("floor", lf, width=2)
        t = rt.f(1.0)
        if rt.binary("<", _u_speed, rt.f(0.0)):
            t = rt.binary("+", _u_time, offset__vec2_vec2(st, lf), 1, "float")
        else:
            t = rt.binary("-", _u_time, offset__vec2_vec2(st, lf), 1, "float")
        blend = rt.binary("*", rt.binary("*", periodicFunction__float(t), rt.component_wise("abs", _u_speed, width=1), 1, "float"), rt.f(0.01), 1, "float")
        color = rt.assign_swizzle(color, "rgb", multires__vec2_vec2_int_float_float(centered, freq, _u_octaves, rt.construct(1, _u_seed), blend))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
