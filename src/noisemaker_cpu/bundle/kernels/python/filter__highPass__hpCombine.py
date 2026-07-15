def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_blurTex = T["blurTex"]
    _u_resolution = U["resolution"]
    _u_mono = U["mono"]
    def lum__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        src = rt.texture(_u_inputTex, uv)
        blur = rt.texture(_u_blurTex, uv)
        diff = rt.binary("-", rt.swizzle(src, "rgb"), rt.swizzle(blur, "rgb"), 3)
        hp = (rt.construct(3, rt.binary("+", lum__vec3(diff), rt.f(0.5), 1)) if _u_mono else rt.binary("+", diff, rt.f(0.5), 3))
        g.fragColor = rt.construct(4, rt.component_wise("clamp", hp, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
