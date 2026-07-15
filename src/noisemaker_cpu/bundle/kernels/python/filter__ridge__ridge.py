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
    _u_level = U["level"]
    def ridge_transform__vec4_float(value, lvl):
        value = rt.copy(value)
        denom = rt.component_wise("max", lvl, rt.binary("-", rt.f(1.0), lvl, 1, "float"), width=1)
        result = rt.binary("-", rt.construct(4, rt.f(1.0)), rt.binary("/", rt.component_wise("abs", rt.binary("-", value, rt.construct(4, lvl), 4, "float"), width=4), denom, 4, "float"), 4, "float")
        return rt.component_wise("clamp", result, rt.construct(4, rt.f(0.0)), rt.construct(4, rt.f(1.0)), width=4)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        dims = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dims), 2, "float")
        texel = rt.texture(_u_inputTex, uv)
        ridged = ridge_transform__vec4_float(texel, _u_level)
        out_color = rt.construct(4, rt.swizzle(ridged, "xyz"), rt.f(1.0))
        g.fragColor = out_color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
