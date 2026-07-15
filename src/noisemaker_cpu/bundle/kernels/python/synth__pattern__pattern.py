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
    _u_patternType = U["patternType"]
    _u_scale = U["scale"]
    _u_thickness = U["thickness"]
    _u_smoothness = U["smoothness"]
    _u_rotation = U["rotation"]
    _u_skew = U["skew"]
    _u_animation = U["animation"]
    _u_speed = U["speed"]
    _u_time = U["time"]
    _u_fgColor = U["fgColor"]
    _u_bgColor = U["bgColor"]
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), c, 1, "float"), 1, "float"))
    def stripes__vec2_float(p, t):
        p = rt.copy(p)
        stripe = rt.component_wise("fract", rt.swizzle(p, "x"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), stripe, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), stripe, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def checkerboard__vec2_float(p, sm):
        p = rt.copy(p)
        f = rt.component_wise("fract", p, width=2)
        d = rt.component_wise("min", rt.component_wise("min", rt.swizzle(f, "x"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), width=1), rt.component_wise("min", rt.swizzle(f, "y"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "y"), 1, "float"), width=1), width=1)
        cell = rt.component_wise("floor", p, width=2)
        check = rt.component_wise("mod", rt.binary("+", rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), 1, "float"), rt.f(2.0), width=1)
        edge = rt.component_wise("smoothstep", rt.f(0.0), rt.binary("*", sm, rt.f(0.5), 1, "float"), d, width=1)
        return rt.component_wise("mix", rt.binary("-", rt.f(1.0), check, 1, "float"), check, edge, width=1)
    def grid__vec2_float(p, t):
        p = rt.copy(p)
        f = rt.component_wise("fract", p, width=2)
        lineX = rt.component_wise("smoothstep", rt.binary("-", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.component_wise("abs", rt.binary("-", rt.swizzle(f, "x"), rt.f(0.5), 1, "float"), width=1), width=1)
        lineY = rt.component_wise("smoothstep", rt.binary("-", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.component_wise("abs", rt.binary("-", rt.swizzle(f, "y"), rt.f(0.5), 1, "float"), width=1), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("min", lineX, lineY, width=1), 1, "float")
    def dots__vec2_float(p, t):
        p = rt.copy(p)
        f = rt.binary("-", rt.component_wise("fract", p, width=2), rt.f(0.5), 2, "float")
        d = rt.length(f)
        radius = rt.binary("*", t, rt.f(0.5), 1, "float")
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", radius, _u_smoothness, 1, "float"), rt.binary("+", radius, _u_smoothness, 1, "float"), d, width=1), 1, "float")
    def hexDist__vec2(p):
        p = rt.copy(p)
        p = rt.component_wise("abs", p, width=2)
        return rt.component_wise("max", rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.f(0.5), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.binary("/", rt.f(1.7320508075688772), rt.f(2.0), 1, "float"), 1, "float"), 1, "float"), rt.swizzle(p, "x"), width=1)
    def hexagons__vec2_float(p, t):
        p = rt.copy(p)
        s = rt.construct(2, rt.f(1.0), rt.f(1.7320508075688772))
        h = rt.binary("*", s, rt.f(0.5), 2, "float")
        a = rt.binary("-", rt.component_wise("mod", p, s, width=2), h, 2, "float")
        b = rt.binary("-", rt.component_wise("mod", rt.binary("+", p, h, 2, "float"), s, width=2), h, 2, "float")
        g = (a if rt.binary("<", rt.length(a), rt.length(b)) else b)
        d = hexDist__vec2(g)
        edge = rt.binary("*", rt.f(0.5), t, 1, "float")
        return rt.component_wise("smoothstep", rt.binary("+", edge, _u_smoothness, 1, "float"), rt.binary("-", edge, _u_smoothness, 1, "float"), d, width=1)
    def concentricRings__vec2_float_float(p, t, timeOffset):
        p = rt.copy(p)
        d = rt.component_wise("fract", rt.binary("+", rt.length(p), timeOffset, 1, "float"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def radialLines__vec2_float_float(p, t, timeOffset):
        p = rt.copy(p)
        lineCount = rt.component_wise("floor", _u_scale, width=1)
        angle = rt.binary("+", rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1), rt.binary("*", timeOffset, rt.f(6.28318530718), 1, "float"), 1, "float")
        d = rt.component_wise("fract", rt.binary("*", rt.binary("/", angle, rt.f(6.28318530718), 1, "float"), lineCount, 1, "float"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def triangularGrid__vec2_float(p, t):
        p = rt.copy(p)
        skewed = rt.construct(2, rt.binary("-", rt.swizzle(p, "x"), rt.binary("/", rt.swizzle(p, "y"), rt.f(1.7320508075688772), 1, "float"), 1, "float"), rt.binary("/", rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float"), rt.f(1.7320508075688772), 1, "float"))
        cell = rt.component_wise("floor", skewed, width=2)
        f = rt.component_wise("fract", skewed, width=2)
        d = rt.f(0.0)
        if rt.binary("<", rt.binary("+", rt.swizzle(f, "x"), rt.swizzle(f, "y"), 1, "float"), rt.f(1.0)):
            d = rt.component_wise("min", rt.component_wise("min", rt.swizzle(f, "x"), rt.swizzle(f, "y"), width=1), rt.binary("-", rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), rt.swizzle(f, "y"), 1, "float"), width=1)
        else:
            d = rt.component_wise("min", rt.component_wise("min", rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "y"), 1, "float"), width=1), rt.binary("-", rt.binary("+", rt.swizzle(f, "x"), rt.swizzle(f, "y"), 1, "float"), rt.f(1.0), 1, "float"), width=1)
        edge = rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.f(0.4), 1, "float")
        return rt.component_wise("smoothstep", rt.binary("-", edge, _u_smoothness, 1, "float"), rt.binary("+", edge, _u_smoothness, 1, "float"), d, width=1)
    def spiralPattern__vec2_float_float(p, t, timeOffset):
        p = rt.copy(p)
        dist = rt.length(p)
        angle = rt.binary("+", rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1), rt.binary("*", timeOffset, rt.f(6.28318530718), 1, "float"), 1, "float")
        d = rt.component_wise("fract", rt.binary("+", rt.binary("/", angle, rt.f(6.28318530718), 1, "float"), dist, 1, "float"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def heartSDF__vec2(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", rt.component_wise("abs", rt.swizzle(p, "x"), width=1))
        if rt.binary(">", rt.binary("+", rt.swizzle(p, "y"), rt.swizzle(p, "x"), 1, "float"), rt.f(1.0)):
            return rt.binary("-", rt.component_wise("sqrt", rt.dot(rt.binary("-", p, rt.construct(2, rt.f(0.25), rt.f(0.75)), 2, "float"), rt.binary("-", p, rt.construct(2, rt.f(0.25), rt.f(0.75)), 2, "float")), width=1), rt.binary("/", rt.component_wise("sqrt", rt.f(2.0), width=1), rt.f(4.0), 1, "float"), 1, "float")
        return rt.binary("*", rt.component_wise("sqrt", rt.component_wise("min", rt.dot(rt.binary("-", p, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), rt.binary("-", p, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), rt.dot(rt.binary("-", p, rt.binary("*", rt.f(0.5), rt.component_wise("max", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.f(0.0), width=1), 1, "float"), 2, "float"), rt.binary("-", p, rt.binary("*", rt.f(0.5), rt.component_wise("max", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.f(0.0), width=1), 1, "float"), 2, "float")), width=1), width=1), rt.component_wise("sign", rt.binary("-", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), width=1), 1, "float")
    def hearts__vec2_float(p, t):
        p = rt.copy(p)
        cell = rt.binary("-", rt.component_wise("fract", p, width=2), rt.f(0.5), 2, "float")
        cell = rt.assign_swizzle(cell, "y", rt.binary("+", rt.swizzle(cell, "y"), rt.f(0.25), 1, "float"))
        d = heartSDF__vec2(rt.binary("*", cell, rt.f(2.4), 2, "float"))
        radius = rt.binary("-", rt.f(0.15), rt.binary("*", t, rt.f(0.15), 1, "float"), 1, "float")
        sm = rt.component_wise("min", _u_smoothness, rt.binary("+", radius, rt.f(0.15), 1, "float"), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", rt.unary("-", radius), sm, 1, "float"), rt.binary("+", rt.unary("-", radius), sm, 1, "float"), d, width=1), 1, "float")
    def waves__vec2_float(p, t):
        p = rt.copy(p)
        y = rt.binary("-", rt.component_wise("fract", rt.swizzle(p, "y"), width=1), rt.f(0.5), 1, "float")
        y = rt.binary("-", y, rt.binary("*", rt.component_wise("cos", rt.binary("*", rt.swizzle(p, "x"), rt.f(6.28318530718), 1, "float"), width=1), rt.f(0.15), 1, "float"), 1, "float")
        dist = rt.component_wise("abs", y, width=1)
        halfW = rt.binary("*", t, rt.f(0.2), 1, "float")
        sm = rt.component_wise("min", _u_smoothness, rt.binary("+", halfW, rt.f(0.01), 1, "float"), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", halfW, sm, 1, "float"), rt.binary("+", halfW, sm, 1, "float"), dist, width=1), 1, "float")
    def zigzag__vec2_float(p, t):
        p = rt.copy(p)
        f = rt.component_wise("fract", p, width=2)
        lineY = rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), rt.component_wise("abs", rt.binary("-", rt.swizzle(f, "x"), rt.f(0.5), 1, "float"), width=1), 1, "float"), 1, "float")
        dist = rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.swizzle(f, "y"), rt.binary("*", lineY, rt.f(0.5), 1, "float"), 1, "float"), rt.f(0.25), 1, "float"), width=1)
        halfW = rt.binary("*", t, rt.f(0.12), 1, "float")
        sm = rt.component_wise("min", _u_smoothness, rt.component_wise("max", rt.binary("-", rt.f(0.24), halfW, 1, "float"), rt.f(0.005), width=1), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", halfW, sm, 1, "float"), rt.binary("+", halfW, sm, 1, "float"), dist, width=1), 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        st = rt.binary("*", rt.binary("-", st, rt.f(0.5), 2, "float"), rt.f(2.0), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        st = rotate2D__vec2_float(st, rad)
        centered = (bool((bool(rt.binary("==", _u_patternType, rt.i(1))) or bool(rt.binary("==", _u_patternType, rt.i(5))))) or bool(rt.binary("==", _u_patternType, rt.i(6))))
        if (bool((not (centered))) and bool(rt.binary("==", _u_animation, rt.i(2)))):
            st = rotate2D__vec2_float(st, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", rt.swizzle(st, "y"), _u_skew, 1, "float"), 1, "float"))
        p = rt.binary("*", st, rt.binary("-", rt.f(21.0), _u_scale, 1, "float"), 2, "float")
        if (bool((not (centered))) and bool(rt.binary("==", _u_animation, rt.i(1)))):
            panPeriod = (rt.f(2.0) if rt.binary("==", _u_patternType, rt.i(0)) else rt.f(1.0))
            p = rt.assign_swizzle(p, "x", rt.binary("+", rt.swizzle(p, "x"), rt.binary("*", rt.binary("*", _u_time, rt.unary("-", rt.component_wise("floor", _u_speed, width=1)), 1, "float"), panPeriod, 1, "float"), 1, "float"))
        m = rt.f(0.0)
        if rt.binary("==", _u_patternType, rt.i(0)):
            m = checkerboard__vec2_float(p, _u_smoothness)
        else:
            if rt.binary("==", _u_patternType, rt.i(1)):
                m = concentricRings__vec2_float_float(p, _u_thickness, rt.binary("*", rt.unary("-", _u_time), rt.component_wise("floor", _u_speed, width=1), 1, "float"))
            else:
                if rt.binary("==", _u_patternType, rt.i(2)):
                    m = dots__vec2_float(p, _u_thickness)
                else:
                    if rt.binary("==", _u_patternType, rt.i(3)):
                        m = grid__vec2_float(p, _u_thickness)
                    else:
                        if rt.binary("==", _u_patternType, rt.i(4)):
                            m = hexagons__vec2_float(p, _u_thickness)
                        else:
                            if rt.binary("==", _u_patternType, rt.i(5)):
                                m = radialLines__vec2_float_float(p, _u_thickness, rt.binary("*", _u_time, rt.component_wise("floor", _u_speed, width=1), 1, "float"))
                            else:
                                if rt.binary("==", _u_patternType, rt.i(6)):
                                    m = spiralPattern__vec2_float_float(p, _u_thickness, rt.binary("*", rt.unary("-", _u_time), rt.component_wise("floor", _u_speed, width=1), 1, "float"))
                                else:
                                    if rt.binary("==", _u_patternType, rt.i(7)):
                                        m = stripes__vec2_float(p, _u_thickness)
                                    else:
                                        if rt.binary("==", _u_patternType, rt.i(8)):
                                            m = triangularGrid__vec2_float(p, _u_thickness)
                                        else:
                                            if rt.binary("==", _u_patternType, rt.i(9)):
                                                m = hearts__vec2_float(p, _u_thickness)
                                            else:
                                                if rt.binary("==", _u_patternType, rt.i(10)):
                                                    m = waves__vec2_float(p, _u_thickness)
                                                else:
                                                    if rt.binary("==", _u_patternType, rt.i(11)):
                                                        m = zigzag__vec2_float(p, _u_thickness)
        color = rt.component_wise("mix", _u_bgColor, _u_fgColor, m, width=3)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
