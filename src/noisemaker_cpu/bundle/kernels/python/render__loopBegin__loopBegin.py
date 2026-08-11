def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_accumTex = T["accumTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        inputColor = rt.texture(_u_inputTex, st)
        accum = rt.texture(_u_accumTex, st)
        a = rt.binary("/", _u_alpha, rt.f(100.0), 1, "float")
        i = rt.binary("/", _u_intensity, rt.f(100.0), 1, "float")
        blended = rt.component_wise("max", inputColor, rt.binary("*", accum, i, 4, "float"), width=4)
        result = rt.component_wise("mix", inputColor, blended, a, width=4)
        result = rt.assign_swizzle(result, "a", rt.component_wise("max", rt.swizzle(inputColor, "a"), rt.swizzle(accum, "a"), width=1))
        g.fragColor[:] = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
