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
    _u_shape = U["shape"]
    _u_power = U["power"]
    _u_hardness = U["hardness"]
    _u_blendMode = U["blendMode"]
    def clamp01__float(x):
        return rt.component_wise("clamp", x, rt.f(0.0), rt.f(1.0), width=1)
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
            return color2
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
    def distanceMetric__vec2_vec2_int(p, corner, m):
        p = rt.copy(p)
        corner = rt.copy(corner)
        mm = rt.binary("%", m, rt.i(3), 1)
        if rt.binary("<", mm, rt.i(0)):
            mm = rt.binary("+", mm, rt.i(3), 1)
        ap = rt.component_wise("abs", p, width=2)
        if rt.binary("==", mm, rt.i(0)):
            d = rt.length(ap)
            maxD = rt.length(corner)
            return rt.binary("/", d, maxD, 1)
        if rt.binary("==", mm, rt.i(1)):
            d = rt.binary("+", rt.swizzle(ap, "x"), rt.swizzle(ap, "y"), 1)
            maxD = rt.binary("+", rt.swizzle(corner, "x"), rt.swizzle(corner, "y"), 1)
            return rt.binary("/", d, maxD, 1)
        d = rt.component_wise("max", rt.swizzle(ap, "x"), rt.swizzle(ap, "y"), width=1)
        maxD = rt.component_wise("max", rt.swizzle(corner, "x"), rt.swizzle(corner, "y"), width=1)
        return rt.binary("/", d, maxD, 1)
    def main__void():
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2)
        edgeColor = rt.texture(_u_inputTex, st)
        centerColor = rt.texture(_u_tex, st)
        minRes = rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        p = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", rt.f(0.5), _u_fullResolution, 2), 2), rt.binary("*", rt.f(0.5), minRes, 1), 2)
        corner = rt.binary("/", _u_fullResolution, minRes, 2)
        dist01 = clamp01__float(distanceMetric__vec2_vec2_int(p, corner, _u_shape))
        scaledPower = rt.component_wise("mix", rt.f(0.1), rt.f(25.05), rt.binary("/", rt.binary("+", _u_power, rt.f(100.0), 1), rt.f(200.0), 1), width=1)
        mask = rt.component_wise("pow", dist01, scaledPower, width=1)
        h = rt.component_wise("clamp", rt.binary("/", _u_hardness, rt.f(100.0), 1), rt.f(0.0), rt.f(0.995), width=1)
        width = rt.binary("*", rt.binary("-", rt.f(1.0), h, 1), rt.f(0.5), 1)
        mask = rt.component_wise("smoothstep", rt.binary("-", rt.f(0.5), width, 1), rt.binary("+", rt.f(0.5), width, 1), mask, width=1)
        f_low = rt.component_wise("clamp", rt.binary("/", rt.binary("+", _u_power, rt.f(100.0), 1), rt.f(5.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        f_high = rt.component_wise("clamp", rt.binary("/", rt.binary("-", rt.f(100.0), _u_power, 1), rt.f(5.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        mask = rt.component_wise("mix", rt.f(1.0), mask, f_low, width=1)
        mask = rt.binary("*", mask, f_high, 1)
        blended = applyBlendMode__vec4_vec4_int(centerColor, edgeColor, _u_blendMode)
        color = rt.component_wise("mix", centerColor, blended, mask, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(edgeColor, "a"), rt.swizzle(centerColor, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
