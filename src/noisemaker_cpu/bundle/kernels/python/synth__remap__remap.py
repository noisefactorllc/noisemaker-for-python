def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_data = U["data"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_zone0_tex = T["zone0_tex"]
    _u_zone1_tex = T["zone1_tex"]
    _u_zone2_tex = T["zone2_tex"]
    _u_zone3_tex = T["zone3_tex"]
    _u_zone4_tex = T["zone4_tex"]
    _u_zone5_tex = T["zone5_tex"]
    _u_zone6_tex = T["zone6_tex"]
    _u_zone7_tex = T["zone7_tex"]
    def getZoneMeta__int(z):
        return _u_data[int(rt.binary("+", rt.i(2), z, 1, "int"))]
    def getZonePack__int_int(zoneIdx, pairIdx):
        return _u_data[int(rt.binary("+", rt.binary("+", rt.i(10), rt.binary("*", zoneIdx, rt.i(32), 1, "int"), 1, "int"), pairIdx, 1, "int"))]
    def getVert__int_int(zoneIdx, vertIdx):
        _packed = getZonePack__int_int(zoneIdx, rt.binary("/", vertIdx, rt.i(2), 1, "int"))
        return (rt.swizzle(_packed, "xy") if rt.binary("==", rt.binary("%", vertIdx, rt.i(2), 1, "int"), rt.i(0)) else rt.swizzle(_packed, "zw"))
    def getZoneCount__int(z):
        return rt.construct(1, rt.swizzle(getZoneMeta__int(z), "x"), base="int")
    def getZoneActive__int(z):
        return rt.construct(1, rt.binary("+", rt.swizzle(getZoneMeta__int(z), "y"), rt.f(0.5), 1, "float"), base="int")
    def getZoneAlpha__int(z):
        return rt.swizzle(getZoneMeta__int(z), "w")
    def sampleZone__int_vec2(z, uv):
        uv = rt.copy(uv)
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
    def pointInZone__vec2_int(p, zoneIdx):
        p = rt.copy(p)
        n = getZoneCount__int(zoneIdx)
        if rt.binary("<", n, rt.i(3)):
            return False
        inside = False
        prev = getVert__int_int(zoneIdx, rt.binary("-", n, rt.i(1), 1, "int"))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(64))):
                break
            if rt.binary(">=", i, n):
                break
            cur = getVert__int_int(zoneIdx, i)
            crosses = rt.binary("!=", rt.binary(">", rt.swizzle(cur, "y"), rt.swizzle(p, "y")), rt.binary(">", rt.swizzle(prev, "y"), rt.swizzle(p, "y")))
            if crosses:
                xCross = rt.binary("+", rt.binary("/", rt.binary("*", rt.binary("-", rt.swizzle(prev, "x"), rt.swizzle(cur, "x"), 1, "float"), rt.binary("-", rt.swizzle(p, "y"), rt.swizzle(cur, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.swizzle(prev, "y"), rt.swizzle(cur, "y"), 1, "float"), rt.f(1e-9), 1, "float"), 1, "float"), rt.swizzle(cur, "x"), 1, "float")
                if rt.binary("<", rt.swizzle(p, "x"), xCross):
                    inside = rt.unary("!", inside)
            prev = cur
        return inside
    def distToZoneEdge__vec2_int(p, zoneIdx):
        p = rt.copy(p)
        n = getZoneCount__int(zoneIdx)
        if rt.binary("<", n, rt.i(3)):
            return rt.f(1e9)
        d = rt.f(1e9)
        prev = getVert__int_int(zoneIdx, rt.binary("-", n, rt.i(1), 1, "int"))
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<", i, rt.i(64))):
                break
            if rt.binary(">=", i, n):
                break
            cur = getVert__int_int(zoneIdx, i)
            ab = rt.binary("-", cur, prev, 2, "float")
            len2 = rt.component_wise("max", rt.dot(ab, ab), rt.f(1e-9), width=1)
            t = rt.component_wise("clamp", rt.binary("/", rt.dot(rt.binary("-", p, prev, 2, "float"), ab), len2, 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
            closest = rt.binary("+", prev, rt.binary("*", t, ab, 2, "float"), 2, "float")
            d = rt.component_wise("min", d, rt.length(rt.binary("-", p, closest, 2, "float")), width=1)
            prev = cur
        return d
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        globalScreen = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), _u_fullResolution, 2, "float")
        p = rt.construct(2, rt.swizzle(globalScreen, "x"), rt.binary("-", rt.f(1.0), rt.swizzle(globalScreen, "y"), 1, "float"))
        sampleUv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        header = _u_data[int(rt.i(0))]
        controls = _u_data[int(rt.i(1))]
        bgColor = rt.swizzle(header, "xyz")
        bgAlpha = rt.swizzle(header, "w")
        activeCount = rt.component_wise("min", rt.construct(1, rt.swizzle(controls, "x"), base="int"), rt.i(8), width=1)
        smoothEdge = rt.swizzle(controls, "y")
        result = rt.construct(4, bgColor, bgAlpha)
        z = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                z = rt.binary("+", z, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<", z, rt.i(8))):
                break
            if rt.binary(">=", z, activeCount):
                break
            if rt.binary("==", getZoneActive__int(z), rt.i(0)):
                continue
            if rt.unary("!", pointInZone__vec2_int(p, z)):
                continue
            src = sampleZone__int_vec2(z, sampleUv)
            zAlpha = getZoneAlpha__int(z)
            edgeWidth = rt.binary("*", smoothEdge, rt.f(0.05), 1, "float")
            edge = (rt.component_wise("smoothstep", rt.f(0.0), edgeWidth, distToZoneEdge__vec2_int(p, z), width=1) if rt.binary(">", edgeWidth, rt.f(0.0)) else rt.f(1.0))
            a = rt.binary("*", zAlpha, edge, 1, "float")
            result = rt.construct(4, rt.component_wise("mix", rt.swizzle(result, "rgb"), rt.swizzle(src, "rgb"), a, width=3), rt.component_wise("max", rt.swizzle(result, "a"), rt.binary("*", rt.swizzle(src, "a"), a, 1, "float"), width=1))
        g.fragColor = result
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
