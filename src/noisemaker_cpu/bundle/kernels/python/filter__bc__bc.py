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
    _u_brightness = U.get("brightness", rt.f(0.0))
    _u_contrast = U.get("contrast", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        color = rt.texture(_u_inputTex, uv)
        color = rt.assign_swizzle(color, "rgb", rt.binary("*", rt.swizzle(color, "rgb"), _u_brightness, 3, "float"))
        contrastFactor = rt.binary("*", _u_contrast, rt.f(2.0), 1, "float")
        color = rt.assign_swizzle(color, "rgb", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(color, "rgb"), rt.f(0.5), 3, "float"), contrastFactor, 3, "float"), rt.f(0.5), 3, "float"))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
