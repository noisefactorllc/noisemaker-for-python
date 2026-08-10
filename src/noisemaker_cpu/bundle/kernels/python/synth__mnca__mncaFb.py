def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_deltaTime = U.get("deltaTime", rt.f(0.0))
    _u_bufTex = T["bufTex"]
    _u_seedTex = T["seedTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_weight = U.get("weight", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resetState = U.get("resetState", False)
    _u_n1v1 = U.get("n1v1", rt.f(0.0))
    _u_n1v2 = U.get("n1v2", rt.f(0.0))
    _u_n1v3 = U.get("n1v3", rt.f(0.0))
    _u_n1v4 = U.get("n1v4", rt.f(0.0))
    _u_n2v1 = U.get("n2v1", rt.f(0.0))
    _u_n2v2 = U.get("n2v2", rt.f(0.0))
    _u_n1r1 = U.get("n1r1", rt.f(0.0))
    _u_n1r2 = U.get("n1r2", rt.f(0.0))
    _u_n1r3 = U.get("n1r3", rt.f(0.0))
    _u_n1r4 = U.get("n1r4", rt.f(0.0))
    _u_n2r1 = U.get("n2r1", rt.f(0.0))
    _u_n2r2 = U.get("n2r2", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def lum__vec3(color):
        color = rt.copy(color, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", rt.dot(rt.swizzle(st, "xy"), rt.construct(2, rt.f(12.9898), rt.f(78.233))), width=1), rt.f(43758.5453123), 1, "float"), width=1)
    def neighborsAvgCircle__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv, "float")
        texelSize = rt.copy(texelSize, "float")
        avg = rt.f(0.0)
        total = rt.f(0.0)
        y = rt.unary("-", rt.i(3))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(3))):
                break
            x = rt.unary("-", rt.i(3))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(3))):
                    break
                if (bool(rt.binary("==", x, rt.i(0))) and bool(rt.binary("==", y, rt.i(0)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", x, width=1), rt.i(3))) and bool(rt.binary(">", rt.component_wise("abs", y, width=1), rt.i(1)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", y, width=1), rt.i(3))) and bool(rt.binary(">", rt.component_wise("abs", x, width=1), rt.i(1)))):
                    continue
                offset = rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), texelSize, 2, "float")
                n = rt.swizzle(rt.texture(_u_bufTex, rt.binary("+", uv, offset, 2, "float")), "r")
                total = rt.binary("+", total, n, 1, "float")
        avg = rt.binary("/", total, rt.f(36.0), 1, "float")
        return avg
    def neighborsAvgRing__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv, "float")
        texelSize = rt.copy(texelSize, "float")
        avg = rt.f(0.0)
        total = rt.f(0.0)
        y = rt.unary("-", rt.i(7))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", y, rt.i(7))):
                break
            x = rt.unary("-", rt.i(7))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<=", x, rt.i(7))):
                    break
                if (bool(rt.binary("<=", rt.component_wise("abs", x, width=1), rt.i(3))) and bool(rt.binary("<=", rt.component_wise("abs", y, width=1), rt.i(3)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", x, width=1), rt.i(4))) and bool(rt.binary("<=", rt.component_wise("abs", y, width=1), rt.i(2)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", y, width=1), rt.i(4))) and bool(rt.binary("<=", rt.component_wise("abs", x, width=1), rt.i(2)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", x, width=1), rt.i(7))) and bool(rt.binary(">", rt.component_wise("abs", y, width=1), rt.i(2)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", x, width=1), rt.i(6))) and bool(rt.binary(">", rt.component_wise("abs", y, width=1), rt.i(4)))):
                    continue
                if (bool(rt.binary("==", rt.component_wise("abs", x, width=1), rt.i(5))) and bool(rt.binary(">", rt.component_wise("abs", y, width=1), rt.i(5)))):
                    continue
                if (bool(rt.binary(">", rt.component_wise("abs", x, width=1), rt.i(2))) and bool(rt.binary(">", rt.component_wise("abs", y, width=1), rt.i(6)))):
                    continue
                offset = rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), texelSize, 2, "float")
                n = rt.swizzle(rt.texture(_u_bufTex, rt.binary("+", uv, offset, 2, "float")), "r")
                total = rt.binary("+", total, n, 1, "float")
        avg = rt.binary("/", total, rt.f(108.0), 1, "float")
        return avg
    def getState__float_float_float(avg1, avg2, state):
        if (bool(rt.binary(">=", avg1, rt.binary("*", _u_n1v1, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg1, rt.binary("+", rt.binary("*", _u_n1v1, rt.f(0.01), 1, "float"), rt.binary("*", _u_n1r1, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(1.0)
        if (bool(rt.binary(">=", avg1, rt.binary("*", _u_n1v2, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg1, rt.binary("+", rt.binary("*", _u_n1v2, rt.f(0.01), 1, "float"), rt.binary("*", _u_n1r2, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(0.0)
        if (bool(rt.binary(">=", avg1, rt.binary("*", _u_n1v3, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg1, rt.binary("+", rt.binary("*", _u_n1v3, rt.f(0.01), 1, "float"), rt.binary("*", _u_n1r3, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(0.0)
        if (bool(rt.binary(">=", avg2, rt.binary("*", _u_n2v1, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg2, rt.binary("+", rt.binary("*", _u_n2v1, rt.f(0.01), 1, "float"), rt.binary("*", _u_n2r1, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(0.0)
        if (bool(rt.binary(">=", avg2, rt.binary("*", _u_n2v2, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg2, rt.binary("+", rt.binary("*", _u_n2v2, rt.f(0.01), 1, "float"), rt.binary("*", _u_n2r2, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(1.0)
        if (bool(rt.binary(">=", avg1, rt.binary("*", _u_n1v4, rt.f(0.01), 1, "float"))) and bool(rt.binary("<=", avg1, rt.binary("+", rt.binary("*", _u_n1v4, rt.f(0.01), 1, "float"), rt.binary("*", _u_n1r4, rt.f(0.01), 1, "float"), 1, "float")))):
            state = rt.f(0.0)
        return state
    def main__void():
        texSize = rt.construct(2, rt.texture_size(_u_bufTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), texSize, 2, "float")
        state = rt.swizzle(rt.texture(_u_bufTex, uv), "r")
        bufState = rt.texture(_u_bufTex, uv)
        bufferIsEmpty = (bool((bool((bool(rt.binary("==", rt.swizzle(bufState, "r"), rt.f(0.0))) and bool(rt.binary("==", rt.swizzle(bufState, "g"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(bufState, "b"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(bufState, "a"), rt.f(0.0))))
        r = rt.f(0.0)
        alive = rt.f(0.0)
        if (bool(_u_resetState) or bool(bufferIsEmpty)):
            r = random__vec2(rt.binary("+", uv, rt.construct(2, rt.construct(1, _u_seed)), 2, "float"))
            alive = rt.component_wise("step", rt.f(0.5), r, width=1)
            g.fragColor[:] = rt.construct(4, alive, alive, alive, rt.f(1.0))
            return
        prevFrame = rt.swizzle(rt.texture(_u_seedTex, uv), "rgb")
        prevLum = lum__vec3(prevFrame)
        newState = state
        n1 = neighborsAvgCircle__vec2_vec2(uv, texelSize)
        n2 = neighborsAvgRing__vec2_vec2(uv, texelSize)
        newState = getState__float_float_float(n1, n2, state)
        if rt.binary(">", _u_weight, rt.f(0.0)):
            newState = rt.component_wise("mix", newState, prevLum, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
        animSpeed = map__float_float_float_float_float(_u_speed, rt.f(1.0), rt.f(100.0), rt.f(0.1), rt.f(100.0))
        currentState = rt.construct(4, state, state, state, rt.f(1.0))
        nextState = rt.construct(4, newState, newState, newState, rt.f(1.0))
        g.fragColor[:] = rt.component_wise("mix", currentState, nextState, rt.component_wise("min", rt.f(1.0), rt.binary("*", _u_deltaTime, animSpeed, 1, "float"), width=1), width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
