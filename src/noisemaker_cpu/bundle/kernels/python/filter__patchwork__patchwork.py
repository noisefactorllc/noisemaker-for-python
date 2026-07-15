def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_squareSize = U["squareSize"]
    _u_relief = U["relief"]
    _u_lightAngle = U["lightAngle"]
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def toSampleUV__vec2(globalPixelPos):
        globalPixelPos = rt.copy(globalPixelPos)
        return rt.component_wise("clamp", rt.binary("/", rt.binary("-", globalPixelPos, _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
    def cellAvgColor3x3__vec2(centerPx):
        centerPx = rt.copy(centerPx)
        sp = rt.binary("*", _u_squareSize, rt.f(0.25), 1, "float")
        sum = rt.construct(4, rt.f(0.0))
        j = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                j = rt.binary("+", j, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", j, rt.i(1))):
                break
            i = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    i = rt.binary("+", i, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", i, rt.i(1))):
                    break
                p = rt.binary("+", centerPx, rt.binary("*", rt.construct(2, rt.construct(1, i), rt.construct(1, j)), sp, 2, "float"), 2, "float")
                sum = rt.binary("+", sum, rt.texture(_u_inputTex, toSampleUV__vec2(p)), 4, "float")
        return rt.binary("*", sum, rt.binary("/", rt.f(1.0), rt.f(9.0), 1, "float"), 4, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        srcOwn = rt.texture(_u_inputTex, uv)
        imgCenter = rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float")
        relPx = rt.binary("-", globalCoord, imgCenter, 2, "float")
        cellIdxF = rt.component_wise("floor", rt.binary("/", relPx, _u_squareSize, 2, "float"), width=2)
        localPx = rt.binary("-", relPx, rt.binary("*", cellIdxF, _u_squareSize, 2, "float"), 2, "float")
        cellCenter = rt.binary("+", imgCenter, rt.binary("*", rt.binary("+", cellIdxF, rt.f(0.5), 2, "float"), _u_squareSize, 2, "float"), 2, "float")
        cellColor = rt.swizzle(cellAvgColor3x3__vec2(cellCenter), "rgb")
        h = lum__vec3(cellColor)
        topFaceShade = rt.binary("+", rt.f(0.9), rt.binary("*", rt.f(0.2), rt.binary("-", h, rt.f(0.5), 1, "float"), 1, "float"), 1, "float")
        rimPx = rt.binary("*", rt.f(0.15), _u_squareSize, 1, "float")
        dLeft = rt.swizzle(localPx, "x")
        dRight = rt.binary("-", _u_squareSize, rt.swizzle(localPx, "x"), 1, "float")
        dBottom = rt.swizzle(localPx, "y")
        dTop = rt.binary("-", _u_squareSize, rt.swizzle(localPx, "y"), 1, "float")
        dMin = rt.component_wise("min", rt.component_wise("min", dLeft, dRight, width=1), rt.component_wise("min", dBottom, dTop, width=1), width=1)
        bevelMul = rt.f(1.0)
        if rt.binary("<", dMin, rimPx):
            neighborIdx = cellIdxF
            edgeNormal = rt.construct(2, 0.0)
            if rt.binary("==", dMin, dLeft):
                neighborIdx = rt.assign_swizzle(neighborIdx, "x", rt.binary("-", rt.swizzle(neighborIdx, "x"), rt.f(1.0), 1, "float"))
                edgeNormal = rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0))
            else:
                if rt.binary("==", dMin, dRight):
                    neighborIdx = rt.assign_swizzle(neighborIdx, "x", rt.binary("+", rt.swizzle(neighborIdx, "x"), rt.f(1.0), 1, "float"))
                    edgeNormal = rt.construct(2, rt.f(1.0), rt.f(0.0))
                else:
                    if rt.binary("==", dMin, dBottom):
                        neighborIdx = rt.assign_swizzle(neighborIdx, "y", rt.binary("-", rt.swizzle(neighborIdx, "y"), rt.f(1.0), 1, "float"))
                        edgeNormal = rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0)))
                    else:
                        neighborIdx = rt.assign_swizzle(neighborIdx, "y", rt.binary("+", rt.swizzle(neighborIdx, "y"), rt.f(1.0), 1, "float"))
                        edgeNormal = rt.construct(2, rt.f(0.0), rt.f(1.0))
            neighborCenter = rt.binary("+", imgCenter, rt.binary("*", rt.binary("+", neighborIdx, rt.f(0.5), 2, "float"), _u_squareSize, 2, "float"), 2, "float")
            hNeighbor = lum__vec3(rt.swizzle(cellAvgColor3x3__vec2(neighborCenter), "rgb"))
            dh = rt.binary("-", h, hNeighbor, 1, "float")
            a = rt.component_wise("radians", _u_lightAngle, width=1)
            lightDir = rt.construct(2, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1))
            signTerm = rt.dot(edgeNormal, lightDir)
            bevelMul = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", rt.binary("*", rt.f(0.35), rt.binary("/", _u_relief, rt.f(100.0), 1, "float"), 1, "float"), rt.component_wise("sign", dh, width=1), 1, "float"), signTerm, 1, "float"), 1, "float")
        result = rt.component_wise("clamp", rt.binary("*", rt.binary("*", cellColor, topFaceShade, 3, "float"), bevelMul, 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(srcOwn, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
