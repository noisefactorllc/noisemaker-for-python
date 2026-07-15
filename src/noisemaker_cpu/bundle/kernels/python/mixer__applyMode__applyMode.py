def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_mode = U["mode"]
    _u_mixAmt = U["mixAmt"]
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
    def rgb2hsv__vec3(c):
        c = rt.copy(c)
        K = rt.construct(4, rt.f(0.0), rt.binary("/", rt.unary("-", rt.f(1.0)), rt.f(3.0), 1), rt.binary("/", rt.f(2.0), rt.f(3.0), 1), rt.unary("-", rt.f(1.0)))
        p = rt.component_wise("mix", rt.construct(4, rt.swizzle(c, "bg"), rt.swizzle(K, "wz")), rt.construct(4, rt.swizzle(c, "gb"), rt.swizzle(K, "xy")), rt.component_wise("step", rt.swizzle(c, "b"), rt.swizzle(c, "g"), width=1), width=4)
        q = rt.component_wise("mix", rt.construct(4, rt.swizzle(p, "xyw"), rt.swizzle(c, "r")), rt.construct(4, rt.swizzle(c, "r"), rt.swizzle(p, "yzx")), rt.component_wise("step", rt.swizzle(p, "x"), rt.swizzle(c, "r"), width=1), width=4)
        d = rt.binary("-", rt.swizzle(q, "x"), rt.component_wise("min", rt.swizzle(q, "w"), rt.swizzle(q, "y"), width=1), 1)
        e = rt.f(1.0e-10)
        return rt.construct(3, rt.component_wise("abs", rt.binary("+", rt.swizzle(q, "z"), rt.binary("/", rt.binary("-", rt.swizzle(q, "w"), rt.swizzle(q, "y"), 1), rt.binary("+", rt.binary("*", rt.f(6.0), d, 1), e, 1), 1), 1), width=1), rt.binary("/", d, rt.binary("+", rt.swizzle(q, "x"), e, 1), 1), rt.swizzle(q, "x"))
    def hsv2rgb__vec3(c):
        c = rt.copy(c)
        K = rt.construct(4, rt.f(1.0), rt.binary("/", rt.f(2.0), rt.f(3.0), 1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1), rt.f(3.0))
        p = rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.component_wise("fract", rt.binary("+", rt.swizzle(c, "xxx"), rt.swizzle(K, "xyz"), 3), width=3), rt.f(6.0), 3), rt.swizzle(K, "www"), 3), width=3)
        return rt.binary("*", rt.swizzle(c, "z"), rt.component_wise("mix", rt.swizzle(K, "xxx"), rt.component_wise("clamp", rt.binary("-", p, rt.swizzle(K, "xxx"), 3), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(c, "y"), width=3), 3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2))
        a = rgb2hsv__vec3(rt.swizzle(color1, "rgb"))
        b = rgb2hsv__vec3(rt.swizzle(color2, "rgb"))
        resultHSV = rt.construct(3, 0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            resultHSV = rt.construct(3, rt.swizzle(a, "x"), rt.swizzle(a, "y"), rt.swizzle(b, "z"))
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                resultHSV = rt.construct(3, rt.swizzle(b, "x"), rt.swizzle(a, "y"), rt.swizzle(a, "z"))
            else:
                resultHSV = rt.construct(3, rt.swizzle(a, "x"), rt.swizzle(b, "y"), rt.swizzle(a, "z"))
        middle = rt.construct(4, hsv2rgb__vec3(resultHSV), rt.f(1.0))
        amt = map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        color = rt.construct(4, 0.0)
        if rt.binary("<", amt, rt.f(0.5)):
            factor = rt.binary("*", amt, rt.f(2.0), 1)
            color = rt.component_wise("mix", color1, middle, factor, width=4)
        else:
            factor = rt.binary("*", rt.binary("-", amt, rt.f(0.5), 1), rt.f(2.0), 1)
            color = rt.component_wise("mix", middle, color2, factor, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
