def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blend = U["blend"]
    _u_repeat = U["repeat"]
    _u_curve = U["curve"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def edgeWeight__float_float(t, width):
        if rt.binary("<=", width, rt.f(0.0)):
            return rt.f(0.0)
        d = rt.component_wise("min", t, rt.binary("-", rt.f(1.0), t, 1), width=1)
        w = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("/", d, width, 1), rt.f(0.0), rt.f(1.0), width=1), 1)
        if rt.binary("==", _u_curve, rt.i(0)):
            return w
        else:
            if rt.binary("==", _u_curve, rt.i(2)):
                return rt.binary("*", w, w, 1)
        return rt.binary("*", rt.binary("*", w, w, 1), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), w, 1), 1), 1)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        st = rt.binary("*", uv, _u_repeat, 2)
        st = rt.component_wise("fract", st, width=2)
        wx = edgeWeight__float_float(rt.swizzle(st, "x"), _u_blend)
        wy = edgeWeight__float_float(rt.swizzle(st, "y"), _u_blend)
        c00 = rt.texture(_u_inputTex, st)
        c10 = rt.texture(_u_inputTex, rt.component_wise("fract", rt.binary("+", st, rt.construct(2, rt.f(0.5), rt.f(0.0)), 2), width=2))
        c01 = rt.texture(_u_inputTex, rt.component_wise("fract", rt.binary("+", st, rt.construct(2, rt.f(0.0), rt.f(0.5)), 2), width=2))
        c11 = rt.texture(_u_inputTex, rt.component_wise("fract", rt.binary("+", st, rt.construct(2, rt.f(0.5), rt.f(0.5)), 2), width=2))
        mx0 = rt.component_wise("mix", c00, c10, wx, width=4)
        mx1 = rt.component_wise("mix", c01, c11, wx, width=4)
        result = rt.component_wise("mix", mx0, mx1, wy, width=4)
        g.fragColor = rt.construct(4, rt.swizzle(result, "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
