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
    _u_degree = U.get("degree", rt.f(0.0))
    _u_relaxation = U.get("relaxation", rt.f(0.0))
    _u_iterations = U.get("iterations", rt.f(0.0))
    _u_tolerance = U.get("tolerance", rt.f(0.0))
    _u_poi = U.get("poi", rt.f(0.0))
    _u_centerHiX = U.get("centerHiX", rt.f(0.0))
    _u_centerHiY = U.get("centerHiY", rt.f(0.0))
    _u_centerLoX = U.get("centerLoX", rt.f(0.0))
    _u_centerLoY = U.get("centerLoY", rt.f(0.0))
    _u_zoomSpeed = U.get("zoomSpeed", rt.f(0.0))
    _u_zoomDepth = U.get("zoomDepth", rt.f(0.0))
    _u_degreeSpeed = U.get("degreeSpeed", rt.f(0.0))
    _u_degreeRange = U.get("degreeRange", rt.f(0.0))
    _u_relaxSpeed = U.get("relaxSpeed", rt.f(0.0))
    _u_relaxRange = U.get("relaxRange", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_outputMode = U.get("outputMode", rt.f(0.0))
    _u_invert = U.get("invert", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.PI = rt.f(3.14159265359)
    g.TAU = rt.f(6.28318530718)
    g.PHI = rt.f(1.6180339887)
    def df64_quick_two_sum__float_float(a, b):
        s = rt.binary("+", a, b, 1, "float")
        e = rt.binary("-", b, rt.binary("-", s, a, 1, "float"), 1, "float")
        return rt.construct(2, s, e)
    def df64_two_sum__float_float(a, b):
        s = rt.binary("+", a, b, 1, "float")
        v = rt.binary("-", s, a, 1, "float")
        e = rt.binary("+", rt.binary("-", a, rt.binary("-", s, v, 1, "float"), 1, "float"), rt.binary("-", b, v, 1, "float"), 1, "float")
        return rt.construct(2, s, e)
    def df64_two_prod__float_float(a, b):
        p = rt.binary("*", a, b, 1, "float")
        ca = rt.binary("*", rt.f(4097.0), a, 1, "float")
        ah = rt.binary("-", ca, rt.binary("-", ca, a, 1, "float"), 1, "float")
        al = rt.binary("-", a, ah, 1, "float")
        cb = rt.binary("*", rt.f(4097.0), b, 1, "float")
        bh = rt.binary("-", cb, rt.binary("-", cb, b, 1, "float"), 1, "float")
        bl = rt.binary("-", b, bh, 1, "float")
        e = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("*", ah, bh, 1, "float"), p, 1, "float"), rt.binary("*", ah, bl, 1, "float"), 1, "float"), rt.binary("*", al, bh, 1, "float"), 1, "float"), rt.binary("*", al, bl, 1, "float"), 1, "float")
        return rt.construct(2, p, e)
    def df64_add__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        s = df64_two_sum__float_float(rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        s = rt.assign_swizzle(s, "y", rt.binary("+", rt.swizzle(s, "y"), rt.binary("+", rt.swizzle(a, "y"), rt.swizzle(b, "y"), 1, "float"), 1, "float"))
        return df64_quick_two_sum__float_float(rt.swizzle(s, "x"), rt.swizzle(s, "y"))
    def df64_sub__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        return df64_add__vec2_vec2(a, rt.construct(2, rt.unary("-", rt.swizzle(b, "x")), rt.unary("-", rt.swizzle(b, "y"))))
    def df64_mul__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        p = df64_two_prod__float_float(rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("+", rt.binary("*", rt.swizzle(a, "x"), rt.swizzle(b, "y"), 1, "float"), rt.binary("*", rt.swizzle(a, "y"), rt.swizzle(b, "x"), 1, "float"), 1, "float"), 1, "float"))
        return df64_quick_two_sum__float_float(rt.swizzle(p, "x"), rt.swizzle(p, "y"))
    def df64_mul_f__vec2_float(a, b):
        a = rt.copy(a, "float")
        p = df64_two_prod__float_float(rt.swizzle(a, "x"), b)
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("*", rt.swizzle(a, "y"), b, 1, "float"), 1, "float"))
        return df64_quick_two_sum__float_float(rt.swizzle(p, "x"), rt.swizzle(p, "y"))
    def df64_from__float(a):
        return rt.construct(2, a, rt.f(0.0))
    def df64_to_float__vec2(a):
        a = rt.copy(a, "float")
        return rt.binary("+", rt.swizzle(a, "x"), rt.swizzle(a, "y"), 1, "float")
    def df64_cmul__vec2_vec2_vec2_vec2_vec2_vec2(ar, ai, br, bi, rr, ri):
        ar = rt.copy(ar, "float")
        ai = rt.copy(ai, "float")
        br = rt.copy(br, "float")
        bi = rt.copy(bi, "float")
        rr = rt.copy(rr, "float")
        ri = rt.copy(ri, "float")
        rr[:] = df64_sub__vec2_vec2(df64_mul__vec2_vec2(ar, br), df64_mul__vec2_vec2(ai, bi))
        ri[:] = df64_add__vec2_vec2(df64_mul__vec2_vec2(ar, bi), df64_mul__vec2_vec2(ai, br))
        return (None, rr, ri)
    def transformCoords_df64__vec2_vec2_vec2_float_float_vec2_vec2(fragCoord, cX_df, cY_df, z_zoom, rot, re_df, im_df):
        fragCoord = rt.copy(fragCoord, "float")
        cX_df = rt.copy(cX_df, "float")
        cY_df = rt.copy(cY_df, "float")
        re_df = rt.copy(re_df, "float")
        im_df = rt.copy(im_df, "float")
        uv = rt.binary("/", rt.binary("-", fragCoord, rt.binary("*", rt.f(0.5), _u_fullResolution, 2, "float"), 2, "float"), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 2, "float")
        angle = rt.binary("/", rt.binary("*", rt.unary("-", rot), g.TAU, 1, "float"), rt.f(360.0), 1, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        uv[:] = rt.matrix_mult(rt.construct(4, c, rt.unary("-", s), s, c), uv, 2)
        scale = rt.binary("/", rt.f(2.5), z_zoom, 1, "float")
        uv_re_df = df64_mul_f__vec2_float(df64_from__float(rt.swizzle(uv, "x")), scale)
        uv_im_df = df64_mul_f__vec2_float(df64_from__float(rt.swizzle(uv, "y")), scale)
        re_df[:] = df64_add__vec2_vec2(uv_re_df, cX_df)
        im_df[:] = df64_add__vec2_vec2(uv_im_df, cY_df)
        return (None, re_df, im_df)
    def getPOI__int(idx):
        if rt.binary("==", idx, rt.i(1)):
            return [rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.f(3.0), rt.f(7.0)]
        if rt.binary("==", idx, rt.i(2)):
            return [rt.construct(4, rt.f(0.25), rt.f(0.4330126941204071), rt.f(0.0), rt.f(7.7718e-09)), rt.f(3.0), rt.f(14.0)]
        if rt.binary("==", idx, rt.i(3)):
            return [rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.f(5.0), rt.f(7.0)]
        if rt.binary("==", idx, rt.i(4)):
            return [rt.construct(4, rt.f(0.6545084714889526), rt.f(0.4755282700061798), rt.f(2.5699e-08), rt.unary("-", rt.f(1.1859e-08))), rt.f(5.0), rt.f(14.0)]
        if rt.binary("==", idx, rt.i(5)):
            return [rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.f(6.0), rt.f(7.0)]
        if rt.binary("==", idx, rt.i(6)):
            return [rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0)), rt.f(8.0), rt.f(7.0)]
        return [rt.construct(4, rt.f(0.0)), rt.f(3.0), rt.f(7.0)]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        maxIter = rt.construct(1, _u_iterations, base="int")
        poiIdx = rt.construct(1, _u_poi, base="int")
        outMode = rt.construct(1, _u_outputMode, base="int")
        doInvert = rt.binary(">", _u_invert, rt.f(0.5))
        effDegree = _u_degree
        if (bool(rt.binary(">", _u_degreeSpeed, rt.f(0.0))) and bool(rt.binary(">", _u_degreeRange, rt.f(0.0)))):
            effDegree = rt.binary("+", effDegree, rt.binary("*", _u_degreeRange, rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, _u_degreeSpeed, 1, "float"), g.TAU, 1, "float"), width=1), 1, "float"), 1, "float")
            effDegree = rt.component_wise("clamp", effDegree, rt.f(3.0), rt.f(8.0), width=1)
        effRelax = _u_relaxation
        if (bool(rt.binary(">", _u_relaxSpeed, rt.f(0.0))) and bool(rt.binary(">", _u_relaxRange, rt.f(0.0)))):
            effRelax = rt.binary("+", effRelax, rt.binary("*", _u_relaxRange, rt.component_wise("sin", rt.binary("*", rt.binary("*", rt.binary("*", _u_time, _u_relaxSpeed, 1, "float"), g.TAU, 1, "float"), g.PHI, 1, "float"), width=1), 1, "float"), 1, "float")
            effRelax = rt.component_wise("clamp", effRelax, rt.f(0.5), rt.f(2.0), width=1)
        cHi = rt.construct(2, 0.0)
        cLo = rt.construct(2, 0.0)
        effZoomDepth = _u_zoomDepth
        p = [rt.construct(4, 0.0), rt.f(0.0), rt.f(0.0)]
        if rt.binary(">", poiIdx, rt.i(0)):
            p = getPOI__int(poiIdx)
            cHi[:] = rt.binary("+", rt.swizzle(p[0], "xy"), rt.construct(2, _u_centerHiX, _u_centerHiY), 2, "float")
            cLo[:] = rt.binary("+", rt.swizzle(p[0], "zw"), rt.construct(2, _u_centerLoX, _u_centerLoY), 2, "float")
            effDegree = p[1]
            effZoomDepth = rt.component_wise("min", _u_zoomDepth, p[2], width=1)
        else:
            (cHi.__setitem__(0, _u_centerHiX), cHi.__setitem__(1, _u_centerHiY), cHi)[-1]
            (cLo.__setitem__(0, _u_centerLoX), cLo.__setitem__(1, _u_centerLoY), cLo)[-1]
        zoom = rt.f(0.0)
        zoomPhase = rt.f(0.0)
        if rt.binary(">", _u_zoomSpeed, rt.f(0.0)):
            zoomPhase = rt.binary("*", rt.f(0.5), rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", rt.binary("*", _u_time, _u_zoomSpeed, 1, "float"), g.TAU, 1, "float"), width=1), 1, "float"), 1, "float")
            zoom = rt.component_wise("pow", rt.f(10.0), rt.binary("*", effZoomDepth, zoomPhase, 1, "float"), width=1)
        else:
            zoom = rt.component_wise("pow", rt.f(10.0), effZoomDepth, width=1)
        re_df = rt.construct(2, 0.0)
        im_df = rt.construct(2, 0.0)
        (((_retc0 := transformCoords_df64__vec2_vec2_vec2_float_float_vec2_vec2(globalCoord, rt.construct(2, rt.swizzle(cHi, "x"), rt.swizzle(cLo, "x")), rt.construct(2, rt.swizzle(cHi, "y"), rt.swizzle(cLo, "y")), zoom, _u_rotation, re_df, im_df)), re_df.__setitem__(slice(None), _retc0[1]), im_df.__setitem__(slice(None), _retc0[2]), _retc0[0])[-1])
        intDeg = rt.construct(1, rt.component_wise("floor", effDegree, width=1), base="int")
        numRoots = intDeg
        roots = rt.new_array(rt.i(8), 2)
        k = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                k = rt.binary("+", k, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", k, rt.i(8))):
                break
            if rt.binary(">=", k, numRoots):
                break
            angle = rt.binary("/", rt.binary("*", g.TAU, rt.construct(1, k), 1, "float"), rt.construct(1, intDeg), 1, "float")
            roots[int(k)] = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
        iter = rt.f(0.0)
        convergedRoot = rt.unary("-", rt.i(1))
        convergeDist = rt.f(1.0)
        bailout = rt.binary("*", rt.f(10000000000.0), effRelax, 1, "float")
        zr_df = re_df
        zi_df = im_df
        n = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                n = rt.binary("+", n, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", n, rt.i(500))):
                break
            if rt.binary(">=", n, maxIter):
                break
            pwr = df64_from__float(rt.f(1.0))
            pwi = df64_from__float(rt.f(0.0))
            j = rt.i(0)
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    j = rt.binary("+", j, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<", j, rt.i(7))):
                    break
                if rt.binary(">=", j, rt.binary("-", intDeg, rt.i(1), 1, "int")):
                    break
                tr = rt.construct(2, 0.0)
                ti = rt.construct(2, 0.0)
                (((_retc1 := df64_cmul__vec2_vec2_vec2_vec2_vec2_vec2(pwr, pwi, zr_df, zi_df, tr, ti)), tr.__setitem__(slice(None), _retc1[1]), ti.__setitem__(slice(None), _retc1[2]), _retc1[0])[-1])
                pwr[:] = tr
                pwi[:] = ti
            znr = rt.construct(2, 0.0)
            zni = rt.construct(2, 0.0)
            (((_retc2 := df64_cmul__vec2_vec2_vec2_vec2_vec2_vec2(pwr, pwi, zr_df, zi_df, znr, zni)), znr.__setitem__(slice(None), _retc2[1]), zni.__setitem__(slice(None), _retc2[2]), _retc2[0])[-1])
            fzr = df64_sub__vec2_vec2(znr, df64_from__float(rt.f(1.0)))
            fzi = zni
            fpzr = df64_mul_f__vec2_float(pwr, rt.construct(1, intDeg))
            fpzi = df64_mul_f__vec2_float(pwi, rt.construct(1, intDeg))
            fpzr_f = df64_to_float__vec2(fpzr)
            fpzi_f = df64_to_float__vec2(fpzi)
            if rt.binary("<", rt.binary("+", rt.binary("*", fpzr_f, fpzr_f, 1, "float"), rt.binary("*", fpzi_f, fpzi_f, 1, "float"), 1, "float"), rt.f(1e-20)):
                break
            denom = rt.binary("+", rt.binary("*", fpzr_f, fpzr_f, 1, "float"), rt.binary("*", fpzi_f, fpzi_f, 1, "float"), 1, "float")
            inv_denom = rt.binary("/", rt.f(1.0), denom, 1, "float")
            nr = df64_add__vec2_vec2(df64_mul__vec2_vec2(fzr, fpzr), df64_mul__vec2_vec2(fzi, fpzi))
            ni = df64_sub__vec2_vec2(df64_mul__vec2_vec2(fzi, fpzr), df64_mul__vec2_vec2(fzr, fpzi))
            dr = df64_mul_f__vec2_float(nr, inv_denom)
            di = df64_mul_f__vec2_float(ni, inv_denom)
            zr_df[:] = df64_sub__vec2_vec2(zr_df, df64_mul_f__vec2_float(dr, effRelax))
            zi_df[:] = df64_sub__vec2_vec2(zi_df, df64_mul_f__vec2_float(di, effRelax))
            zx = df64_to_float__vec2(zr_df)
            zy = df64_to_float__vec2(zi_df)
            if rt.binary(">", rt.binary("+", rt.binary("*", zx, zx, 1, "float"), rt.binary("*", zy, zy, 1, "float"), 1, "float"), bailout):
                break
            k = rt.i(0)
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    k = rt.binary("+", k, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<", k, rt.i(8))):
                    break
                if rt.binary(">=", k, numRoots):
                    break
                dx = rt.binary("-", zx, rt.swizzle(roots[int(k)], "x"), 1, "float")
                dy = rt.binary("-", zy, rt.swizzle(roots[int(k)], "y"), 1, "float")
                d = rt.component_wise("sqrt", rt.binary("+", rt.binary("*", dx, dx, 1, "float"), rt.binary("*", dy, dy, 1, "float"), 1, "float"), width=1)
                if rt.binary("<", d, _u_tolerance):
                    convergedRoot = k
                    convergeDist = d
                    break
            if rt.binary(">=", convergedRoot, rt.i(0)):
                break
            iter = rt.binary("+", iter, rt.f(1.0), 1, "float")
        smoothIter = iter
        if (bool((bool(rt.binary(">=", convergedRoot, rt.i(0))) and bool(rt.binary(">", convergeDist, rt.f(0.0))))) and bool(rt.binary("<", convergeDist, _u_tolerance))):
            smoothIter = rt.binary("-", iter, rt.component_wise("log2", rt.binary("/", rt.component_wise("log", convergeDist, width=1), rt.component_wise("log", _u_tolerance, width=1), 1, "float"), width=1), 1, "float")
        value = rt.f(0.0)
        maxIterF = rt.construct(1, maxIter)
        numRootsF = rt.construct(1, numRoots)
        if rt.binary("==", outMode, rt.i(0)):
            value = rt.binary("/", smoothIter, maxIterF, 1, "float")
        else:
            if rt.binary("==", outMode, rt.i(1)):
                if rt.binary(">=", convergedRoot, rt.i(0)):
                    value = rt.binary("/", rt.construct(1, convergedRoot), numRootsF, 1, "float")
            else:
                if rt.binary(">=", convergedRoot, rt.i(0)):
                    value = rt.binary("/", rt.binary("+", rt.construct(1, convergedRoot), rt.binary("/", smoothIter, maxIterF, 1, "float"), 1, "float"), numRootsF, 1, "float")
        if doInvert:
            value = rt.binary("-", rt.f(1.0), value, 1, "float")
        g.fragColor[:] = rt.construct(4, rt.construct(3, value), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
