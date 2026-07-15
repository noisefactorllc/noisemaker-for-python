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
    _u_x = U["x"]
    _u_y = U["y"]
    _u_wrap = U["wrap"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.swizzle(uv, "x"), _u_x, 1))
        uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.swizzle(uv, "y"), _u_y, 1))
        if rt.binary("==", _u_wrap, rt.i(0)):
            uv = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                uv = rt.component_wise("fract", uv, width=2)
            else:
                uv = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor = rt.texture(_u_inputTex, uv)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
