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
    _u_vignetteBrightness = U["vignetteBrightness"]
    _u_alpha = U["alpha"]
    def computeVignetteMask__vec2_vec2(uv, dims):
        uv = rt.copy(uv)
        dims = rt.copy(dims)
        if (bool(rt.binary("<=", rt.swizzle(dims, "x"), rt.f(0.0))) or bool(rt.binary("<=", rt.swizzle(dims, "y"), rt.f(0.0)))):
            return rt.f(0.0)
        delta = rt.component_wise("abs", rt.binary("-", uv, rt.construct(2, rt.f(0.5)), 2, "float"), width=2)
        aspect = rt.binary("/", rt.swizzle(dims, "x"), rt.component_wise("max", rt.swizzle(dims, "y"), rt.f(1.0), width=1), 1, "float")
        scaled = rt.construct(2, rt.binary("*", rt.swizzle(delta, "x"), aspect, 1, "float"), rt.swizzle(delta, "y"))
        maxRadius = rt.length(rt.construct(2, rt.binary("*", aspect, rt.f(0.5), 1, "float"), rt.f(0.5)))
        if rt.binary("<=", maxRadius, rt.f(0.0)):
            return rt.f(0.0)
        normalizedDist = rt.component_wise("clamp", rt.binary("/", rt.length(scaled), maxRadius, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("*", normalizedDist, normalizedDist, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        dims = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), dims, 2, "float")
        texel = rt.texture(_u_inputTex, uv)
        mask = computeVignetteMask__vec2_vec2(globalUV, dims)
        brightnessRgb = rt.construct(3, _u_vignetteBrightness)
        edgeBlend = rt.component_wise("mix", rt.swizzle(texel, "rgb"), brightnessRgb, mask, width=3)
        finalRgb = rt.component_wise("mix", rt.swizzle(texel, "rgb"), edgeBlend, _u_alpha, width=3)
        g.fragColor = rt.construct(4, finalRgb, rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
