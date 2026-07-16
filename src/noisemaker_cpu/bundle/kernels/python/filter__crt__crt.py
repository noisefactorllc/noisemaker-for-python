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
    _u_speed = U["speed"]
    _u_seed = U["seed"]
    _u_alpha = U["alpha"]
    _u_renderScale = U["renderScale"]
    g.PI = rt.f(3.141592653589793)
    g.TAU = rt.f(6.283185307179586)
    g.INV_THREE = rt.f(0.3333333333333333)
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", value, rt.f(0.0), width=1), base="uint")
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def random_scalar__float(seed):
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", seed, width=1), rt.f(43758.5453123), 1, "float"), width=1)
    def simplex_random__float_float(time, speed):
        angle = rt.binary("*", time, g.TAU, 1, "float")
        z = rt.binary("*", rt.component_wise("cos", angle, width=1), speed, 1, "float")
        w = rt.binary("*", rt.component_wise("sin", angle, width=1), speed, 1, "float")
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", z, rt.f(157.0), 1, "float"), rt.binary("*", w, rt.f(113.0), 1, "float"), 1, "float"), width=1), rt.f(43758.5453), 1, "float"), width=1)
    def freq_for_shape__float_float_float(base_freq, width, height):
        freq = rt.component_wise("max", base_freq, rt.f(1.0), width=1)
        width_safe = rt.component_wise("max", width, rt.f(1.0), width=1)
        height_safe = rt.component_wise("max", height, rt.f(1.0), width=1)
        if rt.binary("<", rt.component_wise("abs", rt.binary("-", width_safe, height_safe, 1, "float"), width=1), rt.f(1e-05)):
            return rt.construct(2, freq, freq)
        if rt.binary("<", height_safe, width_safe):
            scaled = rt.component_wise("floor", rt.binary("/", rt.binary("*", freq, width_safe, 1, "float"), height_safe, 1, "float"), width=1)
            return rt.construct(2, freq, rt.component_wise("max", scaled, rt.f(1.0), width=1))
        scaled = rt.component_wise("floor", rt.binary("/", rt.binary("*", freq, height_safe, 1, "float"), width_safe, 1, "float"), width=1)
        return rt.construct(2, rt.component_wise("max", scaled, rt.f(1.0), width=1), freq)
    def normalized_sine__float(value):
        return rt.binary("+", rt.binary("*", rt.component_wise("sin", value, width=1), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
    def periodic_value__float_float(time, value):
        return normalized_sine__float(rt.binary("*", rt.binary("-", time, value, 1, "float"), g.TAU, 1, "float"))
    def mod289_vec3__vec3(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod289_vec4__vec4(x):
        x = rt.copy(x)
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 4, "float"), width=4), rt.f(289.0), 4, "float"), 4, "float")
    def permute__vec4(x):
        x = rt.copy(x)
        return mod289_vec4__vec4(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 4, "float"), rt.f(1.0), 4, "float"), x, 4, "float"))
    def taylor_inv_sqrt__vec4(r):
        r = rt.copy(r)
        return rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), r, 4, "float"), 4, "float")
    def simplex_noise__vec3(v):
        v = rt.copy(v)
        C = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"))
        D = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        i0 = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.construct(3, rt.swizzle(C, "y"))), 3, "float"), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i0, 3, "float"), rt.dot(i0, rt.construct(3, rt.swizzle(C, "x"))), 3, "float")
        step1 = rt.component_wise("step", rt.construct(3, rt.swizzle(x0, "y"), rt.swizzle(x0, "z"), rt.swizzle(x0, "x")), x0, width=3)
        l = rt.binary("-", rt.construct(3, rt.f(1.0)), step1, 3, "float")
        i1 = rt.component_wise("min", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        i2 = rt.component_wise("max", step1, rt.construct(3, rt.swizzle(l, "z"), rt.swizzle(l, "x"), rt.swizzle(l, "y")), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3, "float"), rt.construct(3, rt.swizzle(C, "x")), 3, "float")
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3, "float"), rt.construct(3, rt.swizzle(C, "y")), 3, "float")
        x3 = rt.binary("-", x0, rt.construct(3, rt.swizzle(D, "y")), 3, "float")
        i = mod289_vec3__vec3(i0)
        p = permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.swizzle(i, "z"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "z"), rt.swizzle(i2, "z"), rt.f(1.0)), 4, "float")), rt.swizzle(i, "y"), 4, "float"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "y"), rt.swizzle(i2, "y"), rt.f(1.0)), 4, "float")), rt.swizzle(i, "x"), 4, "float"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "x"), rt.swizzle(i2, "x"), rt.f(1.0)), 4, "float"))
        n_ = rt.f(0.14285714285714285)
        ns = rt.binary("-", rt.binary("*", n_, rt.construct(3, rt.swizzle(D, "w"), rt.swizzle(D, "y"), rt.swizzle(D, "z")), 3, "float"), rt.construct(3, rt.swizzle(D, "x"), rt.swizzle(D, "z"), rt.swizzle(D, "x")), 3, "float")
        j = rt.binary("-", p, rt.binary("*", rt.f(49.0), rt.component_wise("floor", rt.binary("*", rt.binary("*", p, rt.swizzle(ns, "z"), 4, "float"), rt.swizzle(ns, "z"), 4, "float"), width=4), 4, "float"), 4, "float")
        x_ = rt.component_wise("floor", rt.binary("*", j, rt.swizzle(ns, "z"), 4, "float"), width=4)
        y_ = rt.component_wise("floor", rt.binary("-", j, rt.binary("*", rt.f(7.0), x_, 4, "float"), 4, "float"), width=4)
        x = rt.binary("+", rt.binary("*", x_, rt.swizzle(ns, "x"), 4, "float"), rt.swizzle(ns, "y"), 4, "float")
        y = rt.binary("+", rt.binary("*", y_, rt.swizzle(ns, "x"), 4, "float"), rt.swizzle(ns, "y"), 4, "float")
        h = rt.binary("-", rt.binary("-", rt.f(1.0), rt.component_wise("abs", x, width=4), 4, "float"), rt.component_wise("abs", y, width=4), 4, "float")
        b0 = rt.construct(4, rt.swizzle(x, "x"), rt.swizzle(x, "y"), rt.swizzle(y, "x"), rt.swizzle(y, "y"))
        b1 = rt.construct(4, rt.swizzle(x, "z"), rt.swizzle(x, "w"), rt.swizzle(y, "z"), rt.swizzle(y, "w"))
        s0 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b0, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        s1 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b1, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        sh = rt.unary("-", rt.component_wise("step", h, rt.construct(4, rt.f(0.0)), width=4))
        a0 = rt.binary("+", rt.construct(4, rt.swizzle(b0, "x"), rt.swizzle(b0, "z"), rt.swizzle(b0, "y"), rt.swizzle(b0, "w")), rt.binary("*", rt.construct(4, rt.swizzle(s0, "x"), rt.swizzle(s0, "z"), rt.swizzle(s0, "y"), rt.swizzle(s0, "w")), rt.construct(4, rt.swizzle(sh, "x"), rt.swizzle(sh, "x"), rt.swizzle(sh, "y"), rt.swizzle(sh, "y")), 4, "float"), 4, "float")
        a1 = rt.binary("+", rt.construct(4, rt.swizzle(b1, "x"), rt.swizzle(b1, "z"), rt.swizzle(b1, "y"), rt.swizzle(b1, "w")), rt.binary("*", rt.construct(4, rt.swizzle(s1, "x"), rt.swizzle(s1, "z"), rt.swizzle(s1, "y"), rt.swizzle(s1, "w")), rt.construct(4, rt.swizzle(sh, "z"), rt.swizzle(sh, "z"), rt.swizzle(sh, "w"), rt.swizzle(sh, "w")), 4, "float"), 4, "float")
        g0 = rt.construct(3, rt.swizzle(a0, "x"), rt.swizzle(a0, "y"), rt.swizzle(h, "x"))
        g1 = rt.construct(3, rt.swizzle(a0, "z"), rt.swizzle(a0, "w"), rt.swizzle(h, "y"))
        g2 = rt.construct(3, rt.swizzle(a1, "x"), rt.swizzle(a1, "y"), rt.swizzle(h, "z"))
        g3 = rt.construct(3, rt.swizzle(a1, "z"), rt.swizzle(a1, "w"), rt.swizzle(h, "w"))
        norm = taylor_inv_sqrt__vec4(rt.construct(4, rt.dot(g0, g0), rt.dot(g1, g1), rt.dot(g2, g2), rt.dot(g3, g3)))
        g0n = rt.binary("*", g0, rt.swizzle(norm, "x"), 3, "float")
        g1n = rt.binary("*", g1, rt.swizzle(norm, "y"), 3, "float")
        g2n = rt.binary("*", g2, rt.swizzle(norm, "z"), 3, "float")
        g3n = rt.binary("*", g3, rt.swizzle(norm, "w"), 3, "float")
        m0 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x0, x0), 1, "float"), rt.f(0.0), width=1)
        m1 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x1, x1), 1, "float"), rt.f(0.0), width=1)
        m2 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x2, x2), 1, "float"), rt.f(0.0), width=1)
        m3 = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.dot(x3, x3), 1, "float"), rt.f(0.0), width=1)
        m0sq = rt.binary("*", m0, m0, 1, "float")
        m1sq = rt.binary("*", m1, m1, 1, "float")
        m2sq = rt.binary("*", m2, m2, 1, "float")
        m3sq = rt.binary("*", m3, m3, 1, "float")
        return rt.binary("*", rt.f(42.0), rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", m0sq, m0sq, 1, "float"), rt.dot(g0n, x0), 1, "float"), rt.binary("*", rt.binary("*", m1sq, m1sq, 1, "float"), rt.dot(g1n, x1), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", m2sq, m2sq, 1, "float"), rt.dot(g2n, x2), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", m3sq, m3sq, 1, "float"), rt.dot(g3n, x3), 1, "float"), 1, "float"), 1, "float")
    def wrap_float__float_float(value, limit):
        if rt.binary("<=", limit, rt.f(0.0)):
            return rt.f(0.0)
        result = rt.binary("-", value, rt.binary("*", rt.component_wise("floor", rt.binary("/", value, limit, 1, "float"), width=1), limit, 1, "float"), 1, "float")
        if rt.binary("<", result, rt.f(0.0)):
            result = rt.binary("+", result, limit, 1, "float")
        return result
    def singularity_mask__vec2_float_float(uv, width, height):
        uv = rt.copy(uv)
        if (bool(rt.binary("<=", width, rt.f(0.0))) or bool(rt.binary("<=", height, rt.f(0.0)))):
            return rt.f(0.0)
        delta = rt.component_wise("abs", rt.binary("-", uv, rt.construct(2, rt.f(0.5), rt.f(0.5)), 2, "float"), width=2)
        aspect = rt.binary("/", width, height, 1, "float")
        scaled = rt.construct(2, rt.binary("*", rt.swizzle(delta, "x"), aspect, 1, "float"), rt.swizzle(delta, "y"))
        max_radius = rt.length(rt.construct(2, rt.binary("*", aspect, rt.f(0.5), 1, "float"), rt.f(0.5)))
        if rt.binary("<=", max_radius, rt.f(0.0)):
            return rt.f(0.0)
        normalized = rt.component_wise("clamp", rt.binary("/", rt.length(scaled), max_radius, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        masked = rt.component_wise("sqrt", normalized, width=1)
        return rt.component_wise("pow", masked, rt.f(5.0), width=1)
    def animated_simplex_value__vec2_float_float(uv, time, speed):
        uv = rt.copy(uv)
        angle = rt.binary("*", time, g.TAU, 1, "float")
        z_base = rt.binary("*", rt.component_wise("cos", angle, width=1), speed, 1, "float")
        s = rt.binary("*", rt.construct(1, _u_seed), rt.f(73.0), 1, "float")
        base_seed = rt.construct(3, rt.binary("+", rt.f(17.0), s, 1, "float"), rt.binary("+", rt.f(29.0), rt.binary("*", s, rt.f(1.1), 1, "float"), 1, "float"), rt.binary("+", rt.f(47.0), rt.binary("*", s, rt.f(0.7), 1, "float"), 1, "float"))
        base_noise = simplex_noise__vec3(rt.construct(3, rt.binary("+", rt.swizzle(uv, "x"), rt.swizzle(base_seed, "x"), 1, "float"), rt.binary("+", rt.swizzle(uv, "y"), rt.swizzle(base_seed, "y"), 1, "float"), rt.binary("+", z_base, rt.swizzle(base_seed, "z"), 1, "float")))
        value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", base_noise, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        if (bool(rt.binary("!=", speed, rt.f(0.0))) and bool(rt.binary("!=", time, rt.f(0.0)))):
            time_seed = rt.construct(3, rt.binary("+", rt.swizzle(base_seed, "x"), rt.f(54.0), 1, "float"), rt.binary("+", rt.swizzle(base_seed, "y"), rt.f(82.0), 1, "float"), rt.binary("+", rt.swizzle(base_seed, "z"), rt.f(124.0), 1, "float"))
            time_noise = simplex_noise__vec3(rt.construct(3, rt.binary("+", rt.swizzle(uv, "x"), rt.swizzle(time_seed, "x"), 1, "float"), rt.binary("+", rt.swizzle(uv, "y"), rt.swizzle(time_seed, "y"), 1, "float"), rt.swizzle(time_seed, "z")))
            time_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", time_noise, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
            scaled_time = rt.binary("*", periodic_value__float_float(time, time_value), speed, 1, "float")
            value = clamp01__float(periodic_value__float_float(scaled_time, value))
        return clamp01__float(value)
    def compute_lens_offsets__vec2_float_float_vec2_float_float_float(sample_pos, width, height, freq, time, speed, displacement):
        sample_pos = rt.copy(sample_pos)
        freq = rt.copy(freq)
        width_safe = rt.component_wise("max", width, rt.f(1.0), width=1)
        height_safe = rt.component_wise("max", height, rt.f(1.0), width=1)
        freq_x = rt.component_wise("max", rt.swizzle(freq, "y"), rt.f(1.0), width=1)
        freq_y = rt.component_wise("max", rt.swizzle(freq, "x"), rt.f(1.0), width=1)
        wrapped_pos = rt.construct(2, wrap_float__float_float(rt.swizzle(sample_pos, "x"), width_safe), wrap_float__float_float(rt.swizzle(sample_pos, "y"), height_safe))
        uv = rt.construct(2, rt.binary("*", rt.binary("/", rt.swizzle(wrapped_pos, "x"), width_safe, 1, "float"), freq_x, 1, "float"), rt.binary("*", rt.binary("/", rt.swizzle(wrapped_pos, "y"), height_safe, 1, "float"), freq_y, 1, "float"))
        noise_value = animated_simplex_value__vec2_float_float(uv, time, speed)
        uv_centered = rt.binary("/", rt.binary("+", wrapped_pos, rt.construct(2, rt.f(0.5), rt.f(0.5)), 2, "float"), rt.construct(2, width_safe, height_safe), 2, "float")
        mask = singularity_mask__vec2_float_float(uv_centered, width_safe, height_safe)
        distortion = rt.binary("*", rt.binary("-", rt.binary("*", noise_value, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), mask, 1, "float")
        angle = rt.binary("*", distortion, g.TAU, 1, "float")
        offsets = rt.binary("*", rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), displacement, 2, "float"), rt.construct(2, width_safe, height_safe), 2, "float")
        return offsets
    def fade__float(value):
        return rt.binary("*", rt.binary("*", value, value, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), value, 1, "float"), 1, "float"), 1, "float")
    def fade_vec3__vec3(v):
        v = rt.copy(v)
        return rt.construct(3, fade__float(rt.swizzle(v, "x")), fade__float(rt.swizzle(v, "y")), fade__float(rt.swizzle(v, "z")))
    def lerp__float_float_float(a, b, t):
        return rt.binary("+", a, rt.binary("*", rt.binary("-", b, a, 1, "float"), t, 1, "float"), 1, "float")
    def hash3__ivec3_float(coord, seed):
        coord = rt.copy(coord)
        base = rt.construct(3, coord)
        dot_value = rt.binary("+", rt.dot(base, rt.construct(3, rt.f(12.9898), rt.f(78.233), rt.f(37.719))), rt.binary("*", seed, rt.f(0.001), 1, "float"), 1, "float")
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("sin", dot_value, width=1), rt.f(43758.5453), 1, "float"), width=1)
    def value_noise_3d__vec3_float(coord, seed):
        coord = rt.copy(coord)
        cell = rt.construct(3, rt.component_wise("floor", coord, width=3))
        cell_i = rt.construct(3, cell, base="int")
        local = rt.component_wise("fract", coord, width=3)
        smooth_t = fade_vec3__vec3(local)
        c000 = hash3__ivec3_float(cell_i, seed)
        c100 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(1), rt.i(0), rt.i(0), base="int"), 3, "int"), seed)
        c010 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(0), rt.i(1), rt.i(0), base="int"), 3, "int"), seed)
        c110 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(1), rt.i(1), rt.i(0), base="int"), 3, "int"), seed)
        c001 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(0), rt.i(0), rt.i(1), base="int"), 3, "int"), seed)
        c101 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(1), rt.i(0), rt.i(1), base="int"), 3, "int"), seed)
        c011 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(0), rt.i(1), rt.i(1), base="int"), 3, "int"), seed)
        c111 = hash3__ivec3_float(rt.binary("+", cell_i, rt.construct(3, rt.i(1), rt.i(1), rt.i(1), base="int"), 3, "int"), seed)
        x00 = lerp__float_float_float(c000, c100, rt.swizzle(smooth_t, "x"))
        x10 = lerp__float_float_float(c010, c110, rt.swizzle(smooth_t, "x"))
        x01 = lerp__float_float_float(c001, c101, rt.swizzle(smooth_t, "x"))
        x11 = lerp__float_float_float(c011, c111, rt.swizzle(smooth_t, "x"))
        y0 = lerp__float_float_float(x00, x10, rt.swizzle(smooth_t, "y"))
        y1 = lerp__float_float_float(x01, x11, rt.swizzle(smooth_t, "y"))
        return lerp__float_float_float(y0, y1, rt.swizzle(smooth_t, "z"))
    def compute_singularity__float_float_float_float(x, y, width, height):
        center_x = rt.binary("*", width, rt.f(0.5), 1, "float")
        center_y = rt.binary("*", height, rt.f(0.5), 1, "float")
        dx = rt.binary("/", rt.binary("-", x, center_x, 1, "float"), width, 1, "float")
        dy = rt.binary("/", rt.binary("-", y, center_y, 1, "float"), height, 1, "float")
        return rt.length(rt.construct(2, dx, dy))
    def wrap_unit__float(value):
        wrapped = rt.binary("-", value, rt.component_wise("floor", value, width=1), 1, "float")
        if rt.binary("<", wrapped, rt.f(0.0)):
            wrapped = rt.binary("+", wrapped, rt.f(1.0), 1, "float")
        return wrapped
    def blend_linear__float_float_float(a, b, t):
        return rt.component_wise("mix", a, b, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=1)
    def blend_cosine__float_float_float(a, b, value):
        clamped = rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
        weight = rt.binary("*", rt.binary("-", rt.f(1.0), rt.component_wise("cos", rt.binary("*", clamped, g.PI, 1, "float"), width=1), 1, "float"), rt.f(0.5), 1, "float")
        return rt.component_wise("mix", a, b, weight, width=1)
    def clamp_index__float_float(value, max_index):
        if rt.binary("<=", max_index, rt.f(0.0)):
            return rt.i(0)
        clamped = rt.component_wise("clamp", value, rt.f(0.0), max_index, width=1)
        return rt.construct(1, clamped, base="uint")
    def rgb_to_hsv__vec3(rgb):
        rgb = rt.copy(rgb)
        c_max = rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "x"), rt.swizzle(rgb, "y"), width=1), rt.swizzle(rgb, "z"), width=1)
        c_min = rt.component_wise("min", rt.component_wise("min", rt.swizzle(rgb, "x"), rt.swizzle(rgb, "y"), width=1), rt.swizzle(rgb, "z"), width=1)
        delta = rt.binary("-", c_max, c_min, 1, "float")
        hue = rt.f(0.0)
        if rt.binary(">", delta, rt.f(0.0)):
            if rt.binary("==", c_max, rt.swizzle(rgb, "x")):
                segment = rt.binary("/", rt.binary("-", rt.swizzle(rgb, "y"), rt.swizzle(rgb, "z"), 1, "float"), delta, 1, "float")
                if rt.binary("<", segment, rt.f(0.0)):
                    segment = rt.binary("+", segment, rt.f(6.0), 1, "float")
                hue = segment
            else:
                if rt.binary("==", c_max, rt.swizzle(rgb, "y")):
                    hue = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "z"), rt.swizzle(rgb, "x"), 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float")
                else:
                    hue = rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "x"), rt.swizzle(rgb, "y"), 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float")
            hue = wrap_unit__float(rt.binary("/", hue, rt.f(6.0), 1, "float"))
        saturation = (rt.binary("/", delta, c_max, 1, "float") if rt.binary("!=", c_max, rt.f(0.0)) else rt.f(0.0))
        return rt.construct(3, hue, saturation, c_max)
    def hsv_to_rgb__vec3(hsv):
        hsv = rt.copy(hsv)
        h = rt.swizzle(hsv, "x")
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        dh = rt.binary("*", h, rt.f(6.0), 1, "float")
        r_comp = clamp01__float(rt.binary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(3.0), 1, "float"), width=1), rt.f(1.0), 1, "float"))
        g_comp = clamp01__float(rt.binary("+", rt.unary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(2.0), 1, "float"), width=1)), rt.f(2.0), 1, "float"))
        b_comp = clamp01__float(rt.binary("+", rt.unary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(4.0), 1, "float"), width=1)), rt.f(2.0), 1, "float"))
        one_minus_s = rt.binary("-", rt.f(1.0), s, 1, "float")
        sr = rt.binary("*", s, r_comp, 1, "float")
        sg = rt.binary("*", s, g_comp, 1, "float")
        sb = rt.binary("*", s, b_comp, 1, "float")
        r = clamp01__float(rt.binary("*", rt.binary("+", one_minus_s, sr, 1, "float"), v, 1, "float"))
        _g = clamp01__float(rt.binary("*", rt.binary("+", one_minus_s, sg, 1, "float"), v, 1, "float"))
        b = clamp01__float(rt.binary("*", rt.binary("+", one_minus_s, sb, 1, "float"), v, 1, "float"))
        return rt.construct(3, r, _g, b)
    def adjust_hue__vec3_float(color, amount):
        color = rt.copy(color)
        hsv = rgb_to_hsv__vec3(color)
        hsv = rt.assign_swizzle(hsv, "x", wrap_unit__float(rt.binary("+", rt.swizzle(hsv, "x"), amount, 1, "float")))
        hsv = rt.assign_swizzle(hsv, "y", clamp01__float(rt.swizzle(hsv, "y")))
        hsv = rt.assign_swizzle(hsv, "z", clamp01__float(rt.swizzle(hsv, "z")))
        return rt.component_wise("clamp", rt.construct(3, hsv_to_rgb__vec3(hsv)), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
    def adjust_saturation__vec3_float(color, amount):
        color = rt.copy(color)
        hsv = rgb_to_hsv__vec3(color)
        hsv = rt.assign_swizzle(hsv, "y", clamp01__float(rt.binary("*", rt.swizzle(hsv, "y"), amount, 1, "float")))
        hsv = rt.assign_swizzle(hsv, "z", clamp01__float(rt.swizzle(hsv, "z")))
        return rt.component_wise("clamp", rt.construct(3, hsv_to_rgb__vec3(hsv)), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
    def apply_vignette__float_float_float_float(value, brightness, mask, alpha):
        edge_mix = rt.component_wise("mix", value, brightness, mask, width=1)
        return rt.component_wise("mix", value, edge_mix, rt.component_wise("clamp", alpha, rt.f(0.0), rt.f(1.0), width=1), width=1)
    def get_scanline_base_values__float_float(time, speed):
        time_scaled = rt.binary("*", rt.binary("*", time, speed, 1, "float"), rt.f(0.1), 1, "float")
        noise_seed = rt.binary("+", rt.f(19.37), rt.binary("*", rt.construct(1, _u_seed), rt.f(31.0), 1, "float"), 1, "float")
        noise0 = value_noise_3d__vec3_float(rt.construct(3, rt.f(0.0), rt.f(0.0), time_scaled), noise_seed)
        noise1 = value_noise_3d__vec3_float(rt.construct(3, rt.f(1.0), rt.f(0.0), time_scaled), noise_seed)
        return rt.construct(2, noise0, noise1)
    def get_scanline_value_interpolated__float_float_vec2_float(y, height, base_values, pixels_per_bar):
        base_values = rt.copy(base_values)
        y_scaled = rt.binary("/", y, pixels_per_bar, 1, "float")
        scanline_index = rt.binary("%", rt.construct(1, rt.component_wise("floor", y_scaled, width=1), base="int"), rt.i(2), 1, "int")
        return (rt.swizzle(base_values, "x") if rt.binary("==", scanline_index, rt.i(0)) else rt.swizzle(base_values, "y"))
    def sample_scanline_bilinear__float_float_float_float_vec2_float(sample_x, sample_y, width, height, base_values, pixels_per_bar):
        base_values = rt.copy(base_values)
        wrapped_x = rt.binary("-", sample_x, rt.binary("*", rt.component_wise("floor", rt.binary("/", sample_x, width, 1, "float"), width=1), width, 1, "float"), 1, "float")
        wrapped_y = rt.binary("-", sample_y, rt.binary("*", rt.component_wise("floor", rt.binary("/", sample_y, height, 1, "float"), width=1), height, 1, "float"), 1, "float")
        if rt.binary("<", wrapped_x, rt.f(0.0)):
            wrapped_x = rt.binary("+", wrapped_x, width, 1, "float")
        if rt.binary("<", wrapped_y, rt.f(0.0)):
            wrapped_y = rt.binary("+", wrapped_y, height, 1, "float")
        wrapped_x = rt.component_wise("clamp", wrapped_x, rt.f(0.0), rt.binary("-", width, rt.f(1.0), 1, "float"), width=1)
        wrapped_y = rt.component_wise("clamp", wrapped_y, rt.f(0.0), rt.binary("-", height, rt.f(1.0), 1, "float"), width=1)
        x0 = rt.component_wise("floor", wrapped_x, width=1)
        y0 = rt.component_wise("floor", wrapped_y, width=1)
        x1 = rt.component_wise("min", rt.binary("+", x0, rt.f(1.0), 1, "float"), rt.binary("-", width, rt.f(1.0), 1, "float"), width=1)
        y1 = rt.component_wise("min", rt.binary("+", y0, rt.f(1.0), 1, "float"), rt.binary("-", height, rt.f(1.0), 1, "float"), width=1)
        x_fract = rt.component_wise("clamp", rt.binary("-", wrapped_x, x0, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        y_fract = rt.component_wise("clamp", rt.binary("-", wrapped_y, y0, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        val_x0_y0 = get_scanline_value_interpolated__float_float_vec2_float(y0, height, base_values, pixels_per_bar)
        val_x1_y0 = get_scanline_value_interpolated__float_float_vec2_float(y0, height, base_values, pixels_per_bar)
        val_x0_y1 = get_scanline_value_interpolated__float_float_vec2_float(y1, height, base_values, pixels_per_bar)
        val_x1_y1 = get_scanline_value_interpolated__float_float_vec2_float(y1, height, base_values, pixels_per_bar)
        val_y0 = rt.component_wise("mix", val_x0_y0, val_x1_y0, x_fract, width=1)
        val_y1 = rt.component_wise("mix", val_x0_y1, val_x1_y1, x_fract, width=1)
        return rt.component_wise("mix", val_y0, val_y1, y_fract, width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        global_id = rt.construct(3, rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="uint"), rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="uint"), rt.i(0), base="uint")
        width = as_u32__float(rt.swizzle(_u_resolution, "x"))
        height = as_u32__float(rt.swizzle(_u_resolution, "y"))
        if (bool(rt.binary(">=", rt.swizzle(global_id, "x"), width)) or bool(rt.binary(">=", rt.swizzle(global_id, "y"), height))):
            return
        alphaVal = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("==", alphaVal, rt.f(0.0)):
            g.fragColor = rt.texel_fetch(_u_inputTex, rt.construct(2, rt.construct(1, rt.swizzle(global_id, "x"), base="int"), rt.construct(1, rt.swizzle(global_id, "y"), base="int"), base="int"), rt.i(0))
            return
        rs = rt.component_wise("max", _u_renderScale, rt.f(1.0), width=1)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        width_f = rt.component_wise("max", rt.binary("/", rt.swizzle(fullRes, "x"), rs, 1, "float"), rt.f(1.0), width=1)
        height_f = rt.component_wise("max", rt.binary("/", rt.swizzle(fullRes, "y"), rs, 1, "float"), rt.f(1.0), width=1)
        time = _u_time
        speed = _u_speed
        x = rt.binary("/", rt.binary("+", rt.construct(1, rt.swizzle(global_id, "x")), rt.swizzle(_u_tileOffset, "x"), 1, "float"), rs, 1, "float")
        y = rt.binary("/", rt.binary("+", rt.construct(1, rt.swizzle(global_id, "y")), rt.swizzle(_u_tileOffset, "y"), 1, "float"), rs, 1, "float")
        displacement = rt.f(0.0625)
        freq = freq_for_shape__float_float_float(rt.f(2.0), width_f, height_f)
        base_offsets = compute_lens_offsets__vec2_float_float_vec2_float_float_float(rt.construct(2, x, y), width_f, height_f, freq, time, speed, displacement)
        scanline_base = get_scanline_base_values__float_float(time, speed)
        ppb = rt.f(2.5)
        scan_value = sample_scanline_bilinear__float_float_float_float_vec2_float(rt.binary("+", x, rt.swizzle(base_offsets, "x"), 1, "float"), rt.binary("+", y, rt.swizzle(base_offsets, "y"), 1, "float"), width_f, height_f, scanline_base, ppb)
        base_sample = rt.texel_fetch(_u_inputTex, rt.construct(2, rt.swizzle(global_id, "xy"), base="int"), rt.i(0))
        base_color = rt.swizzle(base_sample, "xyz")
        alpha = rt.swizzle(base_sample, "w")
        color = rt.component_wise("mix", base_color, rt.binary("*", rt.binary("+", base_color, scan_value, 3, "float"), scan_value, 3, "float"), rt.f(0.5), width=3)
        color = rt.component_wise("clamp", color, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        if rt.binary(">=", rt.f(4.0), rt.f(2.5)):
            seed_base = rt.binary("+", rt.f(17.0), rt.binary("*", rt.construct(1, _u_seed), rt.f(73.0), 1, "float"), 1, "float")
            displacement_base = rt.binary("+", rt.f(0.0125), rt.binary("*", random_scalar__float(rt.binary("+", seed_base, rt.f(0.37), 1, "float")), rt.f(0.00625), 1, "float"), 1, "float")
            simplex_value = random_scalar__float(rt.binary("+", seed_base, rt.f(0.73), 1, "float"))
            displacement_pixels = rt.binary("*", rt.binary("*", displacement_base, width_f, 1, "float"), simplex_value, 1, "float")
            singularity = compute_singularity__float_float_float_float(x, y, width_f, height_f)
            aber_mask = rt.component_wise("pow", singularity, rt.f(3.0), width=1)
            gradient = rt.component_wise("clamp", rt.binary("/", x, rt.binary("-", width_f, rt.f(1.0), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
            hue_shift = rt.binary("-", rt.binary("*", random_scalar__float(rt.binary("+", seed_base, rt.f(1.91), 1, "float")), rt.f(0.25), 1, "float"), rt.f(0.125), 1, "float")
            red_x = rt.component_wise("min", rt.binary("+", x, displacement_pixels, 1, "float"), rt.binary("-", width_f, rt.f(1.0), 1, "float"), width=1)
            red_x = blend_linear__float_float_float(red_x, x, gradient)
            red_sample_x = blend_cosine__float_float_float(x, red_x, aber_mask)
            red_sample_global_x = rt.binary("*", red_sample_x, _u_renderScale, 1, "float")
            red_sample_local_x = rt.binary("-", red_sample_global_x, rt.swizzle(_u_tileOffset, "x"), 1, "float")
            red_base_col = rt.swizzle(rt.texel_fetch(_u_inputTex, rt.construct(2, rt.construct(1, red_sample_local_x, base="int"), rt.construct(1, rt.swizzle(global_id, "y"), base="int"), base="int"), rt.i(0)), "xyz")
            red_offsets = compute_lens_offsets__vec2_float_float_vec2_float_float_float(rt.construct(2, red_sample_x, y), width_f, height_f, freq, time, speed, displacement)
            red_scan_val = sample_scanline_bilinear__float_float_float_float_vec2_float(rt.binary("+", red_sample_x, rt.swizzle(red_offsets, "x"), 1, "float"), rt.binary("+", y, rt.swizzle(red_offsets, "y"), 1, "float"), width_f, height_f, scanline_base, ppb)
            red_blended = rt.component_wise("mix", red_base_col, rt.binary("*", rt.binary("+", red_base_col, red_scan_val, 3, "float"), red_scan_val, 3, "float"), rt.f(0.5), width=3)
            green_blended = color
            blue_x = rt.component_wise("max", rt.binary("-", x, displacement_pixels, 1, "float"), rt.f(0.0), width=1)
            blue_x = blend_linear__float_float_float(x, blue_x, gradient)
            blue_sample_x = blend_cosine__float_float_float(x, blue_x, aber_mask)
            blue_sample_global_x = rt.binary("*", blue_sample_x, _u_renderScale, 1, "float")
            blue_sample_local_x = rt.binary("-", blue_sample_global_x, rt.swizzle(_u_tileOffset, "x"), 1, "float")
            blue_base_col = rt.swizzle(rt.texel_fetch(_u_inputTex, rt.construct(2, rt.construct(1, blue_sample_local_x, base="int"), rt.construct(1, rt.swizzle(global_id, "y"), base="int"), base="int"), rt.i(0)), "xyz")
            blue_offsets = compute_lens_offsets__vec2_float_float_vec2_float_float_float(rt.construct(2, blue_sample_x, y), width_f, height_f, freq, time, speed, displacement)
            blue_scan_val = sample_scanline_bilinear__float_float_float_float_vec2_float(rt.binary("+", blue_sample_x, rt.swizzle(blue_offsets, "x"), 1, "float"), rt.binary("+", y, rt.swizzle(blue_offsets, "y"), 1, "float"), width_f, height_f, scanline_base, ppb)
            blue_blended = rt.component_wise("mix", blue_base_col, rt.binary("*", rt.binary("+", blue_base_col, blue_scan_val, 3, "float"), blue_scan_val, 3, "float"), rt.f(0.5), width=3)
            color = rt.construct(3, rt.swizzle(adjust_hue__vec3_float(red_blended, hue_shift), "r"), rt.swizzle(adjust_hue__vec3_float(green_blended, hue_shift), "g"), rt.swizzle(adjust_hue__vec3_float(blue_blended, hue_shift), "b"))
            color = adjust_hue__vec3_float(color, rt.unary("-", hue_shift))
            color = adjust_saturation__vec3_float(color, rt.f(1.125))
            vignette_alpha = rt.binary("*", random_scalar__float(rt.binary("+", seed_base, rt.f(3.17), 1, "float")), rt.f(0.175), 1, "float")
            vignette_mask = singularity
            color = rt.assign_swizzle(color, "x", apply_vignette__float_float_float_float(rt.swizzle(color, "x"), rt.f(0.0), vignette_mask, vignette_alpha))
            color = rt.assign_swizzle(color, "y", apply_vignette__float_float_float_float(rt.swizzle(color, "y"), rt.f(0.0), vignette_mask, vignette_alpha))
            color = rt.assign_swizzle(color, "z", apply_vignette__float_float_float_float(rt.swizzle(color, "z"), rt.f(0.0), vignette_mask, vignette_alpha))
        local_mean = rt.binary("*", rt.binary("+", rt.binary("+", rt.swizzle(color, "x"), rt.swizzle(color, "y"), 1, "float"), rt.swizzle(color, "z"), 1, "float"), g.INV_THREE, 1, "float")
        color = rt.component_wise("clamp", rt.binary("+", rt.binary("*", rt.binary("-", color, local_mean, 3, "float"), rt.f(1.25), 3, "float"), local_mean, 3, "float"), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        color = rt.component_wise("mix", base_color, color, alphaVal, width=3)
        g.fragColor = rt.construct(4, color, rt.swizzle(base_sample, "w"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
