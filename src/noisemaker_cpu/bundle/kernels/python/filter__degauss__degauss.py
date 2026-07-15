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
    _u_seed = U["seed"]
    _u_direction = U["direction"]
    g.TAU = rt.f(6.28318530717958647692)
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
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", value, rt.f(0.0), width=1))
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def wrap_index__int_int(value, limit):
        if rt.binary("<=", limit, rt.i(0)):
            return rt.i(0)
        wrapped = rt.binary("%", value, limit, 1)
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, limit, 1)
        return wrapped
    def wrap_float__float_float(value, limit):
        if rt.binary("<=", limit, rt.f(0.0)):
            return rt.f(0.0)
        result = rt.binary("-", value, rt.binary("*", rt.component_wise("floor", rt.binary("/", value, limit, 1), width=1), limit, 1), 1)
        if rt.binary("<", result, rt.f(0.0)):
            result = rt.binary("+", result, limit, 1)
        return result
    def freq_for_shape__float_float_float(base_freq, width, height):
        if rt.binary("<=", base_freq, rt.f(0.0)):
            return rt.construct(2, rt.f(1.0), rt.f(1.0))
        if rt.binary("<", rt.component_wise("abs", rt.binary("-", width, height, 1), width=1), rt.f(1e-5)):
            return rt.construct(2, base_freq, base_freq)
        if rt.binary("&&", rt.binary("<", height, width), rt.binary(">", height, rt.f(0.0))):
            return rt.construct(2, base_freq, rt.binary("/", rt.binary("*", base_freq, width, 1), height, 1))
        if rt.binary(">", width, rt.f(0.0)):
            return rt.construct(2, rt.binary("/", rt.binary("*", base_freq, height, 1), width, 1), base_freq)
        return rt.construct(2, base_freq, base_freq)
    def normalized_sine__float(value):
        return rt.binary("+", rt.binary("*", rt.component_wise("sin", value, width=1), rt.f(0.5), 1), rt.f(0.5), 1)
    def periodic_value__float_float(time, value):
        return normalized_sine__float(rt.binary("*", rt.binary("-", time, value, 1), g.TAU, 1))
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
        C = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1))
        D = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        i0 = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.construct(3, rt.swizzle(C, "y"))), 3), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i0, 3), rt.dot(i0, rt.construct(3, rt.swizzle(C, "x"))), 3)
        step1 = rt.component_wise("step", rt.construct(3, rt.swizzle(x0, "y"), rt.swizzle(x0, "z"), rt.swizzle(x0, "x")), x0, width=3)
        l = rt.binary("-", rt.construct(3, rt.f(1.0)), step1, 3)
        i1 = rt.component_wise("min", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        i2 = rt.component_wise("max", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3), rt.construct(3, rt.swizzle(C, "x")), 3)
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3), rt.construct(3, rt.swizzle(C, "y")), 3)
        x3 = rt.binary("-", x0, rt.construct(3, rt.swizzle(D, "y")), 3)
        i = mod289_vec3__vec3(i0)
        p = permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.swizzle(i, "z"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "z"), rt.swizzle(i2, "z"), rt.f(1.0)), 4)), rt.swizzle(i, "y"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "y"), rt.swizzle(i2, "y"), rt.f(1.0)), 4)), rt.swizzle(i, "x"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "x"), rt.swizzle(i2, "x"), rt.f(1.0)), 4))
        n_ = rt.f(0.14285714285714285)
        ns = rt.binary("-", rt.binary("*", n_, rt.construct(3, rt.swizzle(D, "w"), rt.swizzle(D, "y"), rt.swizzle(D, "z")), 3), rt.construct(3, rt.swizzle(D, "x"), rt.swizzle(D, "z"), rt.swizzle(D, "x")), 3)
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
    def compute_noise_value__vec2_float_float_vec2_float_float_int(coord, width, height, freq, time, speed, channel):
        coord = rt.copy(coord)
        freq = rt.copy(freq)
        width_safe = rt.component_wise("max", width, rt.f(1.0), width=1)
        height_safe = rt.component_wise("max", height, rt.f(1.0), width=1)
        freq_x = rt.component_wise("max", rt.swizzle(freq, "y"), rt.f(1.0), width=1)
        freq_y = rt.component_wise("max", rt.swizzle(freq, "x"), rt.f(1.0), width=1)
        uv = rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(coord, "x"), width_safe, 1), freq_x, 1), rt.binary("*", rt.binary("/", rt.swizzle(coord, "y"), height_safe, 1), freq_y, 1))
        angle = rt.binary("*", time, g.TAU, 1)
        z_base = rt.binary("*", rt.component_wise("cos", angle, width=1), speed, 1)
        channel_offset = rt.binary("*", channel, rt.f(37.0), 1)
        seed_offset = rt.binary("*", _u_seed, rt.f(73.0), 1)
        base_seed = rt.construct(3, rt.binary("+", rt.binary("+", rt.f(17.0), channel_offset, 1), seed_offset, 1), rt.binary("+", rt.binary("+", rt.f(29.0), rt.binary("*", channel_offset, rt.f(1.3), 1), 1), rt.binary("*", seed_offset, rt.f(1.1), 1), 1), rt.binary("+", rt.binary("+", rt.f(47.0), rt.binary("*", channel_offset, rt.f(1.7), 1), 1), rt.binary("*", seed_offset, rt.f(0.7), 1), 1))
        base_noise = simplex_noise__vec3(rt.construct(3, rt.binary("+", rt.swizzle(uv, "x"), rt.swizzle(base_seed, "x"), 1), rt.binary("+", rt.swizzle(uv, "y"), rt.swizzle(base_seed, "y"), 1), rt.binary("+", z_base, rt.swizzle(base_seed, "z"), 1)))
        value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", base_noise, rt.f(0.5), 1), rt.f(0.5), 1), rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("&&", rt.binary("!=", speed, rt.f(0.0)), rt.binary("!=", time, rt.f(0.0))):
            time_seed = rt.construct(3, rt.binary("+", rt.swizzle(base_seed, "x"), rt.f(54.0), 1), rt.binary("+", rt.swizzle(base_seed, "y"), rt.f(82.0), 1), rt.binary("+", rt.swizzle(base_seed, "z"), rt.f(124.0), 1))
            time_noise = simplex_noise__vec3(rt.construct(3, rt.binary("+", rt.swizzle(uv, "x"), rt.swizzle(time_seed, "x"), 1), rt.binary("+", rt.swizzle(uv, "y"), rt.swizzle(time_seed, "y"), 1), rt.swizzle(time_seed, "z")))
            time_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", time_noise, rt.f(0.5), 1), rt.f(0.5), 1), rt.f(0.0), rt.f(1.0), width=1)
            scaled_time = rt.binary("*", periodic_value__float_float(time, time_value), speed, 1)
            value = clamp01__float(periodic_value__float_float(scaled_time, value))
        return clamp01__float(value)
    def singularity_mask__vec2_float_float(uv, width, height):
        uv = rt.copy(uv)
        if rt.binary("||", rt.binary("<=", width, rt.f(0.0)), rt.binary("<=", height, rt.f(0.0))):
            return rt.f(0.0)
        delta = rt.component_wise("abs", rt.binary("-", uv, rt.construct(2, rt.f(0.5), rt.f(0.5)), 2), width=2)
        aspect = rt.binary("/", width, height, 1)
        scaled = rt.construct(2, rt.binary("*", rt.swizzle(delta, "x"), aspect, 1), rt.swizzle(delta, "y"))
        max_radius = rt.length(rt.construct(2, rt.binary("*", aspect, rt.f(0.5), 1), rt.f(0.5)))
        if rt.binary("<=", max_radius, rt.f(0.0)):
            return rt.f(0.0)
        normalized = rt.component_wise("clamp", rt.binary("/", rt.length(scaled), max_radius, 1), rt.f(0.0), rt.f(1.0), width=1)
        masked = rt.component_wise("sqrt", normalized, width=1)
        return rt.component_wise("pow", masked, rt.f(5.0), width=1)
    def sample_bilinear__vec2_float_float(pos, width, height):
        pos = rt.copy(pos)
        width_f = rt.component_wise("max", width, rt.f(1.0), width=1)
        height_f = rt.component_wise("max", height, rt.f(1.0), width=1)
        wrapped_x = wrap_float__float_float(rt.swizzle(pos, "x"), width_f)
        wrapped_y = wrap_float__float_float(rt.swizzle(pos, "y"), height_f)
        x0 = rt.construct(1, rt.component_wise("floor", wrapped_x, width=1))
        y0 = rt.construct(1, rt.component_wise("floor", wrapped_y, width=1))
        width_i = rt.construct(1, rt.component_wise("max", width, rt.f(1.0), width=1))
        height_i = rt.construct(1, rt.component_wise("max", height, rt.f(1.0), width=1))
        if rt.binary("<", x0, rt.i(0)):
            x0 = rt.i(0)
        else:
            if rt.binary(">=", x0, width_i):
                x0 = rt.binary("-", width_i, rt.i(1), 1)
        if rt.binary("<", y0, rt.i(0)):
            y0 = rt.i(0)
        else:
            if rt.binary(">=", y0, height_i):
                y0 = rt.binary("-", height_i, rt.i(1), 1)
        x1 = wrap_index__int_int(rt.binary("+", x0, rt.i(1), 1), width_i)
        y1 = wrap_index__int_int(rt.binary("+", y0, rt.i(1), 1), height_i)
        fx = rt.component_wise("clamp", rt.binary("-", wrapped_x, x0, 1), rt.f(0.0), rt.f(1.0), width=1)
        fy = rt.component_wise("clamp", rt.binary("-", wrapped_y, y0, 1), rt.f(0.0), rt.f(1.0), width=1)
        tex00 = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(x0, y0), rt.i(0))
        tex10 = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(x1, y0), rt.i(0))
        tex01 = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(x0, y1), rt.i(0))
        tex11 = rt.texel_fetch(_u_inputTex, cpu_ivec2__float_float(x1, y1), rt.i(0))
        mix_x0 = rt.component_wise("mix", tex00, tex10, rt.construct(4, fx), width=4)
        mix_x1 = rt.component_wise("mix", tex01, tex11, rt.construct(4, fx), width=4)
        return rt.component_wise("mix", mix_x0, mix_x1, rt.construct(4, fy), width=4)
    def warped_channel_value__int_vec2_vec2_float_float_vec2_float_float_float_float(channel, coord, base_pos, width, height, freq, displacement, mask, time, speed):
        coord = rt.copy(coord)
        base_pos = rt.copy(base_pos)
        freq = rt.copy(freq)
        noise_value = compute_noise_value__vec2_float_float_vec2_float_float_int(coord, width, height, freq, time, speed, channel)
        centered = rt.binary("*", rt.binary("-", rt.binary("*", noise_value, rt.f(2.0), 1), rt.f(1.0), 1), mask, 1)
        angle = rt.binary("*", centered, g.TAU, 1)
        offset = rt.binary("*", rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), displacement, 2), rt.construct(2, rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y")), 2)
        dirRad = rt.binary("/", rt.binary("*", _u_direction, g.TAU, 1), rt.f(360.0), 1)
        dc = rt.component_wise("cos", dirRad, width=1)
        ds = rt.component_wise("sin", dirRad, width=1)
        offset = rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(offset, "x"), dc, 1), rt.binary("*", rt.swizzle(offset, "y"), ds, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(offset, "x"), ds, 1), rt.binary("*", rt.swizzle(offset, "y"), dc, 1), 1))
        sample_pos = rt.binary("+", base_pos, offset, 2)
        sampled = sample_bilinear__vec2_float_float(sample_pos, rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"))
        if rt.binary("==", channel, rt.i(0)):
            return rt.swizzle(sampled, "r")
        if rt.binary("==", channel, rt.i(1)):
            return rt.swizzle(sampled, "g")
        if rt.binary("==", channel, rt.i(2)):
            return rt.swizzle(sampled, "b")
        return rt.swizzle(sampled, "a")
    def main__void():
        global_id = cpu_uvec3__float_float_float(rt.construct(1, rt.swizzle(ctx.frag_coord, "x")), rt.construct(1, rt.swizzle(ctx.frag_coord, "y")), rt.i(0))
        width = as_u32__float(rt.swizzle(_u_resolution, "x"))
        height = as_u32__float(rt.swizzle(_u_resolution, "y"))
        if rt.binary("||", rt.binary(">=", rt.swizzle(global_id, "x"), width), rt.binary(">=", rt.swizzle(global_id, "y"), height)):
            return
        coords = rt.construct(2, rt.construct(1, rt.swizzle(global_id, "x")), rt.construct(1, rt.swizzle(global_id, "y")))
        original = rt.texel_fetch(_u_inputTex, cpu_ivec2__vec2(coords), rt.i(0))
        if rt.binary("==", _u_displacement, rt.f(0.0)):
            g.fragColor = original
            return
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        width_f = rt.swizzle(fullRes, "x")
        height_f = rt.swizzle(fullRes, "y")
        uv = rt.binary("/", rt.binary("+", rt.construct(2, rt.binary("+", rt.swizzle(global_id, "x"), rt.swizzle(_u_tileOffset, "x"), 1), rt.binary("+", rt.swizzle(global_id, "y"), rt.swizzle(_u_tileOffset, "y"), 1)), rt.construct(2, rt.f(0.5), rt.f(0.5)), 2), rt.construct(2, rt.component_wise("max", width_f, rt.f(1.0), width=1), rt.component_wise("max", height_f, rt.f(1.0), width=1)), 2)
        mask = singularity_mask__vec2_float_float(uv, width_f, height_f)
        if rt.binary("<=", mask, rt.f(0.0)):
            g.fragColor = original
            return
        renderScale = (rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.component_wise("max", rt.swizzle(_u_resolution, "x"), rt.f(1.0), width=1), 1) if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.f(1.0))
        isTiling = rt.binary(">", renderScale, rt.f(1.01))
        maxOffsetPixels = (rt.f(256.0) if isTiling else rt.component_wise("max", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), width=1))
        maxAllowedDisplacement = rt.binary("/", maxOffsetPixels, rt.component_wise("max", rt.swizzle(_u_resolution, "x"), rt.f(1.0), width=1), 1)
        clampedDisplacement = rt.component_wise("min", _u_displacement, maxAllowedDisplacement, width=1)
        freq = freq_for_shape__float_float_float(rt.f(2.0), width_f, height_f)
        base_pos = rt.construct(2, rt.swizzle(global_id, "x"), rt.swizzle(global_id, "y"))
        globalCoordVec = rt.binary("+", rt.construct(2, rt.swizzle(global_id, "x"), rt.swizzle(global_id, "y")), _u_tileOffset, 2)
        coord = cpu_uvec2__vec2(globalCoordVec)
        red = warped_channel_value__int_vec2_vec2_float_float_vec2_float_float_float_float(rt.i(0), coord, base_pos, width_f, height_f, freq, clampedDisplacement, mask, _u_time, _u_speed)
        green = warped_channel_value__int_vec2_vec2_float_float_vec2_float_float_float_float(rt.i(1), coord, base_pos, width_f, height_f, freq, clampedDisplacement, mask, _u_time, _u_speed)
        blue = warped_channel_value__int_vec2_vec2_float_float_vec2_float_float_float_float(rt.i(2), coord, base_pos, width_f, height_f, freq, clampedDisplacement, mask, _u_time, _u_speed)
        alpha = clamp01__float(rt.swizzle(original, "w"))
        g.fragColor = rt.construct(4, red, green, blue, alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
