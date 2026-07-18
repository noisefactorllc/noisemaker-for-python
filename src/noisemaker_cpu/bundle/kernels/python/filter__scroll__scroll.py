def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_aspect = U.get("aspect", rt.f(0.0))
    _u_x = U.get("x", rt.f(0.0))
    _u_y = U.get("y", rt.f(0.0))
    _u_speedX = U.get("speedX", rt.f(0.0))
    _u_speedY = U.get("speedY", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    _u_inputTex = T["inputTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalUV = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        globalUV = rt.assign_swizzle(globalUV, "x", rt.binary("*", rt.swizzle(globalUV, "x"), _u_aspect, 1, "float"))
        offset = rt.construct(2, rt.binary("+", rt.unary("-", _u_x), rt.binary("*", _u_time, rt.unary("-", _u_speedX), 1, "float"), 1, "float"), rt.binary("+", _u_y, rt.binary("*", _u_time, _u_speedY, 1, "float"), 1, "float"))
        offset = rt.assign_swizzle(offset, "x", rt.binary("*", rt.swizzle(offset, "x"), _u_aspect, 1, "float"))
        globalUV[:] = rt.binary("+", globalUV, offset, 2, "float")
        globalUV = rt.assign_swizzle(globalUV, "x", rt.binary("/", rt.swizzle(globalUV, "x"), _u_aspect, 1, "float"))
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", globalUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        if rt.binary("==", _u_wrap, rt.i(0)):
            localUV[:] = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", localUV, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                localUV[:] = rt.component_wise("fract", localUV, width=2)
            else:
                localUV[:] = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor[:] = rt.construct(4, rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
