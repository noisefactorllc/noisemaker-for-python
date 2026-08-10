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
    _u_blendMode = U.get("blendMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        trailColor = rt.texture(_u_trailTex, uv)
        t = rt.binary("/", _u_inputIntensity, rt.f(100.0), 1, "float")
        scaledInput = rt.binary("*", inputColor, t, 4, "float")
        outRGB = rt.construct(3, 0.0)
        outAlpha = rt.f(0.0)
        outRGB_pre = rt.construct(3, 0.0)
        trail = rt.construct(3, 0.0)
        trailPresence = rt.f(0.0)
        if rt.binary("==", _u_blendMode, rt.i(1)):
            outAlpha = rt.binary("+", rt.swizzle(trailColor, "a"), rt.binary("*", rt.swizzle(scaledInput, "a"), rt.binary("-", rt.f(1.0), rt.swizzle(trailColor, "a"), 1, "float"), 1, "float"), 1, "float")
            outRGB_pre = rt.binary("+", rt.swizzle(trailColor, "rgb"), rt.binary("*", rt.binary("*", rt.swizzle(scaledInput, "rgb"), rt.swizzle(scaledInput, "a"), 3, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(trailColor, "a"), 1, "float"), 3, "float"), 3, "float")
            outRGB[:] = (rt.binary("/", outRGB_pre, outAlpha, 3, "float") if rt.binary(">", outAlpha, rt.f(0.0)) else rt.construct(3, rt.f(0.0)))
        else:
            trail = rt.component_wise("clamp", rt.swizzle(trailColor, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
            trailPresence = rt.component_wise("max", rt.component_wise("max", rt.swizzle(trail, "r"), rt.swizzle(trail, "g"), width=1), rt.swizzle(trail, "b"), width=1)
            outRGB[:] = rt.binary("+", trail, rt.binary("*", rt.swizzle(scaledInput, "rgb"), rt.binary("-", rt.f(1.0), trail, 3, "float"), 3, "float"), 3, "float")
            outAlpha = rt.component_wise("max", trailPresence, rt.swizzle(scaledInput, "a"), width=1)
        g.fragColor[:] = rt.component_wise("clamp", rt.construct(4, outRGB, outAlpha), rt.f(0.0), rt.f(1.0), width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
