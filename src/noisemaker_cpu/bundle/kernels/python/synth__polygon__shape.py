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
    _u_sides = U["sides"]
    _u_radius = U["radius"]
    _u_smoothing = U["smoothing"]
    _u_rotation = U["rotation"]
    _u_fgColor = U["fgColor"]
    _u_fgAlpha = U["fgAlpha"]
    _u_bgColor = U["bgColor"]
    _u_bgAlpha = U["bgAlpha"]
    def polygon__vec2_float(st, sides):
        st = rt.copy(st)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "y"), rt.swizzle(st, "x"), width=1), rt.f(3.14159265), 1)
        r = rt.binary("/", rt.f(6.2831853), sides, 1)
        return rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1), 1), width=1), r, 1), a, 1), width=1), rt.length(st), 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        st = rt.binary("*", rt.binary("-", st, rt.f(0.5), 2), rt.f(2.0), 2)
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspect, 1))
        c = rt.component_wise("cos", rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1), rt.f(180.0), 1), width=1)
        s = rt.component_wise("sin", rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1), rt.f(180.0), 1), width=1)
        st = rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(st, "x"), c, 1), rt.binary("*", rt.swizzle(st, "y"), s, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(st, "x"), s, 1), rt.binary("*", rt.swizzle(st, "y"), c, 1), 1))
        sidesF = rt.construct(1, rt.component_wise("max", _u_sides, rt.i(3), width=1))
        if rt.binary("==", _u_sides, rt.i(3)):
            st = rt.construct(2, rt.swizzle(st, "y"), rt.unary("-", rt.swizzle(st, "x")))
        d = rt.binary("/", polygon__vec2_float(st, sidesF), rt.component_wise("cos", rt.binary("/", rt.f(3.14159265359), sidesF, 1), width=1), 1)
        m = rt.component_wise("smoothstep", _u_radius, rt.binary("-", _u_radius, _u_smoothing, 1), d, width=1)
        fgMask = rt.binary("*", m, _u_fgAlpha, 1)
        bgMask = rt.binary("*", rt.binary("-", rt.f(1.0), m, 1), _u_bgAlpha, 1)
        totalAlpha = rt.binary("+", fgMask, bgMask, 1)
        outColor = (rt.binary("/", rt.binary("+", rt.binary("*", _u_fgColor, fgMask, 3), rt.binary("*", _u_bgColor, bgMask, 3), 3), totalAlpha, 3) if rt.binary(">", totalAlpha, rt.f(0.0)) else rt.construct(3, rt.f(0.0)))
        g.fragColor = rt.construct(4, rt.binary("*", outColor, totalAlpha, 3), totalAlpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
