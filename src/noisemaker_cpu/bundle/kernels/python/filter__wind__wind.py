def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_METHOD = U.get("METHOD", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_direction = U.get("direction", 0)
    _u_strength = U.get("strength", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.MAX_STEPS = rt.i(128)
    g.STEP_PX = rt.f(1.0)
    g.MAX_REACH = rt.f(128.0)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        amount = rt.component_wise("clamp", rt.binary("/", _u_strength, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", amount, rt.f(0.0)):
            g.fragColor = src
            return
        reach = rt.binary("*", g.MAX_REACH, amount, 1, "float")
        marchDir = (rt.unary("-", rt.f(1.0)) if rt.binary("==", _u_direction, rt.i(0)) else rt.f(1.0))
        staggerPhase = rt.f(0.0)
        if rt.binary("==", _u_METHOD, rt.i(2)):
            staggerPhase = rt.binary("*", rt.binary("+", rt.f(0.5), rt.binary("*", rt.f(0.5), rt.component_wise("sin", rt.binary("*", rt.swizzle(globalCoord, "y"), rt.f(0.22), 1, "float"), width=1), 1, "float"), 1, "float"), rt.component_wise("min", rt.f(12.0), rt.binary("*", reach, rt.f(0.18), 1, "float"), width=1), 1, "float")
        accumColor = rt.construct(3, rt.f(0.0))
        accumWeight = rt.f(0.0)
        baseLum = lum__vec3(rt.swizzle(src, "rgb"))
        edge = rt.binary("/", _u_threshold, rt.f(100.0), 1, "float")
        i = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", i, g.MAX_STEPS)):
                break
            distancePx = rt.binary("*", rt.construct(1, i), g.STEP_PX, 1, "float")
            if rt.binary(">", distancePx, reach):
                break
            sampleDistance = rt.binary("+", distancePx, staggerPhase, 1, "float")
            sampleUV = rt.component_wise("clamp", rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.binary("*", marchDir, sampleDistance, 1, "float"), rt.f(0.0)), 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
            candidate = rt.swizzle(rt.texture(_u_inputTex, sampleUV), "rgb")
            contrast = rt.binary("-", rt.binary("-", lum__vec3(candidate), baseLum, 1, "float"), edge, 1, "float")
            activation = rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.08), contrast, width=1)
            alongRun = rt.binary("/", distancePx, rt.component_wise("max", reach, rt.f(1.0), width=1), 1, "float")
            decayRate = rt.f(0.0)
            if rt.binary("==", _u_METHOD, rt.i(1)):
                decayRate = rt.f(0.8)
            else:
                if rt.binary("==", _u_METHOD, rt.i(2)):
                    decayRate = rt.f(2.0)
                else:
                    decayRate = rt.f(3.4)
            taperStart = rt.f(0.0)
            if rt.binary("==", _u_METHOD, rt.i(1)):
                taperStart = rt.f(0.82)
            else:
                taperStart = rt.f(0.72)
            endTaper = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", taperStart, rt.f(1.0), alongRun, width=1), 1, "float")
            weight = rt.binary("*", rt.binary("*", activation, rt.component_wise("exp", rt.binary("*", rt.unary("-", decayRate), alongRun, 1, "float"), width=1), 1, "float"), endTaper, 1, "float")
            accumColor = rt.binary("+", accumColor, rt.binary("*", candidate, weight, 3, "float"), 3, "float")
            accumWeight = rt.binary("+", accumWeight, weight, 1, "float")
        integrated = rt.binary("/", accumColor, rt.component_wise("max", accumWeight, rt.f(1e-05), width=1), 3, "float")
        densityRate = rt.f(0.0)
        if rt.binary("==", _u_METHOD, rt.i(1)):
            densityRate = rt.f(0.12)
        else:
            densityRate = rt.f(0.16)
        density = rt.binary("-", rt.f(1.0), rt.component_wise("exp", rt.binary("*", rt.unary("-", accumWeight), densityRate, 1, "float"), width=1), 1, "float")
        methodGain = rt.f(0.0)
        if rt.binary("==", _u_METHOD, rt.i(1)):
            methodGain = rt.f(1.0)
        else:
            methodGain = rt.f(0.88)
        blendAmount = rt.component_wise("clamp", rt.binary("*", rt.binary("*", density, amount, 1, "float"), methodGain, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        streak = rt.component_wise("mix", rt.swizzle(src, "rgb"), integrated, blendAmount, width=3)
        g.fragColor = rt.construct(4, rt.component_wise("max", rt.swizzle(src, "rgb"), streak, width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
