def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_statsTex = T["statsTex"]
    _u_uDisplacement = U.get("uDisplacement", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def clamp01__float(value):
        return rt.component_wise("clamp", value, rt.f(0.0), rt.f(1.0), width=1)
    def srgb_to_linear__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1, "float")
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
    def cube_root__float(value):
        if rt.binary("==", value, rt.f(0.0)):
            return rt.f(0.0)
        sign_value = (rt.f(1.0) if rt.binary(">=", value, rt.f(0.0)) else rt.unary("-", rt.f(1.0)))
        return rt.binary("*", sign_value, rt.component_wise("pow", rt.component_wise("abs", value, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1), 1, "float")
    def oklab_l_component__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r_lin = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "x")))
        g_lin = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "y")))
        b_lin = srgb_to_linear__float(clamp01__float(rt.swizzle(rgb, "z")))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.412165612), r_lin, 1, "float"), rt.binary("*", rt.f(0.536275208), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0514575653), b_lin, 1, "float"), 1, "float")
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.211859107), r_lin, 1, "float"), rt.binary("*", rt.f(0.6807189584), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.107406579), b_lin, 1, "float"), 1, "float")
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r_lin, 1, "float"), rt.binary("*", rt.f(0.2818474174), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.6302613616), b_lin, 1, "float"), 1, "float")
        l_c = cube_root__float(l)
        m_c = cube_root__float(m)
        s_c = cube_root__float(s)
        lightness = rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), l_c, 1, "float"), rt.binary("*", rt.f(0.793617785), m_c, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0040720468), s_c, 1, "float"), 1, "float")
        return clamp01__float(lightness)
    def value_map_component__vec4(texel):
        texel = rt.copy(texel, "float")
        return oklab_l_component__vec3(rt.swizzle(texel, "xyz"))
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        pixel = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        if (bool(rt.binary(">=", rt.swizzle(pixel, "x"), rt.swizzle(texSize, "x"))) or bool(rt.binary(">=", rt.swizzle(pixel, "y"), rt.swizzle(texSize, "y")))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        texel = rt.texel_fetch(_u_inputTex, pixel, rt.i(0))
        referenceValue = value_map_component__vec4(texel)
        minMax = rt.swizzle(rt.texel_fetch(_u_statsTex, rt.construct(2, rt.i(0), rt.i(0), base="int"), rt.i(0)), "xy")
        range = rt.binary("-", rt.swizzle(minMax, "y"), rt.swizzle(minMax, "x"), 1, "float")
        normalized = referenceValue
        if rt.binary(">", range, rt.f(0.0001)):
            normalized = clamp01__float(rt.binary("/", rt.binary("-", referenceValue, rt.swizzle(minMax, "x"), 1, "float"), range, 1, "float"))
        modRange = rt.construct(1, rt.component_wise("min", rt.swizzle(texSize, "x"), rt.swizzle(texSize, "y"), width=1))
        offsetValue = rt.binary("+", rt.binary("*", rt.binary("*", normalized, _u_uDisplacement, 1, "float"), modRange, 1, "float"), normalized, 1, "float")
        sampleX = rt.construct(1, rt.binary("*", rt.component_wise("fract", rt.binary("/", offsetValue, rt.construct(1, rt.swizzle(texSize, "x")), 1, "float"), width=1), rt.construct(1, rt.swizzle(texSize, "x")), 1, "float"), base="int")
        sampleY = rt.construct(1, rt.binary("*", rt.component_wise("fract", rt.binary("/", offsetValue, rt.construct(1, rt.swizzle(texSize, "y")), 1, "float"), width=1), rt.construct(1, rt.swizzle(texSize, "y")), 1, "float"), base="int")
        sampleX = rt.component_wise("min", sampleX, rt.binary("-", rt.swizzle(texSize, "x"), rt.i(1), 1, "int"), width=1)
        sampleY = rt.component_wise("min", sampleY, rt.binary("-", rt.swizzle(texSize, "y"), rt.i(1), 1, "int"), width=1)
        sampled = rt.texel_fetch(_u_inputTex, rt.construct(2, sampleX, sampleY, base="int"), rt.i(0))
        g.fragColor[:] = sampled
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
