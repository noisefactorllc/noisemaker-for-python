def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_mode = U["mode"]
    _u_quantize = U["quantize"]
    _u_mapSource = U["mapSource"]
    _u_threshold = U["threshold"]
    _u_range = U["range"]
    _u_thresholdR = U["thresholdR"]
    _u_rangeR = U["rangeR"]
    _u_thresholdG = U["thresholdG"]
    _u_rangeG = U["rangeG"]
    _u_thresholdB = U["thresholdB"]
    _u_rangeB = U["rangeB"]
    def getLuminosity__vec3(color):
        color = rt.copy(color)
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def quantizeValue__float_int(value, bands):
        if rt.binary("<=", bands, rt.i(0)):
            return value
        numBands = bands
        return rt.binary("/", rt.component_wise("floor", rt.binary("*", value, numBands, 1), width=1), numBands, 1)
    def calculateBlendFactor__float_float_float(mapValue, thresh, rng):
        if rt.binary("<=", rng, rt.f(0.0)):
            return rt.component_wise("step", thresh, mapValue, width=1)
        else:
            lower = thresh
            upper = rt.binary("+", thresh, rng, 1)
            return rt.component_wise("smoothstep", lower, upper, mapValue, width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2))
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
            result = rt.assign_swizzle(result, "a", rt.component_wise("mix", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), rt.binary("/", rt.binary("+", rt.binary("+", blendR, blendG, 1), blendB, 1), rt.f(3.0), 1), width=1))
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
