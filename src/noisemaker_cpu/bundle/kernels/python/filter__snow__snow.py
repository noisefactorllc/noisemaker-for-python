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
    _u_alpha = U["alpha"]
    _u_time = U["time"]
    _u_pause = U["pause"]
    _u_density = U["density"]
    g.CHANNEL_COUNT = rt.i(4)
    g.TAU = rt.f(6.283185307179586)
    g.TIME_SEED_OFFSETS = rt.construct(3, rt.f(97.0), rt.f(57.0), rt.f(131.0))
    g.STATIC_SEED = rt.construct(3, rt.f(37.0), rt.f(17.0), rt.f(53.0))
    g.LIMITER_SEED = rt.construct(3, rt.f(113.0), rt.f(71.0), rt.f(193.0))
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1), base="uint")
    def clamp_01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def normalized_sine__float(value):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", value, width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float")
    def periodic_value__float_float(time, value):
        return normalized_sine__float(rt.binary("*", rt.binary("-", time, value, 1, "float"), g.TAU, 1, "float"))
    def snow_fract_vec3__vec3(value):
        value = rt.copy(value)
        return rt.binary("-", value, rt.component_wise("floor", value, width=3), 3, "float")
    def snow_hash__vec3(input_sample):
        input_sample = rt.copy(input_sample)
        scaled = snow_fract_vec3__vec3(rt.binary("*", input_sample, rt.f(0.1031), 3, "float"))
        dot_val = rt.dot(scaled, rt.binary("+", rt.swizzle(scaled, "yzx"), rt.construct(3, rt.f(33.33)), 3, "float"))
        shifted = rt.binary("+", scaled, dot_val, 3, "float")
        combined = rt.binary("*", rt.binary("+", rt.swizzle(shifted, "x"), rt.swizzle(shifted, "y"), 1, "float"), rt.swizzle(shifted, "z"), 1, "float")
        fractional = rt.binary("-", combined, rt.component_wise("floor", combined, width=1), 1, "float")
        return rt.component_wise("clamp", fractional, rt.f(0.0), rt.f(1.0), width=1)
    def snow_noise__vec2_float_float_vec3(coord, time, speed, seed):
        coord = rt.copy(coord)
        seed = rt.copy(seed)
        angle = rt.binary("*", time, g.TAU, 1, "float")
        z_base = rt.binary("*", rt.component_wise("cos", angle, width=1), speed, 1, "float")
        base_sample = rt.construct(3, rt.binary("+", rt.swizzle(coord, "x"), rt.swizzle(seed, "x"), 1, "float"), rt.binary("+", rt.swizzle(coord, "y"), rt.swizzle(seed, "y"), 1, "float"), rt.binary("+", z_base, rt.swizzle(seed, "z"), 1, "float"))
        base_value = snow_hash__vec3(base_sample)
        if (bool(rt.binary("==", speed, rt.f(0.0))) or bool(rt.binary("==", time, rt.f(0.0)))):
            return base_value
        time_seed = rt.binary("+", seed, g.TIME_SEED_OFFSETS, 3, "float")
        time_sample = rt.construct(3, rt.binary("+", rt.swizzle(coord, "x"), rt.swizzle(time_seed, "x"), 1, "float"), rt.binary("+", rt.swizzle(coord, "y"), rt.swizzle(time_seed, "y"), 1, "float"), rt.binary("+", rt.f(1.0), rt.swizzle(time_seed, "z"), 1, "float"))
        time_value = snow_hash__vec3(time_sample)
        scaled_time = rt.binary("*", periodic_value__float_float(time, time_value), speed, 1, "float")
        periodic = periodic_value__float_float(scaled_time, base_value)
        return rt.component_wise("clamp", periodic, rt.f(0.0), rt.f(1.0), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coords = rt.construct(2, rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="int"), rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="int"), base="int")
        texel = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        alphaVal = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("==", alphaVal, rt.f(0.0)):
            g.fragColor = texel
            return
        pixelCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "x"), rt.swizzle(_u_tileOffset, "x"), 1, "float"), rt.binary("+", rt.swizzle(ctx.frag_coord, "y"), rt.swizzle(_u_tileOffset, "y"), 1, "float"))
        timeVal = (rt.f(0.0) if rt.binary(">", _u_pause, rt.f(0.5)) else _u_time)
        speedVal = rt.f(100.0)
        static_value = snow_noise__vec2_float_float_vec3(pixelCoord, timeVal, speedVal, g.STATIC_SEED)
        limiter_value = snow_noise__vec2_float_float_vec3(pixelCoord, timeVal, speedVal, g.LIMITER_SEED)
        d = rt.component_wise("max", rt.binary("*", _u_density, rt.f(0.01), 1, "float"), rt.f(0.0001), width=1)
        exponent = rt.binary("/", rt.binary("-", rt.f(1.0), d, 1, "float"), d, 1, "float")
        limiter_mask = rt.binary("*", rt.component_wise("pow", rt.component_wise("min", limiter_value, rt.f(0.99), width=1), exponent, width=1), alphaVal, 1, "float")
        static_color = rt.construct(3, static_value)
        mixed_rgb = rt.component_wise("mix", rt.swizzle(texel, "xyz"), static_color, rt.construct(3, limiter_mask), width=3)
        g.fragColor = rt.construct(4, mixed_rgb, rt.swizzle(texel, "w"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
