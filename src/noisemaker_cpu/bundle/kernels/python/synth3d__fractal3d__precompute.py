def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_volumeSize = U.get("volumeSize", 0)
    _u_noiseType = U.get("noiseType", 0)
    _u_power = U.get("power", rt.f(0.0))
    _u_iterations = U.get("iterations", 0)
    _u_bailout = U.get("bailout", rt.f(0.0))
    _u_juliaX = U.get("juliaX", rt.f(0.0))
    _u_juliaY = U.get("juliaY", rt.f(0.0))
    _u_juliaZ = U.get("juliaZ", rt.f(0.0))
    _u_colorMode = U.get("colorMode", 0)
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.PI = rt.f(3.141592653589793)
    def mandelbulb__vec3_float_int_float(pos, n, maxIter, bail):
        pos = rt.copy(pos, "float")
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
        dist = rt.binary("/", rt.binary("*", rt.binary("*", rt.f(0.5), rt.component_wise("log", r, width=1), 1, "float"), r, 1, "float"), dr, 1, "float")
        return rt.construct(3, dist, trap, rt.binary("/", iter, rt.construct(1, maxIter), 1, "float"))
    def juliaBulb__vec3_vec3_float_int_float(pos, c, n, maxIter, bail):
        pos = rt.copy(pos, "float")
        c = rt.copy(c, "float")
        z = pos
        dr = rt.f(1.0)
        r = rt.f(0.0)
        trap = rt.f(10000000000.0)
        iter = rt.f(0.0)
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
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
            z[:] = rt.binary("+", z, c, 3, "float")
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
        dist = rt.binary("/", rt.binary("*", rt.binary("*", rt.f(0.5), rt.component_wise("log", r, width=1), 1, "float"), r, 1, "float"), dr, 1, "float")
        return rt.construct(3, dist, trap, rt.binary("/", iter, rt.construct(1, maxIter), 1, "float"))
    def boxFold__vec3_float(z, foldingLimit):
        z = rt.copy(z, "float")
        return rt.binary("-", rt.binary("*", rt.component_wise("clamp", z, rt.unary("-", foldingLimit), foldingLimit, width=3), rt.f(2.0), 3, "float"), z, 3, "float")
    def mandelcube__vec3_float_int_float(pos, scale, maxIter, bail):
        pos = rt.copy(pos, "float")
        z = pos
        dr = rt.f(1.0)
        trap = rt.f(10000000000.0)
        iter = rt.f(0.0)
        foldingLimit = rt.f(1.0)
        minRadius = rt.f(0.5)
        fixedRadius = rt.f(1.0)
        i = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", i, maxIter)):
                break
            z[:] = boxFold__vec3_float(z, foldingLimit)
            r2 = rt.dot(z, z)
            minR2 = rt.binary("*", minRadius, minRadius, 1, "float")
            fixedR2 = rt.binary("*", fixedRadius, fixedRadius, 1, "float")
            factor = rt.f(0.0)
            if rt.binary("<", r2, minR2):
                factor = rt.binary("/", fixedR2, minR2, 1, "float")
                z[:] = rt.binary("*", z, factor, 3, "float")
                dr = rt.binary("*", dr, factor, 1, "float")
            else:
                if rt.binary("<", r2, fixedR2):
                    factor = rt.binary("/", fixedR2, r2, 1, "float")
                    z[:] = rt.binary("*", z, factor, 3, "float")
                    dr = rt.binary("*", dr, factor, 1, "float")
            z[:] = rt.binary("+", rt.binary("*", z, scale, 3, "float"), pos, 3, "float")
            dr = rt.binary("+", rt.binary("*", dr, rt.component_wise("abs", scale, width=1), 1, "float"), rt.f(1.0), 1, "float")
            trap = rt.component_wise("min", trap, rt.length(z), width=1)
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
            if rt.binary(">", rt.length(z), bail):
                break
        r = rt.length(z)
        dist = rt.binary("/", r, rt.component_wise("abs", dr, width=1), 1, "float")
        return rt.construct(3, dist, trap, rt.binary("/", iter, rt.construct(1, maxIter), 1, "float"))
    def juliaCube__vec3_vec3_float_int_float(pos, c, scale, maxIter, bail):
        pos = rt.copy(pos, "float")
        c = rt.copy(c, "float")
        z = pos
        dr = rt.f(1.0)
        trap = rt.f(10000000000.0)
        iter = rt.f(0.0)
        foldingLimit = rt.f(1.0)
        minRadius = rt.f(0.5)
        fixedRadius = rt.f(1.0)
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for3_first = False
            if not (rt.binary("<", i, maxIter)):
                break
            z[:] = boxFold__vec3_float(z, foldingLimit)
            r2 = rt.dot(z, z)
            minR2 = rt.binary("*", minRadius, minRadius, 1, "float")
            fixedR2 = rt.binary("*", fixedRadius, fixedRadius, 1, "float")
            factor = rt.f(0.0)
            if rt.binary("<", r2, minR2):
                factor = rt.binary("/", fixedR2, minR2, 1, "float")
                z[:] = rt.binary("*", z, factor, 3, "float")
                dr = rt.binary("*", dr, factor, 1, "float")
            else:
                if rt.binary("<", r2, fixedR2):
                    factor = rt.binary("/", fixedR2, r2, 1, "float")
                    z[:] = rt.binary("*", z, factor, 3, "float")
                    dr = rt.binary("*", dr, factor, 1, "float")
            z[:] = rt.binary("+", rt.binary("*", z, scale, 3, "float"), c, 3, "float")
            dr = rt.binary("+", rt.binary("*", dr, rt.component_wise("abs", scale, width=1), 1, "float"), rt.f(1.0), 1, "float")
            trap = rt.component_wise("min", trap, rt.length(z), width=1)
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
            if rt.binary(">", rt.length(z), bail):
                break
        r = rt.length(z)
        dist = rt.binary("/", r, rt.component_wise("abs", dr, width=1), 1, "float")
        return rt.construct(3, dist, trap, rt.binary("/", iter, rt.construct(1, maxIter), 1, "float"))
    def computeFractal__vec3_vec3(p, juliaC):
        p = rt.copy(p, "float")
        juliaC = rt.copy(juliaC, "float")
        scale = rt.f(0.0)
        if rt.binary("==", _u_noiseType, rt.i(0)):
            return mandelbulb__vec3_float_int_float(p, _u_power, _u_iterations, _u_bailout)
        else:
            if rt.binary("==", _u_noiseType, rt.i(1)):
                scale = rt.component_wise("clamp", rt.binary("*", _u_power, rt.f(0.25), 1, "float"), rt.unary("-", rt.f(3.0)), rt.f(3.0), width=1)
                return mandelcube__vec3_float_int_float(p, scale, _u_iterations, _u_bailout)
            else:
                if rt.binary("==", _u_noiseType, rt.i(2)):
                    return juliaBulb__vec3_vec3_float_int_float(p, juliaC, _u_power, _u_iterations, _u_bailout)
                else:
                    scale = rt.component_wise("clamp", rt.binary("*", _u_power, rt.f(0.25), 1, "float"), rt.unary("-", rt.f(3.0)), rt.f(3.0), width=1)
                    return juliaCube__vec3_vec3_float_int_float(p, juliaC, scale, _u_iterations, _u_bailout)
    def main__void():
        volSize = _u_volumeSize
        scaledVolSize = rt.construct(1, rt.binary("*", rt.construct(1, volSize), _u_renderScale, 1, "float"), base="int")
        scaledVolSizeF = rt.construct(1, scaledVolSize)
        globalPixelCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        pixelCoord = rt.construct(2, globalPixelCoord, base="int")
        x = rt.construct(1, rt.component_wise("mod", rt.construct(1, rt.swizzle(pixelCoord, "x")), scaledVolSizeF, width=1), base="int")
        y = rt.binary("%", rt.swizzle(pixelCoord, "y"), scaledVolSize, 1, "int")
        z = rt.binary("/", rt.swizzle(pixelCoord, "y"), scaledVolSize, 1, "int")
        if (bool((bool(rt.binary(">=", x, scaledVolSize)) or bool(rt.binary(">=", y, scaledVolSize)))) or bool(rt.binary(">=", z, scaledVolSize))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))
            return
        p = rt.binary("*", rt.binary("-", rt.binary("*", rt.binary("/", rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z)), rt.binary("-", scaledVolSizeF, rt.f(1.0), 1, "float"), 3, "float"), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float"), rt.f(1.5), 3, "float")
        juliaC = rt.binary("*", rt.construct(3, _u_juliaX, _u_juliaY, _u_juliaZ), rt.f(0.01), 3, "float")
        result = computeFractal__vec3_vec3(p, juliaC)
        dist = rt.swizzle(result, "x")
        normalizedDist = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("+", rt.binary("*", dist, rt.f(2.0), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")
        trap = rt.component_wise("clamp", rt.binary("*", rt.swizzle(result, "y"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        iterRatio = rt.swizzle(result, "z")
        eps = rt.f(0.01)
        dxp = rt.swizzle(computeFractal__vec3_vec3(rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), juliaC), "x")
        dyp = rt.swizzle(computeFractal__vec3_vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), juliaC), "x")
        dzp = rt.swizzle(computeFractal__vec3_vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), juliaC), "x")
        gradient = rt.binary("/", rt.construct(3, rt.binary("-", dxp, dist, 1, "float"), rt.binary("-", dyp, dist, 1, "float"), rt.binary("-", dzp, dist, 1, "float")), eps, 3, "float")
        normal = rt.normalize(rt.binary("+", gradient, rt.construct(3, rt.f(1e-06)), 3, "float"))
        if rt.binary("==", _u_colorMode, rt.i(0)):
            g.fragColor[:] = rt.construct(4, normalizedDist, normalizedDist, normalizedDist, rt.f(1.0))
        else:
            g.fragColor[:] = rt.construct(4, normalizedDist, trap, iterRatio, rt.f(1.0))
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), normalizedDist)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
