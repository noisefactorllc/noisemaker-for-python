def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_dyeDecay = U.get("dyeDecay", rt.f(0.0))
    _u_velocityDecay = U.get("velocityDecay", rt.f(0.0))
    _u_bufTex = T["bufTex"]
    g.fragColor = rt.construct(4, 0.0)
    def fetchTex__ivec2_ivec2_ivec2(idx, minIdx, maxIdx):
        idx = rt.copy(idx, "int")
        minIdx = rt.copy(minIdx, "int")
        maxIdx = rt.copy(maxIdx, "int")
        return rt.texel_fetch(_u_bufTex, rt.component_wise("clamp", idx, minIdx, maxIdx, width=2), rt.i(0))
    def sampleBilinear__vec2_ivec2(uv, texSize):
        uv = rt.copy(uv, "float")
        texSize = rt.copy(texSize, "int")
        minIdx = rt.construct(2, rt.i(0), base="int")
        maxIdx = rt.binary("-", texSize, rt.construct(2, rt.i(1), base="int"), 2, "int")
        texelPos = rt.binary("-", rt.binary("*", uv, rt.construct(2, texSize), 2, "float"), rt.construct(2, rt.f(0.5)), 2, "float")
        baseI = rt.construct(2, rt.component_wise("floor", texelPos, width=2), base="int")
        f = rt.component_wise("fract", texelPos, width=2)
        v00 = fetchTex__ivec2_ivec2_ivec2(baseI, minIdx, maxIdx)
        v10 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), minIdx, maxIdx)
        v01 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
        v11 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
        v0 = rt.component_wise("mix", v00, v10, rt.swizzle(f, "x"), width=4)
        v1 = rt.component_wise("mix", v01, v11, rt.swizzle(f, "x"), width=4)
        return rt.component_wise("mix", v0, v1, rt.swizzle(f, "y"), width=4)
    def main__void():
        texSize = rt.texture_size(_u_bufTex)
        fragCoord = rt.swizzle(ctx.frag_coord, "xy")
        uv = rt.binary("/", fragCoord, rt.construct(2, texSize), 2, "float")
        here = rt.texel_fetch(_u_bufTex, rt.component_wise("clamp", rt.construct(2, fragCoord, base="int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", texSize, rt.construct(2, rt.i(1), base="int"), 2, "int"), width=2), rt.i(0))
        u = rt.swizzle(here, "rg")
        dt = rt.binary("*", rt.component_wise("clamp", _u_speed, rt.f(0.0), rt.f(200.0), width=1), rt.f(0.0001), 1, "float")
        backUv = rt.component_wise("clamp", rt.binary("-", uv, rt.binary("*", u, dt, 2, "float"), 2, "float"), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.f(1.0)), width=2)
        advected = sampleBilinear__vec2_ivec2(backUv, texSize)
        newVel = rt.swizzle(advected, "rg")
        newDye = rt.swizzle(advected, "b")
        vDecay = rt.component_wise("pow", rt.binary("*", rt.component_wise("clamp", _u_velocityDecay, rt.f(0.0), rt.f(100.0), width=1), rt.f(0.01), 1, "float"), rt.binary("*", dt, rt.f(60.0), 1, "float"), width=1)
        dDecay = rt.component_wise("pow", rt.binary("*", rt.component_wise("clamp", _u_dyeDecay, rt.f(0.0), rt.f(100.0), width=1), rt.f(0.01), 1, "float"), rt.binary("*", dt, rt.f(60.0), 1, "float"), width=1)
        newVel[:] = rt.binary("*", newVel, vDecay, 2, "float")
        newDye = rt.binary("*", newDye, dDecay, 1, "float")
        g.fragColor[:] = rt.construct(4, newVel, newDye, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
