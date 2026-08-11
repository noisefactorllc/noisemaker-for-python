def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_noiseType = U.get("noiseType", 0)
    _u_power = U.get("power", rt.f(0.0))
    _u_iterations = U.get("iterations", 0)
    _u_bailout = U.get("bailout", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_voiSize = U.get("voiSize", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    g.SAFETY_RADIUS = rt.f(0.08)
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.PI = rt.f(3.141592653589793)
    g.TAU = rt.f(6.283185307179586)
    def hash__float(n):
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", rt.binary("+", n, _u_seed, 1, "float"), width=1), rt.f(43758.5453123), 1, "float"), width=1)
    def trefoilKnot__float_float(t, scale):
        p = rt.f(2.0)
        q = rt.f(3.0)
        r = rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.2), rt.component_wise("cos", rt.binary("*", q, t, 1, "float"), width=1), 1, "float"), 1, "float")
        return rt.binary("*", scale, rt.construct(3, rt.binary("*", r, rt.component_wise("cos", rt.binary("*", p, t, 1, "float"), width=1), 1, "float"), rt.binary("*", r, rt.component_wise("sin", rt.binary("*", p, t, 1, "float"), width=1), 1, "float"), rt.binary("*", rt.f(0.3), rt.component_wise("sin", rt.binary("*", q, t, 1, "float"), width=1), 1, "float")), 3, "float")
    def tiltedOrbit__float_float(t, scale):
        tilt = rt.f(0.4)
        a = rt.f(1.0)
        b = rt.f(0.7)
        pos = rt.construct(3, rt.binary("*", a, rt.component_wise("cos", t, width=1), 1, "float"), rt.binary("*", b, rt.component_wise("sin", t, width=1), 1, "float"), rt.f(0.0))
        c = rt.component_wise("cos", tilt, width=1)
        s = rt.component_wise("sin", tilt, width=1)
        pos[:] = rt.construct(3, rt.swizzle(pos, "x"), rt.binary("-", rt.binary("*", rt.swizzle(pos, "y"), c, 1, "float"), rt.binary("*", rt.swizzle(pos, "z"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(pos, "y"), s, 1, "float"), rt.binary("*", rt.swizzle(pos, "z"), c, 1, "float"), 1, "float"))
        return rt.binary("*", scale, pos, 3, "float")
    def lissajousOrbit__float_float(t, scale):
        fx = rt.f(1.0)
        fy = rt.f(1.618)
        fz = rt.f(2.0)
        px = rt.f(0.0)
        py = rt.binary("*", g.PI, rt.f(0.5), 1, "float")
        pz = rt.binary("*", g.PI, rt.f(0.25), 1, "float")
        return rt.binary("*", scale, rt.construct(3, rt.component_wise("sin", rt.binary("+", rt.binary("*", fx, t, 1, "float"), px, 1, "float"), width=1), rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", fy, t, 1, "float"), py, 1, "float"), width=1), rt.f(0.6), 1, "float"), rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", fz, t, 1, "float"), pz, 1, "float"), width=1), rt.f(0.4), 1, "float")), 3, "float")
    def getOrbitPosition__float(t):
        orbitScale = rt.f(0.7)
        orbitType = rt.construct(1, rt.component_wise("mod", rt.binary("*", _u_seed, rt.f(3.0), 1, "float"), rt.f(3.0), width=1), base="int")
        if rt.binary("==", orbitType, rt.i(0)):
            return trefoilKnot__float_float(t, orbitScale)
        else:
            if rt.binary("==", orbitType, rt.i(1)):
                return tiltedOrbit__float_float(t, orbitScale)
            else:
                return lissajousOrbit__float_float(t, orbitScale)
    def getOrbitTangent__float(t):
        dt = rt.f(0.01)
        p0 = getOrbitPosition__float(t)
        p1 = getOrbitPosition__float(rt.binary("+", t, dt, 1, "float"))
        return rt.normalize(rt.binary("-", p1, p0, 3, "float"))
    def getWobbleOffset__float_vec3(t, tangent):
        tangent = rt.copy(tangent, "float")
        up = rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))
        if rt.binary(">", rt.component_wise("abs", rt.dot(tangent, up), width=1), rt.f(0.99)):
            (up.__setitem__(0, rt.f(1.0)), up.__setitem__(1, rt.f(0.0)), up.__setitem__(2, rt.f(0.0)), up)[-1]
        right = rt.normalize(rt.cross(tangent, up))
        realUp = rt.normalize(rt.cross(right, tangent))
        wobbleAmp = rt.f(0.15)
        wx = rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", t, rt.f(2.7), 1, "float"), rt.binary("*", _u_seed, g.PI, 1, "float"), 1, "float"), width=1), wobbleAmp, 1, "float")
        wy = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", t, rt.f(1.9), 1, "float"), rt.binary("*", _u_seed, g.TAU, 1, "float"), 1, "float"), width=1), wobbleAmp, 1, "float"), rt.f(0.7), 1, "float")
        return rt.binary("+", rt.binary("*", right, wx, 3, "float"), rt.binary("*", realUp, wy, 3, "float"), 3, "float")
    def getCameraState__float_vec3_vec3_vec3(t, pos, dir, up):
        pos = rt.copy(pos, "float")
        dir = rt.copy(dir, "float")
        up = rt.copy(up, "float")
        orbitTime = rt.binary("*", rt.binary("*", t, _u_speed, 1, "float"), rt.f(0.3), 1, "float")
        orbitPos = getOrbitPosition__float(orbitTime)
        tangent = getOrbitTangent__float(orbitTime)
        wobble = getWobbleOffset__float_vec3(orbitTime, tangent)
        pos[:] = rt.binary("+", orbitPos, wobble, 3, "float")
        dir[:] = tangent
        worldUp = rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0))
        right = rt.normalize(rt.cross(worldUp, dir))
        up[:] = rt.normalize(rt.cross(dir, right))
        roll = rt.binary("*", rt.component_wise("sin", rt.binary("*", orbitTime, rt.f(0.5), 1, "float"), width=1), rt.f(0.1), 1, "float")
        rollRight = rt.binary("+", rt.binary("*", right, rt.component_wise("cos", roll, width=1), 3, "float"), rt.binary("*", up, rt.component_wise("sin", roll, width=1), 3, "float"), 3, "float")
        up[:] = rt.normalize(rt.cross(rollRight, dir))
        return (None, pos, dir, up)
    def mandelbulb__vec3_float_int_float(pos, n, maxIter, bail):
        pos = rt.copy(pos, "float")
        result = [rt.f(0.0), rt.f(0.0), rt.f(0.0)]
        z = pos
        dr = rt.f(1.0)
        r = rt.f(0.0)
        trap = rt.f(10000000000.0)
        iter = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, maxIter)):
                break
            r = rt.length(z)
            if rt.binary(">", r, bail):
                break
            trap = rt.component_wise("min", trap, r, width=1)
            theta = rt.component_wise("acos", rt.binary("/", rt.swizzle(z, "z"), r, 1, "float"), width=1)
            phi = rt.component_wise("atan", rt.swizzle(z, "y"), rt.swizzle(z, "x"), width=1)
            dr = rt.binary("+", rt.binary("*", rt.binary("*", rt.component_wise("pow", r, rt.binary("-", n, rt.f(1.0), 1, "float"), width=1), n, 1, "float"), dr, 1, "float"), rt.f(1.0), 1, "float")
            zr = rt.component_wise("pow", r, n, width=1)
            newTheta = rt.binary("*", theta, n, 1, "float")
            newPhi = rt.binary("*", phi, n, 1, "float")
            z[:] = rt.binary("*", zr, rt.construct(3, rt.binary("*", rt.component_wise("sin", newTheta, width=1), rt.component_wise("cos", newPhi, width=1), 1, "float"), rt.binary("*", rt.component_wise("sin", newTheta, width=1), rt.component_wise("sin", newPhi, width=1), 1, "float"), rt.component_wise("cos", newTheta, width=1)), 3, "float")
            z[:] = rt.binary("+", z, pos, 3, "float")
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
        result[0] = rt.binary("/", rt.binary("*", rt.binary("*", rt.f(0.5), rt.component_wise("log", r, width=1), 1, "float"), r, 1, "float"), dr, 1, "float")
        result[1] = trap
        result[2] = rt.binary("/", iter, rt.construct(1, maxIter), 1, "float")
        return result
    def boxFold__vec3_float(z, foldLimit):
        z = rt.copy(z, "float")
        return rt.binary("-", rt.binary("*", rt.component_wise("clamp", z, rt.unary("-", foldLimit), foldLimit, width=3), rt.f(2.0), 3, "float"), z, 3, "float")
    def mandelbox__vec3_float_int_float(pos, scale, maxIter, bail):
        pos = rt.copy(pos, "float")
        result = [rt.f(0.0), rt.f(0.0), rt.f(0.0)]
        z = pos
        dr = rt.f(1.0)
        trap = rt.f(10000000000.0)
        iter = rt.f(0.0)
        foldLimit = rt.f(1.0)
        minRadius2 = rt.f(0.25)
        fixedRadius2 = rt.f(1.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, maxIter)):
                break
            z[:] = boxFold__vec3_float(z, foldLimit)
            r2 = rt.dot(z, z)
            factor = rt.f(0.0)
            if rt.binary("<", r2, minRadius2):
                factor = rt.binary("/", fixedRadius2, minRadius2, 1, "float")
                z[:] = rt.binary("*", z, factor, 3, "float")
                dr = rt.binary("*", dr, factor, 1, "float")
            else:
                if rt.binary("<", r2, fixedRadius2):
                    factor = rt.binary("/", fixedRadius2, r2, 1, "float")
                    z[:] = rt.binary("*", z, factor, 3, "float")
                    dr = rt.binary("*", dr, factor, 1, "float")
            z[:] = rt.binary("+", rt.binary("*", z, scale, 3, "float"), pos, 3, "float")
            dr = rt.binary("+", rt.binary("*", dr, rt.component_wise("abs", scale, width=1), 1, "float"), rt.f(1.0), 1, "float")
            planeTrap = rt.component_wise("min", rt.component_wise("min", rt.component_wise("abs", rt.swizzle(z, "x"), width=1), rt.component_wise("abs", rt.swizzle(z, "y"), width=1), width=1), rt.component_wise("abs", rt.swizzle(z, "z"), width=1), width=1)
            trap = rt.component_wise("min", trap, planeTrap, width=1)
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
            if rt.binary(">", rt.length(z), bail):
                break
        r = rt.length(z)
        result[0] = rt.binary("/", r, rt.component_wise("abs", dr, width=1), 1, "float")
        result[1] = trap
        result[2] = rt.binary("/", iter, rt.construct(1, maxIter), 1, "float")
        return result
    def computeFractal__vec3(p):
        p = rt.copy(p, "float")
        if rt.binary("==", _u_noiseType, rt.i(0)):
            return mandelbulb__vec3_float_int_float(p, _u_power, _u_iterations, _u_bailout)
        else:
            return mandelbox__vec3_float_int_float(p, _u_power, _u_iterations, _u_bailout)
    def computeGradient__vec3_float(p, eps):
        p = rt.copy(p, "float")
        d0 = computeFractal__vec3(p)[0]
        dx = computeFractal__vec3(rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"))[0]
        dy = computeFractal__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"))[0]
        dz = computeFractal__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"))[0]
        return rt.binary("/", rt.construct(3, rt.binary("-", dx, d0, 1, "float"), rt.binary("-", dy, d0, 1, "float"), rt.binary("-", dz, d0, 1, "float")), eps, 3, "float")
    def applyCollisionAvoidance__vec3(pos):
        pos = rt.copy(pos, "float")
        fr = computeFractal__vec3(pos)
        grad = rt.construct(3, 0.0)
        pushDir = rt.construct(3, 0.0)
        pushDist = rt.f(0.0)
        if rt.binary("<", fr[0], g.SAFETY_RADIUS):
            grad = computeGradient__vec3_float(pos, rt.f(0.01))
            pushDir = rt.normalize(rt.binary("+", grad, rt.construct(3, rt.f(1e-06)), 3, "float"))
            pushDist = rt.binary("-", g.SAFETY_RADIUS, fr[0], 1, "float")
            pos[:] = rt.binary("+", pos, rt.binary("*", rt.binary("*", pushDir, pushDist, 3, "float"), rt.f(1.5), 3, "float"), 3, "float")
        return pos
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        pixelCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        vx = rt.swizzle(pixelCoord, "x")
        vy = rt.binary("%", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        vz = rt.binary("/", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        if (bool((bool(rt.binary(">=", vx, volSize)) or bool(rt.binary(">=", vy, volSize)))) or bool(rt.binary(">=", vz, volSize))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))
            return
        camPos = rt.construct(3, 0.0)
        camDir = rt.construct(3, 0.0)
        camUp = rt.construct(3, 0.0)
        (((_retc0 := getCameraState__float_vec3_vec3_vec3(_u_time, camPos, camDir, camUp)), camPos.__setitem__(slice(None), _retc0[1]), camDir.__setitem__(slice(None), _retc0[2]), camUp.__setitem__(slice(None), _retc0[3]), _retc0[0])[-1])
        camPos[:] = applyCollisionAvoidance__vec3(camPos)
        camRight = rt.normalize(rt.cross(camDir, camUp))
        camUp[:] = rt.normalize(rt.cross(camRight, camDir))
        normalizedCoord = rt.binary("-", rt.binary("*", rt.binary("/", rt.construct(3, rt.construct(1, vx), rt.construct(1, vy), rt.construct(1, vz)), rt.binary("-", volSizeF, rt.f(1.0), 1, "float"), 3, "float"), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
        halfExtent = rt.binary("*", _u_voiSize, rt.f(0.5), 1, "float")
        voiOffset = rt.binary("*", camDir, halfExtent, 3, "float")
        worldPos = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", camPos, voiOffset, 3, "float"), rt.binary("*", rt.binary("*", camRight, rt.swizzle(normalizedCoord, "x"), 3, "float"), halfExtent, 3, "float"), 3, "float"), rt.binary("*", rt.binary("*", camUp, rt.swizzle(normalizedCoord, "y"), 3, "float"), halfExtent, 3, "float"), 3, "float"), rt.binary("*", rt.binary("*", camDir, rt.swizzle(normalizedCoord, "z"), 3, "float"), halfExtent, 3, "float"), 3, "float")
        fr = computeFractal__vec3(worldPos)
        dist = fr[0]
        normalizedDist = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("+", rt.binary("*", dist, rt.f(2.0), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")
        trap = rt.component_wise("clamp", rt.binary("*", fr[1], rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        iterRatio = fr[2]
        eps = rt.f(0.02)
        gradient = computeGradient__vec3_float(worldPos, eps)
        normal = rt.normalize(rt.binary("+", gradient, rt.construct(3, rt.f(1e-06)), 3, "float"))
        g.fragColor[:] = rt.construct(4, normalizedDist, trap, iterRatio, rt.f(1.0))
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), normalizedDist)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
