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
    g.PI = rt.f(3.141592653589793)
    g.TAU = rt.f(6.283185307179586)
    g.UINT32_TO_FLOAT = rt.binary("/", rt.f(1.0), rt.f(4294967296.0), 1, "float")
    g.CHANNEL_COUNT = rt.i(4)
    g.INTERPOLATION_CONSTANT = rt.i(0)
    g.INTERPOLATION_LINEAR = rt.i(1)
    g.INTERPOLATION_COSINE = rt.i(2)
    g.INTERPOLATION_BICUBIC = rt.i(3)
    g.BASE_SEED = rt.i(4660)
    g.fragColor = rt.construct(4, 0.0)
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1), base="uint")
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def pcg3d__uvec3(v_in):
        v_in = rt.copy(v_in)
        v = rt.binary("+", rt.binary("*", v_in, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def random_from_cell_3d__ivec3_uint(cell, seed):
        cell = rt.copy(cell)
        hashed = rt.construct(3, rt.binary("^", rt.construct(1, rt.swizzle(cell, "x"), base="uint"), seed, 1, "uint"), rt.binary("^", rt.construct(1, rt.swizzle(cell, "y"), base="uint"), rt.binary("+", rt.binary("*", seed, rt.i(2654435769), 1, "uint"), rt.i(2135587861), 1, "uint"), 1, "uint"), rt.binary("^", rt.construct(1, rt.swizzle(cell, "z"), base="uint"), rt.binary("+", rt.binary("*", seed, rt.i(1663821211), 1, "uint"), rt.i(1542469173), 1, "uint"), 1, "uint"), base="uint")
        noise = rt.pcg3d(hashed)
        return rt.binary("*", rt.construct(1, rt.swizzle(noise, "x")), g.UINT32_TO_FLOAT, 1, "float")
    def periodic_value__float_float(time_value, sample_val):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", rt.binary("-", time_value, sample_val, 1, "float"), g.TAU, 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float")
    def interpolation_weight__float_uint(value, spline_order):
        if rt.binary("==", spline_order, g.INTERPOLATION_COSINE):
            clamped = rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
            angle = rt.binary("*", clamped, g.PI, 1, "float")
            cos_value = rt.component_wise("cos", angle, width=1)
            return rt.binary("*", rt.binary("-", rt.f(1.0), cos_value, 1, "float"), rt.f(0.5), 1, "float")
        return value
    def blend_cubic__float_float_float_float_float(a, b, c, d, _g):
        t = rt.component_wise("clamp", _g, rt.f(0.0), rt.f(1.0), width=1)
        t2 = rt.binary("*", t, t, 1, "float")
        a0 = rt.binary("+", rt.binary("-", rt.binary("-", d, c, 1, "float"), a, 1, "float"), b, 1, "float")
        a1 = rt.binary("-", rt.binary("-", a, b, 1, "float"), a0, 1, "float")
        a2 = rt.binary("-", c, a, 1, "float")
        a3 = b
        term1 = rt.binary("*", rt.binary("*", a0, t, 1, "float"), t2, 1, "float")
        term2 = rt.binary("*", a1, t2, 1, "float")
        term3 = rt.binary("+", rt.binary("*", a2, t, 1, "float"), a3, 1, "float")
        return rt.binary("+", rt.binary("+", term1, term2, 1, "float"), term3, 1, "float")
    def sample_bicubic_layer__ivec2_vec2_int_uint(cell, frac, z_cell, base_seed):
        cell = rt.copy(cell)
        frac = rt.copy(frac)
        row0 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1, "int"), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1, "int"), rt.binary("-", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), rt.swizzle(frac, "x"))
        row1 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(0), 1, "int"), z_cell, base="int"), base_seed), rt.swizzle(frac, "x"))
        row2 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), z_cell, base="int"), base_seed), rt.swizzle(frac, "x"))
        row3 = blend_cubic__float_float_float_float_float(random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("-", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(0), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1, "int"), z_cell, base="int"), base_seed), random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(2), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(2), 1, "int"), z_cell, base="int"), base_seed), rt.swizzle(frac, "x"))
        return blend_cubic__float_float_float_float_float(row0, row1, row2, row3, rt.swizzle(frac, "y"))
    def sample_raw_value_noise__vec2_vec2_uint_float_float_uint(uv, freq, base_seed, time_value, speed_value, spline_order):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        scaled_freq = rt.component_wise("max", freq, rt.construct(2, rt.f(1.0), rt.f(1.0)), width=2)
        scaled_uv = rt.binary("*", uv, scaled_freq, 2, "float")
        cell_f = rt.component_wise("floor", scaled_uv, width=2)
        cell = rt.construct(2, rt.construct(1, rt.swizzle(cell_f, "x"), base="int"), rt.construct(1, rt.swizzle(cell_f, "y"), base="int"), base="int")
        frac = rt.component_wise("fract", scaled_uv, width=2)
        angle = rt.binary("*", time_value, g.TAU, 1, "float")
        time_coord = rt.binary("*", rt.component_wise("cos", angle, width=1), speed_value, 1, "float")
        time_floor = rt.component_wise("floor", time_coord, width=1)
        time_cell = rt.construct(1, time_floor, base="int")
        time_frac = rt.component_wise("fract", time_coord, width=1)
        if rt.binary("==", spline_order, g.INTERPOLATION_CONSTANT):
            return random_from_cell_3d__ivec3_uint(rt.construct(3, rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell, base="int"), base_seed)
        if rt.binary("==", spline_order, g.INTERPOLATION_LINEAR):
            tl = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell, base="int"), base_seed)
            tr = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.swizzle(cell, "y"), time_cell, base="int"), base_seed)
            bl = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), time_cell, base="int"), base_seed)
            br = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), time_cell, base="int"), base_seed)
            weight_x = interpolation_weight__float_uint(rt.swizzle(frac, "x"), spline_order)
            top = rt.component_wise("mix", tl, tr, weight_x, width=1)
            bottom = rt.component_wise("mix", bl, br, weight_x, width=1)
            weight_y = interpolation_weight__float_uint(rt.swizzle(frac, "y"), spline_order)
            return rt.component_wise("mix", top, bottom, weight_y, width=1)
        if rt.binary("==", spline_order, g.INTERPOLATION_COSINE):
            weight_x = interpolation_weight__float_uint(rt.swizzle(frac, "x"), spline_order)
            weight_y = interpolation_weight__float_uint(rt.swizzle(frac, "y"), spline_order)
            tl = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), time_cell, base="int"), base_seed)
            tr = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.swizzle(cell, "y"), time_cell, base="int"), base_seed)
            bl = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.swizzle(cell, "x"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), time_cell, base="int"), base_seed)
            br = random_from_cell_3d__ivec3_uint(rt.construct(3, rt.binary("+", rt.swizzle(cell, "x"), rt.i(1), 1, "int"), rt.binary("+", rt.swizzle(cell, "y"), rt.i(1), 1, "int"), time_cell, base="int"), base_seed)
            top = rt.component_wise("mix", tl, tr, weight_x, width=1)
            bottom = rt.component_wise("mix", bl, br, weight_x, width=1)
            return rt.component_wise("mix", top, bottom, weight_y, width=1)
        slice0 = sample_bicubic_layer__ivec2_vec2_int_uint(cell, frac, rt.binary("-", time_cell, rt.i(1), 1, "int"), base_seed)
        slice1 = sample_bicubic_layer__ivec2_vec2_int_uint(cell, frac, rt.binary("+", time_cell, rt.i(0), 1, "int"), base_seed)
        slice2 = sample_bicubic_layer__ivec2_vec2_int_uint(cell, frac, rt.binary("+", time_cell, rt.i(1), 1, "int"), base_seed)
        slice3 = sample_bicubic_layer__ivec2_vec2_int_uint(cell, frac, rt.binary("+", time_cell, rt.i(2), 1, "int"), base_seed)
        return blend_cubic__float_float_float_float_float(slice0, slice1, slice2, slice3, time_frac)
    def sample_value_noise__vec2_vec2_uint_float_float_uint(uv, freq, seed, time_value, speed_value, spline_order):
        uv = rt.copy(uv)
        freq = rt.copy(freq)
        base_seed = seed
        base_value = sample_raw_value_noise__vec2_vec2_uint_float_float_uint(uv, freq, base_seed, time_value, speed_value, spline_order)
        if (bool(rt.binary("==", speed_value, rt.f(0.0))) or bool(rt.binary("==", time_value, rt.f(0.0)))):
            return base_value
        time_seed = rt.binary("+", base_seed, rt.i(2654435761), 1, "uint")
        time_field = sample_raw_value_noise__vec2_vec2_uint_float_float_uint(uv, freq, time_seed, rt.f(0.0), rt.f(1.0), spline_order)
        scaled_time = rt.binary("*", periodic_value__float_float(time_value, time_field), speed_value, 1, "float")
        return periodic_value__float_float(scaled_time, base_value)
    def sample_grain_noise__uvec2_vec2_float_float(pixel_coords, dims, time_value, speed_value):
        pixel_coords = rt.copy(pixel_coords)
        dims = rt.copy(dims)
        width = rt.component_wise("max", rt.swizzle(dims, "x"), rt.f(1.0), width=1)
        height = rt.component_wise("max", rt.swizzle(dims, "y"), rt.f(1.0), width=1)
        uv = rt.construct(2, rt.binary("/", rt.construct(1, rt.swizzle(pixel_coords, "x")), width, 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(pixel_coords, "y")), height, 1, "float"))
        freq = rt.construct(2, width, height)
        return sample_value_noise__vec2_vec2_uint_float_float_uint(uv, freq, g.BASE_SEED, time_value, speed_value, g.INTERPOLATION_BICUBIC)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        global_id = rt.construct(3, rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="uint"), rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="uint"), rt.i(0), base="uint")
        res = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        u_width = rt.component_wise("max", as_u32__float(rt.swizzle(res, "x")), rt.i(1), width=1)
        u_height = rt.component_wise("max", as_u32__float(rt.swizzle(res, "y")), rt.i(1), width=1)
        global_pixel = rt.construct(2, rt.construct(1, rt.binary("+", rt.swizzle(ctx.frag_coord, "x"), rt.swizzle(_u_tileOffset, "x"), 1, "float"), base="uint"), rt.construct(1, rt.binary("+", rt.swizzle(ctx.frag_coord, "y"), rt.swizzle(_u_tileOffset, "y"), 1, "float"), base="uint"), base="uint")
        if (bool(rt.binary(">=", rt.swizzle(global_pixel, "x"), u_width)) or bool(rt.binary(">=", rt.swizzle(global_pixel, "y"), u_height))):
            return
        coords = rt.construct(2, rt.construct(1, rt.swizzle(global_id, "x"), base="int"), rt.construct(1, rt.swizzle(global_id, "y"), base="int"), base="int")
        texel = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        blend_alpha = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", blend_alpha, rt.f(0.0)):
            g.fragColor = texel
            return
        effective_time = (rt.f(0.0) if rt.binary(">", _u_pause, rt.f(0.5)) else _u_time)
        rs = rt.component_wise("max", _u_renderScale, rt.f(1.0), width=1)
        noise_value = sample_grain_noise__uvec2_vec2_float_float(global_pixel, rt.construct(2, rt.binary("/", rt.construct(1, u_width), rs, 1, "float"), rt.binary("/", rt.construct(1, u_height), rs, 1, "float")), effective_time, rt.f(100.0))
        noise_rgb = rt.construct(3, noise_value)
        mixed_rgb = rt.component_wise("mix", rt.swizzle(texel, "rgb"), noise_rgb, blend_alpha, width=3)
        g.fragColor = rt.construct(4, clamp01__float(rt.swizzle(mixed_rgb, "x")), clamp01__float(rt.swizzle(mixed_rgb, "y")), clamp01__float(rt.swizzle(mixed_rgb, "z")), rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
