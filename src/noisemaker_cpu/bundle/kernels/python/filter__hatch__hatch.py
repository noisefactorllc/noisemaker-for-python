def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_strokeLength = U.get("strokeLength", rt.f(0.0))
    _u_direction = U.get("direction", 0)
    _u_balance = U.get("balance", rt.f(0.0))
    _u_pressure = U.get("pressure", rt.f(0.0))
    _u_inkColor = U.get("inkColor", rt.construct(3, 0.0))
    _u_paperColor = U.get("paperColor", rt.construct(3, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def vnoise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbm__vec2(p):
        p = rt.copy(p, "float")
        v = rt.f(0.0)
        a = rt.f(0.5)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(5))):
                break
            v = rt.binary("+", v, rt.binary("*", a, vnoise__vec2(p), 1, "float"), 1, "float")
            p[:] = rt.binary("*", p, rt.f(2.03), 2, "float")
            a = rt.binary("*", a, rt.f(0.5), 1, "float")
        return v
    def lumGradient__vec2(uv):
        uv = rt.copy(uv, "float")
        px = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        tl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        l = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        bl = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        tr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        r = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), 2, "float")), "rgb"))
        br = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(1.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        t = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), 2, "float")), "rgb"))
        b = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", px, rt.construct(2, rt.f(0.0), rt.unary("-", rt.f(1.0))), 2, "float"), 2, "float")), "rgb"))
        return rt.construct(2, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tr, rt.binary("*", rt.f(2.0), r, 1, "float"), 1, "float"), br, 1, "float"), tl, 1, "float"), rt.binary("*", rt.f(2.0), l, 1, "float"), 1, "float"), bl, 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("+", rt.binary("+", tl, rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), tr, 1, "float"), bl, 1, "float"), rt.binary("*", rt.f(2.0), b, 1, "float"), 1, "float"), br, 1, "float"))
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink, "float")
        paper = rt.copy(paper, "float")
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def rotate2D__vec2_float(v, angleDeg):
        v = rt.copy(v, "float")
        a = rt.component_wise("radians", angleDeg, width=1)
        co = rt.component_wise("cos", a, width=1)
        si = rt.component_wise("sin", a, width=1)
        return rt.matrix_mult(rt.construct(4, co, rt.unary("-", si), si, co), v, 2)
    def dirAngle__int(d):
        if rt.binary("==", d, rt.i(1)):
            return rt.f(0.0)
        if rt.binary("==", d, rt.i(2)):
            return rt.f(135.0)
        if rt.binary("==", d, rt.i(3)):
            return rt.f(90.0)
        return rt.f(45.0)
    def strokeField__vec2_float_float(gc, angleDeg, stretchAmt):
        gc = rt.copy(gc, "float")
        p = rt.binary("*", rotate2D__vec2_float(gc, angleDeg), rt.construct(2, rt.binary("/", rt.f(1.0), stretchAmt, 1, "float"), rt.f(0.9)), 2, "float")
        return vnoise__vec2(p)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        gc = rt.binary("+", rt.component_wise("floor", rt.swizzle(ctx.frag_coord, "xy"), width=2), _u_tileOffset, 2, "float")
        theta = dirAngle__int(_u_direction)
        stretchAmt = rt.component_wise("mix", rt.f(4.0), rt.f(40.0), rt.binary("/", _u_strokeLength, rt.f(100.0), 1, "float"), width=1)
        t = rt.binary("+", lum__vec3(rt.swizzle(src, "rgb")), rt.binary("/", rt.binary("-", _u_balance, rt.f(50.0), 1, "float"), rt.f(100.0), 1, "float"), 1, "float")
        pb = rt.binary("/", rt.binary("-", _u_pressure, rt.f(50.0), 1, "float"), rt.f(100.0), 1, "float")
        s = strokeField__vec2_float_float(gc, theta, stretchAmt)
        outColor = rt.construct(3, 0.0)
        inkMask = rt.f(0.0)
        s2 = rt.f(0.0)
        rough = rt.f(0.0)
        shadow = rt.f(0.0)
        coverage = rt.f(0.0)
        darkness = rt.f(0.0)
        inkC = rt.construct(3, 0.0)
        midGray = rt.construct(3, 0.0)
        sBg = rt.f(0.0)
        aa = rt.f(0.0)
        fgGate = rt.f(0.0)
        fgMask = rt.f(0.0)
        bgGate = rt.f(0.0)
        bgMask = rt.f(0.0)
        toneGate = rt.f(0.0)
        texture2 = rt.f(0.0)
        level = rt.f(0.0)
        s45a = rt.f(0.0)
        s45b = rt.f(0.0)
        band1 = rt.f(0.0)
        band2 = rt.f(0.0)
        band3 = rt.f(0.0)
        darkGain = rt.f(0.0)
        f0 = rt.f(0.0)
        f1 = rt.f(0.0)
        f2 = rt.f(0.0)
        grad = rt.construct(2, 0.0)
        gradMag = rt.f(0.0)
        edgeAngle = rt.f(0.0)
        sEdge = rt.f(0.0)
        edgeBoost = rt.f(0.0)
        sCombined = rt.f(0.0)
        strokeMask = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            inkMask = rt.component_wise("step", s, rt.component_wise("clamp", rt.binary("+", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("*", pb, rt.f(0.3), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1), width=1)
            outColor[:] = tonemap2__float_vec3_vec3(rt.binary("-", rt.f(1.0), inkMask, 1, "float"), _u_inkColor, _u_paperColor)
        else:
            if rt.binary("==", _u_MODE, rt.i(1)):
                s2 = strokeField__vec2_float_float(rt.binary("+", rt.binary("*", gc, rt.f(2.0), 2, "float"), rt.f(91.7), 2, "float"), theta, rt.binary("*", stretchAmt, rt.f(0.5), 1, "float"))
                rough = rt.binary("+", rt.binary("*", s, rt.f(0.6), 1, "float"), rt.binary("*", s2, rt.f(0.4), 1, "float"), 1, "float")
                shadow = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.15), rt.f(0.55), t, width=1), 1, "float")
                coverage = rt.component_wise("clamp", rt.binary("+", shadow, rt.binary("*", pb, rt.f(0.5), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                inkMask = rt.component_wise("step", rt.binary("-", rt.f(1.0), coverage, 1, "float"), rough, width=1)
                darkness = rt.component_wise("mix", rt.f(0.55), rt.f(1.0), rt.binary("/", _u_pressure, rt.f(100.0), 1, "float"), width=1)
                inkC = rt.component_wise("mix", _u_paperColor, _u_inkColor, darkness, width=3)
                outColor[:] = rt.component_wise("mix", _u_paperColor, inkC, inkMask, width=3)
            else:
                if rt.binary("==", _u_MODE, rt.i(2)):
                    midGray = rt.component_wise("mix", _u_inkColor, _u_paperColor, rt.f(0.5), width=3)
                    sBg = strokeField__vec2_float_float(gc, rt.binary("+", theta, rt.f(90.0), 1, "float"), stretchAmt)
                    aa = rt.component_wise("mix", rt.f(0.4), rt.f(0.04), rt.binary("/", _u_pressure, rt.f(100.0), 1, "float"), width=1)
                    fgGate = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", rt.f(0.4), aa, 1, "float"), rt.binary("+", rt.f(0.4), aa, 1, "float"), t, width=1), 1, "float")
                    fgMask = rt.component_wise("step", rt.binary("-", rt.f(1.0), fgGate, 1, "float"), s, width=1)
                    bgGate = rt.component_wise("smoothstep", rt.binary("-", rt.f(0.6), aa, 1, "float"), rt.binary("+", rt.f(0.6), aa, 1, "float"), t, width=1)
                    bgMask = rt.component_wise("step", rt.binary("-", rt.f(1.0), bgGate, 1, "float"), sBg, width=1)
                    outColor[:] = midGray
                    outColor[:] = rt.component_wise("mix", outColor, _u_inkColor, fgMask, width=3)
                    outColor[:] = rt.component_wise("mix", outColor, _u_paperColor, bgMask, width=3)
                else:
                    if rt.binary("==", _u_MODE, rt.i(3)):
                        toneGate = rt.component_wise("smoothstep", rt.f(0.3), rt.f(0.7), t, width=1)
                        texture2 = rt.component_wise("mix", s, fbm__vec2(rt.binary("+", rt.binary("/", gc, rt.binary("*", stretchAmt, rt.f(0.6), 1, "float"), 2, "float"), rt.f(41.0), 2, "float")), rt.f(0.5), width=1)
                        level = rt.component_wise("mix", texture2, toneGate, rt.component_wise("abs", rt.binary("-", rt.binary("*", toneGate, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), width=1), width=1)
                        level = rt.component_wise("clamp", rt.binary("+", level, rt.binary("*", pb, rt.f(0.15), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                        outColor[:] = tonemap2__float_vec3_vec3(level, _u_inkColor, _u_paperColor)
                    else:
                        if rt.binary("==", _u_MODE, rt.i(4)):
                            s45a = strokeField__vec2_float_float(gc, rt.binary("+", theta, rt.f(45.0), 1, "float"), stretchAmt)
                            s45b = strokeField__vec2_float_float(gc, rt.binary("-", theta, rt.f(45.0), 1, "float"), stretchAmt)
                            band1 = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.65), rt.f(0.85), t, width=1), 1, "float")
                            band2 = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.35), rt.f(0.55), t, width=1), 1, "float")
                            band3 = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.05), rt.f(0.25), t, width=1), 1, "float")
                            darkGain = rt.component_wise("mix", rt.f(0.25), rt.f(1.0), rt.binary("/", _u_pressure, rt.f(100.0), 1, "float"), width=1)
                            f0 = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", band1, darkGain, 1, "float"), rt.binary("-", rt.f(1.0), s, 1, "float"), 1, "float"), 1, "float")
                            f1 = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", band2, darkGain, 1, "float"), rt.binary("-", rt.f(1.0), s45a, 1, "float"), 1, "float"), 1, "float")
                            f2 = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", band3, darkGain, 1, "float"), rt.binary("-", rt.f(1.0), s45b, 1, "float"), 1, "float"), 1, "float")
                            outColor[:] = rt.component_wise("clamp", rt.binary("*", rt.binary("*", rt.binary("*", rt.swizzle(src, "rgb"), f0, 3, "float"), f1, 3, "float"), f2, 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
                        else:
                            grad = lumGradient__vec2(uv)
                            gradMag = rt.length(grad)
                            edgeAngle = rt.binary("+", rt.component_wise("degrees", rt.component_wise("atan", rt.swizzle(grad, "y"), rt.swizzle(grad, "x"), width=1), width=1), rt.f(90.0), 1, "float")
                            sEdge = strokeField__vec2_float_float(gc, edgeAngle, stretchAmt)
                            edgeBoost = rt.component_wise("clamp", rt.binary("*", gradMag, rt.f(3.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                            sCombined = rt.component_wise("mix", s, sEdge, edgeBoost, width=1)
                            coverage = rt.component_wise("clamp", rt.binary("+", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("*", pb, rt.f(0.4), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
                            strokeMask = rt.component_wise("step", rt.binary("-", rt.f(1.0), coverage, 1, "float"), sCombined, width=1)
                            outColor[:] = rt.component_wise("mix", _u_paperColor, rt.swizzle(src, "rgb"), strokeMask, width=3)
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", outColor, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
