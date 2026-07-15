def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_overlayTex = T["overlayTex"]
    _u_alpha = U["alpha"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        base = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        overlay = rt.texel_fetch(_u_overlayTex, coord, rt.i(0))
        scratchStrength = rt.binary("*", rt.swizzle(overlay, "a"), _u_alpha, 1)
        result = rt.component_wise("max", rt.swizzle(base, "rgb"), rt.construct(3, scratchStrength), width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
