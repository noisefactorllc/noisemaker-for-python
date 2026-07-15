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
    def blendOverlay__float_float(a, b):
        return (rt.binary("*", rt.binary("*", rt.f(2.0), a, 1), b, 1) if rt.binary("<", a, rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), a, 1), 1), rt.binary("-", rt.f(1.0), b, 1), 1), 1))
    def blendSoftLight__float_float(base, blend):
        return (rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), base, 1), blend, 1), rt.binary("*", rt.binary("*", base, base, 1), rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), blend, 1), 1), 1), 1) if rt.binary("<", blend, rt.f(0.5)) else rt.binary("+", rt.binary("*", rt.component_wise("sqrt", base, width=1), rt.binary("-", rt.binary("*", rt.f(2.0), blend, 1), rt.f(1.0), 1), 1), rt.binary("*", rt.binary("*", rt.f(2.0), base, 1), rt.binary("-", rt.f(1.0), blend, 1), 1), 1))
    def applyBlendMode__vec4_vec4_int(color1, color2, m):
        color1 = rt.copy(color1)
        color2 = rt.copy(color2)
        if rt.binary("==", m, rt.i(0)):
            return rt.component_wise("min", rt.binary("+", color1, color2, 4), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", m, rt.i(1)):
            return rt.binary("-", rt.f(1.0), rt.component_wise("min", rt.binary("/", rt.binary("-", rt.f(1.0), color1, 4), rt.component_wise("max", color2, rt.construct(4, rt.f(0.001)), width=4), 4), rt.construct(4, rt.f(1.0)), width=4), 4)
        if rt.binary("==", m, rt.i(2)):
            return rt.component_wise("min", color1, color2, width=4)
        if rt.binary("==", m, rt.i(3)):
            return rt.component_wise("abs", rt.binary("-", color1, color2, 4), width=4)
        if rt.binary("==", m, rt.i(4)):
            return rt.component_wise("min", rt.binary("/", color1, rt.component_wise("max", rt.binary("-", rt.f(1.0), color2, 4), rt.construct(4, rt.f(0.001)), width=4), 4), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", m, rt.i(5)):
            return rt.binary("-", rt.binary("+", color1, color2, 4), rt.binary("*", rt.binary("*", rt.f(2.0), color1, 4), color2, 4), 4)
        if rt.binary("==", m, rt.i(6)):
            return rt.construct(4, blendOverlay__float_float(rt.swizzle(color2, "r"), rt.swizzle(color1, "r")), blendOverlay__float_float(rt.swizzle(color2, "g"), rt.swizzle(color1, "g")), blendOverlay__float_float(rt.swizzle(color2, "b"), rt.swizzle(color1, "b")), rt.f(1.0))
        if rt.binary("==", m, rt.i(7)):
            return rt.component_wise("max", color1, color2, width=4)
        if rt.binary("==", m, rt.i(8)):
            return rt.binary("*", rt.binary("+", color1, color2, 4), rt.f(0.5), 4)
        if rt.binary("==", m, rt.i(9)):
            return rt.binary("*", color1, color2, 4)
        if rt.binary("==", m, rt.i(10)):
            return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4), color2, 4), width=4), 4)
        if rt.binary("==", m, rt.i(11)):
            return rt.construct(4, blendOverlay__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendOverlay__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendOverlay__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.f(1.0))
        if rt.binary("==", m, rt.i(12)):
            return rt.binary("+", rt.binary("-", rt.component_wise("min", color1, color2, width=4), rt.component_wise("max", color1, color2, width=4), 4), rt.construct(4, rt.f(1.0)), 4)
        if rt.binary("==", m, rt.i(13)):
            return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4), rt.binary("-", rt.construct(4, rt.f(1.0)), color2, 4), 4), 4)
        if rt.binary("==", m, rt.i(14)):
            return rt.construct(4, blendSoftLight__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendSoftLight__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendSoftLight__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.f(1.0))
        return rt.component_wise("max", rt.binary("-", color1, color2, 4), rt.construct(4, rt.f(0.0)), width=4)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2))
        middle = applyBlendMode__vec4_vec4_int(color1, color2, _u_mode)
        amt = map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        color = rt.construct(4, 0.0)
        if rt.binary("<", amt, rt.f(0.5)):
            factor = rt.binary("*", amt, rt.f(2.0), 1)
            color = rt.component_wise("mix", color1, middle, factor, width=4)
        else:
            factor = rt.binary("*", rt.binary("-", amt, rt.f(0.5), 1), rt.f(2.0), 1)
            color = rt.component_wise("mix", middle, color2, factor, width=4)
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color1, "rgb"), rt.swizzle(color, "rgb"), rt.swizzle(color2, "a"), width=3))
        color = rt.assign_swizzle(color, "a", rt.binary("+", rt.binary("*", rt.swizzle(color2, "a"), amt, 1), rt.binary("*", rt.swizzle(color1, "a"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.swizzle(color2, "a"), amt, 1), 1), 1), 1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
