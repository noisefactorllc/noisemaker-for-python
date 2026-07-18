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
    _u_cReal = U.get("cReal", rt.f(0.0))
    _u_cImag = U.get("cImag", rt.f(0.0))
    _u_poi = U.get("poi", 0)
    _u_outputMode = U.get("outputMode", 0)
    _u_centerX = U.get("centerX", rt.f(0.0))
    _u_centerY = U.get("centerY", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_iterations = U.get("iterations", 0)
    _u_stripeFreq = U.get("stripeFreq", rt.f(0.0))
    _u_trapShape = U.get("trapShape", 0)
    _u_lightAngle = U.get("lightAngle", rt.f(0.0))
    _u_cPath = U.get("cPath", 0)
    _u_cSpeed = U.get("cSpeed", rt.f(0.0))
    _u_cRadius = U.get("cRadius", rt.f(0.0))
    _u_invert = U.get("invert", False)
    _u_zoomSpeed = U.get("zoomSpeed", rt.f(0.0))
    _u_zoomDepth = U.get("zoomDepth", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    g.BAILOUT = rt.f(256.0)
    g.LOG2 = rt.f(0.6931471805599453)
    g.df64_split_const = rt.f(4097.0)
    def getPOI__int(idx):
        if rt.binary("==", idx, rt.i(1)):
            return rt.construct(2, rt.unary("-", rt.f(0.123)), rt.f(0.745))
        if rt.binary("==", idx, rt.i(2)):
            return rt.construct(2, rt.unary("-", rt.f(0.3905)), rt.f(0.5868))
        if rt.binary("==", idx, rt.i(3)):
            return rt.construct(2, rt.f(0.0), rt.f(1.0))
        if rt.binary("==", idx, rt.i(4)):
            return rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0))
        if rt.binary("==", idx, rt.i(5)):
            return rt.construct(2, rt.unary("-", rt.f(0.7455)), rt.f(0.113))
        if rt.binary("==", idx, rt.i(6)):
            return rt.construct(2, rt.unary("-", rt.f(0.0986)), rt.f(0.6534))
        if rt.binary("==", idx, rt.i(7)):
            return rt.construct(2, rt.unary("-", rt.f(0.8)), rt.f(0.156))
        if rt.binary("==", idx, rt.i(8)):
            return rt.construct(2, rt.unary("-", rt.f(0.75)), rt.f(0.0))
        if rt.binary("==", idx, rt.i(9)):
            return rt.construct(2, rt.unary("-", rt.f(0.5792)), rt.f(0.5385))
        if rt.binary("==", idx, rt.i(10)):
            return rt.construct(2, rt.f(0.28), rt.f(0.008))
        return rt.construct(2, rt.unary("-", rt.f(0.123)), rt.f(0.745))
    def getAnimatedC__int_float_float(pathType, t, radius):
        theta = rt.binary("*", t, g.TAU, 1, "float")
        if rt.binary("==", pathType, rt.i(1)):
            return rt.construct(2, rt.binary("-", rt.binary("*", rt.component_wise("cos", theta, width=1), rt.f(0.5), 1, "float"), rt.binary("*", rt.component_wise("cos", rt.binary("*", rt.f(2.0), theta, 1, "float"), width=1), rt.f(0.25), 1, "float"), 1, "float"), rt.binary("-", rt.binary("*", rt.component_wise("sin", theta, width=1), rt.f(0.5), 1, "float"), rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.f(2.0), theta, 1, "float"), width=1), rt.f(0.25), 1, "float"), 1, "float"))
        if rt.binary("==", pathType, rt.i(2)):
            return rt.binary("*", rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), radius, 2, "float")
        if rt.binary("==", pathType, rt.i(3)):
            return rt.construct(2, rt.binary("+", rt.unary("-", rt.f(1.0)), rt.binary("*", rt.component_wise("cos", theta, width=1), rt.f(0.25), 1, "float"), 1, "float"), rt.binary("*", rt.component_wise("sin", theta, width=1), rt.f(0.25), 1, "float"))
        return rt.construct(2, rt.f(0.0))
    def cmul__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "x"), 1, "float"), rt.binary("*", rt.swizzle(a, "y"), rt.swizzle(b, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "y"), 1, "float"), rt.binary("*", rt.swizzle(a, "y"), rt.swizzle(b, "x"), 1, "float"), 1, "float"))
    def df64_from__float(a):
        return rt.construct(2, a, rt.f(0.0))
    def df64_add__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        s = rt.binary("+", rt.swizzle(a, "x"), rt.swizzle(b, "x"), 1, "float")
        v = rt.binary("-", s, rt.swizzle(a, "x"), 1, "float")
        e = rt.binary("+", rt.binary("-", rt.swizzle(a, "x"), rt.binary("-", s, v, 1, "float"), 1, "float"), rt.binary("-", rt.swizzle(b, "x"), v, 1, "float"), 1, "float")
        return rt.construct(2, s, rt.binary("+", rt.binary("+", e, rt.swizzle(a, "y"), 1, "float"), rt.swizzle(b, "y"), 1, "float"))
    def df64_sub__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        return df64_add__vec2_vec2(a, rt.construct(2, rt.unary("-", rt.swizzle(b, "x")), rt.unary("-", rt.swizzle(b, "y"))))
    def df64_split__float_float_float(a, hi, lo):
        t = rt.binary("*", g.df64_split_const, a, 1, "float")
        hi = rt.binary("-", t, rt.binary("-", t, a, 1, "float"), 1, "float")
        lo = rt.binary("-", a, hi, 1, "float")
        return (None, hi, lo)
    def df64_mul__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        p = rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "x"), 1, "float")
        ahi = rt.f(0.0)
        alo = rt.f(0.0)
        bhi = rt.f(0.0)
        blo = rt.f(0.0)
        _retc, ahi, alo = df64_split__float_float_float(rt.swizzle(a, "x"), ahi, alo)
        _retc, bhi, blo = df64_split__float_float_float(rt.swizzle(b, "x"), bhi, blo)
        e = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("*", ahi, bhi, 1, "float"), p, 1, "float"), rt.binary("*", ahi, blo, 1, "float"), 1, "float"), rt.binary("*", alo, bhi, 1, "float"), 1, "float"), rt.binary("*", alo, blo, 1, "float"), 1, "float")
        e = rt.binary("+", e, rt.binary("+", rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "y"), 1, "float"), rt.binary("*", rt.swizzle(a, "y"), rt.swizzle(b, "x"), 1, "float"), 1, "float"), 1, "float")
        return rt.construct(2, p, e)
    def df64_mul_f__vec2_float(a, b):
        a = rt.copy(a, "float")
        p = rt.binary("*", rt.swizzle(a, "x"), b, 1, "float")
        ahi = rt.f(0.0)
        alo = rt.f(0.0)
        bhi = rt.f(0.0)
        blo = rt.f(0.0)
        _retc, ahi, alo = df64_split__float_float_float(rt.swizzle(a, "x"), ahi, alo)
        _retc, bhi, blo = df64_split__float_float_float(b, bhi, blo)
        e = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("*", ahi, bhi, 1, "float"), p, 1, "float"), rt.binary("*", ahi, blo, 1, "float"), 1, "float"), rt.binary("*", alo, bhi, 1, "float"), 1, "float"), rt.binary("*", alo, blo, 1, "float"), 1, "float")
        e = rt.binary("+", e, rt.binary("*", rt.swizzle(a, "y"), b, 1, "float"), 1, "float")
        return rt.construct(2, p, e)
    def resolveC__void():
        if rt.binary(">", _u_poi, rt.i(0)):
            return getPOI__int(_u_poi)
        if rt.binary(">", _u_cPath, rt.i(0)):
            return getAnimatedC__int_float_float(_u_cPath, rt.binary("*", _u_time, _u_cSpeed, 1, "float"), _u_cRadius)
        return rt.construct(2, _u_cReal, _u_cImag)
    def transformCoords__vec2_float_vec2_vec2(fragCoord, zm, reDF, imDF):
        fragCoord = rt.copy(fragCoord, "float")
        reDF = rt.copy(reDF, "float")
        imDF = rt.copy(imDF, "float")
        uv = rt.binary("/", rt.binary("-", fragCoord, rt.binary("*", rt.f(0.5), _u_fullResolution, 2, "float"), 2, "float"), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 2, "float")
        angle = rt.binary("/", rt.binary("*", rt.unary("-", _u_rotation), g.TAU, 1, "float"), rt.f(360.0), 1, "float")
        cs = rt.component_wise("cos", angle, width=1)
        sn = rt.component_wise("sin", angle, width=1)
        uv[:] = rt.matrix_mult(rt.construct(4, cs, rt.unary("-", sn), sn, cs), uv, 2)
        scale = rt.binary("/", rt.f(2.5), zm, 1, "float")
        reDF[:] = df64_add__vec2_vec2(df64_mul_f__vec2_float(df64_from__float(rt.swizzle(uv, "x")), scale), df64_from__float(_u_centerX))
        imDF[:] = df64_add__vec2_vec2(df64_mul_f__vec2_float(df64_from__float(rt.swizzle(uv, "y")), scale), df64_from__float(_u_centerY))
        return (None, reDF, imDF)
    def juliaIterate__vec2_vec2_vec2_int_float_int(z0Re, z0Im, c, maxIter, freq, trap):
        z0Re = rt.copy(z0Re, "float")
        z0Im = rt.copy(z0Im, "float")
        c = rt.copy(c, "float")
        r = [rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)]
        zRe = z0Re
        zIm = z0Im
        dz = rt.construct(2, rt.f(1.0), rt.f(0.0))
        i = rt.f(0.0)
        stripeSum = rt.f(0.0)
        stripeLast = rt.f(0.0)
        stripeCount = rt.f(0.0)
        trapMin = rt.f(10000000000.0)
        bail2 = rt.binary("*", g.BAILOUT, g.BAILOUT, 1, "float")
        zSlow = rt.construct(2, rt.swizzle(z0Re, "x"), rt.swizzle(z0Im, "x"))
        period = rt.i(0)
        n = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                n = rt.binary("+", n, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", n, rt.i(1000))):
                break
            if rt.binary(">=", n, maxIter):
                break
            zF = rt.construct(2, rt.swizzle(zRe, "x"), rt.swizzle(zIm, "x"))
            dz[:] = rt.binary("*", rt.f(2.0), cmul__vec2_vec2(zF, dz), 2, "float")
            zRe2 = df64_mul__vec2_vec2(zRe, zRe)
            zIm2 = df64_mul__vec2_vec2(zIm, zIm)
            zReIm = df64_mul__vec2_vec2(zRe, zIm)
            zRe[:] = df64_add__vec2_vec2(df64_sub__vec2_vec2(zRe2, zIm2), df64_from__float(rt.swizzle(c, "x")))
            zIm[:] = df64_add__vec2_vec2(df64_mul_f__vec2_float(zReIm, rt.f(2.0)), df64_from__float(rt.swizzle(c, "y")))
            zMag2 = rt.binary("+", rt.binary("*", rt.swizzle(zRe, "x"), rt.swizzle(zRe, "x"), 1, "float"), rt.binary("*", rt.swizzle(zIm, "x"), rt.swizzle(zIm, "x"), 1, "float"), 1, "float")
            if rt.binary(">", zMag2, bail2):
                break
            i = rt.binary("+", i, rt.f(1.0), 1, "float")
            zHi = rt.construct(2, rt.swizzle(zRe, "x"), rt.swizzle(zIm, "x"))
            if rt.binary(">", freq, rt.f(0.0)):
                stripeLast = rt.binary("+", rt.binary("*", rt.f(0.5), rt.component_wise("sin", rt.binary("*", freq, rt.component_wise("atan", rt.swizzle(zHi, "y"), rt.swizzle(zHi, "x"), width=1), 1, "float"), width=1), 1, "float"), rt.f(0.5), 1, "float")
                stripeSum = rt.binary("+", stripeSum, stripeLast, 1, "float")
                stripeCount = rt.binary("+", stripeCount, rt.f(1.0), 1, "float")
            td = rt.f(0.0)
            if rt.binary("==", trap, rt.i(0)):
                td = rt.length(zHi)
            else:
                if rt.binary("==", trap, rt.i(1)):
                    td = rt.component_wise("min", rt.component_wise("abs", rt.swizzle(zHi, "x"), width=1), rt.component_wise("abs", rt.swizzle(zHi, "y"), width=1), width=1)
                else:
                    td = rt.component_wise("abs", rt.binary("-", rt.length(zHi), rt.f(1.0), 1, "float"), width=1)
            trapMin = rt.component_wise("min", trapMin, td, width=1)
            period = rt.binary("+", period, rt.i(1), 1, "int")
            if rt.binary("==", period, rt.i(20)):
                period = rt.i(0)
                zSlow[:] = zHi
            else:
                if rt.binary("<", rt.distance(zHi, zSlow), rt.f(1e-10)):
                    i = rt.construct(1, maxIter)
                    break
        r[0] = i
        r[1] = rt.binary("+", rt.binary("*", rt.swizzle(zRe, "x"), rt.swizzle(zRe, "x"), 1, "float"), rt.binary("*", rt.swizzle(zIm, "x"), rt.swizzle(zIm, "x"), 1, "float"), 1, "float")
        r[2] = rt.dot(dz, dz)
        r[3] = stripeSum
        r[4] = stripeCount
        r[5] = stripeLast
        r[6] = trapMin
        return r
    def outputSmoothIteration__struct1_float(r, maxIter):
        if rt.binary(">=", r[0], maxIter):
            return rt.f(0.0)
        log_zn = rt.binary("*", rt.component_wise("log", r[1], width=1), rt.f(0.5), 1, "float")
        nu = rt.binary("/", rt.component_wise("log", rt.binary("/", log_zn, g.LOG2, 1, "float"), width=1), g.LOG2, 1, "float")
        return rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("+", r[0], rt.f(1.0), 1, "float"), nu, 1, "float"), maxIter, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def outputDistanceEstimation__struct1_float(r, maxIter):
        if rt.binary(">=", r[0], maxIter):
            return rt.f(0.0)
        zMag = rt.component_wise("sqrt", r[1], width=1)
        dzMag = rt.component_wise("sqrt", r[2], width=1)
        if rt.binary("<", dzMag, rt.f(1e-10)):
            return rt.f(0.0)
        dist = rt.binary("/", rt.binary("*", rt.binary("*", rt.f(2.0), zMag, 1, "float"), rt.component_wise("log", zMag, width=1), 1, "float"), dzMag, 1, "float")
        return rt.component_wise("clamp", rt.binary("*", rt.component_wise("log", rt.binary("+", dist, rt.f(1.0), 1, "float"), width=1), rt.f(2.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def outputStripeAverage__struct1_float(r, maxIter):
        if rt.binary(">=", r[0], maxIter):
            return rt.f(0.0)
        if rt.binary("<", r[4], rt.f(1.0)):
            return rt.f(0.0)
        avg = rt.binary("/", r[3], r[4], 1, "float")
        prevAvg = (rt.binary("/", rt.binary("-", r[3], r[5], 1, "float"), rt.binary("-", r[4], rt.f(1.0), 1, "float"), 1, "float") if rt.binary(">", r[4], rt.f(1.0)) else avg)
        log_zn = rt.binary("*", rt.component_wise("log", r[1], width=1), rt.f(0.5), 1, "float")
        nu = rt.binary("/", rt.component_wise("log", rt.binary("/", log_zn, g.LOG2, 1, "float"), width=1), g.LOG2, 1, "float")
        frac = rt.component_wise("clamp", rt.binary("+", rt.binary("-", rt.f(1.0), nu, 1, "float"), rt.component_wise("floor", nu, width=1), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.component_wise("clamp", rt.component_wise("mix", prevAvg, avg, frac, width=1), rt.f(0.0), rt.f(1.0), width=1)
    def outputOrbitTrap__struct1_float(r, maxIter):
        if rt.binary(">=", r[0], maxIter):
            return rt.f(0.0)
        return rt.component_wise("clamp", rt.binary("-", rt.f(1.0), r[6], 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def iterateSmooth__vec2_vec2_int_float(fragCoord, c, maxIter, zm):
        fragCoord = rt.copy(fragCoord, "float")
        c = rt.copy(c, "float")
        reDF = rt.construct(2, 0.0)
        imDF = rt.construct(2, 0.0)
        _retc, reDF, imDF = transformCoords__vec2_float_vec2_vec2(fragCoord, zm, reDF, imDF)
        zRe = reDF
        zIm = imDF
        i = rt.f(0.0)
        bail2 = rt.binary("*", g.BAILOUT, g.BAILOUT, 1, "float")
        n = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                n = rt.binary("+", n, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", n, rt.i(1000))):
                break
            if rt.binary(">=", n, maxIter):
                break
            zRe2 = df64_mul__vec2_vec2(zRe, zRe)
            zIm2 = df64_mul__vec2_vec2(zIm, zIm)
            zReIm = df64_mul__vec2_vec2(zRe, zIm)
            zRe[:] = df64_add__vec2_vec2(df64_sub__vec2_vec2(zRe2, zIm2), df64_from__float(rt.swizzle(c, "x")))
            zIm[:] = df64_add__vec2_vec2(df64_mul_f__vec2_float(zReIm, rt.f(2.0)), df64_from__float(rt.swizzle(c, "y")))
            zMag2 = rt.binary("+", rt.binary("*", rt.swizzle(zRe, "x"), rt.swizzle(zRe, "x"), 1, "float"), rt.binary("*", rt.swizzle(zIm, "x"), rt.swizzle(zIm, "x"), 1, "float"), 1, "float")
            if rt.binary(">", zMag2, bail2):
                break
            i = rt.binary("+", i, rt.f(1.0), 1, "float")
        if rt.binary(">=", i, rt.construct(1, maxIter)):
            return rt.f(0.0)
        zMag2 = rt.binary("+", rt.binary("*", rt.swizzle(zRe, "x"), rt.swizzle(zRe, "x"), 1, "float"), rt.binary("*", rt.swizzle(zIm, "x"), rt.swizzle(zIm, "x"), 1, "float"), 1, "float")
        log_zn = rt.binary("*", rt.component_wise("log", zMag2, width=1), rt.f(0.5), 1, "float")
        nu = rt.binary("/", rt.component_wise("log", rt.binary("/", log_zn, g.LOG2, 1, "float"), width=1), g.LOG2, 1, "float")
        return rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.binary("+", i, rt.f(1.0), 1, "float"), nu, 1, "float"), rt.construct(1, maxIter), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def outputNormalMap__vec2_vec2_int_float_float(fragCoord, c, maxIter, angle, zm):
        fragCoord = rt.copy(fragCoord, "float")
        c = rt.copy(c, "float")
        d0 = iterateSmooth__vec2_vec2_int_float(fragCoord, c, maxIter, zm)
        d1 = iterateSmooth__vec2_vec2_int_float(rt.binary("+", fragCoord, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), c, maxIter, zm)
        d2 = iterateSmooth__vec2_vec2_int_float(rt.binary("+", fragCoord, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), c, maxIter, zm)
        normal = rt.normalize(rt.construct(3, rt.binary("-", d1, d0, 1, "float"), rt.binary("-", d2, d0, 1, "float"), rt.f(0.05)))
        rad = rt.binary("/", rt.binary("*", angle, g.TAU, 1, "float"), rt.f(360.0), 1, "float")
        lightDir = rt.normalize(rt.construct(3, rt.component_wise("cos", rad, width=1), rt.component_wise("sin", rad, width=1), rt.f(0.7)))
        return rt.component_wise("clamp", rt.component_wise("max", rt.dot(normal, lightDir), rt.f(0.0), width=1), rt.f(0.0), rt.f(1.0), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        c = resolveC__void()
        effectiveZoom = rt.f(0.0)
        phase = rt.f(0.0)
        if rt.binary(">", _u_zoomSpeed, rt.f(0.0)):
            phase = rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", rt.binary("*", _u_time, _u_zoomSpeed, 1, "float"), g.TAU, 1, "float"), width=1), 1, "float"), 1, "float")
            effectiveZoom = rt.component_wise("pow", rt.f(10.0), rt.binary("*", _u_zoomDepth, phase, 1, "float"), width=1)
        else:
            effectiveZoom = rt.component_wise("pow", rt.f(10.0), _u_zoomDepth, width=1)
        value = rt.f(0.0)
        reDF = rt.construct(2, 0.0)
        imDF = rt.construct(2, 0.0)
        r = [rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)]
        if rt.binary("==", _u_outputMode, rt.i(4)):
            value = outputNormalMap__vec2_vec2_int_float_float(globalCoord, c, _u_iterations, _u_lightAngle, effectiveZoom)
        else:
            reDF = rt.construct(2, 0.0)
            imDF = rt.construct(2, 0.0)
            _retc, reDF, imDF = transformCoords__vec2_float_vec2_vec2(globalCoord, effectiveZoom, reDF, imDF)
            r = juliaIterate__vec2_vec2_vec2_int_float_int(reDF, imDF, c, _u_iterations, _u_stripeFreq, _u_trapShape)
            if rt.binary("==", _u_outputMode, rt.i(0)):
                value = outputSmoothIteration__struct1_float(r, rt.construct(1, _u_iterations))
            else:
                if rt.binary("==", _u_outputMode, rt.i(1)):
                    value = outputDistanceEstimation__struct1_float(r, rt.construct(1, _u_iterations))
                else:
                    if rt.binary("==", _u_outputMode, rt.i(2)):
                        value = outputStripeAverage__struct1_float(r, rt.construct(1, _u_iterations))
                    else:
                        if rt.binary("==", _u_outputMode, rt.i(3)):
                            value = outputOrbitTrap__struct1_float(r, rt.construct(1, _u_iterations))
                        else:
                            value = outputSmoothIteration__struct1_float(r, rt.construct(1, _u_iterations))
        if _u_invert:
            value = rt.binary("-", rt.f(1.0), value, 1, "float")
        g.fragColor[:] = rt.construct(4, rt.construct(3, value), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
