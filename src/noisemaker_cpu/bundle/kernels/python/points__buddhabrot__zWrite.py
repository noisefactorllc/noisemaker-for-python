def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    g.fragColor = rt.construct(4, 0.0)
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        pos = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        if rt.binary("<", rt.swizzle(pos, "w"), rt.f(0.5)):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        cRe = rt.swizzle(vel, "x")
        cIm = rt.swizzle(vel, "y")
        stepI = rt.construct(1, rt.swizzle(vel, "z"), base="int")
        z = rt.construct(2, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(2048))):
                break
            if rt.binary(">=", i, stepI):
                break
            zr = rt.binary("+", rt.binary("-", rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), cRe, 1, "float")
            zi = rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(z, "x"), 1, "float"), rt.swizzle(z, "y"), 1, "float"), cIm, 1, "float")
            (z.__setitem__(0, zr), z.__setitem__(1, zi), z)[-1]
        g.fragColor[:] = rt.construct(4, rt.swizzle(z, "x"), rt.swizzle(z, "y"), rt.f(0.0), rt.f(0.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
