def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_hslEnable = U["hslEnable"]
    _u_hslHueCenter = U["hslHueCenter"]
    _u_hslHueRange = U["hslHueRange"]
    _u_hslSatMin = U["hslSatMin"]
    _u_hslSatMax = U["hslSatMax"]
    _u_hslLumMin = U["hslLumMin"]
    _u_hslLumMax = U["hslLumMax"]
    _u_hslFeather = U["hslFeather"]
    _u_hslHueShift = U["hslHueShift"]
    _u_hslSatAdjust = U["hslSatAdjust"]
    _u_hslLumAdjust = U["hslLumAdjust"]
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722))
    g.PI = rt.f(3.14159265359)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def srgbToLinear__vec3(srgb):
        srgb = rt.copy(srgb)
        linear = rt.construct(3, 0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", srgb[int(i)], rt.f(0.04045)):
                linear[int(i)] = rt.binary("/", srgb[int(i)], rt.f(12.92), 1)
            else:
                linear[int(i)] = rt.component_wise("pow", rt.binary("/", rt.binary("+", srgb[int(i)], rt.f(0.055), 1), rt.f(1.055), 1), rt.f(2.4), width=1)
        return linear
    def linearToSrgb__vec3(linear):
        linear = rt.copy(linear)
        srgb = rt.construct(3, 0.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", linear[int(i)], rt.f(0.0031308)):
                srgb[int(i)] = rt.binary("*", linear[int(i)], rt.f(12.92), 1)
            else:
                srgb[int(i)] = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear[int(i)], rt.binary("/", rt.f(1.0), rt.f(2.4), 1), width=1), 1), rt.f(0.055), 1)
        return srgb
    def rgbToHsl__vec3(rgb):
        rgb = rt.copy(rgb)
        maxC = rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        minC = rt.component_wise("min", rt.component_wise("min", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        delta = rt.binary("-", maxC, minC, 1)
        l = rt.binary("*", rt.binary("+", maxC, minC, 1), rt.f(0.5), 1)
        h = rt.f(0.0)
        s = rt.f(0.0)
        if rt.binary(">", delta, rt.f(0.001)):
            s = (rt.binary("/", delta, rt.binary("-", rt.binary("-", rt.f(2.0), maxC, 1), minC, 1), 1) if rt.binary(">", l, rt.f(0.5)) else rt.binary("/", delta, rt.binary("+", maxC, minC, 1), 1))
            if rt.binary("==", maxC, rt.swizzle(rgb, "r")):
                h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b"), 1), delta, 1), (rt.f(6.0) if rt.binary("<", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b")) else rt.f(0.0)), 1)
            else:
                if rt.binary("==", maxC, rt.swizzle(rgb, "g")):
                    h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "b"), rt.swizzle(rgb, "r"), 1), delta, 1), rt.f(2.0), 1)
                else:
                    h = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), 1), delta, 1), rt.f(4.0), 1)
            h = rt.binary("/", h, rt.f(6.0), 1)
        return rt.construct(3, h, s, l)
    def hslToRgb__vec3(hsl):
        hsl = rt.copy(hsl)
        h = rt.swizzle(hsl, "x")
        s = rt.swizzle(hsl, "y")
        l = rt.swizzle(hsl, "z")
        if rt.binary("<", s, rt.f(0.001)):
            return rt.construct(3, l)
        q = (rt.binary("*", l, rt.binary("+", rt.f(1.0), s, 1), 1) if rt.binary("<", l, rt.f(0.5)) else rt.binary("-", rt.binary("+", l, s, 1), rt.binary("*", l, s, 1), 1))
        p = rt.binary("-", rt.binary("*", rt.f(2.0), l, 1), q, 1)
        rgb = rt.construct(3, 0.0)
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            t = rt.binary("+", h, rt.binary("/", rt.binary("-", rt.f(1.0), i, 1), rt.f(3.0), 1), 1)
            t = rt.component_wise("fract", t, width=1)
            if rt.binary("<", t, rt.binary("/", rt.f(1.0), rt.f(6.0), 1)):
                rgb[int(i)] = rt.binary("+", p, rt.binary("*", rt.binary("*", rt.binary("-", q, p, 1), rt.f(6.0), 1), t, 1), 1)
            else:
                if rt.binary("<", t, rt.f(0.5)):
                    rgb[int(i)] = q
                else:
                    if rt.binary("<", t, rt.binary("/", rt.f(2.0), rt.f(3.0), 1)):
                        rgb[int(i)] = rt.binary("+", p, rt.binary("*", rt.binary("*", rt.binary("-", q, p, 1), rt.binary("-", rt.binary("/", rt.f(2.0), rt.f(3.0), 1), t, 1), 1), rt.f(6.0), 1), 1)
                    else:
                        rgb[int(i)] = p
        return rgb
    def computeHslKey__vec3_float_float_float_float_float_float_float(hsl, hueCenter, hueRange, satMin, satMax, lumMin, lumMax, feather):
        hsl = rt.copy(hsl)
        hueDist = rt.component_wise("abs", rt.binary("-", rt.swizzle(hsl, "x"), hueCenter, 1), width=1)
        hueDist = rt.component_wise("min", hueDist, rt.binary("-", rt.f(1.0), hueDist, 1), width=1)
        hueKey = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", hueRange, feather, 1), rt.binary("+", hueRange, feather, 1), hueDist, width=1), 1)
        satKey = rt.binary("*", rt.component_wise("smoothstep", rt.binary("-", satMin, feather, 1), rt.binary("+", satMin, feather, 1), rt.swizzle(hsl, "y"), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", satMax, feather, 1), rt.binary("+", satMax, feather, 1), rt.swizzle(hsl, "y"), width=1), 1), 1)
        lumKey = rt.binary("*", rt.component_wise("smoothstep", rt.binary("-", lumMin, feather, 1), rt.binary("+", lumMin, feather, 1), rt.swizzle(hsl, "z"), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", lumMax, feather, 1), rt.binary("+", lumMax, feather, 1), rt.swizzle(hsl, "z"), width=1), 1), 1)
        return rt.binary("*", rt.binary("*", hueKey, satKey, 1), lumKey, 1)
    def applyHslCorrection__vec3_float_float_float(hsl, hueShift, satAdjust, lumAdjust):
        hsl = rt.copy(hsl)
        corrected = hsl
        corrected = rt.assign_swizzle(corrected, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(corrected, "x"), hueShift, 1), width=1))
        corrected = rt.assign_swizzle(corrected, "y", rt.component_wise("clamp", rt.binary("+", rt.swizzle(corrected, "y"), satAdjust, 1), rt.f(0.0), rt.f(1.0), width=1))
        corrected = rt.assign_swizzle(corrected, "z", rt.component_wise("clamp", rt.binary("+", rt.swizzle(corrected, "z"), rt.binary("*", lumAdjust, rt.f(0.5), 1), 1), rt.f(0.0), rt.f(1.0), width=1))
        return corrected
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if rt.binary("==", _u_hslEnable, rt.i(0)):
            g.fragColor = color
            return
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        hsl = rgbToHsl__vec3(rgb)
        matte = computeHslKey__vec3_float_float_float_float_float_float_float(hsl, _u_hslHueCenter, _u_hslHueRange, _u_hslSatMin, _u_hslSatMax, _u_hslLumMin, _u_hslLumMax, _u_hslFeather)
        correctedHsl = applyHslCorrection__vec3_float_float_float(hsl, _u_hslHueShift, _u_hslSatAdjust, _u_hslLumAdjust)
        correctedRgb = hslToRgb__vec3(correctedHsl)
        rgb = rt.component_wise("mix", rgb, correctedRgb, matte, width=3)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
