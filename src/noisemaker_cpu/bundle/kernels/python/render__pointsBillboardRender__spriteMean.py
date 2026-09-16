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
    _u_tilesTex = T["tilesTex"]
    _u_shapeMode = U.get("shapeMode", 0)
    _u_aperture = U.get("aperture", rt.f(0.0))
    _u_viewMode = U.get("viewMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    def proceduralCoverage__void():
        if rt.binary("==", _u_shapeMode, rt.i(1)):
            return rt.f(0.713220537)
        if rt.binary("==", _u_shapeMode, rt.i(2)):
            return rt.f(0.310907274)
        if rt.binary("==", _u_shapeMode, rt.i(3)):
            return rt.f(0.680000007)
        if rt.binary("==", _u_shapeMode, rt.i(4)):
            return rt.f(0.519999981)
        if rt.binary("==", _u_shapeMode, rt.i(5)):
            return rt.f(0.0951406509)
        if rt.binary("==", _u_shapeMode, rt.i(6)):
            return rt.f(0.103062622)
        return rt.f(0.362012237)
    def main__void():
        if (bool(rt.binary("<=", _u_aperture, rt.f(0.0))) or bool(rt.binary("==", _u_viewMode, rt.i(0)))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        if rt.binary("!=", _u_shapeMode, rt.i(0)):
            g.fragColor[:] = rt.construct(4, proceduralCoverage__void())
            return
        origin = rt.binary("*", rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int"), rt.i(32), 2, "int")
        total = rt.construct(4, rt.f(0.0))
        y = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", y, rt.i(32))):
                break
            x = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<", x, rt.i(32))):
                    break
                total[:] = rt.binary("+", total, rt.texel_fetch(_u_tilesTex, rt.binary("+", origin, rt.construct(2, x, y, base="int"), 2, "int"), rt.i(0)), 4, "float")
        g.fragColor[:] = total
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
