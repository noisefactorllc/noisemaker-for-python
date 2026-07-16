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
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    _u_maskMode = U.get("maskMode", False)
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        maskVal = rt.f(0.0)
        if _u_maskMode:
            maskVal = rt.dot(rt.swizzle(color2, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
            g.fragColor = rt.construct(4, rt.swizzle(color1, "rgb"), rt.binary("*", rt.swizzle(color1, "a"), maskVal, 1, "float"))
            return
        color = rt.construct(4, 0.0)
        AoverB = rt.construct(4, 0.0)
        BoverA = rt.construct(4, 0.0)
        if rt.binary("<", _u_mixAmt, rt.f(0.0)):
            AoverB = rt.binary("+", rt.binary("*", color2, rt.binary("-", rt.f(1.0), rt.swizzle(color1, "a"), 1, "float"), 4, "float"), rt.binary("*", color1, rt.swizzle(color1, "a"), 4, "float"), 4, "float")
            color = rt.component_wise("mix", color1, AoverB, map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), width=4)
        else:
            BoverA = rt.binary("+", rt.binary("*", color1, rt.binary("-", rt.f(1.0), rt.swizzle(color2, "a"), 1, "float"), 4, "float"), rt.binary("*", color2, rt.swizzle(color2, "a"), 4, "float"), 4, "float")
            color = rt.component_wise("mix", BoverA, color2, map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
