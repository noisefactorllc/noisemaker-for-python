def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_type = U.get("type", 0)
    _u_symmetry = U.get("symmetry", 0)
    _u_offsetX = U.get("offsetX", rt.f(0.0))
    _u_offsetY = U.get("offsetY", rt.f(0.0))
    _u_centerX = U.get("centerX", rt.f(0.0))
    _u_centerY = U.get("centerY", rt.f(0.0))
    _u_zoomAmt = U.get("zoomAmt", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_iterations = U.get("iterations", 0)
    _u_mode = U.get("mode", 0)
    _u_colorMode = U.get("colorMode", 0)
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_levels = U.get("levels", rt.f(0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_cutoff = U.get("cutoff", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
    g.invB = rt.construct(9, rt.f(0.412165612), rt.f(0.211859107), rt.f(0.0883097947), rt.f(0.536275208), rt.f(0.6807189584), rt.f(0.2818474174), rt.f(0.0514575653), rt.f(0.107406579), rt.f(0.6302613616))
    g.invA = rt.construct(9, rt.f(0.2104542553), rt.f(1.9779984951), rt.f(0.0259040371), rt.f(0.793617785), rt.unary("-", rt.f(2.428592205)), rt.f(0.7827717662), rt.unary("-", rt.f(0.0040720468)), rt.f(0.4505937099), rt.unary("-", rt.f(0.808675766)))
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(2.0))
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        return st
    def offset__vec2(st):
        st = rt.copy(st, "float")
        return rt.binary("*", rt.distance(st, rt.construct(2, rt.f(0.5))), rt.f(0.25), 1, "float")
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
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
    def fx__vec2(z):
        z = rt.copy(z, "float")
        xn = rt.construct(2, rt.binary("-", rt.binary("-", rt.component_wise("pow", rt.swizzle(z, "x"), rt.f(3.0), width=1), rt.binary("*", rt.binary("*", rt.f(3.0), rt.swizzle(z, "x"), 1, "float"), rt.component_wise("pow", rt.swizzle(z, "y"), rt.f(2.0), width=1), 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), rt.binary("-", rt.binary("*", rt.binary("*", rt.f(3.0), rt.component_wise("pow", rt.swizzle(z, "x"), rt.f(2.0), width=1), 1, "float"), rt.swizzle(z, "y"), 1, "float"), rt.component_wise("pow", rt.swizzle(z, "y"), rt.f(3.0), width=1), 1, "float"))
        return xn
    def fpx__vec2(z):
        z = rt.copy(z, "float")
        xn = rt.construct(2, rt.binary("-", rt.binary("*", rt.f(3.0), rt.component_wise("pow", rt.swizzle(z, "x"), rt.f(2.0), width=1), 1, "float"), rt.binary("*", rt.f(3.0), rt.component_wise("pow", rt.swizzle(z, "y"), rt.f(2.0), width=1), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(6.0), rt.swizzle(z, "x"), 1, "float"), rt.swizzle(z, "y"), 1, "float"))
        return xn
    def divide__vec2_vec2(z1, z2):
        z1 = rt.copy(z1, "float")
        z2 = rt.copy(z2, "float")
        result = rt.construct(2, 0.0)
        result = rt.assign_swizzle(result, "x", rt.binary("/", rt.binary("+", rt.binary("*", rt.swizzle(z1, "x"), rt.swizzle(z2, "x"), 1, "float"), rt.binary("*", rt.swizzle(z1, "y"), rt.swizzle(z2, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.component_wise("pow", rt.swizzle(z2, "x"), rt.f(2.0), width=1), rt.component_wise("pow", rt.swizzle(z2, "y"), rt.f(2.0), width=1), 1, "float"), 1, "float"))
        result = rt.assign_swizzle(result, "y", rt.binary("/", rt.binary("-", rt.binary("*", rt.swizzle(z1, "y"), rt.swizzle(z2, "x"), 1, "float"), rt.binary("*", rt.swizzle(z1, "x"), rt.swizzle(z2, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.component_wise("pow", rt.swizzle(z2, "x"), rt.f(2.0), width=1), rt.component_wise("pow", rt.swizzle(z2, "y"), rt.f(2.0), width=1), 1, "float"), 1, "float"))
        return result
    def newton__vec2(st):
        st = rt.copy(st, "float")
        st = rotate2D__vec2_float(st, rt.binary("+", _u_rotation, rt.f(90.0), 1, "float"))
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.binary("*", st, map__float_float_float_float_float(_u_zoomAmt, rt.f(0.0), rt.f(130.0), rt.f(1.0), rt.f(0.01)), 2, "float")
        s = map__float_float_float_float_float(_u_speed, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        offX = map__float_float_float_float_float(_u_offsetX, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.25)), rt.f(0.25))
        offY = map__float_float_float_float_float(_u_offsetY, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.25)), rt.f(0.25))
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", _u_centerY, rt.f(0.01), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("*", _u_centerX, rt.f(0.01), 1, "float"), 1, "float"))
        n = st
        iter = rt.f(0.0)
        tst = rt.construct(2, 0.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, _u_iterations)):
                break
            tst = divide__vec2_vec2(fx__vec2(n), fpx__vec2(n))
            tst = rt.binary("+", tst, rt.binary("*", rt.binary("*", rt.construct(2, rt.component_wise("sin", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1), rt.component_wise("cos", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1)), rt.f(0.1), 2, "float"), s, 2, "float"), 2, "float")
            tst = rt.binary("+", tst, rt.construct(2, offX, offY), 2, "float")
            if rt.binary("<", rt.length(tst), rt.f(0.001)):
                break
            n = rt.binary("-", n, tst, 2, "float")
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
        if rt.binary("==", _u_mode, rt.i(0)):
            return rt.binary("/", iter, rt.construct(1, _u_iterations), 1, "float")
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                return rt.length(n)
    def julia__vec2(st):
        st = rt.copy(st, "float")
        zoom = map__float_float_float_float_float(_u_zoomAmt, rt.f(0.0), rt.f(100.0), rt.f(2.0), rt.f(0.5))
        z = rt.construct(2, 0.0)
        speedy = map__float_float_float_float_float(_u_speed, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        s = rt.component_wise("mix", rt.binary("*", speedy, rt.f(0.05), 1, "float"), rt.binary("*", speedy, rt.f(0.125), 1, "float"), speedy, width=1)
        _offsetX = map__float_float_float_float_float(_u_offsetX, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.5)), rt.f(0.5))
        _offsetY = map__float_float_float_float_float(_u_offsetY, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        c = rt.construct(2, rt.binary("+", rt.binary("*", rt.component_wise("sin", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1), s, 1, "float"), _offsetX, 1, "float"), rt.binary("+", rt.binary("*", rt.component_wise("cos", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1), s, 1, "float"), _offsetY, 1, "float"))
        st = rotate2D__vec2_float(st, _u_rotation)
        st = rt.binary("*", rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float"), zoom, 2, "float")
        z = rt.assign_swizzle(z, "x", rt.binary("+", rt.swizzle(st, "x"), map__float_float_float_float_float(_u_centerX, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(1.0), rt.unary("-", rt.f(1.0))), 1, "float"))
        z = rt.assign_swizzle(z, "y", rt.binary("+", rt.swizzle(st, "y"), map__float_float_float_float_float(_u_centerY, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(1.0), rt.unary("-", rt.f(1.0))), 1, "float"))
        iter = 0
        iterScaled = rt.binary("*", _u_iterations, rt.i(2), 1, "int")
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", i, iterScaled)):
                break
            iter = i
            x = rt.binary("+", rt.binary("-", rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), rt.swizzle(c, "x"), 1, "float")
            y = rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), rt.swizzle(c, "y"), 1, "float")
            if rt.binary(">", rt.binary("+", rt.binary("*", x, x, 1, "float"), rt.binary("*", y, y, 1, "float"), 1, "float"), rt.f(4.0)):
                break
            z = rt.assign_swizzle(z, "x", x)
            z = rt.assign_swizzle(z, "y", y)
        if rt.binary("<", rt.binary("-", iterScaled, iter, 1, "int"), rt.construct(1, _u_cutoff, base="int")):
            return rt.f(1.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            return rt.binary("/", rt.construct(1, iter), rt.construct(1, iterScaled), 1, "float")
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                return rt.length(z)
    def mandelbrot__vec2(st):
        st = rt.copy(st, "float")
        zoom = map__float_float_float_float_float(_u_zoomAmt, rt.f(0.0), rt.f(100.0), rt.f(2.0), rt.f(0.5))
        speedy = map__float_float_float_float_float(_u_speed, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        s = rt.component_wise("mix", rt.binary("*", speedy, rt.f(0.05), 1, "float"), rt.binary("*", speedy, rt.f(0.125), 1, "float"), speedy, width=1)
        st = rotate2D__vec2_float(st, _u_rotation)
        st = rt.assign_swizzle(st, "y", rt.binary("-", rt.binary("*", rt.swizzle(st, "y"), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.binary("*", rt.swizzle(st, "x"), rt.f(2.0), 1, "float"), rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        z = rt.construct(2, rt.f(0.0))
        c = rt.binary("-", rt.binary("*", zoom, st, 2, "float"), rt.binary("*", rt.construct(2, rt.binary("+", _u_centerX, rt.f(50.0), 1, "float"), _u_centerY), rt.f(0.01), 2, "float"), 2, "float")
        z = rt.binary("+", z, rt.binary("*", rt.construct(2, rt.component_wise("sin", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1), rt.component_wise("cos", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), width=1)), s, 2, "float"), 2, "float")
        i = rt.f(0.0)
        i = rt.f(0.0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1, "float")
            _for3_first = False
            if not (rt.binary("<", i, rt.construct(1, _u_iterations))):
                break
            z = rt.binary("+", rt.matrix_mult(rt.construct(4, z, rt.unary("-", rt.swizzle(z, "y")), rt.swizzle(z, "x")), z, 2), c, 2, "float")
            if rt.binary(">", rt.dot(z, z), rt.binary("*", rt.f(4.0), rt.f(4.0), 1, "float")):
                break
        if rt.binary("==", i, rt.construct(1, _u_iterations)):
            return rt.f(1.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            return rt.binary("/", i, rt.construct(1, _u_iterations), 1, "float")
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                return rt.binary("/", rt.length(z), rt.construct(1, _u_iterations), 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        blend = periodicFunction__float(rt.binary("-", _u_time, offset__vec2(st), 1, "float"))
        d = rt.f(0.0)
        if rt.binary("==", _u_type, rt.i(0)):
            d = julia__vec2(st)
        else:
            if rt.binary("==", _u_type, rt.i(1)):
                d = newton__vec2(st)
            else:
                d = mandelbrot__vec2(st)
        if rt.binary("==", d, rt.f(1.0)):
            g.fragColor = rt.construct(4, _u_bgColor, rt.binary("*", _u_bgAlpha, rt.f(0.01), 1, "float"))
            return
        if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
            d = rt.binary("-", d, _u_time, 1, "float")
        else:
            if rt.binary("==", _u_cyclePalette, rt.i(1)):
                d = rt.binary("+", d, _u_time, 1, "float")
        d = rt.binary("+", rt.binary("*", d, _u_repeatPalette, 1, "float"), rt.binary("*", _u_rotatePalette, rt.f(0.01), 1, "float"), 1, "float")
        d = rt.component_wise("fract", d, width=1)
        if rt.binary(">", _u_levels, rt.f(0.0)):
            lev = rt.binary("+", _u_levels, rt.f(1.0), 1, "float")
            d = rt.binary("/", rt.component_wise("floor", rt.binary("*", d, lev, 1, "float"), width=1), lev, 1, "float")
        if rt.binary("==", _u_colorMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.construct(3, rt.component_wise("fract", d, width=1)))
        else:
            if rt.binary("==", _u_colorMode, rt.i(4)):
                color = rt.assign_swizzle(color, "rgb", pal__float(d))
            else:
                if rt.binary("==", _u_colorMode, rt.i(6)):
                    d = rt.binary("*", d, rt.binary("*", _u_hueRange, rt.f(0.01), 1, "float"), 1, "float")
                    color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(rt.construct(3, d, rt.f(1.0), rt.f(1.0))))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
