def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    _u_speed = U.get("speed", 0)
    _u_time = U.get("time", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    def rotate2D__float(angle):
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(4, c, rt.unary("-", s), s, c)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        angle = _u_rotation
        if rt.binary("!=", _u_speed, rt.i(0)):
            angle = rt.binary("+", angle, rt.binary("*", rt.binary("*", _u_time, rt.f(360.0), 1, "float"), rt.construct(1, _u_speed), 1, "float"), 1, "float")
        aspect = rt.binary("/", rt.construct(1, rt.swizzle(texSize, "x")), rt.construct(1, rt.swizzle(texSize, "y")), 1, "float")
        center = rt.construct(2, rt.f(0.5))
        uv[:] = rt.binary("-", uv, center, 2, "float")
        uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), aspect, 1, "float"))
        uv[:] = rt.matrix_mult(rotate2D__float(rt.binary("/", rt.binary("*", rt.unary("-", angle), g.TAU, 1, "float"), rt.f(360.0), 1, "float")), uv, 2)
        uv = rt.assign_swizzle(uv, "x", rt.binary("/", rt.swizzle(uv, "x"), aspect, 1, "float"))
        uv[:] = rt.binary("+", uv, center, 2, "float")
        if rt.binary("==", _u_wrap, rt.i(0)):
            uv[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                uv[:] = rt.component_wise("fract", uv, width=2)
            else:
                uv[:] = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor[:] = rt.texture(_u_inputTex, uv)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
