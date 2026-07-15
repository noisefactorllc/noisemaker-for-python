def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_size = U["size"]
    _u_motion = U["motion"]
    g.CHANNEL_COUNT = rt.i(4)
    g.CHANNEL_CAP = rt.i(4)
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
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1))
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def sanitize_channelCount__float(raw_value):
        count = as_u32__float(raw_value)
        if rt.binary("<=", count, rt.i(1)):
            return rt.i(1)
        if rt.binary(">=", count, g.CHANNEL_CAP):
            return g.CHANNEL_CAP
        return count
    def wrap_coord__int_int(value, limit):
        if rt.binary("<=", limit, rt.i(0)):
            return rt.i(0)
        wrapped = rt.binary("%", value, limit, 1)
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, limit, 1)
        return wrapped
    def srgb_to_linear__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1)
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1), rt.f(1.055), 1), rt.f(2.4), width=1)
    def cbrt_safe__float(value):
        if rt.binary("==", value, rt.f(0.0)):
            return rt.f(0.0)
        sign_value = (rt.f(1.0) if rt.binary(">=", value, rt.f(0.0)) else rt.unary("-", rt.f(1.0)))
        return rt.binary("*", sign_value, rt.component_wise("pow", rt.component_wise("abs", value, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1), 1)
    def oklab_l_component__vec3(rgb):
        rgb = rt.copy(rgb)
        r = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "x")))
        g = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "y")))
        b = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "z")))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.4121656120), r, 1), rt.binary("*", rt.f(0.5362752080), g, 1), 1), rt.binary("*", rt.f(0.0514575653), b, 1), 1)
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2118591070), r, 1), rt.binary("*", rt.f(0.6807189584), g, 1), 1), rt.binary("*", rt.f(0.1074065790), b, 1), 1)
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r, 1), rt.binary("*", rt.f(0.2818474174), g, 1), 1), rt.binary("*", rt.f(0.6302613616), b, 1), 1)
        l_c = cbrt_safe__float(l)
        m_c = cbrt_safe__float(m)
        s_c = cbrt_safe__float(s)
        return clamp01__float(rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), l_c, 1), rt.binary("*", rt.f(0.7936177850), m_c, 1), 1), rt.binary("*", rt.f(0.0040720468), s_c, 1), 1))
    def value_map_component__vec4_int(texel, channelCount):
        texel = rt.copy(texel)
        if rt.binary("<=", channelCount, rt.i(1)):
            return rt.swizzle(texel, "x")
        if rt.binary("==", channelCount, rt.i(2)):
            return rt.swizzle(texel, "x")
        if rt.binary("==", channelCount, rt.i(3)):
            return oklab_l_component__vec3(rt.swizzle(texel, "xyz"))
        clamped_rgb = rt.component_wise("clamp", rt.swizzle(texel, "xyz"), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        return oklab_l_component__vec3(clamped_rgb)
    def compute_reference_value__ivec2_int(coords, channelCount):
        coords = rt.copy(coords)
        texel = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        return value_map_component__vec4_int(texel, channelCount)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        global_id = cpu_uvec3__float_float_float(rt.construct(1, rt.swizzle(ctx.frag_coord, "x")), rt.construct(1, rt.swizzle(ctx.frag_coord, "y")), rt.i(0))
        width = as_u32__float(rt.swizzle(_u_size, "x"))
        height = as_u32__float(rt.swizzle(_u_size, "y"))
        dims = rt.texture_size(_u_inputTex)
        if rt.binary("==", width, rt.i(0)):
            width = rt.construct(1, rt.component_wise("max", rt.swizzle(dims, "x"), rt.i(1), width=1))
        if rt.binary("==", height, rt.i(0)):
            height = rt.construct(1, rt.component_wise("max", rt.swizzle(dims, "y"), rt.i(1), width=1))
        if rt.binary("||", rt.binary(">=", rt.swizzle(global_id, "x"), width), rt.binary(">=", rt.swizzle(global_id, "y"), height)):
            return
        channelCount = sanitize_channelCount__float(rt.swizzle(_u_size, "z"))
        width_i = rt.construct(1, width)
        height_i = rt.construct(1, height)
        dx = rt.f(0.0)
        dy = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            offset = g.SOBEL_OFFSETS[int(i)]
            sample_coord = cpu_ivec2__float_float(wrap_coord__int_int(rt.binary("+", rt.construct(1, rt.swizzle(global_id, "x")), rt.swizzle(offset, "x"), 1), width_i), wrap_coord__int_int(rt.binary("+", rt.construct(1, rt.swizzle(global_id, "y")), rt.swizzle(offset, "y"), 1), height_i))
            value = compute_reference_value__ivec2_int(sample_coord, channelCount)
            dx = rt.binary("+", dx, rt.binary("*", value, g.SOBEL_X_KERNEL[int(i)], 1), 1)
            dy = rt.binary("+", dy, rt.binary("*", value, g.SOBEL_Y_KERNEL[int(i)], 1), 1)
        x_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", dx, rt.f(0.5), 1), rt.f(0.5), 1), rt.f(0.0), rt.f(1.0), width=1)
        y_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", dy, rt.f(0.5), 1), rt.f(0.5), 1), rt.f(0.0), rt.f(1.0), width=1)
        z_value = rt.component_wise("clamp", rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("+", rt.component_wise("abs", dx, width=1), rt.component_wise("abs", dy, width=1), 1), rt.f(0.5), 1), 1), rt.f(0.0), rt.f(1.0), width=1)
        texel = rt.texel_fetch(_u_inputTex, cpu_ivec2__vec2(rt.swizzle(global_id, "xy")), rt.i(0))
        g.fragColor = rt.construct(4, x_value, y_value, z_value, rt.swizzle(texel, "w"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
