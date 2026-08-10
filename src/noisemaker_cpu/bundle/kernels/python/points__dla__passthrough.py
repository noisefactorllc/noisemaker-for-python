def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_gridTex = T["gridTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_matteOpacity = U.get("matteOpacity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        inputCol = rt.texture(_u_inputTex, uv)
        grid = rt.texture(_u_gridTex, uv)
        gridStrength = rt.component_wise("clamp", rt.swizzle(grid, "a"), rt.f(0.0), rt.f(1.0), width=1)
        gridColor = rt.swizzle(grid, "rgb")
        matteAlpha = _u_matteOpacity
        color = rt.component_wise("mix", rt.binary("*", rt.swizzle(inputCol, "rgb"), matteAlpha, 3, "float"), gridColor, gridStrength, width=3)
        alpha = rt.component_wise("max", gridStrength, matteAlpha, width=1)
        g.fragColor[:] = rt.construct(4, color, alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
