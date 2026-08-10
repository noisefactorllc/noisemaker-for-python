def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_OCTAVES = U.get("OCTAVES", 0)
    _u_RIDGES = U.get("RIDGES", 0)
    _u_OUTPUT_MODE = U.get("OUTPUT_MODE", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def permute__vec3(x):
        x = rt.copy(x, "float")
        return rt.component_wise("mod", rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3, "float"), rt.f(10.0), 3, "float"), x, 3, "float"), rt.f(289.0), width=3)
    def permute__vec4(x):
        x = rt.copy(x, "float")
        return rt.component_wise("mod", rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 4, "float"), rt.f(10.0), 4, "float"), x, 4, "float"), rt.f(289.0), width=4)
    def taylorInvSqrt__vec4(r):
        r = rt.copy(r, "float")
        return rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), r, 4, "float"), 4, "float")
    def simplex3D__vec3(v):
        v = rt.copy(v, "float")
        C = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"))
        D = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        v[:] = rt.binary("+", v, rt.binary("*", rt.construct(1, _u_seed), rt.f(0.1271), 1, "float"), 3, "float")
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yyy")), 3, "float"), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i, 3, "float"), rt.dot(i, rt.swizzle(C, "xxx")), 3, "float")
        _g = rt.component_wise("step", rt.swizzle(x0, "yzx"), rt.swizzle(x0, "xyz"), width=3)
        l = rt.binary("-", rt.f(1.0), _g, 3, "float")
        i1 = rt.component_wise("min", rt.swizzle(_g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        i2 = rt.component_wise("max", rt.swizzle(_g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3, "float"), rt.swizzle(C, "xxx"), 3, "float")
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3, "float"), rt.swizzle(C, "yyy"), 3, "float")
        x3 = rt.binary("-", x0, rt.swizzle(D, "yyy"), 3, "float")
        i[:] = rt.component_wise("mod", i, rt.f(289.0), width=3)
        p = permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.swizzle(i, "z"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "z"), rt.swizzle(i2, "z"), rt.f(1.0)), 4, "float")), rt.swizzle(i, "y"), 4, "float"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "y"), rt.swizzle(i2, "y"), rt.f(1.0)), 4, "float")), rt.swizzle(i, "x"), 4, "float"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "x"), rt.swizzle(i2, "x"), rt.f(1.0)), 4, "float"))
        n_ = rt.f(0.142857142857)
        ns = rt.binary("-", rt.binary("*", n_, rt.swizzle(D, "wyz"), 3, "float"), rt.swizzle(D, "xzx"), 3, "float")
        j = rt.binary("-", p, rt.binary("*", rt.f(49.0), rt.component_wise("floor", rt.binary("*", rt.binary("*", p, rt.swizzle(ns, "z"), 4, "float"), rt.swizzle(ns, "z"), 4, "float"), width=4), 4, "float"), 4, "float")
        x_ = rt.component_wise("floor", rt.binary("*", j, rt.swizzle(ns, "z"), 4, "float"), width=4)
        y_ = rt.component_wise("floor", rt.binary("-", j, rt.binary("*", rt.f(7.0), x_, 4, "float"), 4, "float"), width=4)
        x = rt.binary("+", rt.binary("*", x_, rt.swizzle(ns, "x"), 4, "float"), rt.swizzle(ns, "yyyy"), 4, "float")
        y = rt.binary("+", rt.binary("*", y_, rt.swizzle(ns, "x"), 4, "float"), rt.swizzle(ns, "yyyy"), 4, "float")
        h = rt.binary("-", rt.binary("-", rt.f(1.0), rt.component_wise("abs", x, width=4), 4, "float"), rt.component_wise("abs", y, width=4), 4, "float")
        b0 = rt.construct(4, rt.swizzle(x, "xy"), rt.swizzle(y, "xy"))
        b1 = rt.construct(4, rt.swizzle(x, "zw"), rt.swizzle(y, "zw"))
        s0 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b0, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        s1 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b1, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        sh = rt.unary("-", rt.component_wise("step", h, rt.construct(4, rt.f(0.0)), width=4))
        a0 = rt.binary("+", rt.swizzle(b0, "xzyw"), rt.binary("*", rt.swizzle(s0, "xzyw"), rt.swizzle(sh, "xxyy"), 4, "float"), 4, "float")
        a1 = rt.binary("+", rt.swizzle(b1, "xzyw"), rt.binary("*", rt.swizzle(s1, "xzyw"), rt.swizzle(sh, "zzww"), 4, "float"), 4, "float")
        p0 = rt.construct(3, rt.swizzle(a0, "xy"), rt.swizzle(h, "x"))
        p1 = rt.construct(3, rt.swizzle(a0, "zw"), rt.swizzle(h, "y"))
        p2 = rt.construct(3, rt.swizzle(a1, "xy"), rt.swizzle(h, "z"))
        p3 = rt.construct(3, rt.swizzle(a1, "zw"), rt.swizzle(h, "w"))
        norm = taylorInvSqrt__vec4(rt.construct(4, rt.dot(p0, p0), rt.dot(p1, p1), rt.dot(p2, p2), rt.dot(p3, p3)))
        p0[:] = rt.binary("*", p0, rt.swizzle(norm, "x"), 3, "float")
        p1[:] = rt.binary("*", p1, rt.swizzle(norm, "y"), 3, "float")
        p2[:] = rt.binary("*", p2, rt.swizzle(norm, "z"), 3, "float")
        p3[:] = rt.binary("*", p3, rt.swizzle(norm, "w"), 3, "float")
        m = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.construct(4, rt.dot(x0, x0), rt.dot(x1, x1), rt.dot(x2, x2), rt.dot(x3, x3)), 4, "float"), rt.f(0.0), width=4)
        m[:] = rt.binary("*", m, m, 4, "float")
        return rt.binary("*", rt.f(42.0), rt.dot(rt.binary("*", m, m, 4, "float"), rt.construct(4, rt.dot(p0, x0), rt.dot(p1, x1), rt.dot(p2, x2), rt.dot(p3, x3))), 1, "float")
    def fbmSimplex3D__vec3(p):
        p = rt.copy(p, "float")
        sum = rt.f(0.0)
        amp = rt.f(1.0)
        freq = rt.f(1.0)
        maxAmp = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, _u_OCTAVES)):
                break
            n = simplex3D__vec3(rt.binary("*", p, freq, 3, "float"))
            sum = rt.binary("+", sum, rt.binary("*", n, amp, 1, "float"), 1, "float")
            maxAmp = rt.binary("+", maxAmp, amp, 1, "float")
            freq = rt.binary("*", freq, rt.f(2.0), 1, "float")
            amp = rt.binary("*", amp, rt.f(0.5), 1, "float")
        return rt.binary("/", sum, maxAmp, 1, "float")
    def curlNoise3D__vec3(p):
        p = rt.copy(p, "float")
        eps = rt.f(1.0)
        a = rt.binary("*", rt.binary("/", rt.binary("+", rt.binary("*", rt.component_wise("sin", rt.binary("*", _u_time, rt.f(6.28318), 1, "float"), width=1), _u_speed, 1, "float"), rt.f(1.0), 1, "float"), rt.construct(1, _u_OCTAVES), 1, "float"), rt.f(0.2), 1, "float")
        b = rt.binary("*", rt.binary("/", rt.binary("+", rt.binary("*", rt.component_wise("cos", rt.binary("*", _u_time, rt.f(6.28318), 1, "float"), width=1), _u_speed, 1, "float"), rt.f(1.0), 1, "float"), rt.construct(1, _u_OCTAVES), 1, "float"), rt.f(0.2), 1, "float")
        offset1 = rt.construct(3, a, b, rt.f(0.0))
        offset2 = rt.construct(3, rt.binary("-", rt.f(31.416), a, 1, "float"), rt.binary("-", rt.f(47.853), b, 1, "float"), rt.f(12.793))
        offset3 = rt.construct(3, rt.binary("-", rt.f(93.719), b, 1, "float"), rt.binary("-", rt.f(61.248), a, 1, "float"), rt.f(73.561))
        Fx_py = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), offset1, 3, "float"))
        Fx_ny = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), offset1, 3, "float"))
        Fx_pz = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), offset1, 3, "float"))
        Fx_nz = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), offset1, 3, "float"))
        Fy_px = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), offset2, 3, "float"))
        Fy_nx = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), offset2, 3, "float"))
        Fy_pz = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), offset2, 3, "float"))
        Fy_nz = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float"), offset2, 3, "float"))
        Fz_px = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), offset3, 3, "float"))
        Fz_nx = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float"), offset3, 3, "float"))
        Fz_py = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), offset3, 3, "float"))
        Fz_ny = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float"), offset3, 3, "float"))
        dFx_dy = rt.binary("/", rt.binary("-", Fx_py, Fx_ny, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        dFx_dz = rt.binary("/", rt.binary("-", Fx_pz, Fx_nz, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        dFy_dx = rt.binary("/", rt.binary("-", Fy_px, Fy_nx, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        dFy_dz = rt.binary("/", rt.binary("-", Fy_pz, Fy_nz, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        dFz_dx = rt.binary("/", rt.binary("-", Fz_px, Fz_nx, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        dFz_dy = rt.binary("/", rt.binary("-", Fz_py, Fz_ny, 1, "float"), rt.binary("*", rt.f(2.0), eps, 1, "float"), 1, "float")
        return rt.construct(3, rt.binary("-", dFz_dy, dFy_dz, 1, "float"), rt.binary("-", dFx_dz, dFz_dx, 1, "float"), rt.binary("-", dFy_dx, dFx_dy, 1, "float"))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float")
        centered = rt.binary("*", rt.binary("-", uv, rt.f(0.5), 2, "float"), rt.construct(2, aspect, rt.f(1.0)), 2, "float")
        p = rt.construct(3, rt.binary("*", centered, rt.binary("-", rt.f(21.0), _u_scale, 1, "float"), 2, "float"), rt.f(0.5))
        curl = curlNoise3D__vec3(p)
        curl[:] = rt.binary("+", rt.binary("*", rt.component_wise("tanh", rt.binary("*", curl, _u_intensity, 3, "float"), width=3), rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        color = rt.construct(3, 0.0)
        if rt.binary("==", _u_OUTPUT_MODE, rt.i(0)):
            color[:] = rt.construct(3, rt.swizzle(curl, "x"))
        else:
            if rt.binary("==", _u_OUTPUT_MODE, rt.i(1)):
                color[:] = rt.construct(3, rt.swizzle(curl, "y"))
            else:
                if rt.binary("==", _u_OUTPUT_MODE, rt.i(2)):
                    color[:] = rt.construct(3, rt.swizzle(curl, "z"))
                else:
                    if rt.binary("==", _u_OUTPUT_MODE, rt.i(3)):
                        color[:] = curl
                    else:
                        curlCentered = rt.binary("-", rt.binary("*", curl, rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
                        mag = rt.length(curlCentered)
                        color[:] = rt.construct(3, mag)
        if _u_RIDGES:
            color[:] = rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", color, rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float"), width=3), 3, "float")
        g.fragColor[:] = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
