def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_NOISE_TYPE = U.get("NOISE_TYPE", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_ridges = U.get("ridges", False)
    _u_offsetX = U.get("offsetX", rt.f(0.0))
    _u_offsetY = U.get("offsetY", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_colorMode = U.get("colorMode", 0)
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.myt = rt.construct(4, rt.f(0.12121212), rt.f(0.13131313), rt.unary("-", rt.f(0.13131313)), rt.f(0.12121212))
    g.mys = rt.construct(2, rt.f(10000.0), rt.f(1000000.0))
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def random__vec2(st):
        st = rt.copy(st, "float")
        return rt.swizzle(prng__vec3(rt.construct(3, st, rt.f(0.0))), "x")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def smootherstep__float(x):
        return rt.binary("*", rt.binary("*", rt.binary("*", x, x, 1, "float"), x, 1, "float"), rt.binary("+", rt.binary("*", x, rt.binary("-", rt.binary("*", x, rt.f(6.0), 1, "float"), rt.f(15.0), 1, "float"), 1, "float"), rt.f(10.0), 1, "float"), 1, "float")
    def rhash__vec2(uv):
        uv = rt.copy(uv, "float")
        uv[:] = rt.binary("*", uv, g.myt, 2, "float")
        uv[:] = rt.binary("*", uv, g.mys, 2, "float")
        return rt.component_wise("fract", rt.binary("*", rt.component_wise("fract", rt.binary("/", uv, g.mys, 2, "float"), width=2), uv, 2, "float"), width=2)
    def voronoi3d__vec3(x):
        x = rt.copy(x, "float")
        p = rt.component_wise("floor", x, width=3)
        f = rt.component_wise("fract", x, width=3)
        id = rt.f(0.0)
        res = rt.construct(2, rt.f(100.0))
        k = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                k = rt.binary("+", k, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", k, rt.i(1))):
                break
            j = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    j = rt.binary("+", j, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", j, rt.i(1))):
                    break
                i = rt.unary("-", rt.i(1))
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        i = rt.binary("+", i, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<=", i, rt.i(1))):
                        break
                    b = rt.construct(3, rt.construct(1, i), rt.construct(1, j), rt.construct(1, k))
                    r = rt.binary("+", rt.binary("-", rt.construct(3, b), f, 3, "float"), prng__vec3(rt.binary("+", p, b, 3, "float")), 3, "float")
                    d = rt.dot(r, r)
                    cond = rt.component_wise("max", rt.component_wise("sign", rt.binary("-", rt.swizzle(res, "x"), d, 1, "float"), width=1), rt.f(0.0), width=1)
                    nCond = rt.binary("-", rt.f(1.0), cond, 1, "float")
                    cond2 = rt.binary("*", nCond, rt.component_wise("max", rt.component_wise("sign", rt.binary("-", rt.swizzle(res, "y"), d, 1, "float"), width=1), rt.f(0.0), width=1), 1, "float")
                    nCond2 = rt.binary("-", rt.f(1.0), cond2, 1, "float")
                    id = rt.binary("+", rt.binary("*", rt.dot(rt.binary("+", p, b, 3, "float"), rt.construct(3, rt.f(1.0), rt.f(57.0), rt.f(113.0))), cond, 1, "float"), rt.binary("*", id, nCond, 1, "float"), 1, "float")
                    res[:] = rt.binary("+", rt.binary("*", rt.construct(2, d, rt.swizzle(res, "x")), cond, 2, "float"), rt.binary("*", res, nCond, 2, "float"), 2, "float")
                    res = rt.assign_swizzle(res, "y", rt.binary("+", rt.binary("*", cond2, d, 1, "float"), rt.binary("*", nCond2, rt.swizzle(res, "y"), 1, "float"), 1, "float"))
        return rt.construct(3, rt.component_wise("sqrt", res, width=2), rt.component_wise("abs", id, width=1))
    def mod289__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 3, "float"), width=3), rt.f(289.0), 3, "float"), 3, "float")
    def mod7__vec3(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(7.0), 1, "float"), 3, "float"), width=3), rt.f(7.0), 3, "float"), 3, "float")
    def permute__vec3(x):
        x = rt.copy(x, "float")
        return mod289__vec3(rt.binary("*", rt.binary("+", rt.binary("*", rt.f(34.0), x, 3, "float"), rt.f(10.0), 3, "float"), x, 3, "float"))
    def cellular__vec3(P):
        P = rt.copy(P, "float")
        Pi = mod289__vec3(rt.component_wise("floor", P, width=3))
        Pf = rt.binary("-", rt.component_wise("fract", P, width=3), rt.f(0.5), 3, "float")
        Pfx = rt.binary("+", rt.swizzle(Pf, "x"), rt.construct(3, rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(1.0))), 3, "float")
        Pfy = rt.binary("+", rt.swizzle(Pf, "y"), rt.construct(3, rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(1.0))), 3, "float")
        Pfz = rt.binary("+", rt.swizzle(Pf, "z"), rt.construct(3, rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(1.0))), 3, "float")
        p = permute__vec3(rt.binary("+", rt.swizzle(Pi, "x"), rt.construct(3, rt.unary("-", rt.f(1.0)), rt.f(0.0), rt.f(1.0)), 3, "float"))
        p1 = permute__vec3(rt.binary("-", rt.binary("+", p, rt.swizzle(Pi, "y"), 3, "float"), rt.f(1.0), 3, "float"))
        p2 = permute__vec3(rt.binary("+", p, rt.swizzle(Pi, "y"), 3, "float"))
        p3 = permute__vec3(rt.binary("+", rt.binary("+", p, rt.swizzle(Pi, "y"), 3, "float"), rt.f(1.0), 3, "float"))
        p11 = permute__vec3(rt.binary("-", rt.binary("+", p1, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        p12 = permute__vec3(rt.binary("+", p1, rt.swizzle(Pi, "z"), 3, "float"))
        p13 = permute__vec3(rt.binary("+", rt.binary("+", p1, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        p21 = permute__vec3(rt.binary("-", rt.binary("+", p2, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        p22 = permute__vec3(rt.binary("+", p2, rt.swizzle(Pi, "z"), 3, "float"))
        p23 = permute__vec3(rt.binary("+", rt.binary("+", p2, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        p31 = permute__vec3(rt.binary("-", rt.binary("+", p3, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        p32 = permute__vec3(rt.binary("+", p3, rt.swizzle(Pi, "z"), 3, "float"))
        p33 = permute__vec3(rt.binary("+", rt.binary("+", p3, rt.swizzle(Pi, "z"), 3, "float"), rt.f(1.0), 3, "float"))
        ox11 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p11, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy11 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p11, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz11 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p11, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox12 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p12, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy12 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p12, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz12 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p12, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox13 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p13, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy13 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p13, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz13 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p13, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox21 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p21, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy21 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p21, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz21 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p21, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox22 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p22, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy22 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p22, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz22 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p22, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox23 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p23, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy23 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p23, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz23 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p23, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox31 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p31, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy31 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p31, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz31 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p31, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox32 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p32, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy32 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p32, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz32 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p32, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        ox33 = rt.binary("-", rt.component_wise("fract", rt.binary("*", p33, rt.f(0.142857142857), 3, "float"), width=3), rt.f(0.428571428571), 3, "float")
        oy33 = rt.binary("-", rt.binary("*", mod7__vec3(rt.component_wise("floor", rt.binary("*", p33, rt.f(0.142857142857), 3, "float"), width=3)), rt.f(0.142857142857), 3, "float"), rt.f(0.428571428571), 3, "float")
        oz33 = rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("*", p33, rt.f(0.020408163265306), 3, "float"), width=3), rt.f(0.166666666667), 3, "float"), rt.f(0.416666666667), 3, "float")
        dx11 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox11, 3, "float"), 3, "float")
        dy11 = rt.binary("+", rt.swizzle(Pfy, "x"), rt.binary("*", rt.f(1.0), oy11, 3, "float"), 3, "float")
        dz11 = rt.binary("+", rt.swizzle(Pfz, "x"), rt.binary("*", rt.f(1.0), oz11, 3, "float"), 3, "float")
        dx12 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox12, 3, "float"), 3, "float")
        dy12 = rt.binary("+", rt.swizzle(Pfy, "x"), rt.binary("*", rt.f(1.0), oy12, 3, "float"), 3, "float")
        dz12 = rt.binary("+", rt.swizzle(Pfz, "y"), rt.binary("*", rt.f(1.0), oz12, 3, "float"), 3, "float")
        dx13 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox13, 3, "float"), 3, "float")
        dy13 = rt.binary("+", rt.swizzle(Pfy, "x"), rt.binary("*", rt.f(1.0), oy13, 3, "float"), 3, "float")
        dz13 = rt.binary("+", rt.swizzle(Pfz, "z"), rt.binary("*", rt.f(1.0), oz13, 3, "float"), 3, "float")
        dx21 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox21, 3, "float"), 3, "float")
        dy21 = rt.binary("+", rt.swizzle(Pfy, "y"), rt.binary("*", rt.f(1.0), oy21, 3, "float"), 3, "float")
        dz21 = rt.binary("+", rt.swizzle(Pfz, "x"), rt.binary("*", rt.f(1.0), oz21, 3, "float"), 3, "float")
        dx22 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox22, 3, "float"), 3, "float")
        dy22 = rt.binary("+", rt.swizzle(Pfy, "y"), rt.binary("*", rt.f(1.0), oy22, 3, "float"), 3, "float")
        dz22 = rt.binary("+", rt.swizzle(Pfz, "y"), rt.binary("*", rt.f(1.0), oz22, 3, "float"), 3, "float")
        dx23 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox23, 3, "float"), 3, "float")
        dy23 = rt.binary("+", rt.swizzle(Pfy, "y"), rt.binary("*", rt.f(1.0), oy23, 3, "float"), 3, "float")
        dz23 = rt.binary("+", rt.swizzle(Pfz, "z"), rt.binary("*", rt.f(1.0), oz23, 3, "float"), 3, "float")
        dx31 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox31, 3, "float"), 3, "float")
        dy31 = rt.binary("+", rt.swizzle(Pfy, "z"), rt.binary("*", rt.f(1.0), oy31, 3, "float"), 3, "float")
        dz31 = rt.binary("+", rt.swizzle(Pfz, "x"), rt.binary("*", rt.f(1.0), oz31, 3, "float"), 3, "float")
        dx32 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox32, 3, "float"), 3, "float")
        dy32 = rt.binary("+", rt.swizzle(Pfy, "z"), rt.binary("*", rt.f(1.0), oy32, 3, "float"), 3, "float")
        dz32 = rt.binary("+", rt.swizzle(Pfz, "y"), rt.binary("*", rt.f(1.0), oz32, 3, "float"), 3, "float")
        dx33 = rt.binary("+", Pfx, rt.binary("*", rt.f(1.0), ox33, 3, "float"), 3, "float")
        dy33 = rt.binary("+", rt.swizzle(Pfy, "z"), rt.binary("*", rt.f(1.0), oy33, 3, "float"), 3, "float")
        dz33 = rt.binary("+", rt.swizzle(Pfz, "z"), rt.binary("*", rt.f(1.0), oz33, 3, "float"), 3, "float")
        d11 = rt.binary("+", rt.binary("+", rt.binary("*", dx11, dx11, 3, "float"), rt.binary("*", dy11, dy11, 3, "float"), 3, "float"), rt.binary("*", dz11, dz11, 3, "float"), 3, "float")
        d12 = rt.binary("+", rt.binary("+", rt.binary("*", dx12, dx12, 3, "float"), rt.binary("*", dy12, dy12, 3, "float"), 3, "float"), rt.binary("*", dz12, dz12, 3, "float"), 3, "float")
        d13 = rt.binary("+", rt.binary("+", rt.binary("*", dx13, dx13, 3, "float"), rt.binary("*", dy13, dy13, 3, "float"), 3, "float"), rt.binary("*", dz13, dz13, 3, "float"), 3, "float")
        d21 = rt.binary("+", rt.binary("+", rt.binary("*", dx21, dx21, 3, "float"), rt.binary("*", dy21, dy21, 3, "float"), 3, "float"), rt.binary("*", dz21, dz21, 3, "float"), 3, "float")
        d22 = rt.binary("+", rt.binary("+", rt.binary("*", dx22, dx22, 3, "float"), rt.binary("*", dy22, dy22, 3, "float"), 3, "float"), rt.binary("*", dz22, dz22, 3, "float"), 3, "float")
        d23 = rt.binary("+", rt.binary("+", rt.binary("*", dx23, dx23, 3, "float"), rt.binary("*", dy23, dy23, 3, "float"), 3, "float"), rt.binary("*", dz23, dz23, 3, "float"), 3, "float")
        d31 = rt.binary("+", rt.binary("+", rt.binary("*", dx31, dx31, 3, "float"), rt.binary("*", dy31, dy31, 3, "float"), 3, "float"), rt.binary("*", dz31, dz31, 3, "float"), 3, "float")
        d32 = rt.binary("+", rt.binary("+", rt.binary("*", dx32, dx32, 3, "float"), rt.binary("*", dy32, dy32, 3, "float"), 3, "float"), rt.binary("*", dz32, dz32, 3, "float"), 3, "float")
        d33 = rt.binary("+", rt.binary("+", rt.binary("*", dx33, dx33, 3, "float"), rt.binary("*", dy33, dy33, 3, "float"), 3, "float"), rt.binary("*", dz33, dz33, 3, "float"), 3, "float")
        d1a = rt.component_wise("min", d11, d12, width=3)
        d12[:] = rt.component_wise("max", d11, d12, width=3)
        d11[:] = rt.component_wise("min", d1a, d13, width=3)
        d13[:] = rt.component_wise("max", d1a, d13, width=3)
        d12[:] = rt.component_wise("min", d12, d13, width=3)
        d2a = rt.component_wise("min", d21, d22, width=3)
        d22[:] = rt.component_wise("max", d21, d22, width=3)
        d21[:] = rt.component_wise("min", d2a, d23, width=3)
        d23[:] = rt.component_wise("max", d2a, d23, width=3)
        d22[:] = rt.component_wise("min", d22, d23, width=3)
        d3a = rt.component_wise("min", d31, d32, width=3)
        d32[:] = rt.component_wise("max", d31, d32, width=3)
        d31[:] = rt.component_wise("min", d3a, d33, width=3)
        d33[:] = rt.component_wise("max", d3a, d33, width=3)
        d32[:] = rt.component_wise("min", d32, d33, width=3)
        da = rt.component_wise("min", d11, d21, width=3)
        d21[:] = rt.component_wise("max", d11, d21, width=3)
        d11[:] = rt.component_wise("min", da, d31, width=3)
        d31[:] = rt.component_wise("max", da, d31, width=3)
        d11 = rt.assign_swizzle(d11, "xy", (rt.swizzle(d11, "xy") if rt.binary("<", rt.swizzle(d11, "x"), rt.swizzle(d11, "y")) else rt.swizzle(d11, "yx")))
        d11 = rt.assign_swizzle(d11, "xz", (rt.swizzle(d11, "xz") if rt.binary("<", rt.swizzle(d11, "x"), rt.swizzle(d11, "z")) else rt.swizzle(d11, "zx")))
        d12[:] = rt.component_wise("min", d12, d21, width=3)
        d12[:] = rt.component_wise("min", d12, d22, width=3)
        d12[:] = rt.component_wise("min", d12, d31, width=3)
        d12[:] = rt.component_wise("min", d12, d32, width=3)
        d11 = rt.assign_swizzle(d11, "yz", rt.component_wise("min", rt.swizzle(d11, "yz"), rt.swizzle(d12, "xy"), width=2))
        d11 = rt.assign_swizzle(d11, "y", rt.component_wise("min", rt.swizzle(d11, "y"), rt.swizzle(d12, "z"), width=1))
        d11 = rt.assign_swizzle(d11, "y", rt.component_wise("min", rt.swizzle(d11, "y"), rt.swizzle(d11, "z"), width=1))
        return rt.component_wise("sqrt", rt.swizzle(d11, "xy"), width=2)
    def mod289__vec4(x):
        x = rt.copy(x, "float")
        return rt.binary("-", x, rt.binary("*", rt.component_wise("floor", rt.binary("*", x, rt.binary("/", rt.f(1.0), rt.f(289.0), 1, "float"), 4, "float"), width=4), rt.f(289.0), 4, "float"), 4, "float")
    def permute__vec4(x):
        x = rt.copy(x, "float")
        return mod289__vec4(rt.binary("*", rt.binary("+", rt.binary("*", x, rt.f(34.0), 4, "float"), rt.f(10.0), 4, "float"), x, 4, "float"))
    def taylorInvSqrt__vec4(r):
        r = rt.copy(r, "float")
        return rt.binary("-", rt.f(1.79284291400159), rt.binary("*", rt.f(0.85373472095314), r, 4, "float"), 4, "float")
    def snoise__vec3(v):
        v = rt.copy(v, "float")
        C = rt.construct(2, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"))
        D = rt.construct(4, rt.f(0.0), rt.f(0.5), rt.f(1.0), rt.f(2.0))
        i = rt.component_wise("floor", rt.binary("+", v, rt.dot(v, rt.swizzle(C, "yyy")), 3, "float"), width=3)
        x0 = rt.binary("+", rt.binary("-", v, i, 3, "float"), rt.dot(i, rt.swizzle(C, "xxx")), 3, "float")
        _g = rt.component_wise("step", rt.swizzle(x0, "yzx"), rt.swizzle(x0, "xyz"), width=3)
        l = rt.binary("-", rt.f(1.0), _g, 3, "float")
        i1 = rt.component_wise("min", rt.swizzle(_g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        i2 = rt.component_wise("max", rt.swizzle(_g, "xyz"), rt.swizzle(l, "zxy"), width=3)
        x1 = rt.binary("+", rt.binary("-", x0, i1, 3, "float"), rt.swizzle(C, "xxx"), 3, "float")
        x2 = rt.binary("+", rt.binary("-", x0, i2, 3, "float"), rt.swizzle(C, "yyy"), 3, "float")
        x3 = rt.binary("-", x0, rt.swizzle(D, "yyy"), 3, "float")
        i[:] = mod289__vec3(i)
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
        bHigh = rt.construct(4, rt.swizzle(x, "zw"), rt.swizzle(y, "zw"))
        s0 = rt.binary("+", rt.binary("*", rt.component_wise("floor", b0, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        sHigh = rt.binary("+", rt.binary("*", rt.component_wise("floor", bHigh, width=4), rt.f(2.0), 4, "float"), rt.f(1.0), 4, "float")
        sh = rt.unary("-", rt.component_wise("step", h, rt.construct(4, rt.f(0.0)), width=4))
        a0 = rt.binary("+", rt.swizzle(b0, "xzyw"), rt.binary("*", rt.swizzle(s0, "xzyw"), rt.swizzle(sh, "xxyy"), 4, "float"), 4, "float")
        aHigh = rt.binary("+", rt.swizzle(bHigh, "xzyw"), rt.binary("*", rt.swizzle(sHigh, "xzyw"), rt.swizzle(sh, "zzww"), 4, "float"), 4, "float")
        p0 = rt.construct(3, rt.swizzle(a0, "xy"), rt.swizzle(h, "x"))
        p1 = rt.construct(3, rt.swizzle(a0, "zw"), rt.swizzle(h, "y"))
        p2 = rt.construct(3, rt.swizzle(aHigh, "xy"), rt.swizzle(h, "z"))
        p3 = rt.construct(3, rt.swizzle(aHigh, "zw"), rt.swizzle(h, "w"))
        norm = taylorInvSqrt__vec4(rt.construct(4, rt.dot(p0, p0), rt.dot(p1, p1), rt.dot(p2, p2), rt.dot(p3, p3)))
        p0[:] = rt.binary("*", p0, rt.swizzle(norm, "x"), 3, "float")
        p1[:] = rt.binary("*", p1, rt.swizzle(norm, "y"), 3, "float")
        p2[:] = rt.binary("*", p2, rt.swizzle(norm, "z"), 3, "float")
        p3[:] = rt.binary("*", p3, rt.swizzle(norm, "w"), 3, "float")
        m = rt.component_wise("max", rt.binary("-", rt.f(0.5), rt.construct(4, rt.dot(x0, x0), rt.dot(x1, x1), rt.dot(x2, x2), rt.dot(x3, x3)), 4, "float"), rt.f(0.0), width=4)
        m[:] = rt.binary("*", m, m, 4, "float")
        return rt.binary("*", rt.f(105.0), rt.dot(rt.binary("*", m, m, 4, "float"), rt.construct(4, rt.dot(p0, x0), rt.dot(p1, x1), rt.dot(p2, x2), rt.dot(p3, x3))), 1, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st[:] = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        return st
    def smin__float_float_float(a, b, k):
        h = rt.binary("/", rt.component_wise("max", rt.binary("-", k, rt.component_wise("abs", rt.binary("-", a, b, 1, "float"), width=1), 1, "float"), rt.f(0.0), width=1), k, 1, "float")
        return rt.binary("-", rt.component_wise("min", a, b, width=1), rt.binary("*", rt.binary("*", rt.binary("*", h, h, 1, "float"), k, 1, "float"), rt.binary("/", rt.f(1.0), rt.f(4.0), 1, "float"), 1, "float"), 1, "float")
    def smax__float_float_float(a, b, k):
        return rt.binary("/", rt.component_wise("log", rt.binary("+", rt.component_wise("exp", rt.binary("*", k, a, 1, "float"), width=1), rt.component_wise("exp", rt.binary("*", k, b, 1, "float"), width=1), 1, "float"), width=1), k, 1, "float")
    def smoothabs__float_float(v, m):
        return rt.component_wise("sqrt", rt.binary("+", rt.binary("*", v, v, 1, "float"), m, 1, "float"), width=1)
    def sine3D__vec3(p):
        p = rt.copy(p, "float")
        r0 = rt.binary("*", prng__vec3(rt.construct(3, rt.construct(1, _u_seed))), rt.f(6.28318530718), 3, "float")
        a = rt.swizzle(r0, "x")
        b = rt.swizzle(r0, "y")
        c = rt.swizzle(r0, "z")
        r1 = rt.binary("+", prng__vec3(rt.construct(3, rt.construct(1, _u_seed))), rt.f(1.0), 3, "float")
        r2 = rt.binary("+", prng__vec3(rt.construct(3, rt.binary("+", rt.construct(1, _u_seed), rt.f(10.0), 1, "float"))), rt.f(1.0), 3, "float")
        r3 = rt.binary("+", prng__vec3(rt.construct(3, rt.binary("+", rt.construct(1, _u_seed), rt.f(20.0), 1, "float"))), rt.f(1.0), 3, "float")
        x = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r1, "x"), rt.swizzle(p, "z"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "y"), rt.swizzle(p, "x"), 1, "float"), a, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r1, "z"), rt.swizzle(p, "y"), 1, "float"), b, 1, "float"), width=1), 1, "float"), c, 1, "float"), width=1)
        y = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r2, "x"), rt.swizzle(p, "x"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "y"), rt.swizzle(p, "y"), 1, "float"), b, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r2, "z"), rt.swizzle(p, "z"), 1, "float"), c, 1, "float"), width=1), 1, "float"), a, 1, "float"), width=1)
        z = rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(r3, "x"), rt.swizzle(p, "y"), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r3, "y"), rt.swizzle(p, "z"), 1, "float"), c, 1, "float"), width=1), 1, "float"), rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.swizzle(r3, "z"), rt.swizzle(p, "x"), 1, "float"), a, 1, "float"), width=1), 1, "float"), b, 1, "float"), width=1)
        return rt.binary("+", rt.binary("*", rt.binary("+", rt.binary("+", x, y, 1, "float"), z, 1, "float"), rt.f(0.33), 1, "float"), rt.f(0.33), 1, "float")
    def spheres__vec3(p):
        p = rt.copy(p, "float")
        q = p
        p[:] = rt.binary("-", p, rt.component_wise("round", p, width=3), 3, "float")
        ip = rt.component_wise("floor", q, width=3)
        fp = rt.component_wise("fract", p, width=3)
        r1 = rt.binary("+", rt.binary("*", prng__vec3(rt.binary("+", ip, rt.construct(1, _u_seed), 3, "float")), rt.f(0.5), 3, "float"), rt.f(0.25), 3, "float")
        return rt.binary("-", rt.length(rt.binary("-", fp, rt.f(0.5), 3, "float")), rt.binary("*", map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.025), rt.f(0.55)), rt.swizzle(r1, "x"), 1, "float"), 1, "float")
    def cubes__vec3(p):
        p = rt.copy(p, "float")
        s = rt.f(4.0)
        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.swizzle(p, "x"), rt.binary("*", s, rt.f(0.5), 1, "float"), 1, "float"))
        p[:] = rt.binary("-", p, rt.binary("*", s, rt.component_wise("round", rt.binary("/", p, s, 3, "float"), width=3), 3, "float"), 3, "float")
        b = rt.construct(3, map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.1), rt.f(0.95)))
        q = rt.binary("-", rt.component_wise("abs", p, width=3), b, 3, "float")
        return rt.binary("+", rt.length(rt.component_wise("max", q, rt.f(0.0), width=3)), rt.component_wise("min", rt.component_wise("max", rt.swizzle(q, "x"), rt.component_wise("max", rt.swizzle(q, "y"), rt.swizzle(q, "z"), width=1), width=1), rt.f(0.0), width=1), 1, "float")
    def getDist__vec3(p):
        p = rt.copy(p, "float")
        d = rt.f(0.0)
        scaleN = rt.f(0.0)
        if rt.binary("==", _u_NOISE_TYPE, rt.i(12)):
            scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.25), rt.f(0.025))
            d = rt.binary("+", rt.binary("*", snoise__vec3(rt.binary("+", rt.binary("*", p, scaleN, 3, "float"), rt.construct(1, _u_seed), 3, "float")), rt.f(0.5), 1, "float"), rt.f(0.5), 1, "float")
            d = smootherstep__float(d)
            if _u_ridges:
                d = rt.binary("-", rt.f(1.0), smoothabs__float_float(rt.binary("-", rt.binary("*", d, rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float"), rt.f(0.05)), 1, "float")
        else:
            if rt.binary("==", _u_NOISE_TYPE, rt.i(20)):
                scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.1), rt.f(0.35))
                d = rt.swizzle(cellular__vec3(rt.binary("+", rt.binary("*", p, rt.f(0.1), 3, "float"), rt.construct(1, _u_seed), 3, "float")), "x")
                d = rt.component_wise("smoothstep", scaleN, rt.f(0.5), d, width=1)
            else:
                if rt.binary("==", _u_NOISE_TYPE, rt.i(21)):
                    d = rt.swizzle(voronoi3d__vec3(rt.binary("+", rt.binary("*", p, rt.f(0.1), 3, "float"), rt.construct(1, _u_seed), 3, "float")), "x")
                    scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.1), rt.f(0.35))
                    d = rt.component_wise("smoothstep", scaleN, rt.f(0.5), d, width=1)
                else:
                    if rt.binary("==", _u_NOISE_TYPE, rt.i(30)):
                        scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(1.0), rt.f(0.1))
                        d = sine3D__vec3(rt.binary("*", p, scaleN, 3, "float"))
                    else:
                        if rt.binary("==", _u_NOISE_TYPE, rt.i(40)):
                            d = spheres__vec3(p)
                        else:
                            if rt.binary("==", _u_NOISE_TYPE, rt.i(50)):
                                d = cubes__vec3(p)
                            else:
                                if rt.binary("==", _u_NOISE_TYPE, rt.i(60)):
                                    scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.25), rt.f(0.025))
                                    d = rt.binary("+", rt.binary("+", rt.unary("-", rt.component_wise("abs", rt.swizzle(p, "y"), width=1)), rt.f(4.0), 1, "float"), rt.binary("*", snoise__vec3(rt.binary("+", rt.binary("*", p, scaleN, 3, "float"), rt.construct(1, _u_seed), 3, "float")), rt.f(0.75), 1, "float"), 1, "float")
                                else:
                                    if rt.binary("==", _u_NOISE_TYPE, rt.i(61)):
                                        scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.25), rt.f(0.025))
                                        d = rt.binary("+", rt.binary("+", rt.swizzle(p, "y"), rt.f(4.0), 1, "float"), rt.binary("*", snoise__vec3(rt.binary("+", rt.binary("*", p, scaleN, 3, "float"), rt.construct(1, _u_seed), 3, "float")), rt.f(0.75), 1, "float"), 1, "float")
                                    else:
                                        if rt.binary("==", _u_NOISE_TYPE, rt.i(62)):
                                            scaleN = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(0.25), rt.f(0.025))
                                            d = rt.binary("+", rt.binary("+", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.binary("*", snoise__vec3(rt.binary("+", rt.binary("*", p, scaleN, 3, "float"), rt.construct(1, _u_seed), 3, "float")), rt.f(0.75), 1, "float"), 1, "float")
                                        else:
                                            d = rt.f(0.0)
        return d
    def getNormal__vec3(p):
        p = rt.copy(p, "float")
        epsilon = rt.f(0.01)
        d = getDist__vec3(p)
        dx = rt.binary("-", getDist__vec3(rt.binary("+", p, rt.construct(3, epsilon, rt.f(0.0), rt.f(0.0)), 3, "float")), d, 1, "float")
        dy = rt.binary("-", getDist__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), epsilon, rt.f(0.0)), 3, "float")), d, 1, "float")
        dz = rt.binary("-", getDist__vec3(rt.binary("+", p, rt.construct(3, rt.f(0.0), rt.f(0.0), epsilon), 3, "float")), d, 1, "float")
        return rt.normalize(rt.construct(3, dx, dy, dz))
    def rayMarch__vec3_vec3(rayOrigin, rayDirection):
        rayOrigin = rt.copy(rayOrigin, "float")
        rayDirection = rt.copy(rayDirection, "float")
        maxSteps = rt.i(100)
        maxDist = rt.f(100.0)
        minDist = rt.f(0.01)
        d = rt.f(0.0)
        i = rt.i(0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for3_first = False
            if not (rt.binary("<", i, maxSteps)):
                break
            p = rt.binary("+", rayOrigin, rt.binary("*", rayDirection, d, 3, "float"), 3, "float")
            dist = getDist__vec3(p)
            d = rt.binary("+", d, dist, 1, "float")
            if (bool(rt.binary(">", d, maxDist)) or bool(rt.binary("<", dist, minDist))):
                break
        return d
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if (bool(rt.binary("<=", rt.f(0.0), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")))):
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
                            else:
                                (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3, "float")
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = rt.swizzle(rgb, "r")
        _g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        max = rt.component_wise("max", r, rt.component_wise("max", _g, b, width=1), width=1)
        min = rt.component_wise("min", r, rt.component_wise("min", _g, b, width=1), width=1)
        delta = rt.binary("-", max, min, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", _g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", max, _g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, _g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", max, rt.f(0.0)) else rt.binary("/", delta, max, 1, "float"))
        v = max
        return rt.construct(3, h, s, v)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        st = rt.binary("/", rt.binary("-", globalCoord, rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "xy"), 2, "float"), 2, "float"), rt.swizzle(_u_fullResolution, "y"), 2, "float")
        rayOrigin = rt.construct(3, rt.binary("*", _u_offsetX, rt.f(0.1), 1, "float"), rt.binary("*", _u_offsetY, rt.f(0.1), 1, "float"), rt.binary("+", rt.unary("-", rt.f(8.0)), rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), _u_speed, 1, "float"), 1, "float"))
        rayDirection = rt.normalize(rt.construct(3, st, rt.f(1.0)))
        d = rayMarch__vec3_vec3(rayOrigin, rayDirection)
        p = rt.binary("+", rayOrigin, rt.binary("*", rayDirection, d, 3, "float"), 3, "float")
        lightPosition = rt.binary("+", rayOrigin, rt.construct(3, rt.unary("-", rt.f(5.0)), rt.f(5.0), rt.unary("-", rt.f(10.0))), 3, "float")
        lightVector = rt.normalize(rt.binary("-", lightPosition, p, 3, "float"))
        normal = getNormal__vec3(p)
        diffuse = rt.component_wise("clamp", rt.dot(normal, lightVector), rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.construct(3, diffuse))
        else:
            if rt.binary("==", _u_colorMode, rt.i(6)):
                color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(rt.construct(3, rt.binary("+", rt.binary("*", diffuse, rt.binary("*", _u_hueRange, rt.f(0.01), 1, "float"), 1, "float"), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), rt.f(0.75), rt.f(0.75))))
            else:
                if rt.binary("==", _u_colorMode, rt.i(7)):
                    color = rt.assign_swizzle(color, "rgb", normal)
                else:
                    if rt.binary("==", _u_colorMode, rt.i(8)):
                        color = rt.assign_swizzle(color, "rgb", rt.construct(3, rt.component_wise("clamp", d, rt.f(0.0), rt.f(1.0), width=1)))
        fogDist = rt.component_wise("clamp", rt.binary("/", d, rt.f(50.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.construct(3, rt.f(0.0)), fogDist, width=3))
        st[:] = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
