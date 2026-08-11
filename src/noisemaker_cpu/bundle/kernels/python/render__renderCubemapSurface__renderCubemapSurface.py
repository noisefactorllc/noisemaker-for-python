def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    _u_cubeBasis = U.get("cubeBasis", rt.construct(9, 0.0))
    _u_bgColor = U.get("bgColor", rt.construct(3, 0.0))
    _u_bgAlpha = U.get("bgAlpha", rt.f(0.0))
    _u_volumeCache = T["volumeCache"]
    _u_density = U.get("density", rt.f(0.0))
    _u_absorption = U.get("absorption", rt.f(0.0))
    _u_emission = U.get("emission", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.geoOut = rt.construct(4, 0.0)
    g.MAX_STEPS = rt.i(256)
    def atlasTexel__ivec3_int(p, volSize):
        p = rt.copy(p, "int")
        return rt.construct(2, rt.swizzle(p, "x"), rt.binary("+", rt.swizzle(p, "y"), rt.binary("*", rt.swizzle(p, "z"), volSize, 1, "int"), 1, "int"), base="int")
    def sampleVolume__vec3(worldPos):
        worldPos = rt.copy(worldPos, "float")
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        uvw = rt.binary("+", rt.binary("*", worldPos, rt.f(0.5), 3, "float"), rt.f(0.5), 3, "float")
        uvw[:] = rt.component_wise("clamp", uvw, rt.f(0.0), rt.f(1.0), width=3)
        texelPos = rt.binary("*", uvw, rt.binary("-", volSizeF, rt.f(1.0), 1, "float"), 3, "float")
        texelFloor = rt.component_wise("floor", texelPos, width=3)
        frac = rt.binary("-", texelPos, texelFloor, 3, "float")
        i0 = rt.construct(3, texelFloor, base="int")
        i1 = rt.component_wise("min", rt.binary("+", i0, rt.i(1), 3, "int"), rt.binary("-", volSize, rt.i(1), 1, "int"), width=3)
        c000 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i0, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c100 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i0, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c010 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i1, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c110 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i1, "y"), rt.swizzle(i0, "z"), base="int"), volSize), rt.i(0))
        c001 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i0, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c101 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i0, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c011 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i0, "x"), rt.swizzle(i1, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c111 = rt.texel_fetch(_u_volumeCache, atlasTexel__ivec3_int(rt.construct(3, rt.swizzle(i1, "x"), rt.swizzle(i1, "y"), rt.swizzle(i1, "z"), base="int"), volSize), rt.i(0))
        c00 = rt.component_wise("mix", c000, c100, rt.swizzle(frac, "x"), width=4)
        c10 = rt.component_wise("mix", c010, c110, rt.swizzle(frac, "x"), width=4)
        c01 = rt.component_wise("mix", c001, c101, rt.swizzle(frac, "x"), width=4)
        c11 = rt.component_wise("mix", c011, c111, rt.swizzle(frac, "x"), width=4)
        c0 = rt.component_wise("mix", c00, c10, rt.swizzle(frac, "y"), width=4)
        c1 = rt.component_wise("mix", c01, c11, rt.swizzle(frac, "y"), width=4)
        return rt.component_wise("mix", c0, c1, rt.swizzle(frac, "z"), width=4)
    def intersectBox__vec3_vec3(ro, rd):
        ro = rt.copy(ro, "float")
        rd = rt.copy(rd, "float")
        invRd = rt.binary("/", rt.f(1.0), rd, 3, "float")
        t0 = rt.binary("*", rt.binary("-", rt.unary("-", rt.f(1.0)), ro, 3, "float"), invRd, 3, "float")
        t1 = rt.binary("*", rt.binary("-", rt.f(1.0), ro, 3, "float"), invRd, 3, "float")
        tmin = rt.component_wise("min", t0, t1, width=3)
        tmax = rt.component_wise("max", t0, t1, width=3)
        tEnter = rt.component_wise("max", rt.component_wise("max", rt.swizzle(tmin, "x"), rt.swizzle(tmin, "y"), width=1), rt.swizzle(tmin, "z"), width=1)
        tExit = rt.component_wise("min", rt.component_wise("min", rt.swizzle(tmax, "x"), rt.swizzle(tmax, "y"), width=1), rt.swizzle(tmax, "z"), width=1)
        if (bool(rt.binary(">", tEnter, tExit)) or bool(rt.binary("<", tExit, rt.f(0.0)))):
            return rt.construct(2, rt.unary("-", rt.f(1.0)))
        return rt.construct(2, tEnter, tExit)
    def main__void():
        res = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        uv = rt.binary("/", rt.binary("-", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), rt.binary("*", rt.f(0.5), res, 2, "float"), 2, "float"), rt.binary("*", rt.f(0.5), rt.swizzle(res, "y"), 1, "float"), 2, "float")
        ro = rt.construct(3, rt.f(0.0))
        rd = rt.normalize(rt.matrix_mult(_u_cubeBasis, rt.construct(3, rt.swizzle(uv, "x"), rt.unary("-", rt.swizzle(uv, "y")), rt.f(1.0)), 3))
        col = rt.construct(3, rt.f(0.0))
        trans = rt.f(1.0)
        tb = intersectBox__vec3_vec3(ro, rd)
        t0 = rt.f(0.0)
        dt = rt.f(0.0)
        t = rt.f(0.0)
        if rt.binary(">", rt.swizzle(tb, "y"), rt.f(0.0)):
            t0 = rt.component_wise("max", rt.swizzle(tb, "x"), rt.f(0.0), width=1)
            dt = rt.binary("/", rt.binary("-", rt.swizzle(tb, "y"), t0, 1, "float"), rt.construct(1, g.MAX_STEPS), 1, "float")
            t = t0
            i = rt.i(0)
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    i = rt.binary("+", i, rt.i(1), 1, "int")
                _for0_first = False
                if not (rt.binary("<", i, g.MAX_STEPS)):
                    break
                s = sampleVolume__vec3(rt.binary("+", ro, rt.binary("*", rd, t, 3, "float"), 3, "float"))
                a = rt.binary("-", rt.f(1.0), rt.component_wise("exp", rt.binary("*", rt.binary("*", rt.binary("*", rt.unary("-", rt.swizzle(s, "r")), _u_density, 1, "float"), _u_absorption, 1, "float"), dt, 1, "float"), width=1), 1, "float")
                col[:] = rt.binary("+", col, rt.binary("*", rt.binary("*", rt.binary("*", trans, a, 1, "float"), rt.swizzle(s, "rgb"), 3, "float"), _u_emission, 3, "float"), 3, "float")
                trans = rt.binary("*", trans, rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float")
                if rt.binary("<", trans, rt.f(0.01)):
                    break
                t = rt.binary("+", t, dt, 1, "float")
        outc = rt.binary("+", col, rt.binary("*", _u_bgColor, trans, 3, "float"), 3, "float")
        g.fragColor[:] = rt.construct(4, outc, rt.binary("+", rt.binary("-", rt.f(1.0), trans, 1, "float"), rt.binary("*", _u_bgAlpha, trans, 1, "float"), 1, "float"))
        g.geoOut[:] = rt.construct(4, rt.f(0.5), rt.f(0.5), rt.f(0.5), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.geoOut
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor', 'geoOut')
