def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_displacement = U.get("displacement", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalPixel = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalPixel, _u_fullResolution, 2, "float")
        maxDisplacementUV = rt.binary("/", rt.f(256.0), rt.swizzle(_u_fullResolution, "x"), 1, "float")
        boundedDisplacement = rt.component_wise("clamp", _u_displacement, rt.unary("-", maxDisplacementUV), maxDisplacementUV, width=1)
        redGlobalUV = rt.binary("+", globalUV, rt.construct(2, boundedDisplacement, rt.f(0.0)), 2, "float")
        redLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", redGlobalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        red = rt.texture(_u_inputTex, redLocalUV)
        greenLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", globalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        green = rt.texture(_u_inputTex, greenLocalUV)
        blueGlobalUV = rt.binary("-", globalUV, rt.construct(2, boundedDisplacement, rt.f(0.0)), 2, "float")
        blueLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", blueGlobalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        blue = rt.texture(_u_inputTex, blueLocalUV)
        g.fragColor[:] = rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(green, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
