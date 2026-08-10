def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_flipMode = U.get("flipMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        texSize = rt.texture_size(_u_inputTex)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        warpedUV = globalUV
        if rt.binary("==", _u_flipMode, rt.i(1)):
            warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
            warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
        else:
            if rt.binary("==", _u_flipMode, rt.i(2)):
                warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
            else:
                if rt.binary("==", _u_flipMode, rt.i(3)):
                    warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                else:
                    if rt.binary("==", _u_flipMode, rt.i(11)):
                        if rt.binary(">", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                            warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                    else:
                        if rt.binary("==", _u_flipMode, rt.i(12)):
                            if rt.binary("<", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                                warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                        else:
                            if rt.binary("==", _u_flipMode, rt.i(13)):
                                if rt.binary(">", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                    warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                            else:
                                if rt.binary("==", _u_flipMode, rt.i(14)):
                                    if rt.binary("<", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                        warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                                else:
                                    if rt.binary("==", _u_flipMode, rt.i(15)):
                                        if rt.binary(">", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                                            warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                                        if rt.binary(">", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                            warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_flipMode, rt.i(16)):
                                            if rt.binary(">", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                                                warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                                            if rt.binary("<", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                                warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                                        else:
                                            if rt.binary("==", _u_flipMode, rt.i(17)):
                                                if rt.binary("<", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                                                    warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                                                if rt.binary(">", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                                    warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
                                            else:
                                                if rt.binary("==", _u_flipMode, rt.i(18)):
                                                    if rt.binary("<", rt.swizzle(warpedUV, "x"), rt.f(0.5)):
                                                        warpedUV = rt.assign_swizzle(warpedUV, "x", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "x"), 1, "float"))
                                                    if rt.binary("<", rt.swizzle(warpedUV, "y"), rt.f(0.5)):
                                                        warpedUV = rt.assign_swizzle(warpedUV, "y", rt.binary("-", rt.f(1.0), rt.swizzle(warpedUV, "y"), 1, "float"))
        localUV = rt.component_wise("fract", rt.binary("/", rt.binary("-", rt.binary("*", warpedUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, texSize), 2, "float"), width=2)
        g.fragColor[:] = rt.texture(_u_inputTex, localUV)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
