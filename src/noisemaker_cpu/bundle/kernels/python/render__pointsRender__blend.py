def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_trailTex = T["trailTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_inputIntensity = U.get("inputIntensity", rt.f(0.0))
    _u_matteOpacity = U.get("matteOpacity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        trailColor = rt.texture(_u_trailTex, uv)
        t = rt.binary("/", _u_inputIntensity, rt.f(100.0), 1, "float")
        matteAlpha = _u_matteOpacity
        trailPresence = rt.component_wise("max", rt.component_wise("max", rt.swizzle(trailColor, "r"), rt.swizzle(trailColor, "g"), width=1), rt.swizzle(trailColor, "b"), width=1)
        rgb = rt.binary("+", rt.swizzle(trailColor, "rgb"), rt.binary("*", rt.binary("*", rt.swizzle(inputColor, "rgb"), t, 3, "float"), matteAlpha, 3, "float"), 3, "float")
        alpha = rt.component_wise("max", trailPresence, matteAlpha, width=1)
        g.fragColor[:] = rt.component_wise("clamp", rt.construct(4, rgb, alpha), rt.f(0.0), rt.f(1.0), width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
