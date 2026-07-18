def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_shape = U.get("shape", 0)
    _u_scale = U.get("scale", rt.f(0.0))
    _u_cellScale = U.get("cellScale", rt.f(0.0))
    _u_cellSmooth = U.get("cellSmooth", rt.f(0.0))
    _u_variation = U.get("variation", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_colorMode = U.get("colorMode", 0)
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
    _u_texInfluence = U.get("texInfluence", 0)
    _u_texIntensity = U.get("texIntensity", rt.f(0.0))
    _u_tex = T["tex"]
    g.fragColor = rt.construct(4, 0.0)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
    g.invB = rt.construct(9, rt.f(0.412165612), rt.f(0.211859107), rt.f(0.0883097947), rt.f(0.536275208), rt.f(0.6807189584), rt.f(0.2818474174), rt.f(0.0514575653), rt.f(0.107406579), rt.f(0.6302613616))
    g.invA = rt.construct(9, rt.f(0.2104542553), rt.f(1.9779984951), rt.f(0.0259040371), rt.f(0.793617785), rt.unary("-", rt.f(2.428592205)), rt.f(0.7827717662), rt.unary("-", rt.f(0.0040720468)), rt.f(0.4505937099), rt.unary("-", rt.f(0.808675766)))
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
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
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
    def pal__float(t):
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
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(2.0))
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        return st
    def polarShape__vec2_int(st, sides):
        st = rt.copy(st, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float")
    def shapeDistance__vec2_vec2_int_float(st, offset, type, scale):
        st = rt.copy(st, "float")
        offset = rt.copy(offset, "float")
        st[:] = rt.binary("+", st, offset, 2, "float")
        d = rt.f(1.0)
        if rt.binary("==", type, rt.i(0)):
            d = rt.length(rt.binary("*", st, rt.f(1.2), 2, "float"))
        else:
            if rt.binary("==", type, rt.i(2)):
                d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(6))
            else:
                if rt.binary("==", type, rt.i(3)):
                    d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(8))
                else:
                    if rt.binary("==", type, rt.i(4)):
                        d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(4))
                    else:
                        if rt.binary("==", type, rt.i(6)):
                            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.f(0.05), 1, "float"))
                            d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(3))
        return rt.binary("*", d, scale, 1, "float")
    def wrapEdges__vec2_float(st, freq):
        st = rt.copy(st, "float")
        if rt.binary("<", rt.swizzle(st, "x"), rt.f(0.0)):
            st = rt.assign_swizzle(st, "x", rt.binary("-", freq, rt.f(1.0), 1, "float"))
        if rt.binary(">", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", freq, rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float")):
            st = rt.assign_swizzle(st, "x", rt.f(0.0))
        if rt.binary("<", rt.swizzle(st, "y"), rt.f(0.0)):
            st = rt.assign_swizzle(st, "y", rt.binary("-", freq, rt.f(1.0), 1, "float"))
        if rt.binary(">", rt.swizzle(st, "y"), freq):
            st = rt.assign_swizzle(st, "y", rt.f(0.0))
        return st
    def smin__float_float_float(a, b, k):
        if rt.binary("==", k, rt.f(0.0)):
            return rt.component_wise("min", a, b, width=1)
        h = rt.binary("/", rt.component_wise("max", rt.binary("-", k, rt.component_wise("abs", rt.binary("-", a, b, 1, "float"), width=1), 1, "float"), rt.f(0.0), width=1), k, 1, "float")
        return rt.binary("-", rt.component_wise("min", a, b, width=1), rt.binary("*", rt.binary("*", rt.binary("*", h, h, 1, "float"), k, 1, "float"), rt.binary("/", rt.f(1.0), rt.f(4.0), 1, "float"), 1, "float"), 1, "float")
    def cells__vec2_float_float_int(st, freq, cellSize, sides):
        st = rt.copy(st, "float")
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.binary("*", st, freq, 2, "float")
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.binary("+", st, rt.swizzle(prng__vec3(rt.construct(3, rt.construct(1, _u_seed))), "xy"), 2, "float")
        i = rt.component_wise("floor", st, width=2)
        f = rt.component_wise("fract", st, width=2)
        d = rt.f(1.0)
        y = rt.unary("-", rt.i(2))
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<=", y, rt.i(2))):
                break
            x = rt.unary("-", rt.i(2))
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<=", x, rt.i(2))):
                    break
                n = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                wrap = rt.binary("+", i, n, 2, "float")
                point = rt.swizzle(prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), "xy")
                r1 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, rt.construct(1, _u_seed), wrap)), rt.f(0.5), 3, "float"), rt.f(0.25), 3, "float")
                r2 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
                spd = rt.component_wise("floor", _u_speed, width=1)
                point[:] = rt.binary("+", point, rt.construct(2, rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "x"), 1, "float"), width=1), rt.swizzle(r1, "x"), 1, "float"), rt.binary("*", rt.component_wise("cos", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "y"), 1, "float"), width=1), rt.swizzle(r1, "y"), 1, "float")), 2, "float")
                diff = rt.binary("-", rt.binary("+", n, point, 2, "float"), f, 2, "float")
                dist = shapeDistance__vec2_vec2_int_float(rt.construct(2, rt.swizzle(diff, "x"), rt.unary("-", rt.swizzle(diff, "y"))), rt.construct(2, rt.f(0.0)), sides, cellSize)
                if rt.binary("==", _u_shape, rt.i(1)):
                    dist = rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "x"), rt.swizzle(point, "x"), 1, "float"), rt.swizzle(f, "x"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "y"), rt.swizzle(point, "y"), 1, "float"), rt.swizzle(f, "y"), 1, "float"), width=1), 1, "float")
                    dist = rt.binary("*", dist, cellSize, 1, "float")
                dist = rt.binary("+", dist, rt.binary("*", rt.swizzle(r1, "z"), rt.binary("*", _u_variation, rt.f(0.01), 1, "float"), 1, "float"), 1, "float")
                d = smin__float_float_float(d, dist, rt.binary("*", _u_cellSmooth, rt.f(0.01), 1, "float"))
        return d
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        freq = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(1.0))
        cellSize = map__float_float_float_float_float(_u_cellScale, rt.f(1.0), rt.f(100.0), rt.f(3.0), rt.f(0.75))
        texLuminosity = rt.f(0.0)
        texFactor = rt.binary("*", _u_texIntensity, rt.f(0.01), 1, "float")
        texCoord = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        texRGB = rt.construct(3, 0.0)
        if rt.binary(">", _u_texInfluence, rt.i(0)):
            texRGB = rt.swizzle(rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")), "rgb")
            texLuminosity = luminance__vec3(texRGB)
            if rt.binary("==", _u_texInfluence, rt.i(1)):
                cellSize = rt.binary("-", cellSize, rt.binary("*", texLuminosity, texFactor, 1, "float"), 1, "float")
            else:
                if rt.binary("==", _u_texInfluence, rt.i(2)):
                    freq = rt.binary("-", freq, rt.binary("*", texLuminosity, rt.binary("*", texFactor, rt.f(5.0), 1, "float"), 1, "float"), 1, "float")
        d = cells__vec2_float_float_int(st, freq, cellSize, _u_shape)
        if rt.binary(">=", _u_texInfluence, rt.i(10)):
            if rt.binary("==", _u_texInfluence, rt.i(10)):
                d = rt.binary("+", d, rt.binary("*", texLuminosity, texFactor, 1, "float"), 1, "float")
            else:
                if rt.binary("==", _u_texInfluence, rt.i(11)):
                    d = rt.component_wise("mix", d, rt.binary("/", d, rt.component_wise("max", rt.f(0.1), texLuminosity, width=1), 1, "float"), texFactor, width=1)
                else:
                    if rt.binary("==", _u_texInfluence, rt.i(12)):
                        d = rt.component_wise("mix", d, rt.component_wise("min", d, texLuminosity, width=1), texFactor, width=1)
                    else:
                        if rt.binary("==", _u_texInfluence, rt.i(13)):
                            d = rt.component_wise("mix", d, rt.component_wise("max", d, texLuminosity, width=1), texFactor, width=1)
                        else:
                            if rt.binary("==", _u_texInfluence, rt.i(14)):
                                d = rt.component_wise("mix", d, rt.component_wise("mod", d, rt.component_wise("max", rt.f(0.1), texLuminosity, width=1), width=1), texFactor, width=1)
                            else:
                                if rt.binary("==", _u_texInfluence, rt.i(15)):
                                    d = rt.component_wise("mix", d, rt.binary("*", d, texLuminosity, 1, "float"), texFactor, width=1)
                                else:
                                    if rt.binary("==", _u_texInfluence, rt.i(16)):
                                        d = rt.binary("-", d, rt.binary("*", texLuminosity, texFactor, 1, "float"), 1, "float")
        if rt.binary("==", _u_colorMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.construct(3, d))
        else:
            if rt.binary("==", _u_colorMode, rt.i(1)):
                color = rt.assign_swizzle(color, "rgb", rt.construct(3, rt.binary("-", rt.f(1.0), d, 1, "float")))
            else:
                if rt.binary("==", _u_colorMode, rt.i(2)):
                    if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                        d = rt.binary("+", d, _u_time, 1, "float")
                    else:
                        if rt.binary("==", _u_cyclePalette, rt.i(1)):
                            d = rt.binary("-", d, _u_time, 1, "float")
                    color = rt.assign_swizzle(color, "rgb", pal__float(d))
        st[:] = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
