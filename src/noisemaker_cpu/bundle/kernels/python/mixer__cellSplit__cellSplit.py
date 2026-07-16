def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_mode = U.get("mode", 0)
    _u_scale = U.get("scale", rt.f(0.0))
    _u_edgeWidth = U.get("edgeWidth", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_invert = U.get("invert", 0)
    _u_time = U.get("time", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530718)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
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
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        p = rt.binary("*", globalUV, rt.binary("-", rt.f(31.0), _u_scale, 1, "float"), 2, "float")
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspect, 1, "float"))
        spd = rt.component_wise("floor", _u_speed, width=1)
        cellCoord = rt.component_wise("floor", p, width=2)
        cellFract = rt.component_wise("fract", p, width=2)
        d1 = rt.f(10000000000.0)
        nearestPoint = rt.construct(2, rt.f(0.0))
        nearestCell = rt.construct(2, rt.f(0.0))
        nearestHash = rt.f(0.0)
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
                neighbor = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                cellId = rt.binary("+", cellCoord, neighbor, 2, "float")
                rnd = prng__vec3(rt.construct(3, cellId, rt.construct(1, _u_seed)))
                wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", g.TAU, _u_time, 1, "float"), spd, 1, "float"), rt.binary("*", rt.swizzle(rnd, "xy"), g.TAU, 2, "float"), 2, "float"), width=2), rt.f(0.15), 2, "float"), rt.component_wise("min", spd, rt.f(1.0), width=1), 2, "float")
                point = rt.binary("-", rt.binary("+", rt.binary("+", neighbor, rt.swizzle(rnd, "xy"), 2, "float"), wobble, 2, "float"), cellFract, 2, "float")
                dist = rt.dot(point, point)
                if rt.binary("<", dist, d1):
                    d1 = dist
                    nearestPoint = point
                    nearestCell = cellId
                    nearestHash = rt.swizzle(rnd, "z")
        edgeDist = rt.f(10000000000.0)
        y = rt.unary("-", rt.i(2))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", y, rt.i(2))):
                break
            x = rt.unary("-", rt.i(2))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<=", x, rt.i(2))):
                    break
                neighbor = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                cellId = rt.binary("+", cellCoord, neighbor, 2, "float")
                if rt.binary("==", cellId, nearestCell):
                    continue
                rnd = prng__vec3(rt.construct(3, cellId, rt.construct(1, _u_seed)))
                wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", g.TAU, _u_time, 1, "float"), spd, 1, "float"), rt.binary("*", rt.swizzle(rnd, "xy"), g.TAU, 2, "float"), 2, "float"), width=2), rt.f(0.15), 2, "float"), rt.component_wise("min", spd, rt.f(1.0), width=1), 2, "float")
                point = rt.binary("-", rt.binary("+", rt.binary("+", neighbor, rt.swizzle(rnd, "xy"), 2, "float"), wobble, 2, "float"), cellFract, 2, "float")
                mid = rt.binary("*", rt.binary("+", nearestPoint, point, 2, "float"), rt.f(0.5), 2, "float")
                edge = rt.normalize(rt.binary("-", point, nearestPoint, 2, "float"))
                d = rt.component_wise("abs", rt.dot(mid, edge), width=1)
                edgeDist = rt.component_wise("min", edgeDist, d, width=1)
        onEdge = (rt.component_wise("step", edgeDist, _u_edgeWidth, width=1) if rt.binary(">", _u_edgeWidth, rt.f(0.0)) else rt.f(0.0))
        mask = rt.f(0.0)
        cellChoice = rt.f(0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            mask = onEdge
        else:
            cellChoice = rt.component_wise("step", rt.f(0.5), nearestHash, width=1)
            if rt.binary("==", _u_invert, rt.i(1)):
                cellChoice = rt.binary("-", rt.f(1.0), cellChoice, 1, "float")
            mask = rt.component_wise("mix", cellChoice, rt.f(0.5), onEdge, width=1)
        if (bool(rt.binary("==", _u_mode, rt.i(0))) and bool(rt.binary("==", _u_invert, rt.i(1)))):
            mask = rt.binary("-", rt.f(1.0), mask, 1, "float")
        color = rt.component_wise("mix", colorA, colorB, mask, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
