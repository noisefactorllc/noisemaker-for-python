def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_renderScale = U["renderScale"]
    _u_cellSize = U["cellSize"]
    _u_seed = U["seed"]
    _u_colorMode = U["colorMode"]
    g.GLYPH_COUNT = rt.i(16)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def hash__vec2(p):
        p = rt.copy(p)
        v = pcg__vec3(cpu_uvec3__float_float_float(rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1))), rt.i(0)))
        return rt.binary("/", rt.swizzle(v, "x"), rt.f(4294967295.0), 1)
    def glyphPixel__int_int_int(g, x, y):
        row = rt.i(0)
        if rt.binary("==", g, rt.i(0)):
            return rt.f(0.0)
        else:
            if rt.binary("==", g, rt.i(1)):
                if rt.binary("==", y, rt.i(5)):
                    row = rt.i(4)
                else:
                    return rt.f(0.0)
            else:
                if rt.binary("==", g, rt.i(2)):
                    if rt.binary("||", rt.binary("==", y, rt.i(1)), rt.binary("==", y, rt.i(5))):
                        row = rt.i(4)
                    else:
                        return rt.f(0.0)
                else:
                    if rt.binary("==", g, rt.i(3)):
                        if rt.binary("==", y, rt.i(3)):
                            row = rt.i(14)
                        else:
                            return rt.f(0.0)
                    else:
                        if rt.binary("==", g, rt.i(4)):
                            if rt.binary("||", rt.binary("==", y, rt.i(1)), rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("||", rt.binary("==", y, rt.i(4)), rt.binary("==", y, rt.i(5))))):
                                row = rt.i(4)
                            else:
                                if rt.binary("==", y, rt.i(3)):
                                    row = rt.i(14)
                                else:
                                    return rt.f(0.0)
                        else:
                            if rt.binary("==", g, rt.i(5)):
                                if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(4))):
                                    row = rt.i(14)
                                else:
                                    return rt.f(0.0)
                            else:
                                if rt.binary("==", g, rt.i(6)):
                                    if rt.binary("||", rt.binary("==", y, rt.i(1)), rt.binary("==", y, rt.i(5))):
                                        row = rt.i(10)
                                    else:
                                        if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(4))):
                                            row = rt.i(4)
                                        else:
                                            if rt.binary("==", y, rt.i(3)):
                                                row = rt.i(14)
                                            else:
                                                return rt.f(0.0)
                                else:
                                    if rt.binary("==", g, rt.i(7)):
                                        if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(5))):
                                            row = rt.i(14)
                                        else:
                                            if rt.binary("||", rt.binary("==", y, rt.i(3)), rt.binary("==", y, rt.i(4))):
                                                row = rt.i(10)
                                            else:
                                                return rt.f(0.0)
                                    else:
                                        if rt.binary("==", g, rt.i(8)):
                                            if rt.binary("||", rt.binary("==", y, rt.i(1)), rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("||", rt.binary("==", y, rt.i(4)), rt.binary("==", y, rt.i(5))))):
                                                row = rt.i(10)
                                            else:
                                                if rt.binary("==", y, rt.i(3)):
                                                    row = rt.i(4)
                                                else:
                                                    return rt.f(0.0)
                                        else:
                                            if rt.binary("==", g, rt.i(9)):
                                                if rt.binary("||", rt.binary("==", y, rt.i(1)), rt.binary("||", rt.binary("==", y, rt.i(3)), rt.binary("==", y, rt.i(5)))):
                                                    row = rt.i(10)
                                                else:
                                                    if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(4))):
                                                        row = rt.i(31)
                                                    else:
                                                        return rt.f(0.0)
                                            else:
                                                if rt.binary("==", g, rt.i(10)):
                                                    if rt.binary("==", y, rt.i(0)):
                                                        row = rt.i(25)
                                                    else:
                                                        if rt.binary("==", y, rt.i(1)):
                                                            row = rt.i(26)
                                                        else:
                                                            if rt.binary("==", y, rt.i(2)):
                                                                row = rt.i(4)
                                                            else:
                                                                if rt.binary("==", y, rt.i(3)):
                                                                    row = rt.i(9)
                                                                else:
                                                                    if rt.binary("==", y, rt.i(4)):
                                                                        row = rt.i(11)
                                                                    else:
                                                                        if rt.binary("==", y, rt.i(5)):
                                                                            row = rt.i(19)
                                                                        else:
                                                                            return rt.f(0.0)
                                                else:
                                                    if rt.binary("==", g, rt.i(11)):
                                                        if rt.binary("==", y, rt.i(0)):
                                                            row = rt.i(4)
                                                        else:
                                                            if rt.binary("==", y, rt.i(1)):
                                                                row = rt.i(10)
                                                            else:
                                                                if rt.binary("==", y, rt.i(2)):
                                                                    row = rt.i(17)
                                                                else:
                                                                    if rt.binary("==", y, rt.i(3)):
                                                                        row = rt.i(31)
                                                                    else:
                                                                        if rt.binary("||", rt.binary("==", y, rt.i(4)), rt.binary("==", y, rt.i(5))):
                                                                            row = rt.i(17)
                                                                        else:
                                                                            return rt.f(0.0)
                                                    else:
                                                        if rt.binary("==", g, rt.i(12)):
                                                            if rt.binary("||", rt.binary("==", y, rt.i(0)), rt.binary("==", y, rt.i(1))):
                                                                row = rt.i(17)
                                                            else:
                                                                if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(3))):
                                                                    row = rt.i(21)
                                                                else:
                                                                    if rt.binary("==", y, rt.i(4)):
                                                                        row = rt.i(27)
                                                                    else:
                                                                        if rt.binary("==", y, rt.i(5)):
                                                                            row = rt.i(10)
                                                                        else:
                                                                            return rt.f(0.0)
                                                        else:
                                                            if rt.binary("==", g, rt.i(13)):
                                                                if rt.binary("==", y, rt.i(0)):
                                                                    row = rt.i(17)
                                                                else:
                                                                    if rt.binary("==", y, rt.i(1)):
                                                                        row = rt.i(27)
                                                                    else:
                                                                        if rt.binary("||", rt.binary("==", y, rt.i(2)), rt.binary("==", y, rt.i(3))):
                                                                            row = rt.i(21)
                                                                        else:
                                                                            if rt.binary("||", rt.binary("==", y, rt.i(4)), rt.binary("==", y, rt.i(5))):
                                                                                row = rt.i(17)
                                                                            else:
                                                                                return rt.f(0.0)
                                                            else:
                                                                if rt.binary("==", g, rt.i(14)):
                                                                    if rt.binary("||", rt.binary("==", y, rt.i(0)), rt.binary("==", y, rt.i(6))):
                                                                        row = rt.i(14)
                                                                    else:
                                                                        if rt.binary("==", y, rt.i(1)):
                                                                            row = rt.i(17)
                                                                        else:
                                                                            if rt.binary("==", y, rt.i(2)):
                                                                                row = rt.i(23)
                                                                            else:
                                                                                if rt.binary("==", y, rt.i(3)):
                                                                                    row = rt.i(21)
                                                                                else:
                                                                                    if rt.binary("==", y, rt.i(4)):
                                                                                        row = rt.i(22)
                                                                                    else:
                                                                                        if rt.binary("==", y, rt.i(5)):
                                                                                            row = rt.i(16)
                                                                                        else:
                                                                                            return rt.f(0.0)
                                                                else:
                                                                    return rt.f(1.0)
        bit = rt.binary("&", rt.binary(">>", row, rt.binary("-", rt.i(4), x, 1), 1), rt.i(1), 1)
        return bit
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        pixelCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        cs = rt.component_wise("max", rt.construct(1, rt.binary("*", _u_cellSize, _u_renderScale, 1)), rt.i(1), width=1)
        isTileRendering = rt.binary(">", rt.length(_u_tileOffset), rt.f(0.0))
        if isTileRendering:
            cs = rt.component_wise("min", cs, rt.i(512), width=1)
        csf = cs
        cellIndex = rt.component_wise("floor", rt.binary("/", pixelCoord, csf, 2), width=2)
        localPos = rt.component_wise("fract", rt.binary("/", pixelCoord, csf, 2), width=2)
        gx = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(localPos, "x"), rt.f(5.0), 1), width=1))
        gy = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(localPos, "y"), rt.f(7.0), 1), width=1))
        gx = rt.component_wise("clamp", gx, rt.i(0), rt.i(4), width=1)
        gy = rt.component_wise("clamp", gy, rt.i(0), rt.i(6), width=1)
        cellCenter = rt.binary("*", rt.binary("+", cellIndex, rt.f(0.5), 2), csf, 2)
        sampleUV = rt.binary("/", rt.binary("-", cellCenter, _u_tileOffset, 2), resolution, 2)
        if isTileRendering:
            sampleUV = rt.component_wise("clamp", sampleUV, rt.f(0.0), rt.f(1.0), width=2)
        srcColor = rt.texture(_u_inputTex, sampleUV)
        luma = rt.dot(rt.swizzle(srcColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        glyphIdx = rt.construct(1, rt.component_wise("floor", rt.binary("*", luma, g.GLYPH_COUNT, 1), width=1))
        glyphIdx = rt.component_wise("clamp", glyphIdx, rt.i(0), rt.binary("-", g.GLYPH_COUNT, rt.i(1), 1), width=1)
        cellHash = hash__vec2(rt.binary("+", cellIndex, rt.binary("*", _u_seed, rt.f(0.37), 1), 2))
        variant = rt.construct(1, rt.component_wise("floor", rt.binary("*", cellHash, rt.f(3.0), 1), width=1))
        if rt.binary("&&", rt.binary("==", variant, rt.i(1)), rt.binary("&&", rt.binary(">", glyphIdx, rt.i(0)), rt.binary("<", glyphIdx, rt.binary("-", g.GLYPH_COUNT, rt.i(1), 1)))):
            glyphIdx = glyphIdx
        else:
            if rt.binary("&&", rt.binary("==", variant, rt.i(2)), rt.binary(">", glyphIdx, rt.i(1))):
                glyphIdx = rt.binary("-", glyphIdx, rt.i(1), 1)
        glyphVal = glyphPixel__int_int_int(glyphIdx, gx, gy)
        if rt.binary(">", _u_colorMode, rt.i(0)):
            g.fragColor = rt.construct(4, rt.binary("*", rt.swizzle(srcColor, "rgb"), glyphVal, 3), rt.f(1.0))
        else:
            g.fragColor = rt.construct(4, rt.construct(3, glyphVal), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
