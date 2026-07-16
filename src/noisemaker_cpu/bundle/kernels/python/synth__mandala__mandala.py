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
    _u_aspect = U.get("aspect", rt.f(0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_thickness = U.get("thickness", rt.f(0.0))
    _u_smoothness = U.get("smoothness", rt.f(0.0))
    _u_symmetry = U.get("symmetry", 0)
    _u_layers = U.get("layers", 0)
    _u_shape = U.get("shape", 0)
    _u_layerSpacing = U.get("layerSpacing", rt.f(0.0))
    _u_twist = U.get("twist", rt.f(0.0))
    _u_shapeGrowth = U.get("shapeGrowth", rt.f(0.0))
    _u_bindu = U.get("bindu", False)
    _u_animation = U.get("animation", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_pulseDepth = U.get("pulseDepth", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_fgColor = U.get("fgColor", rt.construct(3, 0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), c, 1, "float"), 1, "float"))
    def sdEquilateralTriangle__vec2_float(p, r):
        p = rt.copy(p, "float")
        k = rt.f(1.7320508075688772)
        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.component_wise("abs", rt.swizzle(p, "x"), width=1), r, 1, "float"))
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("/", r, k, 1, "float"), 1, "float"))
        if rt.binary(">", rt.binary("+", rt.swizzle(p, "x"), rt.binary("*", k, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.f(0.0)):
            p = rt.binary("/", rt.construct(2, rt.binary("-", rt.swizzle(p, "x"), rt.binary("*", k, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("-", rt.binary("*", rt.unary("-", k), rt.swizzle(p, "x"), 1, "float"), rt.swizzle(p, "y"), 1, "float")), rt.f(2.0), 2, "float")
        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.swizzle(p, "x"), rt.component_wise("clamp", rt.swizzle(p, "x"), rt.binary("*", rt.unary("-", rt.f(2.0)), r, 1, "float"), rt.f(0.0), width=1), 1, "float"))
        return rt.binary("*", rt.unary("-", rt.length(p)), rt.component_wise("sign", rt.swizzle(p, "y"), width=1), 1, "float")
    def fillEdge__float(d):
        return rt.component_wise("smoothstep", _u_smoothness, rt.unary("-", _u_smoothness), d, width=1)
    def mandalaMask__vec2(p):
        p = rt.copy(p, "float")
        r = rt.length(p)
        theta = rt.binary("-", rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1), rt.binary("*", rt.f(3.14159265359), rt.f(0.5), 1, "float"), 1, "float")
        wedge = rt.binary("/", rt.f(6.28318530718), rt.construct(1, _u_symmetry), 1, "float")
        twistRad = rt.binary("/", rt.binary("*", _u_twist, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        baseSize = rt.binary("+", rt.f(0.25), rt.binary("*", _u_thickness, rt.f(0.65), 1, "float"), 1, "float")
        dynTwistRad = twistRad
        if rt.binary("==", _u_animation, rt.i(5)):
            dynTwistRad = rt.binary("*", twistRad, rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"), width=1), 1, "float")
        m = rt.f(0.0)
        dBindu = rt.f(0.0)
        if _u_bindu:
            dBindu = rt.binary("-", rt.length(p), rt.binary("+", rt.f(0.15), rt.binary("*", _u_thickness, rt.f(0.15), 1, "float"), 1, "float"), 1, "float")
            m = rt.component_wise("max", m, fillEdge__float(dBindu), width=1)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(12))):
                break
            if rt.binary(">=", i, _u_layers):
                break
            Rlayer = rt.binary("*", rt.construct(1, rt.binary("+", i, rt.i(1), 1, "int")), _u_layerSpacing, 1, "float")
            layerAnimRot = rt.f(0.0)
            dir = rt.f(0.0)
            if rt.binary("==", _u_animation, rt.i(3)):
                layerAnimRot = rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.binary("+", rt.component_wise("floor", _u_speed, width=1), rt.construct(1, i), 1, "float"), 1, "float")
            else:
                if rt.binary("==", _u_animation, rt.i(4)):
                    dir = (rt.f(1.0) if rt.binary("<", rt.component_wise("mod", rt.construct(1, i), rt.f(2.0), width=1), rt.f(0.5)) else rt.unary("-", rt.f(1.0)))
                    layerAnimRot = rt.binary("*", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"), dir, 1, "float")
            layerTheta = rt.binary("-", rt.binary("-", theta, rt.binary("*", rt.construct(1, i), dynTwistRad, 1, "float"), 1, "float"), layerAnimRot, 1, "float")
            folded = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", layerTheta, rt.binary("*", wedge, rt.f(0.5), 1, "float"), 1, "float"), wedge, width=1), rt.binary("*", wedge, rt.f(0.5), 1, "float"), 1, "float"), width=1)
            radial = rt.binary("-", r, Rlayer, 1, "float")
            tangent = rt.binary("*", folded, Rlayer, 1, "float")
            lt = rt.f(0.0)
            if rt.binary(">", _u_layers, rt.i(1)):
                lt = rt.binary("-", rt.binary("/", rt.construct(1, i), rt.construct(1, rt.binary("-", _u_layers, rt.i(1), 1, "int")), 1, "float"), rt.f(0.5), 1, "float")
            shapeSize = rt.binary("*", baseSize, rt.binary("+", rt.f(1.0), rt.binary("*", _u_shapeGrowth, lt, 1, "float"), 1, "float"), 1, "float")
            if rt.binary("==", _u_animation, rt.i(6)):
                shapeSize = rt.binary("*", shapeSize, rt.binary("+", rt.f(1.0), rt.binary("*", _u_pulseDepth, rt.component_wise("sin", rt.binary("-", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"), rt.binary("*", rt.construct(1, i), rt.f(0.6), 1, "float"), 1, "float"), width=1), 1, "float"), 1, "float"), 1, "float")
            d = rt.f(0.0)
            q = rt.construct(2, 0.0)
            if rt.binary("==", _u_shape, rt.i(0)):
                d = rt.binary("-", rt.length(rt.construct(2, rt.binary("*", radial, rt.f(0.55), 1, "float"), tangent)), shapeSize, 1, "float")
                m = rt.component_wise("max", m, fillEdge__float(d), width=1)
            else:
                if rt.binary("==", _u_shape, rt.i(1)):
                    q = rt.construct(2, tangent, rt.unary("-", radial))
                    d = sdEquilateralTriangle__vec2_float(q, shapeSize)
                    m = rt.component_wise("max", m, fillEdge__float(d), width=1)
                else:
                    d = rt.binary("-", rt.length(rt.construct(2, radial, tangent)), rt.binary("*", shapeSize, rt.f(0.7), 1, "float"), 1, "float")
                    m = rt.component_wise("max", m, fillEdge__float(d), width=1)
        return m
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        st = rt.binary("*", rt.binary("-", st, rt.f(0.5), 2, "float"), rt.f(2.0), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        st = rotate2D__vec2_float(st, rad)
        if rt.binary("==", _u_animation, rt.i(1)):
            st = rotate2D__vec2_float(st, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"))
        scaleFactor = rt.binary("-", rt.f(21.0), _u_scale, 1, "float")
        if rt.binary("==", _u_animation, rt.i(2)):
            scaleFactor = rt.binary("*", scaleFactor, rt.binary("+", rt.f(1.0), rt.binary("*", _u_pulseDepth, rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), rt.component_wise("floor", _u_speed, width=1), 1, "float"), width=1), 1, "float"), 1, "float"), 1, "float")
        p = rt.binary("*", st, scaleFactor, 2, "float")
        m = rt.component_wise("clamp", mandalaMask__vec2(p), rt.f(0.0), rt.f(1.0), width=1)
        color = rt.component_wise("mix", _u_bgColor, _u_fgColor, m, width=3)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
