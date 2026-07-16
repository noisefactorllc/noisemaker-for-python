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
    _u_sharpness = U["sharpness"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        c = rt.texture(_u_inputTex, st)
        l = rt.dot(rt.swizzle(c, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        e = rt.component_wise("smoothstep", rt.binary("-", _u_level, _u_sharpness, 1, "float"), rt.binary("+", _u_level, _u_sharpness, 1, "float"), l, width=1)
        g.fragColor = rt.construct(4, rt.construct(3, e), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
