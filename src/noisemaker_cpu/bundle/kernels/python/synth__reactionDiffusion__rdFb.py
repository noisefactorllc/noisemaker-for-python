def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_bufTex = T["bufTex"]
    _u_feed = U.get("feed", rt.f(0.0))
    _u_kill = U.get("kill", rt.f(0.0))
    _u_rate1 = U.get("rate1", rt.f(0.0))
    _u_rate2 = U.get("rate2", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_weight = U.get("weight", rt.f(0.0))
    _u_sourceF = U.get("sourceF", 0)
    _u_sourceK = U.get("sourceK", 0)
    _u_sourceR1 = U.get("sourceR1", 0)
    _u_sourceR2 = U.get("sourceR2", 0)
    _u_zoom = U.get("zoom", rt.f(0.0))
    _u_inputTex = T["inputTex"]
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def lp__sampler2D_vec2_vec2(tex, uv, size):
        uv = rt.copy(uv, "float")
        size = rt.copy(size, "float")
        val = rt.construct(3, rt.f(0.0))
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1))), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.05), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1))), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.2), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(1), rt.unary("-", rt.i(1))), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.05), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0)), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.2), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(0), rt.i(0)), 2, "float"), size, 2, "float")), "rgb"), rt.unary("-", rt.f(1.0)), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(1), rt.i(0)), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.2), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1)), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.05), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(0), rt.i(1)), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.2), 3, "float"), 3, "float")
        val[:] = rt.binary("+", val, rt.binary("*", rt.swizzle(rt.texture(tex, rt.binary("/", rt.binary("+", uv, rt.construct(2, rt.i(1), rt.i(1)), 2, "float"), size, 2, "float")), "rgb"), rt.f(0.05), 3, "float"), 3, "float")
        return val
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def lum__vec3(color):
        color = rt.copy(color, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def hash__vec2(p):
        p = rt.copy(p, "float")
        p2 = rt.component_wise("fract", rt.binary("*", p, rt.construct(2, rt.f(0.1031), rt.f(0.103)), 2, "float"), width=2)
        p2[:] = rt.binary("+", p2, rt.dot(p2, rt.binary("+", rt.swizzle(p2, "yx"), rt.f(33.33), 2, "float")), 2, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p2, "x"), rt.swizzle(p2, "y"), 1, "float"), rt.swizzle(p2, "x"), 1, "float"), width=1)
    def main__void():
        texSize = rt.texture_size(_u_bufTex)
        tex = rt.texture(_u_bufTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float"))
        a = rt.swizzle(tex, "r")
        b = rt.swizzle(tex, "g")
        bufferIsEmpty = (bool((bool((bool(rt.binary("==", rt.swizzle(tex, "r"), rt.f(0.0))) and bool(rt.binary("==", rt.swizzle(tex, "g"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(tex, "b"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(tex, "a"), rt.f(0.0))))
        if (bool(bufferIsEmpty) or bool(_u_resetState)):
            a = rt.f(1.0)
            b = rt.f(0.0)
            if rt.binary(">", hash__vec2(rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.construct(1, _u_seed)), 2, "float")), rt.f(0.99)):
                b = rt.f(1.0)
            g.fragColor[:] = rt.construct(4, a, b, rt.f(0.0), rt.f(1.0))
            return
        color = lp__sampler2D_vec2_vec2(_u_bufTex, rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize))
        prevFrameCoord = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        prevFrame = rt.swizzle(rt.texture(_u_inputTex, prevFrameCoord), "rgb")
        prevLum = lum__vec3(prevFrame)
        f = rt.binary("*", _u_feed, rt.f(0.001), 1, "float")
        k = rt.binary("*", _u_kill, rt.f(0.001), 1, "float")
        r1 = rt.binary("*", _u_rate1, rt.f(0.01), 1, "float")
        r2 = rt.binary("*", _u_rate2, rt.f(0.01), 1, "float")
        s = rt.binary("*", _u_speed, rt.f(0.01), 1, "float")
        val = rt.f(0.0)
        if rt.binary(">", _u_sourceF, rt.i(0)):
            val = prevLum
            if rt.binary("==", _u_sourceF, rt.i(2)):
                val = rt.binary("-", rt.f(1.0), prevLum, 1, "float")
            else:
                if rt.binary("==", _u_sourceF, rt.i(3)):
                    val = rt.swizzle(prevFrame, "r")
                else:
                    if rt.binary("==", _u_sourceF, rt.i(4)):
                        val = rt.swizzle(prevFrame, "g")
                    else:
                        if rt.binary("==", _u_sourceF, rt.i(5)):
                            val = rt.swizzle(prevFrame, "b")
                        else:
                            if rt.binary("==", _u_sourceF, rt.i(6)):
                                val = map__float_float_float_float_float(prevLum, rt.f(0.0), rt.f(1.0), rt.f(0.01), rt.f(0.11))
                                f = rt.component_wise("mix", f, val, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
            if rt.binary("!=", _u_sourceF, rt.i(6)):
                val = map__float_float_float_float_float(val, rt.f(0.0), rt.f(1.0), rt.f(0.01), rt.f(0.11))
                f = val
        if rt.binary(">", _u_sourceK, rt.i(0)):
            val = prevLum
            if rt.binary("==", _u_sourceK, rt.i(2)):
                val = rt.binary("-", rt.f(1.0), prevLum, 1, "float")
            else:
                if rt.binary("==", _u_sourceK, rt.i(3)):
                    val = rt.swizzle(prevFrame, "r")
                else:
                    if rt.binary("==", _u_sourceK, rt.i(4)):
                        val = rt.swizzle(prevFrame, "g")
                    else:
                        if rt.binary("==", _u_sourceK, rt.i(5)):
                            val = rt.swizzle(prevFrame, "b")
                        else:
                            if rt.binary("==", _u_sourceK, rt.i(6)):
                                val = map__float_float_float_float_float(prevLum, rt.f(0.0), rt.f(1.0), rt.f(0.045), rt.f(0.07))
                                k = rt.component_wise("mix", k, val, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
            if rt.binary("!=", _u_sourceK, rt.i(6)):
                val = map__float_float_float_float_float(val, rt.f(0.0), rt.f(1.0), rt.f(0.045), rt.f(0.07))
                k = val
        if rt.binary(">", _u_sourceR1, rt.i(0)):
            val = prevLum
            if rt.binary("==", _u_sourceR1, rt.i(2)):
                val = rt.binary("-", rt.f(1.0), prevLum, 1, "float")
            else:
                if rt.binary("==", _u_sourceR1, rt.i(3)):
                    val = rt.swizzle(prevFrame, "r")
                else:
                    if rt.binary("==", _u_sourceR1, rt.i(4)):
                        val = rt.swizzle(prevFrame, "g")
                    else:
                        if rt.binary("==", _u_sourceR1, rt.i(5)):
                            val = rt.swizzle(prevFrame, "b")
                        else:
                            if rt.binary("==", _u_sourceR1, rt.i(6)):
                                val = map__float_float_float_float_float(prevLum, rt.f(0.0), rt.f(1.0), rt.f(0.5), rt.f(1.2))
                                r1 = rt.component_wise("mix", r1, val, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
            if rt.binary("!=", _u_sourceR1, rt.i(6)):
                val = map__float_float_float_float_float(val, rt.f(0.0), rt.f(1.0), rt.f(0.5), rt.f(1.2))
                r1 = val
        if rt.binary(">", _u_sourceR2, rt.i(0)):
            val = prevLum
            if rt.binary("==", _u_sourceR2, rt.i(2)):
                val = rt.binary("-", rt.f(1.0), prevLum, 1, "float")
            else:
                if rt.binary("==", _u_sourceR2, rt.i(3)):
                    val = rt.swizzle(prevFrame, "r")
                else:
                    if rt.binary("==", _u_sourceR2, rt.i(4)):
                        val = rt.swizzle(prevFrame, "g")
                    else:
                        if rt.binary("==", _u_sourceR2, rt.i(5)):
                            val = rt.swizzle(prevFrame, "b")
                        else:
                            if rt.binary("==", _u_sourceR2, rt.i(6)):
                                val = map__float_float_float_float_float(prevLum, rt.f(0.0), rt.f(1.0), rt.f(0.2), rt.f(0.5))
                                r2 = rt.component_wise("mix", r2, val, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
            if rt.binary("!=", _u_sourceR2, rt.i(6)):
                val = map__float_float_float_float_float(val, rt.f(0.0), rt.f(1.0), rt.f(0.2), rt.f(0.5))
                r2 = val
        a2 = rt.binary("+", a, rt.binary("*", rt.binary("+", rt.binary("-", rt.binary("*", r1, rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.binary("*", a, b, 1, "float"), b, 1, "float"), 1, "float"), rt.binary("*", f, rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), 1, "float"), s, 1, "float"), 1, "float")
        b2 = rt.binary("+", b, rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("*", r2, rt.swizzle(color, "g"), 1, "float"), rt.binary("*", rt.binary("*", a, b, 1, "float"), b, 1, "float"), 1, "float"), rt.binary("*", rt.binary("+", k, f, 1, "float"), b, 1, "float"), 1, "float"), s, 1, "float"), 1, "float")
        a2 = rt.component_wise("clamp", a2, rt.f(0.0), rt.f(1.0), width=1)
        b2 = rt.component_wise("clamp", b2, rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor[:] = rt.construct(4, a2, b2, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
