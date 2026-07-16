def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_mode = U.get("mode", 0)
    _u_quantize = U.get("quantize", 0)
    _u_mapSource = U.get("mapSource", 0)
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_range = U.get("range", rt.f(0.0))
    _u_thresholdR = U.get("thresholdR", rt.f(0.0))
    _u_rangeR = U.get("rangeR", rt.f(0.0))
    _u_thresholdG = U.get("thresholdG", rt.f(0.0))
    _u_rangeG = U.get("rangeG", rt.f(0.0))
    _u_thresholdB = U.get("thresholdB", rt.f(0.0))
    _u_rangeB = U.get("rangeB", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def getLuminosity__vec3(color):
        color = rt.copy(color, "float")
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def quantizeValue__float_int(value, bands):
        if rt.binary("<=", bands, rt.i(0)):
            return value
        numBands = rt.construct(1, bands)
        return rt.binary("/", rt.component_wise("floor", rt.binary("*", value, numBands, 1, "float"), width=1), numBands, 1, "float")
    def calculateBlendFactor__float_float_float(mapValue, thresh, rng):
        lower = rt.f(0.0)
        upper = rt.f(0.0)
        if rt.binary("<=", rng, rt.f(0.0)):
            return rt.component_wise("step", thresh, mapValue, width=1)
        else:
            lower = thresh
            upper = rt.binary("+", thresh, rng, 1, "float")
            return rt.component_wise("smoothstep", lower, upper, mapValue, width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        mapColor = rt.construct(3, 0.0)
        if rt.binary("==", _u_mapSource, rt.i(0)):
            mapColor = rt.swizzle(colorA, "rgb")
        else:
            mapColor = rt.swizzle(colorB, "rgb")
        if rt.binary(">", _u_quantize, rt.i(0)):
            mapColor = rt.assign_swizzle(mapColor, "r", quantizeValue__float_int(rt.swizzle(mapColor, "r"), _u_quantize))
            mapColor = rt.assign_swizzle(mapColor, "g", quantizeValue__float_int(rt.swizzle(mapColor, "g"), _u_quantize))
            mapColor = rt.assign_swizzle(mapColor, "b", quantizeValue__float_int(rt.swizzle(mapColor, "b"), _u_quantize))
        result = rt.construct(4, 0.0)
        lum = rt.f(0.0)
        blendFactor = rt.f(0.0)
        blendR = rt.f(0.0)
        blendG = rt.f(0.0)
        blendB = rt.f(0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            lum = getLuminosity__vec3(mapColor)
            blendFactor = calculateBlendFactor__float_float_float(lum, _u_threshold, _u_range)
            result = rt.component_wise("mix", colorA, colorB, blendFactor, width=4)
        else:
            blendR = calculateBlendFactor__float_float_float(rt.swizzle(mapColor, "r"), _u_thresholdR, _u_rangeR)
            blendG = calculateBlendFactor__float_float_float(rt.swizzle(mapColor, "g"), _u_thresholdG, _u_rangeG)
            blendB = calculateBlendFactor__float_float_float(rt.swizzle(mapColor, "b"), _u_thresholdB, _u_rangeB)
            result = rt.assign_swizzle(result, "r", rt.component_wise("mix", rt.swizzle(colorA, "r"), rt.swizzle(colorB, "r"), blendR, width=1))
            result = rt.assign_swizzle(result, "g", rt.component_wise("mix", rt.swizzle(colorA, "g"), rt.swizzle(colorB, "g"), blendG, width=1))
            result = rt.assign_swizzle(result, "b", rt.component_wise("mix", rt.swizzle(colorA, "b"), rt.swizzle(colorB, "b"), blendB, width=1))
            result = rt.assign_swizzle(result, "a", rt.component_wise("mix", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), rt.binary("/", rt.binary("+", rt.binary("+", blendR, blendG, 1, "float"), blendB, 1, "float"), rt.f(3.0), 1, "float"), width=1))
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
