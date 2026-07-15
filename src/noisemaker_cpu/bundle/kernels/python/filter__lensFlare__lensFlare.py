def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_LENS_TYPE = U["LENS_TYPE"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_brightness = U["brightness"]
    _u_centerX = U["centerX"]
    _u_centerY = U["centerY"]
    _u_tint = U["tint"]
    def flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, t, aspectRatio):
        flarePos = rt.copy(flarePos)
        mirrorPos = rt.copy(mirrorPos)
        a = rt.component_wise("mix", flarePos, mirrorPos, t, width=2)
        a = rt.assign_swizzle(a, "x", rt.binary("*", rt.swizzle(a, "x"), aspectRatio, 1))
        return a
    def coreGlow__float(d):
        return rt.binary("+", rt.binary("*", rt.component_wise("exp", rt.binary("*", rt.binary("*", rt.unary("-", d), d, 1, "float"), rt.f(900.0), 1, "float"), width=1), rt.f(1.2), 1, "float"), rt.binary("*", rt.component_wise("exp", rt.binary("*", rt.unary("-", d), rt.f(8.0), 1, "float"), width=1), rt.f(0.4), 1, "float"), 1, "float")
    def anamorphicStreak__vec2(delta):
        delta = rt.copy(delta)
        return rt.component_wise("exp", rt.unary("-", rt.binary("+", rt.binary("*", rt.binary("*", rt.swizzle(delta, "y"), rt.swizzle(delta, "y"), 1, "float"), rt.f(4000.0), 1, "float"), rt.binary("*", rt.binary("*", rt.swizzle(delta, "x"), rt.swizzle(delta, "x"), 1, "float"), rt.f(18.0), 1, "float"), 1, "float")), width=1)
    def sixPointStar__vec2_float(delta, d):
        delta = rt.copy(delta)
        phi = rt.component_wise("atan", rt.swizzle(delta, "y"), rt.swizzle(delta, "x"), width=1)
        return rt.binary("*", rt.binary("*", rt.component_wise("pow", rt.component_wise("max", rt.f(0.0), rt.component_wise("cos", rt.binary("*", rt.f(6.0), phi, 1, "float"), width=1), width=1), rt.f(40.0), width=1), rt.component_wise("exp", rt.binary("*", rt.unary("-", d), rt.f(5.0), 1, "float"), width=1), 1, "float"), rt.f(0.5), 1, "float")
    def haloRainbow__float(dc):
        return rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), rt.component_wise("cos", rt.binary("*", rt.f(6.28318530717958647692), rt.binary("+", rt.binary("*", dc, rt.f(10.0), 1, "float"), rt.construct(3, rt.f(0.0), rt.f(0.3333333), rt.f(0.6666667)), 3, "float"), 3, "float"), width=3), 3, "float"), 3, "float")
    def haloBand__float(dc):
        return rt.binary("*", rt.component_wise("exp", rt.binary("*", rt.unary("-", rt.component_wise("abs", rt.binary("-", dc, rt.f(0.28), 1, "float"), width=1)), rt.f(60.0), 1, "float"), width=1), rt.f(0.25), 1, "float")
    def circleGhost__float_float(dist, size):
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("*", size, rt.f(0.6), 1, "float"), size, dist, width=1), 1, "float")
    def softCircleGhost__float_float(dist, size):
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("*", size, rt.f(0.3), 1, "float"), size, dist, width=1), 1, "float")
    def ringGhost__float_float(dist, size):
        outer = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("*", size, rt.f(0.6), 1, "float"), size, dist, width=1), 1, "float")
        inner = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("*", size, rt.f(0.3), 1, "float"), rt.binary("*", size, rt.f(0.6), 1, "float"), dist, width=1), 1, "float")
        return rt.binary("-", outer, inner, 1, "float")
    def hexDist__vec2(p):
        p = rt.copy(p)
        a0 = rt.construct(2, rt.f(1.0), rt.f(0.0))
        a1 = rt.construct(2, rt.f(0.5), rt.f(0.8660254038))
        a2 = rt.construct(2, rt.unary("-", rt.f(0.5)), rt.f(0.8660254038))
        d0 = rt.component_wise("abs", rt.dot(p, a0), width=1)
        d1 = rt.component_wise("abs", rt.dot(p, a1), width=1)
        d2 = rt.component_wise("abs", rt.dot(p, a2), width=1)
        return rt.component_wise("max", d0, rt.component_wise("max", d1, d2, width=1), width=1)
    def hexGhost__vec2_float(delta, size):
        delta = rt.copy(delta)
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("*", size, rt.f(0.6), 1, "float"), size, hexDist__vec2(delta), width=1), 1, "float")
    def main__void():
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        localUV = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, localUV)
        flarePos = rt.construct(2, _u_centerX, _u_centerY)
        mirrorPos = rt.binary("-", rt.construct(2, rt.f(1.0)), flarePos, 2, "float")
        p = uv
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspectRatio, 1))
        aFlare = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.0), aspectRatio)
        delta0 = rt.binary("-", p, aFlare, 2, "float")
        d0 = rt.length(delta0)
        flare = rt.construct(3, rt.f(0.0))
        flare = rt.binary("+", flare, rt.construct(3, coreGlow__float(d0)), 3)
        streakVal = anamorphicStreak__vec2(delta0)
        if rt.binary("==", _u_LENS_TYPE, rt.i(3)):
            streakVal = rt.binary("*", streakVal, rt.f(2.0), 1)
        flare = rt.binary("+", flare, rt.construct(3, streakVal), 3)
        if rt.binary("||", rt.binary("==", _u_LENS_TYPE, rt.i(0)), rt.binary("==", _u_LENS_TYPE, rt.i(3))):
            flare = rt.binary("+", flare, rt.construct(3, sixPointStar__vec2_float(delta0, d0)), 3)
        aMirror = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(1.0), aspectRatio)
        dc = rt.length(rt.binary("-", p, aMirror, 2, "float"))
        flare = rt.binary("+", flare, rt.binary("*", haloRainbow__float(dc), haloBand__float(dc), 3, "float"), 3)
        g = rt.construct(2, rt.f(0.0))
        if rt.binary("||", rt.binary("==", _u_LENS_TYPE, rt.i(0)), rt.binary("==", _u_LENS_TYPE, rt.i(3))):
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.25), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(1.00), rt.f(0.85), rt.f(0.60)), circleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.06)), 3, "float"), rt.f(0.35), 3, "float"), 3)
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.4), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.40), rt.f(0.90), rt.f(0.85)), circleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.10)), 3, "float"), rt.f(0.25), 3, "float"), 3)
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.6), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.65), rt.f(0.40), rt.f(0.95)), circleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.045)), 3, "float"), rt.f(0.45), 3, "float"), 3)
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.85), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.45), rt.f(0.90), rt.f(0.50)), circleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.14)), 3, "float"), rt.f(0.18), 3, "float"), 3)
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(1.2), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(1.00), rt.f(0.55), rt.f(0.20)), circleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.08)), 3, "float"), rt.f(0.30), 3, "float"), 3)
            g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(1.55), aspectRatio)
            flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.40), rt.f(0.55), rt.f(1.00)), ringGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.20)), 3, "float"), rt.f(0.12), 3, "float"), 3)
        else:
            if rt.binary("==", _u_LENS_TYPE, rt.i(1)):
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.3), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(1.00), rt.f(0.80), rt.f(0.55)), hexGhost__vec2_float(rt.binary("-", p, g, 2, "float"), rt.f(0.04)), 3, "float"), rt.f(0.35), 3, "float"), 3)
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.55), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.85), rt.f(0.85), rt.f(0.92)), hexGhost__vec2_float(rt.binary("-", p, g, 2, "float"), rt.f(0.055)), 3, "float"), rt.f(0.30), 3, "float"), 3)
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.8), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.95), rt.f(0.70), rt.f(0.50)), hexGhost__vec2_float(rt.binary("-", p, g, 2, "float"), rt.f(0.065)), 3, "float"), rt.f(0.25), 3, "float"), 3)
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(1.3), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.80), rt.f(0.85), rt.f(0.95)), hexGhost__vec2_float(rt.binary("-", p, g, 2, "float"), rt.f(0.08)), 3, "float"), rt.f(0.20), 3, "float"), 3)
            else:
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.45), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.92), rt.f(0.85), rt.f(0.78)), softCircleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.12)), 3, "float"), rt.f(0.25), 3, "float"), 3)
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(0.9), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.85), rt.f(0.88), rt.f(0.95)), softCircleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.16)), 3, "float"), rt.f(0.20), 3, "float"), 3)
                g = flareAxis__vec2_vec2_float_float(flarePos, mirrorPos, rt.f(1.5), aspectRatio)
                flare = rt.binary("+", flare, rt.binary("*", rt.binary("*", rt.construct(3, rt.f(0.95), rt.f(0.88), rt.f(0.80)), softCircleGhost__float_float(rt.length(rt.binary("-", p, g, 2, "float")), rt.f(0.20)), 3, "float"), rt.f(0.15), 3, "float"), 3)
        outFlare = rt.binary("*", rt.binary("*", flare, _u_tint, 3, "float"), rt.binary("/", _u_brightness, rt.f(100.0), 1, "float"), 3, "float")
        if rt.binary("==", _u_LENS_TYPE, rt.i(3)):
            outFlare = rt.binary("*", outFlare, rt.construct(3, rt.f(0.9), rt.f(0.95), rt.f(1.1)), 3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", rt.binary("+", rt.swizzle(src, "rgb"), outFlare, 3, "float"), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
