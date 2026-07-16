def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_strength = U.get("strength", rt.f(0.0))
    _u_sharpness = U.get("sharpness", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    g.CHANNEL_COUNT = rt.i(4)
    g.EPSILON = rt.f(1e-10)
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114))
    g.fragColor = rt.construct(4, 0.0)
    def as_u32__float(value):
        return rt.construct(1, rt.component_wise("max", rt.component_wise("round", value, width=1), rt.f(0.0), width=1), base="uint")
    def sanitized_channelCount__float(channel_value):
        rounded = rt.construct(1, rt.component_wise("round", channel_value, width=1), base="int")
        if rt.binary("<=", rounded, rt.i(1)):
            return rt.i(1)
        if rt.binary(">=", rounded, rt.i(4)):
            return rt.i(4)
        return rt.construct(1, rounded, base="uint")
    def reflect_coord__int_int(coord, limit):
        if rt.binary("<=", limit, rt.i(1)):
            return rt.i(0)
        period = rt.binary("-", rt.binary("*", rt.i(2), limit, 1, "int"), rt.i(2), 1, "int")
        wrapped = rt.binary("%", coord, period, 1, "int")
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, period, 1, "int")
        if rt.binary("<", wrapped, limit):
            return wrapped
        return rt.binary("-", period, wrapped, 1, "int")
    def load_texel__ivec2_ivec2(coord, size):
        coord = rt.copy(coord, "int")
        size = rt.copy(size, "int")
        reflected_x = reflect_coord__int_int(rt.swizzle(coord, "x"), rt.swizzle(size, "x"))
        reflected_y = reflect_coord__int_int(rt.swizzle(coord, "y"), rt.swizzle(size, "y"))
        return rt.texel_fetch(_u_inputTex, rt.construct(2, reflected_x, reflected_y, base="int"), rt.i(0))
    def luminance_from_rgb__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        return rt.dot(rgb, g.LUMA_WEIGHTS)
    def weight_from_luma__float_float(center_luma, neighbor_luma):
        return rt.component_wise("exp", rt.binary("*", rt.unary("-", _u_sharpness), rt.component_wise("abs", rt.binary("-", center_luma, neighbor_luma, 1, "float"), width=1), 1, "float"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        global_id = rt.construct(3, rt.construct(1, rt.swizzle(ctx.frag_coord, "x"), base="uint"), rt.construct(1, rt.swizzle(ctx.frag_coord, "y"), base="uint"), rt.i(0), base="uint")
        width_u = rt.component_wise("max", as_u32__float(rt.swizzle(_u_resolution, "x")), rt.i(1), width=1)
        height_u = rt.component_wise("max", as_u32__float(rt.swizzle(_u_resolution, "y")), rt.i(1), width=1)
        if (bool(rt.binary(">=", rt.swizzle(global_id, "x"), width_u)) or bool(rt.binary(">=", rt.swizzle(global_id, "y"), height_u))):
            return
        channelCount = rt.i(4)
        image_size = rt.construct(2, rt.construct(1, width_u, base="int"), rt.construct(1, height_u, base="int"), base="int")
        pixel_coord = rt.construct(2, rt.construct(1, rt.swizzle(global_id, "x"), base="int"), rt.construct(1, rt.swizzle(global_id, "y"), base="int"), base="int")
        center_texel = load_texel__ivec2_ivec2(pixel_coord, image_size)
        north_texel = load_texel__ivec2_ivec2(rt.binary("+", pixel_coord, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"), 2, "int"), image_size)
        south_texel = load_texel__ivec2_ivec2(rt.binary("+", pixel_coord, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), image_size)
        west_texel = load_texel__ivec2_ivec2(rt.binary("+", pixel_coord, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"), 2, "int"), image_size)
        east_texel = load_texel__ivec2_ivec2(rt.binary("+", pixel_coord, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), image_size)
        center_rgb = rt.swizzle(center_texel, "xyz")
        north_rgb = rt.swizzle(north_texel, "xyz")
        south_rgb = rt.swizzle(south_texel, "xyz")
        west_rgb = rt.swizzle(west_texel, "xyz")
        east_rgb = rt.swizzle(east_texel, "xyz")
        center_luma = rt.f(0.0)
        north_luma = rt.f(0.0)
        south_luma = rt.f(0.0)
        west_luma = rt.f(0.0)
        east_luma = rt.f(0.0)
        if rt.binary(">=", channelCount, rt.i(3)):
            center_luma = luminance_from_rgb__vec3(center_rgb)
            north_luma = luminance_from_rgb__vec3(north_rgb)
            south_luma = luminance_from_rgb__vec3(south_rgb)
            west_luma = luminance_from_rgb__vec3(west_rgb)
            east_luma = luminance_from_rgb__vec3(east_rgb)
        else:
            center_luma = rt.swizzle(center_texel, "x")
            north_luma = rt.swizzle(north_texel, "x")
            south_luma = rt.swizzle(south_texel, "x")
            west_luma = rt.swizzle(west_texel, "x")
            east_luma = rt.swizzle(east_texel, "x")
        maxDiff = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", rt.binary("-", center_luma, north_luma, 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", center_luma, south_luma, 1, "float"), width=1), width=1), rt.component_wise("max", rt.component_wise("abs", rt.binary("-", center_luma, west_luma, 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", center_luma, east_luma, 1, "float"), width=1), width=1), width=1)
        if rt.binary("<", maxDiff, _u_threshold):
            g.fragColor = center_texel
            return
        weight_center = rt.f(1.0)
        weight_north = weight_from_luma__float_float(center_luma, north_luma)
        weight_south = weight_from_luma__float_float(center_luma, south_luma)
        weight_west = weight_from_luma__float_float(center_luma, west_luma)
        weight_east = weight_from_luma__float_float(center_luma, east_luma)
        weight_sum = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", weight_center, weight_north, 1, "float"), weight_south, 1, "float"), weight_west, 1, "float"), weight_east, 1, "float"), g.EPSILON, 1, "float")
        result_texel = center_texel
        if rt.binary("<=", channelCount, rt.i(2)):
            blended_luma = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(center_texel, "x"), weight_center, 1, "float"), rt.binary("*", rt.swizzle(north_texel, "x"), weight_north, 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(south_texel, "x"), weight_south, 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(west_texel, "x"), weight_west, 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(east_texel, "x"), weight_east, 1, "float"), 1, "float"), weight_sum, 1, "float")
            result_texel = rt.assign_swizzle(result_texel, "x", blended_luma)
            if rt.binary("==", channelCount, rt.i(1)):
                result_texel = rt.assign_swizzle(result_texel, "y", rt.swizzle(center_texel, "y"))
                result_texel = rt.assign_swizzle(result_texel, "z", rt.swizzle(center_texel, "z"))
        else:
            blended_rgb = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", center_rgb, weight_center, 3, "float"), rt.binary("*", north_rgb, weight_north, 3, "float"), 3, "float"), rt.binary("*", south_rgb, weight_south, 3, "float"), 3, "float"), rt.binary("*", west_rgb, weight_west, 3, "float"), 3, "float"), rt.binary("*", east_rgb, weight_east, 3, "float"), 3, "float"), weight_sum, 3, "float")
            result_texel = rt.construct(4, blended_rgb, rt.swizzle(result_texel, "w"))
        result_texel = rt.assign_swizzle(result_texel, "w", rt.swizzle(center_texel, "w"))
        g.fragColor = rt.component_wise("mix", center_texel, result_texel, _u_strength, width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
