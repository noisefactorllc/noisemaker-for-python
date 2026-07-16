def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_lensDisplacement = U.get("lensDisplacement", rt.f(0.0))
    _u_aspectLens = U.get("aspectLens", False)
    _u_antialias = U.get("antialias", False)
    g.fragColor = rt.construct(4, 0.0)
    g.HALF_FRAME = rt.f(0.5)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        dims = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), dims, 2, "float")
        zoom = (rt.binary("*", _u_lensDisplacement, rt.unary("-", rt.f(0.25)), 1, "float") if rt.binary("<", _u_lensDisplacement, rt.f(0.0)) else rt.f(0.0))
        aspect = rt.binary("/", rt.swizzle(dims, "x"), rt.swizzle(dims, "y"), 1, "float")
        dist = rt.binary("-", uv, g.HALF_FRAME, 2, "float")
        aDist = dist
        if _u_aspectLens:
            aDist = rt.assign_swizzle(aDist, "x", rt.binary("*", rt.swizzle(aDist, "x"), aspect, 1, "float"))
        maxDist = rt.length(rt.construct(2, (rt.binary("*", aspect, rt.f(0.5), 1, "float") if _u_aspectLens else rt.f(0.5)), rt.f(0.5)))
        distFromCenter = rt.length(aDist)
        normalizedDist = rt.component_wise("clamp", rt.binary("/", distFromCenter, maxDist, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        centerWeight = rt.binary("-", rt.f(1.0), normalizedDist, 1, "float")
        centerWeightSq = rt.binary("*", centerWeight, centerWeight, 1, "float")
        displacement = rt.binary("+", rt.binary("*", aDist, zoom, 2, "float"), rt.binary("*", rt.binary("*", aDist, centerWeightSq, 2, "float"), _u_lensDisplacement, 2, "float"), 2, "float")
        if _u_aspectLens:
            displacement = rt.assign_swizzle(displacement, "x", rt.binary("/", rt.swizzle(displacement, "x"), aspect, 1, "float"))
        isTileRendering = rt.binary(">", rt.length(_u_tileOffset), rt.f(0.0))
        maxDispPixels = rt.f(0.0)
        dispPixels = rt.f(0.0)
        if isTileRendering:
            maxDispPixels = rt.f(256.0)
            dispPixels = rt.length(rt.binary("*", displacement, dims, 2, "float"))
            if rt.binary(">", dispPixels, maxDispPixels):
                displacement = rt.binary("*", displacement, rt.binary("/", maxDispPixels, dispPixels, 1, "float"), 2, "float")
        warpedGlobalUV = (rt.binary("-", uv, displacement, 2, "float") if isTileRendering else rt.component_wise("fract", rt.binary("-", uv, displacement, 2, "float"), width=2))
        offset = rt.binary("/", rt.binary("-", rt.binary("*", warpedGlobalUV, dims, 2, "float"), _u_tileOffset, 2, "float"), tileDims, 2, "float")
        sampledUV = offset
        dx = rt.construct(2, 0.0)
        dy = rt.construct(2, 0.0)
        col = rt.construct(4, 0.0)
        if _u_antialias:
            dx = rt.dFdx(sampledUV)
            dy = rt.dFdy(sampledUV)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(_u_inputTex, rt.binary("+", rt.binary("+", sampledUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            g.fragColor = rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            g.fragColor = rt.texture(_u_inputTex, sampledUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.uses_derivatives = True
