def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_VIEW_MODE = U.get("VIEW_MODE", 0)
    _u_BLEND_MODE = U.get("BLEND_MODE", 0)
    _u_BLUR_LAYER = U.get("BLUR_LAYER", 0)
    _u_clearValue = U.get("clearValue", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        g.fragColor[:] = rt.construct(4, _u_clearValue)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
