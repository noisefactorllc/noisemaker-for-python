def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_LP_BORDER = U.get("LP_BORDER", 0)
    _u_LP_LIGHT = U.get("LP_LIGHT", 0)
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    _u_mode = U.get("mode", 0)
    _u_edgeStrength = U.get("edgeStrength", rt.f(0.0))
    _u_edgeColor = U.get("edgeColor", rt.construct(3, 0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530718)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def hash2__vec2_float(p, s):
        p = rt.copy(p, "float")
        v = pcg__uvec3(rt.construct(3, rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", s, rt.f(2.0), 1, "float") if rt.binary(">=", s, rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", s), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), base="uint"))
        return rt.binary("/", rt.construct(2, rt.swizzle(v, "xy")), rt.construct(1, rt.i(4294967295)), 2, "float")
    def lowPolySite__ivec2_float_float_float(siteCell, n, s, spd):
        siteCell = rt.copy(siteCell, "int")
        siteCellF = rt.construct(2, siteCell)
        offset = hash2__vec2_float(siteCellF, s)
        animRand = rt.construct(2, 0.0)
        angle = rt.f(0.0)
        radius = rt.f(0.0)
        if rt.binary(">", spd, rt.f(0.0)):
            animRand = hash2__vec2_float(siteCellF, rt.binary("+", s, rt.f(100.0), 1, "float"))
            angle = rt.binary("+", rt.binary("*", _u_time, g.TAU, 1, "float"), rt.binary("*", rt.swizzle(animRand, "x"), g.TAU, 1, "float"), 1, "float")
            radius = rt.binary("*", rt.swizzle(animRand, "y"), spd, 1, "float")
            offset[:] = rt.component_wise("clamp", rt.binary("+", offset, rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), radius, 2, "float"), 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
        return rt.binary("/", rt.binary("+", siteCellF, offset, 2, "float"), n, 2, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), resolution, 2, "float")
        n = rt.component_wise("max", rt.binary("-", rt.f(102.0), _u_scale, 1, "float"), rt.f(2.0), width=1)
        s = _u_seed
        spd = rt.binary("*", _u_speed, rt.f(0.3), 1, "float")
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        auv = rt.construct(2, rt.binary("*", rt.swizzle(globalUV, "x"), aspect, 1, "float"), rt.swizzle(globalUV, "y"))
        scaled = rt.binary("*", auv, n, 2, "float")
        cell = rt.construct(2, rt.component_wise("floor", scaled, width=2), base="int")
        minDist = rt.f(10000000000.0)
        secondDist = rt.f(10000000000.0)
        thirdDist = rt.f(10000000000.0)
        nearestPoint = rt.construct(2, rt.f(0.0))
        nearestCell = rt.construct(2, 0.0, base="int")
        if rt.binary(">", _u_LP_BORDER, rt.i(0)):
            nearestCell = rt.construct(2, rt.i(0), base="int")
        dy = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dy, rt.i(1))):
                break
            dx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", dx, rt.i(1))):
                    break
                neighbor = rt.binary("+", cell, rt.construct(2, dx, dy, base="int"), 2, "int")
                neighborF = rt.construct(2, neighbor)
                offset = hash2__vec2_float(neighborF, s)
                animRand = rt.construct(2, 0.0)
                angle = rt.f(0.0)
                radius = rt.f(0.0)
                if rt.binary(">", spd, rt.f(0.0)):
                    animRand = hash2__vec2_float(neighborF, rt.binary("+", s, rt.f(100.0), 1, "float"))
                    angle = rt.binary("+", rt.binary("*", _u_time, g.TAU, 1, "float"), rt.binary("*", rt.swizzle(animRand, "x"), g.TAU, 1, "float"), 1, "float")
                    radius = rt.binary("*", rt.swizzle(animRand, "y"), spd, 1, "float")
                    offset[:] = rt.component_wise("clamp", rt.binary("+", offset, rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), radius, 2, "float"), 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
                point = rt.binary("/", rt.binary("+", neighborF, offset, 2, "float"), n, 2, "float")
                d = rt.distance(auv, point)
                if rt.binary("<", d, minDist):
                    thirdDist = secondDist
                    secondDist = minDist
                    minDist = d
                    nearestPoint[:] = point
                    if rt.binary(">", _u_LP_BORDER, rt.i(0)):
                        nearestCell[:] = neighbor
                else:
                    if rt.binary("<", d, secondDist):
                        thirdDist = secondDist
                        secondDist = d
                    else:
                        if rt.binary("<", d, thirdDist):
                            thirdDist = d
        globalUV_sample = rt.construct(2, rt.binary("/", rt.swizzle(nearestPoint, "x"), aspect, 1, "float"), rt.swizzle(nearestPoint, "y"))
        localUV_sample = rt.binary("/", rt.binary("-", rt.binary("*", globalUV_sample, resolution, 2, "float"), _u_tileOffset, 2, "float"), tileDims, 2, "float")
        cellColor = rt.texture(_u_inputTex, localUV_sample)
        result = rt.construct(3, 0.0)
        edgeDist = rt.f(0.0)
        edgeFactor = rt.f(0.0)
        selectedDist = rt.f(0.0)
        raw = rt.f(0.0)
        distField = rt.f(0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            result[:] = rt.swizzle(cellColor, "rgb")
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                edgeDist = rt.component_wise("clamp", rt.binary("*", rt.binary("*", rt.binary("-", secondDist, minDist, 1, "float"), n, 1, "float"), rt.f(2.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                edgeFactor = rt.component_wise("mix", _u_edgeStrength, rt.f(0.0), edgeDist, width=1)
                result[:] = rt.component_wise("mix", rt.swizzle(cellColor, "rgb"), _u_edgeColor, edgeFactor, width=3)
            else:
                selectedDist = (secondDist if rt.binary("==", _u_mode, rt.i(2)) else thirdDist)
                raw = rt.component_wise("clamp", rt.binary("*", selectedDist, n, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                distField = rt.component_wise("pow", raw, rt.component_wise("mix", rt.f(0.5), rt.f(3.0), _u_edgeStrength, width=1), width=1)
                result[:] = rt.binary("*", rt.swizzle(cellColor, "rgb"), distField, 3, "float")
        modeResult = rt.construct(3, 0.0)
        borderMask = rt.f(0.0)
        if (bool(rt.binary(">", _u_LP_BORDER, rt.i(0))) or bool(rt.binary(">", _u_LP_LIGHT, rt.i(0)))):
            modeResult = result
            borderMask = rt.f(0.0)
        if rt.binary(">", _u_LP_BORDER, rt.i(0)):
            borderNearestPoint = nearestPoint
            borderNearestCell = nearestCell
            borderNearestDist = minDist
            dy = rt.unary("-", rt.i(2))
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    dy = rt.binary("+", dy, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<=", dy, rt.i(2))):
                    break
                dx = rt.unary("-", rt.i(2))
                _for3_first = True
                for _for3 in range(1048576):
                    if not _for3_first:
                        dx = rt.binary("+", dx, rt.i(1), 1, "int")
                    _for3_first = False
                    if not (rt.binary("<=", dx, rt.i(2))):
                        break
                    candidateCell = rt.binary("+", cell, rt.construct(2, dx, dy, base="int"), 2, "int")
                    candidatePoint = lowPolySite__ivec2_float_float_float(candidateCell, n, s, spd)
                    candidateDist = rt.distance(auv, candidatePoint)
                    if rt.binary("<", candidateDist, borderNearestDist):
                        borderNearestDist = candidateDist
                        borderNearestPoint[:] = candidatePoint
                        borderNearestCell[:] = candidateCell
            distToEdge = rt.f(10000000000.0)
            dy = rt.unary("-", rt.i(2))
            _for4_first = True
            for _for4 in range(1048576):
                if not _for4_first:
                    dy = rt.binary("+", dy, rt.i(1), 1, "int")
                _for4_first = False
                if not (rt.binary("<=", dy, rt.i(2))):
                    break
                dx = rt.unary("-", rt.i(2))
                _for5_first = True
                for _for5 in range(1048576):
                    if not _for5_first:
                        dx = rt.binary("+", dx, rt.i(1), 1, "int")
                    _for5_first = False
                    if not (rt.binary("<=", dx, rt.i(2))):
                        break
                    candidateCell = rt.binary("+", cell, rt.construct(2, dx, dy, base="int"), 2, "int")
                    candidatePoint = rt.construct(2, 0.0)
                    siteVector = rt.construct(2, 0.0)
                    siteDistance = rt.f(0.0)
                    bisectorDistance = rt.f(0.0)
                    if rt.component_wise("any", rt.component_wise("notEqual", candidateCell, borderNearestCell, width=2), width=2):
                        candidatePoint = lowPolySite__ivec2_float_float_float(candidateCell, n, s, spd)
                        siteVector = rt.binary("-", candidatePoint, borderNearestPoint, 2, "float")
                        siteDistance = rt.component_wise("max", rt.length(siteVector), rt.f(1e-08), width=1)
                        bisectorDistance = rt.dot(rt.binary("-", rt.binary("*", rt.binary("+", borderNearestPoint, candidatePoint, 2, "float"), rt.f(0.5), 2, "float"), auv, 2, "float"), rt.binary("/", siteVector, siteDistance, 2, "float"))
                        distToEdge = rt.component_wise("min", distToEdge, bisectorDistance, width=1)
            cellRadius = rt.binary("/", rt.f(0.5), n, 1, "float")
            borderHalfWidth = rt.binary("*", rt.binary("/", rt.construct(1, _u_LP_BORDER), rt.f(100.0), 1, "float"), cellRadius, 1, "float")
            borderFeather = rt.component_wise("max", rt.fwidth(distToEdge), rt.f(1e-06), width=1)
            borderMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", borderHalfWidth, borderFeather, 1, "float"), rt.binary("+", borderHalfWidth, borderFeather, 1, "float"), distToEdge, width=1), 1, "float")
            result[:] = rt.component_wise("mix", modeResult, _u_edgeColor, borderMask, width=3)
        if rt.binary(">", _u_LP_LIGHT, rt.i(0)):
            intensity = rt.component_wise("clamp", rt.binary("/", rt.construct(1, _u_LP_LIGHT), rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
            paneValue = rt.component_wise("max", rt.component_wise("max", rt.swizzle(modeResult, "r"), rt.swizzle(modeResult, "g"), width=1), rt.swizzle(modeResult, "b"), width=1)
            exposure = rt.component_wise("mix", rt.f(1.0), rt.f(2.25), intensity, width=1)
            litValue = rt.binary("-", rt.f(1.0), rt.component_wise("pow", rt.component_wise("max", rt.binary("-", rt.f(1.0), paneValue, 1, "float"), rt.f(0.0), width=1), exposure, width=1), 1, "float")
            litMode = (rt.binary("*", modeResult, rt.binary("/", litValue, paneValue, 1, "float"), 3, "float") if rt.binary(">", paneValue, rt.f(1e-06)) else modeResult)
            result[:] = rt.component_wise("mix", litMode, _u_edgeColor, borderMask, width=3)
        original = rt.texture(_u_inputTex, uv)
        g.fragColor[:] = rt.construct(4, rt.component_wise("mix", rt.swizzle(original, "rgb"), result, _u_alpha, width=3), rt.swizzle(original, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
