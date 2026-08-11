def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_metric = U.get("metric", 0)
    _u_cellVariation = U.get("cellVariation", rt.f(0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_colorMode = U.get("colorMode", 0)
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    def pcg3d__uvec3(v):
        v = rt.copy(v, "uint")
        v[:] = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v[:] = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def hash3__vec3(p):
        p = rt.copy(p, "float")
        p[:] = rt.binary("+", p, rt.binary("*", rt.construct(1, _u_seed), rt.f(0.1), 1, "float"), 3, "float")
        q = rt.construct(3, rt.binary("+", rt.construct(3, rt.binary("*", p, rt.f(1000.0), 3, "float"), base="int"), rt.i(65536), 3, "int"), base="uint")
        q[:] = rt.pcg3d(q)
        return rt.binary("/", rt.construct(3, q), rt.f(4294967295.0), 3, "float")
    def cellNoise3D__vec3(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=3)
        f = rt.component_wise("fract", p, width=3)
        minDist = rt.f(10.0)
        cellId = rt.f(0.0)
        z = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                z = rt.binary("+", z, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", z, rt.i(1))):
                break
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
                    neighbor = rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z))
                    cellPos = rt.binary("+", i, neighbor, 3, "float")
                    randomOffset = hash3__vec3(cellPos)
                    jitter = rt.binary("*", _u_cellVariation, rt.f(0.01), 1, "float")
                    cellPoint = rt.binary("+", neighbor, rt.component_wise("mix", rt.construct(3, rt.f(0.5)), randomOffset, jitter, width=3), 3, "float")
                    diff = rt.binary("-", cellPoint, f, 3, "float")
                    dist = rt.f(0.0)
                    if rt.binary("==", _u_metric, rt.i(0)):
                        dist = rt.length(diff)
                    else:
                        if rt.binary("==", _u_metric, rt.i(1)):
                            dist = rt.binary("+", rt.binary("+", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), 1, "float"), rt.component_wise("abs", rt.swizzle(diff, "z"), width=1), 1, "float")
                        else:
                            dist = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.component_wise("abs", rt.swizzle(diff, "y"), width=1), width=1), rt.component_wise("abs", rt.swizzle(diff, "z"), width=1), width=1)
                    if rt.binary("<", dist, minDist):
                        minDist = dist
                        cellId = rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(cellPos, "x"), rt.f(73.0), 1, "float"), rt.binary("*", rt.swizzle(cellPos, "y"), rt.f(157.0), 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(cellPos, "z"), rt.f(311.0), 1, "float"), 1, "float")
        return rt.construct(2, minDist, cellId)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        pixelCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        x = rt.swizzle(pixelCoord, "x")
        y = rt.binary("%", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        z = rt.binary("/", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        if (bool((bool(rt.binary(">=", x, volSize)) or bool(rt.binary(">=", y, volSize)))) or bool(rt.binary(">=", z, volSize))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(0.0))
            return
        p = rt.binary("-", rt.binary("*", rt.binary("/", rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z)), rt.binary("-", volSizeF, rt.f(1.0), 1, "float"), 3, "float"), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
        scaledP = rt.binary("*", p, rt.binary("-", rt.f(16.0), _u_scale, 1, "float"), 3, "float")
        result = cellNoise3D__vec3(scaledP)
        dist = rt.swizzle(result, "x")
        cellId = rt.swizzle(result, "y")
        eps = rt.binary("/", rt.f(0.01), _u_scale, 1, "float")
        dxp = rt.swizzle(cellNoise3D__vec3(rt.binary("+", scaledP, rt.construct(3, eps, rt.f(0.0), rt.f(0.0)), 3, "float")), "x")
        dyp = rt.swizzle(cellNoise3D__vec3(rt.binary("+", scaledP, rt.construct(3, rt.f(0.0), eps, rt.f(0.0)), 3, "float")), "x")
        dzp = rt.swizzle(cellNoise3D__vec3(rt.binary("+", scaledP, rt.construct(3, rt.f(0.0), rt.f(0.0), eps), 3, "float")), "x")
        gradient = rt.binary("/", rt.construct(3, rt.binary("-", dxp, dist, 1, "float"), rt.binary("-", dyp, dist, 1, "float"), rt.binary("-", dzp, dist, 1, "float")), eps, 3, "float")
        normal = rt.normalize(rt.binary("+", rt.unary("-", gradient), rt.construct(3, rt.f(1e-06)), 3, "float"))
        normalizer = rt.f(0.0)
        if rt.binary("==", _u_metric, rt.i(0)):
            normalizer = rt.f(0.866)
        else:
            if rt.binary("==", _u_metric, rt.i(1)):
                normalizer = rt.f(1.5)
            else:
                normalizer = rt.f(0.6)
        normalizedDist = rt.binary("-", rt.f(1.0), rt.component_wise("clamp", rt.binary("/", dist, normalizer, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), 1, "float")
        h1 = rt.component_wise("fract", rt.binary("*", cellId, rt.f(0.0127), 1, "float"), width=1)
        h2 = rt.component_wise("fract", rt.binary("*", cellId, rt.f(0.0231), 1, "float"), width=1)
        h3 = rt.component_wise("fract", rt.binary("*", cellId, rt.f(0.0347), 1, "float"), width=1)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            g.fragColor[:] = rt.construct(4, normalizedDist, normalizedDist, normalizedDist, rt.f(1.0))
        else:
            g.fragColor[:] = rt.construct(4, normalizedDist, h1, h2, h3)
        g.geoOut[:] = rt.construct(4, rt.binary("+", rt.binary("*", normal, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float"), normalizedDist)
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
