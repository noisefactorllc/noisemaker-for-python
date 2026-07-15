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
    _u_seed = U["seed"]
    _u_aspectLens = U["aspectLens"]
    _u_xChonk = U["xChonk"]
    _u_yChonk = U["yChonk"]
    _u_glitchiness = U["glitchiness"]
    _u_scanlinesAmt = U["scanlinesAmt"]
    _u_snowAmt = U["snowAmt"]
    _u_vignetteAmt = U["vignetteAmt"]
    _u_aberration = U["aberration"]
    _u_distortion = U["distortion"]
    def pcg__uvec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def f__vec2(st):
        st = rt.copy(st)
        return rt.swizzle(prng__vec3(rt.construct(3, rt.component_wise("floor", st, width=2), rt.construct(1, _u_seed))), "x")
    def bicubic__vec2(p):
        p = rt.copy(p)
        x = rt.swizzle(p, "x")
        y = rt.swizzle(p, "y")
        x1 = rt.component_wise("floor", x, width=1)
        y1 = rt.component_wise("floor", y, width=1)
        x2 = rt.binary("+", x1, rt.f(1.0), 1, "float")
        y2 = rt.binary("+", y1, rt.f(1.0), 1, "float")
        f11 = f__vec2(rt.construct(2, x1, y1))
        f12 = f__vec2(rt.construct(2, x1, y2))
        f21 = f__vec2(rt.construct(2, x2, y1))
        f22 = f__vec2(rt.construct(2, x2, y2))
        f11x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), y1)), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), y1)), 1, "float"), rt.f(2.0), 1, "float")
        f12x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), y2)), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), y2)), 1, "float"), rt.f(2.0), 1, "float")
        f21x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), y1)), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), y1)), 1, "float"), rt.f(2.0), 1, "float")
        f22x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), y2)), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), y2)), 1, "float"), rt.f(2.0), 1, "float")
        f11y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x1, rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x1, rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f12y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x1, rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x1, rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f21y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x2, rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x2, rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f22y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x2, rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x2, rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f11xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f12xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f21xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f22xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        Q = rt.construct(16, f11, f21, f11x, f21x, f12, f22, f12x, f22x, f11y, f21y, f11xy, f21xy, f12y, f22y, f12xy, f22xy)
        S = rt.construct(16, rt.f(1.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(3.0)), rt.f(3.0), rt.unary("-", rt.f(2.0)), rt.unary("-", rt.f(1.0)), rt.f(2.0), rt.unary("-", rt.f(2.0)), rt.f(1.0), rt.f(1.0))
        T = rt.construct(16, rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(3.0)), rt.f(2.0), rt.f(0.0), rt.f(0.0), rt.f(3.0), rt.unary("-", rt.f(2.0)), rt.f(0.0), rt.f(1.0), rt.unary("-", rt.f(2.0)), rt.f(1.0), rt.f(0.0), rt.f(0.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        A = rt.matrix_mult(rt.matrix_mult(T, Q, 4), S, 4)
        t = rt.component_wise("fract", rt.swizzle(p, "x"), width=1)
        u = rt.component_wise("fract", rt.swizzle(p, "y"), width=1)
        tv = rt.construct(4, rt.f(1.0), t, rt.binary("*", t, t, 1, "float"), rt.binary("*", rt.binary("*", t, t, 1, "float"), t, 1, "float"))
        uv = rt.construct(4, rt.f(1.0), u, rt.binary("*", u, u, 1, "float"), rt.binary("*", rt.binary("*", u, u, 1, "float"), u, 1, "float"))
        return rt.dot(rt.matrix_mult(tv, A, 4), uv)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def scanlines__vec4_vec2(color, st):
        color = rt.copy(color)
        st = rt.copy(st)
        centerDistance = rt.binary("*", rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), st, 2, "float")), rt.f(3.14159265359), 1, "float"), rt.f(0.5), 1, "float")
        noise = rt.binary("*", periodicFunction__float(rt.binary("-", bicubic__vec2(rt.binary("*", st, rt.f(4.0), 2, "float")), _u_time, 1, "float")), map__float_float_float_float_float(_u_scanlinesAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.5)), 1, "float")
        hatch = rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.binary("*", rt.component_wise("mix", rt.swizzle(st, "y"), rt.binary("+", rt.swizzle(st, "y"), noise, 1, "float"), rt.component_wise("pow", centerDistance, rt.f(8.0), width=1), width=1), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.5), 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float")
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("*", rt.swizzle(color, "rgb"), hatch, 3, "float"), map__float_float_float_float_float(_u_scanlinesAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.5)), width=3))
        return color
    def snow__vec4_vec2(color, st):
        color = rt.copy(color)
        st = rt.copy(st)
        st = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        amt = rt.binary("/", _u_snowAmt, rt.f(100.0), 1, "float")
        noise = rt.swizzle(prng__vec3(rt.construct(3, st, rt.binary("*", _u_time, rt.f(1000.0), 1, "float"))), "x")
        mask = rt.f(0.0)
        maskNoise = rt.swizzle(prng__vec3(rt.construct(3, rt.binary("+", st, rt.f(10.0), 2, "float"), rt.binary("*", _u_time, rt.f(1000.0), 1, "float"))), "x")
        maskNoiseSparse = rt.binary("*", rt.component_wise("clamp", rt.binary("-", maskNoise, rt.f(0.93875), 1, "float"), rt.f(0.0), rt.f(0.06125), width=1), rt.f(16.0), 1, "float")
        if rt.binary("<", amt, rt.f(0.5)):
            mask = rt.component_wise("mix", rt.f(0.0), maskNoiseSparse, rt.binary("*", amt, rt.f(2.0), 1, "float"), width=1)
        else:
            mask = rt.component_wise("mix", maskNoiseSparse, rt.binary("*", maskNoise, maskNoise, 1, "float"), map__float_float_float_float_float(amt, rt.f(0.5), rt.f(1.0), rt.f(0.0), rt.f(1.0)), width=1)
            if rt.binary(">", amt, rt.f(0.75)):
                mask = rt.component_wise("mix", mask, rt.f(1.0), map__float_float_float_float_float(amt, rt.f(0.75), rt.f(1.0), rt.f(0.0), rt.f(1.0)), width=1)
        return rt.construct(4, rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.construct(3, noise), mask, width=3), rt.swizzle(color, "a"))
    def offsets__vec2(st):
        st = rt.copy(st)
        return rt.swizzle(prng__vec3(rt.construct(3, rt.component_wise("floor", st, width=2), rt.f(0.0))), "x")
    def glitch__vec2(st):
        st = rt.copy(st)
        freq = rt.construct(2, rt.f(1.0))
        freq = rt.assign_swizzle(freq, "x", rt.binary("*", rt.swizzle(freq, "x"), map__float_float_float_float_float(_u_xChonk, rt.f(1.0), rt.f(100.0), rt.f(50.0), rt.f(1.0)), 1, "float"))
        freq = rt.assign_swizzle(freq, "y", rt.binary("*", rt.swizzle(freq, "y"), map__float_float_float_float_float(_u_yChonk, rt.f(1.0), rt.f(100.0), rt.f(50.0), rt.f(1.0)), 1, "float"))
        freq = rt.binary("*", freq, rt.construct(2, periodicFunction__float(rt.binary("-", rt.swizzle(prng__vec3(rt.construct(3, rt.component_wise("floor", rt.binary("*", st, freq, 2, "float"), width=2), rt.f(0.0))), "x"), _u_time, 1, "float"))), 2, "float")
        g = map__float_float_float_float_float(_u_glitchiness, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        xDrift = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, rt.binary("+", rt.component_wise("floor", rt.binary("*", st, freq, 2, "float"), width=2), rt.f(10.0), 2, "float"), rt.f(0.0))), "x"), g, 1, "float")
        yDrift = rt.binary("*", rt.swizzle(prng__vec3(rt.construct(3, rt.binary("-", rt.component_wise("floor", rt.binary("*", st, freq, 2, "float"), width=2), rt.f(10.0), 2, "float"), rt.f(0.0))), "x"), g, 1, "float")
        sparseness = map__float_float_float_float_float(_u_glitchiness, rt.f(0.0), rt.f(100.0), rt.f(8.0), rt.f(2.0))
        rand = rt.swizzle(prng__vec3(rt.construct(3, rt.component_wise("floor", rt.binary("*", st, freq, 2, "float"), width=2), rt.f(0.0))), "x")
        xOffset = rt.component_wise("clamp", rt.binary("*", rt.binary("-", periodicFunction__float(rt.binary("-", rt.binary("+", rand, xDrift, 1, "float"), _u_time, 1, "float")), rt.binary("*", periodicFunction__float(rt.binary("-", xDrift, _u_time, 1, "float")), sparseness, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        yOffset = rt.component_wise("clamp", rt.binary("*", rt.binary("-", periodicFunction__float(rt.binary("-", rt.binary("+", rand, yDrift, 1, "float"), _u_time, 1, "float")), rt.binary("*", periodicFunction__float(rt.binary("-", yDrift, _u_time, 1, "float")), sparseness, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        refract = rt.binary("*", g, rt.f(0.125), 1, "float")
        st = rt.assign_swizzle(st, "x", rt.component_wise("mod", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", rt.component_wise("sin", rt.binary("*", xOffset, rt.f(6.28318530718), 1, "float"), width=1), refract, 1, "float"), 1, "float"), rt.f(1.0), width=1))
        st = rt.assign_swizzle(st, "y", rt.component_wise("mod", rt.binary("+", rt.swizzle(st, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", yOffset, rt.f(6.28318530718), 1, "float"), width=1), refract, 1, "float"), 1, "float"), rt.f(1.0), width=1))
        diff = rt.construct(2, rt.binary("-", rt.f(0.5), st, 2, "float"))
        if _u_aspectLens:
            diff = rt.binary("-", rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), rt.construct(2, rt.binary("/", rt.binary("*", rt.swizzle(st, "x"), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.swizzle(st, "y")), 2, "float")
        centerDist = rt.length(diff)
        distort = rt.f(0.0)
        zoom = rt.f(1.0)
        if rt.binary("<", _u_distortion, rt.f(0.0)):
            distort = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.unary("-", rt.f(0.5)), rt.f(0.0))
            zoom = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.01), rt.f(0.0))
        else:
            distort = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.5))
            zoom = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.unary("-", rt.f(0.25)))
        lensedCoords = rt.component_wise("fract", rt.binary("-", rt.binary("-", st, rt.binary("*", diff, zoom, 2, "float"), 2, "float"), rt.binary("*", rt.binary("*", rt.binary("*", diff, centerDist, 2, "float"), centerDist, 2, "float"), distort, 2, "float"), 2, "float"), width=2)
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberration, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.05)), centerDist, 1, "float"), rt.f(3.14159265359), 1, "float"), rt.f(0.5), 1, "float")
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), rt.swizzle(lensedCoords, "x"), width=1)
        localUV_red = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", rt.construct(2, redOffset, rt.swizzle(lensedCoords, "y")), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"), width=2)
        red = rt.texture(_u_inputTex, localUV_red)
        localUV_green = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", lensedCoords, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"), width=2)
        green = rt.texture(_u_inputTex, localUV_green)
        blueOffset = rt.component_wise("mix", rt.swizzle(lensedCoords, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), width=1)
        localUV_blue = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", rt.construct(2, blueOffset, rt.swizzle(lensedCoords, "y")), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"), width=2)
        blue = rt.texture(_u_inputTex, localUV_blue)
        return rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(green, "a"))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.construct(4, rt.f(0.0))
        blendy = periodicFunction__float(rt.binary("-", _u_time, offsets__vec2(uv), 1, "float"))
        color = glitch__vec2(uv)
        color = scanlines__vec4_vec2(color, uv)
        color = snow__vec4_vec2(color, uv)
        if rt.binary("<", _u_vignetteAmt, rt.f(0.0)):
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.binary("-", rt.binary("*", rt.swizzle(color, "rgb"), rt.f(1.0), 3, "float"), rt.component_wise("pow", rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), rt.f(1.125), 1, "float"), rt.f(2.0), width=1), 3, "float"), rt.swizzle(color, "rgb"), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), width=3))
            color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color, "a"), rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(1.0), rt.f(0.0)), 1, "float"), width=1))
        else:
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.binary("-", rt.binary("-", rt.f(1.0), rt.binary("*", rt.swizzle(color, "rgb"), rt.f(1.0), 3, "float"), 3, "float"), rt.component_wise("pow", rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), rt.f(1.125), 1, "float"), rt.f(2.0), width=1), 3, "float"), 3, "float"), map__float_float_float_float_float(_u_vignetteAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=3))
            color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color, "a"), rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(1.0), rt.f(0.0)), 1, "float"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
