def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_aspect = U["aspect"]
    _u_scaleX = U["scaleX"]
    _u_scaleY = U["scaleY"]
    _u_centerX = U["centerX"]
    _u_centerY = U["centerY"]
    _u_wrap = U["wrap"]
    _u_inputTex = T["inputTex"]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        c = rt.construct(2, rt.unary("-", _u_centerX), _u_centerY)
        st = rt.binary("-", st, c, 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1))
        st = rt.binary("/", st, rt.construct(2, _u_scaleX, _u_scaleY), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), _u_aspect, 1))
        st = rt.binary("+", st, c, 2)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", st, _u_fullResolution, 2), _u_tileOffset, 2), _u_resolution, 2)
        if rt.binary("==", _u_wrap, rt.i(0)):
            localUV = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2), rt.f(2.0), width=2), rt.f(1.0), 2), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                localUV = rt.component_wise("fract", localUV, width=2)
            else:
                localUV = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor = rt.construct(4, rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
