def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_trailTex = T["trailTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        trailColor = rt.texture(_u_trailTex, uv)
        decay = rt.component_wise("clamp", rt.binary("/", _u_intensity, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor[:] = rt.component_wise("clamp", rt.binary("*", trailColor, decay, 4, "float"), rt.f(0.0), rt.f(1.0), width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
