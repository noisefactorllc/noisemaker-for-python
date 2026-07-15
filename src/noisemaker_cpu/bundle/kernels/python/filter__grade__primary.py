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
    _u_temperature = U["temperature"]
    _u_tint = U["tint"]
    _u_exposure = U["exposure"]
    _u_contrast = U["contrast"]
    _u_highlights = U["highlights"]
    _u_shadows = U["shadows"]
    _u_whites = U["whites"]
    _u_blacks = U["blacks"]
    _u_saturation = U["saturation"]
    _u_curveShadows = U["curveShadows"]
    _u_curveMidtones = U["curveMidtones"]
    _u_curveHighlights = U["curveHighlights"]
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722))
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
    def applyWhiteBalance__vec3_float_float(rgb, temp, tint):
        rgb = rt.copy(rgb)
        shift = rt.construct(3, rt.binary("+", rt.f(1.0), rt.binary("*", temp, rt.f(0.5), 1), 1), rt.binary("-", rt.f(1.0), rt.binary("*", tint, rt.f(0.5), 1), 1), rt.binary("-", rt.f(1.0), rt.binary("*", temp, rt.f(0.5), 1), 1))
        return rt.binary("*", rgb, shift, 3)
    def shadowWeight__float(luma):
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.5), luma, width=1), 1)
    def highlightWeight__float(luma):
        return rt.component_wise("smoothstep", rt.f(0.5), rt.f(1.0), luma, width=1)
    def midtoneWeight__float(luma):
        return rt.binary("-", rt.f(1.0), rt.binary("*", rt.component_wise("abs", rt.binary("-", luma, rt.f(0.5), 1), width=1), rt.f(2.0), 1), 1)
    def whitesWeight__float(luma):
        return rt.component_wise("smoothstep", rt.f(0.7), rt.f(1.0), luma, width=1)
    def blacksWeight__float(luma):
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.3), luma, width=1), 1)
    def applyTonalRanges__vec3_float_float_float_float(rgb, highlights, shadows, whites, blacks):
        rgb = rt.copy(rgb)
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", rgb, luma, 3)
        hWeight = highlightWeight__float(luma)
        sWeight = shadowWeight__float(luma)
        wWeight = whitesWeight__float(luma)
        bWeight = blacksWeight__float(luma)
        lumaAdjust = rt.f(0.0)
        lumaAdjust = rt.binary("+", lumaAdjust, rt.binary("*", rt.binary("*", highlights, hWeight, 1), rt.f(0.5), 1), 1)
        lumaAdjust = rt.binary("+", lumaAdjust, rt.binary("*", rt.binary("*", shadows, sWeight, 1), rt.f(0.5), 1), 1)
        lumaAdjust = rt.binary("+", lumaAdjust, rt.binary("*", rt.binary("*", whites, wWeight, 1), rt.f(0.3), 1), 1)
        lumaAdjust = rt.binary("+", lumaAdjust, rt.binary("*", rt.binary("*", blacks, bWeight, 1), rt.f(0.3), 1), 1)
        newLuma = rt.binary("+", luma, lumaAdjust, 1)
        newLuma = rt.component_wise("max", newLuma, rt.f(0.0), width=1)
        return rt.binary("+", newLuma, chroma, 3)
    def applyContrast__vec3_float(rgb, contrast):
        rgb = rt.copy(rgb)
        if rt.binary("<", rt.component_wise("abs", contrast, width=1), rt.f(0.001)):
            return rgb
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", rgb, luma, 3)
        pivot = rt.f(0.5)
        factor = rt.binary("+", rt.f(1.0), contrast, 1)
        newLuma = rt.binary("+", rt.binary("*", rt.binary("-", luma, pivot, 1), factor, 1), pivot, 1)
        newLuma = rt.component_wise("clamp", newLuma, rt.f(0.0), rt.f(1.5), width=1)
        return rt.binary("+", newLuma, chroma, 3)
    def applyCurve__vec3_float_float_float(rgb, shadowLift, midGamma, highGain):
        rgb = rt.copy(rgb)
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", rgb, luma, 3)
        sW = shadowWeight__float(luma)
        mW = midtoneWeight__float(luma)
        hW = highlightWeight__float(luma)
        lift = rt.binary("*", rt.binary("*", shadowLift, sW, 1), rt.f(0.2), 1)
        gamma = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", midGamma, mW, 1), rt.f(0.3), 1), 1)
        gain = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", highGain, hW, 1), rt.f(0.5), 1), 1)
        newLuma = rt.binary("+", luma, lift, 1)
        newLuma = rt.component_wise("pow", rt.component_wise("max", newLuma, rt.f(0.001), width=1), gamma, width=1)
        newLuma = rt.binary("*", newLuma, gain, 1)
        return rt.component_wise("max", rt.binary("+", newLuma, chroma, 3), rt.construct(3, rt.f(0.0)), width=3)
    def applySaturation__vec3_float(rgb, satAmount):
        rgb = rt.copy(rgb)
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        chroma = rt.binary("-", rgb, luma, 3)
        return rt.binary("+", luma, rt.binary("*", chroma, satAmount, 3), 3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        rgb = applyWhiteBalance__vec3_float_float(rgb, _u_temperature, _u_tint)
        rgb = rt.binary("*", rgb, rt.component_wise("pow", rt.f(2.0), _u_exposure, width=1), 3)
        rgb = applyContrast__vec3_float(rgb, _u_contrast)
        rgb = applyTonalRanges__vec3_float_float_float_float(rgb, _u_highlights, _u_shadows, _u_whites, _u_blacks)
        rgb = applyCurve__vec3_float_float_float(rgb, _u_curveShadows, _u_curveMidtones, _u_curveHighlights)
        rgb = applySaturation__vec3_float(rgb, _u_saturation)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
