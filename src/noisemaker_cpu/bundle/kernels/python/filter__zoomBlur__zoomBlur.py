def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_strength = U["strength"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
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
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        tileDims = rt.construct(2, texSize)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), tileDims, 2)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        color = rt.construct(3, rt.f(0.0))
        total = rt.f(0.0)
        toCenter = rt.binary("-", globalUV, rt.f(0.5), 2)
        offset = rt.swizzle(prng__vec3(rt.construct(3, rt.f(12.9898), rt.f(78.233), rt.f(151.7182))), "x")
        t = rt.f(0.0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                t = rt.binary("+", t, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", t, rt.f(40.0))):
                break
            percent = rt.binary("/", rt.binary("+", t, offset, 1), rt.f(40.0), 1)
            weight = rt.binary("*", rt.f(4.0), rt.binary("-", percent, rt.binary("*", percent, percent, 1), 1), 1)
            tex = rt.texture(_u_inputTex, rt.binary("+", uv, rt.binary("*", rt.binary("*", toCenter, percent, 2), _u_strength, 2), 2))
            color = rt.binary("+", color, rt.binary("*", rt.swizzle(tex, "rgb"), weight, 3), 3)
            total = rt.binary("+", total, weight, 1)
        color = rt.binary("/", color, total, 3)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
