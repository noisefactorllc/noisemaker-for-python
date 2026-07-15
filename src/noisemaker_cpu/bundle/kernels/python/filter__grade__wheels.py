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
    _u_wheelShadows = U["wheelShadows"]
    _u_wheelMidtones = U["wheelMidtones"]
    _u_wheelHighlights = U["wheelHighlights"]
    _u_wheelBalance = U["wheelBalance"]
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
    def shadowWeight__float_float(luma, balance):
        boundary = rt.binary("-", rt.f(0.33), rt.binary("*", balance, rt.f(0.15), 1), 1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), rt.binary("*", boundary, rt.f(2.0), 1), luma, width=1), 1)
    def midtoneWeight__float_float(luma, balance):
        center = rt.f(0.5)
        spread = rt.binary("-", rt.f(0.4), rt.binary("*", rt.component_wise("abs", balance, width=1), rt.f(0.1), 1), 1)
        dist = rt.binary("/", rt.component_wise("abs", rt.binary("-", luma, center, 1), width=1), spread, 1)
        return rt.component_wise("max", rt.f(0.0), rt.binary("-", rt.f(1.0), dist, 1), width=1)
    def highlightWeight__float_float(luma, balance):
        boundary = rt.binary("+", rt.f(0.67), rt.binary("*", balance, rt.f(0.15), 1), 1)
        return rt.component_wise("smoothstep", rt.binary("-", boundary, rt.f(0.33), 1), rt.f(1.0), luma, width=1)
    def applyWheels__vec3_vec3_vec3_vec3_float(rgb, shadowWheel, midWheel, highWheel, balance):
        rgb = rt.copy(rgb)
        shadowWheel = rt.copy(shadowWheel)
        midWheel = rt.copy(midWheel)
        highWheel = rt.copy(highWheel)
        shadowOffset = rt.binary("*", rt.binary("-", shadowWheel, rt.f(0.5), 3), rt.f(2.0), 3)
        midOffset = rt.binary("*", rt.binary("-", midWheel, rt.f(0.5), 3), rt.f(2.0), 3)
        highOffset = rt.binary("*", rt.binary("-", highWheel, rt.f(0.5), 3), rt.f(2.0), 3)
        if rt.binary("&&", rt.binary("<", rt.length(shadowOffset), rt.f(0.01)), rt.binary("&&", rt.binary("<", rt.length(midOffset), rt.f(0.01)), rt.binary("<", rt.length(highOffset), rt.f(0.01)))):
            return rgb
        luma = rt.dot(rgb, g.LUMA_WEIGHTS)
        sW = shadowWeight__float_float(luma, balance)
        mW = midtoneWeight__float_float(luma, balance)
        hW = highlightWeight__float_float(luma, balance)
        totalWeight = rt.binary("+", rt.binary("+", rt.binary("+", sW, mW, 1), hW, 1), rt.f(0.001), 1)
        sW = rt.binary("/", sW, totalWeight, 1)
        mW = rt.binary("/", mW, totalWeight, 1)
        hW = rt.binary("/", hW, totalWeight, 1)
        colorShift = rt.construct(3, rt.f(0.0))
        colorShift = rt.binary("+", colorShift, rt.binary("*", rt.binary("*", shadowOffset, sW, 3), rt.f(0.5), 3), 3)
        colorShift = rt.binary("+", colorShift, rt.binary("*", rt.binary("*", midOffset, mW, 3), rt.f(0.5), 3), 3)
        colorShift = rt.binary("+", colorShift, rt.binary("*", rt.binary("*", highOffset, hW, 3), rt.f(0.5), 3), 3)
        result = rt.binary("+", rgb, colorShift, 3)
        newLuma = rt.dot(result, g.LUMA_WEIGHTS)
        lumaDiff = rt.binary("-", luma, newLuma, 1)
        result = rt.binary("+", result, rt.binary("*", lumaDiff, rt.f(0.3), 1), 3)
        return result
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        rgb = applyWheels__vec3_vec3_vec3_vec3_float(rgb, _u_wheelShadows, _u_wheelMidtones, _u_wheelHighlights, _u_wheelBalance)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
