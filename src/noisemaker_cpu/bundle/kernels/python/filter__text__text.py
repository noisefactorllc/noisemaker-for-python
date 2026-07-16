def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_textTex = T["textTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_matteColor = U.get("matteColor", rt.construct(3, 0.0))
    _u_matteOpacity = U.get("matteOpacity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        inputColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        text = rt.texture(_u_textTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_textTex)), 2, "float"))
        textPresence = rt.swizzle(text, "a")
        matteAlpha = _u_matteOpacity
        rgb = rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(text, "rgb"), textPresence, 3, "float"), rt.binary("*", rt.binary("*", rt.swizzle(inputColor, "rgb"), rt.binary("-", rt.f(1.0), textPresence, 1, "float"), 3, "float"), rt.binary("-", rt.f(1.0), matteAlpha, 1, "float"), 3, "float"), 3, "float"), rt.binary("*", rt.binary("*", _u_matteColor, matteAlpha, 3, "float"), rt.binary("-", rt.f(1.0), textPresence, 1, "float"), 3, "float"), 3, "float")
        alpha = rt.component_wise("max", textPresence, rt.component_wise("mix", rt.swizzle(inputColor, "a"), rt.f(1.0), matteAlpha, width=1), width=1)
        g.fragColor = rt.construct(4, rgb, alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
