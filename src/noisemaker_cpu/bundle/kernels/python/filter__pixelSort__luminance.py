def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def srgb_to_lin__float(value):
        return (rt.binary("/", value, rt.f(12.92), 1) if rt.binary("<=", value, rt.f(0.04045)) else rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1), rt.f(1.055), 1), rt.f(2.4), width=1))
    def oklab_l__vec3(rgb):
        rgb = rt.copy(rgb)
        r = srgb_to_lin__float(rt.component_wise("clamp", rt.swizzle(rgb, "r"), rt.f(0.0), rt.f(1.0), width=1))
        g = srgb_to_lin__float(rt.component_wise("clamp", rt.swizzle(rgb, "g"), rt.f(0.0), rt.f(1.0), width=1))
        b = srgb_to_lin__float(rt.component_wise("clamp", rt.swizzle(rgb, "b"), rt.f(0.0), rt.f(1.0), width=1))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.4121656120), r, 1), rt.binary("*", rt.f(0.5362752080), g, 1), 1), rt.binary("*", rt.f(0.0514575653), b, 1), 1)
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2118591070), r, 1), rt.binary("*", rt.f(0.6807189584), g, 1), 1), rt.binary("*", rt.f(0.1074065790), b, 1), 1)
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r, 1), rt.binary("*", rt.f(0.2818474174), g, 1), 1), rt.binary("*", rt.f(0.6302613616), b, 1), 1)
        l_c = rt.component_wise("pow", rt.component_wise("abs", l, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1)
        m_c = rt.component_wise("pow", rt.component_wise("abs", m, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1)
        s_c = rt.component_wise("pow", rt.component_wise("abs", s, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), width=1)
        return rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), l_c, 1), rt.binary("*", rt.f(0.7936177850), m_c, 1), 1), rt.binary("*", rt.f(0.0040720468), s_c, 1), 1)
    def main__void():
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        size = rt.texture_size(_u_inputTex)
        texel = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        lum = oklab_l__vec3(rt.swizzle(texel, "rgb"))
        g.fragColor = rt.construct(4, lum, rt.binary("/", rt.swizzle(coord, "x"), rt.construct(1, rt.binary("-", rt.swizzle(size, "x"), rt.i(1), 1)), 1), rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
