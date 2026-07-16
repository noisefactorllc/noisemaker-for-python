def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_iterations = U.get("iterations", 0)
    _u_ridges = U.get("ridges", False)
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_wrap = U.get("wrap", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def applyWrap__vec2(uv):
        uv = rt.copy(uv, "float")
        mode = rt.construct(1, _u_wrap, base="int")
        if rt.binary("==", mode, rt.i(0)):
            return rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", mode, rt.i(1)):
                return rt.component_wise("fract", uv, width=2)
        return rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
    def ridge_transform__vec4(color):
        color = rt.copy(color, "float")
        return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("*", color, rt.f(2.0), 4, "float"), rt.construct(4, rt.f(1.0)), 4, "float"), width=4), 4, "float")
    def main__void():
        dims = rt.texture_size(_u_inputTex)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        localUV = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dims), 2, "float")
        original = rt.texture(_u_inputTex, localUV)
        current = original
        if _u_ridges:
            current = ridge_transform__vec4(current)
        accum = current
        totalWeight = rt.f(1.0)
        weight = rt.f(0.5)
        scale = rt.f(2.0)
        iters = rt.component_wise("clamp", _u_iterations, rt.i(1), rt.i(8), width=1)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, iters)):
                break
            warpedGlobalUV = rt.binary("*", globalUV, scale, 2, "float")
            wrappedGlobalUV = applyWrap__vec2(warpedGlobalUV)
            sampledLocalUV = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", wrappedGlobalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, dims), 2, "float"), width=2)
            scaled = rt.texture(_u_inputTex, sampledLocalUV)
            if _u_ridges:
                scaled = ridge_transform__vec4(scaled)
            accum = rt.binary("+", accum, rt.binary("*", scaled, weight, 4, "float"), 4, "float")
            totalWeight = rt.binary("+", totalWeight, weight, 1, "float")
            scale = rt.binary("*", scale, rt.f(2.0), 1, "float")
            weight = rt.binary("*", weight, rt.f(0.5), 1, "float")
        result = rt.binary("/", accum, totalWeight, 4, "float")
        g.fragColor = rt.construct(4, rt.component_wise("mix", rt.swizzle(original, "rgb"), rt.swizzle(result, "rgb"), _u_alpha, width=3), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
