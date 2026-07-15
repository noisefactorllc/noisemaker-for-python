def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_displacement = U["displacement"]
    def main__void():
        globalPixel = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        globalUV = rt.binary("/", globalPixel, _u_fullResolution, 2)
        maxDisplacementUV = rt.binary("/", rt.f(256.0), rt.swizzle(_u_fullResolution, "x"), 1)
        boundedDisplacement = rt.component_wise("clamp", _u_displacement, rt.unary("-", maxDisplacementUV), maxDisplacementUV, width=1)
        redGlobalUV = rt.binary("+", globalUV, rt.construct(2, boundedDisplacement, rt.f(0.0)), 2)
        redLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", redGlobalUV, _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2)
        red = rt.texture(_u_inputTex, redLocalUV)
        greenLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", globalUV, _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2)
        green = rt.texture(_u_inputTex, greenLocalUV)
        blueGlobalUV = rt.binary("-", globalUV, rt.construct(2, boundedDisplacement, rt.f(0.0)), 2)
        blueLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", blueGlobalUV, _u_fullResolution, 2), _u_tileOffset, 2), rt.construct(2, rt.texture_size(_u_inputTex)), 2)
        blue = rt.texture(_u_inputTex, blueLocalUV)
        g.fragColor = rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(green, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
