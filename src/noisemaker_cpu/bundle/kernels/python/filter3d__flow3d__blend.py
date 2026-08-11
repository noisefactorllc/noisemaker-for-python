def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_BEHAVIOR = U.get("BEHAVIOR", 0)
    _u_mixerTex = T["mixerTex"]
    _u_trailTex = T["trailTex"]
    _u_inputIntensity = U.get("inputIntensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        outputSize = rt.texture_size(_u_trailTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, outputSize), 2, "float")
        inputIntensityValue = rt.binary("/", _u_inputIntensity, rt.f(100.0), 1, "float")
        baseSample = rt.texture(_u_mixerTex, uv)
        baseColor = rt.construct(4, rt.binary("*", rt.swizzle(baseSample, "rgb"), inputIntensityValue, 3, "float"), rt.swizzle(baseSample, "a"))
        trailColor = rt.texture(_u_trailTex, uv)
        combinedRgb = rt.component_wise("clamp", rt.binary("+", rt.swizzle(baseColor, "rgb"), rt.swizzle(trailColor, "rgb"), 3, "float"), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        finalAlpha = rt.component_wise("clamp", rt.component_wise("max", rt.swizzle(baseColor, "a"), rt.swizzle(trailColor, "a"), width=1), rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor[:] = rt.construct(4, combinedRgb, finalAlpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
