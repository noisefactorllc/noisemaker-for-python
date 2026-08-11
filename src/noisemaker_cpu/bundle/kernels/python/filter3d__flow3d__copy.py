def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_BEHAVIOR = U.get("BEHAVIOR", 0)
    _u_sourceTex = T["sourceTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_sourceTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        g.fragColor[:] = rt.texture(_u_sourceTex, uv)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
