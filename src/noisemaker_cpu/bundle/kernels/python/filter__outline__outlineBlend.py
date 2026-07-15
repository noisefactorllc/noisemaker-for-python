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
    _u_edgesTexture = T["edgesTexture"]
    _u_invert = U["invert"]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        dimensions = rt.texture_size(_u_inputTex)
        if (bool(rt.binary("==", rt.swizzle(dimensions, "x"), rt.i(0))) or bool(rt.binary("==", rt.swizzle(dimensions, "y"), rt.i(0)))):
            g.fragColor = rt.construct(4, rt.f(0.0))
            return
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, dimensions), 2, "float")
        base = rt.texture(_u_inputTex, uv)
        edges = rt.texture(_u_edgesTexture, uv)
        strength = rt.component_wise("clamp", rt.swizzle(edges, "r"), rt.f(0.0), rt.f(1.0), width=1)
        outlineColor = (rt.construct(3, rt.f(1.0)) if rt.binary(">", _u_invert, rt.f(0.5)) else rt.construct(3, rt.f(0.0)))
        out_rgb = rt.component_wise("mix", rt.swizzle(base, "rgb"), outlineColor, strength, width=3)
        g.fragColor = rt.construct(4, out_rgb, rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
