def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_enabled = U.get("enabled", False)
    _u_useSpecks = U.get("useSpecks", False)
    _u_splatSource = U.get("splatSource", 0)
    _u_scale = U.get("scale", rt.f(0.0))
    _u_cutoff = U.get("cutoff", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    _u_splatColor = U.get("splatColor", rt.construct(3, 0.0))
    _u_mode = U.get("mode", 0)
    _u_speckScale = U.get("speckScale", rt.f(0.0))
    _u_speckCutoff = U.get("speckCutoff", rt.f(0.0))
    _u_speckSpeed = U.get("speckSpeed", rt.f(0.0))
    _u_speckSeed = U.get("speckSeed", rt.f(0.0))
    _u_speckColor = U.get("speckColor", rt.construct(3, 0.0))
    _u_speckMode = U.get("speckMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def smootherstep__float(x):
        return rt.binary("*", rt.binary("*", rt.binary("*", x, x, 1, "float"), x, 1, "float"), rt.binary("+", rt.binary("*", x, rt.binary("-", rt.binary("*", x, rt.f(6.0), 1, "float"), rt.f(15.0), 1, "float"), 1, "float"), rt.f(10.0), 1, "float"), 1, "float")
    def smoothlerp__float_float_float(x, a, b):
        return rt.binary("+", a, rt.binary("*", smootherstep__float(x), rt.binary("-", b, a, 1, "float"), 1, "float"), 1, "float")
    def grid__vec2_vec2_float(st, cell, speed):
        st = rt.copy(st, "float")
        cell = rt.copy(cell, "float")
        angle = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, cell, rt.f(1.0))), "r"), rt.f(6.28318530718), 1, "float")
        angle = rt.binary("+", angle, rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), speed, 1, "float"), 1, "float")
        gradient = rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1))
        dist = rt.binary("-", st, cell, 2, "float")
        return rt.dot(gradient, dist)
    def perlin__vec2_vec2_float(st, scale, speed):
        st = rt.copy(st, "float")
        scale = rt.copy(scale, "float")
        st[:] = rt.binary("-", st, rt.f(0.5), 2, "float")
        st[:] = rt.binary("*", st, scale, 2, "float")
        st[:] = rt.binary("+", st, rt.f(0.5), 2, "float")
        cell = rt.component_wise("floor", st, width=2)
        tl = grid__vec2_vec2_float(st, cell, speed)
        tr = grid__vec2_vec2_float(st, rt.construct(2, rt.binary("+", rt.swizzle(cell, "x"), rt.f(1.0), 1, "float"), rt.swizzle(cell, "y")), speed)
        bl = grid__vec2_vec2_float(st, rt.construct(2, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.f(1.0), 1, "float")), speed)
        br = grid__vec2_vec2_float(st, rt.binary("+", cell, rt.f(1.0), 2, "float"), speed)
        upper = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1, "float"), tl, tr)
        lower = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "x"), rt.swizzle(cell, "x"), 1, "float"), bl, br)
        val = smoothlerp__float_float_float(rt.binary("-", rt.swizzle(st, "y"), rt.swizzle(cell, "y"), 1, "float"), upper, lower)
        return rt.binary("+", rt.binary("*", val, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
    def splat__vec2_vec2(st, scale):
        st = rt.copy(st, "float")
        scale = rt.copy(scale, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", rt.binary("+", st, _u_seed, 2, "float"), rt.f(50.0), 2, "float"), rt.construct(2, rt.f(2.0), rt.f(3.0)), rt.f(0.0)), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", rt.binary("+", st, _u_seed, 2, "float"), rt.f(60.0), 2, "float"), rt.construct(2, rt.f(2.0), rt.f(3.0)), rt.f(0.0)), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), 1, "float"))
        d = rt.binary("+", rt.binary("+", perlin__vec2_vec2_float(st, rt.binary("*", rt.construct(2, rt.f(4.0)), scale, 2, "float"), _u_speed), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(10.0), 2, "float"), rt.binary("*", rt.construct(2, rt.f(8.0)), scale, 2, "float"), _u_speed), rt.f(0.5), 1, "float"), 1, "float"), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(20.0), 2, "float"), rt.binary("*", rt.construct(2, rt.f(16.0)), scale, 2, "float"), _u_speed), rt.f(0.25), 1, "float"), 1, "float")
        return rt.component_wise("step", map__float_float_float_float_float(_u_cutoff, rt.f(0.0), rt.f(100.0), rt.f(0.85), rt.f(0.99)), d, width=1)
    def speckle__vec2_vec2(st, scale):
        st = rt.copy(st, "float")
        scale = rt.copy(scale, "float")
        d = rt.binary("+", perlin__vec2_vec2_float(st, scale, _u_speckSpeed), rt.binary("*", perlin__vec2_vec2_float(rt.binary("+", st, rt.f(10.0), 2, "float"), rt.binary("*", scale, rt.f(2.0), 2, "float"), _u_speckSpeed), rt.f(0.5), 1, "float"), 1, "float")
        d = rt.binary("/", d, rt.f(1.5), 1, "float")
        return rt.component_wise("step", map__float_float_float_float_float(_u_speckCutoff, rt.f(0.0), rt.f(100.0), rt.f(0.6), rt.f(0.7)), d, width=1)
    def shape__vec2_int_float(st, sides, blend):
        st = rt.copy(st, "float")
        st[:] = rt.binary("-", rt.binary("*", st, rt.f(2.0), 2, "float"), rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float"), blend, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        noiseCoord = rt.binary("*", uv, rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float")
        speckMask = rt.f(0.0)
        if _u_useSpecks:
            speckMask = speckle__vec2_vec2(rt.binary("+", noiseCoord, _u_speckSeed, 2, "float"), rt.binary("*", rt.construct(2, rt.f(32.0)), map__float_float_float_float_float(_u_speckScale, rt.f(1.0), rt.f(5.0), rt.f(2.0), rt.f(0.5)), 2, "float"))
            if rt.binary("==", _u_speckMode, rt.i(0)):
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), _u_speckColor, speckMask, width=3))
            else:
                if rt.binary("==", _u_speckMode, rt.i(1)):
                    color[:] = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", speckMask, rt.f(0.1), 1, "float"), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
                else:
                    if rt.binary("==", _u_speckMode, rt.i(2)):
                        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"), speckMask, width=3))
                    else:
                        if rt.binary("==", _u_speckMode, rt.i(3)):
                            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), speckMask, 3, "float"))
        splatMask = rt.f(0.0)
        if _u_enabled:
            splatMask = splat__vec2_vec2(rt.binary("+", noiseCoord, _u_seed, 2, "float"), rt.construct(2, map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(5.0), rt.f(2.0), rt.f(0.5))))
            texColor = rt.construct(4, 0.0)
            if rt.binary("==", _u_mode, rt.i(0)):
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), _u_splatColor, splatMask, width=3))
            else:
                if rt.binary("==", _u_mode, rt.i(1)):
                    texColor = rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", splatMask, rt.f(0.1), 1, "float"), 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
                    color[:] = rt.component_wise("mix", color, texColor, splatMask, width=4)
                else:
                    if rt.binary("==", _u_mode, rt.i(2)):
                        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"), splatMask, width=3))
                    else:
                        if rt.binary("==", _u_mode, rt.i(3)):
                            color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), map__float_float_float_float_float(rt.binary("-", rt.binary("*", splatMask, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), rt.unary("-", rt.f(0.25)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), 3, "float"))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
