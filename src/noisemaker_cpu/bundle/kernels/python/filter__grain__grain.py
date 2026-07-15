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
    _u_renderScale = U["renderScale"]
    _u_alpha = U["alpha"]
    _u_time = U["time"]
    _u_pause = U["pause"]
    g.PI = rt.f(3.14159265358979323846)
    g.TAU = rt.f(6.28318530717958647692)
    g.UINT32_TO_FLOAT = rt.binary("/", rt.f(1.0), rt.f(4294967296.0), 1)
    g.CHANNEL_COUNT = rt.i(4)
    g.INTERPOLATION_CONSTANT = rt.i(0)
    g.INTERPOLATION_LINEAR = rt.i(1)
    g.INTERPOLATION_COSINE = rt.i(2)
    g.INTERPOLATION_BICUBIC = rt.i(3)
    g.BASE_SEED = rt.i(0x1234)
    def cpu_ivec3__float(value):
        return rt.construct(3, value)
    def cpu_ivec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_ivec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def cpu_uvec2__float(value):
        return rt.construct(2, value)
    def cpu_uvec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_uvec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_umul__int_int(left, right):
        return rt.binary("*", left, right, 1)
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1))
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def pcg3d__vec3(v_in):
        v_in = rt.copy(v_in)
        v = rt.binary("+", rt.binary("*", v_in, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, cpu_uvec3__float(rt.i(16)), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def random_from_cell_3d__ivec3_int(cell, seed):
        cell = rt.copy(cell)
        hashed = cpu_uvec3__float_float_float(rt.binary("^", rt.construct(1, rt.swizzle(cell, "x")), seed, 1), rt.binary("^", rt.construct(1, rt.swizzle(cell, "y")), rt.binary("+", cpu_umul__int_int(seed, rt.f(0x9e3779b9)), rt.i(0x7f4a7c15), 1), 1), rt.binary("^", rt.construct(1, rt.swizzle(cell, "z")), rt.binary("+", cpu_umul__int_int(seed, rt.f(0x632be59b)), rt.i(0x5bf03635), 1), 1))
        noise = pcg3d__vec3(hashed)
        return rt.binary("*", rt.swizzle(noise, "x"), g.UINT32_TO_FLOAT, 1)
    def periodic_value__float_float(time_value, sample_val):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.binary("-", time_value, sample_val, 1), g.TAU, 1), width=1), rt.f(1.0), 1), rt.f(0.5), 1)
    def interpolation_weight__float_int(value, spline_order):
        if rt.binary("==", spline_order, g.INTERPOLATION_COSINE):
            clamped = rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
            angle = rt.binary("*", clamped, g.PI, 1)
            cos_value = rt.component_wise("cos", angle, width=1)
            return rt.binary("*", rt.binary("-", rt.f(1.0), cos_value, 1), rt.f(0.5), 1)
        return value
    def blend_cubic__float_float_float_float_float(a, b, c, d, g):
        t = rt.component_wise("clamp", g, rt.f(0.0), rt.f(1.0), width=1)
        t2 = rt.binary("*", t, t, 1)
        a0 = rt.binary("+", rt.binary("-", rt.binary("-", d, c, 1), a, 1), b, 1)
        a1 = rt.binary("-", rt.binary("-", a, b, 1), a0, 1)
        a2 = rt.binary("-", c, a, 1)
        a3 = b
        term1 = rt.binary("*", rt.binary("*", a0, t, 1), t2, 1)
        term2 = rt.binary("*", a1, t2, 1)
        term3 = rt.binary("+", rt.binary("*", a2, t, 1), a3, 1)
        return rt.binary("+", rt.binary("+", term1, term2, 1), term3, 1)
    def sample_bicubic_layer__ivec2_vec2_int_int(cell, frac, z_cell, base_seed):
        cell = rt.copy(cell)
        frac = rt.copy(frac)
        row0 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), rt.swizzle(frac, "x"))
        row1 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1), z_cell), base_seed), rt.swizzle(frac, "x"))
        row2 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), z_cell), base_seed), rt.swizzle(frac, "x"))
        row3 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1), z_cell), base_seed), random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1), z_cell), base_seed), rt.swizzle(frac, "x"))
        return blend_cubic__float_float_float_float_float(row0, row1, row2, row3, rt.swizzle(frac, "y"))
    def sample_raw_value_noise__vec2_vec2_int_float_float_int(uv, freq, base_seed, time_value, speed_value, spline_order):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        scaled_freq = rt.component_wise("max", freq, rt.construct(2, rt.f(1.0), rt.f(1.0)), width=2)
        scaled_uv = rt.binary("*", uv, scaled_freq, 2)
        cell_f = rt.component_wise("floor", scaled_uv, width=2)
        cell = cpu_ivec2__float_float(rt.construct(1, rt.swizzle(cell_f, "x")), rt.construct(1, rt.swizzle(cell_f, "y")))
        frac = rt.component_wise("fract", scaled_uv, width=2)
        angle = rt.binary("*", time_value, g.TAU, 1)
        time_coord = rt.binary("*", rt.component_wise("cos", angle, width=1), speed_value, 1)
        time_floor = rt.component_wise("floor", time_coord, width=1)
        time_cell = rt.construct(1, time_floor)
        time_frac = rt.component_wise("fract", time_coord, width=1)
        if rt.binary("==", spline_order, g.INTERPOLATION_CONSTANT):
            return random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell), base_seed)
        if rt.binary("==", spline_order, g.INTERPOLATION_LINEAR):
            tl = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell), base_seed)
            tr = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.swizzle(cell, "y"), time_cell), base_seed)
            bl = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), time_cell), base_seed)
            br = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), time_cell), base_seed)
            weight_x = interpolation_weight__float_int(rt.swizzle(frac, "x"), spline_order)
            top = rt.component_wise("mix", tl, tr, weight_x, width=1)
            bottom = rt.component_wise("mix", bl, br, weight_x, width=1)
            weight_y = interpolation_weight__float_int(rt.swizzle(frac, "y"), spline_order)
            return rt.component_wise("mix", top, bottom, weight_y, width=1)
        if rt.binary("==", spline_order, g.INTERPOLATION_COSINE):
            weight_x = interpolation_weight__float_int(rt.swizzle(frac, "x"), spline_order)
            weight_y = interpolation_weight__float_int(rt.swizzle(frac, "y"), spline_order)
            tl = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell), base_seed)
            tr = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.swizzle(cell, "y"), time_cell), base_seed)
            bl = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), time_cell), base_seed)
            br = random_from_cell_3d__ivec3_int(cpu_ivec3__float_float_float(rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1), time_cell), base_seed)
            top = rt.component_wise("mix", tl, tr, weight_x, width=1)
            bottom = rt.component_wise("mix", bl, br, weight_x, width=1)
            return rt.component_wise("mix", top, bottom, weight_y, width=1)
        slice0 = sample_bicubic_layer__ivec2_vec2_int_int(cell, frac, rt.binary("-", time_cell, rt.i(1), 1), base_seed)
        slice1 = sample_bicubic_layer__ivec2_vec2_int_int(cell, frac, rt.binary("+", time_cell, rt.i(0), 1), base_seed)
        slice2 = sample_bicubic_layer__ivec2_vec2_int_int(cell, frac, rt.binary("+", time_cell, rt.i(1), 1), base_seed)
        slice3 = sample_bicubic_layer__ivec2_vec2_int_int(cell, frac, rt.binary("+", time_cell, rt.i(2), 1), base_seed)
        return blend_cubic__float_float_float_float_float(slice0, slice1, slice2, slice3, time_frac)
    def sample_value_noise__vec2_vec2_int_float_float_int(uv, freq, seed, time_value, speed_value, spline_order):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        base_seed = seed
        base_value = sample_raw_value_noise__vec2_vec2_int_float_float_int(uv, freq, base_seed, time_value, speed_value, spline_order)
        if rt.binary("||", rt.binary("==", speed_value, rt.f(0.0)), rt.binary("==", time_value, rt.f(0.0))):
            return base_value
        time_seed = rt.binary("+", base_seed, rt.f(0x9e3779b1), 1)
        time_field = sample_raw_value_noise__vec2_vec2_int_float_float_int(uv, freq, time_seed, rt.f(0.0), rt.f(1.0), spline_order)
        scaled_time = rt.binary("*", periodic_value__float_float(time_value, time_field), speed_value, 1)
        return periodic_value__float_float(scaled_time, base_value)
    def sample_grain_noise__vec2_vec2_float_float(pixel_coords, dims, time_value, speed_value):
        pixel_coords = rt.copy(pixel_coords)
        dims = rt.copy(dims)
        width = rt.component_wise("max", rt.swizzle(dims, "x"), rt.f(1.0), width=1)
        height = rt.component_wise("max", rt.swizzle(dims, "y"), rt.f(1.0), width=1)
        uv = rt.construct(2, rt.binary("/", rt.swizzle(pixel_coords, "x"), width, 1), rt.binary("/", rt.swizzle(pixel_coords, "y"), height, 1))
        freq = rt.construct(2, width, height)
        return sample_value_noise__vec2_vec2_int_float_float_int(uv, freq, g.BASE_SEED, time_value, speed_value, g.INTERPOLATION_BICUBIC)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        global_id = cpu_uvec3__float_float_float(rt.construct(1, rt.swizzle(ctx.frag_coord, "x")), rt.construct(1, rt.swizzle(ctx.frag_coord, "y")), rt.i(0))
        res = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        u_width = rt.component_wise("max", as_u32__float(rt.swizzle(res, "x")), rt.i(1), width=1)
        u_height = rt.component_wise("max", as_u32__float(rt.swizzle(res, "y")), rt.i(1), width=1)
        global_pixel = cpu_uvec2__float_float(rt.construct(1, rt.binary("+", rt.swizzle(ctx.frag_coord, "x"), rt.swizzle(_u_tileOffset, "x"), 1)), rt.construct(1, rt.binary("+", rt.swizzle(ctx.frag_coord, "y"), rt.swizzle(_u_tileOffset, "y"), 1)))
        if rt.binary("||", rt.binary(">=", rt.swizzle(global_pixel, "x"), u_width), rt.binary(">=", rt.swizzle(global_pixel, "y"), u_height)):
            return
        coords = cpu_ivec2__float_float(rt.construct(1, rt.swizzle(global_id, "x")), rt.construct(1, rt.swizzle(global_id, "y")))
        texel = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        blend_alpha = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", blend_alpha, rt.f(0.0)):
            g.fragColor = texel
            return
        effective_time = (rt.f(0.0) if rt.binary(">", _u_pause, rt.f(0.5)) else _u_time)
        rs = rt.component_wise("max", _u_renderScale, rt.f(1.0), width=1)
        noise_value = sample_grain_noise__vec2_vec2_float_float(global_pixel, rt.construct(2, rt.binary("/", u_width, rs, 1), rt.binary("/", u_height, rs, 1)), effective_time, rt.f(100.0))
        noise_rgb = rt.construct(3, noise_value)
        mixed_rgb = rt.component_wise("mix", rt.swizzle(texel, "rgb"), noise_rgb, blend_alpha, width=3)
        g.fragColor = rt.construct(4, clamp01__float(rt.swizzle(mixed_rgb, "x")), clamp01__float(rt.swizzle(mixed_rgb, "y")), clamp01__float(rt.swizzle(mixed_rgb, "z")), rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
