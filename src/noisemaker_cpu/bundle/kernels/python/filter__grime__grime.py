def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_strength = U.get("strength", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def clamp01__float(v):
        return rt.component_wise("clamp", v, rt.f(0.0), rt.f(1.0), width=1)
    def freq_for_shape__float_float_float(freq, w, h):
        if (bool(rt.binary("<=", w, rt.f(0.0))) or bool(rt.binary("<=", h, rt.f(0.0)))):
            return rt.construct(2, freq)
        if rt.binary("<", rt.component_wise("abs", rt.binary("-", w, h, 1, "float"), width=1), rt.f(0.5)):
            return rt.construct(2, freq)
        if rt.binary("<", h, w):
            return rt.construct(2, freq, rt.binary("/", rt.binary("*", freq, w, 1, "float"), h, 1, "float"))
        return rt.construct(2, rt.binary("/", rt.binary("*", freq, h, 1, "float"), w, 1, "float"), freq)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def hash21__vec2(p):
        p = rt.copy(p, "float")
        v = pcg__uvec3(rt.construct(3, rt.float_bits_to_uint(rt.swizzle(p, "x")), rt.float_bits_to_uint(rt.swizzle(p, "y")), rt.i(0), base="uint"))
        return rt.binary("/", rt.construct(1, rt.swizzle(v, "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def hash31__vec3(p):
        p = rt.copy(p, "float")
        v = pcg__uvec3(rt.construct(3, rt.float_bits_to_uint(rt.swizzle(p, "x")), rt.float_bits_to_uint(rt.swizzle(p, "y")), rt.float_bits_to_uint(rt.swizzle(p, "z")), base="uint"))
        return rt.binary("/", rt.construct(1, rt.swizzle(v, "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def fade__float(t):
        return rt.binary("*", rt.binary("*", t, t, 1, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), 1, "float")
    def value_noise__vec2_float(coord, s):
        coord = rt.copy(coord, "float")
        cell = rt.component_wise("floor", coord, width=2)
        f = rt.component_wise("fract", coord, width=2)
        tl = hash31__vec3(rt.construct(3, cell, s))
        tr = hash31__vec3(rt.construct(3, rt.binary("+", cell, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), s))
        bl = hash31__vec3(rt.construct(3, rt.binary("+", cell, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), s))
        br = hash31__vec3(rt.construct(3, rt.binary("+", cell, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float"), s))
        st = rt.construct(2, fade__float(rt.swizzle(f, "x")), fade__float(rt.swizzle(f, "y")))
        return rt.component_wise("mix", rt.component_wise("mix", tl, tr, rt.swizzle(st, "x"), width=1), rt.component_wise("mix", bl, br, rt.swizzle(st, "x"), width=1), rt.swizzle(st, "y"), width=1)
    def seed_offset__float(s):
        angle = rt.binary("*", s, rt.f(0.1375), 1, "float")
        radius = rt.binary("*", rt.f(0.35), rt.binary("+", rt.f(0.25), rt.binary("*", rt.f(0.75), rt.component_wise("sin", rt.binary("*", s, rt.f(1.37), 1, "float"), width=1), 1, "float"), 1, "float"), 1, "float")
        return rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), radius, 2, "float")
    def simple_multires__vec2_vec2_float(uv, base_freq, s):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        freq = base_freq
        amp = rt.f(0.5)
        total = rt.f(0.0)
        accum = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(8))):
                break
            os = rt.binary("+", s, rt.binary("*", rt.construct(1, i), rt.f(37.11), 1, "float"), 1, "float")
            off = rt.binary("/", seed_offset__float(os), freq, 2, "float")
            accum = rt.binary("+", accum, rt.binary("*", value_noise__vec2_float(rt.binary("+", rt.binary("*", uv, freq, 2, "float"), off, 2, "float"), os), amp, 1, "float"), 1, "float")
            total = rt.binary("+", total, amp, 1, "float")
            freq[:] = rt.binary("*", freq, rt.f(2.0), 2, "float")
            amp = rt.binary("*", amp, rt.f(0.5), 1, "float")
        return clamp01__float(rt.binary("/", accum, rt.component_wise("max", total, rt.f(0.001), width=1), 1, "float"))
    def refracted_field__vec2_vec2_vec2_float_float(uv, base_freq, px, disp, s):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        px = rt.copy(px, "float")
        base_mask = simple_multires__vec2_vec2_float(uv, base_freq, s)
        off_mask = simple_multires__vec2_vec2_float(rt.component_wise("fract", rt.binary("+", uv, rt.f(0.5), 2, "float"), width=2), base_freq, rt.binary("+", s, rt.f(19.0), 1, "float"))
        off_vec = rt.construct(2, rt.binary("*", rt.binary("*", rt.binary("-", rt.binary("*", base_mask, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), disp, 1, "float"), rt.swizzle(px, "x"), 1, "float"), rt.binary("*", rt.binary("*", rt.binary("-", rt.binary("*", off_mask, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), disp, 1, "float"), rt.swizzle(px, "y"), 1, "float"))
        return simple_multires__vec2_vec2_float(rt.component_wise("fract", rt.binary("+", uv, off_vec, 2, "float"), width=2), base_freq, rt.binary("+", s, rt.f(41.0), 1, "float"))
    def chebyshev_gradient__vec2_vec2_vec2_float_float(uv, base_freq, px, disp, s):
        uv = rt.copy(uv, "float")
        base_freq = rt.copy(base_freq, "float")
        px = rt.copy(px, "float")
        ox = rt.construct(2, rt.swizzle(px, "x"), rt.f(0.0))
        oy = rt.construct(2, rt.f(0.0), rt.swizzle(px, "y"))
        r = refracted_field__vec2_vec2_vec2_float_float(rt.component_wise("fract", rt.binary("+", uv, ox, 2, "float"), width=2), base_freq, px, disp, s)
        l = refracted_field__vec2_vec2_vec2_float_float(rt.component_wise("fract", rt.binary("-", uv, ox, 2, "float"), width=2), base_freq, px, disp, s)
        u = refracted_field__vec2_vec2_vec2_float_float(rt.component_wise("fract", rt.binary("+", uv, oy, 2, "float"), width=2), base_freq, px, disp, s)
        d = refracted_field__vec2_vec2_vec2_float_float(rt.component_wise("fract", rt.binary("-", uv, oy, 2, "float"), width=2), base_freq, px, disp, s)
        dx = rt.binary("*", rt.binary("-", r, l, 1, "float"), rt.f(0.5), 1, "float")
        dy = rt.binary("*", rt.binary("-", u, d, 1, "float"), rt.f(0.5), 1, "float")
        return clamp01__float(rt.binary("*", rt.component_wise("max", rt.component_wise("abs", dx, width=1), rt.component_wise("abs", dy, width=1), width=1), rt.f(4.0), 1, "float"))
    def exponential_noise__vec2_vec2_float(uv, freq, s):
        uv = rt.copy(uv, "float")
        freq = rt.copy(freq, "float")
        off = seed_offset__float(rt.binary("+", s, rt.f(7.0), 1, "float"))
        return rt.component_wise("pow", clamp01__float(value_noise__vec2_float(rt.binary("+", rt.binary("*", uv, freq, 2, "float"), off, 2, "float"), rt.binary("+", s, rt.f(13.0), 1, "float"))), rt.f(4.0), width=1)
    def refracted_exponential__vec2_vec2_vec2_float_float(uv, freq, px, disp, s):
        uv = rt.copy(uv, "float")
        freq = rt.copy(freq, "float")
        px = rt.copy(px, "float")
        base = exponential_noise__vec2_vec2_float(uv, freq, s)
        ox = exponential_noise__vec2_vec2_float(uv, freq, rt.binary("+", s, rt.f(23.0), 1, "float"))
        oy = exponential_noise__vec2_vec2_float(rt.component_wise("fract", rt.binary("+", uv, rt.f(0.5), 2, "float"), width=2), freq, rt.binary("+", s, rt.f(47.0), 1, "float"))
        off_vec = rt.construct(2, rt.binary("*", rt.binary("*", rt.binary("-", rt.binary("*", ox, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), disp, 1, "float"), rt.swizzle(px, "x"), 1, "float"), rt.binary("*", rt.binary("*", rt.binary("-", rt.binary("*", oy, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), disp, 1, "float"), rt.swizzle(px, "y"), 1, "float"))
        warped = exponential_noise__vec2_vec2_float(rt.component_wise("fract", rt.binary("+", uv, off_vec, 2, "float"), width=2), freq, rt.binary("+", s, rt.f(59.0), 1, "float"))
        return clamp01__float(rt.binary("*", rt.binary("+", base, warped, 1, "float"), rt.f(0.5), 1, "float"))
    def main__void():
        tileSize = rt.construct(2, rt.texture_size(_u_inputTex))
        globalCoord = rt.binary("+", rt.binary("*", ctx.uv, tileSize, 2, "float"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        px = rt.binary("/", rt.f(1.0), _u_fullResolution, 2, "float")
        base_color = rt.texture(_u_inputTex, ctx.uv)
        str = rt.component_wise("max", _u_strength, rt.f(0.0), width=1)
        s = _u_seed
        freq_mask = freq_for_shape__float_float_float(rt.f(5.0), rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"))
        mask_refracted = refracted_field__vec2_vec2_vec2_float_float(globalUV, freq_mask, px, rt.f(1.0), rt.binary("+", s, rt.f(11.0), 1, "float"))
        mask_gradient = chebyshev_gradient__vec2_vec2_vec2_float_float(globalUV, freq_mask, px, rt.f(1.0), rt.binary("+", s, rt.f(11.0), 1, "float"))
        mask_value = clamp01__float(rt.component_wise("mix", mask_refracted, mask_gradient, rt.f(0.125), width=1))
        mask_power = clamp01__float(rt.binary("*", rt.binary("*", mask_value, mask_value, 1, "float"), rt.f(0.4), 1, "float"))
        dusty = rt.component_wise("mix", rt.swizzle(base_color, "rgb"), rt.construct(3, rt.f(0.15)), mask_power, width=3)
        freq_specks = rt.binary("*", _u_fullResolution, rt.f(0.1), 2, "float")
        dropout = (rt.f(1.0) if rt.binary("<", hash21__vec2(rt.binary("+", rt.binary("*", globalUV, _u_fullResolution, 2, "float"), rt.construct(2, rt.binary("+", s, rt.f(37.0), 1, "float"), rt.binary("*", s, rt.f(1.37), 1, "float")), 2, "float")), rt.f(0.4)) else rt.f(0.0))
        specks_field = rt.binary("*", refracted_exponential__vec2_vec2_vec2_float_float(globalUV, freq_specks, px, rt.f(0.25), rt.binary("+", s, rt.f(71.0), 1, "float")), dropout, 1, "float")
        trimmed = clamp01__float(rt.binary("/", rt.binary("-", specks_field, rt.f(0.3), 1, "float"), rt.f(0.7), 1, "float"))
        specks = rt.binary("-", rt.f(1.0), rt.component_wise("sqrt", trimmed, width=1), 1, "float")
        sparse_mask = (rt.f(1.0) if rt.binary("<", hash21__vec2(rt.binary("+", rt.binary("*", globalUV, _u_fullResolution, 2, "float"), rt.construct(2, rt.binary("+", s, rt.f(113.0), 1, "float"), rt.binary("+", s, rt.f(171.0), 1, "float")), 2, "float")), rt.f(0.25)) else rt.f(0.0))
        sparse_noise = rt.binary("*", exponential_noise__vec2_vec2_float(globalUV, _u_fullResolution, rt.binary("+", s, rt.f(131.0), 1, "float")), sparse_mask, 1, "float")
        dusty[:] = rt.component_wise("mix", dusty, rt.construct(3, sparse_noise), rt.f(0.15), width=3)
        dusty[:] = rt.binary("*", dusty, specks, 3, "float")
        blend_mask = clamp01__float(rt.binary("*", mask_value, str, 1, "float"))
        final_rgb = rt.component_wise("mix", rt.swizzle(base_color, "rgb"), dusty, blend_mask, width=3)
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", final_rgb, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(base_color, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
