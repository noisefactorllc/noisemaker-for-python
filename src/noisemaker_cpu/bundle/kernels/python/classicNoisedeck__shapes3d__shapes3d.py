def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_SHAPE_A = U.get("SHAPE_A", 0)
    _u_SHAPE_B = U.get("SHAPE_B", 0)
    _u_BLEND_MODE = U.get("BLEND_MODE", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_shapeAScale = U.get("shapeAScale", rt.f(0.0))
    _u_shapeBScale = U.get("shapeBScale", rt.f(0.0))
    _u_shapeAThickness = U.get("shapeAThickness", rt.f(0.0))
    _u_shapeBThickness = U.get("shapeBThickness", rt.f(0.0))
    _u_smoothness = U.get("smoothness", rt.f(0.0))
    _u_spin = U.get("spin", rt.f(0.0))
    _u_flip = U.get("flip", rt.f(0.0))
    _u_spinSpeed = U.get("spinSpeed", rt.f(0.0))
    _u_flipSpeed = U.get("flipSpeed", rt.f(0.0))
    _u_repetition = U.get("repetition", False)
    _u_animation = U.get("animation", 0)
    _u_flythroughSpeed = U.get("flythroughSpeed", rt.f(0.0))
    _u_spacing = U.get("spacing", rt.f(0.0))
    _u_cameraDist = U.get("cameraDist", rt.f(0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_colorMode = U.get("colorMode", 0)
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
    _u_weight = U.get("weight", rt.f(0.0))
    _u_inputTex = T["inputTex"]
    g.fragColor = rt.construct(4, 0.0)
    g.MIN_DIST = rt.f(0.01)
    g.MAX_DIST = rt.f(200.0)
    g.MAX_STEPS = rt.i(100)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
    g.invB = rt.construct(9, rt.f(0.412165612), rt.f(0.211859107), rt.f(0.0883097947), rt.f(0.536275208), rt.f(0.6807189584), rt.f(0.2818474174), rt.f(0.0514575653), rt.f(0.107406579), rt.f(0.6302613616))
    g.invA = rt.construct(9, rt.f(0.2104542553), rt.f(1.9779984951), rt.f(0.0259040371), rt.f(0.793617785), rt.unary("-", rt.f(2.428592205)), rt.f(0.7827717662), rt.unary("-", rt.f(0.0040720468)), rt.f(0.4505937099), rt.unary("-", rt.f(0.808675766)))
    def computeTransformData__void():
        data = [rt.construct(2, 0.0), rt.construct(2, 0.0), rt.construct(2, 0.0), rt.construct(2, 0.0), rt.f(0.0), rt.f(0.0), False, False, False]
        staticSpinAngle = rt.component_wise("radians", _u_spin, width=1)
        staticFlipAngle = rt.component_wise("radians", _u_flip, width=1)
        data[0] = rt.construct(2, rt.component_wise("cos", staticSpinAngle, width=1), rt.component_wise("sin", staticSpinAngle, width=1))
        data[1] = rt.construct(2, rt.component_wise("cos", staticFlipAngle, width=1), rt.component_wise("sin", staticFlipAngle, width=1))
        dynamicSpinAngle = rt.binary("*", rt.binary("*", _u_time, rt.binary("*", _u_spinSpeed, rt.f(0.1), 1, "float"), 1, "float"), rt.f(3.14159265359), 1, "float")
        dynamicFlipAngle = rt.binary("*", rt.binary("*", _u_time, rt.binary("*", _u_flipSpeed, rt.f(0.1), 1, "float"), 1, "float"), rt.f(3.14159265359), 1, "float")
        data[2] = rt.construct(2, rt.component_wise("cos", dynamicSpinAngle, width=1), rt.component_wise("sin", dynamicSpinAngle, width=1))
        data[3] = rt.construct(2, rt.component_wise("cos", dynamicFlipAngle, width=1), rt.component_wise("sin", dynamicFlipAngle, width=1))
        data[4] = _u_spacing
        hasRepetition = _u_repetition
        data[6] = (bool(hasRepetition) and bool(rt.binary("==", _u_animation, rt.i(1))))
        data[7] = (bool(hasRepetition) and bool(rt.binary("==", _u_animation, rt.i(0))))
        enableFlythrough = (bool((bool(hasRepetition) and bool(rt.binary("!=", _u_animation, rt.i(0))))) and bool(rt.binary("!=", _u_flythroughSpeed, rt.f(0.0))))
        data[5] = (rt.binary("*", _u_time, _u_flythroughSpeed, 1, "float") if enableFlythrough else rt.f(0.0))
        data[8] = enableFlythrough
        return data
    def computeShapeParams__void():
        params = [rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)]
        params[0] = rt.binary("+", rt.f(1.0), rt.binary("*", _u_shapeAScale, rt.f(0.1), 1, "float"), 1, "float")
        params[1] = rt.binary("+", rt.f(1.0), rt.binary("*", _u_shapeBScale, rt.f(0.1), 1, "float"), 1, "float")
        params[2] = _u_shapeAThickness
        params[3] = _u_shapeBThickness
        return params
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
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
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
    def luminance__vec3(color):
        color = rt.copy(color, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def pal__float(t):
        a = _u_paletteOffset
        b = _u_paletteAmp
        c = _u_paletteFreq
        d = _u_palettePhase
        t = rt.component_wise("abs", t, width=1)
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
    def smin__float_float_float(d1, d2, k):
        h = rt.component_wise("clamp", rt.binary("+", rt.f(0.5), rt.binary("/", rt.binary("*", rt.f(0.5), rt.binary("-", d2, d1, 1, "float"), 1, "float"), k, 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("-", rt.component_wise("mix", d2, d1, h, width=1), rt.binary("*", rt.binary("*", k, h, 1, "float"), rt.binary("-", rt.f(1.0), h, 1, "float"), 1, "float"), 1, "float")
    def ssub__float_float_float(d1, d2, k):
        h = rt.component_wise("clamp", rt.binary("-", rt.f(0.5), rt.binary("/", rt.binary("*", rt.f(0.5), rt.binary("+", d2, d1, 1, "float"), 1, "float"), k, 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("+", rt.component_wise("mix", d2, rt.unary("-", d1), h, width=1), rt.binary("*", rt.binary("*", k, h, 1, "float"), rt.binary("-", rt.f(1.0), h, 1, "float"), 1, "float"), 1, "float")
    def smax__float_float_float(d1, d2, k):
        h = rt.component_wise("clamp", rt.binary("-", rt.f(0.5), rt.binary("/", rt.binary("*", rt.f(0.5), rt.binary("-", d2, d1, 1, "float"), 1, "float"), k, 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("+", rt.component_wise("mix", d2, d1, h, width=1), rt.binary("*", rt.binary("*", k, h, 1, "float"), rt.binary("-", rt.f(1.0), h, 1, "float"), 1, "float"), 1, "float")
    def shape3dA__vec3_vec3_float_float(p, origin, scale, thickness):
        p = rt.copy(p, "float")
        origin = rt.copy(origin, "float")
        d = rt.f(0.0)
        s = rt.binary("*", scale, rt.f(0.25), 1, "float")
        q = rt.construct(2, 0.0)
        if rt.binary("==", _u_SHAPE_A, rt.i(20)):
            d = rt.binary("-", rt.length(rt.binary("-", p, origin, 3, "float")), s, 1, "float")
        else:
            if rt.binary("==", _u_SHAPE_A, rt.i(30)):
                q = rt.construct(2, rt.binary("-", rt.length(rt.swizzle(p, "xy")), s, 1, "float"), rt.swizzle(p, "z"))
                d = rt.binary("-", rt.length(q), rt.f(0.2), 1, "float")
            else:
                if rt.binary("==", _u_SHAPE_A, rt.i(31)):
                    q = rt.construct(2, rt.binary("-", rt.length(rt.swizzle(p, "xz")), s, 1, "float"), rt.swizzle(p, "y"))
                    d = rt.binary("-", rt.length(q), rt.f(0.2), 1, "float")
                else:
                    if rt.binary("==", _u_SHAPE_A, rt.i(10)):
                        s = rt.binary("*", s, rt.f(0.75), 1, "float")
                        p[:] = rt.binary("-", p, rt.component_wise("clamp", p, rt.unary("-", s), s, width=3), 3, "float")
                        d = rt.binary("-", rt.length(p), rt.f(0.01), 1, "float")
                    else:
                        if rt.binary("==", _u_SHAPE_A, rt.i(40)):
                            s = rt.binary("*", s, rt.f(0.75), 1, "float")
                            d = rt.binary("-", rt.length(rt.swizzle(p, "xz")), s, 1, "float")
                        else:
                            if rt.binary("==", _u_SHAPE_A, rt.i(50)):
                                s = rt.binary("*", s, rt.f(0.75), 1, "float")
                                d = rt.component_wise("max", rt.length(rt.binary("-", p, rt.component_wise("clamp", p, rt.unary("-", s), s, width=3), 3, "float")), rt.binary("-", rt.length(rt.swizzle(p, "xy")), s, 1, "float"), width=1)
                            else:
                                if rt.binary("==", _u_SHAPE_A, rt.i(60)):
                                    p = rt.assign_swizzle(p, "y", rt.binary("-", rt.swizzle(p, "y"), rt.component_wise("clamp", rt.swizzle(p, "y"), rt.binary("*", rt.unary("-", scale), rt.f(0.5), 1, "float"), rt.binary("*", scale, rt.f(0.5), 1, "float"), width=1), 1, "float"))
                                    d = rt.binary("-", rt.length(p), rt.binary("*", s, rt.f(0.5), 1, "float"), 1, "float")
                                else:
                                    if rt.binary("==", _u_SHAPE_A, rt.i(70)):
                                        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.swizzle(p, "x"), rt.component_wise("clamp", rt.swizzle(p, "x"), rt.binary("*", rt.unary("-", scale), rt.f(0.5), 1, "float"), rt.binary("*", scale, rt.f(0.5), 1, "float"), width=1), 1, "float"))
                                        d = rt.binary("-", rt.length(p), rt.binary("*", s, rt.f(0.5), 1, "float"), 1, "float")
                                    else:
                                        if rt.binary("==", _u_SHAPE_A, rt.i(80)):
                                            p[:] = rt.component_wise("abs", p, width=3)
                                            return rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), s, 1, "float"), rt.f(0.57735027), 1, "float")
        d = rt.binary("-", rt.component_wise("abs", d, width=1), rt.binary("*", thickness, rt.f(0.01), 1, "float"), 1, "float")
        return d
    def shape3dB__vec3_vec3_float_float(p, origin, scale, thickness):
        p = rt.copy(p, "float")
        origin = rt.copy(origin, "float")
        d = rt.f(0.0)
        s = rt.binary("*", scale, rt.f(0.25), 1, "float")
        q = rt.construct(2, 0.0)
        if rt.binary("==", _u_SHAPE_B, rt.i(20)):
            d = rt.binary("-", rt.length(rt.binary("-", p, origin, 3, "float")), s, 1, "float")
        else:
            if rt.binary("==", _u_SHAPE_B, rt.i(30)):
                q = rt.construct(2, rt.binary("-", rt.length(rt.swizzle(p, "xy")), s, 1, "float"), rt.swizzle(p, "z"))
                d = rt.binary("-", rt.length(q), rt.f(0.2), 1, "float")
            else:
                if rt.binary("==", _u_SHAPE_B, rt.i(31)):
                    q = rt.construct(2, rt.binary("-", rt.length(rt.swizzle(p, "xz")), s, 1, "float"), rt.swizzle(p, "y"))
                    d = rt.binary("-", rt.length(q), rt.f(0.2), 1, "float")
                else:
                    if rt.binary("==", _u_SHAPE_B, rt.i(10)):
                        s = rt.binary("*", s, rt.f(0.75), 1, "float")
                        p[:] = rt.binary("-", p, rt.component_wise("clamp", p, rt.unary("-", s), s, width=3), 3, "float")
                        d = rt.binary("-", rt.length(p), rt.f(0.01), 1, "float")
                    else:
                        if rt.binary("==", _u_SHAPE_B, rt.i(40)):
                            s = rt.binary("*", s, rt.f(0.75), 1, "float")
                            d = rt.binary("-", rt.length(rt.swizzle(p, "xz")), s, 1, "float")
                        else:
                            if rt.binary("==", _u_SHAPE_B, rt.i(50)):
                                s = rt.binary("*", s, rt.f(0.75), 1, "float")
                                d = rt.component_wise("max", rt.length(rt.binary("-", p, rt.component_wise("clamp", p, rt.unary("-", s), s, width=3), 3, "float")), rt.binary("-", rt.length(rt.swizzle(p, "xy")), s, 1, "float"), width=1)
                            else:
                                if rt.binary("==", _u_SHAPE_B, rt.i(60)):
                                    p = rt.assign_swizzle(p, "y", rt.binary("-", rt.swizzle(p, "y"), rt.component_wise("clamp", rt.swizzle(p, "y"), rt.binary("*", rt.unary("-", scale), rt.f(0.5), 1, "float"), rt.binary("*", scale, rt.f(0.5), 1, "float"), width=1), 1, "float"))
                                    d = rt.binary("-", rt.length(p), rt.binary("*", s, rt.f(0.5), 1, "float"), 1, "float")
                                else:
                                    if rt.binary("==", _u_SHAPE_B, rt.i(70)):
                                        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.swizzle(p, "x"), rt.component_wise("clamp", rt.swizzle(p, "x"), rt.binary("*", rt.unary("-", scale), rt.f(0.5), 1, "float"), rt.binary("*", scale, rt.f(0.5), 1, "float"), width=1), 1, "float"))
                                        d = rt.binary("-", rt.length(p), rt.binary("*", s, rt.f(0.5), 1, "float"), 1, "float")
                                    else:
                                        if rt.binary("==", _u_SHAPE_B, rt.i(80)):
                                            p[:] = rt.component_wise("abs", p, width=3)
                                            return rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), s, 1, "float"), rt.f(0.57735027), 1, "float")
        d = rt.binary("-", rt.component_wise("abs", d, width=1), rt.binary("*", thickness, rt.f(0.01), 1, "float"), 1, "float")
        return d
    def blend__float_float(shape1, shape2):
        if rt.binary("==", _u_BLEND_MODE, rt.i(10)):
            return smin__float_float_float(shape1, shape2, rt.binary("*", _u_smoothness, rt.f(0.02), 1, "float"))
        else:
            if rt.binary("==", _u_BLEND_MODE, rt.i(20)):
                return smax__float_float_float(shape1, shape2, rt.binary("*", _u_smoothness, rt.f(0.01), 1, "float"))
            else:
                if rt.binary("==", _u_BLEND_MODE, rt.i(25)):
                    return ssub__float_float_float(shape1, shape2, rt.binary("*", _u_smoothness, rt.f(0.02), 1, "float"))
                else:
                    if rt.binary("==", _u_BLEND_MODE, rt.i(26)):
                        return ssub__float_float_float(rt.unary("-", shape1), shape2, rt.binary("*", _u_smoothness, rt.f(0.02), 1, "float"))
                    else:
                        if rt.binary("==", _u_BLEND_MODE, rt.i(30)):
                            return rt.component_wise("min", shape1, shape2, width=1)
                        else:
                            if rt.binary("==", _u_BLEND_MODE, rt.i(40)):
                                return rt.component_wise("max", shape1, shape2, width=1)
                            else:
                                if rt.binary("==", _u_BLEND_MODE, rt.i(50)):
                                    return rt.component_wise("max", rt.unary("-", shape1), shape2, width=1)
                                else:
                                    if rt.binary("==", _u_BLEND_MODE, rt.i(51)):
                                        return rt.component_wise("max", shape1, rt.unary("-", shape2), width=1)
                                    else:
                                        return rt.f(0.0)
    def rotate2D__vec2_vec2(st, cs):
        st = rt.copy(st, "float")
        cs = rt.copy(cs, "float")
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(st, "x"), rt.swizzle(cs, "x"), 1, "float"), rt.binary("*", rt.swizzle(st, "y"), rt.swizzle(cs, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(st, "x"), rt.swizzle(cs, "y"), 1, "float"), rt.binary("*", rt.swizzle(st, "y"), rt.swizzle(cs, "x"), 1, "float"), 1, "float"))
    def applyTransform__vec3_struct1(p, data):
        p = rt.copy(p, "float")
        if data[8]:
            p = rt.assign_swizzle(p, "z", rt.binary("+", rt.swizzle(p, "z"), data[5], 1, "float"))
        p = rt.assign_swizzle(p, "xz", rotate2D__vec2_vec2(rt.swizzle(p, "xz"), data[0]))
        p = rt.assign_swizzle(p, "yz", rotate2D__vec2_vec2(rt.swizzle(p, "yz"), data[1]))
        if data[6]:
            p[:] = rt.binary("-", p, rt.binary("*", data[4], rt.component_wise("round", rt.binary("/", p, data[4], 3, "float"), width=3), 3, "float"), 3, "float")
        p = rt.assign_swizzle(p, "xz", rotate2D__vec2_vec2(rt.swizzle(p, "xz"), data[2]))
        p = rt.assign_swizzle(p, "yz", rotate2D__vec2_vec2(rt.swizzle(p, "yz"), data[3]))
        if data[7]:
            p[:] = rt.binary("-", p, rt.binary("*", data[4], rt.component_wise("round", rt.binary("/", p, data[4], 3, "float"), width=3), 3, "float"), 3, "float")
        return p
    def getDist__vec3_struct1_struct1(p, data, params):
        p = rt.copy(p, "float")
        p[:] = applyTransform__vec3_struct1(p, data)
        shape1 = shape3dA__vec3_vec3_float_float(p, rt.construct(3, rt.f(0.0)), params[0], params[2])
        shape2 = shape3dB__vec3_vec3_float_float(p, rt.construct(3, rt.f(0.0)), params[1], params[3])
        return blend__float_float(shape1, shape2)
    def getNormal__vec3_struct1_struct1(p, data, params):
        p = rt.copy(p, "float")
        epsilon = rt.f(0.01)
        d = getDist__vec3_struct1_struct1(p, data, params)
        dx = rt.binary("-", getDist__vec3_struct1_struct1(rt.binary("+", p, rt.construct(3, epsilon, rt.f(0.0), rt.f(0.0)), 3, "float"), data, params), d, 1, "float")
        dy = rt.binary("-", getDist__vec3_struct1_struct1(rt.binary("+", p, rt.construct(3, rt.f(0.0), epsilon, rt.f(0.0)), 3, "float"), data, params), d, 1, "float")
        dz = rt.binary("-", getDist__vec3_struct1_struct1(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), epsilon), 3, "float"), data, params), d, 1, "float")
        return rt.normalize(rt.construct(3, dx, dy, dz))
    def rayMarch__vec3_vec3_struct1_struct1(rayOrigin, rayDirection, data, params):
        rayOrigin = rt.copy(rayOrigin, "float")
        rayDirection = rt.copy(rayDirection, "float")
        distAccum = rt.f(0.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, g.MAX_STEPS)):
                break
            p = rt.binary("+", rayOrigin, rt.binary("*", rayDirection, distAccum, 3, "float"), 3, "float")
            dist = getDist__vec3_struct1_struct1(p, data, params)
            distAccum = rt.binary("+", distAccum, dist, 1, "float")
            if (bool(rt.binary(">", distAccum, g.MAX_DIST)) or bool(rt.binary("<", dist, g.MIN_DIST))):
                break
        return distAccum
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(1.0))
        st = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "xy"), 2, "float"), 2, "float"), rt.swizzle(_u_fullResolution, "y"), 2, "float")
        rayOrigin = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.unary("-", _u_cameraDist))
        rayDirection = rt.normalize(rt.construct(3, st, rt.f(1.0)))
        transformData = computeTransformData__void()
        shapeParams = computeShapeParams__void()
        d = rayMarch__vec3_vec3_struct1_struct1(rayOrigin, rayDirection, transformData, shapeParams)
        p = rt.binary("+", rayOrigin, rt.binary("*", rayDirection, d, 3, "float"), 3, "float")
        lightPosition = rt.construct(3, rt.unary("-", rt.f(5.0)), rt.f(5.0), rt.unary("-", rt.f(5.0)))
        lightVector = rt.normalize(rt.binary("-", lightPosition, p, 3, "float"))
        normal = getNormal__vec3_struct1_struct1(p, transformData, shapeParams)
        diffuse = rt.component_wise("clamp", rt.dot(normal, lightVector), rt.f(0.0), rt.f(1.0), width=1)
        localP = rt.construct(3, 0.0)
        colorXY = rt.construct(3, 0.0)
        colorXZ = rt.construct(3, 0.0)
        colorYZ = rt.construct(3, 0.0)
        if rt.binary(">", _u_weight, rt.f(0.0)):
            localP = applyTransform__vec3_struct1(p, transformData)
            localP[:] = rt.binary("+", rt.binary("*", localP, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
            colorXY = rt.swizzle(rt.texture(_u_inputTex, rt.swizzle(localP, "xy")), "rgb")
            colorXZ = rt.swizzle(rt.texture(_u_inputTex, rt.swizzle(localP, "xz")), "rgb")
            colorYZ = rt.swizzle(rt.texture(_u_inputTex, rt.swizzle(localP, "yz")), "rgb")
            normal[:] = rt.component_wise("abs", normal, width=3)
            color = rt.assign_swizzle(color, "rgb", rt.binary("+", rt.binary("+", rt.binary("*", colorXY, rt.swizzle(normal, "z"), 3, "float"), rt.binary("*", colorXZ, rt.swizzle(normal, "y"), 3, "float"), 3, "float"), rt.binary("*", colorYZ, rt.swizzle(normal, "x"), 3, "float"), 3, "float"))
        lum = rt.f(0.0)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.construct(3, rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("*", d, rt.f(0.035), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")), 3, "float"))
        else:
            if rt.binary("==", _u_colorMode, rt.i(1)):
                color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.binary("+", rt.construct(3, rt.binary("*", diffuse, rt.f(1.5), 1, "float")), rt.f(0.5), 3, "float"), 3, "float"))
            else:
                if rt.binary("==", _u_colorMode, rt.i(10)):
                    color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.binary("+", rt.construct(3, rt.binary("*", diffuse, rt.f(1.5), 1, "float")), rt.f(0.5), 3, "float"), 3, "float"))
                    lum = luminance__vec3(rt.swizzle(color, "rgb"))
                    if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                        lum = rt.binary("+", lum, _u_time, 1, "float")
                    else:
                        if rt.binary("==", _u_cyclePalette, rt.i(1)):
                            lum = rt.binary("-", lum, _u_time, 1, "float")
                    color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), pal__float(lum), 3, "float"))
        fogDist = rt.component_wise("clamp", rt.binary("/", d, rt.f(200.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        if _u_repetition:
            color[:] = rt.component_wise("mix", color, rt.construct(4, _u_bgColor, rt.binary("*", _u_bgAlpha, rt.f(0.01), 1, "float")), fogDist, width=4)
        else:
            color[:] = rt.component_wise("mix", color, rt.construct(4, _u_bgColor, rt.binary("*", _u_bgAlpha, rt.f(0.01), 1, "float")), rt.component_wise("floor", fogDist, width=1), width=4)
        st[:] = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
