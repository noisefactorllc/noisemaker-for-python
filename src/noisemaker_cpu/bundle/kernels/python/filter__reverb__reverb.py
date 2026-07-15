def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_iterations = U["iterations"]
    _u_ridges = U["ridges"]
    _u_alpha = U["alpha"]
    _u_wrap = U["wrap"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def applyWrap__vec2(uv):
        uv = rt.copy(uv)
        mode = rt.construct(1, _u_wrap)
        if rt.binary("==", mode, rt.i(0)):
            return rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
        else:
            if rt.binary("==", mode, rt.i(1)):
                return rt.component_wise("fract", uv, width=2)
        return rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
    def ridge_transform__vec4(color):
        color = rt.copy(color)
        return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("*", color, rt.f(2.0), 4), rt.construct(4, rt.f(1.0)), 4), width=4), 4)
    def main__void():
        dims = rt.texture_size(_u_inputTex)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2)
        localUV = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dims), 2)
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
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, iters)):
                break
            warpedGlobalUV = rt.binary("*", globalUV, scale, 2)
            wrappedGlobalUV = applyWrap__vec2(warpedGlobalUV)
            sampledLocalUV = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", wrappedGlobalUV, _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, dims), 2), width=2)
            scaled = rt.texture(_u_inputTex, sampledLocalUV)
            if _u_ridges:
                scaled = ridge_transform__vec4(scaled)
            accum = rt.binary("+", accum, rt.binary("*", scaled, weight, 4), 4)
            totalWeight = rt.binary("+", totalWeight, weight, 1)
            scale = rt.binary("*", scale, rt.f(2.0), 1)
            weight = rt.binary("*", weight, rt.f(0.5), 1)
        result = rt.binary("/", accum, totalWeight, 4)
        g.fragColor = rt.construct(4, rt.component_wise("mix", rt.swizzle(original, "rgb"), rt.swizzle(result, "rgb"), _u_alpha, width=3), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
