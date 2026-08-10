def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_size = U.get("size", rt.construct(4, 0.0))
    _u_motion = U.get("motion", rt.construct(4, 0.0))
    g.CHANNEL_COUNT = rt.i(4)
    g.CHANNEL_CAP = rt.i(4)
    g.fragColor = rt.construct(4, 0.0)
    g.SOBEL_OFFSETS = rt.array([rt.construct(2, rt.unary("-", rt.i(1)), rt.unary("-", rt.i(1)), base="int"), rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"), rt.construct(2, rt.i(1), rt.unary("-", rt.i(1)), base="int"), rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"), rt.construct(2, rt.i(0), rt.i(0), base="int"), rt.construct(2, rt.i(1), rt.i(0), base="int"), rt.construct(2, rt.unary("-", rt.i(1)), rt.i(1), base="int"), rt.construct(2, rt.i(0), rt.i(1), base="int"), rt.construct(2, rt.i(1), rt.i(1), base="int")])
    g.SOBEL_X_KERNEL = rt.array([rt.f(0.5), rt.f(0.0), rt.unary("-", rt.f(0.5)), rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(1.0)), rt.f(0.5), rt.f(0.0), rt.unary("-", rt.f(0.5))])
    g.SOBEL_Y_KERNEL = rt.array([rt.f(0.5), rt.f(1.0), rt.f(0.5), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.unary("-", rt.f(0.5)), rt.unary("-", rt.f(1.0)), rt.unary("-", rt.f(0.5))])
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1), base="uint")
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
        wrapped = rt.binary("%", value, limit, 1, "int")
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, limit, 1, "int")
        return wrapped
    def srgb_to_linear__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1, "float")
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
    def cbrt_safe__float(value):
        if rt.binary("==", value, rt.f(0.0)):
            return rt.f(0.0)
        sign_value = (rt.f(1.0) if rt.binary(">=", value, rt.f(0.0)) else rt.unary("-", rt.f(1.0)))
        return rt.binary("*", sign_value, rt.component_wise("pow", rt.component_wise("abs", value, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1), 1, "float")
    def oklab_l_component__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "x")))
        _g = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "y")))
        b = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "z")))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.412165612), r, 1, "float"), rt.binary("*", rt.f(0.536275208), _g, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0514575653), b, 1, "float"), 1, "float")
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.211859107), r, 1, "float"), rt.binary("*", rt.f(0.6807189584), _g, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.107406579), b, 1, "float"), 1, "float")
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r, 1, "float"), rt.binary("*", rt.f(0.2818474174), _g, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.6302613616), b, 1, "float"), 1, "float")
        l_c = cbrt_safe__float(l)
        m_c = cbrt_safe__float(m)
        s_c = cbrt_safe__float(s)
        return clamp01__float(rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), l_c, 1, "float"), rt.binary("*", rt.f(0.793617785), m_c, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0040720468), s_c, 1, "float"), 1, "float"))
    def value_map_component__vec4_uint(texel, channelCount):
        texel = rt.copy(texel, "float")
        if rt.binary("<=", channelCount, rt.i(1)):
            return rt.swizzle(texel, "x")
        if rt.binary("==", channelCount, rt.i(2)):
            return rt.swizzle(texel, "x")
        if rt.binary("==", channelCount, rt.i(3)):
            return oklab_l_component__vec3(rt.swizzle(texel, "xyz"))
        clamped_rgb = rt.component_wise("clamp", rt.swizzle(texel, "xyz"), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        return oklab_l_component__vec3(clamped_rgb)
    def compute_reference_value__ivec2_uint(coords, channelCount):
        coords = rt.copy(coords, "int")
        texel = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        return value_map_component__vec4_uint(texel, channelCount)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        global_id = rt.construct(3, rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="uint"), rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="uint"), rt.i(0), base="uint")
        width = as_u32__float(rt.swizzle(_u_size, "x"))
        height = as_u32__float(rt.swizzle(_u_size, "y"))
        dims = rt.texture_size(_u_inputTex)
        if rt.binary("==", width, rt.i(0)):
            width = rt.construct(1, rt.component_wise("max", rt.swizzle(dims, "x"), rt.i(1), width=1), base="uint")
        if rt.binary("==", height, rt.i(0)):
            height = rt.construct(1, rt.component_wise("max", rt.swizzle(dims, "y"), rt.i(1), width=1), base="uint")
        if (bool(rt.binary(">=", rt.swizzle(global_id, "x"), width)) or bool(rt.binary(">=", rt.swizzle(global_id, "y"), height))):
            return
        channelCount = sanitize_channelCount__float(rt.swizzle(_u_size, "z"))
        width_i = rt.construct(1, width, base="int")
        height_i = rt.construct(1, height, base="int")
        dx = rt.f(0.0)
        dy = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            offset = g.SOBEL_OFFSETS[int(i)]
            sample_coord = rt.construct(2, wrap_coord__int_int(rt.binary("+", rt.construct(1, rt.swizzle(global_id, "x"), base="int"), rt.swizzle(offset, "x"), 1, "int"), width_i), wrap_coord__int_int(rt.binary("+", rt.construct(1, rt.swizzle(global_id, "y"), base="int"), rt.swizzle(offset, "y"), 1, "int"), height_i), base="int")
            value = compute_reference_value__ivec2_uint(sample_coord, channelCount)
            dx = rt.binary("+", dx, rt.binary("*", value, g.SOBEL_X_KERNEL[int(i)], 1, "float"), 1, "float")
            dy = rt.binary("+", dy, rt.binary("*", value, g.SOBEL_Y_KERNEL[int(i)], 1, "float"), 1, "float")
        x_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", dx, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        y_value = rt.component_wise("clamp", rt.binary("+", rt.binary("*", dy, rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        z_value = rt.component_wise("clamp", rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("+", rt.component_wise("abs", dx, width=1), rt.component_wise("abs", dy, width=1), 1, "float"), rt.f(0.5), 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        texel = rt.texel_fetch(_u_inputTex, rt.construct(2, rt.swizzle(global_id, "xy"), base="int"), rt.i(0))
        g.fragColor[:] = rt.construct(4, x_value, y_value, z_value, rt.swizzle(texel, "w"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
