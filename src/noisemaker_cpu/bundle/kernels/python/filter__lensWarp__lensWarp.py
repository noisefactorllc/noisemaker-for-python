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
    _u_displacement = U["displacement"]
    _u_speed = U["speed"]
    _u_antialias = U["antialias"]
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525)), 3), rt.construct(1, rt.i(1013904223)), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16)), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1)))
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def smootherstep__float(x):
        return rt.binary("*", rt.binary("*", rt.binary("*", x, x, 1), x, 1), rt.binary("+", rt.binary("*", x, rt.binary("-", rt.binary("*", x, rt.f(6.0), 1), rt.f(15.0), 1), 1), rt.f(10.0), 1), 1)
    def smoothlerp__float_float_float(x, a, b):
        return rt.binary("+", a, rt.binary("*", smootherstep__float(x), rt.binary("-", b, a, 1), 1), 1)
    def grid__vec2_vec2(st, cell):
        st = rt.copy(st)
        cell = rt.copy(cell)
        angle = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, cell, rt.f(1.0))), "r"), rt.f(6.28318530718), 1)
        angle = rt.binary("+", angle, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), _u_speed, 1), 1)
        gradient = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
        dist = rt.binary("-", st, cell, 2)
        return rt.dot(gradient, dist)
    def perlinNoise__vec2_vec2(st, noiseScale):
        st = rt.copy(st)
        noiseScale = rt.copy(noiseScale)
        st = rt.binary("*", st, noiseScale, 2)
        cell = rt.component_wise("floor", st, width=2)
        tl = grid__vec2_vec2(st, cell)
        tr = grid__vec2_vec2(st, rt.construct(2, rt.binary("+", rt.swizzle(cell, "x"), rt.f(1.0), 1), rt.swizzle(cell, "y")))
        bl = grid__vec2_vec2(st, rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.f(1.0), 1)))
        br = grid__vec2_vec2(st, rt.binary("+", cell, rt.f(1.0), 2))
        upper = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1), tl, tr)
        lower = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1), bl, br)
        val = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "y"), rt.swizzle(cell, "y"), 1), upper, lower)
        return rt.binary("+", rt.binary("*", val, rt.f(0.5), 1), rt.f(0.5), 1)
    def main__void():
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspectRatio = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        maxDisplacementUV = rt.binary("/", rt.f(256.0), rt.swizzle(fullRes, "x"), 1)
        clampedDisplacement = rt.component_wise("clamp", _u_displacement, rt.unary("-", maxDisplacementUV), maxDisplacementUV, width=1)
        delta = rt.component_wise("abs", rt.binary("-", uv, rt.construct(2, rt.f(0.5)), 2), width=2)
        scaled = rt.construct(2, rt.binary("*", rt.swizzle(delta, "x"), aspectRatio, 1), rt.swizzle(delta, "y"))
        maxRadius = rt.length(rt.construct(2, rt.binary("*", aspectRatio, rt.f(0.5), 1), rt.f(0.5)))
        mask = rt.component_wise("pow", rt.component_wise("clamp", rt.binary("/", rt.length(scaled), maxRadius, 1), rt.f(0.0), rt.f(1.0), width=1), rt.f(5.0), width=1)
        noiseCoord = rt.binary("*", uv, rt.construct(2, aspectRatio, rt.f(1.0)), 2)
        noiseX = perlinNoise__vec2_vec2(rt.binary("+", noiseCoord, rt.f(42.0), 2), rt.construct(2, rt.f(2.0)))
        noiseY = perlinNoise__vec2_vec2(rt.binary("+", noiseCoord, rt.f(97.0), 2), rt.construct(2, rt.f(2.0)))
        uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", rt.binary("*", rt.binary("-", noiseX, rt.f(0.5), 1), clampedDisplacement, 1), mask, 1), 1))
        uv = rt.assign_swizzle(uv, "y", rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", rt.binary("*", rt.binary("-", noiseY, rt.f(0.5), 1), clampedDisplacement, 1), mask, 1), 1))
        uv = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, fullRes, 2), _u_tileOffset, 2), _u_resolution, 2)
        localUV = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        if _u_antialias:
            dx = rt.component_wise("dFdx", uv, width=2)
            dy = rt.component_wise("dFdy", uv, width=2)
            col = rt.construct(4, rt.f(0.0))
            sUV = rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", rt.binary("+", uv, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2), 2), fullRes, 2), _u_tileOffset, 2), _u_resolution, 2)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.component_wise("clamp", sUV, rt.f(0.0), rt.f(1.0), width=2)), 4)
            sUV = rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", rt.binary("+", uv, rt.binary("*", dx, rt.f(0.125), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2), 2), fullRes, 2), _u_tileOffset, 2), _u_resolution, 2)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.component_wise("clamp", sUV, rt.f(0.0), rt.f(1.0), width=2)), 4)
            sUV = rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", rt.binary("+", uv, rt.binary("*", dx, rt.f(0.375), 2), 2), rt.binary("*", dy, rt.f(0.125), 2), 2), fullRes, 2), _u_tileOffset, 2), _u_resolution, 2)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.component_wise("clamp", sUV, rt.f(0.0), rt.f(1.0), width=2)), 4)
            sUV = rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", rt.binary("+", uv, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2), 2), rt.binary("*", dy, rt.f(0.375), 2), 2), fullRes, 2), _u_tileOffset, 2), _u_resolution, 2)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.component_wise("clamp", sUV, rt.f(0.0), rt.f(1.0), width=2)), 4)
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4)
        else:
            g.fragColor = rt.texture(_u_inputTex, localUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
