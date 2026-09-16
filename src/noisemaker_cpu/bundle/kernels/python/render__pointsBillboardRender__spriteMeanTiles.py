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
    _u_spriteTex = T["spriteTex"]
    _u_shapeMode = U.get("shapeMode", 0)
    _u_aperture = U.get("aperture", rt.f(0.0))
    _u_viewMode = U.get("viewMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        if (bool((bool(rt.binary("!=", _u_shapeMode, rt.i(0))) or bool(rt.binary("<=", _u_aperture, rt.f(0.0))))) or bool(rt.binary("==", _u_viewMode, rt.i(0)))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        dims = rt.texture_size(_u_spriteTex)
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        node = rt.binary("/", coord, rt.i(32), 2, "int")
        tile = rt.binary("%", coord, rt.i(32), 2, "int")
        start = rt.component_wise("max", rt.binary("/", rt.binary("*", tile, dims, 2, "int"), rt.i(32), 2, "int"), rt.binary("-", rt.binary("/", rt.binary("*", rt.binary("-", node, rt.i(1), 2, "int"), dims, 2, "int"), rt.i(4), 2, "int"), rt.i(1), 2, "int"), width=2)
        end = rt.component_wise("min", rt.binary("/", rt.binary("*", rt.binary("+", tile, rt.i(1), 2, "int"), dims, 2, "int"), rt.i(32), 2, "int"), rt.binary("+", rt.binary("/", rt.binary("*", rt.binary("+", node, rt.i(1), 2, "int"), dims, 2, "int"), rt.i(4), 2, "int"), rt.i(1), 2, "int"), width=2)
        total = rt.construct(4, rt.f(0.0))
        y = rt.swizzle(start, "y")
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", y, rt.swizzle(end, "y"))):
                break
            x = rt.swizzle(start, "x")
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<", x, rt.swizzle(end, "x"))):
                    break
                uv = rt.binary("/", rt.binary("+", rt.construct(2, x, y), rt.f(0.5), 2, "float"), rt.construct(2, dims), 2, "float")
                weight = rt.component_wise("max", rt.construct(2, rt.f(0.0)), rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", uv, rt.f(4.0), 2, "float"), rt.construct(2, node), 2, "float"), width=2), 2, "float"), width=2)
                total[:] = rt.binary("+", total, rt.binary("*", rt.texel_fetch(_u_spriteTex, rt.construct(2, x, y, base="int"), rt.i(0)), rt.binary("*", rt.swizzle(weight, "x"), rt.swizzle(weight, "y"), 1, "float"), 4, "float"), 4, "float")
        g.fragColor[:] = rt.binary("/", total, rt.construct(1, rt.binary("*", rt.swizzle(dims, "x"), rt.swizzle(dims, "y"), 1, "int")), 4, "float")
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
