def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_spacing = U.get("spacing", rt.f(0.0))
    _u_depth = U.get("depth", rt.f(0.0))
    _u_brightness = U.get("brightness", rt.f(0.0))
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
    def hash12__ivec2(p):
        p = rt.copy(p, "int")
        return rt.binary("/", rt.construct(1, rt.binary(">>", rt.swizzle(rt.pcg3d(rt.construct(3, rt.construct(2, p, base="uint"), rt.i(0), base="uint")), "x"), rt.i(8), 1, "uint")), rt.f(16777216.0), 1, "float")
    def hash22__ivec2_int(p, seedVal):
        p = rt.copy(p, "int")
        h = rt.binary(">>", rt.swizzle(rt.pcg3d(rt.construct(3, rt.construct(2, p, base="uint"), rt.construct(1, seedVal, base="uint"), base="uint")), "xy"), rt.construct(2, rt.i(8), base="uint"), 2, "uint")
        return rt.construct(2, rt.binary("/", rt.construct_raw(2, rt.construct(2, h)), rt.f(16777216.0), 2, 'float'))
    def vnoise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.construct(2, rt.component_wise("floor", p, width=2), base="int")
        f = rt.component_wise("fract", p, width=2)
        u = rt.construct(2, rt.binary("*", rt.binary("*", f, f, 2, 'float'), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, 'float'), 2, 'float'), 2, 'float'))
        return rt.component_wise("mix", rt.component_wise("mix", hash12__ivec2(i), hash12__ivec2(rt.binary("+", i, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__ivec2(rt.binary("+", i, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int")), hash12__ivec2(rt.binary("+", i, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def voronoiF1F2__vec2_float_int(p, jitter, seedVal):
        p = rt.copy(p, "float")
        _g = rt.component_wise("floor", p, width=2)
        f = rt.construct(2, rt.binary("-", p, _g, 2, 'float'))
        gi = rt.construct(2, _g, base="int")
        best = rt.f(1000000000.0)
        second = rt.f(1000000000.0)
        y = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                cell = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                pt = rt.construct(2, rt.binary("+", rt.construct(2, rt.binary("+", cell, rt.f(0.5), 2, 'float')), rt.construct(2, rt.binary("*", rt.construct(2, rt.binary("-", hash22__ivec2_int(rt.binary("+", gi, rt.construct(2, x, y, base="int"), 2, "int"), seedVal), rt.f(0.5), 2, 'float')), jitter, 2, 'float')), 2, 'float'))
                d = rt.dot(rt.binary("-", pt, f, 2, 'float'), rt.binary("-", pt, f, 2, 'float'))
                if rt.binary("<", d, best):
                    second = best
                    best = d
                else:
                    if rt.binary("<", d, second):
                        second = d
        return rt.construct(2, rt.component_wise("sqrt", best, width=1), rt.component_wise("sqrt", second, width=1))
    def reliefShade__float_float_float_float_float(hC, hR, hT, strength, lightAngleDeg):
        grad = rt.construct(2, rt.binary("*", rt.construct_raw(2, rt.binary("-", hR, hC, 1, "float"), rt.binary("-", hT, hC, 1, "float")), strength, 2, 'float'))
        n = rt.normalize(rt.construct(3, rt.unary("-", grad), rt.f(1.0)))
        a = rt.component_wise("radians", lightAngleDeg, width=1)
        L = rt.normalize(rt.construct(3, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1), rt.f(0.75)))
        return rt.component_wise("clamp", rt.dot(n, L), rt.f(0.0), rt.f(1.0), width=1)
    def crackMask__vec2_float_float_int(gc, spacingPx, depthPct, seedVal):
        gc = rt.copy(gc, "float")
        wob = rt.construct(2, rt.binary("*", rt.construct_raw(2, vnoise__vec2(rt.construct(2, rt.binary("/", gc, rt.f(6.0), 2, 'float'))), vnoise__vec2(rt.construct(2, rt.binary("+", rt.binary("/", gc, rt.f(6.0), 2, 'float'), rt.construct_raw(2, rt.f(37.7), rt.f(91.3)), 2, 'float')))), rt.f(2.0), 2, 'float'))
        p = rt.construct(2, rt.binary("/", rt.binary("+", gc, wob, 2, 'float'), spacingPx, 2, 'float'))
        f1f2 = voronoiF1F2__vec2_float_int(p, rt.f(1.0), seedVal)
        d = rt.binary("*", rt.binary("-", rt.swizzle(f1f2, "y"), rt.swizzle(f1f2, "x"), 1, "float"), spacingPx, 1, "float")
        edge = rt.binary("+", rt.f(1.5), rt.binary("*", rt.binary("/", depthPct, rt.f(100.0), 1, "float"), rt.f(2.0), 1, "float"), 1, "float")
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), edge, d, width=1), 1, "float")
    def main__void():
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        uv = rt.construct(2, rt.fdiv(rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2))
        src = rt.texture(_u_inputTex, uv)
        kC = crackMask__vec2_float_float_int(globalCoord, _u_spacing, _u_depth, _u_seed)
        kR = crackMask__vec2_float_float_int(rt.construct(2, rt.binary("+", globalCoord, rt.construct_raw(2, rt.f(1.0), rt.f(0.0)), 2, 'float')), _u_spacing, _u_depth, _u_seed)
        kL = crackMask__vec2_float_float_int(rt.construct(2, rt.binary("-", globalCoord, rt.construct_raw(2, rt.f(1.0), rt.f(0.0)), 2, 'float')), _u_spacing, _u_depth, _u_seed)
        kT = crackMask__vec2_float_float_int(rt.construct(2, rt.binary("+", globalCoord, rt.construct_raw(2, rt.f(0.0), rt.f(1.0)), 2, 'float')), _u_spacing, _u_depth, _u_seed)
        kB = crackMask__vec2_float_float_int(rt.construct(2, rt.binary("-", globalCoord, rt.construct_raw(2, rt.f(0.0), rt.f(1.0)), 2, 'float')), _u_spacing, _u_depth, _u_seed)
        gradK = rt.construct(2, rt.binary("*", rt.binary("-", kR, kL, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("*", rt.binary("-", kT, kB, 1, "float"), rt.f(0.5), 1, "float"))
        hC = rt.unary("-", kC)
        hR = rt.binary("-", hC, rt.swizzle(gradK, "x"), 1, "float")
        hT = rt.binary("-", hC, rt.swizzle(gradK, "y"), 1, "float")
        shadeStrength = rt.f(6.0)
        shade = reliefShade__float_float_float_float_float(hC, hR, hT, shadeStrength, rt.f(135.0))
        gradMagK = rt.length(gradK)
        wallMask = rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.02), gradMagK, width=1)
        shadeMul = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", shade, rt.f(0.6), 1, "float"), rt.f(2.0), 1, "float"), rt.binary("/", rt.binary("*", rt.f(0.25), _u_depth, 1, "float"), rt.f(100.0), 1, "float"), 1, "float"), wallMask, 1, "float"), 1, "float")
        darkened = rt.construct(3, rt.binary("*", rt.swizzle(src, "rgb"), rt.component_wise("mix", rt.f(1.0), rt.binary("+", rt.f(0.35), rt.binary("*", rt.binary("/", _u_brightness, rt.f(100.0), 1, "float"), rt.f(0.5), 1, "float"), 1, "float"), kC, width=1), 3, 'float'))
        result = rt.component_wise("clamp", rt.binary("*", darkened, shadeMul, 3, 'float'), rt.f(0.0), rt.f(1.0), width=3)
        g.fragColor[:] = rt.construct(4, result, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
