def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_detail = U["detail"]
    def sort2__vec3_vec3(a, b):
        a = rt.copy(a)
        b = rt.copy(b)
        lo = rt.component_wise("min", a, b, width=3)
        hi = rt.component_wise("max", a, b, width=3)
        a = lo
        b = hi
    def main__void():
        stride = rt.component_wise("mix", rt.f(3.0), rt.f(1.0), rt.binary("/", rt.component_wise("clamp", _u_detail, rt.f(0.0), rt.f(100.0), width=1), rt.f(100.0), 1), width=1)
        texel = rt.binary("/", stride, _u_resolution, 2)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        s0 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.unary("-", rt.swizzle(texel, "y"))), 2))
        s1 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(texel, "y"))), 2))
        s2 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.unary("-", rt.swizzle(texel, "y"))), 2))
        s3 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.f(0.0)), 2))
        s4 = rt.texture(_u_inputTex, uv)
        s5 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2))
        s6 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.unary("-", rt.swizzle(texel, "x")), rt.swizzle(texel, "y")), 2))
        s7 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2))
        s8 = rt.texture(_u_inputTex, rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.swizzle(texel, "y")), 2))
        p0 = rt.swizzle(s0, "rgb")
        p1 = rt.swizzle(s1, "rgb")
        p2 = rt.swizzle(s2, "rgb")
        p3 = rt.swizzle(s3, "rgb")
        p4 = rt.swizzle(s4, "rgb")
        p5 = rt.swizzle(s5, "rgb")
        p6 = rt.swizzle(s6, "rgb")
        p7 = rt.swizzle(s7, "rgb")
        p8 = rt.swizzle(s8, "rgb")
        sort2__vec3_vec3(p1, p2)
        sort2__vec3_vec3(p4, p5)
        sort2__vec3_vec3(p7, p8)
        sort2__vec3_vec3(p0, p1)
        sort2__vec3_vec3(p3, p4)
        sort2__vec3_vec3(p6, p7)
        sort2__vec3_vec3(p1, p2)
        sort2__vec3_vec3(p4, p5)
        sort2__vec3_vec3(p7, p8)
        sort2__vec3_vec3(p0, p3)
        sort2__vec3_vec3(p5, p8)
        sort2__vec3_vec3(p4, p7)
        sort2__vec3_vec3(p3, p6)
        sort2__vec3_vec3(p1, p4)
        sort2__vec3_vec3(p2, p5)
        sort2__vec3_vec3(p4, p7)
        sort2__vec3_vec3(p4, p2)
        sort2__vec3_vec3(p6, p4)
        sort2__vec3_vec3(p4, p2)
        g.fragColor = rt.construct(4, p4, rt.swizzle(s4, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
