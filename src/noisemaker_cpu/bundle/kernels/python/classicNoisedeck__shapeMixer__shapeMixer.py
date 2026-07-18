def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_LOOP_OFFSET = U.get("LOOP_OFFSET", 0)
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_blendMode = U.get("blendMode", 0)
    _u_loopScale = U.get("loopScale", rt.f(0.0))
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_animate = U.get("animate", 0)
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
    _u_levels = U.get("levels", rt.f(0.0))
    _u_wrap = U.get("wrap", False)
    g.fragColor = rt.construct(4, 0.0)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
    g.invB = rt.construct(9, rt.f(0.412165612), rt.f(0.211859107), rt.f(0.0883097947), rt.f(0.536275208), rt.f(0.6807189584), rt.f(0.2818474174), rt.f(0.0514575653), rt.f(0.107406579), rt.f(0.6302613616))
    g.invA = rt.construct(9, rt.f(0.2104542553), rt.f(1.9779984951), rt.f(0.0259040371), rt.f(0.793617785), rt.unary("-", rt.f(2.428592205)), rt.f(0.7827717662), rt.unary("-", rt.f(0.0040720468)), rt.f(0.4505937099), rt.unary("-", rt.f(0.808675766)))
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
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
            rgb[:] = rt.construct(3, c, x, rt.f(0.0))
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                rgb[:] = rt.construct(3, x, c, rt.f(0.0))
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    rgb[:] = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        rgb[:] = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            rgb[:] = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                rgb[:] = rt.construct(3, c, rt.f(0.0), x)
                            else:
                                rgb[:] = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))
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
        srgb = rt.construct(3, 0.0)
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
    def oklab_from_linear_srgb__vec3(c):
        c = rt.copy(c, "float")
        lms = rt.matrix_mult(g.invB, c, 3)
        return rt.matrix_mult(g.invA, rt.binary("*", rt.component_wise("sign", lms, width=3), rt.component_wise("pow", rt.component_wise("abs", lms, width=3), rt.construct(3, rt.f(0.3333333333333)), width=3), 3, "float"), 3)
    def linear_srgb_from_oklab__vec3(c):
        c = rt.copy(c, "float")
        lms = rt.matrix_mult(g.fwdA, c, 3)
        return rt.matrix_mult(g.fwdB, rt.binary("*", rt.binary("*", lms, lms, 3, "float"), lms, 3, "float"), 3)
    def posterize__float_float(d, lev):
        if rt.binary("==", lev, rt.f(0.0)):
            return d
        else:
            if rt.binary("==", lev, rt.f(1.0)):
                lev = rt.f(2.0)
        d = rt.component_wise("clamp", d, rt.f(0.0), rt.f(0.99), width=1)
        d = rt.binary("*", d, lev, 1, "float")
        d = rt.binary("+", rt.component_wise("floor", d, width=1), rt.f(0.5), 1, "float")
        d = rt.binary("/", d, lev, 1, "float")
        return d
    def posterize2__float_float(d, lev):
        if rt.binary("==", lev, rt.f(0.0)):
            return d
        else:
            lev = rt.binary("+", lev, rt.f(0.1), 1, "float")
        return rt.binary("/", rt.component_wise("floor", rt.binary("*", d, lev, 1, "float"), width=1), lev, 1, "float")
    def posterize2__vec3_float(c, lev):
        c = rt.copy(c, "float")
        c = rt.assign_swizzle(c, "r", posterize2__float_float(rt.swizzle(c, "r"), lev))
        c = rt.assign_swizzle(c, "g", posterize2__float_float(rt.swizzle(c, "g"), lev))
        c = rt.assign_swizzle(c, "b", posterize2__float_float(rt.swizzle(c, "b"), lev))
        return c
    def isNan__float(val):
        return (False if (bool(rt.binary("<=", val, rt.f(0.0))) or bool(rt.binary("<=", rt.f(0.0), val))) else True)
    def isInf__float(val):
        return (True if (bool(rt.binary("!=", val, rt.f(0.0))) and bool(rt.binary("==", rt.binary("*", val, rt.f(2.0), 1, "float"), val))) else False)
    def pal__float(t):
        if isNan__float(t):
            return rt.construct(3, rt.f(0.0))
        else:
            if isInf__float(t):
                return rt.construct(3, rt.f(0.0))
        a = _u_paletteOffset
        b = _u_paletteAmp
        c = _u_paletteFreq
        d = _u_palettePhase
        t = rt.binary("+", rt.binary("*", t, _u_repeatPalette, 1, "float"), rt.binary("*", _u_rotatePalette, rt.f(0.01), 1, "float"), 1, "float")
        color = rt.binary("+", a, rt.binary("*", b, rt.component_wise("cos", rt.binary("*", rt.f(6.28318), rt.binary("+", rt.binary("*", c, t, 3, "float"), d, 3, "float"), 3, "float"), width=3), 3, "float"), 3, "float")
        if rt.binary("==", _u_paletteMode, rt.i(1)):
            color[:] = hsv2rgb__vec3(color)
        else:
            if rt.binary("==", _u_paletteMode, rt.i(2)):
                color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
                color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
                color[:] = linear_srgb_from_oklab__vec3(color)
                color[:] = linearToSrgb__vec3(color)
        return color
    def luminance__vec3(color):
        color = rt.copy(color, "float")
        return rt.swizzle(rgb2hsv__vec3(color), "b")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def rings__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.component_wise("cos", rt.binary("*", rt.binary("*", dist, rt.f(3.14159265359), 1, "float"), freq, 1, "float"), width=1)
    def circles__vec2_float(st, freq):
        st = rt.copy(st, "float")
        dist = rt.length(rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"))
        return rt.binary("*", dist, freq, 1, "float")
    def diamonds__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st[:] = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), rt.swizzle(_u_fullResolution, "y"), 2, "float")
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.binary("*", st, freq, 2, "float")
        return rt.binary("+", rt.component_wise("cos", rt.binary("*", rt.swizzle(st, "x"), rt.f(3.14159265359), 1, "float"), width=1), rt.component_wise("cos", rt.binary("*", rt.swizzle(st, "y"), rt.f(3.14159265359), 1, "float"), width=1), 1, "float")
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st, "float")
        st[:] = rt.binary("-", rt.binary("*", st, rt.f(2.0), 2, "float"), rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float"), blend, 1, "float")
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.swizzle(prng__vec3(rt.construct(3, st, rt.f(0.0))), "x")
    def f__vec2(st):
        st = rt.copy(st, "float")
        return random__vec2(rt.component_wise("floor", st, width=2))
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
    def simplexValue__vec2_float_float_float(st, freq, s, blend):
        st = rt.copy(st, "float")
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        uv = rt.binary("*", st, freq, 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), s, 1, "float"))
        i = rt.component_wise("floor", rt.binary("+", uv, rt.dot(uv, rt.swizzle(C, "yy")), 2, "float"), width=2)
        x0 = rt.binary("+", rt.binary("-", uv, i, 2, "float"), rt.dot(i, rt.swizzle(C, "xx")), 2, "float")
        i1 = rt.construct(2, 0.0)
        i1[:] = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4, "float")
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2, "float"))
        i[:] = mod289__vec2(i)
        p = permute__vec3(rt.binary("+", rt.binary("+", permute__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3, "float")), rt.swizzle(i, "x"), 3, "float"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3, "float"))
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(3, rt.dot(x0, x0), rt.dot(rt.swizzle(x12, "xy"), rt.swizzle(x12, "xy")), rt.dot(rt.swizzle(x12, "zw"), rt.swizzle(x12, "zw"))), 3, "float"), rt.f(0.0), width=3)
        m[:] = rt.binary("*", m, m, 3, "float")
        m[:] = rt.binary("*", m, m, 3, "float")
        x = rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", p, rt.swizzle(C, "www"), 3, "float"), width=3), 3, "float"), rt.f(1.0), 3, "float")
        h = rt.binary("-", rt.component_wise("abs", x, width=3), rt.f(0.5), 3, "float")
        ox = rt.component_wise("floor", rt.binary("+", x, rt.f(0.5), 3, "float"), width=3)
        a0 = rt.binary("-", x, ox, 3, "float")
        m[:] = rt.binary("*", m, rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), rt.binary("+", rt.binary("*", a0, a0, 3, "float"), rt.binary("*", h, h, 3, "float"), 3, "float"), 3, "float"), 3, "float"), 3, "float")
        _g = rt.construct(3, 0.0)
        _g = rt.assign_swizzle(_g, "x", rt.binary("+", rt.binary("*", rt.swizzle(a0, "x"), rt.swizzle(x0, "x"), 1, "float"), rt.binary("*", rt.swizzle(h, "x"), rt.swizzle(x0, "y"), 1, "float"), 1, "float"))
        _g = rt.assign_swizzle(_g, "yz", rt.binary("+", rt.binary("*", rt.swizzle(a0, "yz"), rt.swizzle(x12, "xz"), 2, "float"), rt.binary("*", rt.swizzle(h, "yz"), rt.swizzle(x12, "yw"), 2, "float"), 2, "float"))
        v = rt.binary("*", rt.f(130.0), rt.dot(m, _g), 1, "float")
        return periodicFunction__float(rt.binary("-", map__float_float_float_float_float(v, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0)), blend, 1, "float"))
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
        scaledTime = rt.f(1.0)
        if rt.binary("==", _u_animate, rt.unary("-", rt.i(1))):
            scaledTime = periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1, "float"))
        else:
            if rt.binary("==", _u_animate, rt.i(1)):
                scaledTime = periodicFunction__float(rt.binary("+", rt.swizzle(randTime, "x"), _u_time, 1, "float"))
        rand = randomFromLatticeWithOffset__vec2_float_ivec2(st, freq, rt.construct(2, rt.i(0), rt.i(0), base="int"))
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "x"), scaledTime, 1, "float"))
    def quadratic3__float_float_float_float(p0, p1, p2, t):
        t2 = rt.binary("*", t, t, 1, "float")
        B0 = rt.binary("*", rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float")
        B1 = rt.binary("*", rt.f(0.5), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1, "float"), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), 1, "float")
        B2 = rt.binary("*", rt.f(0.5), t2, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", p0, B0, 1, "float"), rt.binary("*", p1, B1, 1, "float"), 1, "float"), rt.binary("*", p2, B2, 1, "float"), 1, "float")
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
    def blendLinearOrCosine__float_float_float_int(a, b, amount, interp):
        if rt.binary("==", interp, rt.i(1)):
            return rt.component_wise("mix", a, b, amount, width=1)
        return rt.component_wise("mix", a, b, rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), amount, width=1), width=1)
    def value__vec2_float_int(st, freq, interp):
        st = rt.copy(st, "float")
        st2 = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        scaledTime = rt.f(1.0)
        d = rt.f(0.0)
        x1y1 = rt.f(0.0)
        if rt.binary("==", interp, rt.i(5)):
            d = quadratic3x3Value__vec2_float(st, freq)
        else:
            if rt.binary("==", interp, rt.i(10)):
                if rt.binary("==", _u_animate, rt.unary("-", rt.i(1))):
                    scaledTime = simplexValue__vec2_float_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.f(40.0), 1, "float"), _u_time)
                else:
                    if rt.binary("==", _u_animate, rt.i(1)):
                        scaledTime = simplexValue__vec2_float_float_float(st, freq, rt.binary("+", rt.construct(1, _u_seed), rt.f(40.0), 1, "float"), rt.unary("-", _u_time))
                d = simplexValue__vec2_float_float_float(st, freq, rt.construct(1, _u_seed), scaledTime)
            else:
                x1y1 = constant__vec2_float(st, freq)
                ndX = rt.f(0.0)
                ndY = rt.f(0.0)
                x1y2 = rt.f(0.0)
                x2y1 = rt.f(0.0)
                x2y2 = rt.f(0.0)
                uv = rt.construct(2, 0.0)
                a = rt.f(0.0)
                b = rt.f(0.0)
                if rt.binary("==", interp, rt.i(0)):
                    d = x1y1
                else:
                    ndX = rt.binary("/", rt.f(1.0), freq, 1, "float")
                    ndY = rt.binary("/", rt.f(1.0), freq, 1, "float")
                    x1y2 = constant__vec2_float(rt.construct(2, rt.swizzle(st, "x"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), freq)
                    x2y1 = constant__vec2_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.swizzle(st, "y")), freq)
                    x2y2 = constant__vec2_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), freq)
                    uv = rt.binary("*", st, freq, 2, "float")
                    a = blendLinearOrCosine__float_float_float_int(x1y1, x2y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
                    b = blendLinearOrCosine__float_float_float_int(x1y2, x2y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), interp)
                    d = blendLinearOrCosine__float_float_float_int(a, b, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1), interp)
        return d
    def sineNoise__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.binary("*", st, freq, 2, "float")
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        r1 = prng__vec3(rt.construct(3, rt.construct(1, _u_seed)))
        r2 = prng__vec3(rt.construct(3, rt.binary("+", rt.construct(1, _u_seed), rt.f(10.0), 1, "float")))
        scaleA = rt.binary("*", rt.swizzle(r1, "x"), rt.f(6.28318530718), 1, "float")
        scaleC = rt.binary("*", rt.swizzle(r1, "y"), rt.f(6.28318530718), 1, "float")
        scaleB = rt.binary("*", rt.swizzle(r1, "z"), rt.f(6.28318530718), 1, "float")
        scaleD = rt.binary("*", rt.swizzle(r2, "x"), rt.f(6.28318530718), 1, "float")
        offA = rt.binary("*", rt.swizzle(r2, "y"), rt.f(6.28318530718), 1, "float")
        offB = rt.binary("*", rt.swizzle(r2, "z"), rt.f(6.28318530718), 1, "float")
        return rt.binary("+", rt.binary("+", rt.component_wise("sin", rt.binary("+", rt.binary("*", scaleA, rt.swizzle(st, "x"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", scaleB, rt.swizzle(st, "y"), 1, "float"), offA, 1, "float"), width=1), 1, "float"), width=1), rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", scaleC, rt.swizzle(st, "y"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", scaleD, rt.swizzle(st, "x"), 1, "float"), offB, 1, "float"), width=1), 1, "float"), width=1), rt.f(0.5), 1, "float"), 1, "float"), rt.f(0.5), 1, "float")
    def offset__vec2_float(st, freq):
        st = rt.copy(st, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        d = rt.f(0.0)
        sides = 0
        idx = 0
        interp = 0
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(10)):
            d = circles__vec2_float(st, freq)
        else:
            if rt.binary("==", _u_LOOP_OFFSET, rt.i(20)):
                d = shape__vec2_int_float(st, rt.i(3), rt.binary("*", freq, rt.f(0.5), 1, "float"))
            else:
                if rt.binary("==", _u_LOOP_OFFSET, rt.i(30)):
                    d = rt.binary("*", rt.binary("*", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), rt.f(0.5), 1, "float"), width=1), 1, "float"), freq, 1, "float"), rt.f(0.5), 1, "float")
                else:
                    if (bool(rt.binary(">=", _u_LOOP_OFFSET, rt.i(40))) and bool(rt.binary("<=", _u_LOOP_OFFSET, rt.i(80)))):
                        sides = rt.binary("/", _u_LOOP_OFFSET, rt.i(10), 1, "int")
                        d = shape__vec2_int_float(st, sides, rt.binary("*", freq, rt.f(0.5), 1, "float"))
                    else:
                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(200)):
                            d = rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.f(0.5), 1, "float")
                        else:
                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(210)):
                                d = rt.binary("*", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), rt.f(0.5), 1, "float")
                            else:
                                if rt.binary("==", _u_LOOP_OFFSET, rt.i(380)):
                                    return rt.binary("-", rt.f(1.0), sineNoise__vec2_float(st, freq), 1, "float")
                                else:
                                    if (bool(rt.binary(">=", _u_LOOP_OFFSET, rt.i(300))) and bool(rt.binary("<=", _u_LOOP_OFFSET, rt.i(370)))):
                                        idx = rt.binary("/", rt.binary("-", _u_LOOP_OFFSET, rt.i(300), 1, "int"), rt.i(10), 1, "int")
                                        interp = (idx if rt.binary("<=", idx, rt.i(6)) else rt.binary("+", idx, rt.i(3), 1, "int"))
                                        d = rt.binary("-", rt.f(1.0), value__vec2_float_int(st, freq, interp), 1, "float")
                                    else:
                                        if rt.binary("==", _u_LOOP_OFFSET, rt.i(400)):
                                            d = rt.binary("-", rt.f(1.0), rings__vec2_float(st, freq), 1, "float")
                                        else:
                                            if rt.binary("==", _u_LOOP_OFFSET, rt.i(410)):
                                                d = rt.binary("+", rt.binary("-", rt.f(1.0), rt.binary("*", diamonds__vec2_float(st, freq), rt.f(0.5), 1, "float"), 1, "float"), rt.f(0.5), 1, "float")
        return d
    def blend__vec3_vec3_int_float(color1, color2, mode, factor):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        color = rt.construct(3, rt.f(0.0))
        factor = rt.binary("-", rt.f(1.0), factor, 1, "float")
        if rt.binary("==", mode, rt.i(0)):
            color[:] = rt.binary("+", color1, rt.binary("*", color2, factor, 3, "float"), 3, "float")
        else:
            if rt.binary("==", mode, rt.i(1)):
                color[:] = rt.binary("*", rt.binary("/", color1, color2, 3, "float"), factor, 3, "float")
            else:
                if rt.binary("==", mode, rt.i(2)):
                    color[:] = rt.component_wise("max", color1, rt.binary("*", color2, factor, 3, "float"), width=3)
                else:
                    if rt.binary("==", mode, rt.i(3)):
                        color[:] = rt.component_wise("min", color1, rt.binary("*", color2, factor, 3, "float"), width=3)
                    else:
                        if rt.binary("==", mode, rt.i(4)):
                            factor = rt.component_wise("clamp", factor, rt.f(0.0), rt.f(1.0), width=1)
                            color[:] = rt.component_wise("mix", color1, color2, factor, width=3)
                        else:
                            if rt.binary("==", mode, rt.i(5)):
                                color[:] = rt.component_wise("mod", color1, rt.binary("*", color2, factor, 3, "float"), width=3)
                            else:
                                if rt.binary("==", mode, rt.i(6)):
                                    color[:] = rt.binary("*", rt.binary("*", color1, color2, 3, "float"), factor, 3, "float")
                                else:
                                    if rt.binary("==", mode, rt.i(7)):
                                        color[:] = rt.reflect(color1, rt.binary("*", color2, factor, 3, "float"))
                                    else:
                                        if rt.binary("==", mode, rt.i(8)):
                                            color[:] = rt.refract(color1, color2, factor)
                                        else:
                                            if rt.binary("==", mode, rt.i(9)):
                                                color[:] = rt.binary("-", color1, rt.binary("*", color2, factor, 3, "float"), 3, "float")
                                            else:
                                                factor = rt.component_wise("clamp", factor, rt.f(0.0), rt.f(1.0), width=1)
                                                color[:] = rt.component_wise("mix", color1, color2, factor, width=3)
        return color
    def blend__float_float_int_float(color1, color2, mode, factor):
        color = rt.f(0.0)
        factor = rt.binary("-", rt.f(1.0), factor, 1, "float")
        if rt.binary("==", mode, rt.i(0)):
            color = rt.binary("+", color1, rt.binary("*", color2, factor, 1, "float"), 1, "float")
        else:
            if rt.binary("==", mode, rt.i(1)):
                color2 = rt.component_wise("max", rt.f(0.1), rt.binary("*", color2, factor, 1, "float"), width=1)
                color = rt.binary("/", color1, color2, 1, "float")
            else:
                if rt.binary("==", mode, rt.i(2)):
                    color = rt.component_wise("max", color1, rt.binary("*", color2, factor, 1, "float"), width=1)
                else:
                    if rt.binary("==", mode, rt.i(3)):
                        color = rt.component_wise("min", color1, rt.binary("*", color2, factor, 1, "float"), width=1)
                    else:
                        if rt.binary("==", mode, rt.i(4)):
                            factor = rt.component_wise("clamp", factor, rt.f(0.0), rt.f(1.0), width=1)
                            color = rt.component_wise("mix", color1, color2, factor, width=1)
                        else:
                            if rt.binary("==", mode, rt.i(5)):
                                color2 = rt.component_wise("max", rt.f(0.1), rt.binary("*", color2, factor, 1, "float"), width=1)
                                color = rt.component_wise("mod", color1, color2, width=1)
                            else:
                                if rt.binary("==", mode, rt.i(6)):
                                    color = rt.binary("*", rt.binary("*", color1, color2, 1, "float"), factor, 1, "float")
                                else:
                                    if rt.binary("==", mode, rt.i(7)):
                                        color = rt.reflect(color1, rt.binary("*", color2, factor, 1, "float"))
                                    else:
                                        if rt.binary("==", mode, rt.i(8)):
                                            color = rt.refract(color1, color2, factor)
                                        else:
                                            if rt.binary("==", mode, rt.i(9)):
                                                color = rt.binary("-", color1, rt.binary("*", color2, factor, 1, "float"), 1, "float")
                                            else:
                                                factor = rt.component_wise("clamp", factor, rt.f(0.0), rt.f(1.0), width=1)
                                                color = rt.component_wise("mix", color1, color2, factor, width=1)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        freq = rt.f(1.0)
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(350)):
            freq = map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(12.0), rt.f(0.5))
        else:
            freq = map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(10.0), rt.f(2.0))
        if (bool((bool(rt.binary(">=", _u_LOOP_OFFSET, rt.i(300))) and bool(rt.binary("<", _u_LOOP_OFFSET, rt.i(340))))) and bool(_u_wrap)):
            freq = rt.component_wise("floor", freq, width=1)
            freq = rt.binary("*", freq, rt.f(2.0), 1, "float")
        t = rt.f(1.0)
        if rt.binary("==", _u_animate, rt.unary("-", rt.i(1))):
            t = rt.binary("+", _u_time, offset__vec2_float(st, freq), 1, "float")
        else:
            if rt.binary("==", _u_animate, rt.i(1)):
                t = rt.binary("-", _u_time, offset__vec2_float(st, freq), 1, "float")
            else:
                t = offset__vec2_float(st, freq)
        blendy = periodicFunction__float(t)
        if rt.binary("==", _u_LOOP_OFFSET, rt.i(0)):
            blendy = rt.f(0.5)
        avg1 = luminance__vec3(rt.swizzle(color1, "rgb"))
        avg2 = luminance__vec3(rt.swizzle(color2, "rgb"))
        avgMix = blend__float_float_int_float(avg1, avg2, _u_blendMode, blendy)
        d = posterize__float_float(avgMix, _u_levels)
        if rt.binary("==", _u_paletteMode, rt.i(4)):
            color = rt.assign_swizzle(color, "rgb", blend__vec3_vec3_int_float(rt.swizzle(color1, "rgb"), rt.swizzle(color2, "rgb"), _u_blendMode, rt.binary("*", blendy, rt.f(0.5), 1, "float")))
            color = rt.assign_swizzle(color, "rgb", rgb2hsv__vec3(rt.swizzle(color, "rgb")))
            color = rt.assign_swizzle(color, "r", rt.binary("+", rt.swizzle(color, "r"), rt.binary("*", _u_rotatePalette, rt.f(0.01), 1, "float"), 1, "float"))
            if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                color = rt.assign_swizzle(color, "r", rt.component_wise("mod", rt.binary("+", rt.swizzle(color, "r"), _u_time, 1, "float"), rt.f(1.0), width=1))
            else:
                if rt.binary("==", _u_cyclePalette, rt.i(1)):
                    color = rt.assign_swizzle(color, "r", rt.component_wise("mod", rt.binary("-", rt.swizzle(color, "r"), _u_time, 1, "float"), rt.f(1.0), width=1))
            color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(rt.swizzle(color, "rgb")))
            color = rt.assign_swizzle(color, "rgb", posterize2__vec3_float(rt.swizzle(color, "rgb"), _u_levels))
        else:
            if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                color = rt.assign_swizzle(color, "rgb", pal__float(rt.binary("+", d, _u_time, 1, "float")))
            else:
                if rt.binary("==", _u_cyclePalette, rt.i(1)):
                    color = rt.assign_swizzle(color, "rgb", pal__float(rt.binary("-", d, _u_time, 1, "float")))
                else:
                    color = rt.assign_swizzle(color, "rgb", pal__float(d))
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
