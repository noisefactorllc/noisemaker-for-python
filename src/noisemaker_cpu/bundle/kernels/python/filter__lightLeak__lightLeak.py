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
    _u_fullResolution = U["fullResolution"]
    _u_alpha = U["alpha"]
    _u_color = U["color"]
    _u_speed = U["speed"]
    _u_seed = U["seed"]
    _u_time = U["time"]
    g.TAU = rt.f(6.283185307179586)
    g.POINT_COUNT = rt.i(6)
    def pcg__uvec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "float"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "float"))
        return v
    def hash31__vec3(p):
        p = rt.copy(p)
        v = rt.construct(3, rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), base="uint")
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__uvec3(v), "x")), rt.construct(1, rt.i(4294967295)), 1, "float")
    def hash33__vec3(p):
        p = rt.copy(p)
        v = rt.construct(3, rt.construct(1, (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), rt.construct(1, (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")), base="uint"), base="uint")
        h = pcg__uvec3(v)
        return rt.construct(3, rt.binary("/", rt.construct(1, rt.swizzle(h, "x")), rt.construct(1, rt.i(4294967295)), 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(h, "y")), rt.construct(1, rt.i(4294967295)), 1, "float"), rt.binary("/", rt.construct(1, rt.swizzle(h, "z")), rt.construct(1, rt.i(4294967295)), 1, "float"))
    def luminance__vec3(c):
        c = rt.copy(c)
        return rt.dot(c, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def voronoiCell__vec2_float_float_vec3_float(uv, seed_f, t, cell_color, cell_dist):
        uv = rt.copy(uv)
        cell_color = rt.copy(cell_color)
        best_dist = rt.f(1000000000.0)
        best_index = rt.i(0)
        drift = rt.f(0.05)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, g.POINT_COUNT)):
                break
            s = rt.construct(3, seed_f, rt.binary("*", rt.construct(1, i), rt.f(7.31), 1, "float"), rt.f(0.0))
            base = rt.swizzle(hash33__vec3(s), "xy")
            osc = rt.binary("*", rt.construct(2, rt.component_wise("sin", rt.binary("+", rt.binary("*", t, rt.f(0.7), 1, "float"), rt.binary("*", rt.construct(1, i), rt.f(1.618), 1, "float"), 1, "float"), width=1), rt.component_wise("cos", rt.binary("+", rt.binary("*", t, rt.f(0.5), 1, "float"), rt.binary("*", rt.construct(1, i), rt.f(2.236), 1, "float"), 1, "float"), width=1)), drift, 2, "float")
            pt = rt.component_wise("fract", rt.binary("+", base, osc, 2, "float"), width=2)
            delta = rt.component_wise("abs", rt.binary("-", uv, pt, 2, "float"), width=2)
            wd = rt.component_wise("min", delta, rt.binary("-", rt.f(1.0), delta, 2, "float"), width=2)
            dist = rt.dot(wd, wd)
            if rt.binary("<", dist, best_dist):
                best_dist = dist
                best_index = i
        s = rt.construct(3, rt.binary("+", seed_f, rt.f(100.0), 1, "float"), rt.binary("*", rt.construct(1, best_index), rt.f(13.37), 1, "float"), rt.f(5.0))
        cell_color = rt.component_wise("mix", hash33__vec3(s), _u_color, rt.f(0.6), width=3)
        cell_dist = best_dist
    def centerMask__vec2(uv):
        uv = rt.copy(uv)
        centered = rt.component_wise("abs", rt.binary("-", uv, rt.f(0.5), 2, "float"), width=2)
        dist = rt.component_wise("max", rt.swizzle(centered, "x"), rt.swizzle(centered, "y"), width=1)
        return rt.component_wise("clamp", rt.binary("*", dist, rt.f(2.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        coords = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        tileDims = rt.texture_size(_u_inputTex)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, tileDims))
        uv = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        base = rt.texel_fetch(_u_inputTex, coords, rt.i(0))
        blend_alpha = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        if rt.binary("<=", blend_alpha, rt.f(0.0)):
            g.fragColor = base
            return
        seed_f = rt.construct(1, _u_seed)
        t = rt.binary("*", _u_time, _u_speed, 1, "float")
        base_cell = rt.construct(3, 0.0)
        base_dist = rt.f(0.0)
        voronoiCell__vec2_float_float_vec3_float(uv, seed_f, t, base_cell, base_dist)
        luma = luminance__vec3(base_cell)
        angle = rt.binary("+", rt.binary("*", luma, g.TAU, 1, "float"), rt.binary("*", rt.binary("*", t, _u_speed, 1, "float"), rt.f(0.5), 1, "float"), 1, "float")
        warp = rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), rt.f(0.25), 2, "float")
        warped_uv = rt.component_wise("fract", rt.binary("+", uv, warp, 2, "float"), width=2)
        warp_cell = rt.construct(3, 0.0)
        warp_dist = rt.f(0.0)
        voronoiCell__vec2_float_float_vec3_float(warped_uv, seed_f, t, warp_cell, warp_dist)
        glow = rt.component_wise("exp", rt.binary("*", rt.unary("-", warp_dist), rt.f(12.0), 1, "float"), width=1)
        bloom_color = rt.component_wise("mix", warp_cell, rt.binary("*", warp_cell, rt.f(1.3), 3, "float"), glow, width=3)
        leak = rt.component_wise("clamp", rt.component_wise("mix", rt.component_wise("sqrt", rt.component_wise("clamp", warp_cell, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3), width=3), bloom_color, rt.f(0.55), width=3), rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3)
        screened = rt.binary("-", rt.construct(3, rt.f(1.0)), rt.binary("*", rt.binary("-", rt.construct(3, rt.f(1.0)), rt.swizzle(base, "rgb"), 3, "float"), rt.binary("-", rt.construct(3, rt.f(1.0)), leak, 3, "float"), 3, "float"), 3, "float")
        mask = rt.component_wise("pow", centerMask__vec2(uv), rt.f(4.0), width=1)
        masked = rt.component_wise("mix", rt.swizzle(base, "rgb"), screened, mask, width=3)
        soft_accum = rt.binary("*", masked, rt.f(4.0), 3, "float")
        soft_w = rt.f(4.0)
        nb0 = rt.component_wise("clamp", rt.binary("+", coords, rt.construct(2, rt.i(2), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", tileDims, rt.i(1), 2, "int"), width=2)
        nb1 = rt.component_wise("clamp", rt.binary("+", coords, rt.construct(2, rt.unary("-", rt.i(2)), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", tileDims, rt.i(1), 2, "int"), width=2)
        nb2 = rt.component_wise("clamp", rt.binary("+", coords, rt.construct(2, rt.i(0), rt.i(2), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", tileDims, rt.i(1), 2, "int"), width=2)
        nb3 = rt.component_wise("clamp", rt.binary("+", coords, rt.construct(2, rt.i(0), rt.unary("-", rt.i(2)), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", tileDims, rt.i(1), 2, "int"), width=2)
        soft_accum = rt.binary("+", soft_accum, rt.swizzle(rt.texel_fetch(_u_inputTex, nb0, rt.i(0)), "rgb"), 3, "float")
        soft_accum = rt.binary("+", soft_accum, rt.swizzle(rt.texel_fetch(_u_inputTex, nb1, rt.i(0)), "rgb"), 3, "float")
        soft_accum = rt.binary("+", soft_accum, rt.swizzle(rt.texel_fetch(_u_inputTex, nb2, rt.i(0)), "rgb"), 3, "float")
        soft_accum = rt.binary("+", soft_accum, rt.swizzle(rt.texel_fetch(_u_inputTex, nb3, rt.i(0)), "rgb"), 3, "float")
        soft_w = rt.binary("+", soft_w, rt.f(4.0), 1, "float")
        vaseline = rt.binary("/", soft_accum, soft_w, 3, "float")
        final_color = rt.component_wise("mix", rt.swizzle(base, "rgb"), rt.component_wise("mix", masked, vaseline, blend_alpha, width=3), blend_alpha, width=3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", final_color, rt.construct(3, rt.f(0.0)), rt.construct(3, rt.f(1.0)), width=3), rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
