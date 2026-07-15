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
    _u_amount = U["amount"]
    _u_colorMode = U["colorMode"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def normalized_sine__float(value):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", value, width=1), rt.f(1.0), 1), rt.f(0.5), 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        color = rt.texture(_u_inputTex, uv)
        use_rgb = rt.binary(">", _u_colorMode, rt.f(0.5))
        if use_rgb:
            color = rt.assign_swizzle(color, "r", normalized_sine__float(rt.binary("*", rt.swizzle(color, "r"), _u_amount, 1)))
            color = rt.assign_swizzle(color, "g", normalized_sine__float(rt.binary("*", rt.swizzle(color, "g"), _u_amount, 1)))
            color = rt.assign_swizzle(color, "b", normalized_sine__float(rt.binary("*", rt.swizzle(color, "b"), _u_amount, 1)))
        else:
            lum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.299), rt.swizzle(color, "r"), 1), rt.binary("*", rt.f(0.587), rt.swizzle(color, "g"), 1), 1), rt.binary("*", rt.f(0.114), rt.swizzle(color, "b"), 1), 1)
            result = normalized_sine__float(rt.binary("*", lum, _u_amount, 1))
            color = rt.assign_swizzle(color, "rgb", rt.construct(3, result))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
