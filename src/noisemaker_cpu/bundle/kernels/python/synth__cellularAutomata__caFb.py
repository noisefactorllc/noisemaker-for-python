def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_deltaTime = U.get("deltaTime", rt.f(0.0))
    _u_frame = U.get("frame", 0)
    _u_bufTex = T["bufTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_ruleIndex = U.get("ruleIndex", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_weight = U.get("weight", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resetState = U.get("resetState", False)
    _u_useCustom = U.get("useCustom", False)
    _u_source = U.get("source", 0)
    g.fragColor = rt.construct(4, 0.0)
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", rt.dot(rt.swizzle(st, "xy"), rt.construct(2, rt.f(12.9898), rt.f(78.233))), width=1), rt.f(43758.5453123), 1, "float"), width=1)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def lum__vec3(color):
        color = rt.copy(color, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def shouldBeBorn__int(n):
        should = False
        if (bool((bool(rt.binary("==", _u_ruleIndex, rt.i(0))) or bool(rt.binary("==", _u_ruleIndex, rt.i(5))))) or bool(rt.binary("==", _u_ruleIndex, rt.i(8)))):
            should = rt.binary("==", n, rt.i(3))
        else:
            if (bool((bool(rt.binary("==", _u_ruleIndex, rt.i(1))) or bool(rt.binary("==", _u_ruleIndex, rt.i(11))))) or bool(rt.binary("==", _u_ruleIndex, rt.i(16)))):
                should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(6))))
            else:
                if rt.binary("==", _u_ruleIndex, rt.i(2)):
                    should = rt.binary("==", n, rt.i(2))
                else:
                    if rt.binary("==", _u_ruleIndex, rt.i(3)):
                        should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(8))))
                    else:
                        if rt.binary("==", _u_ruleIndex, rt.i(4)):
                            should = (bool((bool((bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(7))))) or bool(rt.binary("==", n, rt.i(8))))
                        else:
                            if rt.binary("==", _u_ruleIndex, rt.i(6)):
                                should = (bool((bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(3))))) or bool(rt.binary("==", n, rt.i(5))))) or bool(rt.binary("==", n, rt.i(7))))
                            else:
                                if rt.binary("==", _u_ruleIndex, rt.i(7)):
                                    should = (bool((bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(5))))) or bool(rt.binary("==", n, rt.i(7))))
                                else:
                                    if rt.binary("==", _u_ruleIndex, rt.i(9)):
                                        should = (bool(rt.binary("==", n, rt.i(2))) or bool(rt.binary("==", n, rt.i(5))))
                                    else:
                                        if rt.binary("==", _u_ruleIndex, rt.i(10)):
                                            should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary(">=", n, rt.i(5))))
                                        else:
                                            if rt.binary("==", _u_ruleIndex, rt.i(12)):
                                                should = (bool((bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(8))))
                                            else:
                                                if rt.binary("==", _u_ruleIndex, rt.i(13)):
                                                    should = (bool((bool((bool(rt.binary("==", n, rt.i(4))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(7))))) or bool(rt.binary("==", n, rt.i(8))))
                                                else:
                                                    if rt.binary("==", _u_ruleIndex, rt.i(14)):
                                                        should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(4))))
                                                    else:
                                                        if rt.binary("==", _u_ruleIndex, rt.i(15)):
                                                            should = (bool((bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(8))))
                                                        else:
                                                            if rt.binary("==", _u_ruleIndex, rt.i(17)):
                                                                should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(7))))
        return should
    def shouldSurvive__int_float(n, current):
        should = False
        if (bool((bool((bool(rt.binary("==", _u_ruleIndex, rt.i(0))) or bool(rt.binary("==", _u_ruleIndex, rt.i(1))))) or bool(rt.binary("==", _u_ruleIndex, rt.i(3))))) or bool(rt.binary("==", _u_ruleIndex, rt.i(17)))):
            should = (bool(rt.binary("==", n, rt.i(2))) or bool(rt.binary("==", n, rt.i(3))))
        else:
            if rt.binary("==", _u_ruleIndex, rt.i(2)):
                should = False
            else:
                if rt.binary("==", _u_ruleIndex, rt.i(4)):
                    should = (bool((bool((bool((bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(4))))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(7))))) or bool(rt.binary("==", n, rt.i(8))))
                else:
                    if rt.binary("==", _u_ruleIndex, rt.i(5)):
                        should = True
                    else:
                        if rt.binary("==", _u_ruleIndex, rt.i(6)):
                            should = (bool((bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(3))))) or bool(rt.binary("==", n, rt.i(5))))) or bool(rt.binary("==", n, rt.i(7))))
                        else:
                            if rt.binary("==", _u_ruleIndex, rt.i(7)):
                                should = (bool((bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(3))))) or bool(rt.binary("==", n, rt.i(5))))) or bool(rt.binary("==", n, rt.i(8))))
                            else:
                                if rt.binary("==", _u_ruleIndex, rt.i(8)):
                                    should = (bool(rt.binary(">=", n, rt.i(1))) and bool(rt.binary("<=", n, rt.i(5))))
                                else:
                                    if rt.binary("==", _u_ruleIndex, rt.i(9)):
                                        should = rt.binary("==", n, rt.i(4))
                                    else:
                                        if rt.binary("==", _u_ruleIndex, rt.i(10)):
                                            should = rt.binary(">=", n, rt.i(5))
                                        else:
                                            if rt.binary("==", _u_ruleIndex, rt.i(11)):
                                                should = (bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(2))))) or bool(rt.binary("==", n, rt.i(5))))
                                            else:
                                                if (bool(rt.binary("==", _u_ruleIndex, rt.i(12))) or bool(rt.binary("==", _u_ruleIndex, rt.i(16)))):
                                                    should = (bool((bool(rt.binary("==", n, rt.i(2))) or bool(rt.binary("==", n, rt.i(4))))) or bool(rt.binary("==", n, rt.i(5))))
                                                else:
                                                    if rt.binary("==", _u_ruleIndex, rt.i(13)):
                                                        should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary(">=", n, rt.i(5))))
                                                    else:
                                                        if rt.binary("==", _u_ruleIndex, rt.i(14)):
                                                            should = (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(4))))
                                                        else:
                                                            if rt.binary("==", _u_ruleIndex, rt.i(15)):
                                                                should = (bool((bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(2))))) or bool(rt.binary("==", n, rt.i(5))))) or bool(rt.binary(">=", n, rt.i(7))))
        if rt.binary("<", current, rt.f(0.5)):
            should = False
        return should
    def countNeighbors__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv, "float")
        texelSize = rt.copy(texelSize, "float")
        count = rt.i(0)
        y = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                if (bool(rt.binary("==", x, rt.i(0))) and bool(rt.binary("==", y, rt.i(0)))):
                    continue
                offset = rt.binary("*", rt.construct(2, rt.construct(1, x), rt.construct(1, y)), texelSize, 2, "float")
                n = rt.swizzle(rt.texture(_u_bufTex, rt.binary("+", uv, offset, 2, "float")), "r")
                count = rt.binary("+", count, rt.construct(1, rt.binary(">", n, rt.f(0.5)), base="int"), 1, "int")
        return count
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
        prevFrame = rt.swizzle(rt.texture(_u_tex, uv), "rgb")
        prevLum = lum__vec3(prevFrame)
        neighbors = countNeighbors__vec2_vec2(uv, texelSize)
        newState = state
        if shouldBeBorn__int(neighbors):
            newState = rt.f(1.0)
        else:
            if shouldSurvive__int_float(neighbors, state):
                newState = rt.f(1.0)
            else:
                newState = rt.f(0.0)
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
