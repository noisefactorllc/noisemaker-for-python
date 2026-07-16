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
    _u_vibrance = U.get("vibrance", rt.f(0.0))
    _u_fadedFilm = U.get("fadedFilm", rt.f(0.0))
    _u_shadowTint = U.get("shadowTint", rt.construct(3, 0.0))
    _u_highlightTint = U.get("highlightTint", rt.construct(3, 0.0))
    _u_splitToneBalance = U.get("splitToneBalance", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722))
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
    def applyVibrance__vec3_float(rgb, vibrance):
        rgb = rt.copy(rgb, "float")
        if rt.binary("<", rt.component_wise("abs", vibrance, width=1), rt.f(0.001)):
            return rgb
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", rgb, luma, 3, "float")
        maxC = rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        minC = rt.component_wise("min", rt.component_wise("min", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        sat = (rt.binary("/", rt.binary("-", maxC, minC, 1, "float"), maxC, 1, "float") if rt.binary(">", maxC, rt.f(0.001)) else rt.f(0.0))
        vibranceGain = rt.binary("+", rt.f(1.0), rt.binary("*", vibrance, rt.binary("-", rt.f(1.0), sat, 1, "float"), 1, "float"), 1, "float")
        skinFactor = rt.f(1.0)
        hueScore = rt.f(0.0)
        if (bool(rt.binary(">", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"))) and bool(rt.binary(">", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b")))):
            hueScore = rt.binary("/", rt.binary("-", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "b"), 1, "float"), rt.binary("+", rt.binary("-", maxC, minC, 1, "float"), rt.f(0.001), 1, "float"), 1, "float")
            skinFactor = rt.binary("+", rt.binary("*", rt.component_wise("smoothstep", rt.f(0.3), rt.f(0.7), sat, width=1), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
        finalGain = rt.component_wise("mix", rt.f(1.0), vibranceGain, skinFactor, width=1)
        return rt.binary("+", luma, rt.binary("*", chroma, finalGain, 3, "float"), 3, "float")
    def applyFadedFilm__vec3_float(rgb, amount):
        rgb = rt.copy(rgb, "float")
        if rt.binary("<", amount, rt.f(0.001)):
            return rgb
        lifted = rt.component_wise("mix", rgb, rt.construct(3, rt.f(0.2)), rt.binary("*", amount, rt.f(0.5), 1, "float"), width=3)
        luma = rt.dot(lifted, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", lifted, luma, 3, "float")
        pivot = rt.f(0.5)
        contrastFactor = rt.binary("-", rt.f(1.0), rt.binary("*", amount, rt.f(0.3), 1, "float"), 1, "float")
        newLuma = rt.binary("+", rt.binary("*", rt.binary("-", luma, pivot, 1, "float"), contrastFactor, 1, "float"), pivot, 1, "float")
        return rt.binary("+", newLuma, rt.binary("*", chroma, rt.binary("-", rt.f(1.0), rt.binary("*", amount, rt.f(0.2), 1, "float"), 1, "float"), 3, "float"), 3, "float")
    def applySplitTone__vec3_vec3_vec3_float(rgb, shadowTint, highlightTint, balance):
        rgb = rt.copy(rgb, "float")
        shadowTint = rt.copy(shadowTint, "float")
        highlightTint = rt.copy(highlightTint, "float")
        shadowShift = rt.binary("*", rt.binary("-", shadowTint, rt.f(0.5), 3, "float"), rt.f(2.0), 3, "float")
        highlightShift = rt.binary("*", rt.binary("-", highlightTint, rt.f(0.5), 3, "float"), rt.f(2.0), 3, "float")
        if (bool(rt.binary("<", rt.length(shadowShift), rt.f(0.01))) and bool(rt.binary("<", rt.length(highlightShift), rt.f(0.01)))):
            return rgb
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        balancePoint = rt.binary("+", rt.f(0.5), rt.binary("*", balance, rt.f(0.3), 1, "float"), 1, "float")
        shadowWeight = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), balancePoint, luma, width=1), 1, "float")
        highlightWeight = rt.component_wise("smoothstep", balancePoint, rt.f(1.0), luma, width=1)
        tintedRgb = rgb
        tintedRgb = rt.binary("+", tintedRgb, rt.binary("*", rt.binary("*", shadowShift, shadowWeight, 3, "float"), rt.f(0.3), 3, "float"), 3, "float")
        tintedRgb = rt.binary("+", tintedRgb, rt.binary("*", rt.binary("*", highlightShift, highlightWeight, 3, "float"), rt.f(0.3), 3, "float"), 3, "float")
        return tintedRgb
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        rgb = applyVibrance__vec3_float(rgb, _u_vibrance)
        rgb = applyFadedFilm__vec3_float(rgb, _u_fadedFilm)
        rgb = applySplitTone__vec3_vec3_vec3_float(rgb, _u_shadowTint, _u_highlightTint, _u_splitToneBalance)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
