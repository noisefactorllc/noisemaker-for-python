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
    _u_preset = U.get("preset", 0)
    _u_alpha = U.get("alpha", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def srgbToLinear__vec3(srgb):
        srgb = rt.copy(srgb, "float")
        linear = rt.construct(3, 0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", srgb[int(i)], rt.f(0.04045)):
                linear[int(i)] = rt.binary("/", srgb[int(i)], rt.f(12.92), 1, "float")
            else:
                linear[int(i)] = rt.component_wise("pow", rt.binary("/", rt.binary("+", srgb[int(i)], rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
        return linear
    def linearToSrgb__vec3(linear):
        linear = rt.copy(linear, "float")
        srgb = rt.construct(3, 0.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", linear[int(i)], rt.f(0.0031308)):
                srgb[int(i)] = rt.binary("*", linear[int(i)], rt.f(12.92), 1, "float")
            else:
                srgb[int(i)] = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear[int(i)], rt.binary("/", rt.f(1.0), rt.f(2.4), 1, "float"), width=1), 1, "float"), rt.f(0.055), 1, "float")
        return srgb
    def rgbToHsl__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        maxC = rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        minC = rt.component_wise("min", rt.component_wise("min", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        delta = rt.binary("-", maxC, minC, 1, "float")
        l = rt.binary("*", rt.binary("+", maxC, minC, 1, "float"), rt.f(0.5), 1, "float")
        h = rt.f(0.0)
        s = rt.f(0.0)
        if rt.binary(">", delta, rt.f(0.001)):
            s = (rt.binary("/", delta, rt.binary("-", rt.binary("-", rt.f(2.0), maxC, 1, "float"), minC, 1, "float"), 1, "float") if rt.binary(">", l, rt.f(0.5)) else rt.binary("/", delta, rt.binary("+", maxC, minC, 1, "float"), 1, "float"))
            if rt.binary("==", maxC, rt.swizzle(rgb, "r")):
                h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b"), 1, "float"), delta, 1, "float"), (rt.f(6.0) if rt.binary("<", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b")) else rt.f(0.0)), 1, "float")
            else:
                if rt.binary("==", maxC, rt.swizzle(rgb, "g")):
                    h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "b"), rt.swizzle(rgb, "r"), 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float")
                else:
                    h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float")
            h = rt.binary("/", h, rt.f(6.0), 1, "float")
        return rt.construct(3, h, s, l)
    def hue2rgb__float_float_float(p, q, t):
        if rt.binary("<", t, rt.f(0.0)):
            t = rt.binary("+", t, rt.f(1.0), 1, "float")
        if rt.binary(">", t, rt.f(1.0)):
            t = rt.binary("-", t, rt.f(1.0), 1, "float")
        if rt.binary("<", t, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")):
            return rt.binary("+", p, rt.binary("*", rt.binary("*", rt.binary("-", q, p, 1, "float"), rt.f(6.0), 1, "float"), t, 1, "float"), 1, "float")
        if rt.binary("<", t, rt.binary("/", rt.f(1.0), rt.f(2.0), 1, "float")):
            return q
        if rt.binary("<", t, rt.binary("/", rt.f(2.0), rt.f(3.0), 1, "float")):
            return rt.binary("+", p, rt.binary("*", rt.binary("*", rt.binary("-", q, p, 1, "float"), rt.binary("-", rt.binary("/", rt.f(2.0), rt.f(3.0), 1, "float"), t, 1, "float"), 1, "float"), rt.f(6.0), 1, "float"), 1, "float")
        return p
    def hslToRgb__vec3(hsl):
        hsl = rt.copy(hsl, "float")
        if rt.binary("==", rt.swizzle(hsl, "y"), rt.f(0.0)):
            return rt.construct(3, rt.swizzle(hsl, "z"))
        q = (rt.binary("*", rt.swizzle(hsl, "z"), rt.binary("+", rt.f(1.0), rt.swizzle(hsl, "y"), 1, "float"), 1, "float") if rt.binary("<", rt.swizzle(hsl, "z"), rt.f(0.5)) else rt.binary("-", rt.binary("+", rt.swizzle(hsl, "z"), rt.swizzle(hsl, "y"), 1, "float"), rt.binary("*", rt.swizzle(hsl, "z"), rt.swizzle(hsl, "y"), 1, "float"), 1, "float"))
        p = rt.binary("-", rt.binary("*", rt.f(2.0), rt.swizzle(hsl, "z"), 1, "float"), q, 1, "float")
        return rt.construct(3, hue2rgb__float_float_float(p, q, rt.binary("+", rt.swizzle(hsl, "x"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), 1, "float")), hue2rgb__float_float_float(p, q, rt.swizzle(hsl, "x")), hue2rgb__float_float_float(p, q, rt.binary("-", rt.swizzle(hsl, "x"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), 1, "float")))
    def luma__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        return rt.dot(rgb, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def lutTealOrange__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        teal = rt.construct(3, rt.f(0.0), rt.f(0.5), rt.f(0.6))
        orange = rt.construct(3, rt.f(1.0), rt.f(0.6), rt.f(0.3))
        graded = rt.component_wise("mix", teal, orange, l, width=3)
        hsl = rgbToHsl__vec3(rgb)
        gradedHsl = rgbToHsl__vec3(graded)
        gradedHsl = rt.assign_swizzle(gradedHsl, "y", rt.component_wise("mix", rt.swizzle(gradedHsl, "y"), rt.swizzle(hsl, "y"), rt.f(0.5), width=1))
        return hslToRgb__vec3(gradedHsl)
    def lutWarmFilm__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        rgb = rt.binary("+", rt.binary("*", rgb, rt.f(0.95), 3, "float"), rt.f(0.05), 3, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.component_wise("pow", rt.swizzle(rgb, "r"), rt.f(0.95), width=1))
        rgb = rt.assign_swizzle(rgb, "b", rt.component_wise("pow", rt.swizzle(rgb, "b"), rt.f(1.05), width=1))
        l = luma__vec3(rgb)
        rgb = rt.assign_swizzle(rgb, "g", rt.component_wise("mix", rt.binary("*", rt.swizzle(rgb, "g"), rt.f(0.95), 1, "float"), rt.swizzle(rgb, "g"), l, width=1))
        rgb = rt.binary("*", rt.binary("*", rgb, rgb, 3, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), rgb, 3, "float"), 3, "float"), 3, "float")
        return rgb
    def lutCoolShadows__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        coolBlue = rt.construct(3, rt.f(0.4), rt.f(0.5), rt.f(0.7))
        shadowMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.5), l, width=1), 1, "float")
        rgb = rt.component_wise("mix", rgb, rt.binary("*", rt.binary("*", coolBlue, l, 3, "float"), rt.f(2.0), 3, "float"), rt.binary("*", shadowMask, rt.f(0.4), 1, "float"), width=3)
        return rgb
    def lutBleachBypass__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        desat = rt.construct(3, l)
        rgb = rt.component_wise("mix", rgb, desat, rt.f(0.5), width=3)
        rgb = rt.binary("+", rt.binary("*", rt.binary("-", rgb, rt.f(0.5), 3, "float"), rt.f(1.3), 3, "float"), rt.f(0.5), 3, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.binary("*", rt.swizzle(rgb, "r"), rt.f(1.02), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "b", rt.binary("*", rt.swizzle(rgb, "b"), rt.f(0.98), 1, "float"))
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutCrossProcess__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.component_wise("pow", rt.swizzle(rgb, "r"), rt.f(0.9), width=1))
        rgb = rt.assign_swizzle(rgb, "g", rt.component_wise("pow", rt.swizzle(rgb, "g"), rt.f(1.0), width=1))
        rgb = rt.assign_swizzle(rgb, "b", rt.component_wise("pow", rt.swizzle(rgb, "b"), rt.f(1.2), width=1))
        l = luma__vec3(rgb)
        rgb = rt.assign_swizzle(rgb, "r", rt.binary("+", rt.swizzle(rgb, "r"), rt.binary("+", rt.binary("*", rt.binary("-", rt.f(1.0), l, 1, "float"), rt.unary("-", rt.f(0.1)), 1, "float"), rt.binary("*", l, rt.f(0.1), 1, "float"), 1, "float"), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "g", rt.binary("+", rt.swizzle(rgb, "g"), rt.binary("*", rt.binary("-", rt.f(1.0), l, 1, "float"), rt.f(0.05), 1, "float"), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "b", rt.binary("+", rt.swizzle(rgb, "b"), rt.binary("+", rt.binary("*", rt.binary("-", rt.f(1.0), l, 1, "float"), rt.f(0.1), 1, "float"), rt.binary("*", l, rt.unary("-", rt.f(0.15)), 1, "float"), 1, "float"), 1, "float"))
        hsl = rgbToHsl__vec3(rgb)
        hsl = rt.assign_swizzle(hsl, "y", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(1.2), 1, "float"))
        rgb = hslToRgb__vec3(hsl)
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutCinematic__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        rgb = rt.binary("+", rt.binary("*", rgb, rt.f(0.9), 3, "float"), rt.f(0.03), 3, "float")
        shadowTint = rt.construct(3, rt.f(0.95), rt.f(1.0), rt.f(1.05))
        highlightTint = rt.construct(3, rt.f(1.05), rt.f(1.0), rt.f(0.95))
        rgb = rt.binary("*", rgb, rt.component_wise("mix", shadowTint, highlightTint, l, width=3), 3, "float")
        rgb = rt.component_wise("pow", rgb, rt.construct(3, rt.f(1.1)), width=3)
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutDayForNight__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        rgb = rt.assign_swizzle(rgb, "r", rt.binary("*", rt.swizzle(rgb, "r"), rt.f(0.5), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "g", rt.binary("*", rt.swizzle(rgb, "g"), rt.f(0.6), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "b", rt.binary("*", rt.swizzle(rgb, "b"), rt.f(1.0), 1, "float"))
        rgb = rt.binary("*", rgb, rt.f(0.4), 3, "float")
        rgb = rt.component_wise("mix", rt.construct(3, luma__vec3(rgb)), rgb, rt.f(0.7), width=3)
        return rgb
    def lutVintage__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        rgb = rt.binary("+", rt.binary("*", rgb, rt.f(0.85), 3, "float"), rt.f(0.08), 3, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.component_wise("pow", rt.swizzle(rgb, "r"), rt.f(0.95), width=1))
        rgb = rt.assign_swizzle(rgb, "b", rt.component_wise("pow", rt.swizzle(rgb, "b"), rt.f(1.1), width=1))
        hsl = rgbToHsl__vec3(rgb)
        hsl = rt.assign_swizzle(hsl, "y", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(0.7), 1, "float"))
        rgb = hslToRgb__vec3(hsl)
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutNoir__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        l = rt.binary("+", rt.binary("*", rt.binary("-", l, rt.f(0.5), 1, "float"), rt.f(1.5), 1, "float"), rt.f(0.5), 1, "float")
        l = rt.component_wise("clamp", l, rt.f(0.0), rt.f(1.0), width=1)
        blue = rt.construct(3, rt.f(0.9), rt.f(0.95), rt.f(1.0))
        mono = rt.binary("*", rt.construct(3, l), rt.component_wise("mix", blue, rt.construct(3, rt.f(1.0)), l, width=3), 3, "float")
        return rt.component_wise("clamp", mono, rt.f(0.0), rt.f(1.0), width=3)
    def lutSepia__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        sepia = rt.construct(3, rt.f(1.0), rt.f(0.89), rt.f(0.71))
        result = rt.binary("*", l, sepia, 3, "float")
        result = rt.binary("+", rt.binary("*", result, rt.f(0.9), 3, "float"), rt.f(0.05), 3, "float")
        return rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3)
    def lutInfrared__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        result = rt.construct(3, 0.0)
        result = rt.assign_swizzle(result, "r", rt.component_wise("pow", l, rt.f(0.7), width=1))
        result = rt.assign_swizzle(result, "g", rt.binary("*", rt.swizzle(rgb, "g"), rt.f(0.3), 1, "float"))
        result = rt.assign_swizzle(result, "b", rt.binary("-", rt.f(1.0), l, 1, "float"))
        foliage = rt.binary("*", rt.component_wise("smoothstep", rt.f(0.2), rt.f(0.6), rt.swizzle(rgb, "g"), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "b"), 1, "float"), width=1), 1, "float"), 1, "float")
        result = rt.assign_swizzle(result, "r", rt.component_wise("mix", rt.swizzle(result, "r"), rt.f(1.0), rt.binary("*", foliage, rt.f(0.7), 1, "float"), width=1))
        return rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3)
    def lutTechnicolor__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.binary("*", rt.component_wise("pow", rt.swizzle(rgb, "r"), rt.f(0.85), width=1), rt.f(1.1), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "g", rt.binary("*", rt.component_wise("pow", rt.swizzle(rgb, "g"), rt.f(1.0), width=1), rt.f(0.95), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "b", rt.binary("*", rt.component_wise("pow", rt.swizzle(rgb, "b"), rt.f(0.9), width=1), rt.f(1.05), 1, "float"))
        hsl = rgbToHsl__vec3(rgb)
        hsl = rt.assign_swizzle(hsl, "y", rt.component_wise("min", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(1.4), 1, "float"), rt.f(1.0), width=1))
        rgb = hslToRgb__vec3(hsl)
        rgb = rt.binary("+", rt.binary("*", rt.binary("-", rgb, rt.f(0.5), 3, "float"), rt.f(1.15), 3, "float"), rt.f(0.5), 3, "float")
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutNeon__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        hsl = rgbToHsl__vec3(rgb)
        hsl = rt.assign_swizzle(hsl, "x", rt.component_wise("mod", rt.binary("+", rt.swizzle(hsl, "x"), rt.f(0.05), 1, "float"), rt.f(1.0), width=1))
        hsl = rt.assign_swizzle(hsl, "y", rt.component_wise("min", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(1.8), 1, "float"), rt.f(1.0), width=1))
        rgb = hslToRgb__vec3(hsl)
        rgb = rt.binary("+", rt.binary("*", rt.binary("-", rgb, rt.f(0.5), 3, "float"), rt.f(1.4), 3, "float"), rt.f(0.5), 3, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.component_wise("pow", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.f(0.0), width=1), rt.f(0.9), width=1))
        rgb = rt.assign_swizzle(rgb, "b", rt.component_wise("pow", rt.component_wise("max", rt.swizzle(rgb, "b"), rt.f(0.0), width=1), rt.f(0.85), width=1))
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutMatrix__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        boosted = rt.component_wise("pow", l, rt.f(0.8), width=1)
        result = rt.construct(3, rt.binary("*", boosted, rt.f(0.2), 1, "float"), boosted, rt.binary("*", boosted, rt.f(0.15), 1, "float"))
        result = rt.binary("+", result, rt.construct(3, rt.f(0.0), rt.f(0.02), rt.f(0.0)), 3, "float")
        return rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3)
    def lutUnderwater__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        rgb = rt.assign_swizzle(rgb, "r", rt.binary("*", rt.swizzle(rgb, "r"), rt.f(0.5), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "g", rt.binary("*", rt.component_wise("pow", rt.swizzle(rgb, "g"), rt.f(0.9), width=1), rt.f(0.9), 1, "float"))
        rgb = rt.assign_swizzle(rgb, "b", rt.binary("*", rt.component_wise("pow", rt.swizzle(rgb, "b"), rt.f(0.85), width=1), rt.f(1.1), 1, "float"))
        depth = rt.binary("-", rt.f(1.0), rt.binary("*", luma__vec3(rgb), rt.f(0.3), 1, "float"), 1, "float")
        rgb = rt.component_wise("mix", rgb, rt.binary("*", rgb, rt.construct(3, rt.f(0.4), rt.f(0.7), rt.f(1.0)), 3, "float"), rt.binary("*", rt.f(0.3), depth, 1, "float"), width=3)
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutSunset__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        warmth = rt.component_wise("smoothstep", rt.f(0.3), rt.f(0.7), l, width=1)
        sunset = rt.component_wise("mix", rt.construct(3, rt.f(1.0), rt.f(0.3), rt.f(0.5)), rt.construct(3, rt.f(1.0), rt.f(0.8), rt.f(0.4)), warmth, width=3)
        rgb = rt.component_wise("mix", rt.binary("*", rgb, sunset, 3, "float"), rgb, rt.f(0.4), width=3)
        rgb = rt.assign_swizzle(rgb, "r", rt.component_wise("pow", rt.swizzle(rgb, "r"), rt.f(0.9), width=1))
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutMonochrome__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        l = rt.binary("+", rt.binary("*", rt.binary("-", l, rt.f(0.5), 1, "float"), rt.f(1.2), 1, "float"), rt.f(0.5), 1, "float")
        return rt.component_wise("clamp", rt.construct(3, l), rt.f(0.0), rt.f(1.0), width=3)
    def lutPsychedelic__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        hsl = rgbToHsl__vec3(rgb)
        hsl = rt.assign_swizzle(hsl, "x", rt.component_wise("mod", rt.binary("+", rt.binary("*", rt.swizzle(hsl, "x"), rt.f(3.0), 1, "float"), rt.binary("*", rt.swizzle(hsl, "z"), rt.f(0.5), 1, "float"), 1, "float"), rt.f(1.0), width=1))
        hsl = rt.assign_swizzle(hsl, "y", rt.component_wise("min", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(2.0), 1, "float"), rt.f(1.0), width=1))
        hsl = rt.assign_swizzle(hsl, "z", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(hsl, "z"), rt.f(0.5), 1, "float"), rt.f(1.3), 1, "float"), rt.f(0.5), 1, "float"))
        rgb = hslToRgb__vec3(hsl)
        return rt.component_wise("clamp", rgb, rt.f(0.0), rt.f(1.0), width=3)
    def lutHardLight__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        result = rt.construct(3, 0.0)
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<", rgb[int(i)], rt.f(0.5)):
                result[int(i)] = rt.binary("*", rt.binary("*", rt.f(2.0), rgb[int(i)], 1, "float"), l, 1, "float")
            else:
                result[int(i)] = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), rgb[int(i)], 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), l, 1, "float"), 1, "float"), 1, "float")
        result = rt.binary("+", rt.binary("*", rt.binary("-", result, rt.f(0.5), 3, "float"), rt.f(1.4), 3, "float"), rt.f(0.5), 3, "float")
        highlightMask = rt.component_wise("smoothstep", rt.f(0.5), rt.f(1.0), l, width=1)
        result = rt.assign_swizzle(result, "b", rt.binary("+", rt.swizzle(result, "b"), rt.binary("*", highlightMask, rt.f(0.05), 1, "float"), 1, "float"))
        return rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3)
    def lutPosterize__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        levels = rt.f(6.0)
        quantized = rt.binary("/", rt.component_wise("floor", rt.binary("+", rt.binary("*", l, levels, 1, "float"), rt.f(0.5), 1, "float"), width=1), levels, 1, "float")
        ramp = rt.construct(3, 0.0)
        if rt.binary("<", quantized, rt.f(0.2)):
            ramp = rt.construct(3, rt.f(0.1), rt.f(0.05), rt.f(0.15))
        else:
            if rt.binary("<", quantized, rt.f(0.4)):
                ramp = rt.construct(3, rt.f(0.3), rt.f(0.2), rt.f(0.4))
            else:
                if rt.binary("<", quantized, rt.f(0.6)):
                    ramp = rt.construct(3, rt.f(0.5), rt.f(0.4), rt.f(0.6))
                else:
                    if rt.binary("<", quantized, rt.f(0.8)):
                        ramp = rt.construct(3, rt.f(0.8), rt.f(0.6), rt.f(0.5))
                    else:
                        ramp = rt.construct(3, rt.f(1.0), rt.f(0.9), rt.f(0.8))
        hsl = rgbToHsl__vec3(rgb)
        rampHsl = rgbToHsl__vec3(ramp)
        rampHsl = rt.assign_swizzle(rampHsl, "x", rt.component_wise("mix", rt.swizzle(rampHsl, "x"), rt.swizzle(hsl, "x"), rt.f(0.3), width=1))
        return hslToRgb__vec3(rampHsl)
    def lutSolarize__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        l = luma__vec3(rgb)
        threshold = rt.f(0.5)
        result = rt.construct(3, 0.0)
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for3_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary(">", rgb[int(i)], threshold):
                result[int(i)] = rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), rgb[int(i)], 1, "float"), 1, "float")
            else:
                result[int(i)] = rt.binary("*", rt.f(2.0), rgb[int(i)], 1, "float")
        hsl = rgbToHsl__vec3(result)
        hsl = rt.assign_swizzle(hsl, "y", rt.component_wise("min", rt.binary("*", rt.swizzle(hsl, "y"), rt.f(1.5), 1, "float"), rt.f(1.0), width=1))
        result = hslToRgb__vec3(hsl)
        result = rt.binary("+", rt.binary("*", rt.binary("-", result, rt.f(0.5), 3, "float"), rt.f(1.1), 3, "float"), rt.f(0.5), 3, "float")
        return rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if (bool(rt.binary("==", _u_preset, rt.i(0))) or bool(rt.binary("<=", _u_alpha, rt.f(0.0)))):
            g.fragColor = color
            return
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        graded = rgb
        if rt.binary("==", _u_preset, rt.i(1)):
            graded = lutTealOrange__vec3(rgb)
        else:
            if rt.binary("==", _u_preset, rt.i(2)):
                graded = lutWarmFilm__vec3(rgb)
            else:
                if rt.binary("==", _u_preset, rt.i(3)):
                    graded = lutCoolShadows__vec3(rgb)
                else:
                    if rt.binary("==", _u_preset, rt.i(4)):
                        graded = lutBleachBypass__vec3(rgb)
                    else:
                        if rt.binary("==", _u_preset, rt.i(5)):
                            graded = lutCrossProcess__vec3(rgb)
                        else:
                            if rt.binary("==", _u_preset, rt.i(6)):
                                graded = lutCinematic__vec3(rgb)
                            else:
                                if rt.binary("==", _u_preset, rt.i(7)):
                                    graded = lutDayForNight__vec3(rgb)
                                else:
                                    if rt.binary("==", _u_preset, rt.i(8)):
                                        graded = lutVintage__vec3(rgb)
                                    else:
                                        if rt.binary("==", _u_preset, rt.i(9)):
                                            graded = lutNoir__vec3(rgb)
                                        else:
                                            if rt.binary("==", _u_preset, rt.i(10)):
                                                graded = lutSepia__vec3(rgb)
                                            else:
                                                if rt.binary("==", _u_preset, rt.i(11)):
                                                    graded = lutInfrared__vec3(rgb)
                                                else:
                                                    if rt.binary("==", _u_preset, rt.i(12)):
                                                        graded = lutTechnicolor__vec3(rgb)
                                                    else:
                                                        if rt.binary("==", _u_preset, rt.i(13)):
                                                            graded = lutNeon__vec3(rgb)
                                                        else:
                                                            if rt.binary("==", _u_preset, rt.i(14)):
                                                                graded = lutMatrix__vec3(rgb)
                                                            else:
                                                                if rt.binary("==", _u_preset, rt.i(15)):
                                                                    graded = lutUnderwater__vec3(rgb)
                                                                else:
                                                                    if rt.binary("==", _u_preset, rt.i(16)):
                                                                        graded = lutSunset__vec3(rgb)
                                                                    else:
                                                                        if rt.binary("==", _u_preset, rt.i(17)):
                                                                            graded = lutMonochrome__vec3(rgb)
                                                                        else:
                                                                            if rt.binary("==", _u_preset, rt.i(18)):
                                                                                graded = lutPsychedelic__vec3(rgb)
                                                                            else:
                                                                                if rt.binary("==", _u_preset, rt.i(20)):
                                                                                    graded = lutHardLight__vec3(rgb)
                                                                                else:
                                                                                    if rt.binary("==", _u_preset, rt.i(21)):
                                                                                        graded = lutPosterize__vec3(rgb)
                                                                                    else:
                                                                                        if rt.binary("==", _u_preset, rt.i(22)):
                                                                                            graded = lutSolarize__vec3(rgb)
        rgb = rt.component_wise("mix", rgb, graded, _u_alpha, width=3)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
