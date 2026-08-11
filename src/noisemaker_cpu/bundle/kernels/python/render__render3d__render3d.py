def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_FILTERING = U.get("FILTERING", 0)
    _u_INVERT = U.get("INVERT", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_orbitSpeed = U.get("orbitSpeed", 0)
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_volumeCache = T["volumeCache"]
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    g.PI = rt.f(3.141592653589793)
    g.MAX_STEPS = rt.i(256)
    g.MAX_DIST = rt.f(10.0)
    def atlasTexel__ivec3_int(p, volSize):
        p = rt.copy(p, "int")
        return rt.construct(2, rt.swizzle(p, "x"), rt.binary("+", rt.swizzle(p, "y"), rt.binary("*", rt.swizzle(p, "z"), volSize, 1, "int"), 1, "int"), base="int")
    def sampleVoxel__ivec3(voxel):
        voxel = rt.copy(voxel, "int")
        volSize = _u_volumeSize
        clamped = rt.component_wise("clamp", voxel, rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", volSize, rt.i(1), 1, "int"), base="int"), width=3)
        return rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(clamped, volSize), rt.i(0))
    def sampleVolume__vec3(worldPos):
        worldPos = rt.copy(worldPos, "float")
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        uvw = rt.binary("+", rt.binary("*", worldPos, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        uvw[:] = rt.component_wise("clamp", uvw, rt.f(0.0), rt.f(1.0), width=3)
        texelPos = rt.binary("*", uvw, rt.binary("-", volSizeF, rt.f(1.0), 1, "float"), 3, "float")
        texelFloor = rt.component_wise("floor", texelPos, width=3)
        frac = rt.binary("-", texelPos, texelFloor, 3, "float")
        i0 = rt.construct(3, texelFloor, base="int")
        i1 = rt.component_wise("min", rt.binary("+", i0, rt.i(1), 3, "int"), rt.binary("-", volSize, rt.i(1), 1, "int"), width=3)
        c000 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i0, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c100 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i0, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c010 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i1, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c110 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i1, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c001 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i0, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c101 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i0, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c011 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i1, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c111 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i1, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c00 = rt.component_wise("mix", c000, c100, rt.swizzle(frac, "x"), width=4)
        c10 = rt.component_wise("mix", c010, c110, rt.swizzle(frac, "x"), width=4)
        c01 = rt.component_wise("mix", c001, c101, rt.swizzle(frac, "x"), width=4)
        c11 = rt.component_wise("mix", c011, c111, rt.swizzle(frac, "x"), width=4)
        c0 = rt.component_wise("mix", c00, c10, rt.swizzle(frac, "y"), width=4)
        c1 = rt.component_wise("mix", c01, c11, rt.swizzle(frac, "y"), width=4)
        return rt.component_wise("mix", c0, c1, rt.swizzle(frac, "z"), width=4)
    def getField__vec3(p):
        p = rt.copy(p, "float")
        val = rt.swizzle(sampleVolume__vec3(p), "r")
        if _u_INVERT:
            val = rt.binary("-", rt.f(1.0), val, 1, "float")
        return rt.binary("-", _u_threshold, val, 1, "float")
    def isVoxelSolid__ivec3(voxel):
        voxel = rt.copy(voxel, "int")
        val = rt.swizzle(sampleVoxel__ivec3(voxel), "r")
        if _u_INVERT:
            val = rt.binary("-", rt.f(1.0), val, 1, "float")
        return rt.binary(">", val, _u_threshold)
    def worldToVoxel__vec3(worldPos):
        worldPos = rt.copy(worldPos, "float")
        volSize = _u_volumeSize
        uvw = rt.binary("+", rt.binary("*", worldPos, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        return rt.construct(3, rt.component_wise("floor", rt.binary("*", uvw, rt.construct(1, volSize), 3, "float"), width=3), base="int")
    def voxelToWorld__ivec3(voxel):
        voxel = rt.copy(voxel, "int")
        volSize = _u_volumeSize
        uvw = rt.binary("/", rt.binary("+", rt.construct(3, voxel), rt.f(0.5), 3, "float"), rt.construct(1, volSize), 3, "float")
        return rt.binary("-", rt.binary("*", uvw, rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
    def voxelTrace__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        result = [rt.f(0.0), rt.construct(3, 0.0), rt.construct(3, 0.0, base="int")]
        result[0] = rt.unary("-", rt.f(1.0))
        result[1] = rt.construct(3, rt.f(0.0))
        result[2] = rt.construct(3, rt.i(0), base="int")
        volSize = _u_volumeSize
        voxelSize = rt.binary("/", rt.f(2.0), rt.construct(1, volSize), 1, "float")
        invRd = rt.binary("/", rt.f(1.0), rd, 3, "float")
        t0 = rt.binary("*", rt.binary("-", rt.unary("-", rt.f(1.0)), ro, 3, "float"), invRd, 3, "float")
        t1 = rt.binary("*", rt.binary("-", rt.f(1.0), ro, 3, "float"), invRd, 3, "float")
        tmin = rt.component_wise("min", t0, t1, width=3)
        tmax = rt.component_wise("max", t0, t1, width=3)
        tEnter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "y"), width=1), rt.swizzle(tmin, "z"), width=1)
        tExit = rt.component_wise("min", rt.component_wise("min", rt.swizzle(tmax, "x"), rt.swizzle(tmax, "y"), width=1), rt.swizzle(tmax, "z"), width=1)
        if (bool(rt.binary(">", tEnter, tExit)) or bool(rt.binary("<", tExit, rt.f(0.0)))):
            return result
        tStart = rt.component_wise("max", rt.binary("+", tEnter, rt.f(0.001), 1, "float"), rt.f(0.0), width=1)
        pos = rt.binary("+", ro, rt.binary("*", rd, tStart, 3, "float"), 3, "float")
        voxel = worldToVoxel__vec3(pos)
        voxel[:] = rt.component_wise("clamp", voxel, rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", volSize, rt.i(1), 1, "int"), base="int"), width=3)
        step = rt.construct(3, rt.component_wise("sign", rd, width=3), base="int")
        voxelBounds = voxelToWorld__ivec3(rt.binary("+", voxel, rt.component_wise("max", step, rt.construct(3, rt.i(0), base="int"), width=3), 3, "int"))
        tMaxVec = rt.binary("*", rt.binary("-", voxelBounds, ro, 3, "float"), invRd, 3, "float")
        tDelta = rt.component_wise("abs", rt.binary("*", voxelSize, invRd, 3, "float"), width=3)
        lastNormal = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.binary("*", g.MAX_STEPS, rt.i(2), 1, "int"))):
                break
            if (bool((bool((bool((bool((bool(rt.binary(">=", rt.swizzle(voxel, "x"), rt.i(0))) and bool(rt.binary("<", rt.swizzle(voxel, "x"), volSize)))) and bool(rt.binary(">=", rt.swizzle(voxel, "y"), rt.i(0))))) and bool(rt.binary("<", rt.swizzle(voxel, "y"), volSize)))) and bool(rt.binary(">=", rt.swizzle(voxel, "z"), rt.i(0))))) and bool(rt.binary("<", rt.swizzle(voxel, "z"), volSize))):
                if isVoxelSolid__ivec3(voxel):
                    result[0] = tStart
                    result[1] = lastNormal
                    result[2] = voxel
                    if rt.binary("==", lastNormal, rt.construct(3, rt.f(0.0))):
                        if (bool(rt.binary(">", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "y"))) and bool(rt.binary(">", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "z")))):
                            result[1] = rt.construct(3, rt.unary("-", rt.component_wise("sign", rt.swizzle(rd, "x"), width=1)), rt.f(0.0), rt.f(0.0))
                        else:
                            if rt.binary(">", rt.swizzle(tmin, "y"), rt.swizzle(tmin, "z")):
                                result[1] = rt.construct(3, rt.f(0.0), rt.unary("-", rt.component_wise("sign", rt.swizzle(rd, "y"), width=1)), rt.f(0.0))
                            else:
                                result[1] = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.unary("-", rt.component_wise("sign", rt.swizzle(rd, "z"), width=1)))
                    return result
            if rt.binary("<", rt.swizzle(tMaxVec, "x"), rt.swizzle(tMaxVec, "y")):
                if rt.binary("<", rt.swizzle(tMaxVec, "x"), rt.swizzle(tMaxVec, "z")):
                    tStart = rt.swizzle(tMaxVec, "x")
                    tMaxVec = rt.assign_swizzle(tMaxVec, "x", rt.binary("+", rt.swizzle(tMaxVec, "x"), rt.swizzle(tDelta, "x"), 1, "float"))
                    voxel = rt.assign_swizzle(voxel, "x", rt.binary("+", rt.swizzle(voxel, "x"), rt.swizzle(step, "x"), 1, "int"))
                    (lastNormal.__setitem__(0, rt.unary("-", rt.construct(1, rt.swizzle(step, "x")))), lastNormal.__setitem__(1, rt.f(0.0)), lastNormal.__setitem__(2, rt.f(0.0)), lastNormal)[-1]
                else:
                    tStart = rt.swizzle(tMaxVec, "z")
                    tMaxVec = rt.assign_swizzle(tMaxVec, "z", rt.binary("+", rt.swizzle(tMaxVec, "z"), rt.swizzle(tDelta, "z"), 1, "float"))
                    voxel = rt.assign_swizzle(voxel, "z", rt.binary("+", rt.swizzle(voxel, "z"), rt.swizzle(step, "z"), 1, "int"))
                    (lastNormal.__setitem__(0, rt.f(0.0)), lastNormal.__setitem__(1, rt.f(0.0)), lastNormal.__setitem__(2, rt.unary("-", rt.construct(1, rt.swizzle(step, "z")))), lastNormal)[-1]
            else:
                if rt.binary("<", rt.swizzle(tMaxVec, "y"), rt.swizzle(tMaxVec, "z")):
                    tStart = rt.swizzle(tMaxVec, "y")
                    tMaxVec = rt.assign_swizzle(tMaxVec, "y", rt.binary("+", rt.swizzle(tMaxVec, "y"), rt.swizzle(tDelta, "y"), 1, "float"))
                    voxel = rt.assign_swizzle(voxel, "y", rt.binary("+", rt.swizzle(voxel, "y"), rt.swizzle(step, "y"), 1, "int"))
                    (lastNormal.__setitem__(0, rt.f(0.0)), lastNormal.__setitem__(1, rt.unary("-", rt.construct(1, rt.swizzle(step, "y")))), lastNormal.__setitem__(2, rt.f(0.0)), lastNormal)[-1]
                else:
                    tStart = rt.swizzle(tMaxVec, "z")
                    tMaxVec = rt.assign_swizzle(tMaxVec, "z", rt.binary("+", rt.swizzle(tMaxVec, "z"), rt.swizzle(tDelta, "z"), 1, "float"))
                    voxel = rt.assign_swizzle(voxel, "z", rt.binary("+", rt.swizzle(voxel, "z"), rt.swizzle(step, "z"), 1, "int"))
                    (lastNormal.__setitem__(0, rt.f(0.0)), lastNormal.__setitem__(1, rt.f(0.0)), lastNormal.__setitem__(2, rt.unary("-", rt.construct(1, rt.swizzle(step, "z")))), lastNormal)[-1]
            if rt.binary(">", tStart, tExit):
                break
        return result
    def calcNormal__vec3(p):
        p = rt.copy(p, "float")
        eps = rt.binary("/", rt.f(2.0), rt.construct(1, _u_volumeSize), 1, "float")
        dx = rt.binary("-", getField__vec3(rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float")), getField__vec3(rt.binary("-", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float")), 1, "float")
        dy = rt.binary("-", getField__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float")), getField__vec3(rt.binary("-", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float")), 1, "float")
        dz = rt.binary("-", getField__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float")), getField__vec3(rt.binary("-", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float")), 1, "float")
        n = rt.construct(3, dx, dy, dz)
        len = rt.length(n)
        if rt.binary("<", len, rt.f(0.0001)):
            return rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))
        return rt.binary("/", n, len, 3, "float")
    def isosurfaceTrace__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        result = [rt.f(0.0), rt.construct(3, 0.0), False]
        result[2] = False
        result[0] = rt.unary("-", rt.f(1.0))
        result[1] = rt.construct(3, rt.f(0.0))
        invRd = rt.binary("/", rt.f(1.0), rd, 3, "float")
        t0 = rt.binary("*", rt.binary("-", rt.unary("-", rt.f(1.0)), ro, 3, "float"), invRd, 3, "float")
        t1 = rt.binary("*", rt.binary("-", rt.f(1.0), ro, 3, "float"), invRd, 3, "float")
        tmin = rt.component_wise("min", t0, t1, width=3)
        tmax = rt.component_wise("max", t0, t1, width=3)
        tEnter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "y"), width=1), rt.swizzle(tmin, "z"), width=1)
        tExit = rt.component_wise("min", rt.component_wise("min", rt.swizzle(tmax, "x"), rt.swizzle(tmax, "y"), width=1), rt.swizzle(tmax, "z"), width=1)
        if (bool(rt.binary(">", tEnter, tExit)) or bool(rt.binary("<", tExit, rt.f(0.0)))):
            return result
        tStart = rt.component_wise("max", tEnter, rt.f(0.0), width=1)
        stepSize = rt.binary("/", rt.f(1.5), rt.construct(1, _u_volumeSize), 1, "float")
        t = tStart
        prevField = getField__vec3(rt.binary("+", ro, rt.binary("*", rd, t, 3, "float"), 3, "float"))
        if rt.binary("<", prevField, rt.f(0.0)):
            result[2] = True
            result[0] = tStart
            result[1] = rt.binary("+", ro, rt.binary("*", rd, tStart, 3, "float"), 3, "float")
            return result
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, g.MAX_STEPS)):
                break
            t = rt.binary("+", t, stepSize, 1, "float")
            if rt.binary(">", t, tExit):
                break
            p = rt.binary("+", ro, rt.binary("*", rd, t, 3, "float"), 3, "float")
            field = getField__vec3(p)
            tLo = rt.f(0.0)
            tHi = rt.f(0.0)
            if rt.binary("<", rt.binary("*", prevField, field, 1, "float"), rt.f(0.0)):
                tLo = rt.binary("-", t, stepSize, 1, "float")
                tHi = t
                j = rt.i(0)
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        j = rt.binary("+", j, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<", j, rt.i(8))):
                        break
                    tMid = rt.binary("*", rt.binary("+", tLo, tHi, 1, "float"), rt.f(0.5), 1, "float")
                    fMid = getField__vec3(rt.binary("+", ro, rt.binary("*", rd, tMid, 3, "float"), 3, "float"))
                    if rt.binary("<", rt.binary("*", prevField, fMid, 1, "float"), rt.f(0.0)):
                        tHi = tMid
                    else:
                        tLo = tMid
                        prevField = fMid
                result[2] = True
                result[0] = rt.binary("*", rt.binary("+", tLo, tHi, 1, "float"), rt.f(0.5), 1, "float")
                result[1] = rt.binary("+", ro, rt.binary("*", rd, result[0], 3, "float"), 3, "float")
                return result
            prevField = field
        return result
    def shade__vec3_vec3(p, rd):
        p = rt.copy(p, "float")
        rd = rt.copy(rd, "float")
        n = calcNormal__vec3(p)
        lightDir = rt.normalize(rt.construct(3, rt.f(1.0), rt.f(1.0), rt.unary("-", rt.f(1.0))))
        diff = rt.component_wise("max", rt.dot(n, lightDir), rt.f(0.0), width=1)
        amb = rt.f(0.15)
        halfVec = rt.normalize(rt.binary("-", lightDir, rd, 3, "float"))
        spec = rt.component_wise("pow", rt.component_wise("max", rt.dot(n, halfVec), rt.f(0.0), width=1), rt.f(32.0), width=1)
        rim = rt.component_wise("pow", rt.binary("-", rt.f(1.0), rt.component_wise("max", rt.dot(n, rt.unary("-", rd)), rt.f(0.0), width=1), 1, "float"), rt.f(3.0), width=1)
        volColor = sampleVolume__vec3(p)
        baseColor = rt.swizzle(volColor, "rgb")
        colorVariance = rt.length(rt.binary("-", rt.swizzle(volColor, "rgb"), rt.construct(3, rt.swizzle(volColor, "r")), 3, "float"))
        if rt.binary("<", colorVariance, rt.f(0.01)):
            baseColor[:] = rt.construct(3, rt.f(0.75))
        return rt.binary("+", rt.binary("+", rt.binary("*", baseColor, rt.binary("+", amb, rt.binary("*", diff, rt.f(0.7), 1, "float"), 1, "float"), 3, "float"), rt.binary("*", spec, rt.f(0.2), 1, "float"), 3, "float"), rt.binary("*", rim, rt.f(0.15), 1, "float"), 3, "float")
    def shadeVoxel__vec3_vec3_vec3_ivec3(p, rd, n, voxel):
        p = rt.copy(p, "float")
        rd = rt.copy(rd, "float")
        n = rt.copy(n, "float")
        voxel = rt.copy(voxel, "int")
        lightDir = rt.normalize(rt.construct(3, rt.f(1.0), rt.f(1.0), rt.unary("-", rt.f(1.0))))
        diff = rt.component_wise("max", rt.dot(n, lightDir), rt.f(0.0), width=1)
        amb = rt.f(0.3)
        volColor = sampleVoxel__ivec3(voxel)
        baseColor = rt.swizzle(volColor, "rgb")
        colorVariance = rt.length(rt.binary("-", rt.swizzle(volColor, "rgb"), rt.construct(3, rt.swizzle(volColor, "r")), 3, "float"))
        faceShade = rt.f(0.0)
        if rt.binary("<", colorVariance, rt.f(0.01)):
            faceShade = rt.binary("+", rt.binary("+", rt.binary("*", rt.component_wise("abs", rt.swizzle(n, "x"), width=1), rt.f(0.9), 1, "float"), rt.binary("*", rt.component_wise("abs", rt.swizzle(n, "y"), width=1), rt.f(1.0), 1, "float"), 1, "float"), rt.binary("*", rt.component_wise("abs", rt.swizzle(n, "z"), width=1), rt.f(0.85), 1, "float"), 1, "float")
            baseColor[:] = rt.construct(3, rt.binary("*", rt.f(0.7), faceShade, 1, "float"))
        return rt.binary("*", baseColor, rt.binary("+", amb, rt.binary("*", diff, rt.f(0.7), 1, "float"), 1, "float"), 3, "float")
    def main__void():
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        if rt.binary("<", rt.swizzle(fullRes, "x"), rt.f(1.0)):
            (fullRes.__setitem__(0, rt.f(1024.0)), fullRes.__setitem__(1, rt.f(1024.0)), fullRes)[-1]
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", rt.f(0.5), fullRes, 2, "float"), 2, "float"), rt.swizzle(fullRes, "y"), 2, "float")
        camDist = rt.f(3.5)
        angle = rt.binary("*", rt.binary("*", _u_time, g.TAU, 1, "float"), rt.construct(1, _u_orbitSpeed), 1, "float")
        ro = rt.construct(3, rt.binary("*", rt.component_wise("sin", angle, width=1), camDist, 1, "float"), rt.f(0.5), rt.binary("*", rt.component_wise("cos", angle, width=1), camDist, 1, "float"))
        lookAt = rt.construct(3, rt.f(0.0))
        forward = rt.normalize(rt.binary("-", lookAt, ro, 3, "float"))
        right = rt.normalize(rt.cross(rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), forward))
        up = rt.cross(forward, right)
        rd = rt.normalize(rt.binary("+", rt.binary("+", forward, rt.binary("*", rt.swizzle(uv, "x"), right, 3, "float"), 3, "float"), rt.binary("*", rt.swizzle(uv, "y"), up, 3, "float"), 3, "float"))
        color = rt.construct(3, 0.0)
        normal = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0))
        depth = rt.f(1.0)
        alpha = rt.f(1.0)
        hit = [rt.f(0.0), rt.construct(3, 0.0), False]
        if rt.binary("==", _u_FILTERING, rt.i(1)):
            hit = voxelTrace__vec3_vec3(ro, rd)
            p = rt.construct(3, 0.0)
            if rt.binary(">", hit[0], rt.f(0.0)):
                p = rt.binary("+", ro, rt.binary("*", rd, hit[0], 3, "float"), 3, "float")
                color[:] = shadeVoxel__vec3_vec3_vec3_ivec3(p, rd, hit[1], hit[2])
                normal[:] = hit[1]
                depth = rt.binary("/", hit[0], g.MAX_DIST, 1, "float")
            else:
                color[:] = _u_bgColor
                alpha = _u_bgAlpha
        else:
            hit = isosurfaceTrace__vec3_vec3(ro, rd)
            if hit[2]:
                color[:] = shade__vec3_vec3(hit[1], rd)
                normal[:] = calcNormal__vec3(hit[1])
                depth = rt.binary("/", hit[0], g.MAX_DIST, 1, "float")
            else:
                color[:] = _u_bgColor
                alpha = _u_bgAlpha
        color[:] = rt.component_wise("pow", color, rt.construct(3, rt.binary("/", rt.f(1.0), rt.f(2.2), 1, "float")), width=3)
        g.fragColor[:] = rt.construct(4, color, alpha)
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), depth)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
