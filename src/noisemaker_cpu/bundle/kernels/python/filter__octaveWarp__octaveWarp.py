def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_frequency = U["frequency"]
    _u_octaves = U["octaves"]
    _u_displacement = U["displacement"]
    _u_speed = U["speed"]
    _u_wrap = U["wrap"]
    _u_seed = U["seed"]
    _u_antialias = U["antialias"]
    g.TAU = rt.f(6.28318530717959)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def hash21__vec2(p):
        p = rt.copy(p)
        v = cpu_uvec3__float_float_float(rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, _u_seed))
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__vec3(v), "x")), rt.f(4294967295.0), 1)
    def noise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        f = rt.binary("*", rt.binary("*", f, f, 2), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2), 2), 2)
        a = hash21__vec2(i)
        b = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2))
        c = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2))
        d = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2))
        return rt.component_wise("mix", rt.component_wise("mix", a, b, rt.swizzle(f, "x"), width=1), rt.component_wise("mix", c, d, rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1)
    def simplexNoise__vec2_float_float_float(p, t, phase, radius):
        p = rt.copy(p)
        angle = rt.binary("+", rt.binary("*", t, g.TAU, 1), phase, 1)
        cx = rt.binary("*", rt.component_wise("cos", angle, width=1), radius, 1)
        cy = rt.binary("*", rt.component_wise("sin", angle, width=1), radius, 1)
        n = noise__vec2(rt.binary("+", p, rt.construct(2, cx, cy), 2))
        n = rt.binary("+", n, rt.binary("*", noise__vec2(rt.binary("+", rt.binary("*", p, rt.f(2.0), 2), rt.binary("*", rt.construct(2, rt.unary("-", cy), cx), rt.f(0.75), 2), 2)), rt.f(0.5), 1), 1)
        n = rt.binary("+", n, rt.binary("*", noise__vec2(rt.binary("+", rt.binary("*", p, rt.f(4.0), 2), rt.binary("*", rt.construct(2, cx, rt.unary("-", cy)), rt.f(0.5), 2), 2)), rt.f(0.25), 1), 1)
        return rt.binary("/", n, rt.f(1.75), 1)
    def wrapFloat__float_float_int(value, limit, mode):
        if rt.binary("<=", limit, rt.f(0.0)):
            return rt.f(0.0)
        norm = rt.binary("/", value, limit, 1)
        if rt.binary("==", mode, rt.i(0)):
            norm = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", norm, rt.f(1.0), 1), rt.f(2.0), width=1), rt.f(1.0), 1), width=1)
        else:
            if rt.binary("==", mode, rt.i(1)):
                norm = rt.component_wise("mod", norm, rt.f(1.0), width=1)
                if rt.binary("<", norm, rt.f(0.0)):
                    norm = rt.binary("+", norm, rt.f(1.0), 1)
            else:
                norm = rt.component_wise("clamp", norm, rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("*", norm, limit, 1)
    def main__void():
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        dims = fullRes
        width = rt.swizzle(dims, "x")
        height = rt.swizzle(dims, "y")
        baseFreq = rt.binary("-", rt.f(11.0), _u_frequency, 1)
        aspect = rt.binary("/", width, height, 1)
        freq = rt.construct(2, baseFreq)
        if rt.binary(">", aspect, rt.f(1.0)):
            freq = rt.assign_swizzle(freq, "y", rt.binary("*", rt.swizzle(freq, "y"), aspect, 1))
        else:
            freq = rt.assign_swizzle(freq, "x", rt.binary("/", rt.swizzle(freq, "x"), aspect, 1))
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        sampleCoord = rt.binary("*", uv, dims, 2)
        numOctaves = rt.component_wise("max", rt.construct(1, _u_octaves), rt.i(1), width=1)
        displaceBase = _u_displacement
        octave = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                octave = rt.binary("+", octave, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", octave, rt.i(10))):
                break
            if rt.binary(">", octave, numOctaves):
                break
            multiplier = rt.component_wise("pow", rt.f(2.0), octave, width=1)
            freqScaled = rt.binary("*", rt.binary("*", freq, rt.f(0.5), 2), multiplier, 2)
            if rt.binary("||", rt.binary(">=", rt.swizzle(freqScaled, "x"), width), rt.binary(">=", rt.swizzle(freqScaled, "y"), height)):
                break
            phase = rt.binary("*", octave, rt.f(2.399), 1)
            radius = rt.binary("/", rt.f(0.5), rt.component_wise("sqrt", multiplier, width=1), 1)
            noiseCoord = rt.binary("*", rt.binary("/", sampleCoord, dims, 2), freqScaled, 2)
            refX = simplexNoise__vec2_float_float_float(rt.binary("+", noiseCoord, rt.construct(2, rt.f(17.0), rt.f(29.0)), 2), rt.binary("*", _u_time, _u_speed, 1), phase, radius)
            refY = simplexNoise__vec2_float_float_float(rt.binary("+", noiseCoord, rt.construct(2, rt.f(23.0), rt.f(31.0)), 2), rt.binary("*", _u_time, _u_speed, 1), phase, radius)
            refX = rt.binary("-", rt.binary("*", refX, rt.f(2.0), 1), rt.f(1.0), 1)
            refY = rt.binary("-", rt.binary("*", refY, rt.f(2.0), 1), rt.f(1.0), 1)
            displaceScale = rt.binary("/", displaceBase, multiplier, 1)
            offset = rt.construct(2, rt.binary("*", rt.binary("*", refX, displaceScale, 1), width, 1), rt.binary("*", rt.binary("*", refY, displaceScale, 1), height, 1))
            sampleCoord = rt.binary("+", sampleCoord, offset, 2)
            sampleCoord = rt.construct(2, wrapFloat__float_float_int(rt.swizzle(sampleCoord, "x"), width, rt.construct(1, _u_wrap)), wrapFloat__float_float_int(rt.swizzle(sampleCoord, "y"), height, rt.construct(1, _u_wrap)))
        finalUV = rt.binary("/", rt.construct(2, wrapFloat__float_float_int(rt.swizzle(sampleCoord, "x"), width, rt.construct(1, _u_wrap)), wrapFloat__float_float_int(rt.swizzle(sampleCoord, "y"), height, rt.construct(1, _u_wrap))), dims, 2)
        if _u_antialias:
            dx = rt.component_wise("dFdx", finalUV, width=2)
            dy = rt.component_wise("dFdy", finalUV, width=2)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.f(0.125), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.f(0.375), 2), 2), rt.binary("*", dy, rt.f(0.125), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2), 2), rt.binary("*", dy, rt.f(0.375), 2), 2)), 4)
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4)
        else:
            g.fragColor = rt.texture(_u_inputTex, finalUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
