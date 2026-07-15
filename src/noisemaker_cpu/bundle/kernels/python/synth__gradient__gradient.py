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
    _u_gradientType = U["gradientType"]
    _u_rotation = U["rotation"]
    _u_repeat = U["repeat"]
    _u_colorCount = U["colorCount"]
    _u_color1 = U["color1"]
    _u_color2 = U["color2"]
    _u_color3 = U["color3"]
    _u_color4 = U["color4"]
    _u_seed = U["seed"]
    _u_time = U["time"]
    _u_speed = U["speed"]
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def rotate2D__vec2_float(st, angle):
        st = rt.copy(st)
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), aspectRatio, 1))
        st = rt.binary("-", st, rt.construct(2, rt.binary("*", aspectRatio, rt.f(0.5), 1), rt.f(0.5)), 2)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        st = rt.binary("*", rt.construct(4, c, rt.unary("-", s), s, c), st, 4)
        st = rt.binary("+", st, rt.construct(2, rt.binary("*", aspectRatio, rt.f(0.5), 1), rt.f(0.5)), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), aspectRatio, 1))
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
        segment = rt.binary("*", t, _u_colorCount, 1)
        idx = rt.construct(1, rt.component_wise("floor", segment, width=1))
        localT = rt.component_wise("fract", segment, width=1)
        next = rt.binary("+", idx, rt.i(1), 1)
        if rt.binary(">=", next, _u_colorCount):
            next = rt.i(0)
        return rt.component_wise("mix", getColor__int(idx), getColor__int(next), localT, width=3)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525)), 3), rt.construct(1, rt.i(1013904223)), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16)), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1)))
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def hash2D__vec2(p):
        p = rt.copy(p)
        return rt.swizzle(prng__vec3(rt.construct(3, p, _u_seed)), "x")
    def valueNoise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2), 2), 2)
        a = hash2D__vec2(i)
        b = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2))
        c = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2))
        d = hash2D__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2))
        return rt.component_wise("mix", rt.component_wise("mix", a, b, rt.swizzle(u, "x"), width=1), rt.component_wise("mix", c, d, rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbmNoise__vec2(p):
        p = rt.copy(p)
        sum = rt.f(0.0)
        amp = rt.f(0.5)
        freq = rt.f(1.0)
        maxVal = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            sum = rt.binary("+", sum, rt.binary("*", valueNoise__vec2(rt.binary("*", p, freq, 2)), amp, 1), 1)
            maxVal = rt.binary("+", maxVal, amp, 1)
            freq = rt.binary("*", freq, rt.f(2.0), 1)
            amp = rt.binary("*", amp, rt.f(0.5), 1)
        return rt.binary("/", sum, maxVal, 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        aspectRatio = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        angle = rt.binary("/", rt.binary("*", rt.unary("-", _u_rotation), rt.f(3.14159265359), 1), rt.f(180.0), 1)
        rotatedSt = rotate2D__vec2_float(st, angle)
        centered = rt.binary("-", st, rt.f(0.5), 2)
        centered = rt.assign_swizzle(centered, "x", rt.binary("*", rt.swizzle(centered, "x"), aspectRatio, 1))
        rotatedCentered = centered
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        rotatedCentered = rt.binary("*", rt.construct(4, c, rt.unary("-", s), s, c), centered, 4)
        color = rt.construct(3, 0.0)
        t = rt.f(0.0)
        timeOffset = rt.binary("*", _u_time, _u_speed, 1)
        if rt.binary("==", _u_gradientType, rt.i(0)):
            a = rt.component_wise("atan", rt.swizzle(rotatedCentered, "y"), rt.swizzle(rotatedCentered, "x"), width=1)
            t = rt.binary("/", rt.binary("+", a, rt.f(3.14159265359), 1), rt.f(6.28318530718), 1)
            t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
            color = blendColors__float(t)
        else:
            if rt.binary("==", _u_gradientType, rt.i(1)):
                t = rt.binary("+", rt.component_wise("abs", rt.swizzle(rotatedCentered, "x"), width=1), rt.component_wise("abs", rt.swizzle(rotatedCentered, "y"), width=1), 1)
                t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
                color = blendColors__float(t)
            else:
                if rt.binary("==", _u_gradientType, rt.i(2)):
                    cornerSt = rotate2D__vec2_float(st, angle)
                    cTL = _u_color1
                    cTR = (_u_color2 if rt.binary(">=", _u_colorCount, rt.i(3)) else _u_color1)
                    cBL = (_u_color3 if rt.binary(">=", _u_colorCount, rt.i(3)) else _u_color2)
                    cBR = (_u_color4 if rt.binary(">=", _u_colorCount, rt.i(4)) else cBL)
                    top = rt.component_wise("mix", cTL, cTR, rt.swizzle(cornerSt, "x"), width=3)
                    bottom = rt.component_wise("mix", cBL, cBR, rt.swizzle(cornerSt, "x"), width=3)
                    color = rt.component_wise("mix", bottom, top, rt.swizzle(cornerSt, "y"), width=3)
                else:
                    if rt.binary("==", _u_gradientType, rt.i(3)):
                        t = rt.swizzle(rotatedSt, "y")
                        t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
                        color = blendColors__float(t)
                    else:
                        if rt.binary("==", _u_gradientType, rt.i(4)):
                            noiseSt = rt.binary("*", rotatedCentered, rt.f(4.0), 2)
                            t = fbmNoise__vec2(noiseSt)
                            t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
                            color = blendColors__float(t)
                        else:
                            if rt.binary("==", _u_gradientType, rt.i(5)):
                                rotatedPoint = rt.binary("*", rt.construct(4, c, rt.unary("-", s), s, c), centered, 4)
                                dist = rt.binary("*", rt.length(rotatedPoint), rt.f(2.0), 1)
                                t = dist
                                t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
                                color = blendColors__float(t)
                            else:
                                if rt.binary("==", _u_gradientType, rt.i(6)):
                                    a = rt.component_wise("atan", rt.swizzle(rotatedCentered, "y"), rt.swizzle(rotatedCentered, "x"), width=1)
                                    dist = rt.length(centered)
                                    t = rt.component_wise("fract", rt.binary("+", rt.binary("/", a, rt.f(6.28318530718), 1), rt.binary("*", dist, rt.f(2.0), 1), 1), width=1)
                                    t = rt.component_wise("fract", rt.binary("+", rt.binary("*", t, _u_repeat, 1), timeOffset, 1), width=1)
                                    color = blendColors__float(t)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
