def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_speed = U.get("speed", 0)
    _u_time = U.get("time", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530718)
    def mod289__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod289__vec2(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 2, "float"), width=2), rt.f(289.0), 2, "float"), 2, "float")
    def permute__vec3(x):
        x = rt.copy(x, "float")
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3, "float"), rt.f(1.0), 3, "float"), x, 3, "float"))
    def simplex2d__vec2(v):
        v = rt.copy(v, "float")
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yy")), 2, "float"), width=2)
        x0 = rt.binary("+", rt.binary("-", v, i, 2, "float"), rt.dot(i, rt.swizzle(C, "xx")), 2, "float")
        i1 = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4, "float")
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2, "float"))
        i = mod289__vec2(i)
        p = permute__vec3(rt.binary("+", rt.binary("+", permute__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3, "float")), rt.swizzle(i, "x"), 3, "float"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3, "float"))
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(3, rt.dot(x0, x0), rt.dot(rt.swizzle(x12, "xy"), rt.swizzle(x12, "xy")), rt.dot(rt.swizzle(x12, "zw"), rt.swizzle(x12, "zw"))), 3, "float"), rt.f(0.0), width=3)
        m = rt.binary("*", m, m, 3, "float")
        m = rt.binary("*", m, m, 3, "float")
        x = rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", p, rt.swizzle(C, "www"), 3, "float"), width=3), 3, "float"), rt.f(1.0), 3, "float")
        h = rt.binary("-", rt.component_wise("abs", x, width=3), rt.f(0.5), 3, "float")
        ox = rt.component_wise("floor", rt.binary("+", x, rt.f(0.5), 3, "float"), width=3)
        a0 = rt.binary("-", x, ox, 3, "float")
        m = rt.binary("*", m, rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), rt.binary("+", rt.binary("*", a0, a0, 3, "float"), rt.binary("*", h, h, 3, "float"), 3, "float"), 3, "float"), 3, "float"), 3, "float")
        _g = rt.construct(3, 0.0)
        _g = rt.assign_swizzle(_g, "x", rt.binary("+", rt.binary("*", rt.swizzle(a0, "x"), rt.swizzle(x0, "x"), 1, "float"), rt.binary("*", rt.swizzle(h, "x"), rt.swizzle(x0, "y"), 1, "float"), 1, "float"))
        _g = rt.assign_swizzle(_g, "yz", rt.binary("+", rt.binary("*", rt.swizzle(a0, "yz"), rt.swizzle(x12, "xz"), 2, "float"), rt.binary("*", rt.swizzle(h, "yz"), rt.swizzle(x12, "yw"), 2, "float"), 2, "float"))
        return rt.binary("*", rt.f(130.0), rt.dot(m, _g), 1, "float")
    def cloudNoise__vec2_float_int_float_float(uv, baseFreq, octaves, animPhase, animSpeed):
        uv = rt.copy(uv, "float")
        accum = rt.f(0.0)
        totalAmp = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(8))):
                break
            if rt.binary(">=", i, octaves):
                break
            freq = rt.binary("*", baseFreq, rt.component_wise("pow", rt.f(2.0), rt.construct(1, i), width=1), 1, "float")
            amp = rt.binary("/", rt.f(1.0), rt.component_wise("pow", rt.f(2.0), rt.construct(1, i), width=1), 1, "float")
            octavePhase = rt.binary("*", rt.construct(1, i), rt.f(2.13), 1, "float")
            octaveRadius = rt.binary("*", rt.binary("+", rt.f(0.25), rt.binary("*", rt.construct(1, i), rt.f(0.08), 1, "float"), 1, "float"), animSpeed, 1, "float")
            timeOffset = rt.binary("*", rt.binary("-", rt.construct(2, rt.component_wise("cos", rt.binary("+", animPhase, octavePhase, 1, "float"), width=1), rt.component_wise("sin", rt.binary("+", animPhase, octavePhase, 1, "float"), width=1)), rt.construct(2, rt.component_wise("cos", octavePhase, width=1), rt.component_wise("sin", octavePhase, width=1)), 2, "float"), octaveRadius, 2, "float")
            n = simplex2d__vec2(rt.binary("+", rt.binary("+", rt.binary("*", uv, freq, 2, "float"), rt.construct(2, rt.binary("*", rt.construct(1, i), rt.f(37.0), 1, "float"), rt.binary("*", rt.construct(1, i), rt.f(53.0), 1, "float")), 2, "float"), timeOffset, 2, "float"))
            n = rt.binary("+", rt.binary("*", n, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
            accum = rt.binary("+", accum, rt.binary("*", n, amp, 1, "float"), 1, "float")
            totalAmp = rt.binary("+", totalAmp, amp, 1, "float")
        return rt.binary("/", accum, totalAmp, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), resolution, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        seedOffset = rt.construct(2, rt.binary("*", _u_seed, rt.f(17.31), 1, "float"), rt.binary("*", _u_seed, rt.f(23.71), 1, "float"))
        animPhase = rt.binary("*", rt.binary("*", _u_time, g.TAU, 1, "float"), rt.construct(1, _u_speed), 1, "float")
        animSpeed = rt.construct(1, _u_speed)
        cloudUV = rt.binary("+", rt.binary("/", rt.binary("*", globalUV, rt.construct(2, aspect, rt.f(1.0)), 2, "float"), _u_scale, 2, "float"), seedOffset, 2, "float")
        cloud = cloudNoise__vec2_float_int_float_float(cloudUV, rt.f(1.0), rt.i(7), animPhase, animSpeed)
        cloudMask = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.65), cloud, width=1)
        cloudDepth = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.85), cloud, width=1)
        cloudBrightness = rt.component_wise("mix", rt.f(0.75), rt.f(1.0), cloudDepth, width=1)
        shadowDist = rt.binary("*", rt.component_wise("min", rt.swizzle(resolution, "x"), rt.swizzle(resolution, "y"), width=1), rt.f(0.008), 1, "float")
        shadowOffset = rt.binary("/", rt.construct(2, rt.unary("-", shadowDist), shadowDist), resolution, 2, "float")
        shadowUV = rt.binary("+", rt.binary("/", rt.binary("*", rt.binary("+", globalUV, shadowOffset, 2, "float"), rt.construct(2, aspect, rt.f(1.0)), 2, "float"), _u_scale, 2, "float"), seedOffset, 2, "float")
        shadowCloud = cloudNoise__vec2_float_int_float_float(shadowUV, rt.f(1.0), rt.i(7), animPhase, animSpeed)
        shadowMask = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.65), shadowCloud, width=1)
        shadow = rt.binary("*", rt.component_wise("max", rt.binary("-", shadowMask, cloudMask, 1, "float"), rt.f(0.0), width=1), rt.f(0.5), 1, "float")
        result = rt.binary("*", rt.swizzle(inputColor, "rgb"), rt.binary("-", rt.f(1.0), shadow, 1, "float"), 3, "float")
        result = rt.component_wise("mix", result, rt.construct(3, cloudBrightness), cloudMask, width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
