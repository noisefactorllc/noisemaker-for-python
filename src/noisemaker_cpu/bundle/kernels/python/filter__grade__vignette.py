def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_vignetteAmount = U.get("vignetteAmount", rt.f(0.0))
    _u_vignetteMidpoint = U.get("vignetteMidpoint", rt.f(0.0))
    _u_vignetteRoundness = U.get("vignetteRoundness", rt.f(0.0))
    _u_vignetteFeather = U.get("vignetteFeather", rt.f(0.0))
    _u_vigHiProtect = U.get("vigHiProtect", rt.f(0.0))
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
    def computeVignette__vec2_vec2_float_float_float(uv, aspectRatio, midpoint, roundness, feather):
        uv = rt.copy(uv, "float")
        aspectRatio = rt.copy(aspectRatio, "float")
        centered = rt.binary("-", uv, rt.f(0.5), 2, "float")
        scale = rt.construct(2, 0.0)
        if rt.binary(">", roundness, rt.f(0.0)):
            scale = rt.component_wise("mix", aspectRatio, rt.construct(2, rt.f(1.0)), roundness, width=2)
        else:
            scale = rt.component_wise("mix", aspectRatio, rt.binary("*", aspectRatio, rt.construct(2, rt.binary("+", rt.f(1.0), rt.component_wise("abs", roundness, width=1), 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.component_wise("abs", roundness, width=1), rt.f(0.5), 1, "float"), 1, "float")), 2, "float"), rt.unary("-", roundness), width=2)
        centered = rt.binary("*", centered, scale, 2, "float")
        dist = rt.binary("*", rt.length(centered), rt.f(2.0), 1, "float")
        inner = rt.binary("-", midpoint, rt.binary("*", feather, rt.f(0.5), 1, "float"), 1, "float")
        outer = rt.binary("+", midpoint, rt.binary("*", feather, rt.f(0.5), 1, "float"), 1, "float")
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", inner, outer, dist, width=1), 1, "float")
    def applyVignette__vec3_float_float_float(rgb, vignetteMask, amount, highlightProtect):
        rgb = rt.copy(rgb, "float")
        if rt.binary("<", rt.component_wise("abs", amount, width=1), rt.f(0.001)):
            return rgb
        darken = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), vignetteMask, 1, "float"), rt.component_wise("abs", amount, width=1), 1, "float"), 1, "float")
        luma = rt.f(0.0)
        protection = rt.f(0.0)
        if rt.binary(">", highlightProtect, rt.f(0.0)):
            luma = rt.dot(rgb, g.LUMA_WEIGHTS)
            protection = rt.binary("*", rt.component_wise("smoothstep", rt.f(0.5), rt.f(1.0), luma, width=1), highlightProtect, 1, "float")
            darken = rt.component_wise("mix", darken, rt.f(1.0), protection, width=1)
        if rt.binary(">", amount, rt.f(0.0)):
            return rt.binary("*", rgb, darken, 3, "float")
        else:
            return rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), rgb, 3, "float"), darken, 3, "float"), 3, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else texSize)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        color = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if rt.binary("<", rt.component_wise("abs", _u_vignetteAmount, width=1), rt.f(0.001)):
            g.fragColor = color
            return
        rgb = srgbToLinear__vec3(rt.swizzle(color, "rgb"))
        aspectRatio = rt.construct(2, rt.f(1.0))
        if rt.binary(">", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y")):
            aspectRatio = rt.construct(2, rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float"), rt.f(1.0))
        else:
            aspectRatio = rt.construct(2, rt.f(1.0), rt.binary("/", rt.swizzle(fullRes, "y"), rt.swizzle(fullRes, "x"), 1, "float"))
        vignetteMask = computeVignette__vec2_vec2_float_float_float(globalUV, aspectRatio, _u_vignetteMidpoint, _u_vignetteRoundness, _u_vignetteFeather)
        rgb = applyVignette__vec3_float_float_float(rgb, vignetteMask, _u_vignetteAmount, _u_vigHiProtect)
        rgb = linearToSrgb__vec3(rt.component_wise("max", rgb, rt.construct(3, rt.f(0.0)), width=3))
        g.fragColor = rt.construct(4, rgb, rt.swizzle(color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
