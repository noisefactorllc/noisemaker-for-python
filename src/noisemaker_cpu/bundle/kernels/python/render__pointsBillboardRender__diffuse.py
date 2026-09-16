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
    _u_trailTex = T["trailTex"]
    _u_defocusTex = T["defocusTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_aperture = U.get("aperture", rt.f(0.0))
    _u_viewMode = U.get("viewMode", 0)
    _u_blendMode = U.get("blendMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def sampleDefocus__vec2(uv):
        uv = rt.copy(uv, "float")
        dims = rt.texture_size(_u_defocusTex)
        p = rt.binary("-", rt.binary("*", uv, rt.construct(2, dims), 2, "float"), rt.f(0.5), 2, "float")
        lo = rt.construct(2, rt.component_wise("floor", p, width=2), base="int")
        f = rt.component_wise("fract", p, width=2)
        a = rt.component_wise("clamp", lo, rt.construct(2, rt.i(0), base="int"), rt.binary("-", dims, rt.i(1), 2, "int"), width=2)
        b = rt.component_wise("clamp", rt.binary("+", lo, rt.i(1), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", dims, rt.i(1), 2, "int"), width=2)
        return rt.component_wise("mix", rt.component_wise("mix", rt.texel_fetch(_u_defocusTex, a, rt.i(0)), rt.texel_fetch(_u_defocusTex, rt.construct(2, rt.swizzle(b, "x"), rt.swizzle(a, "y"), base="int"), rt.i(0)), rt.swizzle(f, "x"), width=4), rt.component_wise("mix", rt.texel_fetch(_u_defocusTex, rt.construct(2, rt.swizzle(a, "x"), rt.swizzle(b, "y"), base="int"), rt.i(0)), rt.texel_fetch(_u_defocusTex, b, rt.i(0)), rt.swizzle(f, "x"), width=4), rt.swizzle(f, "y"), width=4)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        trailColor = rt.texture(_u_trailTex, uv)
        decay = rt.component_wise("clamp", rt.binary("/", _u_intensity, rt.f(100.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor[:] = rt.component_wise("clamp", rt.binary("*", trailColor, decay, 4, "float"), rt.f(0.0), rt.f(1.0), width=4)
        if (bool((bool(rt.binary("==", _u_blendMode, rt.i(0))) and bool(rt.binary(">", _u_aperture, rt.f(0.0))))) and bool(rt.binary("!=", _u_viewMode, rt.i(0)))):
            g.fragColor[:] = rt.binary("+", g.fragColor, sampleDefocus__vec2(uv), 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
