def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_seed = U["seed"]
    _u_scale = U["scale"]
    _u_speed = U["speed"]
    _u_time = U["time"]
    g.TAU = rt.f(6.28318530718)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def mod289__vec3(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 3), width=3), rt.f(289.0), 3), 3)
    def mod289__vec2(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 2), width=2), rt.f(289.0), 2), 2)
    def permute__vec3(x):
        x = rt.copy(x)
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3), rt.f(1.0), 3), x, 3))
    def simplex2d__vec2(v):
        v = rt.copy(v)
        C = rt.construct(4, rt.f(0.211324865405187), rt.f(0.366025403784439), rt.unary("-", rt.f(0.577350269189626)), rt.f(0.024390243902439))
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yy")), 2), width=2)
        x0 = rt.binary("+", rt.binary("-", v, i, 2), rt.dot(i, rt.swizzle(C, "xx")), 2)
        i1 = (rt.construct(2, rt.f(1.0), rt.f(0.0)) if rt.binary(">", rt.swizzle(x0, "x"), rt.swizzle(x0, "y")) else rt.construct(2, rt.f(0.0), rt.f(1.0)))
        x12 = rt.binary("+", rt.swizzle(x0, "xyxy"), rt.swizzle(C, "xxzz"), 4)
        x12 = rt.assign_swizzle(x12, "xy", rt.binary("-", rt.swizzle(x12, "xy"), i1, 2))
        i = mod289__vec2(i)
        p = permute__vec3(rt.binary("+", rt.binary("+", permute__vec3(rt.binary("+", rt.swizzle(i, "y"), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "y"), rt.f(1.0)), 3)), rt.swizzle(i, "x"), 3), rt.construct(3, rt.f(0.0), rt.swizzle(i1, "x"), rt.f(1.0)), 3))
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(3, rt.dot(x0, x0), rt.dot(rt.swizzle(x12, "xy"), rt.swizzle(x12, "xy")), rt.dot(rt.swizzle(x12, "zw"), rt.swizzle(x12, "zw"))), 3), rt.f(0.0), width=3)
        m = rt.binary("*", m, m, 3)
        m = rt.binary("*", m, m, 3)
        x = rt.binary("-", rt.binary("*", rt.f(2.0), rt.component_wise("fract", rt.binary("*", p, rt.swizzle(C, "www"), 3), width=3), 3), rt.f(1.0), 3)
        h = rt.binary("-", rt.component_wise("abs", x, width=3), rt.f(0.5), 3)
        ox = rt.component_wise("floor", rt.binary("+", x, rt.f(0.5), 3), width=3)
        a0 = rt.binary("-", x, ox, 3)
        m = rt.binary("*", m, rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), rt.binary("+", rt.binary("*", a0, a0, 3), rt.binary("*", h, h, 3), 3), 3), 3), 3)
        g = rt.construct(3, 0.0)
        g = rt.assign_swizzle(g, "x", rt.binary("+", rt.binary("*", rt.swizzle(a0, "x"), rt.swizzle(x0, "x"), 1), rt.binary("*", rt.swizzle(h, "x"), rt.swizzle(x0, "y"), 1), 1))
        g = rt.assign_swizzle(g, "yz", rt.binary("+", rt.binary("*", rt.swizzle(a0, "yz"), rt.swizzle(x12, "xz"), 2), rt.binary("*", rt.swizzle(h, "yz"), rt.swizzle(x12, "yw"), 2), 2))
        return rt.binary("*", rt.f(130.0), rt.dot(m, g), 1)
    def cloudNoise__vec2_float_int_float_float(uv, baseFreq, octaves, animPhase, animSpeed):
        uv = rt.copy(uv)
        accum = rt.f(0.0)
        totalAmp = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(8))):
                break
            if rt.binary(">=", i, octaves):
                break
            freq = rt.binary("*", baseFreq, rt.component_wise("pow", rt.f(2.0), i, width=1), 1)
            amp = rt.binary("/", rt.f(1.0), rt.component_wise("pow", rt.f(2.0), i, width=1), 1)
            octavePhase = rt.binary("*", i, rt.f(2.13), 1)
            octaveRadius = rt.binary("*", rt.binary("+", rt.f(0.25), rt.binary("*", i, rt.f(0.08), 1), 1), animSpeed, 1)
            timeOffset = rt.binary("*", rt.binary("-", rt.construct(2, rt.component_wise("cos", rt.binary("+", animPhase, octavePhase, 1), width=1), rt.component_wise("sin", rt.binary("+", animPhase, octavePhase, 1), width=1)), rt.construct(2, rt.component_wise("cos", octavePhase, width=1), rt.component_wise("sin", octavePhase, width=1)), 2), octaveRadius, 2)
            n = simplex2d__vec2(rt.binary("+", rt.binary("+", rt.binary("*", uv, freq, 2), rt.construct(2, rt.binary("*", i, rt.f(37.0), 1), rt.binary("*", i, rt.f(53.0), 1)), 2), timeOffset, 2))
            n = rt.binary("+", rt.binary("*", n, rt.f(0.5), 1), rt.f(0.5), 1)
            accum = rt.binary("+", accum, rt.binary("*", n, amp, 1), 1)
            totalAmp = rt.binary("+", totalAmp, amp, 1)
        return rt.binary("/", accum, totalAmp, 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), resolution, 2)
        inputColor = rt.texture(_u_inputTex, uv)
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        seedOffset = rt.construct(2, rt.binary("*", _u_seed, rt.f(17.31), 1), rt.binary("*", _u_seed, rt.f(23.71), 1))
        animPhase = rt.binary("*", rt.binary("*", _u_time, g.TAU, 1), _u_speed, 1)
        animSpeed = _u_speed
        cloudUV = rt.binary("+", rt.binary("/", rt.binary("*", globalUV, rt.construct(2, aspect, rt.f(1.0)), 2), _u_scale, 2), seedOffset, 2)
        cloud = cloudNoise__vec2_float_int_float_float(cloudUV, rt.f(1.0), rt.i(7), animPhase, animSpeed)
        cloudMask = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.65), cloud, width=1)
        cloudDepth = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.85), cloud, width=1)
        cloudBrightness = rt.component_wise("mix", rt.f(0.75), rt.f(1.0), cloudDepth, width=1)
        shadowDist = rt.binary("*", rt.component_wise("min", rt.swizzle(resolution, "x"), rt.swizzle(resolution, "y"), width=1), rt.f(0.008), 1)
        shadowOffset = rt.binary("/", rt.construct(2, rt.unary("-", shadowDist), shadowDist), resolution, 2)
        shadowUV = rt.binary("+", rt.binary("/", rt.binary("*", rt.binary("+", globalUV, shadowOffset, 2), rt.construct(2, aspect, rt.f(1.0)), 2), _u_scale, 2), seedOffset, 2)
        shadowCloud = cloudNoise__vec2_float_int_float_float(shadowUV, rt.f(1.0), rt.i(7), animPhase, animSpeed)
        shadowMask = rt.component_wise("smoothstep", rt.f(0.45), rt.f(0.65), shadowCloud, width=1)
        shadow = rt.binary("*", rt.component_wise("max", rt.binary("-", shadowMask, cloudMask, 1), rt.f(0.0), width=1), rt.f(0.5), 1)
        result = rt.binary("*", rt.swizzle(inputColor, "rgb"), rt.binary("-", rt.f(1.0), shadow, 1), 3)
        result = rt.component_wise("mix", result, rt.construct(3, cloudBrightness), cloudMask, width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
