def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_data = U.get("data", rt.construct(4, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_zone0_tex = T["zone0_tex"]
    _u_zone1_tex = T["zone1_tex"]
    _u_zone2_tex = T["zone2_tex"]
    _u_zone3_tex = T["zone3_tex"]
    _u_zone4_tex = T["zone4_tex"]
    _u_zone5_tex = T["zone5_tex"]
    _u_zone6_tex = T["zone6_tex"]
    _u_zone7_tex = T["zone7_tex"]
    g.fragColor = rt.construct(4, 0.0)
    def sampleZone__int_vec2(z, uv):
        uv = rt.copy(uv, "float")
        if rt.binary("==", z, rt.i(0)):
            return rt.texture(_u_zone0_tex, uv)
        if rt.binary("==", z, rt.i(1)):
            return rt.texture(_u_zone1_tex, uv)
        if rt.binary("==", z, rt.i(2)):
            return rt.texture(_u_zone2_tex, uv)
        if rt.binary("==", z, rt.i(3)):
            return rt.texture(_u_zone3_tex, uv)
        if rt.binary("==", z, rt.i(4)):
            return rt.texture(_u_zone4_tex, uv)
        if rt.binary("==", z, rt.i(5)):
            return rt.texture(_u_zone5_tex, uv)
        if rt.binary("==", z, rt.i(6)):
            return rt.texture(_u_zone6_tex, uv)
        return rt.texture(_u_zone7_tex, uv)
    def testEdge__struct1_vec2_vec2_vec2_bool(t, a, b, q, needDist):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        q = rt.copy(q, "float")
        e = rt.binary("-", b, a, 2, "float")
        w = rt.binary("-", q, a, 2, "float")
        c = rt.construct(3, rt.binary(">=", rt.swizzle(q, "y"), rt.swizzle(a, "y")), rt.binary("<", rt.swizzle(q, "y"), rt.swizzle(b, "y")), rt.binary(">", rt.binary("*", rt.swizzle(e, "x"), rt.swizzle(w, "y"), 1, "float"), rt.binary("*", rt.swizzle(e, "y"), rt.swizzle(w, "x"), 1, "float")))
        if (bool(rt.component_wise("all", c, width=3)) or bool((not (rt.component_wise("any", c, width=3))))):
            t[0] = (not (t[0]))
        s = rt.f(0.0)
        r = rt.construct(2, 0.0)
        if needDist:
            s = rt.component_wise("clamp", rt.binary("/", rt.dot(w, e), rt.component_wise("max", rt.dot(e, e), rt.f(1e-06), width=1), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
            r = rt.binary("-", w, rt.binary("*", e, s, 2, "float"), 2, "float")
            t[1] = rt.component_wise("min", t[1], rt.dot(r, r), width=1)
        return t
    def walkZone__int_int_vec2_bool(base, n, q, needDist):
        q = rt.copy(q, "float")
        t = [False, rt.f(1e+30)]
        last = rt.binary("-", n, rt.i(1), 1, "int")
        lastPack = _u_data[int(rt.binary("+", base, rt.binary("/", last, rt.i(2), 1, "int"), 1, "int"))]
        prev = rt.binary("*", (rt.swizzle(lastPack, "xy") if rt.binary("==", rt.binary("%", last, rt.i(2), 1, "int"), rt.i(0)) else rt.swizzle(lastPack, "zw")), _u_fullResolution, 2, "float")
        pairs = rt.binary("/", rt.binary("+", n, rt.i(1), 1, "int"), rt.i(2), 1, "int")
        pair = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                pair = rt.binary("+", pair, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", pair, rt.i(32))):
                break
            if rt.binary(">=", pair, pairs):
                break
            pack = _u_data[int(rt.binary("+", base, pair, 1, "int"))]
            v0 = rt.binary("*", rt.swizzle(pack, "xy"), _u_fullResolution, 2, "float")
            t = testEdge__struct1_vec2_vec2_vec2_bool(t, v0, prev, q, needDist)
            prev[:] = v0
            v1 = rt.construct(2, 0.0)
            if rt.binary("<", rt.binary("+", rt.binary("*", pair, rt.i(2), 1, "int"), rt.i(1), 1, "int"), n):
                v1 = rt.binary("*", rt.swizzle(pack, "zw"), _u_fullResolution, 2, "float")
                t = testEdge__struct1_vec2_vec2_vec2_bool(t, v1, prev, q, needDist)
                prev[:] = v1
        return t
    def main__void():
        globalPx = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        q = rt.construct(2, rt.swizzle(globalPx, "x"), rt.binary("-", rt.swizzle(_u_fullResolution, "y"), rt.swizzle(globalPx, "y"), 1, "float"))
        p = rt.binary("/", q, _u_fullResolution, 2, "float")
        sampleUv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.swizzle(_u_data[int(rt.i(266))], "xy"), 2, "float")
        header = _u_data[int(rt.i(0))]
        controls = _u_data[int(rt.i(1))]
        activeCount = rt.component_wise("min", rt.construct(1, rt.swizzle(controls, "x"), base="int"), rt.i(8), width=1)
        featherPx = rt.binary("*", rt.binary("*", rt.component_wise("max", rt.swizzle(controls, "y"), rt.f(0.0), width=1), rt.f(0.05), 1, "float"), rt.component_wise("min", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 1, "float")
        needDist = rt.binary(">", featherPx, rt.f(0.0))
        dilate = rt.binary("/", rt.construct(2, featherPx), _u_fullResolution, 2, "float")
        result = rt.construct(4, rt.f(0.0))
        k = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                k = rt.binary("+", k, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", k, rt.i(8))):
                break
            z = rt.binary("-", rt.binary("-", activeCount, rt.i(1), 1, "int"), k, 1, "int")
            if rt.binary("<", z, rt.i(0)):
                break
            zoneMeta = _u_data[int(rt.binary("+", rt.i(2), z, 1, "int"))]
            n = rt.component_wise("min", rt.construct(1, rt.swizzle(zoneMeta, "x"), base="int"), rt.binary("*", rt.i(32), rt.i(2), 1, "int"), width=1)
            if (bool(rt.binary("<", n, rt.i(3))) or bool(rt.binary("<", rt.swizzle(zoneMeta, "y"), rt.f(0.5)))):
                continue
            bounds = _u_data[int(rt.binary("+", rt.i(267), z, 1, "int"))]
            if (bool(rt.component_wise("any", rt.component_wise("lessThan", p, rt.binary("-", rt.swizzle(bounds, "xy"), dilate, 2, "float"), width=2), width=2)) or bool(rt.component_wise("any", rt.component_wise("greaterThan", p, rt.binary("+", rt.swizzle(bounds, "zw"), dilate, 2, "float"), width=2), width=2))):
                continue
            base = rt.binary("+", rt.i(10), rt.binary("*", z, rt.i(32), 1, "int"), 1, "int")
            t = [False, rt.f(0.0)]
            if needDist:
                t = walkZone__int_int_vec2_bool(base, n, q, True)
            else:
                t = walkZone__int_int_vec2_bool(base, n, q, False)
            coverage = rt.f(1.0)
            if (not (t[0])):
                if (not (needDist)):
                    continue
                coverage = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), featherPx, rt.component_wise("sqrt", t[1], width=1), width=1), 1, "float")
                if rt.binary("<=", coverage, rt.f(0.0)):
                    continue
            src = rt.binary("*", sampleZone__int_vec2(z, sampleUv), rt.binary("*", coverage, rt.swizzle(zoneMeta, "w"), 1, "float"), 4, "float")
            result[:] = rt.binary("+", result, rt.binary("*", src, rt.binary("-", rt.f(1.0), rt.swizzle(result, "a"), 1, "float"), 4, "float"), 4, "float")
            if rt.binary(">=", rt.swizzle(result, "a"), rt.f(0.999)):
                break
        result[:] = rt.binary("+", result, rt.binary("*", rt.construct(4, rt.binary("*", rt.swizzle(header, "xyz"), rt.swizzle(header, "w"), 3, "float"), rt.swizzle(header, "w")), rt.binary("-", rt.f(1.0), rt.swizzle(result, "a"), 1, "float"), 4, "float"), 4, "float")
        g.fragColor[:] = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
