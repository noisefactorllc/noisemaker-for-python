def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_OCTAVES = U["OCTAVES"]
    _u_RIDGES = U["RIDGES"]
    _u_OUTPUT_MODE = U["OUTPUT_MODE"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_scale = U["scale"]
    _u_seed = U["seed"]
    _u_speed = U["speed"]
    _u_intensity = U["intensity"]
    def permute__vec3(x):
        x = rt.copy(x)
        return rt.component_wise("mod", rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 3), rt.f(10.0), 3), x, 3), rt.f(289.0), width=3)
    def permute__vec4(x):
        x = rt.copy(x)
        return rt.component_wise("mod", rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 4), rt.f(10.0), 4), x, 4), rt.f(289.0), width=4)
    def taylorInvSqrt__vec4(r):
        r = rt.copy(r)
        return rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), r, 4), 4)
    def simplex3D__vec3(v):
        v = rt.copy(v)
        C = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1))
        D = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        v = rt.binary("+", v, rt.binary("*", _u_seed, rt.f(0.1271), 1), 3)
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yyy")), 3), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i, 3), rt.dot(i, rt.swizzle(C, "xxx")), 3)
        g = rt.component_wise("step", rt.swizzle(x0, "yzx"), rt.swizzle(x0, "xyz"), width=3)
        l = rt.binary("-", rt.f(1.0), g, 3)
        i1 = rt.component_wise("min", rt.swizzle(g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        i2 = rt.component_wise("max", rt.swizzle(g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3), rt.swizzle(C, "xxx"), 3)
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3), rt.swizzle(C, "yyy"), 3)
        x3 = rt.binary("-", x0, rt.swizzle(D, "yyy"), 3)
        i = rt.component_wise("mod", i, rt.f(289.0), width=3)
        p = permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.binary("+", permute__vec4(rt.binary("+", rt.swizzle(i, "z"), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "z"), rt.swizzle(i2, "z"), rt.f(1.0)), 4)), rt.swizzle(i, "y"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "y"), rt.swizzle(i2, "y"), rt.f(1.0)), 4)), rt.swizzle(i, "x"), 4), rt.construct(4, rt.f(0.0), rt.swizzle(i1, "x"), rt.swizzle(i2, "x"), rt.f(1.0)), 4))
        n_ = rt.f(0.142857142857)
        ns = rt.binary("-", rt.binary("*", n_, rt.swizzle(D, "wyz"), 3), rt.swizzle(D, "xzx"), 3)
        j = rt.binary("-", p, rt.binary("*", rt.f(49.0), rt.component_wise("floor", rt.binary("*", rt.binary("*", p, rt.swizzle(ns, "z"), 4), rt.swizzle(ns, "z"), 4), width=4), 4), 4)
        x_ = rt.component_wise("floor", rt.binary("*", j, rt.swizzle(ns, "z"), 4), width=4)
        y_ = rt.component_wise("floor", rt.binary("-", j, rt.binary("*", rt.f(7.0), x_, 4), 4), width=4)
        x = rt.binary("+", rt.binary("*", x_, rt.swizzle(ns, "x"), 4), rt.swizzle(ns, "yyyy"), 4)
        y = rt.binary("+", rt.binary("*", y_, rt.swizzle(ns, "x"), 4), rt.swizzle(ns, "yyyy"), 4)
        h = rt.binary("-", rt.binary("-", rt.f(1.0), rt.component_wise("abs", x, width=4), 4), rt.component_wise("abs", y, width=4), 4)
        b0 = rt.construct(4, rt.swizzle(x, "xy"), rt.swizzle(y, "xy"))
        b1 = rt.construct(4, rt.swizzle(x, "zw"), rt.swizzle(y, "zw"))
        s0 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b0, width=4), rt.f(2.0), 4), rt.f(1.0), 4)
        s1 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b1, width=4), rt.f(2.0), 4), rt.f(1.0), 4)
        sh = rt.unary("-", rt.component_wise("step", h, rt.construct(4, rt.f(0.0)), width=4))
        a0 = rt.binary("+", rt.swizzle(b0, "xzyw"), rt.binary("*", rt.swizzle(s0, "xzyw"), rt.swizzle(sh, "xxyy"), 4), 4)
        a1 = rt.binary("+", rt.swizzle(b1, "xzyw"), rt.binary("*", rt.swizzle(s1, "xzyw"), rt.swizzle(sh, "zzww"), 4), 4)
        p0 = rt.construct(3, rt.swizzle(a0, "xy"), rt.swizzle(h, "x"))
        p1 = rt.construct(3, rt.swizzle(a0, "zw"), rt.swizzle(h, "y"))
        p2 = rt.construct(3, rt.swizzle(a1, "xy"), rt.swizzle(h, "z"))
        p3 = rt.construct(3, rt.swizzle(a1, "zw"), rt.swizzle(h, "w"))
        norm = taylorInvSqrt__vec4(rt.construct(4, rt.dot(p0, p0), rt.dot(p1, p1), rt.dot(p2, p2), rt.dot(p3, p3)))
        p0 = rt.binary("*", p0, rt.swizzle(norm, "x"), 3)
        p1 = rt.binary("*", p1, rt.swizzle(norm, "y"), 3)
        p2 = rt.binary("*", p2, rt.swizzle(norm, "z"), 3)
        p3 = rt.binary("*", p3, rt.swizzle(norm, "w"), 3)
        m = rt.component_wise("max", rt.binary("-", rt.f(0.6), rt.construct(4, rt.dot(x0, x0), rt.dot(x1, x1), rt.dot(x2, x2), rt.dot(x3, x3)), 4), rt.f(0.0), width=4)
        m = rt.binary("*", m, m, 4)
        return rt.binary("*", rt.f(42.0), rt.dot(rt.binary("*", m, m, 4), rt.construct(4, rt.dot(p0, x0), rt.dot(p1, x1), rt.dot(p2, x2), rt.dot(p3, x3))), 1)
    def fbmSimplex3D__vec3(p):
        p = rt.copy(p)
        sum = rt.f(0.0)
        amp = rt.f(1.0)
        freq = rt.f(1.0)
        maxAmp = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, _u_OCTAVES)):
                break
            n = simplex3D__vec3(rt.binary("*", p, freq, 3))
            sum = rt.binary("+", sum, rt.binary("*", n, amp, 1), 1)
            maxAmp = rt.binary("+", maxAmp, amp, 1)
            freq = rt.binary("*", freq, rt.f(2.0), 1)
            amp = rt.binary("*", amp, rt.f(0.5), 1)
        return rt.binary("/", sum, maxAmp, 1)
    def curlNoise3D__vec3(p):
        p = rt.copy(p)
        eps = rt.f(1.0)
        a = rt.binary("*", rt.binary("/", rt.binary("+", rt.binary("*", rt.component_wise("sin", rt.binary("*", _u_time, rt.f(6.28318), 1), width=1), _u_speed, 1), rt.f(1.0), 1), _u_OCTAVES, 1), rt.f(0.2), 1)
        b = rt.binary("*", rt.binary("/", rt.binary("+", rt.binary("*", rt.component_wise("cos", rt.binary("*", _u_time, rt.f(6.28318), 1), width=1), _u_speed, 1), rt.f(1.0), 1), _u_OCTAVES, 1), rt.f(0.2), 1)
        offset1 = rt.construct(3, a, b, rt.f(0.0))
        offset2 = rt.construct(3, rt.binary("-", rt.f(31.416), a, 1), rt.binary("-", rt.f(47.853), b, 1), rt.f(12.793))
        offset3 = rt.construct(3, rt.binary("-", rt.f(93.719), b, 1), rt.binary("-", rt.f(61.248), a, 1), rt.f(73.561))
        Fx_py = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3), offset1, 3))
        Fx_ny = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3), offset1, 3))
        Fx_pz = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3), offset1, 3))
        Fx_nz = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3), offset1, 3))
        Fy_px = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3), offset2, 3))
        Fy_nx = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3), offset2, 3))
        Fy_pz = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3), offset2, 3))
        Fy_nz = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3), offset2, 3))
        Fz_px = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3), offset3, 3))
        Fz_nx = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3), offset3, 3))
        Fz_py = fbmSimplex3D__vec3(rt.binary("-", rt.binary("+", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3), offset3, 3))
        Fz_ny = fbmSimplex3D__vec3(rt.binary("+", rt.binary("-", p, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3), offset3, 3))
        dFx_dy = rt.binary("/", rt.binary("-", Fx_py, Fx_ny, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        dFx_dz = rt.binary("/", rt.binary("-", Fx_pz, Fx_nz, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        dFy_dx = rt.binary("/", rt.binary("-", Fy_px, Fy_nx, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        dFy_dz = rt.binary("/", rt.binary("-", Fy_pz, Fy_nz, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        dFz_dx = rt.binary("/", rt.binary("-", Fz_px, Fz_nx, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        dFz_dy = rt.binary("/", rt.binary("-", Fz_py, Fz_ny, 1), rt.binary("*", rt.f(2.0), eps, 1), 1)
        return rt.construct(3, rt.binary("-", dFz_dy, dFy_dz, 1), rt.binary("-", dFx_dz, dFz_dx, 1), rt.binary("-", dFy_dx, dFx_dy, 1))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        aspect = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        centered = rt.binary("*", rt.binary("-", uv, rt.f(0.5), 2), rt.construct(2, aspect, rt.f(1.0)), 2)
        p = rt.construct(3, rt.binary("*", centered, rt.binary("-", rt.f(21.0), _u_scale, 1), 2), rt.f(0.5))
        curl = curlNoise3D__vec3(p)
        curl = rt.binary("+", rt.binary("*", rt.component_wise("tanh", rt.binary("*", curl, _u_intensity, 3), width=3), rt.f(0.5), 3), rt.f(0.5), 3)
        color = rt.construct(3, 0.0)
        if rt.binary("==", _u_OUTPUT_MODE, rt.i(0)):
            color = rt.construct(3, rt.swizzle(curl, "x"))
        else:
            if rt.binary("==", _u_OUTPUT_MODE, rt.i(1)):
                color = rt.construct(3, rt.swizzle(curl, "y"))
            else:
                if rt.binary("==", _u_OUTPUT_MODE, rt.i(2)):
                    color = rt.construct(3, rt.swizzle(curl, "z"))
                else:
                    if rt.binary("==", _u_OUTPUT_MODE, rt.i(3)):
                        color = curl
                    else:
                        curlCentered = rt.binary("-", rt.binary("*", curl, rt.f(2.0), 3), rt.f(1.0), 3)
                        mag = rt.length(curlCentered)
                        color = rt.construct(3, mag)
        if _u_RIDGES:
            color = rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.binary("*", color, rt.f(2.0), 3), rt.f(1.0), 3), width=3), 3)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
