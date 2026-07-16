def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_EXTRUDE_TYPE = U["EXTRUDE_TYPE"]
    _u_DEPTH_SOURCE = U["DEPTH_SOURCE"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_size = U["size"]
    _u_depth = U["depth"]
    _u_solidFront = U["solidFront"]
    g.fragColor = rt.construct(4, 0.0)
    g.TOP_SIGN = rt.f(1.0)
    g.SHADE_TOP = rt.f(0.8875)
    g.SHADE_BOTTOM = rt.f(0.6625)
    g.SHADE_LEFT = rt.f(0.969856)
    g.SHADE_RIGHT = rt.f(0.580144)
    g.EPS = rt.f(0.0001)
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def toSampleUV__vec2(globalPixelPos):
        globalPixelPos = rt.copy(globalPixelPos)
        return rt.component_wise("clamp", rt.binary("/", rt.binary("-", globalPixelPos, _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
    def cellAvgColor3x3__vec2(centerPx):
        centerPx = rt.copy(centerPx)
        sp = rt.binary("*", _u_size, rt.f(0.25), 1, "float")
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
    def cellHeight__vec2_vec2(cellC, cellIdxF):
        cellC = rt.copy(cellC)
        cellIdxF = rt.copy(cellIdxF)
        if rt.binary("==", _u_DEPTH_SOURCE, rt.i(1)):
            return hash12__vec2(cellIdxF)
        else:
            return lum__vec3(rt.swizzle(cellAvgColor3x3__vec2(cellC), "rgb"))
    def baryWeights__vec2_vec2_vec2_vec2(p, a, b, c):
        p = rt.copy(p)
        a = rt.copy(a)
        b = rt.copy(b)
        c = rt.copy(c)
        v0 = rt.binary("-", b, a, 2, "float")
        v1 = rt.binary("-", c, a, 2, "float")
        v2 = rt.binary("-", p, a, 2, "float")
        d00 = rt.dot(v0, v0)
        d01 = rt.dot(v0, v1)
        d11 = rt.dot(v1, v1)
        d20 = rt.dot(v2, v0)
        d21 = rt.dot(v2, v1)
        denom = rt.binary("-", rt.binary("*", d00, d11, 1, "float"), rt.binary("*", d01, d01, 1, "float"), 1, "float")
        if rt.binary("<", rt.component_wise("abs", denom, width=1), rt.f(1e-08)):
            return rt.construct(3, rt.unary("-", rt.f(2.0)))
        v = rt.binary("/", rt.binary("-", rt.binary("*", d11, d20, 1, "float"), rt.binary("*", d01, d21, 1, "float"), 1, "float"), denom, 1, "float")
        w = rt.binary("/", rt.binary("-", rt.binary("*", d00, d21, 1, "float"), rt.binary("*", d01, d20, 1, "float"), 1, "float"), denom, 1, "float")
        u = rt.binary("-", rt.binary("-", rt.f(1.0), v, 1, "float"), w, 1, "float")
        return rt.construct(3, u, v, w)
    def pyramidTriHit__vec2_vec2_vec2_vec2(P, cellC, apex, halfCell):
        P = rt.copy(P)
        cellC = rt.copy(cellC)
        apex = rt.copy(apex)
        halfCell = rt.copy(halfCell)
        topC = rt.binary("+", cellC, rt.binary("*", g.TOP_SIGN, rt.construct(2, rt.f(0.0), rt.swizzle(halfCell, "y")), 2, "float"), 2, "float")
        botC = rt.binary("-", cellC, rt.binary("*", g.TOP_SIGN, rt.construct(2, rt.f(0.0), rt.swizzle(halfCell, "y")), 2, "float"), 2, "float")
        leftX = rt.binary("-", rt.swizzle(cellC, "x"), rt.swizzle(halfCell, "x"), 1, "float")
        rightX = rt.binary("+", rt.swizzle(cellC, "x"), rt.swizzle(halfCell, "x"), 1, "float")
        Cbl = rt.construct(2, leftX, rt.swizzle(botC, "y"))
        Cbr = rt.construct(2, rightX, rt.swizzle(botC, "y"))
        Ctr = rt.construct(2, rightX, rt.swizzle(topC, "y"))
        Ctl = rt.construct(2, leftX, rt.swizzle(topC, "y"))
        bc = baryWeights__vec2_vec2_vec2_vec2(P, Cbl, Cbr, apex)
        if (bool((bool(rt.binary(">=", rt.swizzle(bc, "x"), rt.unary("-", g.EPS))) and bool(rt.binary(">=", rt.swizzle(bc, "y"), rt.unary("-", g.EPS))))) and bool(rt.binary(">=", rt.swizzle(bc, "z"), rt.unary("-", g.EPS)))):
            return rt.i(0)
        bc = baryWeights__vec2_vec2_vec2_vec2(P, Cbr, Ctr, apex)
        if (bool((bool(rt.binary(">=", rt.swizzle(bc, "x"), rt.unary("-", g.EPS))) and bool(rt.binary(">=", rt.swizzle(bc, "y"), rt.unary("-", g.EPS))))) and bool(rt.binary(">=", rt.swizzle(bc, "z"), rt.unary("-", g.EPS)))):
            return rt.i(1)
        bc = baryWeights__vec2_vec2_vec2_vec2(P, Ctr, Ctl, apex)
        if (bool((bool(rt.binary(">=", rt.swizzle(bc, "x"), rt.unary("-", g.EPS))) and bool(rt.binary(">=", rt.swizzle(bc, "y"), rt.unary("-", g.EPS))))) and bool(rt.binary(">=", rt.swizzle(bc, "z"), rt.unary("-", g.EPS)))):
            return rt.i(2)
        bc = baryWeights__vec2_vec2_vec2_vec2(P, Ctl, Cbl, apex)
        if (bool((bool(rt.binary(">=", rt.swizzle(bc, "x"), rt.unary("-", g.EPS))) and bool(rt.binary(">=", rt.swizzle(bc, "y"), rt.unary("-", g.EPS))))) and bool(rt.binary(">=", rt.swizzle(bc, "z"), rt.unary("-", g.EPS)))):
            return rt.i(3)
        return rt.unary("-", rt.i(1))
    def sideShade__vec2_vec2(P, cellC):
        P = rt.copy(P)
        cellC = rt.copy(cellC)
        d = rt.binary("-", P, cellC, 2, "float")
        dyUp = rt.binary("*", rt.swizzle(d, "y"), g.TOP_SIGN, 1, "float")
        if rt.binary(">", rt.component_wise("abs", rt.swizzle(d, "x"), width=1), rt.component_wise("abs", dyUp, width=1)):
            return (g.SHADE_RIGHT if rt.binary(">", rt.swizzle(d, "x"), rt.f(0.0)) else g.SHADE_LEFT)
        return (g.SHADE_TOP if rt.binary(">", dyUp, rt.f(0.0)) else g.SHADE_BOTTOM)
    def main__void():
        P = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        imgCenter = rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float")
        halfCell = rt.construct(2, rt.binary("*", _u_size, rt.f(0.5), 1, "float"))
        toCenter = rt.binary("-", imgCenter, P, 2, "float")
        distToCenter = rt.length(toCenter)
        stepDir = (rt.binary("/", toCenter, distToCenter, 2, "float") if rt.binary(">", distToCenter, rt.f(0.0)) else rt.construct(2, rt.f(0.0)))
        bestPriority = rt.unary("-", rt.f(1000000000.0))
        bestCenterPx = rt.construct(2, rt.f(0.0))
        bestS = rt.f(1.0)
        bestIsTop = False
        bestTri = rt.unary("-", rt.i(1))
        found = False
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", i, rt.i(6))):
                break
            t = rt.component_wise("min", rt.binary("*", rt.construct(1, i), _u_size, 1, "float"), distToCenter, width=1)
            samplePos = rt.binary("+", P, rt.binary("*", stepDir, t, 2, "float"), 2, "float")
            cellIdxF = rt.component_wise("floor", rt.binary("/", rt.binary("-", samplePos, imgCenter, 2, "float"), _u_size, 2, "float"), width=2)
            cellC = rt.binary("+", imgCenter, rt.binary("*", rt.binary("+", cellIdxF, rt.f(0.5), 2, "float"), _u_size, 2, "float"), 2, "float")
            h = cellHeight__vec2_vec2(cellC, cellIdxF)
            s = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", h, rt.binary("/", _u_depth, rt.f(100.0), 1, "float"), 1, "float"), rt.f(0.4), 1, "float"), 1, "float")
            if rt.binary("==", _u_EXTRUDE_TYPE, rt.i(1)):
                apex = rt.binary("+", imgCenter, rt.binary("*", rt.binary("-", cellC, imgCenter, 2, "float"), s, 2, "float"), 2, "float")
                tri = pyramidTriHit__vec2_vec2_vec2_vec2(P, cellC, apex, halfCell)
                if (bool(rt.binary(">=", tri, rt.i(0))) and bool(rt.binary(">", s, bestPriority))):
                    bestPriority = s
                    bestCenterPx = cellC
                    bestS = s
                    bestTri = tri
                    found = True
            else:
                faceCenter = rt.binary("+", imgCenter, rt.binary("*", rt.binary("-", cellC, imgCenter, 2, "float"), s, 2, "float"), 2, "float")
                faceHalf = rt.binary("*", halfCell, s, 2, "float")
                topHit = rt.component_wise("all", rt.component_wise("lessThanEqual", rt.component_wise("abs", rt.binary("-", P, faceCenter, 2, "float"), width=2), faceHalf, width=2), width=2)
                sideHit = (bool((not (topHit))) and bool(rt.component_wise("all", rt.component_wise("lessThanEqual", rt.component_wise("abs", rt.binary("-", P, cellC, 2, "float"), width=2), halfCell, width=2), width=2)))
                if (bool(topHit) or bool(sideHit)):
                    priority = rt.binary("+", s, (rt.f(1000.0) if topHit else rt.f(0.0)), 1, "float")
                    if rt.binary(">", priority, bestPriority):
                        bestPriority = priority
                        bestCenterPx = cellC
                        bestS = s
                        bestIsTop = topHit
                        found = True
            if rt.binary(">=", t, distToCenter):
                break
        outColor = rt.construct(4, 0.0)
        if (not (found)):
            cellC = rt.binary("+", imgCenter, rt.binary("*", rt.binary("+", rt.component_wise("floor", rt.binary("/", rt.binary("-", P, imgCenter, 2, "float"), _u_size, 2, "float"), width=2), rt.f(0.5), 2, "float"), _u_size, 2, "float"), 2, "float")
            outColor = cellAvgColor3x3__vec2(cellC)
        else:
            if rt.binary("==", _u_EXTRUDE_TYPE, rt.i(1)):
                apex = rt.binary("+", imgCenter, rt.binary("*", rt.binary("-", bestCenterPx, imgCenter, 2, "float"), bestS, 2, "float"), 2, "float")
                topC = rt.binary("+", bestCenterPx, rt.binary("*", g.TOP_SIGN, rt.construct(2, rt.f(0.0), rt.swizzle(halfCell, "y")), 2, "float"), 2, "float")
                botC = rt.binary("-", bestCenterPx, rt.binary("*", g.TOP_SIGN, rt.construct(2, rt.f(0.0), rt.swizzle(halfCell, "y")), 2, "float"), 2, "float")
                leftX = rt.binary("-", rt.swizzle(bestCenterPx, "x"), rt.swizzle(halfCell, "x"), 1, "float")
                rightX = rt.binary("+", rt.swizzle(bestCenterPx, "x"), rt.swizzle(halfCell, "x"), 1, "float")
                Cbl = rt.construct(2, leftX, rt.swizzle(botC, "y"))
                Cbr = rt.construct(2, rightX, rt.swizzle(botC, "y"))
                Ctr = rt.construct(2, rightX, rt.swizzle(topC, "y"))
                Ctl = rt.construct(2, leftX, rt.swizzle(topC, "y"))
                Ci = rt.construct(2, 0.0)
                Ci1 = rt.construct(2, 0.0)
                shadeConst = rt.f(0.0)
                if rt.binary("==", bestTri, rt.i(0)):
                    Ci = Cbl
                    Ci1 = Cbr
                    shadeConst = g.SHADE_BOTTOM
                else:
                    if rt.binary("==", bestTri, rt.i(1)):
                        Ci = Cbr
                        Ci1 = Ctr
                        shadeConst = g.SHADE_RIGHT
                    else:
                        if rt.binary("==", bestTri, rt.i(2)):
                            Ci = Ctr
                            Ci1 = Ctl
                            shadeConst = g.SHADE_TOP
                        else:
                            Ci = Ctl
                            Ci1 = Cbl
                            shadeConst = g.SHADE_LEFT
                bc = baryWeights__vec2_vec2_vec2_vec2(P, Ci, Ci1, apex)
                apexW = rt.component_wise("clamp", rt.swizzle(bc, "z"), rt.f(0.0), rt.f(1.0), width=1)
                baseColor = rt.construct(4, 0.0)
                if _u_solidFront:
                    baseColor = cellAvgColor3x3__vec2(bestCenterPx)
                else:
                    localPos = rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(bc, "x"), Ci, 2, "float"), rt.binary("*", rt.swizzle(bc, "y"), Ci1, 2, "float"), 2, "float"), rt.binary("*", rt.swizzle(bc, "z"), bestCenterPx, 2, "float"), 2, "float")
                    baseColor = rt.texture(_u_inputTex, toSampleUV__vec2(localPos))
                shade = rt.component_wise("mix", rt.f(1.0), shadeConst, apexW, width=1)
                outColor = rt.construct(4, rt.binary("*", rt.swizzle(baseColor, "rgb"), shade, 3, "float"), rt.swizzle(baseColor, "a"))
            else:
                if bestIsTop:
                    if _u_solidFront:
                        outColor = cellAvgColor3x3__vec2(bestCenterPx)
                    else:
                        localPos = rt.binary("+", imgCenter, rt.binary("/", rt.binary("-", P, imgCenter, 2, "float"), bestS, 2, "float"), 2, "float")
                        outColor = rt.texture(_u_inputTex, toSampleUV__vec2(localPos))
                else:
                    shade = sideShade__vec2_vec2(P, bestCenterPx)
                    meanColor = cellAvgColor3x3__vec2(bestCenterPx)
                    outColor = rt.construct(4, rt.binary("*", rt.swizzle(meanColor, "rgb"), shade, 3, "float"), rt.swizzle(meanColor, "a"))
        g.fragColor = outColor
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
