def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_color = U["color"]
    _u_alpha = U["alpha"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        g.fragColor = rt.construct(4, rt.binary("*", _u_color, _u_alpha, 3, "float"), _u_alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
