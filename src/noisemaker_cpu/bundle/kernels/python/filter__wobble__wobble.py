def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_time = U["time"]
    _u_speed = U["speed"]
    _u_range = U["range"]
    _u_wrap = U["wrap"]
    g.TAU = rt.f(6.28318530717959)
    g.X_NOISE_SEED = rt.construct(3, rt.f(17.0), rt.f(29.0), rt.f(11.0))
    g.Y_NOISE_SEED = rt.construct(3, rt.f(41.0), rt.f(23.0), rt.f(7.0))
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
    def hash31__vec3(p):
        p = rt.copy(p)
        seed = cpu_uvec3__float_float_float(rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1))))
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__vec3(seed), "x")), rt.f(4294967295.0), 1)
    def noise3d__vec3(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=3)
        f = rt.component_wise("fract", p, width=3)
        f = rt.binary("*", rt.binary("*", f, f, 3), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 3), 3), 3)
        n000 = hash31__vec3(i)
        n100 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(0.0)), 3))
        n010 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), 3))
        n110 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(0.0)), 3))
        n001 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0)), 3))
        n101 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(1.0)), 3))
        n011 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(1.0)), 3))
        n111 = hash31__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(1.0)), 3))
        x0 = rt.component_wise("mix", n000, n100, rt.swizzle(f, "x"), width=1)
        x1 = rt.component_wise("mix", n010, n110, rt.swizzle(f, "x"), width=1)
        x2 = rt.component_wise("mix", n001, n101, rt.swizzle(f, "x"), width=1)
        x3 = rt.component_wise("mix", n011, n111, rt.swizzle(f, "x"), width=1)
        y0 = rt.component_wise("mix", x0, x1, rt.swizzle(f, "y"), width=1)
        y1 = rt.component_wise("mix", x2, x3, rt.swizzle(f, "y"), width=1)
        return rt.component_wise("mix", y0, y1, rt.swizzle(f, "z"), width=1)
    def simplexRandom__float_float_vec3(t, spd, seed):
        seed = rt.copy(seed)
        angle = rt.binary("*", t, g.TAU, 1)
        z = rt.binary("+", rt.binary("+", rt.binary("*", rt.component_wise("cos", angle, width=1), spd, 1), rt.swizzle(seed, "x"), 1), rt.binary("*", spd, rt.f(0.317), 1), 1)
        w = rt.binary("+", rt.binary("+", rt.binary("*", rt.component_wise("sin", angle, width=1), spd, 1), rt.swizzle(seed, "y"), 1), rt.binary("*", spd, rt.f(0.519), 1), 1)
        n = noise3d__vec3(rt.construct(3, z, w, rt.binary("+", rt.swizzle(seed, "z"), rt.binary("*", spd, rt.f(0.1), 1), 1)))
        return rt.component_wise("clamp", n, rt.f(0.0), rt.f(1.0), width=1)
    def applyWrap__vec2(uv):
        uv = rt.copy(uv)
        mode = rt.construct(1, _u_wrap)
        if rt.binary("==", mode, rt.i(0)):
            return rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
        else:
            if rt.binary("==", mode, rt.i(1)):
                return rt.component_wise("fract", uv, width=2)
        return rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
    def main__void():
        spd = rt.component_wise("max", _u_speed, rt.f(0.001), width=1)
        r = rt.component_wise("max", _u_range, rt.f(0.0), width=1)
        xRandom = simplexRandom__float_float_vec3(rt.binary("+", _u_time, rt.binary("*", _u_speed, rt.f(0.1), 1), 1), spd, g.X_NOISE_SEED)
        yRandom = simplexRandom__float_float_vec3(rt.binary("+", _u_time, rt.binary("*", _u_speed, rt.f(0.1), 1), 1), spd, g.Y_NOISE_SEED)
        offsetScale = rt.binary("*", r, rt.binary("+", rt.f(0.01), rt.binary("*", _u_speed, rt.f(0.02), 1), 1), 1)
        offset = rt.binary("*", rt.binary("-", rt.construct(2, xRandom, yRandom), rt.f(0.5), 2), offsetScale, 2)
        sampleCoord = rt.binary("+", g.v_texCoord, offset, 2)
        sampleCoord = applyWrap__vec2(sampleCoord)
        sampled = rt.texture(_u_inputTex, sampleCoord)
        g.fragColor = sampled
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
