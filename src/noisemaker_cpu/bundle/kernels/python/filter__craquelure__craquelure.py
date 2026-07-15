def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_spacing = U["spacing"]
    _u_depth = U["depth"]
    _u_brightness = U["brightness"]
    _u_seed = U["seed"]
    def hash12__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def hash22__vec2(p):
        p = rt.copy(p)
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.construct(3, rt.f(0.1031), rt.f(0.103), rt.f(0.0973)), 3, "float"), width=3)
        p3 = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "xx"), rt.swizzle(p3, "yz"), 2, "float"), rt.swizzle(p3, "zy"), 2, "float"), width=2)
    def vnoise__vec2(p):
        p = rt.copy(p)
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def voronoiF1F2__vec2_float_float(p, jitter, seedVal):
        p = rt.copy(p)
        g = rt.component_wise("floor", p, width=2)
        f = rt.binary("-", p, g, 2, "float")
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
                pt = rt.binary("+", rt.binary("+", cell, rt.f(0.5), 2, "float"), rt.binary("*", rt.binary("-", hash22__vec2(rt.binary("+", rt.binary("+", g, cell, 2, "float"), rt.binary("*", seedVal, rt.f(101.7), 1, "float"), 2, "float")), rt.f(0.5), 2, "float"), jitter, 2, "float"), 2, "float")
                d = rt.dot(rt.binary("-", pt, f, 2, "float"), rt.binary("-", pt, f, 2, "float"))
                if rt.binary("<", d, best):
                    second = best
                    best = d
                else:
                    if rt.binary("<", d, second):
                        second = d
        return rt.construct(2, rt.component_wise("sqrt", best, width=1), rt.component_wise("sqrt", second, width=1))
    def reliefShade__float_float_float_float_float(hC, hR, hT, strength, lightAngleDeg):
        grad = rt.binary("*", rt.construct(2, rt.binary("-", hR, hC, 1, "float"), rt.binary("-", hT, hC, 1, "float")), strength, 2, "float")
        n = rt.normalize(rt.construct(3, rt.unary("-", grad), rt.f(1.0)))
        a = rt.component_wise("radians", lightAngleDeg, width=1)
        L = rt.normalize(rt.construct(3, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1), rt.f(0.75)))
        return rt.component_wise("clamp", rt.dot(n, L), rt.f(0.0), rt.f(1.0), width=1)
    def crackMask__vec2_float_float_float(gc, spacingPx, depthPct, seedVal):
        gc = rt.copy(gc)
        wob = rt.binary("*", rt.construct(2, vnoise__vec2(rt.binary("/", gc, rt.f(6.0), 2, "float")), vnoise__vec2(rt.binary("+", rt.binary("/", gc, rt.f(6.0), 2, "float"), rt.construct(2, rt.f(37.7), rt.f(91.3)), 2, "float"))), rt.f(2.0), 2, "float")
        p = rt.binary("/", rt.binary("+", gc, wob, 2, "float"), spacingPx, 2, "float")
        f1f2 = voronoiF1F2__vec2_float_float(p, rt.f(1.0), seedVal)
        d = rt.binary("*", rt.binary("-", rt.swizzle(f1f2, "y"), rt.swizzle(f1f2, "x"), 1, "float"), spacingPx, 1, "float")
        edge = rt.binary("+", rt.f(1.5), rt.binary("*", rt.binary("/", depthPct, rt.f(100.0), 1, "float"), rt.f(2.0), 1, "float"), 1, "float")
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), edge, d, width=1), 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        src = rt.texture(_u_inputTex, uv)
        seedF = rt.construct(1, _u_seed)
        kC = crackMask__vec2_float_float_float(globalCoord, _u_spacing, _u_depth, seedF)
        kR = crackMask__vec2_float_float_float(rt.binary("+", globalCoord, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), _u_spacing, _u_depth, seedF)
        kL = crackMask__vec2_float_float_float(rt.binary("-", globalCoord, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float"), _u_spacing, _u_depth, seedF)
        kT = crackMask__vec2_float_float_float(rt.binary("+", globalCoord, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), _u_spacing, _u_depth, seedF)
        kB = crackMask__vec2_float_float_float(rt.binary("-", globalCoord, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float"), _u_spacing, _u_depth, seedF)
        gradK = rt.construct(2, rt.binary("*", rt.binary("-", kR, kL, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("*", rt.binary("-", kT, kB, 1, "float"), rt.f(0.5), 1, "float"))
        hC = rt.unary("-", kC)
        hR = rt.binary("-", hC, rt.swizzle(gradK, "x"), 1, "float")
        hT = rt.binary("-", hC, rt.swizzle(gradK, "y"), 1, "float")
        shadeStrength = rt.f(6.0)
        shade = reliefShade__float_float_float_float_float(hC, hR, hT, shadeStrength, rt.f(135.0))
        gradMagK = rt.length(gradK)
        wallMask = rt.component_wise("smoothstep", rt.f(0.0), rt.f(0.02), gradMagK, width=1)
        shadeMul = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", shade, rt.f(0.6), 1, "float"), rt.f(2.0), 1, "float"), rt.binary("/", rt.binary("*", rt.f(0.25), _u_depth, 1, "float"), rt.f(100.0), 1, "float"), 1, "float"), wallMask, 1, "float"), 1, "float")
        darkened = rt.binary("*", rt.swizzle(src, "rgb"), rt.component_wise("mix", rt.f(1.0), rt.binary("+", rt.f(0.35), rt.binary("*", rt.binary("/", _u_brightness, rt.f(100.0), 1, "float"), rt.f(0.5), 1, "float"), 1, "float"), kC, width=1), 3, "float")
        result = rt.component_wise("clamp", rt.binary("*", darkened, shadeMul, 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        g.fragColor = rt.construct(4, result, rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
