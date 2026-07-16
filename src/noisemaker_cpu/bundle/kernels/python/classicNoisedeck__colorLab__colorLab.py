def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_levels = U.get("levels", rt.f(0.0))
    _u_dither = U.get("dither", 0)
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_invert = U.get("invert", False)
    _u_brightness = U.get("brightness", rt.f(0.0))
    _u_contrast = U.get("contrast", rt.f(0.0))
    _u_saturation = U.get("saturation", rt.f(0.0))
    _u_colorMode = U.get("colorMode", 0)
    _u_paletteMode = U.get("paletteMode", 0)
    _u_paletteOffset = U.get("paletteOffset", rt.construct(3, 0.0))
    _u_paletteAmp = U.get("paletteAmp", rt.construct(3, 0.0))
    _u_paletteFreq = U.get("paletteFreq", rt.construct(3, 0.0))
    _u_palettePhase = U.get("palettePhase", rt.construct(3, 0.0))
    _u_cyclePalette = U.get("cyclePalette", 0)
    _u_rotatePalette = U.get("rotatePalette", rt.f(0.0))
    _u_repeatPalette = U.get("repeatPalette", rt.f(0.0))
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
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.swizzle(prng__vec3(rt.construct(3, st, rt.f(1.0))), "x")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def posterize__vec3_float(color, lev):
        color = rt.copy(color, "float")
        if rt.binary("==", lev, rt.f(0.0)):
            return color
        else:
            if rt.binary("==", lev, rt.f(1.0)):
                lev = rt.f(2.0)
        gamma = rt.f(0.65)
        color = rt.component_wise("pow", color, rt.construct(3, gamma), width=3)
        color = rt.binary("/", rt.component_wise("floor", rt.binary("*", color, lev, 3, "float"), width=3), lev, 3, "float")
        color = rt.component_wise("pow", color, rt.construct(3, rt.binary("/", rt.f(1.0), gamma, 1, "float")), width=3)
        return color
    def brightnessContrast__vec3(color):
        color = rt.copy(color, "float")
        bright = map__float_float_float_float_float(_u_brightness, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        cont = map__float_float_float_float_float(_u_contrast, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0))
        color = rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", color, rt.f(0.5), 3, "float"), cont, 3, "float"), rt.f(0.5), 3, "float"), bright, 3, "float")
        return color
    def saturate__vec3(color):
        color = rt.copy(color, "float")
        sat = map__float_float_float_float_float(_u_saturation, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        avg = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(color, "r"), rt.swizzle(color, "g"), 1, "float"), rt.swizzle(color, "b"), 1, "float"), rt.f(3.0), 1, "float")
        color = rt.binary("-", color, rt.binary("*", rt.binary("-", avg, color, 3, "float"), sat, 3, "float"), 3, "float")
        return color
    def desaturate__vec3(color):
        color = rt.copy(color, "float")
        avg = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
        return rt.construct(3, avg)
    def periodicFunction__float(p):
        x = rt.binary("*", rt.f(6.28318530718), p, 1, "float")
        func = rt.component_wise("sin", x, width=1)
        return map__float_float_float_float_float(func, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def offsets__vec2(st):
        st = rt.copy(st, "float")
        return rt.distance(st, rt.construct(2, rt.f(0.5)))
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
    def srgbToLinear__vec3(srgb):
        srgb = rt.copy(srgb, "float")
        linear = rt.construct(3, 0.0)
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
                color = linearToSrgb__vec3(rt.swizzle(color, "rgb"))
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.construct(4, rt.f(0.0))
        blendy = periodicFunction__float(rt.binary("-", _u_time, offsets__vec2(uv), 1, "float"))
        color = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        if rt.binary("!=", _u_levels, rt.f(0.0)):
            color = rt.assign_swizzle(color, "rgb", posterize__vec3_float(rt.swizzle(color, "rgb"), _u_levels))
        bright = rgb2hsv__vec3(rt.swizzle(color, "rgb"))[int(rt.i(2))]
        coord = rt.construct(2, 0.0)
        if rt.binary("==", _u_dither, rt.i(1)):
            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.construct(3, rt.component_wise("step", rt.f(0.5), bright, width=1)), 3, "float"))
        else:
            if rt.binary("==", _u_dither, rt.i(2)):
                color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.construct(3, rt.component_wise("step", random__vec2(globalCoord), bright, width=1)), 3, "float"))
            else:
                if rt.binary("==", _u_dither, rt.i(3)):
                    color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), rt.construct(3, rt.component_wise("step", periodicFunction__float(rt.binary("+", random__vec2(globalCoord), _u_time, 1, "float")), bright, width=1)), 3, "float"))
                else:
                    if rt.binary("==", _u_dither, rt.i(4)):
                        coord = rt.binary("-", rt.swizzle(rt.component_wise("mod", rt.binary("/", globalCoord, _u_renderScale, 2, "float"), rt.f(4.0), width=2), "xy"), rt.f(0.5), 2, "float")
                        if rt.binary("<", bright, rt.f(0.12)):
                            color = rt.assign_swizzle(color, "rgb", rt.construct(3, rt.f(0.0)))
                        else:
                            if rt.binary("<", bright, rt.f(0.24)):
                                color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(1.0)) if rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(1.0))) else rt.construct(3, rt.f(0.0))), 3, "float"))
                            else:
                                if rt.binary("<", bright, rt.f(0.36)):
                                    color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(1.0)) if (bool(rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(1.0)))) or bool(rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(3.0))))) else rt.construct(3, rt.f(0.0))), 3, "float"))
                                else:
                                    if rt.binary("<", bright, rt.f(0.48)):
                                        color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(1.0)) if (bool((bool(rt.binary("==", rt.swizzle(coord, "x"), rt.f(1.0))) or bool(rt.binary("==", rt.swizzle(coord, "x"), rt.f(3.0))))) and bool((bool(rt.binary("==", rt.swizzle(coord, "y"), rt.f(1.0))) or bool(rt.binary("==", rt.swizzle(coord, "y"), rt.f(3.0)))))) else rt.construct(3, rt.f(0.0))), 3, "float"))
                                    else:
                                        if rt.binary("<", bright, rt.f(0.6)):
                                            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(0.0)) if (bool((bool(rt.binary("==", rt.swizzle(coord, "x"), rt.f(1.0))) or bool(rt.binary("==", rt.swizzle(coord, "x"), rt.f(3.0))))) and bool((bool(rt.binary("==", rt.swizzle(coord, "y"), rt.f(1.0))) or bool(rt.binary("==", rt.swizzle(coord, "y"), rt.f(3.0)))))) else rt.construct(3, rt.f(1.0))), 3, "float"))
                                        else:
                                            if rt.binary("<", bright, rt.f(0.72)):
                                                color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(0.0)) if (bool(rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(1.0)))) or bool(rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(3.0))))) else rt.construct(3, rt.f(1.0))), 3, "float"))
                                            else:
                                                if rt.binary("<", bright, rt.f(0.84)):
                                                    color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), (rt.construct(3, rt.f(0.0)) if rt.binary("==", rt.swizzle(coord, "xy"), rt.construct(2, rt.f(1.0))) else rt.construct(3, rt.f(1.0))), 3, "float"))
        d = rt.f(0.0)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.construct(3, rt.swizzle(rgb2hsv__vec3(rt.swizzle(color, "rgb")), "b")))
        else:
            if rt.binary("==", _u_colorMode, rt.i(1)):
                color = rt.assign_swizzle(color, "rgb", srgbToLinear__vec3(rt.swizzle(color, "rgb")))
            else:
                if rt.binary("==", _u_colorMode, rt.i(3)):
                    color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
                    color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
                    color = rt.assign_swizzle(color, "rgb", linear_srgb_from_oklab__vec3(rt.swizzle(color, "rgb")))
                    color = rt.assign_swizzle(color, "rgb", linearToSrgb__vec3(rt.swizzle(color, "rgb")))
                else:
                    if rt.binary("==", _u_colorMode, rt.i(4)):
                        d = rt.swizzle(rgb2hsv__vec3(rt.swizzle(color, "rgb")), "b")
                        if rt.binary("==", _u_cyclePalette, rt.unary("-", rt.i(1))):
                            d = rt.binary("+", d, _u_time, 1, "float")
                        else:
                            if rt.binary("==", _u_cyclePalette, rt.i(1)):
                                d = rt.binary("-", d, _u_time, 1, "float")
                        color = rt.assign_swizzle(color, "rgb", pal__float(d))
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv[int(rt.i(0))] = rt.component_wise("mod", rt.binary("+", rt.binary("*", hsv[int(rt.i(0))], map__float_float_float_float_float(_u_hueRange, rt.f(0.0), rt.f(200.0), rt.f(0.0), rt.f(2.0)), 1, "float"), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), rt.f(1.0), width=1)
        color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(hsv))
        if _u_invert:
            color = rt.assign_swizzle(color, "rgb", rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"))
        color = rt.assign_swizzle(color, "rgb", brightnessContrast__vec3(rt.swizzle(color, "rgb")))
        color = rt.assign_swizzle(color, "rgb", saturate__vec3(rt.swizzle(color, "rgb")))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
