def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_mode = U.get("mode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        color = rt.texture(_u_inputTex, uv)
        if rt.binary("==", _u_mode, rt.i(1)):
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("min", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"), width=3))
        else:
            color = rt.assign_swizzle(color, "rgb", rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
