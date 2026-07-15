def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_mode = U["mode"]
    _u_scale = U["scale"]
    _u_edgeWidth = U["edgeWidth"]
    _u_seed = U["seed"]
    _u_invert = U["invert"]
    _u_time = U["time"]
    _u_speed = U["speed"]
    g.TAU = rt.f(6.28318530718)
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525)), 3), rt.construct(1, rt.i(1013904223)), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16)), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1)))
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        p = rt.binary("*", globalUV, rt.binary("-", rt.f(31.0), _u_scale, 1), 2)
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspect, 1))
        spd = rt.component_wise("floor", _u_speed, width=1)
        cellCoord = rt.component_wise("floor", p, width=2)
        cellFract = rt.component_wise("fract", p, width=2)
        d1 = rt.f(1e10)
        nearestPoint = rt.construct(2, rt.f(0.0))
        nearestCell = rt.construct(2, rt.f(0.0))
        nearestHash = rt.f(0.0)
        y = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(1))):
                break
            x = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1)
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(1))):
                    break
                neighbor = rt.construct(2, x, y)
                cellId = rt.binary("+", cellCoord, neighbor, 2)
                rnd = prng__vec3(rt.construct(3, cellId, _u_seed))
                wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", g.TAU, _u_time, 1), spd, 1), rt.binary("*", rt.swizzle(rnd, "xy"), g.TAU, 2), 2), width=2), rt.f(0.15), 2), rt.component_wise("min", spd, rt.f(1.0), width=1), 2)
                point = rt.binary("-", rt.binary("+", rt.binary("+", neighbor, rt.swizzle(rnd, "xy"), 2), wobble, 2), cellFract, 2)
                dist = rt.dot(point, point)
                if rt.binary("<", dist, d1):
                    d1 = dist
                    nearestPoint = point
                    nearestCell = cellId
                    nearestHash = rt.swizzle(rnd, "z")
        edgeDist = rt.f(1e10)
        y = rt.unary("-", rt.i(2))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                y = rt.binary("+", y, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<=", y, rt.i(2))):
                break
            x = rt.unary("-", rt.i(2))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    x = rt.binary("+", x, rt.i(1), 1)
                _for3_first = False
                if not (rt.binary("<=", x, rt.i(2))):
                    break
                neighbor = rt.construct(2, x, y)
                cellId = rt.binary("+", cellCoord, neighbor, 2)
                if rt.binary("==", cellId, nearestCell):
                    continue
                rnd = prng__vec3(rt.construct(3, cellId, _u_seed))
                wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", g.TAU, _u_time, 1), spd, 1), rt.binary("*", rt.swizzle(rnd, "xy"), g.TAU, 2), 2), width=2), rt.f(0.15), 2), rt.component_wise("min", spd, rt.f(1.0), width=1), 2)
                point = rt.binary("-", rt.binary("+", rt.binary("+", neighbor, rt.swizzle(rnd, "xy"), 2), wobble, 2), cellFract, 2)
                mid = rt.binary("*", rt.binary("+", nearestPoint, point, 2), rt.f(0.5), 2)
                edge = rt.normalize(rt.binary("-", point, nearestPoint, 2))
                d = rt.component_wise("abs", rt.dot(mid, edge), width=1)
                edgeDist = rt.component_wise("min", edgeDist, d, width=1)
        onEdge = (rt.component_wise("step", edgeDist, _u_edgeWidth, width=1) if rt.binary(">", _u_edgeWidth, rt.f(0.0)) else rt.f(0.0))
        mask = rt.f(0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            mask = onEdge
        else:
            cellChoice = rt.component_wise("step", rt.f(0.5), nearestHash, width=1)
            if rt.binary("==", _u_invert, rt.i(1)):
                cellChoice = rt.binary("-", rt.f(1.0), cellChoice, 1)
            mask = rt.component_wise("mix", cellChoice, rt.f(0.5), onEdge, width=1)
        if rt.binary("&&", rt.binary("==", _u_mode, rt.i(0)), rt.binary("==", _u_invert, rt.i(1))):
            mask = rt.binary("-", rt.f(1.0), mask, 1)
        color = rt.component_wise("mix", colorA, colorB, mask, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
