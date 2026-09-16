def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_VIEW_MODE = U.get("VIEW_MODE", 0)
    _u_BLEND_MODE = U.get("BLEND_MODE", 0)
    _u_BLUR_LAYER = U.get("BLUR_LAYER", 0)
    _u_xyzTex = T["xyzTex"]
    _u_rotateX = U.get("rotateX", rt.f(0.0))
    _u_rotateY = U.get("rotateY", rt.f(0.0))
    _u_posZ = U.get("posZ", rt.f(0.0))
    g.viewMode = _u_VIEW_MODE
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        dims = rt.texture_size(_u_xyzTex)
        pos = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        p = rt.swizzle(pos, "xyz")
        if (bool((bool((bool((bool((bool(rt.binary("==", g.viewMode, rt.i(1))) and bool(rt.binary("<", rt.component_wise("abs", rt.swizzle(p, "z"), width=1), rt.f(1.0))))) and bool(rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0))))) and bool(rt.binary("<=", rt.swizzle(p, "x"), rt.f(1.0))))) and bool(rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0))))) and bool(rt.binary("<=", rt.swizzle(p, "y"), rt.f(1.0)))):
            p = rt.assign_swizzle(p, "xy", rt.binary("-", rt.swizzle(p, "xy"), rt.f(0.5), 2, "float"))
            p = rt.assign_swizzle(p, "z", rt.f(0.0))
        p[:] = rt.construct(3, rt.swizzle(p, "x"), rt.binary("-", rt.binary("*", rt.swizzle(p, "y"), rt.component_wise("cos", _u_rotateX, width=1), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.component_wise("sin", _u_rotateX, width=1), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "y"), rt.component_wise("sin", _u_rotateX, width=1), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.component_wise("cos", _u_rotateX, width=1), 1, "float"), 1, "float"))
        p[:] = rt.construct(3, rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.component_wise("cos", _u_rotateY, width=1), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.component_wise("sin", _u_rotateY, width=1), 1, "float"), 1, "float"), rt.swizzle(p, "y"), rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.component_wise("sin", _u_rotateY, width=1), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.component_wise("cos", _u_rotateY, width=1), 1, "float"), 1, "float"))
        depth = rt.binary("-", rt.binary("+", rt.swizzle(p, "z"), _u_posZ, 1, "float"), rt.f(80.0), 1, "float")
        key = (depth if (bool(rt.binary(">=", rt.swizzle(pos, "w"), rt.f(0.5))) and bool(rt.binary("<=", rt.component_wise("abs", depth, width=1), rt.f(3.402823466e+38)))) else rt.f(3.402823466e+38))
        g.fragColor[:] = rt.construct(4, key, rt.construct(1, rt.binary("+", rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(dims, "x"), 1, "int"), rt.swizzle(coord, "x"), 1, "int")), rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
