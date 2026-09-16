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
    _u_orderTex = T["orderTex"]
    _u_runLength = U.get("runLength", 0)
    g.fragColor = rt.construct(4, 0.0)
    def keyAt__int_int(index, width):
        return rt.swizzle(rt.texel_fetch(_u_orderTex, rt.construct(2, rt.binary("%", index, width, 1, "int"), rt.binary("/", index, width, 1, "int"), base="int"), rt.i(0)), "rg")
    def before__vec2_vec2(a, b):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        return (bool(rt.binary("<", rt.swizzle(a, "x"), rt.swizzle(b, "x"))) or bool((bool(rt.binary("==", rt.swizzle(a, "x"), rt.swizzle(b, "x"))) and bool(rt.binary("<=", rt.swizzle(a, "y"), rt.swizzle(b, "y"))))))
    def main__void():
        dims = rt.texture_size(_u_orderTex)
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        index = rt.binary("+", rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(dims, "x"), 1, "int"), rt.swizzle(coord, "x"), 1, "int")
        count = rt.binary("*", rt.swizzle(dims, "x"), rt.swizzle(dims, "y"), 1, "int")
        if rt.binary(">=", _u_runLength, count):
            g.fragColor[:] = rt.texel_fetch(_u_orderTex, coord, rt.i(0))
            return
        start = rt.binary("*", rt.binary("/", index, rt.binary("*", rt.i(2), _u_runLength, 1, "int"), 1, "int"), rt.binary("*", rt.i(2), _u_runLength, 1, "int"), 1, "int")
        lengthA = rt.component_wise("min", _u_runLength, rt.binary("-", count, start, 1, "int"), width=1)
        lengthB = rt.component_wise("min", _u_runLength, rt.binary("-", rt.binary("-", count, start, 1, "int"), lengthA, 1, "int"), width=1)
        diagonal = rt.binary("-", index, start, 1, "int")
        low = rt.component_wise("max", rt.i(0), rt.binary("-", diagonal, lengthB, 1, "int"), width=1)
        high = rt.component_wise("min", diagonal, lengthA, width=1)
        step = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                step = rt.binary("+", step, rt.i(1), 1, "int")
            _for0_first = False
            if not ((bool(rt.binary("<", step, rt.i(22))) and bool(rt.binary("<", low, high)))):
                break
            mid = rt.binary("/", rt.binary("+", low, high, 1, "int"), rt.i(2), 1, "int")
            other = rt.binary("-", diagonal, mid, 1, "int")
            if (bool((bool(rt.binary("<", mid, lengthA)) and bool(rt.binary(">", other, rt.i(0))))) and bool(before__vec2_vec2(keyAt__int_int(rt.binary("+", start, mid, 1, "int"), rt.swizzle(dims, "x")), keyAt__int_int(rt.binary("-", rt.binary("+", rt.binary("+", start, lengthA, 1, "int"), other, 1, "int"), rt.i(1), 1, "int"), rt.swizzle(dims, "x"))))):
                low = rt.binary("+", mid, rt.i(1), 1, "int")
            else:
                high = mid
        other = rt.binary("-", diagonal, low, 1, "int")
        a = (keyAt__int_int(rt.binary("+", start, low, 1, "int"), rt.swizzle(dims, "x")) if rt.binary("<", low, lengthA) else rt.construct(2, rt.f(3.402823466e+38)))
        b = (keyAt__int_int(rt.binary("+", rt.binary("+", start, lengthA, 1, "int"), other, 1, "int"), rt.swizzle(dims, "x")) if rt.binary("<", other, lengthB) else rt.construct(2, rt.f(3.402823466e+38)))
        g.fragColor[:] = rt.construct(4, (a if before__vec2_vec2(a, b) else b), rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
