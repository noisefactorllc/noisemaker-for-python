def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_speed = U["speed"]
    _u_timeOffset = U["timeOffset"]
    _u_distortion = U["distortion"]
    _u_noise = U["noise"]
    _u_mode = U["mode"]
    _u_time = U["time"]
    _u_renderScale = U["renderScale"]
    g.TAU = rt.f(6.283185307179586)
    g.BASE_SEED_LINE = rt.construct(3, rt.f(37.0), rt.f(91.0), rt.f(53.0))
    g.TIME_SEED_LINE = rt.construct(3, rt.binary("+", rt.swizzle(g.BASE_SEED_LINE, "x"), rt.f(97.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_LINE, "y"), rt.f(59.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_LINE, "z"), rt.f(131.0), 1))
    g.BASE_SEED_SWERVE = rt.construct(3, rt.f(11.0), rt.f(73.0), rt.f(29.0))
    g.TIME_SEED_SWERVE = rt.construct(3, rt.binary("+", rt.swizzle(g.BASE_SEED_SWERVE, "x"), rt.f(89.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_SWERVE, "y"), rt.f(41.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_SWERVE, "z"), rt.f(149.0), 1))
    g.BASE_SEED_WHITE = rt.construct(3, rt.f(67.0), rt.f(29.0), rt.f(149.0))
    g.TIME_SEED_WHITE = rt.construct(3, rt.binary("+", rt.swizzle(g.BASE_SEED_WHITE, "x"), rt.f(113.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_WHITE, "y"), rt.f(53.0), 1), rt.binary("+", rt.swizzle(g.BASE_SEED_WHITE, "z"), rt.f(173.0), 1))
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec2__float(value):
        return rt.construct(2, value)
    def cpu_uvec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_uvec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def mod289_vec3__vec3(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 3), width=3), rt.f(289.0), 3), 3)
    def mod289_vec4__vec4(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1), 4), width=4), rt.f(289.0), 4), 4)
    def permute__vec4(x):
        x = rt.copy(x)
        return mod289_vec4__vec4(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 4), rt.f(1.0), 4), x, 4))
    def taylor_inv_sqrt__vec4(r):
        r = rt.copy(r)
        return rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), r, 4), 4)
    def simplex_noise__vec3(v):
        v = rt.copy(v)
        c = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1))
        d = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        i0 = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.construct(3, rt.swizzle(c, "y"))), 3), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i0, 3), rt.dot(i0, rt.construct(3, rt.swizzle(c, "x"))), 3)
        step1 = rt.component_wise("step", rt.construct(3, rt.swizzle(x0, "y"), rt.swizzle(x0, "z"), rt.swizzle(x0, "x")), x0, width=3)
        l = rt.binary("-", rt.construct(3, rt.f(1.0)), step1, 3)
        i1 = rt.component_wise("min", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        i2 = rt.component_wise("max", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3), rt.construct(3, rt.swizzle(c, "x")), 3)
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3), rt.construct(3, rt.swizzle(c, "y")), 3)
        x3 = rt.binary("-", x0, rt.construct(3, rt.swizzle(d, "y")), 3)
        i = mod289_vec3__vec3(i0)
        p = permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.swizzle(i, "z"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "z"), rt.swizzle(i2, "z"), rt.f(1.0)), 4)), rt.swizzle(i, "y"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "y"), rt.swizzle(i2, "y"), rt.f(1.0)), 4)), rt.swizzle(i, "x"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "x"), rt.swizzle(i2, "x"), rt.f(1.0)), 4))
        n_ = rt.f(0.14285714285714285)
        ns = rt.binary("-", rt.binary("*", n_, rt.construct(3, rt.swizzle(d, "w"), rt.swizzle(d, "y"), rt.swizzle(d, "z")), 3), rt.construct(3, rt.swizzle(d, "x"), rt.swizzle(d, "z"), rt.swizzle(d, "x")), 3)
        j = rt.binary("-", p, rt.binary("*", rt.f(49.0), rt.component_wise("floor", rt.binary("*", rt.binary("*", p, rt.swizzle(ns, "z"), 4), rt.swizzle(ns, "z"), 4), width=4), 4), 4)
        x_ = rt.component_wise("floor", rt.binary("*", j, rt.swizzle(ns, "z"), 4), width=4)
        y_ = rt.component_wise("floor", rt.binary("-", j, rt.binary("*", rt.f(7.0), x_, 4), 4), width=4)
        x = rt.binary("+", rt.binary("*", x_, rt.swizzle(ns, "x"), 4), rt.swizzle(ns, "y"), 4)
        y = rt.binary("+", rt.binary("*", y_, rt.swizzle(ns, "x"), 4), rt.swizzle(ns, "y"), 4)
        h = rt.binary("-", rt.binary("-", rt.f(1.0), rt.component_wise("abs", x, width=4), 4), rt.component_wise("abs", y, width=4), 4)
        b0 = rt.construct(4, rt.swizzle(x, "x"), rt.swizzle(x, "y"), rt.swizzle(y, "x"), rt.swizzle(y, "y"))
        b1 = rt.construct(4, rt.swizzle(x, "z"), rt.swizzle(x, "w"), rt.swizzle(y, "z"), rt.swizzle(y, "w"))
        s0 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b0, width=4), rt.f(2.0), 4), rt.f(1.0), 4)
        s1 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b1, width=4), rt.f(2.0), 4), rt.f(1.0), 4)
        sh = rt.unary("-", rt.component_wise("step", h, rt.construct(4, rt.f(0.0)), width=4))
        a0 = rt.binary("+", rt.construct(4, rt.swizzle(b0, "x"), rt.swizzle(b0, "z"), rt.swizzle(b0, "y"), rt.swizzle(b0, "w")), rt.binary("*", rt.construct(4, rt.swizzle(s0, "x"), rt.swizzle(s0, "z"), rt.swizzle(s0, "y"), rt.swizzle(s0, "w")), rt.construct(4, rt.swizzle(sh, "x"), rt.swizzle(sh, "x"), rt.swizzle(sh, "y"), rt.swizzle(sh, "y")), 4), 4)
        a1 = rt.binary("+", rt.construct(4, rt.swizzle(b1, "x"), rt.swizzle(b1, "z"), rt.swizzle(b1, "y"), rt.swizzle(b1, "w")), rt.binary("*", rt.construct(4, rt.swizzle(s1, "x"), rt.swizzle(s1, "z"), rt.swizzle(s1, "y"), rt.swizzle(s1, "w")), rt.construct(4, rt.swizzle(sh, "z"), rt.swizzle(sh, "z"), rt.swizzle(sh, "w"), rt.swizzle(sh, "w")), 4), 4)
        g0 = rt.construct(3, rt.swizzle(a0, "x"), rt.swizzle(a0, "y"), rt.swizzle(h, "x"))
        g1 = rt.construct(3, rt.swizzle(a0, "z"), rt.swizzle(a0, "w"), rt.swizzle(h, "y"))
        g2 = rt.construct(3, rt.swizzle(a1, "x"), rt.swizzle(a1, "y"), rt.swizzle(h, "z"))
        g3 = rt.construct(3, rt.swizzle(a1, "z"), rt.swizzle(a1, "w"), rt.swizzle(h, "w"))
        norm = taylor_inv_sqrt__vec4(rt.construct(4, rt.dot(g0, g0), rt.dot(g1, g1), rt.dot(g2, g2), rt.dot(g3, g3)))
        g0n = rt.binary("*", g0, rt.swizzle(norm, "x"), 3)
        g1n = rt.binary("*", g1, rt.swizzle(norm, "y"), 3)
        g2n = rt.binary("*", g2, rt.swizzle(norm, "z"), 3)
        g3n = rt.binary("*", g3, rt.swizzle(norm, "w"), 3)
        m0 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x0, x0), 1), rt.f(0.0), width=1)
        m1 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x1, x1), 1), rt.f(0.0), width=1)
        m2 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x2, x2), 1), rt.f(0.0), width=1)
        m3 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x3, x3), 1), rt.f(0.0), width=1)
        m0sq = rt.binary("*", m0, m0, 1)
        m1sq = rt.binary("*", m1, m1, 1)
        m2sq = rt.binary("*", m2, m2, 1)
        m3sq = rt.binary("*", m3, m3, 1)
        return rt.binary("*", rt.f(42.0), rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", m0sq, m0sq, 1), rt.dot(g0n, x0), 1), rt.binary("*", rt.binary("*", m1sq, m1sq, 1), rt.dot(g1n, x1), 1), 1), rt.binary("*", rt.binary("*", m2sq, m2sq, 1), rt.dot(g2n, x2), 1), 1), rt.binary("*", rt.binary("*", m3sq, m3sq, 1), rt.dot(g3n, x3), 1), 1), 1)
    def periodic_value__float_float(t, value):
        return rt.binary("+", rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.binary("-", t, value, 1), g.TAU, 1), width=1), rt.f(0.5), 1), rt.f(0.5), 1)
    def normalized_coord__vec2_vec2(coord, dims):
        coord = rt.copy(coord)
        dims = rt.copy(dims)
        width_safe = rt.component_wise("max", rt.swizzle(dims, "x"), rt.f(1.0), width=1)
        height_safe = rt.component_wise("max", rt.swizzle(dims, "y"), rt.f(1.0), width=1)
        return rt.construct(2, rt.binary("/", rt.binary("+", rt.swizzle(coord, "x"), rt.f(0.5), 1), width_safe, 1), rt.binary("/", rt.binary("+", rt.swizzle(coord, "y"), rt.f(0.5), 1), height_safe, 1))
    def compute_simplex_value__vec2_vec2_float_float_vec3(coord, freq, t, speed_value, offset):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        offset = rt.copy(offset)
        freq_x = rt.component_wise("max", rt.swizzle(freq, "x"), rt.f(1.0), width=1)
        freq_y = rt.component_wise("max", rt.swizzle(freq, "y"), rt.f(1.0), width=1)
        angle = rt.binary("*", rt.component_wise("cos", rt.binary("*", t, g.TAU, 1), width=1), speed_value, 1)
        sampleVec = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(coord, "x"), freq_x, 1), rt.swizzle(offset, "x"), 1), rt.binary("+", rt.binary("*", rt.swizzle(coord, "y"), freq_y, 1), rt.swizzle(offset, "y"), 1), rt.binary("+", angle, rt.swizzle(offset, "z"), 1))
        return simplex_noise__vec3(sampleVec)
    def compute_value_noise__vec2_vec2_float_float_vec3_vec3(coord, freq, t, speed_value, base_seed, time_seed):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        base_seed = rt.copy(base_seed)
        time_seed = rt.copy(time_seed)
        base_noise = compute_simplex_value__vec2_vec2_float_float_vec3(coord, freq, t, speed_value, base_seed)
        value = clamp01__float(rt.binary("+", rt.binary("*", base_noise, rt.f(0.5), 1), rt.f(0.5), 1))
        if rt.binary("&&", rt.binary("!=", speed_value, rt.f(0.0)), rt.binary("!=", t, rt.f(0.0))):
            time_noise_raw = compute_simplex_value__vec2_vec2_float_float_vec3(coord, freq, rt.f(0.0), rt.f(1.0), time_seed)
            time_value = clamp01__float(rt.binary("+", rt.binary("*", time_noise_raw, rt.f(0.5), 1), rt.f(0.5), 1))
            scaled_time = rt.binary("*", periodic_value__float_float(t, time_value), speed_value, 1)
            value = periodic_value__float_float(scaled_time, value)
        return clamp01__float(value)
    def compute_exponential_noise__vec2_vec2_float_float_vec3_vec3(coord, freq, t, speed_value, base_seed, time_seed):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        base_seed = rt.copy(base_seed)
        time_seed = rt.copy(time_seed)
        base = compute_value_noise__vec2_vec2_float_float_vec3_vec3(coord, freq, t, speed_value, base_seed, time_seed)
        return rt.component_wise("pow", base, rt.f(4.0), width=1)
    def wrap_coord__int_int(coord, limit):
        if rt.binary("<=", limit, rt.i(0)):
            return rt.i(0)
        wrapped = rt.binary("%", coord, limit, 1)
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, limit, 1)
        return wrapped
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
    def hashNoise__vec3(p):
        p = rt.copy(p)
        seed = cpu_uvec3__float_float_float(rt.component_wise("floatBitsToUint", rt.swizzle(p, "x"), width=1), rt.component_wise("floatBitsToUint", rt.swizzle(p, "y"), width=1), rt.component_wise("floatBitsToUint", rt.swizzle(p, "z"), width=1))
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__vec3(seed), "x")), rt.f(4294967295.0), 1)
    def valueNoise__vec3(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=3)
        f = rt.component_wise("fract", p, width=3)
        u = rt.binary("*", rt.binary("*", f, f, 3), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 3), 3), 3)
        c000 = hashNoise__vec3(i)
        c100 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(0.0)), 3))
        c010 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), 3))
        c110 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(0.0)), 3))
        c001 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0)), 3))
        c101 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(1.0)), 3))
        c011 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(1.0)), 3))
        c111 = hashNoise__vec3(rt.binary("+", i, rt.construct(3, rt.f(1.0), rt.f(1.0), rt.f(1.0)), 3))
        return rt.component_wise("mix", rt.component_wise("mix", rt.component_wise("mix", c000, c100, rt.swizzle(u, "x"), width=1), rt.component_wise("mix", c010, c110, rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1), rt.component_wise("mix", rt.component_wise("mix", c001, c101, rt.swizzle(u, "x"), width=1), rt.component_wise("mix", c011, c111, rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1), rt.swizzle(u, "z"), width=1)
    def vhs_computeNoise__vec2_vec2_float_float_vec3_vec3(coord, freq, t, spd, baseOff, timeOff):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        baseOff = rt.copy(baseOff)
        timeOff = rt.copy(timeOff)
        p = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(coord, "x"), rt.swizzle(freq, "x"), 1), rt.swizzle(baseOff, "x"), 1), rt.binary("+", rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(freq, "y"), 1), rt.swizzle(baseOff, "y"), 1), rt.binary("+", rt.binary("*", rt.component_wise("cos", rt.binary("*", t, g.TAU, 1), width=1), spd, 1), rt.swizzle(baseOff, "z"), 1))
        val = valueNoise__vec3(p)
        if rt.binary("&&", rt.binary("!=", spd, rt.f(0.0)), rt.binary("!=", t, rt.f(0.0))):
            tp = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(coord, "x"), rt.swizzle(freq, "x"), 1), rt.swizzle(timeOff, "x"), 1), rt.binary("+", rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(freq, "y"), 1), rt.swizzle(timeOff, "y"), 1), rt.swizzle(timeOff, "z"))
            timeVal = valueNoise__vec3(tp)
            scaledTime = rt.binary("*", periodic_value__float_float(t, timeVal), spd, 1)
            val = periodic_value__float_float(scaledTime, val)
        return rt.component_wise("clamp", val, rt.f(0.0), rt.f(1.0), width=1)
    def vhs_gradValue__float_float_float_float(yNorm, freqY, t, spd):
        base = vhs_computeNoise__vec2_vec2_float_float_vec3_vec3(rt.construct(2, rt.f(0.0), yNorm), rt.construct(2, rt.f(1.0), freqY), t, spd, rt.construct(3, rt.f(17.0), rt.f(29.0), rt.f(47.0)), rt.construct(3, rt.f(71.0), rt.f(113.0), rt.f(191.0)))
        g = rt.component_wise("max", rt.binary("-", base, rt.f(0.5), 1), rt.f(0.0), width=1)
        return rt.component_wise("min", rt.binary("*", g, rt.f(2.0), 1), rt.f(1.0), width=1)
    def vhs_scanNoise__vec2_vec2_float_float(coord, freq, t, spd):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        return vhs_computeNoise__vec2_vec2_float_float_vec3_vec3(coord, freq, t, spd, rt.construct(3, rt.f(37.0), rt.f(59.0), rt.f(83.0)), rt.construct(3, rt.f(131.0), rt.f(173.0), rt.f(211.0)))
    def main__void():
        gid = cpu_uvec3__float_float_float(rt.construct(1, rt.swizzle(ctx.frag_coord, "x")), rt.construct(1, rt.swizzle(ctx.frag_coord, "y")), rt.i(0))
        input_size = rt.texture_size(_u_inputTex)
        tile_width = rt.construct(1, rt.swizzle(input_size, "x"))
        tile_height = rt.construct(1, rt.swizzle(input_size, "y"))
        if rt.binary("||", rt.binary("==", tile_width, rt.i(0)), rt.binary("||", rt.binary("==", tile_height, rt.i(0)), rt.binary("||", rt.binary(">=", rt.swizzle(gid, "x"), tile_width), rt.binary(">=", rt.swizzle(gid, "y"), tile_height)))):
            g.fragColor = rt.construct(4, rt.f(0.0))
            return
        fullRes = (rt.binary("/", _u_fullResolution, _u_renderScale, 2) if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, input_size))
        width_f = rt.swizzle(fullRes, "x")
        height_f = rt.swizzle(fullRes, "y")
        dims = rt.construct(2, width_f, height_f)
        globalGid_f = rt.construct(2, rt.binary("+", rt.swizzle(gid, "x"), rt.swizzle(_u_tileOffset, "x"), 1), rt.binary("+", rt.swizzle(gid, "y"), rt.swizzle(_u_tileOffset, "y"), 1))
        globalGid = cpu_uvec2__float_float(rt.construct(1, rt.swizzle(globalGid_f, "x")), rt.construct(1, rt.swizzle(globalGid_f, "y")))
        time_value = rt.binary("+", _u_time, _u_timeOffset, 1)
        speed_value = rt.component_wise("max", _u_speed, rt.f(0.0), width=1)
        m = rt.construct(1, _u_mode)
        if rt.binary("==", m, rt.i(1)):
            yNorm = rt.binary("/", rt.binary("+", rt.swizzle(globalGid, "y"), rt.f(0.5), 1), rt.swizzle(_u_fullResolution, "y"), 1)
            xNorm = rt.binary("/", rt.binary("+", rt.swizzle(globalGid, "x"), rt.f(0.5), 1), rt.swizzle(_u_fullResolution, "x"), 1)
            destCoord = rt.construct(2, xNorm, yNorm)
            gradDest = vhs_gradValue__float_float_float_float(yNorm, rt.f(5.0), time_value, speed_value)
            scanBase = rt.binary("+", rt.component_wise("floor", rt.binary("*", height_f, rt.f(0.5), 1), width=1), rt.f(1.0), 1)
            scanFreq = rt.construct(2, 0.0)
            if rt.binary("<", height_f, width_f):
                scanFreq = rt.construct(2, rt.binary("*", scanBase, rt.binary("/", height_f, width_f, 1), 1), scanBase)
            else:
                scanFreq = rt.construct(2, scanBase, rt.binary("*", scanBase, rt.binary("/", width_f, height_f, 1), 1))
            scanDest = vhs_scanNoise__vec2_vec2_float_float(destCoord, scanFreq, time_value, rt.binary("*", speed_value, rt.f(100.0), 1))
            fullWidth = (rt.swizzle(_u_fullResolution, "x") if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else width_f)
            shiftAmount = rt.component_wise("floor", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", scanDest, fullWidth, 1), gradDest, 1), gradDest, 1), _u_distortion, 1), width=1)
            globalSampleX = rt.binary("-", rt.swizzle(globalGid, "x"), shiftAmount, 1)
            wrappedGlobalX = wrap_coord__int_int(rt.construct(1, globalSampleX), rt.construct(1, fullWidth))
            localSampleX = rt.binary("-", wrappedGlobalX, rt.construct(1, rt.swizzle(_u_tileOffset, "x")), 1)
            if rt.binary("<", localSampleX, rt.i(0)):
                localSampleX = rt.binary("+", localSampleX, rt.construct(1, tile_width), 1)
            localSampleX = rt.component_wise("clamp", localSampleX, rt.i(0), rt.binary("-", rt.construct(1, tile_width), rt.i(1), 1), width=1)
            srcTexel = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(localSampleX, rt.construct(1, rt.swizzle(gid, "y"))), rt.i(0))
            srcXNorm = rt.binary("/", rt.binary("+", wrappedGlobalX, rt.f(0.5), 1), rt.swizzle(_u_fullResolution, "x"), 1)
            scanSource = vhs_scanNoise__vec2_vec2_float_float(rt.construct(2, srcXNorm, yNorm), scanFreq, time_value, rt.binary("*", speed_value, rt.f(100.0), 1))
            gradSource = vhs_gradValue__float_float_float_float(yNorm, rt.f(5.0), time_value, speed_value)
            noiseColor = rt.construct(3, scanSource)
            blended = rt.component_wise("mix", rt.swizzle(srcTexel, "rgb"), noiseColor, rt.binary("*", gradSource, _u_noise, 1), width=3)
            g.fragColor = rt.construct(4, blended, rt.swizzle(srcTexel, "a"))
        else:
            base_coord = cpu_ivec2__float_float(rt.construct(1, rt.swizzle(gid, "x")), rt.construct(1, rt.swizzle(gid, "y")))
            input_texel = rt.texel_fetch(_u_inputTex, base_coord, rt.i(0))
            coord_norm = normalized_coord__vec2_vec2(globalGid, dims)
            freq_line = rt.construct(2, rt.component_wise("max", rt.component_wise("floor", rt.binary("*", width_f, rt.f(0.5), 1), width=1), rt.f(1.0), width=1), rt.component_wise("max", rt.component_wise("floor", rt.binary("*", height_f, rt.f(0.5), 1), width=1), rt.f(1.0), width=1))
            swerve_height = rt.component_wise("max", rt.component_wise("floor", rt.binary("*", height_f, rt.f(0.01), 1), width=1), rt.f(1.0), width=1)
            freq_swerve = rt.construct(2, rt.f(1.0), swerve_height)
            swerve_coord = rt.construct(2, rt.f(0.0), rt.swizzle(coord_norm, "y"))
            line_noise = compute_exponential_noise__vec2_vec2_float_float_vec3_vec3(coord_norm, freq_line, time_value, rt.binary("*", speed_value, rt.f(10.0), 1), g.BASE_SEED_LINE, g.TIME_SEED_LINE)
            line_noise = rt.binary("*", rt.component_wise("max", rt.binary("-", line_noise, rt.f(0.25), 1), rt.f(0.0), width=1), rt.f(2.0), 1)
            swerve_noise = compute_exponential_noise__vec2_vec2_float_float_vec3_vec3(swerve_coord, freq_swerve, time_value, speed_value, g.BASE_SEED_SWERVE, g.TIME_SEED_SWERVE)
            swerve_noise = rt.binary("*", rt.component_wise("max", rt.binary("-", swerve_noise, rt.f(0.25), 1), rt.f(0.0), width=1), rt.f(2.0), 1)
            line_weighted = rt.binary("*", line_noise, swerve_noise, 1)
            swerve_weight = rt.binary("*", swerve_noise, rt.f(2.0), 1)
            white_base = compute_value_noise__vec2_vec2_float_float_vec3_vec3(coord_norm, freq_line, time_value, rt.binary("*", speed_value, rt.f(100.0), 1), g.BASE_SEED_WHITE, g.TIME_SEED_WHITE)
            white_weighted = rt.binary("*", white_base, swerve_weight, 1)
            combined_error = clamp01__float(rt.binary("+", line_weighted, white_weighted, 1))
            fullWidth = (rt.swizzle(_u_fullResolution, "x") if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else width_f)
            shift_amount = rt.binary("*", rt.binary("*", rt.binary("*", combined_error, fullWidth, 1), rt.f(0.025), 1), _u_distortion, 1)
            shift_pixels = rt.construct(1, rt.component_wise("floor", shift_amount, width=1))
            globalSampleX = rt.binary("-", rt.swizzle(globalGid, "x"), shift_pixels, 1)
            wrappedGlobalX = wrap_coord__int_int(rt.construct(1, globalSampleX), rt.construct(1, fullWidth))
            localSampleX = rt.binary("-", wrappedGlobalX, rt.construct(1, rt.swizzle(_u_tileOffset, "x")), 1)
            if rt.binary("<", localSampleX, rt.i(0)):
                localSampleX = rt.binary("+", localSampleX, rt.construct(1, tile_width), 1)
            localSampleX = rt.component_wise("clamp", localSampleX, rt.i(0), rt.binary("-", rt.construct(1, tile_width), rt.i(1), 1), width=1)
            texel = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(localSampleX, rt.construct(1, rt.swizzle(gid, "y"))), rt.i(0))
            additive = rt.component_wise("clamp", rt.binary("*", rt.binary("*", rt.binary("*", line_weighted, white_weighted, 1), rt.f(4.0), 1), _u_noise, 1), rt.f(0.0), rt.f(4.0), width=1)
            boosted = rt.component_wise("clamp", rt.binary("+", rt.swizzle(texel, "rgb"), rt.construct(3, additive), 3), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
            g.fragColor = rt.construct(4, boosted, rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
