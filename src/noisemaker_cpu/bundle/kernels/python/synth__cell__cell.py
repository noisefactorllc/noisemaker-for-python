def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U["time"]
    _u_seed = U["seed"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_renderScale = U["renderScale"]
    _u_metric = U["metric"]
    _u_scale = U["scale"]
    _u_cellScale = U["cellScale"]
    _u_cellSmooth = U["cellSmooth"]
    _u_variation = U["variation"]
    _u_speed = U["speed"]
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def pcg__uvec3(v):
        v = rt.copy(v)
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
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
    def polarShape__vec2_int(st, sides):
        st = rt.copy(st)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float")
    def shape__vec2_vec2_int_float(st, offset, type, scale):
        st = rt.copy(st)
        offset = rt.copy(offset)
        st = rt.binary("+", st, offset, 2, "float")
        d = rt.f(1.0)
        if rt.binary("==", type, rt.i(0)):
            d = rt.length(rt.binary("*", st, rt.f(1.2), 2, "float"))
        else:
            if rt.binary("==", type, rt.i(2)):
                d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(6))
            else:
                if rt.binary("==", type, rt.i(3)):
                    d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(8))
                else:
                    if rt.binary("==", type, rt.i(4)):
                        d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(4))
                    else:
                        if rt.binary("==", type, rt.i(6)):
                            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.f(0.05), 1, "float"))
                            d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(3))
        return rt.binary("*", d, scale, 1, "float")
    def smin__float_float_float(a, b, k):
        if rt.binary("==", k, rt.f(0.0)):
            return rt.component_wise("min", a, b, width=1)
        h = rt.binary("/", rt.component_wise("max", rt.binary("-", k, rt.component_wise("abs", rt.binary("-", a, b, 1, "float"), width=1), 1, "float"), rt.f(0.0), width=1), k, 1, "float")
        return rt.binary("-", rt.component_wise("min", a, b, width=1), rt.binary("*", rt.binary("*", rt.binary("*", h, h, 1, "float"), k, 1, "float"), rt.binary("/", rt.f(1.0), rt.f(4.0), 1, "float"), 1, "float"), 1, "float")
    def cells__vec2_float_float_int(st, freq, cellSize, sides):
        st = rt.copy(st)
        st = rt.binary("-", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.binary("*", st, freq, 2, "float")
        st = rt.binary("+", st, rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.binary("+", st, rt.swizzle(prng__vec3(rt.construct(3, rt.construct(1, _u_seed))), "xy"), 2, "float")
        i = rt.component_wise("floor", st, width=2)
        f = rt.component_wise("fract", st, width=2)
        d = rt.f(1.0)
        y = rt.unary("-", rt.i(2))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, rt.i(2))):
                break
            x = rt.unary("-", rt.i(2))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, rt.i(2))):
                    break
                n = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                wrap = rt.binary("+", i, n, 2, "float")
                point = rt.swizzle(prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), "xy")
                r1 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, rt.construct(1, _u_seed), wrap)), rt.f(0.5), 3, "float"), rt.f(0.25), 3, "float")
                r2 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
                spd = rt.component_wise("floor", _u_speed, width=1)
                point = rt.binary("+", point, rt.construct(2, rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "x"), 1, "float"), width=1), rt.swizzle(r1, "x"), 1, "float"), rt.binary("*", rt.component_wise("cos", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "y"), 1, "float"), width=1), rt.swizzle(r1, "y"), 1, "float")), 2, "float")
                diff = rt.binary("-", rt.binary("+", n, point, 2, "float"), f, 2, "float")
                dist = shape__vec2_vec2_int_float(rt.construct(2, rt.swizzle(diff, "x"), rt.unary("-", rt.swizzle(diff, "y"))), rt.construct(2, rt.f(0.0)), sides, cellSize)
                if rt.binary("==", _u_metric, rt.i(1)):
                    dist = rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "x"), rt.swizzle(point, "x"), 1, "float"), rt.swizzle(f, "x"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "y"), rt.swizzle(point, "y"), 1, "float"), rt.swizzle(f, "y"), 1, "float"), width=1), 1, "float")
                    dist = rt.binary("*", dist, cellSize, 1, "float")
                dist = rt.binary("+", dist, rt.binary("*", rt.swizzle(r1, "z"), rt.binary("*", _u_variation, rt.f(0.01), 1, "float"), 1, "float"), 1, "float")
                d = smin__float_float_float(d, dist, rt.binary("*", _u_cellSmooth, rt.f(0.01), 1, "float"))
        return d
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, rt.swizzle(_u_fullResolution, "y"), 2, "float")
        freq = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(1.0))
        cellSize = map__float_float_float_float_float(_u_cellScale, rt.f(1.0), rt.f(100.0), rt.f(3.0), rt.f(0.75))
        d = cells__vec2_float_float_int(st, freq, cellSize, _u_metric)
        color = rt.assign_swizzle(color, "rgb", rt.construct(3, d))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
