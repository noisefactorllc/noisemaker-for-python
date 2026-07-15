def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_kernel = U["kernel"]
    _u_size = U["size"]
    _u_renderScale = U["renderScale"]
    _u_blend = U["blend"]
    _u_invert = U["invert"]
    _u_channel = U["channel"]
    _u_threshold = U["threshold"]
    _u_amount = U["amount"]
    _u_mixAmt = U["mixAmt"]
    _u_level = U["level"]
    _u_contourSide = U["contourSide"]
    g.LUMA = rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722))
    def getWeight__int_int_int(dx, dy, kernelType):
        if (bool(rt.binary("==", dx, rt.i(0))) and bool(rt.binary("==", dy, rt.i(0)))):
            return rt.f(0.0)
        if rt.binary("==", kernelType, rt.i(0)):
            if (bool(rt.binary("==", dx, rt.i(0))) or bool(rt.binary("==", dy, rt.i(0)))):
                return rt.unary("-", rt.f(1.0))
            return rt.f(0.0)
        else:
            return rt.unary("-", rt.f(1.0))
    def applyBlend__vec4_vec4_int(edge, orig, mode):
        edge = rt.copy(edge)
        orig = rt.copy(orig)
        if rt.binary("==", mode, rt.i(0)):
            return rt.component_wise("min", rt.binary("+", orig, edge, 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", mode, rt.i(1)):
            return rt.component_wise("min", orig, edge, width=4)
        if rt.binary("==", mode, rt.i(2)):
            return rt.component_wise("abs", rt.binary("-", orig, edge, 4, "float"), width=4)
        if rt.binary("==", mode, rt.i(3)):
            return rt.component_wise("min", rt.binary("/", orig, rt.component_wise("max", rt.binary("-", rt.f(1.0), edge, 4, "float"), rt.construct(4, rt.f(0.001)), width=4), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", mode, rt.i(4)):
            return rt.component_wise("max", orig, edge, width=4)
        if rt.binary("==", mode, rt.i(5)):
            return rt.binary("*", orig, edge, 4, "float")
        if rt.binary("==", mode, rt.i(7)):
            result = rt.construct(4, 0.0)
            result = rt.assign_swizzle(result, "r", (rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(orig, "r"), 1, "float"), rt.swizzle(edge, "r"), 1, "float") if rt.binary("<", rt.swizzle(orig, "r"), rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), rt.swizzle(orig, "r"), 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(edge, "r"), 1, "float"), 1, "float"), 1, "float")))
            result = rt.assign_swizzle(result, "g", (rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(orig, "g"), 1, "float"), rt.swizzle(edge, "g"), 1, "float") if rt.binary("<", rt.swizzle(orig, "g"), rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), rt.swizzle(orig, "g"), 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(edge, "g"), 1, "float"), 1, "float"), 1, "float")))
            result = rt.assign_swizzle(result, "b", (rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(orig, "b"), 1, "float"), rt.swizzle(edge, "b"), 1, "float") if rt.binary("<", rt.swizzle(orig, "b"), rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), rt.swizzle(orig, "b"), 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(edge, "b"), 1, "float"), 1, "float"), 1, "float")))
            result = rt.assign_swizzle(result, "a", rt.swizzle(orig, "a"))
            return result
        if rt.binary("==", mode, rt.i(8)):
            return rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), orig, 4, "float"), rt.binary("-", rt.f(1.0), edge, 4, "float"), 4, "float"), 4, "float")
        return edge
    def contourConv__vec2_vec2_vec3_float_bool_bool(fragCoord, texelSize, centerRGB, lvl, useLuma, upperSide):
        fragCoord = rt.copy(fragCoord)
        texelSize = rt.copy(texelSize)
        centerRGB = rt.copy(centerRGB)
        northRGB = rt.swizzle(rt.texture(_u_inputTex, rt.binary("*", rt.binary("+", fragCoord, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), texelSize, 2, "float")), "rgb")
        southRGB = rt.swizzle(rt.texture(_u_inputTex, rt.binary("*", rt.binary("+", fragCoord, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, "float"), texelSize, 2, "float")), "rgb")
        eastRGB = rt.swizzle(rt.texture(_u_inputTex, rt.binary("*", rt.binary("+", fragCoord, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), texelSize, 2, "float")), "rgb")
        westRGB = rt.swizzle(rt.texture(_u_inputTex, rt.binary("*", rt.binary("+", fragCoord, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, "float"), texelSize, 2, "float")), "rgb")
        if useLuma:
            centerL = rt.dot(centerRGB, g.LUMA)
            centerOnSide = (rt.binary(">=", centerL, lvl) if upperSide else rt.binary("<", centerL, lvl))
            crossing = (bool(centerOnSide) and bool(((bool((bool((bool(rt.binary("<", rt.dot(northRGB, g.LUMA), lvl)) or bool(rt.binary("<", rt.dot(southRGB, g.LUMA), lvl)))) or bool(rt.binary("<", rt.dot(eastRGB, g.LUMA), lvl)))) or bool(rt.binary("<", rt.dot(westRGB, g.LUMA), lvl))) if upperSide else (bool((bool((bool(rt.binary(">=", rt.dot(northRGB, g.LUMA), lvl)) or bool(rt.binary(">=", rt.dot(southRGB, g.LUMA), lvl)))) or bool(rt.binary(">=", rt.dot(eastRGB, g.LUMA), lvl)))) or bool(rt.binary(">=", rt.dot(westRGB, g.LUMA), lvl))))))
            return rt.construct(3, (rt.f(0.0) if crossing else rt.f(1.0)))
        centerOnSide = (rt.component_wise("greaterThanEqual", centerRGB, rt.construct(3, lvl), width=3) if upperSide else rt.component_wise("lessThan", centerRGB, rt.construct(3, lvl), width=3))
        crossing = rt.construct(3, (bool(rt.swizzle(centerOnSide, "r")) and bool(((bool((bool((bool(rt.binary("<", rt.swizzle(northRGB, "r"), lvl)) or bool(rt.binary("<", rt.swizzle(southRGB, "r"), lvl)))) or bool(rt.binary("<", rt.swizzle(eastRGB, "r"), lvl)))) or bool(rt.binary("<", rt.swizzle(westRGB, "r"), lvl))) if upperSide else (bool((bool((bool(rt.binary(">=", rt.swizzle(northRGB, "r"), lvl)) or bool(rt.binary(">=", rt.swizzle(southRGB, "r"), lvl)))) or bool(rt.binary(">=", rt.swizzle(eastRGB, "r"), lvl)))) or bool(rt.binary(">=", rt.swizzle(westRGB, "r"), lvl)))))), (bool(rt.swizzle(centerOnSide, "g")) and bool(((bool((bool((bool(rt.binary("<", rt.swizzle(northRGB, "g"), lvl)) or bool(rt.binary("<", rt.swizzle(southRGB, "g"), lvl)))) or bool(rt.binary("<", rt.swizzle(eastRGB, "g"), lvl)))) or bool(rt.binary("<", rt.swizzle(westRGB, "g"), lvl))) if upperSide else (bool((bool((bool(rt.binary(">=", rt.swizzle(northRGB, "g"), lvl)) or bool(rt.binary(">=", rt.swizzle(southRGB, "g"), lvl)))) or bool(rt.binary(">=", rt.swizzle(eastRGB, "g"), lvl)))) or bool(rt.binary(">=", rt.swizzle(westRGB, "g"), lvl)))))), (bool(rt.swizzle(centerOnSide, "b")) and bool(((bool((bool((bool(rt.binary("<", rt.swizzle(northRGB, "b"), lvl)) or bool(rt.binary("<", rt.swizzle(southRGB, "b"), lvl)))) or bool(rt.binary("<", rt.swizzle(eastRGB, "b"), lvl)))) or bool(rt.binary("<", rt.swizzle(westRGB, "b"), lvl))) if upperSide else (bool((bool((bool(rt.binary(">=", rt.swizzle(northRGB, "b"), lvl)) or bool(rt.binary(">=", rt.swizzle(southRGB, "b"), lvl)))) or bool(rt.binary(">=", rt.swizzle(eastRGB, "b"), lvl)))) or bool(rt.binary(">=", rt.swizzle(westRGB, "b"), lvl)))))))
        return rt.construct(3, (rt.f(0.0) if rt.swizzle(crossing, "r") else rt.f(1.0)), (rt.f(0.0) if rt.swizzle(crossing, "g") else rt.f(1.0)), (rt.f(0.0) if rt.swizzle(crossing, "b") else rt.f(1.0)))
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        texelSize = rt.binary("/", rt.f(1.0), resolution, 2, "float")
        origColor = rt.texture(_u_inputTex, rt.binary("*", rt.swizzle(ctx.frag_coord, "xy"), texelSize, 2, "float"))
        kernelType = rt.construct(1, _u_kernel, base="int")
        radius = rt.component_wise("min", rt.construct(1, rt.binary("*", rt.binary("+", _u_size, rt.f(1.0), 1, "float"), _u_renderScale, 1, "float"), base="int"), rt.i(256), width=1)
        blendMode = rt.construct(1, _u_blend, base="int")
        doInvert = rt.binary(">", _u_invert, rt.f(0.5))
        useLuma = rt.binary(">", _u_channel, rt.f(0.5))
        conv = rt.construct(3, rt.f(0.0))
        centerWeight = rt.f(0.0)
        if rt.binary("==", kernelType, rt.i(2)):
            conv = contourConv__vec2_vec2_vec3_float_bool_bool(rt.swizzle(ctx.frag_coord, "xy"), texelSize, rt.swizzle(origColor, "rgb"), rt.binary("/", _u_level, rt.f(100.0), 1, "float"), useLuma, rt.binary(">", _u_contourSide, rt.f(0.5)))
        else:
            dy = rt.unary("-", rt.i(3))
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    dy = rt.binary("+", dy, rt.i(1), 1, "int")
                _for0_first = False
                if not (rt.binary("<=", dy, rt.i(3))):
                    break
                dx = rt.unary("-", rt.i(3))
                _for1_first = True
                for _for1 in range(1048576):
                    if not _for1_first:
                        dx = rt.binary("+", dx, rt.i(1), 1, "int")
                    _for1_first = False
                    if not (rt.binary("<=", dx, rt.i(3))):
                        break
                    if (bool(rt.binary(">", rt.component_wise("abs", dx, width=1), radius)) or bool(rt.binary(">", rt.component_wise("abs", dy, width=1), radius))):
                        continue
                    if (bool(rt.binary("==", dx, rt.i(0))) and bool(rt.binary("==", dy, rt.i(0)))):
                        continue
                    w = getWeight__int_int_int(dx, dy, kernelType)
                    if rt.binary("==", w, rt.f(0.0)):
                        continue
                    sampleCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.construct(1, dx), rt.construct(1, dy)), 2, "float")
                    localUV = rt.binary("*", sampleCoord, texelSize, 2, "float")
                    s = rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb")
                    if useLuma:
                        conv = rt.binary("+", conv, rt.binary("*", rt.construct(3, rt.dot(s, g.LUMA)), w, 3, "float"), 3, "float")
                    else:
                        conv = rt.binary("+", conv, rt.binary("*", s, w, 3, "float"), 3, "float")
                    centerWeight = rt.binary("-", centerWeight, w, 1, "float")
            centerSample = rt.swizzle(origColor, "rgb")
            if useLuma:
                centerSample = rt.construct(3, rt.dot(centerSample, g.LUMA))
            conv = rt.binary("+", conv, rt.binary("*", centerSample, centerWeight, 3, "float"), 3, "float")
        conv = rt.binary("*", conv, rt.binary("/", _u_amount, rt.f(50.0), 1, "float"), 3, "float")
        conv = rt.component_wise("clamp", conv, rt.f(0.0), rt.f(1.0), width=3)
        if rt.binary(">", _u_threshold, rt.f(0.0)):
            thresh = rt.binary("/", _u_threshold, rt.f(100.0), 1, "float")
            edge = rt.f(0.0)
            if useLuma:
                edge = rt.swizzle(conv, "r")
            else:
                edge = rt.dot(conv, g.LUMA)
            mask = rt.component_wise("smoothstep", rt.binary("-", thresh, rt.f(0.01), 1, "float"), rt.binary("+", thresh, rt.f(0.01), 1, "float"), edge, width=1)
            conv = rt.binary("*", conv, mask, 3, "float")
        if doInvert:
            conv = rt.binary("-", rt.f(1.0), conv, 3, "float")
        edgeColor = rt.construct(4, conv, rt.swizzle(origColor, "a"))
        blended = applyBlend__vec4_vec4_int(edgeColor, origColor, blendMode)
        m = rt.binary("/", _u_mixAmt, rt.f(100.0), 1, "float")
        g.fragColor = rt.construct(4, rt.component_wise("mix", rt.swizzle(origColor, "rgb"), rt.swizzle(blended, "rgb"), m, width=3), rt.swizzle(origColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
