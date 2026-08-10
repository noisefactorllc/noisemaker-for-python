def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_selfTex = T["selfTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_amount = U.get("amount", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        if _u_resetState:
            g.fragColor[:] = rt.texture(_u_inputTex, uv)
            return
        current = rt.texture(_u_inputTex, uv)
        previous = rt.texture(_u_selfTex, uv)
        mixFactor = rt.component_wise("clamp", rt.binary("*", _u_amount, rt.f(0.008), 1, "float"), rt.f(0.0), rt.f(0.98), width=1)
        g.fragColor[:] = rt.component_wise("mix", current, previous, mixFactor, width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
