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
    _u_threshold = U["threshold"]
    _u_antialias = U["antialias"]
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
        color = rt.texture(_u_inputTex, uv)
        if _u_antialias:
            fw = rt.component_wise("fwidth", rt.swizzle(color, "rgb"), width=3)
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("smoothstep", rt.binary("-", _u_threshold, rt.binary("*", fw, rt.f(0.5), 3), 3), rt.binary("+", _u_threshold, rt.binary("*", fw, rt.f(0.5), 3), 3), rt.swizzle(color, "rgb"), width=3))
        else:
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("step", _u_threshold, rt.swizzle(color, "rgb"), width=3))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
