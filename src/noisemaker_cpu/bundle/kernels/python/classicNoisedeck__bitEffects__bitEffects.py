def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U["MODE"]
    _u_FORMULA = U["FORMULA"]
    _u_COLOR_SCHEME = U["COLOR_SCHEME"]
    _u_INTERP = U["INTERP"]
    _u_MASK_FORMULA = U["MASK_FORMULA"]
    _u_MASK_COLOR_SCHEME = U["MASK_COLOR_SCHEME"]
    _u_time = U["time"]
    _u_seed = U["seed"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_n = U["n"]
    _u_scale = U["scale"]
    _u_rotation = U["rotation"]
    _u_speed = U["speed"]
    _u_tiles = U["tiles"]
    _u_complexity = U["complexity"]
    _u_hueRange = U["hueRange"]
    _u_hueRotation = U["hueRotation"]
    _u_baseHueRange = U["baseHueRange"]
    g.BIT_COUNT = rt.i(8)
    g.mask = rt.binary("-", rt.binary("<<", rt.i(1), g.BIT_COUNT, 1, "int"), rt.i(1), 1, "int")
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
        return rt.binary("*", left, right, 1, "int")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="int"), 3, "float"), rt.construct(1, rt.i(1013904223), base="int"), 3, "float")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "float"), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "float"), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "float"), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="int"), 3, "int"), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "float"), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "float"), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "float"), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st)
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(1.0))
        angle = rt.binary("*", rot, rt.f(6.28318530718), 1, "float")
        st = rt.binary("-", st, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2)
        st = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st = rt.binary("+", st, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2)
        return st
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, offset):
        st = rt.copy(st)
        offset = rt.copy(offset)
        lattice = rt.construct(2, rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"))
        baseFloor = rt.component_wise("floor", lattice, width=2)
        base = rt.binary("+", cpu_ivec2__vec2(baseFloor), offset, 2, "float")
        frac = rt.binary("-", lattice, baseFloor, 2, "float")
        seedInt = rt.construct(1, rt.component_wise("floor", s, width=1), base="int")
        seedFrac = rt.component_wise("fract", s, width=1)
        xCombined = rt.binary("+", rt.swizzle(frac, "x"), seedFrac, 1, "float")
        xi = rt.binary("+", rt.binary("+", rt.swizzle(base, "x"), seedInt, 1, "int"), rt.construct(1, rt.component_wise("floor", xCombined, width=1), base="int"), 1, "int")
        yi = rt.swizzle(base, "y")
        xBits = rt.construct(1, xi, base="int")
        yBits = rt.construct(1, yi, base="int")
        seedBits = rt.float_bits_to_uint(s)
        fracBits = rt.float_bits_to_uint(seedFrac)
        jitter = cpu_uvec3__float_float_float(rt.binary("^", cpu_umul__int_int(fracBits, rt.i(374761393)), rt.f(0x9E3779B9), 1, "int"), rt.binary("^", cpu_umul__int_int(fracBits, rt.i(668265263)), rt.i(0x7F4A7C15), 1, "int"), rt.binary("^", cpu_umul__int_int(fracBits, rt.i(2246822519)), rt.i(0x94D049B4), 1, "int"))
        state = rt.binary("^", cpu_uvec3__float_float_float(xBits, yBits, seedBits), jitter, 3, "int")
        prngState = pcg__vec3(state)
        denom = rt.f(4294967295.0)
        return rt.construct(3, rt.binary("/", rt.swizzle(prngState, "x"), denom, 1, "float"), rt.binary("/", rt.swizzle(prngState, "y"), denom, 1, "float"), rt.binary("/", rt.swizzle(prngState, "z"), denom, 1, "float"))
    def constant__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st)
        randTime = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, cpu_ivec2__float_float(rt.i(40), rt.i(0)))
        scaledTime = rt.binary("*", periodicFunction__float(rt.binary("-", rt.swizzle(randTime, "x"), _u_time, 1, "float")), map__float_float_float_float_float(rt.component_wise("abs", _u_speed, width=1), rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.333)), 1, "float")
        rand = randomFromLatticeWithOffset__vec2_float_float_float_ivec2(st, xFreq, yFreq, s, cpu_ivec2__float_float(rt.i(0), rt.i(0)))
        return periodicFunction__float(rt.binary("-", rt.swizzle(rand, "x"), scaledTime, 1, "float"))
    def value__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st)
        x1y1 = constant__vec2_float_float_float(st, xFreq, yFreq, s)
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
        return rt.binary("&", rt.binary("^", a, rt.i(0xFFFFFFF), 1, "int"), g.mask, 1, "int")
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
        st = rt.copy(st)
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
        st = rt.copy(st)
        st = rt.binary("/", st, _u_scale, 2)
        st = rotate2D__vec2_float(st, _u_rotation)
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
        hsv = rt.copy(hsv)
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if rt.binary("&&", rt.binary("<=", rt.f(0.0), h), rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"))):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h), rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"))):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h), rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"))):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h), rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"))):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h), rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"))):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h), rt.binary("<", h, rt.f(1.0))):
                                rgb = rt.construct(3, c, rt.f(0.0), x)
                            else:
                                rgb = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3, "float")
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb)
        r = rt.swizzle(rgb, "r")
        g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        _max = rt.component_wise("max", r, rt.component_wise("max", g, b, width=1), width=1)
        _min = rt.component_wise("min", r, rt.component_wise("min", g, b, width=1), width=1)
        delta = rt.binary("-", _max, _min, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", _max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", _max, g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", _max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", _max, rt.f(0.0)) else rt.binary("/", delta, _max, 1, "float"))
        v = _max
        return rt.construct(3, h, s, v)
    def maskValue__vec2_float_float_float(st, xFreq, yFreq, s):
        st = rt.copy(st)
        return constant__vec2_float_float_float(st, xFreq, yFreq, s)
    def maskValue__vec2_float_float(st, freq, s):
        st = rt.copy(st)
        return maskValue__vec2_float_float_float(st, freq, freq, s)
    def arecibo__vec2_float_float_float(st, xFreq, yFreq, _seed):
        st = rt.copy(st)
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), width=1), xFreq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), yFreq, 1, "float"), width=1), yFreq, width=1)
        v = rt.f(1.0)
        if rt.binary("||", rt.binary("==", xMod, rt.f(0.0)), rt.binary("||", rt.binary("==", yMod, rt.f(0.0)), rt.binary("||", rt.binary("==", xMod, rt.binary("-", xFreq, rt.f(1.0), 1, "float")), rt.binary("==", yMod, rt.binary("-", yFreq, rt.f(1.0), 1, "float"))))):
            v = rt.f(0.0)
        else:
            if rt.binary("==", yMod, rt.f(1.0)):
                v = (rt.f(1.0) if rt.binary("==", xMod, rt.f(1.0)) else rt.f(0.0))
            else:
                v = maskValue__vec2_float_float_float(st, xFreq, yFreq, _seed)
        return v
    def areciboNum__vec2_float_float(st, freq, _seed):
        st = rt.copy(st)
        return arecibo__vec2_float_float_float(st, rt.binary("+", rt.component_wise("floor", rt.binary("*", freq, rt.f(0.5), 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.component_wise("floor", freq, width=1), _seed)
    def glyphs__vec2_float_float(st, freq, _seed):
        st = rt.copy(st)
        xFreq = rt.component_wise("floor", rt.binary("*", freq, rt.f(0.75), 1, "float"), width=1)
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), xFreq, 1, "float"), width=1), xFreq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), width=1), freq, width=1)
        v = rt.f(1.0)
        if rt.binary("||", rt.binary("==", xMod, rt.f(0.0)), rt.binary("||", rt.binary("==", yMod, rt.f(0.0)), rt.binary("||", rt.binary("==", xMod, rt.binary("-", xFreq, rt.f(1.0), 1, "float")), rt.binary("==", yMod, rt.binary("-", freq, rt.f(1.0), 1, "float"))))):
            v = rt.f(0.0)
        else:
            v = maskValue__vec2_float_float_float(st, xFreq, freq, _seed)
        return v
    def invaders__vec2_float_float(st, freq, _seed):
        st = rt.copy(st)
        xMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "x"), freq, 1, "float"), width=1), freq, width=1)
        yMod = rt.component_wise("mod", rt.component_wise("floor", rt.binary("*", rt.swizzle(st, "y"), freq, 1, "float"), width=1), freq, width=1)
        v = rt.f(1.0)
        if rt.binary("||", rt.binary("==", xMod, rt.f(0.0)), rt.binary("||", rt.binary("==", yMod, rt.f(0.0)), rt.binary("||", rt.binary("==", xMod, rt.binary("-", freq, rt.f(1.0), 1, "float")), rt.binary("==", yMod, rt.binary("-", freq, rt.f(1.0), 1, "float"))))):
            v = rt.f(0.0)
        else:
            if rt.binary(">=", xMod, rt.binary("*", freq, rt.f(0.5), 1, "float")):
                v = maskValue__vec2_float_float(rt.construct(2, rt.binary("+", rt.component_wise("floor", rt.swizzle(st, "x"), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("fract", rt.swizzle(st, "x"), width=1), 1, "float"), 1, "float"), rt.swizzle(st, "y")), freq, _seed)
            else:
                v = maskValue__vec2_float_float(st, freq, _seed)
        return v
    def bitMaskValue__vec2_float_float(st, freq, _seed):
        st = rt.copy(st)
        v = rt.f(1.0)
        if rt.binary("||", rt.binary("==", _u_MASK_FORMULA, rt.i(10)), rt.binary("==", _u_MASK_FORMULA, rt.i(11))):
            v = invaders__vec2_float_float(st, freq, _seed)
        else:
            if rt.binary("==", _u_MASK_FORMULA, rt.i(20)):
                v = glyphs__vec2_float_float(st, freq, _seed)
            else:
                if rt.binary("==", _u_MASK_FORMULA, rt.i(30)):
                    v = areciboNum__vec2_float_float(st, freq, _seed)
        return v
    def bitMask__vec2(st):
        st = rt.copy(st)
        color = rt.construct(3, rt.f(0.0))
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2)
        st = rt.binary("*", st, _u_tiles, 2)
        st = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1))
        if rt.binary("==", _u_MASK_FORMULA, rt.i(11)):
            st = rt.assign_swizzle(st, "y", rt.binary("*", rt.swizzle(st, "y"), rt.f(2.0), 1))
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
            if rt.binary("||", rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(2)), rt.binary("==", _u_MASK_COLOR_SCHEME, rt.i(3))):
                color = rt.assign_swizzle(color, "b", mask)
            else:
                color = rt.assign_swizzle(color, "b", rt.binary("*", bitMaskValue__vec2_float_float(st, freq, rt.f(50.0)), mask, 1, "float"))
            color = hsv2rgb__vec3(color)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        st = globalCoord
        if rt.binary("==", _u_MODE, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", bitField__vec2(st))
        else:
            st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
            st = rt.binary("+", st, rt.binary("+", _u_seed, rt.f(1000.0), 1, "float"), 2)
            color = rt.assign_swizzle(color, "rgb", bitMask__vec2(st))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
