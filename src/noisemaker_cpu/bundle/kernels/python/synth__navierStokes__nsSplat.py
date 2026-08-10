def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_seed = U.get("seed", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_inputForce = U.get("inputForce", rt.f(0.0))
    _u_inputDye = U.get("inputDye", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    _u_bufTex = T["bufTex"]
    _u_inputTex = T["inputTex"]
    g.fragColor = rt.construct(4, 0.0)
    def hash11__float(x):
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", rt.binary("*", x, rt.f(12.9898), 1, "float"), width=1), rt.f(43758.5453), 1, "float"), width=1)
    def hash22__vec2(p):
        p = rt.copy(p, "float")
        (p.__setitem__(0, rt.dot(p, rt.construct(2, rt.f(127.1), rt.f(311.7)))), p.__setitem__(1, rt.dot(p, rt.construct(2, rt.f(269.5), rt.f(183.3)))), p)[-1]
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", p, width=2), rt.f(43758.5453), 2, "float"), width=2)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(c, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(c, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(c, "b"), 1, "float"), 1, "float")
    def main__void():
        texSize = rt.texture_size(_u_bufTex)
        fragCoord = rt.swizzle(ctx.frag_coord, "xy")
        uv = rt.binary("/", fragCoord, rt.construct(2, texSize), 2, "float")
        prev = rt.texture(_u_bufTex, uv)
        bufferEmpty = rt.binary("==", rt.swizzle(prev, "a"), rt.f(0.0))
        vel = rt.construct(2, 0.0)
        dye = rt.f(0.0)
        seedF = rt.f(0.0)
        if (bool(_u_resetState) or bool(bufferEmpty)):
            vel = rt.construct(2, rt.f(0.0))
            dye = rt.f(0.0)
            seedF = rt.construct(1, _u_seed)
            i = rt.i(0)
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    i = rt.binary("+", i, rt.i(1), 1, "int")
                _for0_first = False
                if not (rt.binary("<", i, rt.i(9))):
                    break
                idf = rt.construct(1, i)
                c = hash22__vec2(rt.construct(2, rt.binary("+", rt.binary("*", idf, rt.f(7.31), 1, "float"), rt.f(1.0), 1, "float"), rt.binary("+", rt.binary("*", seedF, rt.f(13.7), 1, "float"), idf, 1, "float")))
                sign = (rt.f(1.0) if rt.binary(">", hash11__float(rt.binary("+", rt.binary("*", idf, rt.f(4.17), 1, "float"), rt.binary("*", seedF, rt.f(5.9), 1, "float"), 1, "float")), rt.f(0.5)) else rt.unary("-", rt.f(1.0)))
                radius = rt.binary("+", rt.f(0.1), rt.binary("*", rt.f(0.06), hash11__float(rt.binary("+", rt.binary("*", idf, rt.f(2.11), 1, "float"), seedF, 1, "float")), 1, "float"), 1, "float")
                d = rt.binary("-", uv, c, 2, "float")
                r2 = rt.dot(d, d)
                falloff = rt.component_wise("exp", rt.binary("/", rt.unary("-", r2), rt.binary("*", rt.binary("*", rt.f(2.0), radius, 1, "float"), radius, 1, "float"), 1, "float"), width=1)
                tangent = rt.construct(2, rt.unary("-", rt.swizzle(d, "y")), rt.swizzle(d, "x"))
                vel[:] = rt.binary("+", vel, rt.binary("*", rt.binary("*", rt.binary("*", tangent, sign, 2, "float"), falloff, 2, "float"), rt.f(12.0), 2, "float"), 2, "float")
                dye = rt.binary("+", dye, falloff, 1, "float")
            g.fragColor[:] = rt.construct(4, vel, rt.component_wise("clamp", dye, rt.f(0.0), rt.f(1.0), width=1), rt.f(1.0))
            return
        vel = rt.swizzle(prev, "rg")
        dye = rt.swizzle(prev, "b")
        dt = rt.binary("*", rt.component_wise("clamp", _u_speed, rt.f(0.0), rt.f(200.0), width=1), rt.f(0.0001), 1, "float")
        iForce = rt.binary("*", rt.component_wise("clamp", _u_inputForce, rt.f(0.0), rt.f(100.0), width=1), rt.f(0.01), 1, "float")
        iDye = rt.binary("*", rt.component_wise("clamp", _u_inputDye, rt.f(0.0), rt.f(100.0), width=1), rt.f(0.01), 1, "float")
        texel = rt.construct(2, 0.0)
        lc = rt.f(0.0)
        lr = rt.f(0.0)
        lu = rt.f(0.0)
        grad = rt.construct(2, 0.0)
        if (bool(rt.binary(">", iForce, rt.f(0.0))) or bool(rt.binary(">", iDye, rt.f(0.0)))):
            texel = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
            lc = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, uv), "rgb"))
            lr = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), "rgb"))
            lu = lum__vec3(rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), "rgb"))
            grad = rt.construct(2, rt.binary("-", lr, lc, 1, "float"), rt.binary("-", lu, lc, 1, "float"))
            vel[:] = rt.binary("+", vel, rt.binary("*", rt.binary("*", grad, iForce, 2, "float"), rt.f(50.0), 2, "float"), 2, "float")
            dye = rt.binary("+", dye, rt.binary("*", rt.binary("*", rt.binary("*", lc, iDye, 1, "float"), dt, 1, "float"), rt.f(60.0), 1, "float"), 1, "float")
        dye = rt.component_wise("clamp", dye, rt.f(0.0), rt.f(2.0), width=1)
        g.fragColor[:] = rt.construct(4, vel, dye, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
