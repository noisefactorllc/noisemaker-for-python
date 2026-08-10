def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_FORMULA = U.get("FORMULA", 0)
    _u_COLOR_SCHEME = U.get("COLOR_SCHEME", 0)
    _u_INTERP = U.get("INTERP", 0)
    _u_MASK_FORMULA = U.get("MASK_FORMULA", 0)
    _u_MASK_COLOR_SCHEME = U.get("MASK_COLOR_SCHEME", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_n = U.get("n", rt.f(0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_tiles = U.get("tiles", rt.f(0.0))
    _u_complexity = U.get("complexity", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_baseHueRange = U.get("baseHueRange", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.BIT_COUNT = rt.i(8)
    g.mask = rt.binary("-", rt.binary("<<", rt.i(1), g.BIT_COUNT, 1, "int"), rt.i(1), 1, "int")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
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
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(1.0))
        angle = rt.binary("*", rot, rt.f(6.28318530718), 1, "float")
        st[:] = rt.binary("-", st, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2, "float")
        st[:] = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st[:] = rt.binary("+", st, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2, "float")
        return st
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
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
        xBits = rt.construct(1, xi, base="uint")
        yBits = rt.construct(1, yi, base="uint")
        seedBits = rt.float_bits_to_uint(s)
        fracBits = rt.float_bits_to_uint(seedFrac)
        jitter = rt.construct(3, rt.binary("^", rt.binary("*", fracBits, rt.i(374761393), 1, "uint"), rt.i(2654435769), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(668265263), 1, "uint"), rt.i(2135587861), 1, "uint"), rt.binary("^", rt.binary("*", fracBits, rt.i(2246822519), 1, "uint"), rt.i(2496678324), 1, "uint"), base="uint")
        state = rt.binary("^", rt.construct(3, xBits, yBits, seedBits, base="uint"), jitter, 3, "uint")
        prngState = pcg__uvec3(state)
        denom = rt.construct(1, rt.i(4294967295))
        return rt.construct(3, rt.binary("/", rt.construct(1, rt.swizzle(prngState, "x")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "y")), denom, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(prngState, "z")), denom, 1, "float"))
    def constant__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        randTime = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(40), rt.i(0), base="int"))
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1, "float")
        rand = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, rt.construct(2, rt.i(0), rt.i(0), base="int"))
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "x"), scaledTime, 1, "float"))
    def value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        x1y1 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
        ndX = rt.f(0.0)
        ndY = rt.f(0.0)
        x1y2 = rt.f(0.0)
        x2y1 = rt.f(0.0)
        x2y2 = rt.f(0.0)
        uv = rt.construct(2, 0.0)
        a = rt.f(0.0)
        b = rt.f(0.0)
        if rt.binary("==", _u_INTERP, rt.i(0)):
            return x1y1
        else:
            ndX = rt.binary("/", rt.f(1.0), xFreq, 1, "float")
            ndY = rt.binary("/", rt.f(1.0), yFreq, 1, "float")
            x1y2 = constant__vec2_float_float_float(rt.construct(2, rt.swizzle(st, "x"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), xFreq, yFreq, s)
            x2y1 = constant__vec2_float_float_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.swizzle(st, "y")), xFreq, yFreq, s)
            x2y2 = constant__vec2_float_float_float(rt.construct(2, rt.binary("+", rt.swizzle(st, "x"), ndX, 1, "float"), rt.binary("+", rt.swizzle(st, "y"), ndY, 1, "float")), xFreq, yFreq, s)
            uv = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
            a = rt.component_wise("mix", x1y1, x2y1, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), width=1)
            b = rt.component_wise("mix", x1y2, x2y2, rt.component_wise("fract", rt.swizzle(uv, "x"), width=1), width=1)
            return rt.component_wise("mix", a, b, rt.component_wise("fract", rt.swizzle(uv, "y"), width=1), width=1)
    def modi__int_int(x, y):
        return rt.binary("&", rt.binary("%", x, y, 1, "int"), g.mask, 1, "int")
    def _or__int_int(a, b):
        return rt.binary("|", rt.binary("&", a, g.mask, 1, "int"), rt.binary("&", b, g.mask, 1, "int"), 1, "int")
    def _and__int_int(a, b):
        return rt.binary("&", rt.binary("&", a, g.mask, 1, "int"), rt.binary("&", b, g.mask, 1, "int"), 1, "int")
    def not2__int(a):
        return rt.binary("&", rt.binary("^", a, rt.i(4294967295), 1, "int"), g.mask, 1, "int")
    def xor__int_int(a, b):
        return rt.binary("^", rt.binary("&", a, g.mask, 1, "int"), rt.binary("&", b, g.mask, 1, "int"), 1, "int")
    def _or__float_float(a, b):
        return rt.construct(1, _or__int_int(rt.construct(1, a, base="int"), rt.construct(1, b, base="int")))
    def _and__float_float(a, b):
        return rt.construct(1, _and__int_int(rt.construct(1, a, base="int"), rt.construct(1, b, base="int")))
    def not3__float(a):
        return rt.construct(1, not2__int(rt.construct(1, a, base="int")))
    def xor__float_float(a, b):
        return rt.construct(1, xor__int_int(rt.construct(1, a, base="int"), rt.construct(1, b, base="int")))
    def bitValue__vec2_float_float(st, freq, nForColor):
        st = rt.copy(st, "float")
        blendy = rt.binary("+", nForColor, rt.binary("*", periodicFunction__float(rt.binary("*", value__vec2_float_float_float(st, rt.binary("*", freq, rt.f(0.01), 1, "float"), rt.binary("*", freq, rt.f(0.01), 1, "float"), nForColor), rt.f(0.1), 1, "float")), rt.f(100.0), 1, "float"), 1, "float")
        v = rt.f(1.0)
        if rt.binary("==", _u_FORMULA, rt.i(0)):
            v = rt.component_wise("mod", xor__float_float(rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float")), blendy, width=1)
        else:
            if rt.binary("==", _u_FORMULA, rt.i(1)):
                v = rt.component_wise("mod", _or__float_float(rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float")), blendy, width=1)
            else:
                if rt.binary("==", _u_FORMULA, rt.i(2)):
                    v = rt.component_wise("mod", rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), 1, "float"), blendy, width=1)
                else:
                    if rt.binary("==", _u_FORMULA, rt.i(3)):
                        v = rt.construct(1, rt.binary("<", xor__float_float(rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float")), blendy))
                    else:
                        if rt.binary("==", _u_FORMULA, rt.i(4)):
                            v = rt.component_wise("mod", rt.binary("*", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), blendy, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), width=1)
                        else:
                            if rt.binary("==", _u_FORMULA, rt.i(5)):
                                v = rt.component_wise("mod", rt.binary("*", rt.binary("-", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.25), 1, "float"), rt.binary("-", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), rt.f(0.5), 1, "float"), width=1)
        return (rt.f(0.0) if rt.binary(">", v, rt.f(1.0)) else rt.f(1.0))
    def bitField__vec2(st):
        st = rt.copy(st, "float")
        st[:] = rt.binary("/", st, _u_scale, 2, "float")
        st[:] = rotate2D__vec2_float(st, _u_rotation)
        freq = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), _u_scale, rt.f(8.0))
        color = rt.construct(3, rt.f(0.0))
        if rt.binary("==", _u_COLOR_SCHEME, rt.i(0)):
            color = rt.assign_swizzle(color, "b", bitValue__vec2_float_float(st, freq, _u_n))
        else:
            if rt.binary("==", _u_COLOR_SCHEME, rt.i(1)):
                color = rt.assign_swizzle(color, "gb", rt.construct(2, bitValue__vec2_float_float(st, freq, _u_n)))
            else:
                if rt.binary("==", _u_COLOR_SCHEME, rt.i(2)):
                    color = rt.assign_swizzle(color, "g", bitValue__vec2_float_float(st, freq, _u_n))
                else:
                    if rt.binary("==", _u_COLOR_SCHEME, rt.i(3)):
                        color = rt.assign_swizzle(color, "br", rt.construct(2, bitValue__vec2_float_float(st, freq, _u_n)))
                    else:
                        if rt.binary("==", _u_COLOR_SCHEME, rt.i(4)):
                            color = rt.assign_swizzle(color, "r", bitValue__vec2_float_float(st, freq, _u_n))
                        else:
                            if rt.binary("==", _u_COLOR_SCHEME, rt.i(5)):
                                color = rt.assign_swizzle(color, "rgb", rt.construct(3, bitValue__vec2_float_float(st, freq, _u_n)))
                            else:
                                if rt.binary("==", _u_COLOR_SCHEME, rt.i(6)):
                                    color = rt.assign_swizzle(color, "rg", rt.construct(2, bitValue__vec2_float_float(st, freq, _u_n)))
                                else:
                                    if rt.binary("==", _u_COLOR_SCHEME, rt.i(10)):
                                        color = rt.assign_swizzle(color, "b", bitValue__vec2_float_float(st, freq, _u_n))
                                        color = rt.assign_swizzle(color, "g", bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float")))
                                    else:
                                        if rt.binary("==", _u_COLOR_SCHEME, rt.i(11)):
                                            color = rt.assign_swizzle(color, "b", bitValue__vec2_float_float(st, freq, _u_n))
                                            color = rt.assign_swizzle(color, "r", bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float")))
                                        else:
                                            if rt.binary("==", _u_COLOR_SCHEME, rt.i(12)):
                                                color = rt.assign_swizzle(color, "b", bitValue__vec2_float_float(st, freq, _u_n))
                                                color = rt.assign_swizzle(color, "rg", rt.construct(2, bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float"))))
                                            else:
                                                if rt.binary("==", _u_COLOR_SCHEME, rt.i(13)):
                                                    color = rt.assign_swizzle(color, "g", bitValue__vec2_float_float(st, freq, _u_n))
                                                    color = rt.assign_swizzle(color, "rb", rt.construct(2, bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float"))))
                                                else:
                                                    if rt.binary("==", _u_COLOR_SCHEME, rt.i(14)):
                                                        color = rt.assign_swizzle(color, "g", bitValue__vec2_float_float(st, freq, _u_n))
                                                        color = rt.assign_swizzle(color, "r", bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float")))
                                                    else:
                                                        if rt.binary("==", _u_COLOR_SCHEME, rt.i(15)):
                                                            color = rt.assign_swizzle(color, "r", bitValue__vec2_float_float(st, freq, _u_n))
                                                            color = rt.assign_swizzle(color, "bg", rt.construct(2, bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float"))))
                                                        else:
                                                            if rt.binary("==", _u_COLOR_SCHEME, rt.i(20)):
                                                                color = rt.assign_swizzle(color, "r", bitValue__vec2_float_float(st, freq, _u_n))
                                                                color = rt.assign_swizzle(color, "g", bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(1.0), 1, "float")))
                                                                color = rt.assign_swizzle(color, "b", bitValue__vec2_float_float(st, freq, rt.binary("+", _u_n, rt.f(2.0), 1, "float")))
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
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
                            else:
                                (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
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
    def maskValue__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st, "float")
        return constant__vec2_float_float_float(st, xFreq, yFreq, s)
    def maskValue__vec2_float_float(st, freq, s):
        st = rt.copy(st, "float")
        return maskValue__vec2_float_float_float(st, freq, freq, s)
    def arecibo__vec2_float_float_float(st, xFreq, yFreq, _seed):
        st = rt.copy(st, "float")
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), width=1), xFreq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"), width=1), yFreq, width=1)
        v = rt.f(1.0)
        if (bool((bool((bool(rt.binary("==", xMod, rt.f(0.0))) or bool(rt.binary("==", yMod, rt.f(0.0))))) or bool(rt.binary("==", xMod, rt.binary("-", xFreq, rt.f(1.0), 1, "float"))))) or bool(rt.binary("==", yMod, rt.binary("-", yFreq, rt.f(1.0), 1, "float")))):
            v = rt.f(0.0)
        else:
            if rt.binary("==", yMod, rt.f(1.0)):
                v = (rt.f(1.0) if rt.binary("==", xMod, rt.f(1.0)) else rt.f(0.0))
            else:
                v = maskValue__vec2_float_float_float(st, xFreq, yFreq, _seed)
        return v
    def areciboNum__vec2_float_float(st, freq, _seed):
        st = rt.copy(st, "float")
        return arecibo__vec2_float_float_float(st, rt.binary("+", rt.component_wise("floor", rt.binary("*", freq, rt.f(0.5), 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.component_wise("floor", freq, width=1), _seed)
    def glyphs__vec2_float_float(st, freq, _seed):
        st = rt.copy(st, "float")
        xFreq = rt.component_wise("floor", rt.binary("*", freq, rt.f(0.75), 1, "float"), width=1)
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), width=1), xFreq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), width=1), freq, width=1)
        v = rt.f(1.0)
        if (bool((bool((bool(rt.binary("==", xMod, rt.f(0.0))) or bool(rt.binary("==", yMod, rt.f(0.0))))) or bool(rt.binary("==", xMod, rt.binary("-", xFreq, rt.f(1.0), 1, "float"))))) or bool(rt.binary("==", yMod, rt.binary("-", freq, rt.f(1.0), 1, "float")))):
            v = rt.f(0.0)
        else:
            v = maskValue__vec2_float_float_float(st, xFreq, freq, _seed)
        return v
    def invaders__vec2_float_float(st, freq, _seed):
        st = rt.copy(st, "float")
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), width=1), freq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), width=1), freq, width=1)
        v = rt.f(1.0)
        if (bool((bool((bool(rt.binary("==", xMod, rt.f(0.0))) or bool(rt.binary("==", yMod, rt.f(0.0))))) or bool(rt.binary("==", xMod, rt.binary("-", freq, rt.f(1.0), 1, "float"))))) or bool(rt.binary("==", yMod, rt.binary("-", freq, rt.f(1.0), 1, "float")))):
            v = rt.f(0.0)
        else:
            if rt.binary(">=", xMod, rt.binary("*", freq, rt.f(0.5), 1, "float")):
                v = maskValue__vec2_float_float(rt.construct(2, rt.binary("+", rt.component_wise("floor", rt.swizzle(st, "x"), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("fract", rt.swizzle(st, "x"), width=1), 1, "float"), 1, "float"), rt.swizzle(st, "y")), freq, _seed)
            else:
                v = maskValue__vec2_float_float(st, freq, _seed)
        return v
    def bitMaskValue__vec2_float_float(st, freq, _seed):
        st = rt.copy(st, "float")
        v = rt.f(1.0)
        if (bool(rt.binary("==", _u_MASK_FORMULA, rt.i(10))) or bool(rt.binary("==", _u_MASK_FORMULA, rt.i(11)))):
            v = invaders__vec2_float_float(st, freq, _seed)
        else:
            if rt.binary("==", _u_MASK_FORMULA, rt.i(20)):
                v = glyphs__vec2_float_float(st, freq, _seed)
            else:
                if rt.binary("==", _u_MASK_FORMULA, rt.i(30)):
                    v = areciboNum__vec2_float_float(st, freq, _seed)
        return v
    def bitMask__vec2(st):
        st = rt.copy(st, "float")
        color = rt.construct(3, rt.f(0.0))
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.binary("*", st, _u_tiles, 2, "float")
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        if rt.binary("==", _u_MASK_FORMULA, rt.i(11)):
            st = rt.assign_swizzle(st, "y", rt.binary("*", rt.swizzle(st, "y"), rt.f(2.0), 1, "float"))
        freq = rt.component_wise("floor", map__float_float_float_float_float(_u_complexity, rt.f(1.0), rt.f(100.0), rt.f(5.0), rt.f(12.0)), width=1)
        mask = (rt.f(1.0) if rt.binary(">", bitMaskValue__vec2_float_float(st, freq, rt.unary("-", rt.f(100.0))), rt.f(0.5)) else rt.f(0.0))
        if rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(0)):
            color = rt.assign_swizzle(color, "r", mask)
            color = rt.assign_swizzle(color, "g", mask)
            color = rt.assign_swizzle(color, "b", mask)
        else:
            baseHue = rt.binary("+", rt.f(0.01), rt.binary("*", rt.binary("*", maskValue__vec2_float_float(st, rt.f(1.0), rt.unary("-", rt.f(100.0))), _u_baseHueRange, 1, "float"), rt.f(0.01), 1, "float"), 1, "float")
            color = rt.assign_swizzle(color, "r", rt.binary("*", rt.component_wise("fract", rt.binary("+", rt.binary("+", baseHue, rt.binary("*", rt.binary("*", bitMaskValue__vec2_float_float(st, freq, rt.f(0.0)), _u_hueRange, 1, "float"), rt.f(0.01), 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"), width=1), mask, 1, "float"))
            if rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(3)):
                color = rt.assign_swizzle(color, "g", mask)
            else:
                color = rt.assign_swizzle(color, "g", rt.binary("*", bitMaskValue__vec2_float_float(st, freq, rt.f(25.0)), mask, 1, "float"))
            if (bool(rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(2))) or bool(rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(3)))):
                color = rt.assign_swizzle(color, "b", mask)
            else:
                color = rt.assign_swizzle(color, "b", rt.binary("*", bitMaskValue__vec2_float_float(st, freq, rt.f(50.0)), mask, 1, "float"))
            color[:] = hsv2rgb__vec3(color)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        st = globalCoord
        if rt.binary("==", _u_MODE, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", bitField__vec2(st))
        else:
            st[:] = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
            st[:] = rt.binary("+", st, rt.binary("+", rt.construct(1, _u_seed), rt.f(1000.0), 1, "float"), 2, "float")
            color = rt.assign_swizzle(color, "rgb", bitMask__vec2(st))
        st[:] = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
