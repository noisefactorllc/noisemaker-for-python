def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_mode = U.get("mode", 0)
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_saturation = U.get("saturation", rt.f(0.0))
    _u_brightness = U.get("brightness", rt.f(0.0))
    _u_contrast = U.get("contrast", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530718)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.291485548)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.341134429)), rt.f(1.7068625689))
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
        if rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            rgb = rt.construct(3, c, rt.f(0.0), x)
        return rt.binary("+", rgb, m, 3, "float")
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = rt.swizzle(rgb, "r")
        _g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        maxC = rt.component_wise("max", r, rt.component_wise("max", _g, b, width=1), width=1)
        minC = rt.component_wise("min", r, rt.component_wise("min", _g, b, width=1), width=1)
        delta = rt.binary("-", maxC, minC, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", maxC, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", _g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", maxC, _g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, _g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", maxC, rt.f(0.0)) else rt.binary("/", delta, maxC, 1, "float"))
        return rt.construct(3, h, s, maxC)
    def linear_srgb_from_oklab__vec3(c):
        c = rt.copy(c, "float")
        lms = rt.matrix_mult(g.fwdA, c, 3)
        return rt.matrix_mult(g.fwdB, rt.binary("*", rt.binary("*", lms, lms, 3, "float"), lms, 3, "float"), 3)
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
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        color = rt.texture(_u_inputTex, uv)
        if rt.binary("==", _u_mode, rt.i(1)):
            color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(rt.swizzle(color, "rgb")))
        else:
            if rt.binary("==", _u_mode, rt.i(2)):
                color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.276), 1, "float"))
                color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1, "float"), rt.f(0.198), 1, "float"))
                color = rt.assign_swizzle(color, "rgb", linear_srgb_from_oklab__vec3(rt.swizzle(color, "rgb")))
                color = rt.assign_swizzle(color, "rgb", linearToSrgb__vec3(rt.swizzle(color, "rgb")))
            else:
                if rt.binary("==", _u_mode, rt.i(3)):
                    L = rt.swizzle(color, "r")
                    C = rt.binary("*", rt.swizzle(color, "g"), rt.f(0.4), 1, "float")
                    H = rt.binary("*", rt.swizzle(color, "b"), g.TAU, 1, "float")
                    a = rt.binary("*", C, rt.component_wise("cos", H, width=1), 1, "float")
                    b = rt.binary("*", C, rt.component_wise("sin", H, width=1), 1, "float")
                    color = rt.assign_swizzle(color, "rgb", linear_srgb_from_oklab__vec3(rt.construct(3, L, a, b)))
                    color = rt.assign_swizzle(color, "rgb", linearToSrgb__vec3(rt.swizzle(color, "rgb")))
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv = rt.assign_swizzle(hsv, "x", rt.component_wise("fract", rt.binary("+", rt.binary("*", rt.swizzle(hsv, "x"), map__float_float_float_float_float(_u_hueRange, rt.f(0.0), rt.f(200.0), rt.f(0.0), rt.f(2.0)), 1, "float"), rt.binary("/", _u_rotation, rt.f(360.0), 1, "float"), 1, "float"), width=1))
        hsv = rt.assign_swizzle(hsv, "y", rt.binary("*", rt.swizzle(hsv, "y"), _u_saturation, 1, "float"))
        color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(hsv))
        color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), _u_brightness, 3, "float"))
        contrastFactor = rt.binary("*", _u_contrast, rt.f(2.0), 1, "float")
        color = rt.assign_swizzle(color, "rgb", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(color, "rgb"), rt.f(0.5), 3, "float"), contrastFactor, 3, "float"), rt.f(0.5), 3, "float"))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
