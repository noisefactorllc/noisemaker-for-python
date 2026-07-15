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
    _u_renderScale = U["renderScale"]
    _u_mode = U["mode"]
    _u_depth = U["depth"]
    _u_density = U["density"]
    _u_seed = U["seed"]
    _u_fill = U["fill"]
    _u_outline = U["outline"]
    _u_inputMix = U["inputMix"]
    _u_wrap = U["wrap"]
    _u_time = U["time"]
    _u_speed = U["speed"]
    g.PHI = rt.f(1.618033988749895)
    def pcg__uvec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, rt.construct(1, rt.swizzle(p, "x"), base="uint"), rt.construct(1, rt.swizzle(p, "y"), base="uint"), rt.construct(1, rt.swizzle(p, "z"), base="uint"), base="uint"))), rt.construct(1, rt.i(4294967295)), 3, "float")
    def cellRand__vec2_float_float_float(cellMin, level, channel, animSeed):
        cellMin = rt.copy(cellMin)
        cx = rt.component_wise("floor", rt.binary("*", rt.swizzle(cellMin, "x"), rt.f(1000.0), 1, "float"), width=1)
        cy = rt.component_wise("floor", rt.binary("*", rt.swizzle(cellMin, "y"), rt.f(1000.0), 1, "float"), width=1)
        return rt.swizzle(prng__vec3(rt.construct(3, rt.binary("+", cx, rt.binary("*", level, rt.f(7.0), 1, "float"), 1, "float"), rt.binary("+", cy, rt.binary("*", level, rt.f(13.0), 1, "float"), 1, "float"), rt.binary("+", rt.binary("+", _u_seed, channel, 1, "float"), rt.binary("*", animSeed, rt.f(100.0), 1, "float"), 1, "float"))), "x")
    def circleShape__vec2(centered):
        centered = rt.copy(centered)
        return rt.component_wise("step", rt.length(centered), rt.f(0.32), width=1)
    def diamondShape__vec2(centered):
        centered = rt.copy(centered)
        return rt.component_wise("step", rt.binary("+", rt.component_wise("abs", rt.swizzle(centered, "x"), width=1), rt.component_wise("abs", rt.swizzle(centered, "y"), width=1), 1, "float"), rt.f(0.32), width=1)
    def squareShape__vec2(centered):
        centered = rt.copy(centered)
        return rt.component_wise("step", rt.component_wise("max", rt.component_wise("abs", rt.swizzle(centered, "x"), width=1), rt.component_wise("abs", rt.swizzle(centered, "y"), width=1), width=1), rt.f(0.28), width=1)
    def arcShape__vec2_float_float_float(centered, halfW, halfH, h):
        centered = rt.copy(centered)
        corner = rt.construct(1, rt.binary("*", h, rt.f(4.0), 1, "float"), base="int")
        origin = rt.construct(2, 0.0)
        if rt.binary("==", corner, rt.i(0)):
            origin = rt.construct(2, rt.unary("-", halfW), rt.unary("-", halfH))
        else:
            if rt.binary("==", corner, rt.i(1)):
                origin = rt.construct(2, halfW, rt.unary("-", halfH))
            else:
                if rt.binary("==", corner, rt.i(2)):
                    origin = rt.construct(2, rt.unary("-", halfW), halfH)
                else:
                    origin = rt.construct(2, halfW, halfH)
        dist = rt.length(rt.binary("-", centered, origin, 2, "float"))
        return rt.binary("*", rt.component_wise("step", dist, rt.f(0.7), width=1), rt.binary("-", rt.f(1.0), rt.component_wise("step", dist, rt.f(0.5), width=1), 1, "float"), 1, "float")
    def drawShape__int_vec2_float_float_float(shapeType, centered, halfW, halfH, h):
        centered = rt.copy(centered)
        if rt.binary("==", shapeType, rt.i(0)):
            return rt.f(1.0)
        if rt.binary("==", shapeType, rt.i(1)):
            return circleShape__vec2(centered)
        if rt.binary("==", shapeType, rt.i(2)):
            return diamondShape__vec2(centered)
        if rt.binary("==", shapeType, rt.i(3)):
            return squareShape__vec2(centered)
        if rt.binary("==", shapeType, rt.i(4)):
            return arcShape__vec2_float_float_float(centered, halfW, halfH, h)
        return rt.f(1.0)
    def shadeFromHash__float(h):
        idx = rt.construct(1, rt.binary("*", h, rt.f(5.0), 1, "float"), base="int")
        if rt.binary("==", idx, rt.i(0)):
            return rt.f(0.15)
        if rt.binary("==", idx, rt.i(1)):
            return rt.f(0.35)
        if rt.binary("==", idx, rt.i(2)):
            return rt.f(0.55)
        if rt.binary("==", idx, rt.i(3)):
            return rt.f(0.75)
        return rt.f(1.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        maxDepth = rt.construct(1, _u_depth, base="int")
        dens = rt.binary("/", _u_density, rt.f(100.0), 1, "float")
        fillType = rt.construct(1, _u_fill, base="int")
        modeType = rt.construct(1, _u_mode, base="int")
        spd = rt.binary("*", rt.component_wise("floor", _u_speed, width=1), rt.f(2.0), 1, "float")
        outlineWidthX = rt.binary("/", rt.binary("*", _u_outline, _u_renderScale, 1, "float"), rt.swizzle(_u_fullResolution, "x"), 1, "float")
        outlineWidthY = rt.binary("/", rt.binary("*", _u_outline, _u_renderScale, 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        cellMin = rt.construct(2, rt.f(0.0))
        cellMax = rt.construct(2, rt.f(1.0))
        isOutline = False
        level = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                level = rt.binary("+", level, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", level, rt.i(6))):
                break
            if rt.binary(">=", level, maxDepth):
                break
            levelTime = rt.component_wise("floor", rt.binary("+", rt.binary("*", _u_time, spd, 1, "float"), rt.binary("*", rt.construct(1, level), g.PHI, 1, "float"), 1, "float"), width=1)
            h = cellRand__vec2_float_float_float(cellMin, rt.construct(1, level), rt.f(0.0), levelTime)
            if rt.binary("<", h, dens):
                cellW = rt.binary("*", rt.binary("-", rt.swizzle(cellMax, "x"), rt.swizzle(cellMin, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "x"), 1, "float")
                cellH = rt.binary("*", rt.binary("-", rt.swizzle(cellMax, "y"), rt.swizzle(cellMin, "y"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
                canSplitH = rt.binary(">=", rt.binary("/", rt.component_wise("min", cellW, rt.binary("*", cellH, rt.f(0.5), 1, "float"), width=1), rt.component_wise("max", cellW, rt.binary("*", cellH, rt.f(0.5), 1, "float"), width=1), 1, "float"), rt.f(0.2))
                canSplitV = rt.binary(">=", rt.binary("/", rt.component_wise("min", rt.binary("*", cellW, rt.f(0.5), 1, "float"), cellH, width=1), rt.component_wise("max", rt.binary("*", cellW, rt.f(0.5), 1, "float"), cellH, width=1), 1, "float"), rt.f(0.2))
                if rt.binary("==", modeType, rt.i(0)):
                    dir = cellRand__vec2_float_float_float(cellMin, rt.construct(1, level), rt.f(1.0), levelTime)
                    splitDir = rt.unary("-", rt.i(1))
                    if rt.binary("<", dir, rt.f(0.5)):
                        if canSplitH:
                            splitDir = rt.i(0)
                        else:
                            if canSplitV:
                                splitDir = rt.i(1)
                    else:
                        if canSplitV:
                            splitDir = rt.i(1)
                        else:
                            if canSplitH:
                                splitDir = rt.i(0)
                    if rt.binary("==", splitDir, rt.i(0)):
                        mid = rt.binary("*", rt.binary("+", rt.swizzle(cellMin, "y"), rt.swizzle(cellMax, "y"), 1, "float"), rt.f(0.5), 1, "float")
                        if rt.binary("<", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), mid, 1, "float"), width=1), outlineWidthY):
                            isOutline = True
                        if rt.binary("<", rt.swizzle(st, "y"), mid):
                            cellMax = rt.assign_swizzle(cellMax, "y", mid)
                        else:
                            cellMin = rt.assign_swizzle(cellMin, "y", mid)
                    else:
                        if rt.binary("==", splitDir, rt.i(1)):
                            mid = rt.binary("*", rt.binary("+", rt.swizzle(cellMin, "x"), rt.swizzle(cellMax, "x"), 1, "float"), rt.f(0.5), 1, "float")
                            if rt.binary("<", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), mid, 1, "float"), width=1), outlineWidthX):
                                isOutline = True
                            if rt.binary("<", rt.swizzle(st, "x"), mid):
                                cellMax = rt.assign_swizzle(cellMax, "x", mid)
                            else:
                                cellMin = rt.assign_swizzle(cellMin, "x", mid)
                else:
                    if (bool(canSplitH) and bool(canSplitV)):
                        mid = rt.binary("*", rt.binary("+", cellMin, cellMax, 2, "float"), rt.f(0.5), 2, "float")
                        if (bool(rt.binary("<", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(mid, "x"), 1, "float"), width=1), outlineWidthX)) or bool(rt.binary("<", rt.component_wise("abs", rt.binary("-", rt.swizzle(st, "y"), rt.swizzle(mid, "y"), 1, "float"), width=1), outlineWidthY))):
                            isOutline = True
                        if rt.binary("<", rt.swizzle(st, "x"), rt.swizzle(mid, "x")):
                            cellMax = rt.assign_swizzle(cellMax, "x", rt.swizzle(mid, "x"))
                        else:
                            cellMin = rt.assign_swizzle(cellMin, "x", rt.swizzle(mid, "x"))
                        if rt.binary("<", rt.swizzle(st, "y"), rt.swizzle(mid, "y")):
                            cellMax = rt.assign_swizzle(cellMax, "y", rt.swizzle(mid, "y"))
                        else:
                            cellMin = rt.assign_swizzle(cellMin, "y", rt.swizzle(mid, "y"))
        cellSize = rt.binary("-", cellMax, cellMin, 2, "float")
        cellUv = rt.binary("/", rt.binary("-", st, cellMin, 2, "float"), cellSize, 2, "float")
        cellPixelW = rt.binary("*", rt.swizzle(cellSize, "x"), rt.swizzle(_u_fullResolution, "x"), 1, "float")
        cellPixelH = rt.binary("*", rt.swizzle(cellSize, "y"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        minDim = rt.component_wise("min", cellPixelW, cellPixelH, width=1)
        centered = rt.binary("-", cellUv, rt.f(0.5), 2, "float")
        centered = rt.assign_swizzle(centered, "x", rt.binary("*", rt.swizzle(centered, "x"), rt.binary("/", cellPixelW, minDim, 1, "float"), 1, "float"))
        centered = rt.assign_swizzle(centered, "y", rt.binary("*", rt.swizzle(centered, "y"), rt.binary("/", cellPixelH, minDim, 1, "float"), 1, "float"))
        halfW = rt.binary("*", rt.binary("/", cellPixelW, minDim, 1, "float"), rt.f(0.5), 1, "float")
        halfH = rt.binary("*", rt.binary("/", cellPixelH, minDim, 1, "float"), rt.f(0.5), 1, "float")
        visualT = rt.binary("+", rt.binary("*", _u_time, spd, 1, "float"), rt.binary("*", g.PHI, rt.f(7.0), 1, "float"), 1, "float")
        curVisualTime = rt.component_wise("floor", visualT, width=1)
        nextVisualTime = rt.binary("+", curVisualTime, rt.f(1.0), 1, "float")
        visualBlend = rt.component_wise("smoothstep", rt.f(0.0), rt.f(1.0), rt.component_wise("fract", visualT, width=1), width=1)
        shade = rt.component_wise("mix", shadeFromHash__float(cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(2.0), curVisualTime)), shadeFromHash__float(cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(2.0), nextVisualTime)), visualBlend, width=1)
        bgShade = rt.component_wise("mix", shadeFromHash__float(cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(8.0), curVisualTime)), shadeFromHash__float(cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(8.0), nextVisualTime)), visualBlend, width=1)
        curShapeType = fillType
        nextShapeType = fillType
        if rt.binary("==", modeType, rt.i(0)):
            curShapeType = rt.i(0)
            nextShapeType = rt.i(0)
        else:
            if rt.binary("==", fillType, rt.i(5)):
                curShapeType = rt.construct(1, rt.binary("*", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(3.0), curVisualTime), rt.f(5.0), 1, "float"), base="int")
                nextShapeType = rt.construct(1, rt.binary("*", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(3.0), nextVisualTime), rt.f(5.0), 1, "float"), base="int")
        curCorner = cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(4.0), curVisualTime)
        nextCorner = cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(4.0), nextVisualTime)
        curMask = drawShape__int_vec2_float_float_float(curShapeType, centered, halfW, halfH, curCorner)
        nextMask = drawShape__int_vec2_float_float_float(nextShapeType, centered, halfW, halfH, nextCorner)
        shapeMask = rt.component_wise("mix", curMask, nextMask, visualBlend, width=1)
        color = rt.component_wise("mix", bgShade, shade, shapeMask, width=1)
        result = rt.construct(3, color)
        blend = rt.binary("/", _u_inputMix, rt.f(100.0), 1, "float")
        if rt.binary(">", blend, rt.f(0.0)):
            curTexScale = rt.binary("+", rt.f(0.3), rt.binary("*", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(5.0), curVisualTime), rt.f(0.7), 1, "float"), 1, "float")
            nextTexScale = rt.binary("+", rt.f(0.3), rt.binary("*", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(5.0), nextVisualTime), rt.f(0.7), 1, "float"), 1, "float")
            texScale = rt.component_wise("mix", curTexScale, nextTexScale, visualBlend, width=1)
            texUv = cellUv
            cellAspect = rt.binary("/", rt.binary("*", rt.swizzle(cellSize, "x"), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.binary("*", rt.swizzle(cellSize, "y"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float")
            texAspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
            ratio = rt.binary("/", cellAspect, texAspect, 1, "float")
            if rt.binary(">", ratio, rt.f(1.0)):
                texUv = rt.assign_swizzle(texUv, "x", rt.binary("+", rt.f(0.5), rt.binary("*", rt.binary("-", rt.swizzle(texUv, "x"), rt.f(0.5), 1, "float"), ratio, 1, "float"), 1, "float"))
            else:
                texUv = rt.assign_swizzle(texUv, "y", rt.binary("+", rt.f(0.5), rt.binary("/", rt.binary("-", rt.swizzle(texUv, "y"), rt.f(0.5), 1, "float"), ratio, 1, "float"), 1, "float"))
            texUv = rt.binary("*", texUv, texScale, 2, "float")
            texUv = rt.assign_swizzle(texUv, "x", rt.binary("+", rt.swizzle(texUv, "x"), rt.binary("*", rt.component_wise("mix", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(6.0), curVisualTime), cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(6.0), nextVisualTime), visualBlend, width=1), rt.binary("-", rt.f(1.0), texScale, 1, "float"), 1, "float"), 1, "float"))
            texUv = rt.assign_swizzle(texUv, "y", rt.binary("+", rt.swizzle(texUv, "y"), rt.binary("*", rt.component_wise("mix", cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(7.0), curVisualTime), cellRand__vec2_float_float_float(cellMin, rt.f(0.0), rt.f(7.0), nextVisualTime), visualBlend, width=1), rt.binary("-", rt.f(1.0), texScale, 1, "float"), 1, "float"), 1, "float"))
            wrapMode = rt.construct(1, _u_wrap, base="int")
            if rt.binary("==", wrapMode, rt.i(0)):
                texUv = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", texUv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
            else:
                if rt.binary("==", wrapMode, rt.i(1)):
                    texUv = rt.component_wise("mod", texUv, rt.f(1.0), width=2)
                else:
                    texUv = rt.component_wise("clamp", texUv, rt.f(0.0), rt.f(1.0), width=2)
            inputColor = rt.swizzle(rt.texture(_u_inputTex, texUv), "rgb")
            result = rt.component_wise("mix", result, inputColor, blend, width=3)
        if (bool(isOutline) and bool(rt.binary(">", _u_outline, rt.f(0.0)))):
            result = rt.construct(3, rt.f(0.0))
        g.fragColor = rt.construct(4, result, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
