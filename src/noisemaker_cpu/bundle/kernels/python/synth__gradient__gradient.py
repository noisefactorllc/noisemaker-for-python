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
    _u_gradientType = U.get("gradientType", 0)
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_repeat = U.get("repeat", 0)
    _u_colorCount = U.get("colorCount", 0)
    _u_color1 = U.get("color1", rt.construct(3, 0.0))
    _u_color2 = U.get("color2", rt.construct(3, 0.0))
    _u_color3 = U.get("color3", rt.construct(3, 0.0))
    _u_color4 = U.get("color4", rt.construct(3, 0.0))
    _u_seed = U.get("seed", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def rotate2D__vec2_float(st, angle):
        st = rt.copy(st, "float")
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspectRatio, 1, "float"))
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("*", aspectRatio, rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        st[:] = rt.matrix_mult(rt.construct(4, c, rt.unary("-", s), s, c), st, 2)
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("*", aspectRatio, rt.f(0.5), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspectRatio, 1, "float"))
        return st
    def getColor__int(idx):
        if rt.binary("==", idx, rt.i(0)):
            return _u_color1
        if rt.binary("==", idx, rt.i(1)):
            return _u_color2
        if rt.binary("==", idx, rt.i(2)):
            return _u_color3
        return _u_color4
    def blendColors__float(t):
        t = rt.component_wise("fract", t, width=1)
        segment = rt.binary("*", t, rt.construct(1, _u_colorCount), 1, "float")
        idx = rt.construct(1, rt.component_wise("floor", segment, width=1), base="int")
        localT = rt.component_wise("fract", segment, width=1)
        next = rt.binary("+", idx, rt.i(1), 1, "int")
        if rt.binary(">=", next, _u_colorCount):
            next = rt.i(0)
        return rt.component_wise("mix", getColor__int(idx), getColor__int(next), localT, width=3)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def hash2D__vec2(p):
        p = rt.copy(p, "float")
        return rt.swizzle(prng__vec3(rt.construct(3, p, rt.construct(1, _u_seed))), "x")
    def valueNoise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        a = hash2D__vec2(i)
        b = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"))
        c = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"))
        d = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"))
        return rt.component_wise("mix", rt.component_wise("mix", a, b, rt.swizzle(u, "x"), width=1), rt.component_wise("mix", c, d, rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbmNoise__vec2(p):
        p = rt.copy(p, "float")
        sum = rt.f(0.0)
        amp = rt.f(0.5)
        freq = rt.f(1.0)
        maxVal = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            sum = rt.binary("+", sum, rt.binary("*", valueNoise__vec2(rt.binary("*", p, freq, 2, "float")), amp, 1, "float"), 1, "float")
            maxVal = rt.binary("+", maxVal, amp, 1, "float")
            freq = rt.binary("*", freq, rt.f(2.0), 1, "float")
            amp = rt.binary("*", amp, rt.f(0.5), 1, "float")
        return rt.binary("/", sum, maxVal, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        angle = rt.binary("/", rt.binary("*", rt.unary("-", _u_rotation), rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        rotatedSt = rotate2D__vec2_float(st, angle)
        centered = rt.binary("-", st, rt.f(0.5), 2, "float")
        centered = rt.assign_swizzle(centered, "x", rt.binary("*", rt.swizzle(centered, "x"), aspectRatio, 1, "float"))
        rotatedCentered = centered
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        rotatedCentered[:] = rt.matrix_mult(rt.construct(4, c, rt.unary("-", s), s, c), centered, 2)
        color = rt.construct(3, 0.0)
        t = rt.f(0.0)
        timeOffset = rt.binary("*", _u_time, _u_speed, 1, "float")
        a = rt.f(0.0)
        cornerSt = rt.construct(2, 0.0)
        cTL = rt.construct(3, 0.0)
        cTR = rt.construct(3, 0.0)
        cBL = rt.construct(3, 0.0)
        cBR = rt.construct(3, 0.0)
        top = rt.construct(3, 0.0)
        bottom = rt.construct(3, 0.0)
        noiseSt = rt.construct(2, 0.0)
        rotatedPoint = rt.construct(2, 0.0)
        dist = rt.f(0.0)
        if rt.binary("==", _u_gradientType, rt.i(0)):
            a = rt.component_wise("atan", rt.swizzle(rotatedCentered, "y"), rt.swizzle(rotatedCentered, "x"), width=1)
            t = rt.binary("/", rt.binary("+", a, rt.f(3.14159265359), 1, "float"), rt.f(6.28318530718), 1, "float")
            t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
            color[:] = blendColors__float(t)
        else:
            if rt.binary("==", _u_gradientType, rt.i(1)):
                t = rt.binary("+", rt.component_wise("abs", rt.swizzle(rotatedCentered, "x"), width=1), rt.component_wise("abs", rt.swizzle(rotatedCentered, "y"), width=1), 1, "float")
                t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
                color[:] = blendColors__float(t)
            else:
                if rt.binary("==", _u_gradientType, rt.i(2)):
                    cornerSt = rotate2D__vec2_float(st, angle)
                    cTL = _u_color1
                    cTR = (_u_color2 if rt.binary(">=", _u_colorCount, rt.i(3)) else _u_color1)
                    cBL = (_u_color3 if rt.binary(">=", _u_colorCount, rt.i(3)) else _u_color2)
                    cBR = (_u_color4 if rt.binary(">=", _u_colorCount, rt.i(4)) else cBL)
                    top = rt.component_wise("mix", cTL, cTR, rt.swizzle(cornerSt, "x"), width=3)
                    bottom = rt.component_wise("mix", cBL, cBR, rt.swizzle(cornerSt, "x"), width=3)
                    color[:] = rt.component_wise("mix", bottom, top, rt.swizzle(cornerSt, "y"), width=3)
                else:
                    if rt.binary("==", _u_gradientType, rt.i(3)):
                        t = rt.swizzle(rotatedSt, "y")
                        t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
                        color[:] = blendColors__float(t)
                    else:
                        if rt.binary("==", _u_gradientType, rt.i(4)):
                            noiseSt = rt.binary("*", rotatedCentered, rt.f(4.0), 2, "float")
                            t = fbmNoise__vec2(noiseSt)
                            t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
                            color[:] = blendColors__float(t)
                        else:
                            if rt.binary("==", _u_gradientType, rt.i(5)):
                                rotatedPoint = rt.matrix_mult(rt.construct(4, c, rt.unary("-", s), s, c), centered, 2)
                                dist = rt.binary("*", rt.length(rotatedPoint), rt.f(2.0), 1, "float")
                                t = dist
                                t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
                                color[:] = blendColors__float(t)
                            else:
                                if rt.binary("==", _u_gradientType, rt.i(6)):
                                    a = rt.component_wise("atan", rt.swizzle(rotatedCentered, "y"), rt.swizzle(rotatedCentered, "x"), width=1)
                                    dist = rt.length(centered)
                                    t = rt.component_wise("fract", rt.binary("+", rt.binary("/", a, rt.f(6.28318530718), 1, "float"), rt.binary("*", dist, rt.f(2.0), 1, "float"), 1, "float"), width=1)
                                    t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, rt.construct(1, _u_repeat), 1, "float"), timeOffset, 1, "float"), width=1)
                                    color[:] = blendColors__float(t)
        g.fragColor[:] = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
