def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_frequency = U.get("frequency", rt.f(0.0))
    _u_octaves = U.get("octaves", rt.f(0.0))
    _u_displacement = U.get("displacement", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_wrap = U.get("wrap", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    _u_antialias = U.get("antialias", False)
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530717959)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def hash21__vec2(p):
        p = rt.copy(p, "float")
        v = rt.construct(3, rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, _u_seed, base="uint"), base="uint")
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__uvec3(v), "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def noise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        f = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        a = hash21__vec2(i)
        b = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"))
        c = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"))
        d = hash21__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"))
        return rt.component_wise("mix", rt.component_wise("mix", a, b, rt.swizzle(f, "x"), width=1), rt.component_wise("mix", c, d, rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1)
    def simplexNoise__vec2_float_float_float(p, t, phase, radius):
        p = rt.copy(p, "float")
        angle = rt.binary("+", rt.binary("*", t, g.TAU, 1, "float"), phase, 1, "float")
        cx = rt.binary("*", rt.component_wise("cos", angle, width=1), radius, 1, "float")
        cy = rt.binary("*", rt.component_wise("sin", angle, width=1), radius, 1, "float")
        n = noise__vec2(rt.binary("+", p, rt.construct(2, cx, cy), 2, "float"))
        n = rt.binary("+", n, rt.binary("*", noise__vec2(rt.binary("+", rt.binary("*", p, rt.f(2.0), 2, "float"), rt.binary("*", rt.construct(2, rt.unary("-", cy), cx), rt.f(0.75), 2, "float"), 2, "float")), rt.f(0.5), 1, "float"), 1, "float")
        n = rt.binary("+", n, rt.binary("*", noise__vec2(rt.binary("+", rt.binary("*", p, rt.f(4.0), 2, "float"), rt.binary("*", rt.construct(2, cx, rt.unary("-", cy)), rt.f(0.5), 2, "float"), 2, "float")), rt.f(0.25), 1, "float"), 1, "float")
        return rt.binary("/", n, rt.f(1.75), 1, "float")
    def wrapFloat__float_float_int(value, limit, mode):
        if rt.binary("<=", limit, rt.f(0.0)):
            return rt.f(0.0)
        norm = rt.binary("/", value, limit, 1, "float")
        if rt.binary("==", mode, rt.i(0)):
            norm = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", norm, rt.f(1.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1)
        else:
            if rt.binary("==", mode, rt.i(1)):
                norm = rt.component_wise("mod", norm, rt.f(1.0), width=1)
                if rt.binary("<", norm, rt.f(0.0)):
                    norm = rt.binary("+", norm, rt.f(1.0), 1, "float")
            else:
                norm = rt.component_wise("clamp", norm, rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("*", norm, limit, 1, "float")
    def main__void():
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        dims = fullRes
        width = rt.swizzle(dims, "x")
        height = rt.swizzle(dims, "y")
        baseFreq = rt.binary("-", rt.f(11.0), _u_frequency, 1, "float")
        aspect = rt.binary("/", width, height, 1, "float")
        freq = rt.construct(2, baseFreq)
        if rt.binary(">", aspect, rt.f(1.0)):
            freq = rt.assign_swizzle(freq, "y", rt.binary("*", rt.swizzle(freq, "y"), aspect, 1, "float"))
        else:
            freq = rt.assign_swizzle(freq, "x", rt.binary("/", rt.swizzle(freq, "x"), aspect, 1, "float"))
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        sampleCoord = rt.binary("*", uv, dims, 2, "float")
        numOctaves = rt.component_wise("max", rt.construct(1, _u_octaves, base="int"), rt.i(1), width=1)
        displaceBase = _u_displacement
        octave = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                octave = rt.binary("+", octave, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", octave, rt.i(10))):
                break
            if rt.binary(">", octave, numOctaves):
                break
            multiplier = rt.component_wise("pow", rt.f(2.0), rt.construct(1, octave), width=1)
            freqScaled = rt.binary("*", rt.binary("*", freq, rt.f(0.5), 2, "float"), multiplier, 2, "float")
            if (bool(rt.binary(">=", rt.swizzle(freqScaled, "x"), width)) or bool(rt.binary(">=", rt.swizzle(freqScaled, "y"), height))):
                break
            phase = rt.binary("*", rt.construct(1, octave), rt.f(2.399), 1, "float")
            radius = rt.binary("/", rt.f(0.5), rt.component_wise("sqrt", multiplier, width=1), 1, "float")
            noiseCoord = rt.binary("*", rt.binary("/", sampleCoord, dims, 2, "float"), freqScaled, 2, "float")
            refX = simplexNoise__vec2_float_float_float(rt.binary("+", noiseCoord, rt.construct(2, rt.f(17.0), rt.f(29.0)), 2, "float"), rt.binary("*", _u_time, _u_speed, 1, "float"), phase, radius)
            refY = simplexNoise__vec2_float_float_float(rt.binary("+", noiseCoord, rt.construct(2, rt.f(23.0), rt.f(31.0)), 2, "float"), rt.binary("*", _u_time, _u_speed, 1, "float"), phase, radius)
            refX = rt.binary("-", rt.binary("*", refX, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")
            refY = rt.binary("-", rt.binary("*", refY, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")
            displaceScale = rt.binary("/", displaceBase, multiplier, 1, "float")
            offset = rt.construct(2, rt.binary("*", rt.binary("*", refX, displaceScale, 1, "float"), width, 1, "float"), rt.binary("*", rt.binary("*", refY, displaceScale, 1, "float"), height, 1, "float"))
            sampleCoord = rt.binary("+", sampleCoord, offset, 2, "float")
            sampleCoord = rt.construct(2, wrapFloat__float_float_int(rt.swizzle(sampleCoord, "x"), width, rt.construct(1, _u_wrap, base="int")), wrapFloat__float_float_int(rt.swizzle(sampleCoord, "y"), height, rt.construct(1, _u_wrap, base="int")))
        finalUV = rt.binary("/", rt.construct(2, wrapFloat__float_float_int(rt.swizzle(sampleCoord, "x"), width, rt.construct(1, _u_wrap, base="int")), wrapFloat__float_float_int(rt.swizzle(sampleCoord, "y"), height, rt.construct(1, _u_wrap, base="int"))), dims, 2, "float")
        dx = rt.construct(2, 0.0)
        dy = rt.construct(2, 0.0)
        col = rt.construct(4, 0.0)
        if _u_antialias:
            dx = rt.dFdx(finalUV)
            dy = rt.dFdy(finalUV)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", finalUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            g.fragColor = rt.texture(_u_inputTex, finalUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
