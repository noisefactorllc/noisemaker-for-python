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
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_maskSource = U.get("maskSource", 0)
    _u_sourceChannel = U.get("sourceChannel", 0)
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_color = U.get("color", rt.construct(3, 0.0))
    _u_offsetX = U.get("offsetX", rt.f(0.0))
    _u_offsetY = U.get("offsetY", rt.f(0.0))
    _u_blur = U.get("blur", rt.f(0.0))
    _u_spread = U.get("spread", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    g.fragColor = rt.construct(4, 0.0)
    def getChannel__vec4_int(color, channel):
        color = rt.copy(color, "float")
        if rt.binary("==", channel, rt.i(0)):
            return rt.swizzle(color, "r")
        if rt.binary("==", channel, rt.i(1)):
            return rt.swizzle(color, "g")
        if rt.binary("==", channel, rt.i(2)):
            return rt.swizzle(color, "b")
        return rt.swizzle(color, "a")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        baseColor = (rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")) if rt.binary("==", _u_maskSource, rt.i(0)) else rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")))
        maskUV = rt.binary("-", uv, rt.binary("*", rt.binary("*", rt.construct(2, _u_offsetX, _u_offsetY), rt.f(0.1), 2, "float"), _u_renderScale, 2, "float"), 2, "float")
        shadowMask = rt.f(0.0)
        totalWeight = rt.f(0.0)
        blurPixels = rt.component_wise("min", rt.binary("*", _u_blur, _u_renderScale, 1, "float"), rt.f(256.0), width=1)
        sigma = rt.component_wise("max", blurPixels, rt.f(0.001), width=1)
        sigma2 = rt.binary("*", rt.binary("*", rt.f(2.0), sigma, 1, "float"), sigma, 1, "float")
        x = rt.unary("-", rt.i(5))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                x = rt.binary("+", x, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", x, rt.i(5))):
                break
            y = rt.unary("-", rt.i(5))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    y = rt.binary("+", y, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", y, rt.i(5))):
                    break
                offset = rt.binary("/", rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), blurPixels, 2, "float"), _u_resolution, 2, "float")
                sampleUV = rt.binary("+", maskUV, offset, 2, "float")
                localUV = rt.binary("/", rt.binary("-", rt.binary("*", sampleUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
                thresholded = rt.f(0.0)
                wrappedUV = rt.construct(2, 0.0)
                maskSample = rt.construct(4, 0.0)
                if rt.binary("==", _u_wrap, rt.i(0)):
                    if (bool((bool((bool(rt.binary(">=", rt.swizzle(localUV, "x"), rt.f(0.0))) and bool(rt.binary("<=", rt.swizzle(localUV, "x"), rt.f(1.0))))) and bool(rt.binary(">=", rt.swizzle(localUV, "y"), rt.f(0.0))))) and bool(rt.binary("<=", rt.swizzle(localUV, "y"), rt.f(1.0)))):
                        maskSample = (rt.texture(_u_inputTex, localUV) if rt.binary("==", _u_maskSource, rt.i(0)) else rt.texture(_u_tex, localUV))
                        thresholded = rt.component_wise("step", _u_threshold, getChannel__vec4_int(maskSample, _u_sourceChannel), width=1)
                else:
                    wrappedUV = localUV
                    if rt.binary("==", _u_wrap, rt.i(1)):
                        wrappedUV[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
                    else:
                        if rt.binary("==", _u_wrap, rt.i(2)):
                            wrappedUV[:] = rt.component_wise("fract", localUV, width=2)
                        else:
                            wrappedUV[:] = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
                    maskSample = (rt.texture(_u_inputTex, wrappedUV) if rt.binary("==", _u_maskSource, rt.i(0)) else rt.texture(_u_tex, wrappedUV))
                    thresholded = rt.component_wise("step", _u_threshold, getChannel__vec4_int(maskSample, _u_sourceChannel), width=1)
                dist2 = rt.construct(1, rt.binary("+", rt.binary("*", x, x, 1, "int"), rt.binary("*", y, y, 1, "int"), 1, "int"))
                weight = rt.component_wise("exp", rt.binary("/", rt.unary("-", dist2), sigma2, 1, "float"), width=1)
                shadowMask = rt.binary("+", shadowMask, rt.binary("*", thresholded, weight, 1, "float"), 1, "float")
                totalWeight = rt.binary("+", totalWeight, weight, 1, "float")
        shadowMask = rt.binary("/", shadowMask, totalWeight, 1, "float")
        shadowMask = rt.component_wise("clamp", rt.binary("*", shadowMask, rt.binary("+", rt.f(1.0), _u_spread, 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        withShadow = rt.component_wise("mix", rt.swizzle(baseColor, "rgb"), _u_color, shadowMask, width=3)
        fgSample = (rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")) if rt.binary("==", _u_maskSource, rt.i(0)) else rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")))
        fgMask = rt.component_wise("step", _u_threshold, getChannel__vec4_int(fgSample, _u_sourceChannel), width=1)
        result = rt.component_wise("mix", withShadow, rt.swizzle(fgSample, "rgb"), fgMask, width=3)
        g.fragColor[:] = rt.construct(4, result, rt.swizzle(baseColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
