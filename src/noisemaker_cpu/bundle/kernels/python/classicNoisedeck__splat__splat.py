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
    _u_enabled = U["enabled"]
    _u_useSpecks = U["useSpecks"]
    _u_splatSource = U["splatSource"]
    _u_scale = U["scale"]
    _u_cutoff = U["cutoff"]
    _u_speed = U["speed"]
    _u_seed = U["seed"]
    _u_splatColor = U["splatColor"]
    _u_mode = U["mode"]
    _u_speckScale = U["speckScale"]
    _u_speckCutoff = U["speckCutoff"]
    _u_speckSpeed = U["speckSpeed"]
    _u_speckSeed = U["speckSeed"]
    _u_speckColor = U["speckColor"]
    _u_speckMode = U["speckMode"]
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
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
    def grid__vec2_vec2_float(st, cell, speed):
        st = rt.copy(st)
        cell = rt.copy(cell)
        angle = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, cell, rt.f(1.0))), "r"), rt.f(6.28318530718), 1)
        angle = rt.binary("+", angle, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), speed, 1), 1)
        gradient = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
        dist = rt.binary("-", st, cell, 2)
        return rt.dot(gradient, dist)
    def perlin__vec2_vec2_float(st, scale, speed):
        st = rt.copy(st)
        scale = rt.copy(scale)
        st = rt.binary("-", st, rt.f(0.5), 2)
        st = rt.binary("*", st, scale, 2)
        st = rt.binary("+", st, rt.f(0.5), 2)
        cell = rt.component_wise("floor", st, width=2)
        tl = grid__vec2_vec2_float(st, cell, speed)
        tr = grid__vec2_vec2_float(st, rt.construct(2, rt.binary("+", rt.swizzle(cell, "x"), rt.f(1.0), 1), rt.swizzle(cell, "y")), speed)
        bl = grid__vec2_vec2_float(st, rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.f(1.0), 1)), speed)
        br = grid__vec2_vec2_float(st, rt.binary("+", cell, rt.f(1.0), 2), speed)
        upper = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1), tl, tr)
        lower = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1), bl, br)
        val = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "y"), rt.swizzle(cell, "y"), 1), upper, lower)
        return rt.binary("+", rt.binary("*", val, rt.f(0.5), 1), rt.f(0.5), 1)
    def splat__vec2_vec2(st, scale):
        st = rt.copy(st)
        scale = rt.copy(scale)
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", rt.binary("+", st, _u_seed, 2), rt.f(50.0), 2), rt.construct(2, rt.f(2.0), rt.f(3.0)), rt.f(0.0)), rt.f(0.5), 1), rt.f(0.5), 1), 1))
        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", rt.binary("+", st, _u_seed, 2), rt.f(60.0), 2), rt.construct(2, rt.f(2.0), rt.f(3.0)), rt.f(0.0)), rt.f(0.5), 1), rt.f(0.5), 1), 1))
        d = rt.binary("+", rt.binary("+", perlin__vec2_vec2_float(st, rt.binary("*", rt.construct(2, rt.f(4.0)), scale, 2), _u_speed), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(10.0), 2), rt.binary("*", rt.construct(2, rt.f(8.0)), scale, 2), _u_speed), rt.f(0.5), 1), 1), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(20.0), 2), rt.binary("*", rt.construct(2, rt.f(16.0)), scale, 2), _u_speed), rt.f(0.25), 1), 1)
        return rt.component_wise("step", map__float_float_float_float_float(_u_cutoff, rt.f(0.0), rt.f(100.0), rt.f(0.85), rt.f(0.99)), d, width=1)
    def speckle__vec2_vec2(st, scale):
        st = rt.copy(st)
        scale = rt.copy(scale)
        d = rt.binary("+", perlin__vec2_vec2_float(st, scale, _u_speckSpeed), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(10.0), 2), rt.binary("*", scale, rt.f(2.0), 2), _u_speckSpeed), rt.f(0.5), 1), 1)
        d = rt.binary("/", d, rt.f(1.5), 1)
        return rt.component_wise("step", map__float_float_float_float_float(_u_speckCutoff, rt.f(0.0), rt.f(100.0), rt.f(0.6), rt.f(0.7)), d, width=1)
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st)
        st = rt.binary("-", rt.binary("*", st, rt.f(2.0), 2), rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1), rt.f(1.0)), 2)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1)
        r = rt.binary("/", rt.f(6.28318530718), sides, 1)
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1), 1), width=1), r, 1), a, 1), width=1), rt.length(st), 1), blend, 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        color = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        noiseCoord = rt.binary("*", uv, rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1), rt.f(1.0)), 2)
        if _u_useSpecks:
            speckMask = speckle__vec2_vec2(rt.binary("+", noiseCoord, _u_speckSeed, 2), rt.binary("*", rt.construct(2, rt.f(32.0)), map__float_float_float_float_float(_u_speckScale, rt.f(1.0), rt.f(5.0), rt.f(2.0), rt.f(0.5)), 2))
            if rt.binary("==", _u_speckMode, rt.i(0)):
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), _u_speckColor, speckMask, width=3))
            else:
                if rt.binary("==", _u_speckMode, rt.i(1)):
                    color = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", speckMask, rt.f(0.1), 1), 2), _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
                else:
                    if rt.binary("==", _u_speckMode, rt.i(2)):
                        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3), speckMask, width=3))
                    else:
                        if rt.binary("==", _u_speckMode, rt.i(3)):
                            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), speckMask, 3))
        if _u_enabled:
            splatMask = splat__vec2_vec2(rt.binary("+", noiseCoord, _u_seed, 2), rt.construct(2, map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(5.0), rt.f(2.0), rt.f(0.5))))
            if rt.binary("==", _u_mode, rt.i(0)):
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), _u_splatColor, splatMask, width=3))
            else:
                if rt.binary("==", _u_mode, rt.i(1)):
                    texColor = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", splatMask, rt.f(0.1), 1), 2), _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
                    color = rt.component_wise("mix", color, texColor, splatMask, width=4)
                else:
                    if rt.binary("==", _u_mode, rt.i(2)):
                        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3), splatMask, width=3))
                    else:
                        if rt.binary("==", _u_mode, rt.i(3)):
                            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), map__float_float_float_float_float(rt.binary("-", rt.binary("*", splatMask, rt.f(0.5), 1), rt.f(0.5), 1), rt.unary("-", rt.f(0.25)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), 3))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
