def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blurTex = T["blurTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_amount = U.get("amount", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        blur = rt.texture(_u_blurTex, uv)
        diff = rt.binary("-", rt.swizzle(src, "rgb"), rt.swizzle(blur, "rgb"), 3, "float")
        t = rt.binary("/", _u_threshold, rt.f(100.0), 1, "float")
        mag = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", rt.swizzle(diff, "r"), width=1), rt.component_wise("abs", rt.swizzle(diff, "g"), width=1), width=1), rt.component_wise("abs", rt.swizzle(diff, "b"), width=1), width=1)
        gate = rt.component_wise("smoothstep", t, rt.binary("+", t, rt.f(0.02), 1, "float"), mag, width=1)
        outc = rt.binary("+", rt.swizzle(src, "rgb"), rt.binary("*", rt.binary("*", diff, rt.binary("/", _u_amount, rt.f(100.0), 1, "float"), 3, "float"), gate, 3, "float"), 3, "float")
        g.fragColor = rt.construct(4, rt.component_wise("clamp", outc, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
