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
    _u_aspect = U["aspect"]
    _u_scale = U["scale"]
    _u_rotation = U["rotation"]
    _u_thickness = U["thickness"]
    _u_smoothness = U["smoothness"]
    _u_geometry = U["geometry"]
    _u_rings = U["rings"]
    _u_starPoints = U["starPoints"]
    _u_animation = U["animation"]
    _u_speed = U["speed"]
    _u_pulseDepth = U["pulseDepth"]
    _u_time = U["time"]
    _u_fgColor = U["fgColor"]
    _u_bgColor = U["bgColor"]
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1), rt.binary("*", rt.swizzle(p, "y"), s, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1), rt.binary("*", rt.swizzle(p, "y"), c, 1), 1))
    def lineSegmentSDF__vec2_vec2_vec2(p, a, b):
        p = rt.copy(p)
        a = rt.copy(a)
        b = rt.copy(b)
        pa = rt.binary("-", p, a, 2)
        ba = rt.binary("-", b, a, 2)
        h = rt.component_wise("clamp", rt.binary("/", rt.dot(pa, ba), rt.dot(ba, ba), 1), rt.f(0.0), rt.f(1.0), width=1)
        return rt.length(rt.binary("-", pa, rt.binary("*", ba, h, 2), 2))
    def outlineEdge__float_float(d, w):
        return rt.component_wise("smoothstep", rt.binary("+", w, _u_smoothness, 1), rt.binary("-", w, _u_smoothness, 1), rt.component_wise("abs", d, width=1), width=1)
    def ripplePulse__float(phase):
        return rt.binary("+", rt.f(1.0), rt.binary("*", _u_pulseDepth, rt.component_wise("sin", rt.binary("-", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), rt.component_wise("floor", _u_speed, width=1), 1), phase, 1), width=1), 1), 1)
    def unfoldVis__float(t_e):
        return rt.component_wise("max", rt.f(0.0), rt.component_wise("sin", rt.binary("*", rt.binary("*", rt.binary("-", _u_time, rt.binary("*", t_e, rt.f(0.5), 1), 1), rt.f(6.28318530718), 1), rt.component_wise("floor", _u_speed, width=1), 1), width=1), width=1)
    def flowerMask__vec2_int_float(p, ringsN, figureScale):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        circleRadius = rt.f(1.0)
        p = rt.binary("*", p, figureScale, 2)
        m = rt.f(0.0)
        q = rt.unary("-", rt.i(6))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                q = rt.binary("+", q, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", q, rt.i(6))):
                break
            if rt.binary("||", rt.binary("<", q, rt.unary("-", ringsN)), rt.binary(">", q, ringsN)):
                continue
            r = rt.unary("-", rt.i(6))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    r = rt.binary("+", r, rt.i(1), 1)
                _for1_first = False
                if not (rt.binary("<=", r, rt.i(6))):
                    break
                if rt.binary("||", rt.binary("<", r, rt.unary("-", ringsN)), rt.binary(">", r, ringsN)):
                    continue
                if rt.binary("||", rt.binary("<", rt.binary("+", q, r, 1), rt.unary("-", ringsN)), rt.binary(">", rt.binary("+", q, r, 1), ringsN)):
                    continue
                center = rt.construct(2, rt.binary("+", q, rt.binary("*", r, rt.f(0.5), 1), 1), rt.binary("*", rt.binary("*", r, rt.f(1.7320508075688772), 1), rt.f(0.5), 1))
                hexDist = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", q, width=1), rt.component_wise("abs", r, width=1), width=1), rt.component_wise("abs", rt.construct(1, rt.binary("+", q, r, 1)), width=1), width=1)
                circleR = circleRadius
                if rt.binary("==", _u_animation, rt.i(4)):
                    circleR = rt.binary("*", circleR, ripplePulse__float(rt.binary("*", hexDist, rt.f(1.4), 1)), 1)
                d = rt.binary("-", rt.length(rt.binary("-", p, center, 2)), circleR, 1)
                vis = rt.f(1.0)
                if rt.binary("==", _u_animation, rt.i(5)):
                    t_e = rt.binary("/", hexDist, rt.component_wise("max", ringsN, rt.f(1.0), width=1), 1)
                    vis = unfoldVis__float(t_e)
                m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(d, lineWidth), vis, 1), width=1)
        return m
    def fruitMask__vec2_bool(p, drawLines):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        p = rt.binary("*", p, rt.f(0.5), 2)
        centers = rt.construct(2, 0.0)
        centers[int(rt.i(0))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        k = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                k = rt.binary("+", k, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<", k, rt.i(6))):
                break
            angle = rt.binary("/", rt.binary("*", k, rt.f(3.14159265359), 1), rt.f(3.0), 1)
            centers[int(rt.binary("+", rt.i(1), k, 1))] = rt.binary("*", rt.f(2.0), rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), 2)
        k = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                k = rt.binary("+", k, rt.i(1), 1)
            _for3_first = False
            if not (rt.binary("<", k, rt.i(6))):
                break
            angle = rt.binary("+", rt.binary("/", rt.binary("*", k, rt.f(3.14159265359), 1), rt.f(3.0), 1), rt.binary("/", rt.f(3.14159265359), rt.f(6.0), 1), 1)
            centers[int(rt.binary("+", rt.i(7), k, 1))] = rt.binary("*", rt.binary("*", rt.f(2.0), rt.f(1.7320508075688772), 1), rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), 2)
        maxCircleDist = rt.binary("*", rt.f(2.0), rt.f(1.7320508075688772), 1)
        circleUnfoldRange = (rt.f(0.6) if drawLines else rt.f(1.0))
        m = rt.f(0.0)
        i = rt.i(0)
        _for4_first = True
        for _for4 in range(1048576):
            if not _for4_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for4_first = False
            if not (rt.binary("<", i, rt.i(13))):
                break
            distFromOrigin = rt.length(centers[int(i)])
            circleR = rt.f(1.0)
            if rt.binary("==", _u_animation, rt.i(4)):
                circleR = rt.binary("*", circleR, ripplePulse__float(rt.binary("*", distFromOrigin, rt.f(0.8), 1)), 1)
            d = rt.binary("-", rt.length(rt.binary("-", p, centers[int(i)], 2)), circleR, 1)
            vis = rt.f(1.0)
            if rt.binary("==", _u_animation, rt.i(5)):
                t_e = rt.binary("*", rt.binary("/", distFromOrigin, maxCircleDist, 1), circleUnfoldRange, 1)
                vis = unfoldVis__float(t_e)
            m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(d, lineWidth), vis, 1), width=1)
        if drawLines:
            lineVis = rt.f(1.0)
            if rt.binary("==", _u_animation, rt.i(5)):
                lineVis = unfoldVis__float(rt.f(0.65))
            i = rt.i(0)
            _for5_first = True
            for _for5 in range(1048576):
                if not _for5_first:
                    i = rt.binary("+", i, rt.i(1), 1)
                _for5_first = False
                if not (rt.binary("<", i, rt.i(13))):
                    break
                j = rt.i(0)
                _for6_first = True
                for _for6 in range(1048576):
                    if not _for6_first:
                        j = rt.binary("+", j, rt.i(1), 1)
                    _for6_first = False
                    if not (rt.binary("<", j, rt.i(13))):
                        break
                    if rt.binary("<=", j, i):
                        continue
                    dL = lineSegmentSDF__vec2_vec2_vec2(p, centers[int(i)], centers[int(j)])
                    m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(dL, rt.binary("*", lineWidth, rt.f(0.5), 1)), lineVis, 1), width=1)
        return m
    def vesicaMask__vec2(p):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        p = rt.binary("*", p, rt.f(0.25), 2)
        r = rt.f(1.5)
        sep = rt.binary("*", r, rt.f(0.5), 1)
        rA = r
        rB = r
        if rt.binary("==", _u_animation, rt.i(4)):
            rA = rt.binary("*", rA, ripplePulse__float(rt.f(0.0)), 1)
            rB = rt.binary("*", rB, ripplePulse__float(rt.f(3.14159265359)), 1)
        visA = rt.f(1.0)
        visB = rt.f(1.0)
        if rt.binary("==", _u_animation, rt.i(5)):
            visA = unfoldVis__float(rt.f(0.0))
            visB = unfoldVis__float(rt.f(0.5))
        dA = rt.binary("-", rt.length(rt.binary("-", p, rt.construct(2, rt.unary("-", sep), rt.f(0.0)), 2)), rA, 1)
        dB = rt.binary("-", rt.length(rt.binary("-", p, rt.construct(2, sep, rt.f(0.0)), 2)), rB, 1)
        m = rt.f(0.0)
        m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(dA, lineWidth), visA, 1), width=1)
        m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(dB, lineWidth), visB, 1), width=1)
        return m
    def triquetraMask__vec2(p):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        p = rt.binary("*", p, rt.f(0.30), 2)
        r = rt.f(2.25)
        dist = rt.binary("/", r, rt.f(1.7320508075688772), 1)
        C0 = rt.binary("*", dist, rt.construct(2, rt.component_wise("cos", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), width=1), rt.component_wise("sin", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), width=1)), 2)
        C1 = rt.binary("*", dist, rt.construct(2, rt.component_wise("cos", rt.binary("+", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), rt.binary("/", rt.f(6.28318530718), rt.f(3.0), 1), 1), width=1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), rt.binary("/", rt.f(6.28318530718), rt.f(3.0), 1), 1), width=1)), 2)
        C2 = rt.binary("*", dist, rt.construct(2, rt.component_wise("cos", rt.binary("+", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), rt.binary("/", rt.binary("*", rt.f(2.0), rt.f(6.28318530718), 1), rt.f(3.0), 1), 1), width=1), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), rt.binary("/", rt.binary("*", rt.f(2.0), rt.f(6.28318530718), 1), rt.f(3.0), 1), 1), width=1)), 2)
        r0 = r
        r1 = r
        r2 = r
        if rt.binary("==", _u_animation, rt.i(4)):
            r0 = rt.binary("*", r0, ripplePulse__float(rt.f(0.0)), 1)
            r1 = rt.binary("*", r1, ripplePulse__float(rt.binary("/", rt.f(6.28318530718), rt.f(3.0), 1)), 1)
            r2 = rt.binary("*", r2, ripplePulse__float(rt.binary("/", rt.binary("*", rt.f(2.0), rt.f(6.28318530718), 1), rt.f(3.0), 1)), 1)
        d0 = rt.binary("-", rt.length(rt.binary("-", p, C0, 2)), r0, 1)
        d1 = rt.binary("-", rt.length(rt.binary("-", p, C1, 2)), r1, 1)
        d2 = rt.binary("-", rt.length(rt.binary("-", p, C2, 2)), r2, 1)
        v01 = rt.f(1.0)
        v02 = rt.f(1.0)
        v12 = rt.f(1.0)
        if rt.binary("==", _u_animation, rt.i(5)):
            v01 = unfoldVis__float(rt.f(0.0))
            v02 = unfoldVis__float(rt.f(0.33))
            v12 = unfoldVis__float(rt.f(0.66))
        m = rt.f(0.0)
        m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(rt.component_wise("max", d0, d1, width=1), lineWidth), v01, 1), width=1)
        m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(rt.component_wise("max", d0, d2, width=1), lineWidth), v02, 1), width=1)
        m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(rt.component_wise("max", d1, d2, width=1), lineWidth), v12, 1), width=1)
        return m
    def borromeanMask__vec2(p):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        p = rt.binary("*", p, rt.f(0.32), 2)
        r = rt.f(1.5)
        dist = rt.f(1.4)
        m = rt.f(0.0)
        i = rt.i(0)
        _for7_first = True
        for _for7 in range(1048576):
            if not _for7_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for7_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            angle = rt.binary("+", rt.binary("/", rt.binary("*", i, rt.f(6.28318530718), 1), rt.f(3.0), 1), rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), 1)
            c = rt.binary("*", dist, rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), 2)
            circleR = r
            if rt.binary("==", _u_animation, rt.i(4)):
                circleR = rt.binary("*", circleR, ripplePulse__float(rt.binary("/", rt.binary("*", i, rt.f(6.28318530718), 1), rt.f(3.0), 1)), 1)
            d = rt.binary("-", rt.length(rt.binary("-", p, c, 2)), circleR, 1)
            vis = rt.f(1.0)
            if rt.binary("==", _u_animation, rt.i(5)):
                vis = unfoldVis__float(rt.binary("/", i, rt.f(3.0), 1))
            m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(d, lineWidth), vis, 1), width=1)
        return m
    def starPolygonMask__vec2_int(p, n):
        p = rt.copy(p)
        lineWidth = rt.binary("+", rt.f(0.04), rt.binary("*", _u_thickness, rt.f(0.12), 1), 1)
        p = rt.binary("*", p, rt.f(0.32), 2)
        radius = rt.f(2.8)
        if rt.binary("==", _u_animation, rt.i(4)):
            radius = rt.binary("*", radius, ripplePulse__float(rt.f(0.0)), 1)
        m = rt.f(0.0)
        i = rt.i(0)
        _for8_first = True
        for _for8 in range(1048576):
            if not _for8_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for8_first = False
            if not (rt.binary("<", i, rt.i(12))):
                break
            if rt.binary(">=", i, n):
                break
            j = rt.binary("-", rt.binary("+", i, rt.i(2), 1), rt.binary("*", rt.binary("/", rt.binary("+", i, rt.i(2), 1), n, 1), n, 1), 1)
            angle1 = rt.binary("+", rt.binary("/", rt.binary("*", i, rt.f(6.28318530718), 1), n, 1), rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), 1)
            angle2 = rt.binary("+", rt.binary("/", rt.binary("*", j, rt.f(6.28318530718), 1), n, 1), rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1), 1)
            a = rt.binary("*", radius, rt.construct(2, rt.component_wise("cos", angle1, width=1), rt.component_wise("sin", angle1, width=1)), 2)
            b = rt.binary("*", radius, rt.construct(2, rt.component_wise("cos", angle2, width=1), rt.component_wise("sin", angle2, width=1)), 2)
            dL = lineSegmentSDF__vec2_vec2_vec2(p, a, b)
            vis = rt.f(1.0)
            if rt.binary("==", _u_animation, rt.i(5)):
                vis = unfoldVis__float(rt.binary("/", i, n, 1))
            m = rt.component_wise("max", m, rt.binary("*", outlineEdge__float_float(dL, lineWidth), vis, 1), width=1)
        return m
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        st = rt.binary("*", rt.binary("-", st, rt.f(0.5), 2), rt.f(2.0), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1))
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1), rt.f(180.0), 1)
        st = rotate2D__vec2_float(st, rad)
        if rt.binary("==", _u_animation, rt.i(1)):
            st = rotate2D__vec2_float(st, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), rt.component_wise("floor", _u_speed, width=1), 1))
        scaleFactor = rt.binary("-", rt.f(21.0), _u_scale, 1)
        if rt.binary("==", _u_animation, rt.i(2)):
            scaleFactor = rt.binary("*", scaleFactor, rt.binary("+", rt.f(1.0), rt.binary("*", _u_pulseDepth, rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), rt.component_wise("floor", _u_speed, width=1), 1), width=1), 1), 1), 1)
        p = rt.binary("*", st, scaleFactor, 2)
        m = rt.f(0.0)
        if rt.binary("==", _u_geometry, rt.i(0)):
            m = flowerMask__vec2_int_float(p, _u_rings, rt.f(0.45))
        else:
            if rt.binary("==", _u_geometry, rt.i(4)):
                m = flowerMask__vec2_int_float(p, rt.i(1), rt.f(0.23))
            else:
                if rt.binary("==", _u_geometry, rt.i(1)):
                    m = fruitMask__vec2_bool(p, False)
                else:
                    if rt.binary("==", _u_geometry, rt.i(3)):
                        m = fruitMask__vec2_bool(p, True)
                    else:
                        if rt.binary("==", _u_geometry, rt.i(5)):
                            m = vesicaMask__vec2(p)
                        else:
                            if rt.binary("==", _u_geometry, rt.i(6)):
                                m = borromeanMask__vec2(p)
                            else:
                                if rt.binary("==", _u_geometry, rt.i(8)):
                                    m = triquetraMask__vec2(p)
                                else:
                                    if rt.binary("==", _u_geometry, rt.i(7)):
                                        m = starPolygonMask__vec2_int(p, _u_starPoints)
        m = rt.component_wise("clamp", m, rt.f(0.0), rt.f(1.0), width=1)
        color = rt.component_wise("mix", _u_bgColor, _u_fgColor, m, width=3)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
