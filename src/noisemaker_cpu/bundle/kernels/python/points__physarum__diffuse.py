def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_trailTex = T["trailTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_decay = U.get("decay", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        if _u_resetState:
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        trailColor = rt.texture(_u_trailTex, uv)
        persistence = rt.component_wise("clamp", rt.binary("-", rt.f(1.0), _u_decay, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor[:] = rt.binary("*", trailColor, persistence, 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
