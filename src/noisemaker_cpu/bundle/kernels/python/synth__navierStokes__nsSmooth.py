def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_smoothing = U.get("smoothing", 0)
    _u_canvasTex = T["canvasTex"]
    g.fragColor = rt.construct(4, 0.0)
    def fetchTex__ivec2_ivec2_ivec2(idx, minIdx, maxIdx):
        idx = rt.copy(idx, "int")
        minIdx = rt.copy(minIdx, "int")
        maxIdx = rt.copy(maxIdx, "int")
        return rt.texel_fetch(_u_canvasTex, rt.component_wise("clamp", idx, minIdx, maxIdx, width=2), rt.i(0))
    def quad3v__vec4_vec4_vec4_float(p0, p1, p2, t):
        p0 = rt.copy(p0, "float")
        p1 = rt.copy(p1, "float")
        p2 = rt.copy(p2, "float")
        t2 = rt.binary("*", t, t, 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", p0, rt.f(0.5), 4, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 4, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 4, "float"), rt.binary("*", rt.binary("*", p1, rt.f(0.5), 4, "float"), rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t2, 1, "float"), rt.binary("*", rt.f(2.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), 4, "float"), 4, "float"), rt.binary("*", rt.binary("*", p2, rt.f(0.5), 4, "float"), t2, 4, "float"), 4, "float")
    def bicubic4v__vec4_vec4_vec4_vec4_float(p0, p1, p2, p3, t):
        p0 = rt.copy(p0, "float")
        p1 = rt.copy(p1, "float")
        p2 = rt.copy(p2, "float")
        p3 = rt.copy(p3, "float")
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        b0 = rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), t, 1, "float"), 1, "float"), rt.f(6.0), 1, "float")
        b1 = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(3.0), t3, 1, "float"), rt.binary("*", rt.f(6.0), t2, 1, "float"), 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        b2 = rt.binary("/", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(3.0)), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), rt.binary("*", rt.f(3.0), t, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), rt.f(6.0), 1, "float")
        b3 = rt.binary("/", t3, rt.f(6.0), 1, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", p0, b0, 4, "float"), rt.binary("*", p1, b1, 4, "float"), 4, "float"), rt.binary("*", p2, b2, 4, "float"), 4, "float"), rt.binary("*", p3, b3, 4, "float"), 4, "float")
    def catmull3v__vec4_vec4_vec4_float(p0, p1, p2, t):
        p0 = rt.copy(p0, "float")
        p1 = rt.copy(p1, "float")
        p2 = rt.copy(p2, "float")
        t2 = rt.binary("*", t, t, 1, "float")
        t3 = rt.binary("*", t2, t, 1, "float")
        m = rt.binary("*", rt.f(0.5), rt.binary("-", p2, p0, 4, "float"), 4, "float")
        return rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), rt.f(1.0), 1, "float"), p1, 4, "float"), rt.binary("*", rt.binary("+", rt.binary("-", t3, rt.binary("*", rt.f(2.0), t2, 1, "float"), 1, "float"), t, 1, "float"), m, 4, "float"), 4, "float"), rt.binary("*", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(2.0)), t3, 1, "float"), rt.binary("*", rt.f(3.0), t2, 1, "float"), 1, "float"), p2, 4, "float"), 4, "float"), rt.binary("*", rt.binary("-", t3, t2, 1, "float"), m, 4, "float"), 4, "float")
    def catmull4v__vec4_vec4_vec4_vec4_float(p0, p1, p2, p3, t):
        p0 = rt.copy(p0, "float")
        p1 = rt.copy(p1, "float")
        p2 = rt.copy(p2, "float")
        p3 = rt.copy(p3, "float")
        return rt.binary("+", p1, rt.binary("*", rt.binary("*", rt.f(0.5), t, 1, "float"), rt.binary("+", rt.binary("-", p2, p0, 4, "float"), rt.binary("*", t, rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("*", rt.f(2.0), p0, 4, "float"), rt.binary("*", rt.f(5.0), p1, 4, "float"), 4, "float"), rt.binary("*", rt.f(4.0), p2, 4, "float"), 4, "float"), p3, 4, "float"), rt.binary("*", t, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(3.0), rt.binary("-", p1, p2, 4, "float"), 4, "float"), p3, 4, "float"), p0, 4, "float"), 4, "float"), 4, "float"), 4, "float"), 4, "float"), 4, "float"), 4, "float")
    def main__void():
        texSize = rt.texture_size(_u_canvasTex)
        minIdx = rt.construct(2, rt.i(0), base="int")
        maxIdx = rt.binary("-", texSize, rt.construct(2, rt.i(1), base="int"), 2, "int")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texelPos = rt.binary("-", rt.binary("*", uv, rt.construct(2, texSize), 2, "float"), rt.construct(2, rt.f(0.5)), 2, "float")
        baseI = rt.construct(2, rt.component_wise("floor", texelPos, width=2), base="int")
        f = rt.component_wise("fract", texelPos, width=2)
        sampled = rt.construct(4, 0.0)
        idx = rt.construct(2, 0.0, base="int")
        v00 = rt.construct(4, 0.0)
        v10 = rt.construct(4, 0.0)
        v01 = rt.construct(4, 0.0)
        v11 = rt.construct(4, 0.0)
        w = rt.construct(2, 0.0)
        v0 = rt.construct(4, 0.0)
        v1 = rt.construct(4, 0.0)
        p = rt.construct(4, 0.0)
        r0 = rt.construct(4, 0.0)
        r1 = rt.construct(4, 0.0)
        r2 = rt.construct(4, 0.0)
        r3 = rt.construct(4, 0.0)
        if rt.binary("==", _u_smoothing, rt.i(0)):
            idx = rt.component_wise("clamp", rt.construct(2, rt.component_wise("floor", rt.binary("+", texelPos, rt.f(0.5), 2, "float"), width=2), base="int"), minIdx, maxIdx, width=2)
            sampled[:] = rt.texel_fetch(_u_canvasTex, idx, rt.i(0))
        else:
            if rt.binary("==", _u_smoothing, rt.i(2)):
                v00 = fetchTex__ivec2_ivec2_ivec2(baseI, minIdx, maxIdx)
                v10 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), minIdx, maxIdx)
                v01 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
                v11 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
                w = rt.component_wise("smoothstep", rt.construct(2, rt.f(0.0)), rt.construct(2, rt.f(1.0)), f, width=2)
                v0 = rt.component_wise("mix", v00, v10, rt.swizzle(w, "x"), width=4)
                v1 = rt.component_wise("mix", v01, v11, rt.swizzle(w, "x"), width=4)
                sampled[:] = rt.component_wise("mix", v0, v1, rt.swizzle(w, "y"), width=4)
            else:
                if rt.binary("==", _u_smoothing, rt.i(3)):
                    p = rt.new_array(rt.i(9), 4)
                    j = rt.i(0)
                    _for0_first = True
                    for _for0 in range(1048576):
                        if not _for0_first:
                            j = rt.binary("+", j, rt.i(1), 1, "int")
                        _for0_first = False
                        if not (rt.binary("<", j, rt.i(3))):
                            break
                        i = rt.i(0)
                        _for1_first = True
                        for _for1 in range(1048576):
                            if not _for1_first:
                                i = rt.binary("+", i, rt.i(1), 1, "int")
                            _for1_first = False
                            if not (rt.binary("<", i, rt.i(3))):
                                break
                            p[int(rt.binary("+", rt.binary("*", j, rt.i(3), 1, "int"), i, 1, "int"))] = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.binary("-", i, rt.i(1), 1, "int"), rt.binary("-", j, rt.i(1), 1, "int"), base="int"), 2, "int"), minIdx, maxIdx)
                    r0 = catmull3v__vec4_vec4_vec4_float(p[int(rt.i(0))], p[int(rt.i(1))], p[int(rt.i(2))], rt.swizzle(f, "x"))
                    r1 = catmull3v__vec4_vec4_vec4_float(p[int(rt.i(3))], p[int(rt.i(4))], p[int(rt.i(5))], rt.swizzle(f, "x"))
                    r2 = catmull3v__vec4_vec4_vec4_float(p[int(rt.i(6))], p[int(rt.i(7))], p[int(rt.i(8))], rt.swizzle(f, "x"))
                    sampled[:] = catmull3v__vec4_vec4_vec4_float(r0, r1, r2, rt.swizzle(f, "y"))
                else:
                    if rt.binary("==", _u_smoothing, rt.i(4)):
                        p = rt.new_array(rt.i(16), 4)
                        j = rt.i(0)
                        _for2_first = True
                        for _for2 in range(1048576):
                            if not _for2_first:
                                j = rt.binary("+", j, rt.i(1), 1, "int")
                            _for2_first = False
                            if not (rt.binary("<", j, rt.i(4))):
                                break
                            i = rt.i(0)
                            _for3_first = True
                            for _for3 in range(1048576):
                                if not _for3_first:
                                    i = rt.binary("+", i, rt.i(1), 1, "int")
                                _for3_first = False
                                if not (rt.binary("<", i, rt.i(4))):
                                    break
                                p[int(rt.binary("+", rt.binary("*", j, rt.i(4), 1, "int"), i, 1, "int"))] = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.binary("-", i, rt.i(1), 1, "int"), rt.binary("-", j, rt.i(1), 1, "int"), base="int"), 2, "int"), minIdx, maxIdx)
                        r0 = catmull4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(0))], p[int(rt.i(1))], p[int(rt.i(2))], p[int(rt.i(3))], rt.swizzle(f, "x"))
                        r1 = catmull4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(4))], p[int(rt.i(5))], p[int(rt.i(6))], p[int(rt.i(7))], rt.swizzle(f, "x"))
                        r2 = catmull4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(8))], p[int(rt.i(9))], p[int(rt.i(10))], p[int(rt.i(11))], rt.swizzle(f, "x"))
                        r3 = catmull4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(12))], p[int(rt.i(13))], p[int(rt.i(14))], p[int(rt.i(15))], rt.swizzle(f, "x"))
                        sampled[:] = catmull4v__vec4_vec4_vec4_vec4_float(r0, r1, r2, r3, rt.swizzle(f, "y"))
                    else:
                        if rt.binary("==", _u_smoothing, rt.i(5)):
                            p = rt.new_array(rt.i(9), 4)
                            j = rt.i(0)
                            _for4_first = True
                            for _for4 in range(1048576):
                                if not _for4_first:
                                    j = rt.binary("+", j, rt.i(1), 1, "int")
                                _for4_first = False
                                if not (rt.binary("<", j, rt.i(3))):
                                    break
                                i = rt.i(0)
                                _for5_first = True
                                for _for5 in range(1048576):
                                    if not _for5_first:
                                        i = rt.binary("+", i, rt.i(1), 1, "int")
                                    _for5_first = False
                                    if not (rt.binary("<", i, rt.i(3))):
                                        break
                                    p[int(rt.binary("+", rt.binary("*", j, rt.i(3), 1, "int"), i, 1, "int"))] = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.binary("-", i, rt.i(1), 1, "int"), rt.binary("-", j, rt.i(1), 1, "int"), base="int"), 2, "int"), minIdx, maxIdx)
                            r0 = quad3v__vec4_vec4_vec4_float(p[int(rt.i(0))], p[int(rt.i(1))], p[int(rt.i(2))], rt.swizzle(f, "x"))
                            r1 = quad3v__vec4_vec4_vec4_float(p[int(rt.i(3))], p[int(rt.i(4))], p[int(rt.i(5))], rt.swizzle(f, "x"))
                            r2 = quad3v__vec4_vec4_vec4_float(p[int(rt.i(6))], p[int(rt.i(7))], p[int(rt.i(8))], rt.swizzle(f, "x"))
                            sampled[:] = quad3v__vec4_vec4_vec4_float(r0, r1, r2, rt.swizzle(f, "y"))
                        else:
                            if rt.binary("==", _u_smoothing, rt.i(6)):
                                p = rt.new_array(rt.i(16), 4)
                                j = rt.i(0)
                                _for6_first = True
                                for _for6 in range(1048576):
                                    if not _for6_first:
                                        j = rt.binary("+", j, rt.i(1), 1, "int")
                                    _for6_first = False
                                    if not (rt.binary("<", j, rt.i(4))):
                                        break
                                    i = rt.i(0)
                                    _for7_first = True
                                    for _for7 in range(1048576):
                                        if not _for7_first:
                                            i = rt.binary("+", i, rt.i(1), 1, "int")
                                        _for7_first = False
                                        if not (rt.binary("<", i, rt.i(4))):
                                            break
                                        p[int(rt.binary("+", rt.binary("*", j, rt.i(4), 1, "int"), i, 1, "int"))] = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.binary("-", i, rt.i(1), 1, "int"), rt.binary("-", j, rt.i(1), 1, "int"), base="int"), 2, "int"), minIdx, maxIdx)
                                r0 = bicubic4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(0))], p[int(rt.i(1))], p[int(rt.i(2))], p[int(rt.i(3))], rt.swizzle(f, "x"))
                                r1 = bicubic4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(4))], p[int(rt.i(5))], p[int(rt.i(6))], p[int(rt.i(7))], rt.swizzle(f, "x"))
                                r2 = bicubic4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(8))], p[int(rt.i(9))], p[int(rt.i(10))], p[int(rt.i(11))], rt.swizzle(f, "x"))
                                r3 = bicubic4v__vec4_vec4_vec4_vec4_float(p[int(rt.i(12))], p[int(rt.i(13))], p[int(rt.i(14))], p[int(rt.i(15))], rt.swizzle(f, "x"))
                                sampled[:] = bicubic4v__vec4_vec4_vec4_vec4_float(r0, r1, r2, r3, rt.swizzle(f, "y"))
                            else:
                                v00 = fetchTex__ivec2_ivec2_ivec2(baseI, minIdx, maxIdx)
                                v10 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), minIdx, maxIdx)
                                v01 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
                                v11 = fetchTex__ivec2_ivec2_ivec2(rt.binary("+", baseI, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), minIdx, maxIdx)
                                v0 = rt.component_wise("mix", v00, v10, rt.swizzle(f, "x"), width=4)
                                v1 = rt.component_wise("mix", v01, v11, rt.swizzle(f, "x"), width=4)
                                sampled[:] = rt.component_wise("mix", v0, v1, rt.swizzle(f, "y"), width=4)
        g.fragColor[:] = sampled
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
