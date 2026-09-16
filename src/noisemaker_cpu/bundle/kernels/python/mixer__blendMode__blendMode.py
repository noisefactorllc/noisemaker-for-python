def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_mode = U.get("mode", 0)
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def blendOverlay__float_float(a, b):
        return (rt.binary("*", rt.binary("*", rt.f(2.0), a, 1, "float"), b, 1, "float") if rt.binary("<", a, rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), b, 1, "float"), 1, "float"), 1, "float"))
    def blendSoftLight__float_float(base, blend):
        return (rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), blend, 1, "float"), rt.binary("*", rt.binary("*", base, base, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), blend, 1, "float"), 1, "float"), 1, "float"), 1, "float") if rt.binary("<", blend, rt.f(0.5)) else rt.binary("+", rt.binary("*", rt.component_wise("sqrt", base, width=1), rt.binary("-", rt.binary("*", rt.f(2.0), blend, 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), rt.binary("-", rt.f(1.0), blend, 1, "float"), 1, "float"), 1, "float"))
    def applyBlendMode__vec4_vec4_int(color1, color2, m):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        if rt.binary("==", m, rt.i(0)):
            return rt.component_wise("min", rt.binary("+", color1, color2, 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", m, rt.i(1)):
            return rt.binary("-", rt.f(1.0), rt.component_wise("min", rt.binary("/", rt.binary("-", rt.f(1.0), color1, 4, "float"), rt.component_wise("max", color2, rt.construct(4, rt.f(0.001)), width=4), 4, "float"), rt.construct(4, rt.f(1.0)), width=4), 4, "float")
        if rt.binary("==", m, rt.i(2)):
            return rt.component_wise("min", color1, color2, width=4)
        if rt.binary("==", m, rt.i(3)):
            return rt.component_wise("abs", rt.binary("-", color1, color2, 4, "float"), width=4)
        if rt.binary("==", m, rt.i(4)):
            return rt.component_wise("min", rt.binary("/", color1, rt.component_wise("max", rt.binary("-", rt.f(1.0), color2, 4, "float"), rt.construct(4, rt.f(0.001)), width=4), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        if rt.binary("==", m, rt.i(5)):
            return rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), color1, 4, "float"), color2, 4, "float"), 4, "float")
        if rt.binary("==", m, rt.i(6)):
            return rt.construct(4, blendOverlay__float_float(rt.swizzle(color2, "r"), rt.swizzle(color1, "r")), blendOverlay__float_float(rt.swizzle(color2, "g"), rt.swizzle(color1, "g")), blendOverlay__float_float(rt.swizzle(color2, "b"), rt.swizzle(color1, "b")), rt.f(1.0))
        if rt.binary("==", m, rt.i(7)):
            return rt.component_wise("max", color1, color2, width=4)
        if rt.binary("==", m, rt.i(8)):
            return rt.binary("*", rt.binary("+", color1, color2, 4, "float"), rt.f(0.5), 4, "float")
        if rt.binary("==", m, rt.i(9)):
            return rt.binary("*", color1, color2, 4, "float")
        if rt.binary("==", m, rt.i(10)):
            return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4, "float"), color2, 4, "float"), width=4), 4, "float")
        if rt.binary("==", m, rt.i(11)):
            return rt.construct(4, blendOverlay__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendOverlay__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendOverlay__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.f(1.0))
        if rt.binary("==", m, rt.i(12)):
            return rt.binary("+", rt.binary("-", rt.component_wise("min", color1, color2, width=4), rt.component_wise("max", color1, color2, width=4), 4, "float"), rt.construct(4, rt.f(1.0)), 4, "float")
        if rt.binary("==", m, rt.i(13)):
            return rt.binary("-", rt.construct(4, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4, "float"), rt.binary("-", rt.construct(4, rt.f(1.0)), color2, 4, "float"), 4, "float"), 4, "float")
        if rt.binary("==", m, rt.i(14)):
            return rt.construct(4, blendSoftLight__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendSoftLight__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendSoftLight__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.f(1.0))
        return rt.component_wise("max", rt.binary("-", color1, color2, 4, "float"), rt.construct(4, rt.f(0.0)), width=4)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        amt = map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        opacity = (amt if rt.binary("==", _u_mode, rt.i(8)) else rt.component_wise("min", rt.binary("*", amt, rt.f(2.0), 1, "float"), rt.f(1.0), width=1))
        sourceAlpha = rt.binary("*", rt.swizzle(color2, "a"), opacity, 1, "float")
        source = rt.binary("*", rt.swizzle(color2, "rgb"), opacity, 3, "float")
        baseColor = rt.construct(4, 0.0)
        sourceColor = rt.construct(4, 0.0)
        blended = rt.construct(3, 0.0)
        if rt.binary("!=", _u_mode, rt.i(8)):
            baseColor = rt.construct(4, (rt.binary("/", rt.swizzle(color1, "rgb"), rt.swizzle(color1, "a"), 3, "float") if rt.binary(">", rt.swizzle(color1, "a"), rt.f(0.0)) else rt.construct(3, rt.f(0.0))), rt.f(1.0))
            sourceColor = rt.construct(4, (rt.binary("/", rt.swizzle(color2, "rgb"), rt.swizzle(color2, "a"), 3, "float") if rt.binary(">", rt.swizzle(color2, "a"), rt.f(0.0)) else rt.construct(3, rt.f(0.0))), rt.f(1.0))
            blended = rt.swizzle(applyBlendMode__vec4_vec4_int(baseColor, sourceColor, _u_mode), "rgb")
            blended[:] = rt.component_wise("mix", blended, rt.swizzle(sourceColor, "rgb"), rt.component_wise("max", rt.binary("-", rt.binary("*", amt, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), rt.f(0.0), width=1), width=3)
            source[:] = rt.binary("+", rt.binary("*", source, rt.binary("-", rt.f(1.0), rt.swizzle(color1, "a"), 1, "float"), 3, "float"), rt.binary("*", rt.binary("*", blended, sourceAlpha, 3, "float"), rt.swizzle(color1, "a"), 3, "float"), 3, "float")
        g.fragColor[:] = rt.construct(4, rt.binary("+", source, rt.binary("*", rt.swizzle(color1, "rgb"), rt.binary("-", rt.f(1.0), sourceAlpha, 1, "float"), 3, "float"), 3, "float"), rt.binary("+", sourceAlpha, rt.binary("*", rt.swizzle(color1, "a"), rt.binary("-", rt.f(1.0), sourceAlpha, 1, "float"), 1, "float"), 1, "float"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
