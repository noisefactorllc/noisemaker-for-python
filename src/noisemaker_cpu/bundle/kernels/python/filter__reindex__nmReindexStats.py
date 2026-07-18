def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    g.F32_MAX = rt.f(3.402823466e+38)
    g.F32_MIN = rt.unary("-", rt.f(3.402823466e+38))
    g.TILE_SIZE = rt.i(8)
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
        fragCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        localX = rt.binary("%", rt.swizzle(fragCoord, "x"), g.TILE_SIZE, 1, "int")
        localY = rt.binary("%", rt.swizzle(fragCoord, "y"), g.TILE_SIZE, 1, "int")
        if (bool(rt.binary("!=", localX, rt.i(0))) or bool(rt.binary("!=", localY, rt.i(0)))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        texSize = rt.texture_size(_u_inputTex)
        tileOrigin = fragCoord
        minValue = g.F32_MAX
        maxValue = g.F32_MIN
        oy = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                oy = rt.binary("+", oy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", oy, g.TILE_SIZE)):
                break
            py = rt.binary("+", rt.swizzle(tileOrigin, "y"), oy, 1, "int")
            if rt.binary(">=", py, rt.swizzle(texSize, "y")):
                break
            ox = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    ox = rt.binary("+", ox, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<", ox, g.TILE_SIZE)):
                    break
                px = rt.binary("+", rt.swizzle(tileOrigin, "x"), ox, 1, "int")
                if rt.binary(">=", px, rt.swizzle(texSize, "x")):
                    break
                texel = rt.texel_fetch(_u_inputTex, rt.construct(2, px, py, base="int"), rt.i(0))
                value = value_map_component__vec4(texel)
                minValue = rt.component_wise("min", minValue, value, width=1)
                maxValue = rt.component_wise("max", maxValue, value, width=1)
        g.fragColor[:] = rt.construct(4, minValue, maxValue, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
