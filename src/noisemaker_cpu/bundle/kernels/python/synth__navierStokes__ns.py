def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputIntensity = U.get("inputIntensity", rt.f(0.0))
    _u_fbTex = T["fbTex"]
    _u_inputTex = T["inputTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_fbTex)
        minIdx = rt.construct(2, rt.i(0), base="int")
        maxIdx = rt.binary("-", texSize, rt.construct(2, rt.i(1), base="int"), 2, "int")
        texelPos = rt.binary("-", rt.binary("/", rt.binary("*", globalCoord, rt.construct(2, texSize), 2, "float"), _u_fullResolution, 2, "float"), rt.construct(2, rt.f(0.5)), 2, "float")
        baseI = rt.construct(2, rt.component_wise("floor", texelPos, width=2), base="int")
        f = rt.component_wise("fract", texelPos, width=2)
        v00 = rt.swizzle(rt.texel_fetch(_u_fbTex, rt.component_wise("clamp", baseI, minIdx, maxIdx, width=2), rt.i(0)), "b")
        v10 = rt.swizzle(rt.texel_fetch(_u_fbTex, rt.component_wise("clamp", rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), minIdx, maxIdx, width=2), rt.i(0)), "b")
        v01 = rt.swizzle(rt.texel_fetch(_u_fbTex, rt.component_wise("clamp", rt.binary("+", baseI, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx, width=2), rt.i(0)), "b")
        v11 = rt.swizzle(rt.texel_fetch(_u_fbTex, rt.component_wise("clamp", rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx, width=2), rt.i(0)), "b")
        v0 = rt.component_wise("mix", v00, v10, rt.swizzle(f, "x"), width=1)
        v1 = rt.component_wise("mix", v01, v11, rt.swizzle(f, "x"), width=1)
        state = rt.component_wise("mix", v0, v1, rt.swizzle(f, "y"), width=1)
        intensity = rt.component_wise("clamp", state, rt.f(0.0), rt.f(1.0), width=1)
        outCol = rt.construct(3, intensity)
        blend = rt.binary("*", rt.component_wise("clamp", _u_inputIntensity, rt.f(0.0), rt.f(100.0), width=1), rt.f(0.01), 1, "float")
        inputUv = rt.construct(2, 0.0)
        inputColor = rt.construct(3, 0.0)
        if rt.binary(">", blend, rt.f(0.0)):
            inputUv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
            inputColor = rt.swizzle(rt.texture(_u_inputTex, inputUv), "rgb")
            outCol[:] = rt.component_wise("mix", outCol, inputColor, blend, width=3)
        g.fragColor[:] = rt.construct(4, outCol, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
