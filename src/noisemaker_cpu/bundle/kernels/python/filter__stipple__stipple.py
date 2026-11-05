def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_MODE = U.get("MODE", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_cellSize = U.get("cellSize", rt.f(0.0))
    _u_grainSize = U.get("grainSize", rt.f(0.0))
    _u_density = U.get("density", rt.f(0.0))
    _u_paperColor = U.get("paperColor", rt.construct(3, 0.0))
    _u_seed = U.get("seed", 0)
    g.fragColor = rt.construct(4, 0.0)
    def pcg3d__uvec3(v_in):
        v_in = rt.copy(v_in, "uint")
        v = rt.binary("+", rt.binary("*", v_in, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        ((_vector_write_0_0 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "x")), (_vector_write_0_1 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "y")), (_vector_write_0_2 := rt.swizzle(rt.binary("^", v, rt.binary(">>", v, rt.construct(3, rt.i(16), base="uint"), 3, "uint"), 3, "uint"), "z")), v.__setitem__(0, _vector_write_0_0), v.__setitem__(1, _vector_write_0_1), v.__setitem__(2, _vector_write_0_2), v)[-1]
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def hash16__uvec2_uint(cell, s):
        cell = rt.copy(cell, "uint")
        return rt.binary(">>", rt.swizzle(rt.pcg3d(rt.construct(3, cell, s, base="uint")), "x"), rt.i(16), 1, "uint")
    def unorm16__float(x):
        return rt.component_wise("min", rt.construct(1, rt.binary("*", rt.component_wise("clamp", x, rt.f(0.0), rt.f(1.0), width=1), rt.f(65536.0), 1, "float"), base="uint"), rt.i(65535), width=1)
    def lum16__vec3(c):
        c = rt.copy(c, "float")
        return rt.binary(">>", rt.binary("+", rt.binary("+", rt.binary("*", unorm16__float(rt.swizzle(c, "r")), rt.i(13933), 1, "uint"), rt.binary("*", unorm16__float(rt.swizzle(c, "g")), rt.i(46872), 1, "uint"), 1, "uint"), rt.binary("*", unorm16__float(rt.swizzle(c, "b")), rt.i(4731), 1, "uint"), 1, "uint"), rt.i(16), 1, "uint")
    def smooth12__uint(t):
        return rt.binary(">>", rt.binary("*", rt.binary(">>", rt.binary("*", t, t, 1, "uint"), rt.i(12), 1, "uint"), rt.binary("-", rt.i(12288), rt.binary("*", rt.i(2), t, 1, "uint"), 1, "uint"), 1, "uint"), rt.i(12), 1, "uint")
    def vnoise__uvec2_uvec2_uint(n, d, s):
        n = rt.copy(n, "uint")
        d = rt.copy(d, "uint")
        i = rt.binary("/", n, d, 2, "uint")
        f = rt.binary("/", rt.binary("<<", rt.binary("-", n, rt.binary("*", i, d, 2, "uint"), 2, "uint"), rt.construct(2, rt.i(12), base="uint"), 2, "uint"), d, 2, "uint")
        ux = smooth12__uint(rt.swizzle(f, "x"))
        uy = smooth12__uint(rt.swizzle(f, "y"))
        ab = rt.binary(">>", rt.binary("+", rt.binary("*", hash16__uvec2_uint(i, s), rt.binary("-", rt.i(4096), ux, 1, "uint"), 1, "uint"), rt.binary("*", hash16__uvec2_uint(rt.binary("+", i, rt.construct(2, rt.i(1), rt.i(0), base="uint"), 2, "uint"), s), ux, 1, "uint"), 1, "uint"), rt.i(12), 1, "uint")
        cd = rt.binary(">>", rt.binary("+", rt.binary("*", hash16__uvec2_uint(rt.binary("+", i, rt.construct(2, rt.i(0), rt.i(1), base="uint"), 2, "uint"), s), rt.binary("-", rt.i(4096), ux, 1, "uint"), 1, "uint"), rt.binary("*", hash16__uvec2_uint(rt.binary("+", i, rt.construct(2, rt.i(1), rt.i(1), base="uint"), 2, "uint"), s), ux, 1, "uint"), 1, "uint"), rt.i(12), 1, "uint")
        return rt.binary(">>", rt.binary("+", rt.binary("*", ab, rt.binary("-", rt.i(4096), uy, 1, "uint"), 1, "uint"), rt.binary("*", cd, uy, 1, "uint"), 1, "uint"), rt.i(12), 1, "uint")
    def fbm__uvec2_uint_uint(n, grain, s):
        n = rt.copy(n, "uint")
        M = rt.array([rt.i(65536), rt.i(32284), rt.i(15903), rt.i(7834), rt.i(3859)])
        v = rt.i(0)
        k = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                k = rt.binary("+", k, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", k, rt.i(5))):
                break
            dk = rt.component_wise("max", rt.binary(">>", rt.binary("+", rt.binary("*", grain, M[int(k)], 1, "uint"), rt.i(8192), 1, "uint"), rt.i(14), 1, "uint"), rt.i(1), width=1)
            v = rt.binary("+", v, rt.binary(">>", vnoise__uvec2_uvec2_uint(n, rt.construct(2, dk, base="uint"), s), rt.construct(1, rt.binary("+", k, rt.i(1), 1, "int"), base="uint"), 1, "uint"), 1, "uint")
        return v
    def isqrt__uint(x):
        r = rt.construct(1, rt.component_wise("sqrt", rt.construct(1, x), width=1), base="uint")
        if rt.binary(">", rt.binary("*", r, r, 1, "uint"), x):
            r = rt.binary("-", r, rt.i(1), 1, "uint")
        if rt.binary(">", rt.binary("*", r, r, 1, "uint"), x):
            r = rt.binary("-", r, rt.i(1), 1, "uint")
        if rt.binary("<=", rt.binary("*", rt.binary("+", r, rt.i(1), 1, "uint"), rt.binary("+", r, rt.i(1), 1, "uint"), 1, "uint"), x):
            r = rt.binary("+", r, rt.i(1), 1, "uint")
        if rt.binary("<=", rt.binary("*", rt.binary("+", r, rt.i(1), 1, "uint"), rt.binary("+", r, rt.i(1), 1, "uint"), 1, "uint"), x):
            r = rt.binary("+", r, rt.i(1), 1, "uint")
        return r
    def inkStep__uint_uint_int(edge, value, d256):
        return (rt.f(1.0) if rt.binary(">=", rt.binary("+", rt.binary("*", rt.i(25), rt.construct(1, value, base="int"), 1, "int"), rt.i(819200), 1, "int"), rt.binary("+", rt.binary("*", rt.i(25), rt.construct(1, edge, base="int"), 1, "int"), rt.binary("*", rt.i(64), d256, 1, "int"), 1, "int")) else rt.f(0.0))
    def main__void():
        texel = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        texSize = rt.texture_size(_u_inputTex)
        px = rt.construct(2, rt.binary("+", texel, rt.construct(2, _u_tileOffset, base="int"), 2, "int"), base="uint")
        center = rt.binary("*", rt.binary("+", rt.binary("*", rt.i(2), px, 2, "uint"), rt.i(1), 2, "uint"), rt.i(128), 2, "uint")
        src = rt.texel_fetch(_u_inputTex, texel, rt.i(0))
        s = rt.construct(1, _u_seed, base="uint")
        d256 = rt.construct(1, rt.component_wise("floor", rt.binary("*", _u_density, rt.f(256.0), 1, "float"), width=1), base="int")
        g256 = rt.component_wise("clamp", rt.construct(1, rt.binary("*", rt.component_wise("max", _u_grainSize, rt.f(0.0), width=1), rt.f(256.0), 1, "float"), base="uint"), rt.i(1), rt.i(32768), width=1)
        result = rt.construct(3, 0.0)
        c256 = 0
        _g = rt.construct(2, 0.0, base="uint")
        f = rt.construct(2, 0.0, base="int")
        best = 0
        bestPt = rt.construct(2, 0.0, base="int")
        seed256 = rt.construct(2, 0.0, base="int")
        seedTexel = rt.construct(2, 0.0, base="int")
        seedColor = rt.construct(3, 0.0)
        radius = 0
        d = 0
        aa = 0
        t = 0
        inside = 0
        paper = rt.construct(3, 0.0, base="uint")
        ink = rt.construct(3, 0.0, base="uint")
        pos = rt.construct(2, 0.0, base="uint")
        grain = 0
        lattice = rt.construct(2, 0.0, base="uint")
        n = 0
        l = 0
        amp = 0
        clumpNoise = 0
        if rt.binary("==", _u_MODE, rt.i(0)):
            c256 = rt.component_wise("clamp", rt.construct(1, rt.binary("*", rt.component_wise("max", _u_cellSize, rt.f(0.0), width=1), rt.f(256.0), 1, "float"), base="uint"), rt.i(1), rt.i(65535), width=1)
            _g = rt.binary("/", center, c256, 2, "uint")
            f = rt.construct(2, rt.binary("/", rt.binary("<<", rt.binary("-", center, rt.binary("*", _g, c256, 2, "uint"), 2, "uint"), rt.construct(2, rt.i(12), base="uint"), 2, "uint"), c256, 2, "uint"), base="int")
            best = rt.i(2147483647)
            bestPt = rt.construct(2, rt.i(0), base="int")
            y = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    y = rt.binary("+", y, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", y, rt.i(1))):
                    break
                x = rt.unary("-", rt.i(1))
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        x = rt.binary("+", x, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<=", x, rt.i(1))):
                        break
                    cell = rt.construct(2, x, y, base="int")
                    h = rt.binary(">>", rt.swizzle(rt.pcg3d(rt.construct(3, rt.construct(2, rt.binary("+", rt.construct(2, _g, base="int"), cell, 2, "int"), base="uint"), s, base="uint")), "xy"), rt.construct(2, rt.i(16), base="uint"), 2, "uint")
                    pt = rt.binary("+", rt.binary("+", rt.binary("*", cell, rt.i(4096), 2, "int"), rt.i(205), 2, "int"), rt.construct(2, rt.binary(">>", rt.binary("/", rt.binary("*", h, rt.i(9), 2, "uint"), rt.i(10), 2, "uint"), rt.construct(2, rt.i(4), base="uint"), 2, "uint"), base="int"), 2, "int")
                    dv = rt.binary("-", pt, f, 2, "int")
                    dd = rt.binary("+", rt.binary("*", rt.swizzle(dv, "x"), rt.swizzle(dv, "x"), 1, "int"), rt.binary("*", rt.swizzle(dv, "y"), rt.swizzle(dv, "y"), 1, "int"), 1, "int")
                    if rt.binary("<", dd, best):
                        best = dd
                        bestPt[:] = pt
            seed256 = rt.binary("+", rt.binary("*", rt.binary("-", rt.construct(2, _g, base="int"), rt.i(1), 2, "int"), rt.construct(1, c256, base="int"), 2, "int"), rt.construct(2, rt.binary(">>", rt.binary("*", rt.construct(2, rt.binary("+", bestPt, rt.i(4096), 2, "int"), base="uint"), c256, 2, "uint"), rt.construct(2, rt.i(12), base="uint"), 2, "uint"), base="int"), 2, "int")
            seedTexel = rt.component_wise("clamp", rt.binary("-", rt.binary(">>", rt.component_wise("max", seed256, rt.construct(2, rt.i(0), base="int"), width=2), rt.i(8), 2, "int"), rt.construct(2, _u_tileOffset, base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", texSize, rt.i(1), 2, "int"), width=2)
            seedColor = rt.swizzle(rt.texel_fetch(_u_inputTex, seedTexel, rt.i(0)), "rgb")
            radius = rt.binary("+", rt.i(1434), rt.construct(1, rt.binary(">>", rt.binary("*", rt.i(1638), rt.binary("-", rt.i(65535), lum16__vec3(seedColor), 1, "uint"), 1, "uint"), rt.i(16), 1, "uint"), base="int"), 1, "int")
            d = rt.construct(1, isqrt__uint(rt.construct(1, best, base="uint")), base="int")
            aa = rt.construct(1, rt.binary("/", rt.i(2097152), c256, 1, "uint"), base="int")
            t = (rt.i(0) if rt.binary("<=", d, rt.binary("-", radius, aa, 1, "int")) else (rt.i(4096) if rt.binary(">=", d, rt.binary("+", radius, aa, 1, "int")) else rt.binary("/", rt.binary("<<", rt.construct(1, rt.binary("+", rt.binary("-", d, radius, 1, "int"), aa, 1, "int"), base="uint"), rt.i(12), 1, "uint"), rt.construct(1, rt.binary("*", rt.i(2), aa, 1, "int"), base="uint"), 1, "uint")))
            inside = rt.binary("-", rt.i(4096), smooth12__uint(t), 1, "uint")
            paper = rt.construct(3, unorm16__float(rt.swizzle(_u_paperColor, "r")), unorm16__float(rt.swizzle(_u_paperColor, "g")), unorm16__float(rt.swizzle(_u_paperColor, "b")), base="uint")
            ink = rt.construct(3, unorm16__float(rt.swizzle(seedColor, "r")), unorm16__float(rt.swizzle(seedColor, "g")), unorm16__float(rt.swizzle(seedColor, "b")), base="uint")
            result[:] = rt.binary("/", rt.construct_raw(3, rt.construct(3, rt.binary(">>", rt.binary("+", rt.binary("*", paper, rt.binary("-", rt.i(4096), inside, 1, "uint"), 3, "uint"), rt.binary("*", ink, inside, 3, "uint"), 3, "uint"), rt.construct(3, rt.i(12), base="uint"), 3, "uint"))), rt.f(65536.0), 3, 'float')
        else:
            if (bool((bool(rt.binary("==", _u_MODE, rt.i(1))) or bool(rt.binary("==", _u_MODE, rt.i(2))))) or bool(rt.binary("==", _u_MODE, rt.i(3)))):
                pos = center
                grain = g256
                if rt.binary("==", _u_MODE, rt.i(3)):
                    (pos.__setitem__(0, rt.binary("*", rt.binary("+", rt.binary("+", rt.swizzle(px, "x"), rt.swizzle(px, "y"), 1, "uint"), rt.i(1), 1, "uint"), rt.i(256), 1, "uint")), pos.__setitem__(1, rt.binary("*", rt.binary("-", rt.binary("+", rt.swizzle(px, "y"), rt.i(1048576), 1, "uint"), rt.swizzle(px, "x"), 1, "uint"), rt.i(256), 1, "uint")), pos)[-1]
                    grain = rt.binary(">>", rt.binary("+", rt.binary("*", g256, rt.i(92682), 1, "uint"), rt.i(32768), 1, "uint"), rt.i(16), 1, "uint")
                lattice = rt.construct(2, 0.0, base="uint")
                if rt.binary("==", _u_MODE, rt.i(1)):
                    lattice[:] = rt.construct(2, grain, base="uint")
                else:
                    (lattice.__setitem__(0, grain), lattice.__setitem__(1, rt.binary("*", grain, rt.i(8), 1, "uint")), lattice)[-1]
                n = vnoise__uvec2_uvec2_uint(pos, lattice, s)
                (result.__setitem__(0, inkStep__uint_uint_int(n, unorm16__float(rt.swizzle(src, "r")), d256)), result.__setitem__(1, inkStep__uint_uint_int(n, unorm16__float(rt.swizzle(src, "g")), d256)), result.__setitem__(2, inkStep__uint_uint_int(n, unorm16__float(rt.swizzle(src, "b")), d256)), result)[-1]
            else:
                l = lum16__vec3(rt.swizzle(src, "rgb"))
                amp = rt.binary("-", rt.i(78643), rt.binary(">>", rt.binary("*", rt.i(39322), l, 1, "uint"), rt.i(16), 1, "uint"), 1, "uint")
                clumpNoise = rt.binary(">>", rt.binary("*", fbm__uvec2_uint_uint(center, g256, s), rt.binary(">>", amp, rt.i(2), 1, "uint"), 1, "uint"), rt.i(14), 1, "uint")
                result[:] = (rt.construct(3, rt.f(0.97)) if rt.binary(">", inkStep__uint_uint_int(clumpNoise, l, d256), rt.f(0.5)) else rt.construct(3, rt.f(0.05)))
        g.fragColor[:] = rt.construct(4, result, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
