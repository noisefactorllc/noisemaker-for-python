def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_STYLE = U["STYLE"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_amount = U["amount"]
    _u_angle = U["angle"]
    _u_height = U["height"]
    _u_colorAmount = U["colorAmount"]
    _u_renderScale = U["renderScale"]
    g.fragColor = rt.construct(4, 0.0)
    g.LUMA = rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722))
    def sampleGlobal__vec2(globalUV):
        globalUV = rt.copy(globalUV)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", globalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        return rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb")
    def colorDefaultEmboss__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        kernel = rt.new_array(rt.i(9), 1)
        kernel[int(rt.i(0))] = rt.unary("-", rt.f(2.0))
        kernel[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(2))] = rt.f(0.0)
        kernel[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(4))] = rt.f(1.0)
        kernel[int(rt.i(5))] = rt.f(1.0)
        kernel[int(rt.i(6))] = rt.f(0.0)
        kernel[int(rt.i(7))] = rt.f(1.0)
        kernel[int(rt.i(8))] = rt.f(2.0)
        offsets = rt.new_array(rt.i(9), 2)
        offsets[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(2))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.unary("-", rt.swizzle(texelSize, "y")))
        offsets[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.f(0.0))
        offsets[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offsets[int(rt.i(5))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.f(0.0))
        offsets[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.swizzle(texelSize, "y"))
        offsets[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(texelSize, "y"))
        offsets[int(rt.i(8))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.swizzle(texelSize, "y"))
        conv = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            texSample = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", rt.binary("*", offsets[int(i)], _u_amount, 2, "float"), _u_renderScale, 2, "float"), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", texSample, kernel[int(i)], 3, "float"), 3, "float")
        return conv
    def colorGeneralEmboss__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        kernel = rt.new_array(rt.i(9), 1)
        kernel[int(rt.i(0))] = rt.unary("-", rt.f(2.0))
        kernel[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(2))] = rt.f(0.0)
        kernel[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        kernel[int(rt.i(4))] = rt.f(1.0)
        kernel[int(rt.i(5))] = rt.f(1.0)
        kernel[int(rt.i(6))] = rt.f(0.0)
        kernel[int(rt.i(7))] = rt.f(1.0)
        kernel[int(rt.i(8))] = rt.f(2.0)
        baseOffsetsPx = rt.new_array(rt.i(9), 2)
        baseOffsetsPx[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0)))
        baseOffsetsPx[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0)))
        baseOffsetsPx[int(rt.i(2))] = rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0)))
        baseOffsetsPx[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0))
        baseOffsetsPx[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        baseOffsetsPx[int(rt.i(5))] = rt.construct(2, rt.f(1.0), rt.f(0.0))
        baseOffsetsPx[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0))
        baseOffsetsPx[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.f(1.0))
        baseOffsetsPx[int(rt.i(8))] = rt.construct(2, rt.f(1.0), rt.f(1.0))
        theta = rt.component_wise("radians", rt.binary("-", _u_angle, rt.f(135.0), 1, "float"), width=1)
        ct = rt.component_wise("cos", theta, width=1)
        st = rt.component_wise("sin", theta, width=1)
        conv = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            basePx = baseOffsetsPx[int(i)]
            rotatedPx = rt.binary("*", rt.construct(2, rt.binary("+", rt.binary("*", ct, rt.swizzle(basePx, "x"), 1, "float"), rt.binary("*", st, rt.swizzle(basePx, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.unary("-", st), rt.swizzle(basePx, "x"), 1, "float"), rt.binary("*", ct, rt.swizzle(basePx, "y"), 1, "float"), 1, "float")), _u_height, 2, "float")
            offsetUV = rt.binary("*", rt.binary("*", rt.binary("*", rotatedPx, texelSize, 2, "float"), _u_amount, 2, "float"), _u_renderScale, 2, "float")
            texSample = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, offsetUV, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", texSample, kernel[int(i)], 3, "float"), 3, "float")
        return conv
    def grayEmboss__vec2_vec3(uv, centerRGB):
        uv = rt.copy(uv)
        centerRGB = rt.copy(centerRGB)
        theta = rt.component_wise("radians", _u_angle, width=1)
        direction = rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1))
        offsetUV = rt.binary("/", rt.binary("*", direction, rt.binary("*", _u_height, _u_renderScale, 1, "float"), 2, "float"), _u_fullResolution, 2, "float")
        positiveLuma = rt.dot(sampleGlobal__vec2(rt.binary("+", uv, offsetUV, 2, "float")), g.LUMA)
        negativeLuma = rt.dot(sampleGlobal__vec2(rt.binary("-", uv, offsetUV, 2, "float")), g.LUMA)
        signedEdge = rt.binary("-", positiveLuma, negativeLuma, 1, "float")
        edgeMagnitude = rt.component_wise("abs", signedEdge, width=1)
        relief = rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), signedEdge, 1, "float"), 1, "float")
        centerLuma = rt.dot(centerRGB, g.LUMA)
        sourceChroma = rt.binary("-", centerRGB, rt.construct(3, centerLuma), 3, "float")
        tracedColor = rt.binary("*", rt.binary("*", sourceChroma, edgeMagnitude, 3, "float"), rt.component_wise("clamp", rt.binary("/", _u_colorAmount, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 3, "float")
        return rt.binary("+", rt.construct(3, relief), tracedColor, 3, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        resolution = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), resolution, 2, "float")
        origColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), resolution, 2, "float"))
        fullFrame = (bool(rt.component_wise("all", rt.component_wise("equal", _u_tileOffset, rt.construct(2, rt.f(0.0)), width=2), width=2)) and bool(rt.component_wise("all", rt.component_wise("equal", _u_fullResolution, resolution, width=2), width=2)))
        colorTexelSize = (texelSize if fullFrame else rt.binary("/", rt.f(1.0), _u_fullResolution, 2, "float"))
        result = rt.construct(3, 0.0)
        if rt.binary("==", _u_STYLE, rt.i(0)):
            if (bool(rt.binary("==", _u_angle, rt.f(135.0))) and bool(rt.binary("==", _u_height, rt.f(1.0)))):
                result = colorDefaultEmboss__vec2_vec2(uv, colorTexelSize)
            else:
                result = colorGeneralEmboss__vec2_vec2(uv, colorTexelSize)
        else:
            result = grayEmboss__vec2_vec3(uv, rt.swizzle(origColor, "rgb"))
        g.fragColor = rt.construct(4, rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(origColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
