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
    def hash12__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.f(0.1031), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "x"), rt.swizzle(p3, "y"), 1, "float"), rt.swizzle(p3, "z"), 1, "float"), width=1)
    def hash22__vec2(p):
        p = rt.copy(p, "float")
        p3 = rt.component_wise("fract", rt.binary("*", rt.construct(3, rt.swizzle(p, "xyx")), rt.construct(3, rt.f(0.1031), rt.f(0.103), rt.f(0.0973)), 3, "float"), width=3)
        p3[:] = rt.binary("+", p3, rt.dot(p3, rt.binary("+", rt.swizzle(p3, "yzx"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p3, "xx"), rt.swizzle(p3, "yz"), 2, "float"), rt.swizzle(p3, "zy"), 2, "float"), width=2)
    def lum__vec3(c):
        c = rt.copy(c, "float")
        return rt.dot(c, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def vnoise__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        u = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        return rt.component_wise("mix", rt.component_wise("mix", hash12__vec2(i), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(0.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.component_wise("mix", hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(0.0), rt.f(1.0)), 2, "float")), hash12__vec2(rt.binary("+", i, rt.construct(2, rt.f(1.0), rt.f(1.0)), 2, "float")), rt.swizzle(u, "x"), width=1), rt.swizzle(u, "y"), width=1)
    def fbm__vec2(p):
        p = rt.copy(p, "float")
        v = rt.f(0.0)
        a = rt.f(0.5)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(5))):
                break
            v = rt.binary("+", v, rt.binary("*", a, vnoise__vec2(p), 1, "float"), 1, "float")
            p[:] = rt.binary("*", p, rt.f(2.03), 2, "float")
            a = rt.binary("*", a, rt.f(0.5), 1, "float")
        return v
    def voronoiCell__vec2_float_float(p, jitter, seedVal):
        p = rt.copy(p, "float")
        _g = rt.component_wise("floor", p, width=2)
        f = rt.binary("-", p, _g, 2, "float")
        best = rt.f(1000000000.0)
        res = rt.construct(4, rt.f(0.0))
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
                cell = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                pt = rt.binary("+", rt.binary("+", cell, rt.f(0.5), 2, "float"), rt.binary("*", rt.binary("-", hash22__vec2(rt.binary("+", rt.binary("+", _g, cell, 2, "float"), rt.binary("*", seedVal, rt.f(101.7), 1, "float"), 2, "float")), rt.f(0.5), 2, "float"), jitter, 2, "float"), 2, "float")
                d = rt.dot(rt.binary("-", pt, f, 2, "float"), rt.binary("-", pt, f, 2, "float"))
                if rt.binary("<", d, best):
                    best = d
                    res[:] = rt.construct(4, rt.binary("+", _g, pt, 2, "float"), rt.binary("+", _g, cell, 2, "float"))
        return res
    def tonemap2__float_vec3_vec3(t, ink, paper):
        ink = rt.copy(ink, "float")
        paper = rt.copy(paper, "float")
        return rt.component_wise("mix", ink, paper, rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1), width=3)
    def rotate2D__vec2_float(v, angleDeg):
        v = rt.copy(v, "float")
        a = rt.component_wise("radians", angleDeg, width=1)
        co = rt.component_wise("cos", a, width=1)
        si = rt.component_wise("sin", a, width=1)
        return rt.matrix_mult(rt.construct(4, co, rt.unary("-", si), si, co), v, 2)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        alpha = rt.swizzle(rt.texture(_u_inputTex, uv), "a")
        result = rt.construct(3, 0.0)
        p = rt.construct(2, 0.0)
        cell = rt.construct(4, 0.0)
        seedGc = rt.construct(2, 0.0)
        seedUV = rt.construct(2, 0.0)
        seedColor = rt.construct(3, 0.0)
        radius = rt.f(0.0)
        d = rt.f(0.0)
        aa = rt.f(0.0)
        inside = rt.f(0.0)
        gc = rt.construct(2, 0.0)
        noiseP = rt.construct(2, 0.0)
        n = rt.f(0.0)
        src = rt.construct(3, 0.0)
        l = rt.f(0.0)
        clumpNoise = rt.f(0.0)
        if rt.binary("==", _u_MODE, rt.i(0)):
            p = rt.binary("/", globalCoord, _u_cellSize, 2, "float")
            cell = voronoiCell__vec2_float_float(p, rt.f(0.9), rt.construct(1, _u_seed))
            seedGc = rt.binary("*", rt.swizzle(cell, "xy"), _u_cellSize, 2, "float")
            seedUV = rt.component_wise("clamp", rt.binary("/", rt.binary("-", seedGc, _u_tileOffset, 2, "float"), _u_resolution, 2, "float"), rt.f(0.0), rt.f(1.0), width=2)
            seedColor = rt.swizzle(rt.texture(_u_inputTex, seedUV), "rgb")
            radius = rt.binary("+", rt.f(0.35), rt.binary("*", rt.f(0.4), rt.binary("-", rt.f(1.0), lum__vec3(seedColor), 1, "float"), 1, "float"), 1, "float")
            d = rt.length(rt.binary("-", p, rt.swizzle(cell, "xy"), 2, "float"))
            aa = rt.component_wise("max", rt.binary("*", rt.fwidth(d), rt.f(1.5), 1, "float"), rt.f(1e-05), width=1)
            inside = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", radius, aa, 1, "float"), rt.binary("+", radius, aa, 1, "float"), d, width=1), 1, "float")
            result[:] = rt.component_wise("mix", _u_paperColor, seedColor, inside, width=3)
        else:
            if (bool((bool(rt.binary("==", _u_MODE, rt.i(1))) or bool(rt.binary("==", _u_MODE, rt.i(2))))) or bool(rt.binary("==", _u_MODE, rt.i(3)))):
                gc = globalCoord
                if rt.binary("==", _u_MODE, rt.i(3)):
                    gc[:] = rotate2D__vec2_float(gc, rt.f(45.0))
                noiseP = rt.construct(2, 0.0)
                if rt.binary("==", _u_MODE, rt.i(1)):
                    noiseP[:] = rt.binary("/", gc, _u_grainSize, 2, "float")
                else:
                    noiseP[:] = rt.binary("*", gc, rt.construct(2, rt.binary("/", rt.f(1.0), _u_grainSize, 1, "float"), rt.binary("/", rt.f(1.0), rt.binary("*", _u_grainSize, rt.f(8.0), 1, "float"), 1, "float")), 2, "float")
                n = vnoise__vec2(rt.binary("+", noiseP, rt.binary("*", rt.construct(1, _u_seed), rt.f(101.7), 1, "float"), 2, "float"))
                n = rt.binary("+", n, rt.binary("/", rt.binary("-", _u_density, rt.f(50.0), 1, "float"), rt.f(100.0), 1, "float"), 1, "float")
                src = rt.swizzle(rt.texture(_u_inputTex, uv), "rgb")
                (result.__setitem__(0, rt.component_wise("step", n, rt.swizzle(src, "r"), width=1)), result.__setitem__(1, rt.component_wise("step", n, rt.swizzle(src, "g"), width=1)), result.__setitem__(2, rt.component_wise("step", n, rt.swizzle(src, "b"), width=1)), result)[-1]
            else:
                src = rt.swizzle(rt.texture(_u_inputTex, uv), "rgb")
                l = lum__vec3(src)
                clumpNoise = rt.binary("*", fbm__vec2(rt.binary("+", rt.binary("/", globalCoord, rt.binary("*", _u_grainSize, rt.f(4.0), 1, "float"), 2, "float"), rt.binary("*", rt.construct(1, _u_seed), rt.f(101.7), 1, "float"), 2, "float")), rt.component_wise("mix", rt.f(1.2), rt.f(0.6), l, width=1), 1, "float")
                clumpNoise = rt.binary("+", clumpNoise, rt.binary("/", rt.binary("-", _u_density, rt.f(50.0), 1, "float"), rt.f(100.0), 1, "float"), 1, "float")
                result[:] = tonemap2__float_vec3_vec3(rt.component_wise("step", clumpNoise, l, width=1), rt.construct(3, rt.f(0.05)), rt.construct(3, rt.f(0.97)))
        g.fragColor[:] = rt.construct(4, result, alpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
run_pixel.uses_derivatives = True
