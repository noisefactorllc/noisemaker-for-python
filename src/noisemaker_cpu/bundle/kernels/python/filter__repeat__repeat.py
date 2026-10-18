def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_aspect = U.get("aspect", rt.f(0.0))
    _u_x = U.get("x", rt.f(0.0))
    _u_y = U.get("y", rt.f(0.0))
    _u_offsetX = U.get("offsetX", rt.f(0.0))
    _u_offsetY = U.get("offsetY", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        globalUV = rt.construct(2, rt.fdiv(globalCoord, _u_fullResolution, 2))
        st = rt.copy_decl(globalUV, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        ((_vector_write_0_0 := rt.swizzle(rt.binary("+", rt.binary("*", st, rt.construct_raw(2, _u_x, _u_y), 2, 'float'), rt.construct_raw(2, rt.binary("*", _u_offsetX, _u_aspect, 1, "float"), _u_offsetY), 2, 'float'), "x")), (_vector_write_0_1 := rt.swizzle(rt.binary("+", rt.binary("*", st, rt.construct_raw(2, _u_x, _u_y), 2, 'float'), rt.construct_raw(2, rt.binary("*", _u_offsetX, _u_aspect, 1, "float"), _u_offsetY), 2, 'float'), "y")), st.__setitem__(0, _vector_write_0_0), st.__setitem__(1, _vector_write_0_1), st)[-1]
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), _u_aspect, 1, "float"))
        if rt.binary("==", _u_wrap, rt.i(0)):
            st[:] = rt.component_wise("abs", rt.construct(2, rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(2.0), rt.component_wise("floor", rt.binary("*", rt.binary("+", st, rt.f(1.0), 2, 'float'), rt.f(0.5), 2, 'float'), width=2), 2, 'float')), 2, 'float')), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                st[:] = rt.component_wise("fract", st, width=2)
            else:
                st[:] = rt.component_wise("clamp", st, rt.f(0.0), rt.f(1.0), width=2)
        localUV = rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", st, _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        if rt.binary("==", _u_wrap, rt.i(0)):
            localUV[:] = rt.component_wise("abs", rt.construct(2, rt.binary("-", localUV, rt.construct(2, rt.binary("*", rt.f(2.0), rt.component_wise("floor", rt.binary("*", rt.binary("+", localUV, rt.f(1.0), 2, 'float'), rt.f(0.5), 2, 'float'), width=2), 2, 'float')), 2, 'float')), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                localUV[:] = rt.component_wise("fract", localUV, width=2)
            else:
                localUV[:] = rt.component_wise("clamp", localUV, rt.f(0.0), rt.f(1.0), width=2)
        g.fragColor[:] = rt.construct(4, rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb"), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
