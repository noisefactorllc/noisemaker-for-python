def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_poi = U["poi"]
    _u_outputMode = U["outputMode"]
    _u_iterations = U["iterations"]
    _u_centerHiX = U["centerHiX"]
    _u_centerHiY = U["centerHiY"]
    _u_centerLoX = U["centerLoX"]
    _u_centerLoY = U["centerLoY"]
    _u_zoomSpeed = U["zoomSpeed"]
    _u_zoomDepth = U["zoomDepth"]
    _u_invert = U["invert"]
    _u_stripeFreq = U["stripeFreq"]
    _u_trapShape = U["trapShape"]
    _u_lightAngle = U["lightAngle"]
    _u_rotation = U["rotation"]
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    g.BAILOUT = rt.f(256.0)
    g.LOG2 = rt.f(0.6931471805599453)
    g.MAX_ITER = rt.i(500)
    def df64_quick_two_sum__float_float(a, b):
        s = rt.binary("+", a, b, 1)
        e = rt.binary("-", b, rt.binary("-", s, a, 1), 1)
        return rt.construct(2, s, e)
    def df64_two_sum__float_float(a, b):
        s = rt.binary("+", a, b, 1)
        v = rt.binary("-", s, a, 1)
        e = rt.binary("+", rt.binary("-", a, rt.binary("-", s, v, 1), 1), rt.binary("-", b, v, 1), 1)
        return rt.construct(2, s, e)
    def df64_two_prod__float_float(a, b):
        p = rt.binary("*", a, b, 1)
        ca = rt.binary("*", rt.f(4097.0), a, 1)
        ah = rt.binary("-", ca, rt.binary("-", ca, a, 1), 1)
        al = rt.binary("-", a, ah, 1)
        cb = rt.binary("*", rt.f(4097.0), b, 1)
        bh = rt.binary("-", cb, rt.binary("-", cb, b, 1), 1)
        bl = rt.binary("-", b, bh, 1)
        e = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("*", ah, bh, 1), p, 1), rt.binary("*", ah, bl, 1), 1), rt.binary("*", al, bh, 1), 1), rt.binary("*", al, bl, 1), 1)
        return rt.construct(2, p, e)
    def df64_add__vec2_vec2(a, b):
        a = rt.copy(a)
        b = rt.copy(b)
        s = df64_two_sum__float_float(rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        s = rt.assign_swizzle(s, "y", rt.binary("+", rt.swizzle(s, "y"), rt.binary("+", rt.swizzle(a, "y"), rt.swizzle(b, "y"), 1), 1))
        return df64_quick_two_sum__float_float(rt.swizzle(s, "x"), rt.swizzle(s, "y"))
    def df64_sub__vec2_vec2(a, b):
        a = rt.copy(a)
        b = rt.copy(b)
        return df64_add__vec2_vec2(a, rt.construct(2, rt.unary("-", rt.swizzle(b, "x")), rt.unary("-", rt.swizzle(b, "y"))))
    def df64_mul__vec2_vec2(a, b):
        a = rt.copy(a)
        b = rt.copy(b)
        p = df64_two_prod__float_float(rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("+", rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "y"), 1), rt.binary("*", rt.swizzle(a, "y"), rt.swizzle(b, "x"), 1), 1), 1))
        return df64_quick_two_sum__float_float(rt.swizzle(p, "x"), rt.swizzle(p, "y"))
    def df64_mul_f__vec2_float(a, b):
        a = rt.copy(a)
        p = df64_two_prod__float_float(rt.swizzle(a, "x"), b)
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("*", rt.swizzle(a, "y"), b, 1), 1))
        return df64_quick_two_sum__float_float(rt.swizzle(p, "x"), rt.swizzle(p, "y"))
    def df64_from__float(a):
        return rt.construct(2, a, rt.f(0.0))
    def df64_to_float__vec2(a):
        a = rt.copy(a)
        return rt.binary("+", rt.swizzle(a, "x"), rt.swizzle(a, "y"), 1)
    def getPoiMaxZoom__int(index):
        if rt.binary("||", rt.binary("==", index, rt.i(2)), rt.binary("==", index, rt.i(7))):
            return rt.f(7.0)
        if rt.binary("==", index, rt.i(8)):
            return rt.f(10.0)
        return rt.f(14.0)
    def getPOI__int_vec2_vec2(index, cX_df, cY_df):
        cX_df = rt.copy(cX_df)
        cY_df = rt.copy(cY_df)
        if rt.binary("==", index, rt.i(1)):
            cX_df = rt.construct(2, rt.unary("-", rt.f(0.7445398569107056)), rt.unary("-", rt.f(3.4452027897e-9)))
            cY_df = rt.construct(2, rt.f(0.12172377109527588), rt.f(2.7991489404e-9))
        else:
            if rt.binary("==", index, rt.i(2)):
                cX_df = rt.construct(2, rt.f(0.29833000898361206), rt.unary("-", rt.f(8.9836120765e-9)))
                cY_df = rt.construct(2, rt.f(0.0011099999537691474), rt.f(4.6230852696e-11))
            else:
                if rt.binary("==", index, rt.i(3)):
                    cX_df = rt.construct(2, rt.unary("-", rt.f(1.7548776865005493)), rt.f(2.0253856592e-8))
                    cY_df = rt.construct(2, rt.f(0.0), rt.f(0.0))
                else:
                    if rt.binary("==", index, rt.i(4)):
                        cX_df = rt.construct(2, rt.unary("-", rt.f(1.7400623559951782)), rt.unary("-", rt.f(2.6584161761e-8)))
                        cY_df = rt.construct(2, rt.f(0.028175339102745056), rt.f(6.7646594229e-10))
                    else:
                        if rt.binary("==", index, rt.i(5)):
                            cX_df = rt.construct(2, rt.unary("-", rt.f(1.4011552333831787)), rt.f(4.4291128098e-8))
                            cY_df = rt.construct(2, rt.f(0.0), rt.f(0.0))
                        else:
                            if rt.binary("==", index, rt.i(6)):
                                cX_df = rt.construct(2, rt.f(0.37500011920928955), rt.f(8.5257595428e-10))
                                cY_df = rt.construct(2, rt.unary("-", rt.f(0.21663938462734222)), rt.unary("-", rt.f(3.8103704636e-9)))
                            else:
                                if rt.binary("==", index, rt.i(7)):
                                    cX_df = rt.construct(2, rt.unary("-", rt.f(0.7445389032363892)), rt.unary("-", rt.f(1.6763610833e-8)))
                                    cY_df = rt.construct(2, rt.f(0.12172418087720871), rt.unary("-", rt.f(8.7720870845e-10)))
                                else:
                                    if rt.binary("==", index, rt.i(8)):
                                        cX_df = rt.construct(2, rt.unary("-", rt.f(1.2553445100784302)), rt.unary("-", rt.f(1.4721569741e-8)))
                                        cY_df = rt.construct(2, rt.unary("-", rt.f(0.3822004497051239)), rt.unary("-", rt.f(1.3294876089e-8)))
                                    else:
                                        cX_df = rt.construct(2, _u_centerHiX, _u_centerLoX)
                                        cY_df = rt.construct(2, _u_centerHiY, _u_centerLoY)
    def transformCoords_df64__vec2_vec2_vec2_float_float_vec2_vec2(fragCoord, cX_df, cY_df, z, rot, re_df, im_df):
        fragCoord = rt.copy(fragCoord)
        cX_df = rt.copy(cX_df)
        cY_df = rt.copy(cY_df)
        re_df = rt.copy(re_df)
        im_df = rt.copy(im_df)
        uv = rt.binary("/", rt.binary("-", fragCoord, rt.binary("*", rt.f(0.5), _u_fullResolution, 2), 2), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 2)
        angle = rt.binary("/", rt.binary("*", rt.unary("-", rot), g.TAU, 1), rt.f(360.0), 1)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        uv = rt.binary("*", rt.construct(4, c, rt.unary("-", s), s, c), uv, 4)
        scale = rt.binary("/", rt.f(2.5), z, 1)
        re_df = df64_add__vec2_vec2(df64_from__float(rt.binary("*", rt.swizzle(uv, "x"), scale, 1)), cX_df)
        im_df = df64_add__vec2_vec2(df64_from__float(rt.binary("*", rt.swizzle(uv, "y"), scale, 1)), cY_df)
    def inCardioid__float_float(x, y):
        y2 = rt.binary("*", y, y, 1)
        q = rt.binary("+", rt.binary("*", rt.binary("-", x, rt.f(0.25), 1), rt.binary("-", x, rt.f(0.25), 1), 1), y2, 1)
        return rt.binary("<=", rt.binary("*", q, rt.binary("+", q, rt.binary("-", x, rt.f(0.25), 1), 1), 1), rt.binary("*", rt.f(0.25), y2, 1))
    def inPeriod2Bulb__float_float(x, y):
        xp1 = rt.binary("+", x, rt.f(1.0), 1)
        return rt.binary("<=", rt.binary("+", rt.binary("*", xp1, xp1, 1), rt.binary("*", y, y, 1), 1), rt.f(0.0625))
    def trapDistance__vec2_int(z, shape):
        z = rt.copy(z)
        if rt.binary("==", shape, rt.i(0)):
            return rt.length(z)
        else:
            if rt.binary("==", shape, rt.i(1)):
                return rt.component_wise("min", rt.component_wise("abs", rt.swizzle(z, "x"), width=1), rt.component_wise("abs", rt.swizzle(z, "y"), width=1), width=1)
            else:
                return rt.component_wise("abs", rt.binary("-", rt.length(z), rt.f(1.0), 1), width=1)
    def mandelbrot_df64__vec2_vec2_int_float_float_vec2_vec2_float_float(c_re, c_im, maxIter, smoothIter, rawIter, z_final, dz_final, stripeAcc, trapMin):
        c_re = rt.copy(c_re)
        c_im = rt.copy(c_im)
        z_final = rt.copy(z_final)
        dz_final = rt.copy(dz_final)
        cx = df64_to_float__vec2(c_re)
        cy = df64_to_float__vec2(c_im)
        if rt.binary("||", inCardioid__float_float(cx, cy), inPeriod2Bulb__float_float(cx, cy)):
            smoothIter = maxIter
            rawIter = maxIter
            z_final = rt.construct(2, rt.f(0.0))
            dz_final = rt.construct(2, rt.f(0.0))
            stripeAcc = rt.f(0.0)
            trapMin = rt.f(1e20)
            return
        zr = rt.construct(2, rt.f(0.0))
        zi = rt.construct(2, rt.f(0.0))
        dz = rt.construct(2, rt.f(1.0), rt.f(0.0))
        stripe = rt.f(0.0)
        trap = rt.f(1e20)
        i = rt.f(0.0)
        n = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                n = rt.binary("+", n, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", n, g.MAX_ITER)):
                break
            if rt.binary(">=", n, maxIter):
                break
            zx = df64_to_float__vec2(zr)
            zy = df64_to_float__vec2(zi)
            dz = rt.construct(2, rt.binary("+", rt.binary("*", rt.f(2.0), rt.binary("-", rt.binary("*", zx, rt.swizzle(dz, "x"), 1), rt.binary("*", zy, rt.swizzle(dz, "y"), 1), 1), 1), rt.f(1.0), 1), rt.binary("*", rt.f(2.0), rt.binary("+", rt.binary("*", zx, rt.swizzle(dz, "y"), 1), rt.binary("*", zy, rt.swizzle(dz, "x"), 1), 1), 1))
            zr2 = df64_mul__vec2_vec2(zr, zr)
            zi2 = df64_mul__vec2_vec2(zi, zi)
            zri = df64_mul__vec2_vec2(zr, zi)
            new_zr = df64_add__vec2_vec2(df64_sub__vec2_vec2(zr2, zi2), c_re)
            new_zi = df64_add__vec2_vec2(df64_mul_f__vec2_float(zri, rt.f(2.0)), c_im)
            zr = new_zr
            zi = new_zi
            post_zx = df64_to_float__vec2(zr)
            post_zy = df64_to_float__vec2(zi)
            post_mag2 = rt.binary("+", rt.binary("*", post_zx, post_zx, 1), rt.binary("*", post_zy, post_zy, 1), 1)
            if rt.binary(">", _u_stripeFreq, rt.f(0.0)):
                stripe = rt.binary("+", stripe, rt.component_wise("sin", rt.binary("*", _u_stripeFreq, rt.component_wise("atan", post_zy, post_zx, width=1), 1), width=1), 1)
            trap = rt.component_wise("min", trap, trapDistance__vec2_int(rt.construct(2, post_zx, post_zy), _u_trapShape), width=1)
            if rt.binary(">", post_mag2, rt.binary("*", g.BAILOUT, g.BAILOUT, 1)):
                break
            i = rt.binary("+", i, rt.f(1.0), 1)
        rawIter = i
        fx = df64_to_float__vec2(zr)
        fy = df64_to_float__vec2(zi)
        z_final = rt.construct(2, fx, fy)
        dz_final = dz
        stripeAcc = stripe
        trapMin = trap
        mag2 = rt.dot(z_final, z_final)
        if rt.binary("&&", rt.binary("<", i, maxIter), rt.binary(">", mag2, rt.f(1.0))):
            log_zn = rt.binary("*", rt.component_wise("log", mag2, width=1), rt.f(0.5), 1)
            nu = rt.binary("/", rt.component_wise("log", rt.binary("/", log_zn, g.LOG2, 1), width=1), g.LOG2, 1)
            smoothIter = rt.binary("-", rt.binary("+", i, rt.f(1.0), 1), nu, 1)
        else:
            smoothIter = i
    def outputSmoothIteration__float_float_int(smoothIter, rawIter, maxIter):
        if rt.binary(">=", rawIter, maxIter):
            return rt.f(0.0)
        return rt.binary("/", smoothIter, maxIter, 1)
    def outputDistance__vec2_vec2_float_int(z, dz, rawIter, maxIter):
        z = rt.copy(z)
        dz = rt.copy(dz)
        if rt.binary(">=", rawIter, maxIter):
            return rt.f(0.0)
        mag = rt.length(z)
        dmag = rt.length(dz)
        if rt.binary("==", dmag, rt.f(0.0)):
            return rt.f(0.0)
        dist = rt.binary("/", rt.binary("*", rt.binary("*", rt.f(2.0), mag, 1), rt.component_wise("log", mag, width=1), 1), dmag, 1)
        return rt.component_wise("clamp", rt.binary("*", rt.component_wise("sqrt", rt.binary("*", dist, maxIter, 1), width=1), rt.f(0.5), 1), rt.f(0.0), rt.f(1.0), width=1)
    def outputStripeAverage__float_float_float_int(smoothIter, rawIter, stripeAcc, maxIter):
        if rt.binary(">=", rawIter, maxIter):
            return rt.f(0.0)
        count = rt.component_wise("max", rawIter, rt.f(1.0), width=1)
        avg = rt.binary("/", stripeAcc, count, 1)
        frac = rt.binary("-", smoothIter, rt.component_wise("floor", smoothIter, width=1), 1)
        return rt.component_wise("clamp", rt.binary("+", rt.f(0.5), rt.binary("*", rt.binary("*", rt.f(0.5), avg, 1), rt.binary("-", rt.f(1.0), frac, 1), 1), 1), rt.f(0.0), rt.f(1.0), width=1)
    def outputOrbitTrap__float_float_int(trapMin, rawIter, maxIter):
        if rt.binary(">=", rawIter, maxIter):
            return rt.f(0.0)
        return rt.component_wise("clamp", rt.binary("-", rt.f(1.0), rt.binary("*", trapMin, rt.f(0.5), 1), 1), rt.f(0.0), rt.f(1.0), width=1)
    def computeValueAt_df64__vec2_vec2_vec2_float_float_int(fragCoord, cX_df, cY_df, z_zoom, rot, maxIter):
        fragCoord = rt.copy(fragCoord)
        cX_df = rt.copy(cX_df)
        cY_df = rt.copy(cY_df)
        re_df = rt.construct(2, 0.0)
        im_df = rt.construct(2, 0.0)
        transformCoords_df64__vec2_vec2_vec2_float_float_vec2_vec2(fragCoord, cX_df, cY_df, z_zoom, rot, re_df, im_df)
        sI = rt.f(0.0)
        rI = rt.f(0.0)
        zf = rt.construct(2, 0.0)
        dzf = rt.construct(2, 0.0)
        sa = rt.f(0.0)
        tm = rt.f(0.0)
        mandelbrot_df64__vec2_vec2_int_float_float_vec2_vec2_float_float(re_df, im_df, maxIter, sI, rI, zf, dzf, sa, tm)
        return outputDistance__vec2_vec2_float_int(zf, dzf, rI, maxIter)
    def outputNormalMap__vec2_vec2_vec2_float_float_int_float(fragCoord, cX_df, cY_df, z_zoom, rot, maxIter, angle):
        fragCoord = rt.copy(fragCoord)
        cX_df = rt.copy(cX_df)
        cY_df = rt.copy(cY_df)
        eps = rt.binary("/", rt.f(1.0), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 1)
        h0 = computeValueAt_df64__vec2_vec2_vec2_float_float_int(fragCoord, cX_df, cY_df, z_zoom, rot, maxIter)
        hx = computeValueAt_df64__vec2_vec2_vec2_float_float_int(rt.binary("+", fragCoord, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2), cX_df, cY_df, z_zoom, rot, maxIter)
        hy = computeValueAt_df64__vec2_vec2_vec2_float_float_int(rt.binary("+", fragCoord, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2), cX_df, cY_df, z_zoom, rot, maxIter)
        normal = rt.normalize(rt.construct(3, rt.binary("-", h0, hx, 1), rt.binary("-", h0, hy, 1), eps))
        rad = rt.binary("/", rt.binary("*", angle, g.TAU, 1), rt.f(360.0), 1)
        lightDir = rt.normalize(rt.construct(3, rt.component_wise("cos", rad, width=1), rt.component_wise("sin", rad, width=1), rt.f(0.7)))
        diffuse = rt.component_wise("max", rt.dot(normal, lightDir), rt.f(0.0), width=1)
        return rt.component_wise("clamp", diffuse, rt.f(0.0), rt.f(1.0), width=1)
    def getEffectiveZoom__int(poiIndex):
        maxDepth = (getPoiMaxZoom__int(poiIndex) if rt.binary(">", poiIndex, rt.i(0)) else rt.f(14.0))
        effDepth = rt.component_wise("min", _u_zoomDepth, maxDepth, width=1)
        if rt.binary(">", _u_zoomSpeed, rt.f(0.0)):
            zoomPhase = rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", rt.binary("*", _u_time, _u_zoomSpeed, 1), g.TAU, 1), width=1), 1), 1)
            return rt.component_wise("pow", rt.f(10.0), rt.binary("*", effDepth, zoomPhase, 1), width=1)
        return rt.component_wise("pow", rt.f(10.0), effDepth, width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        maxIter = rt.component_wise("min", _u_iterations, g.MAX_ITER, width=1)
        effZoom = getEffectiveZoom__int(_u_poi)
        rot = (rt.f(0.0) if rt.binary(">", _u_poi, rt.i(0)) else _u_rotation)
        _local_cX_df_1 = rt.construct(2, 0.0)
        cY_df = rt.construct(2, 0.0)
        getPOI__int_vec2_vec2(_u_poi, _local_cX_df_1, cY_df)
        value = rt.f(0.0)
        if rt.binary("==", _u_outputMode, rt.i(4)):
            value = outputNormalMap__vec2_vec2_vec2_float_float_int_float(globalCoord, _local_cX_df_1, cY_df, effZoom, rot, maxIter, _u_lightAngle)
        else:
            smoothI = rt.f(0.0)
            rawI = rt.f(0.0)
            z_final = rt.construct(2, 0.0)
            dz_final = rt.construct(2, 0.0)
            stripeAcc = rt.f(0.0)
            trapMin = rt.f(0.0)
            re_df = rt.construct(2, 0.0)
            im_df = rt.construct(2, 0.0)
            transformCoords_df64__vec2_vec2_vec2_float_float_vec2_vec2(globalCoord, _local_cX_df_1, cY_df, effZoom, rot, re_df, im_df)
            mandelbrot_df64__vec2_vec2_int_float_float_vec2_vec2_float_float(re_df, im_df, maxIter, smoothI, rawI, z_final, dz_final, stripeAcc, trapMin)
            if rt.binary("==", _u_outputMode, rt.i(0)):
                value = outputSmoothIteration__float_float_int(smoothI, rawI, maxIter)
            else:
                if rt.binary("==", _u_outputMode, rt.i(1)):
                    value = outputDistance__vec2_vec2_float_int(z_final, dz_final, rawI, maxIter)
                else:
                    if rt.binary("==", _u_outputMode, rt.i(2)):
                        value = outputStripeAverage__float_float_float_int(smoothI, rawI, stripeAcc, maxIter)
                    else:
                        if rt.binary("==", _u_outputMode, rt.i(3)):
                            value = outputOrbitTrap__float_float_int(trapMin, rawI, maxIter)
                        else:
                            value = outputSmoothIteration__float_float_int(smoothI, rawI, maxIter)
        if rt.binary(">", _u_invert, rt.f(0.5)):
            value = rt.binary("-", rt.f(1.0), value, 1)
        g.fragColor = rt.construct(4, rt.construct(3, value), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
