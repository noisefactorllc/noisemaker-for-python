def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_aspect = U["aspect"]
    _u_x = U["x"]
    _u_y = U["y"]
    _u_offsetX = U["offsetX"]
    _u_offsetY = U["offsetY"]
    _u_wrap = U["wrap"]
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        st = globalUV
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        st = rt.binary("+", rt.binary("*", st, rt.construct(2, _u_x, _u_y), 2, "float"), rt.construct(2, rt.binary("*", _u_offsetX, _u_aspect, 1, "float"), _u_offsetY), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        if rt.binary("==", _u_wrap, rt.i(0)):
            st = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", st, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                st = rt.component_wise("fract", st, width=2)
            else:
                st = rt.component_wise("clamp", st, rt.f(0.0), rt.f(1.0), width=2)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", st, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        if rt.binary("==", _u_wrap, rt.i(0)):
            localUV = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                localUV = rt.component_wise("fract", localUV, width=2)
            else:
                localUV = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor = rt.construct(4, rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
