def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_invert = U.get("invert", 0)
    _u_volumeSize = U.get("volumeSize", 0)
    _u_shape = U.get("shape", 0)
    _u_orbitSpeed = U.get("orbitSpeed", 0)
    _u_cameraPosition = U.get("cameraPosition", rt.construct(3, 0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_volumeCache = T["volumeCache"]
    _u_lightDirection = U.get("lightDirection", rt.construct(3, 0.0))
    _u_diffuseColor = U.get("diffuseColor", rt.construct(3, 0.0))
    _u_diffuseIntensity = U.get("diffuseIntensity", rt.f(0.0))
    _u_specularColor = U.get("specularColor", rt.construct(3, 0.0))
    _u_specularIntensity = U.get("specularIntensity", rt.f(0.0))
    _u_shininess = U.get("shininess", rt.f(0.0))
    _u_ambientColor = U.get("ambientColor", rt.construct(3, 0.0))
    _u_rimIntensity = U.get("rimIntensity", rt.f(0.0))
    _u_rimPower = U.get("rimPower", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    g.PI = rt.f(3.141592653589793)
    g.MAX_STEPS = rt.i(256)
    g.MAX_DIST = rt.f(10.0)
    g.NEAR_CLIP = rt.f(0.01)
    def atlasTexel__ivec3_int(p, volSize):
        p = rt.copy(p, "int")
        return rt.construct(2, rt.swizzle(p, "x"), rt.binary("+", rt.swizzle(p, "y"), rt.binary("*", rt.swizzle(p, "z"), volSize, 1, "int"), 1, "int"), base="int")
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
        if rt.binary("==", _u_invert, rt.i(1)):
            val = rt.binary("-", rt.f(1.0), val, 1, "float")
        return rt.binary("-", _u_threshold, val, 1, "float")
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
    def calcBoundaryNormal__vec3(p):
        p = rt.copy(p, "float")
        absP = rt.construct(3, 0.0)
        if rt.binary("==", _u_shape, rt.i(0)):
            absP = rt.component_wise("abs", p, width=3)
            if (bool(rt.binary(">", rt.swizzle(absP, "x"), rt.swizzle(absP, "y"))) and bool(rt.binary(">", rt.swizzle(absP, "x"), rt.swizzle(absP, "z")))):
                return rt.construct(3, rt.component_wise("sign", rt.swizzle(p, "x"), width=1), rt.f(0.0), rt.f(0.0))
            else:
                if rt.binary(">", rt.swizzle(absP, "y"), rt.swizzle(absP, "z")):
                    return rt.construct(3, rt.f(0.0), rt.component_wise("sign", rt.swizzle(p, "y"), width=1), rt.f(0.0))
                else:
                    return rt.construct(3, rt.f(0.0), rt.f(0.0), rt.component_wise("sign", rt.swizzle(p, "z"), width=1))
        else:
            return rt.normalize(p)
    def intersectBox__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        invRd = rt.binary("/", rt.f(1.0), rd, 3, "float")
        t0 = rt.binary("*", rt.binary("-", rt.unary("-", rt.f(1.0)), ro, 3, "float"), invRd, 3, "float")
        t1 = rt.binary("*", rt.binary("-", rt.f(1.0), ro, 3, "float"), invRd, 3, "float")
        tmin = rt.component_wise("min", t0, t1, width=3)
        tmax = rt.component_wise("max", t0, t1, width=3)
        tEnter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "y"), width=1), rt.swizzle(tmin, "z"), width=1)
        tExit = rt.component_wise("min", rt.component_wise("min", rt.swizzle(tmax, "x"), rt.swizzle(tmax, "y"), width=1), rt.swizzle(tmax, "z"), width=1)
        if (bool(rt.binary(">", tEnter, tExit)) or bool(rt.binary("<", tExit, rt.f(0.0)))):
            return rt.construct(2, rt.unary("-", rt.f(1.0)))
        return rt.construct(2, tEnter, tExit)
    def intersectSphere__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        b = rt.dot(ro, rd)
        c = rt.binary("-", rt.dot(ro, ro), rt.f(1.0), 1, "float")
        disc = rt.binary("-", rt.binary("*", b, b, 1, "float"), c, 1, "float")
        if rt.binary("<", disc, rt.f(0.0)):
            return rt.construct(2, rt.unary("-", rt.f(1.0)))
        sqrtDisc = rt.component_wise("sqrt", disc, width=1)
        tEnter = rt.binary("-", rt.unary("-", b), sqrtDisc, 1, "float")
        tExit = rt.binary("+", rt.unary("-", b), sqrtDisc, 1, "float")
        if rt.binary("<", tExit, rt.f(0.0)):
            return rt.construct(2, rt.unary("-", rt.f(1.0)))
        return rt.construct(2, tEnter, tExit)
    def getRayBounds__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        t = rt.construct(2, 0.0)
        if rt.binary("==", _u_shape, rt.i(0)):
            t[:] = intersectBox__vec3_vec3(ro, rd)
        else:
            t[:] = intersectSphere__vec3_vec3(ro, rd)
        if (bool(rt.binary("<", rt.swizzle(t, "x"), rt.f(0.0))) and bool(rt.binary("<", rt.swizzle(t, "y"), rt.f(0.0)))):
            return rt.construct(2, rt.unary("-", rt.f(1.0)))
        t = rt.assign_swizzle(t, "x", rt.component_wise("max", rt.swizzle(t, "x"), g.NEAR_CLIP, width=1))
        return t
    def raymarch__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        result = [rt.f(0.0), rt.construct(3, 0.0), False, False]
        result[2] = False
        result[0] = rt.unary("-", rt.f(1.0))
        result[1] = rt.construct(3, rt.f(0.0))
        result[3] = False
        bounds = getRayBounds__vec3_vec3(ro, rd)
        if rt.binary("<", rt.swizzle(bounds, "x"), rt.f(0.0)):
            return result
        tStart = rt.swizzle(bounds, "x")
        tEnd = rt.swizzle(bounds, "y")
        stepSize = rt.binary("/", rt.f(1.5), rt.construct(1, _u_volumeSize), 1, "float")
        t = tStart
        prevField = getField__vec3(rt.binary("+", ro, rt.binary("*", rd, t, 3, "float"), 3, "float"))
        if rt.binary("<", prevField, rt.f(0.0)):
            result[2] = True
            result[0] = tStart
            result[1] = rt.binary("+", ro, rt.binary("*", rd, tStart, 3, "float"), 3, "float")
            result[3] = True
            return result
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.MAX_STEPS)):
                break
            t = rt.binary("+", t, stepSize, 1, "float")
            if rt.binary(">", t, tEnd):
                break
            p = rt.binary("+", ro, rt.binary("*", rd, t, 3, "float"), 3, "float")
            if rt.binary("==", _u_shape, rt.i(0)):
                if (bool(rt.component_wise("any", rt.component_wise("lessThan", p, rt.construct(3, rt.unary("-", rt.f(1.0))), width=3), width=3)) or bool(rt.component_wise("any", rt.component_wise("greaterThan", p, rt.construct(3, rt.f(1.0)), width=3), width=3))):
                    break
            else:
                if rt.binary("==", _u_shape, rt.i(1)):
                    if rt.binary(">", rt.dot(p, p), rt.f(1.0)):
                        break
            field = getField__vec3(p)
            tLo = rt.f(0.0)
            tHi = rt.f(0.0)
            if rt.binary("<", rt.binary("*", prevField, field, 1, "float"), rt.f(0.0)):
                tLo = rt.binary("-", t, stepSize, 1, "float")
                tHi = t
                j = rt.i(0)
                _for1_first = True
                for _for1 in range(1048576):
                    if not _for1_first:
                        j = rt.binary("+", j, rt.i(1), 1, "int")
                    _for1_first = False
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
    def applyLighting__vec3_vec3_vec3_vec3(baseColor, n, rd, worldLightDir):
        baseColor = rt.copy(baseColor, "float")
        n = rt.copy(n, "float")
        rd = rt.copy(rd, "float")
        worldLightDir = rt.copy(worldLightDir, "float")
        lightDir = rt.normalize(worldLightDir)
        viewDir = rt.unary("-", rd)
        if rt.binary("<", rt.dot(n, viewDir), rt.f(0.0)):
            n[:] = rt.unary("-", n)
        ambient = rt.binary("*", _u_ambientColor, baseColor, 3, "float")
        diffuseFactor = rt.component_wise("max", rt.dot(n, lightDir), rt.f(0.0), width=1)
        diffuse = rt.binary("*", rt.binary("*", rt.binary("*", _u_diffuseColor, diffuseFactor, 3, "float"), baseColor, 3, "float"), _u_diffuseIntensity, 3, "float")
        halfDir = rt.normalize(rt.binary("+", lightDir, viewDir, 3, "float"))
        specAngle = rt.component_wise("max", rt.dot(halfDir, n), rt.f(0.0), width=1)
        specularFactor = rt.component_wise("pow", specAngle, _u_shininess, width=1)
        specular = rt.binary("*", rt.binary("*", _u_specularColor, specularFactor, 3, "float"), _u_specularIntensity, 3, "float")
        rim = rt.component_wise("pow", rt.binary("-", rt.f(1.0), rt.component_wise("max", rt.dot(n, viewDir), rt.f(0.0), width=1), 1, "float"), _u_rimPower, width=1)
        rimLight = rt.binary("*", rt.construct(3, rim), _u_rimIntensity, 3, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", ambient, diffuse, 3, "float"), specular, 3, "float"), rimLight, 3, "float")
    def shade__vec3_vec3_vec3_vec3(p, n, rd, worldLightDir):
        p = rt.copy(p, "float")
        n = rt.copy(n, "float")
        rd = rt.copy(rd, "float")
        worldLightDir = rt.copy(worldLightDir, "float")
        volColor = sampleVolume__vec3(p)
        baseColor = rt.swizzle(volColor, "rgb")
        colorVariance = rt.length(rt.binary("-", rt.swizzle(volColor, "rgb"), rt.construct(3, rt.swizzle(volColor, "r")), 3, "float"))
        if rt.binary("<", colorVariance, rt.f(0.01)):
            baseColor[:] = rt.construct(3, rt.f(0.75))
        return applyLighting__vec3_vec3_vec3_vec3(baseColor, n, rd, worldLightDir)
    def main__void():
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        if rt.binary("<", rt.swizzle(fullRes, "x"), rt.f(1.0)):
            (fullRes.__setitem__(0, rt.f(1024.0)), fullRes.__setitem__(1, rt.f(1024.0)), fullRes)[-1]
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", rt.f(0.5), fullRes, 2, "float"), 2, "float"), rt.swizzle(fullRes, "y"), 2, "float")
        ro = rt.binary("*", rt.binary("*", _u_cameraPosition, rt.construct(3, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(1.0)), 3, "float"), rt.f(3.5), 3, "float")
        forward = rt.construct(3, 0.0)
        if rt.binary("<", rt.length(ro), rt.f(0.001)):
            (forward.__setitem__(0, rt.f(0.0)), forward.__setitem__(1, rt.f(0.0)), forward.__setitem__(2, rt.unary("-", rt.f(1.0))), forward)[-1]
        else:
            forward[:] = rt.normalize(rt.unary("-", ro))
        worldUp = rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))
        if rt.binary(">", rt.component_wise("abs", rt.dot(forward, worldUp), width=1), rt.f(0.999)):
            (worldUp.__setitem__(0, rt.f(0.0)), worldUp.__setitem__(1, rt.f(0.0)), worldUp.__setitem__(2, rt.f(1.0)), worldUp)[-1]
        right = rt.normalize(rt.cross(worldUp, forward))
        up = rt.cross(forward, right)
        rd = rt.normalize(rt.binary("+", rt.binary("+", forward, rt.binary("*", rt.swizzle(uv, "x"), right, 3, "float"), 3, "float"), rt.binary("*", rt.swizzle(uv, "y"), up, 3, "float"), 3, "float"))
        worldLightDir = rt.normalize(rt.binary("*", _u_lightDirection, rt.construct(3, rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(1.0)), 3, "float"))
        angle = rt.binary("*", rt.binary("*", _u_time, g.TAU, 1, "float"), rt.construct(1, _u_orbitSpeed), 1, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        roVol = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(ro, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(ro, "z"), s, 1, "float"), 1, "float"), rt.swizzle(ro, "y"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(ro, "x")), s, 1, "float"), rt.binary("*", rt.swizzle(ro, "z"), c, 1, "float"), 1, "float"))
        rdVol = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(rd, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(rd, "z"), s, 1, "float"), 1, "float"), rt.swizzle(rd, "y"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(rd, "x")), s, 1, "float"), rt.binary("*", rt.swizzle(rd, "z"), c, 1, "float"), 1, "float"))
        color = rt.construct(3, 0.0)
        normal = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0))
        depth = rt.f(1.0)
        alpha = rt.f(1.0)
        hit = raymarch__vec3_vec3(roVol, rdVol)
        if hit[2]:
            if hit[3]:
                normal[:] = calcBoundaryNormal__vec3(hit[1])
            else:
                normal[:] = calcNormal__vec3(hit[1])
            normal[:] = rt.construct(3, rt.binary("-", rt.binary("*", rt.swizzle(normal, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(normal, "z"), s, 1, "float"), 1, "float"), rt.swizzle(normal, "y"), rt.binary("+", rt.binary("*", rt.swizzle(normal, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(normal, "z"), c, 1, "float"), 1, "float"))
            color[:] = shade__vec3_vec3_vec3_vec3(hit[1], normal, rd, worldLightDir)
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
