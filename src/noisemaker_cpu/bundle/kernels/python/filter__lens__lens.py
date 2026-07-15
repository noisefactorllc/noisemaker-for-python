def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_lensDisplacement = U["lensDisplacement"]
    _u_aspectLens = U["aspectLens"]
    _u_antialias = U["antialias"]
    g.HALF_FRAME = rt.f(0.5)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        dims = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), dims, 2)
        zoom = (rt.binary("*", _u_lensDisplacement, rt.unary("-", rt.f(0.25)), 1) if rt.binary("<", _u_lensDisplacement, rt.f(0.0)) else rt.f(0.0))
        aspect = rt.binary("/", rt.swizzle(dims, "x"), rt.swizzle(dims, "y"), 1)
        dist = rt.binary("-", uv, g.HALF_FRAME, 2)
        aDist = dist
        if _u_aspectLens:
            aDist = rt.assign_swizzle(aDist, "x", rt.binary("*", rt.swizzle(aDist, "x"), aspect, 1))
        maxDist = rt.length(rt.construct(2, (rt.binary("*", aspect, rt.f(0.5), 1) if _u_aspectLens else rt.f(0.5)), rt.f(0.5)))
        distFromCenter = rt.length(aDist)
        normalizedDist = rt.component_wise("clamp", rt.binary("/", distFromCenter, maxDist, 1), rt.f(0.0), rt.f(1.0), width=1)
        centerWeight = rt.binary("-", rt.f(1.0), normalizedDist, 1)
        centerWeightSq = rt.binary("*", centerWeight, centerWeight, 1)
        displacement = rt.binary("+", rt.binary("*", aDist, zoom, 2), rt.binary("*", rt.binary("*", aDist, centerWeightSq, 2), _u_lensDisplacement, 2), 2)
        if _u_aspectLens:
            displacement = rt.assign_swizzle(displacement, "x", rt.binary("/", rt.swizzle(displacement, "x"), aspect, 1))
        isTileRendering = rt.binary(">", rt.length(_u_tileOffset), rt.f(0.0))
        if isTileRendering:
            maxDispPixels = rt.f(256.0)
            dispPixels = rt.length(rt.binary("*", displacement, dims, 2))
            if rt.binary(">", dispPixels, maxDispPixels):
                displacement = rt.binary("*", displacement, rt.binary("/", maxDispPixels, dispPixels, 1), 2)
        warpedGlobalUV = (rt.binary("-", uv, displacement, 2) if isTileRendering else rt.component_wise("fract", rt.binary("-", uv, displacement, 2), width=2))
        offset = rt.binary("/", rt.binary("-", rt.binary("*", warpedGlobalUV, dims, 2), _u_tileOffset, 2), tileDims, 2)
        sampledUV = offset
        if _u_antialias:
            dx = rt.component_wise("dFdx", sampledUV, width=2)
            dy = rt.component_wise("dFdy", sampledUV, width=2)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.f(0.125), 2), 2), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.f(0.375), 2), 2), rt.binary("*", dy, rt.f(0.125), 2), 2)), 4)
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2), 2), rt.binary("*", dy, rt.f(0.375), 2), 2)), 4)
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4)
        else:
            g.fragColor = rt.texture(_u_inputTex, sampledUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
