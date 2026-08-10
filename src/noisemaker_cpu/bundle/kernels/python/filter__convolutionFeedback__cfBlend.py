def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_feedbackTex = T["feedbackTex"]
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        inputColor = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if _u_resetState:
            g.fragColor[:] = inputColor
            return
        feedback = rt.texel_fetch(_u_feedbackTex, coord, rt.i(0))
        result = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), rt.swizzle(feedback, "rgb"), _u_intensity, width=3)
        g.fragColor[:] = rt.construct(4, result, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
