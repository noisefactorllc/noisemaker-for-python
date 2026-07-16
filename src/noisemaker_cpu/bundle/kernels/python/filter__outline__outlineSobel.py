def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_valueTexture = T["valueTexture"]
    _u_sobelMetric = U.get("sobelMetric", rt.f(0.0))
    _u_thickness = U.get("thickness", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def wrapCoord__int_int(value, size):
        if rt.binary("<=", size, rt.i(0)):
            return rt.i(0)
        wrapped = rt.binary("%", value, size, 1, "int")
        if rt.binary("<", wrapped, rt.i(0)):
            wrapped = rt.binary("+", wrapped, size, 1, "int")
        return wrapped
    def distanceMetric__float_float_int(gx, gy, metric):
        abs_gx = rt.component_wise("abs", gx, width=1)
        abs_gy = rt.component_wise("abs", gy, width=1)
        cross = rt.f(0.0)
        if rt.binary("==", metric, rt.i(2)):
            return rt.binary("+", abs_gx, abs_gy, 1, "float")
        else:
            if rt.binary("==", metric, rt.i(3)):
                return rt.component_wise("max", abs_gx, abs_gy, width=1)
            else:
                if rt.binary("==", metric, rt.i(4)):
                    cross = rt.binary("/", rt.binary("+", abs_gx, abs_gy, 1, "float"), rt.f(1.414), 1, "float")
                    return rt.component_wise("max", cross, rt.component_wise("max", abs_gx, abs_gy, width=1), width=1)
                else:
                    return rt.component_wise("sqrt", rt.binary("+", rt.binary("*", gx, gx, 1, "float"), rt.binary("*", gy, gy, 1, "float"), 1, "float"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        dimensions = rt.texture_size(_u_valueTexture)
        if (bool(rt.binary("==", rt.swizzle(dimensions, "x"), rt.i(0))) or bool(rt.binary("==", rt.swizzle(dimensions, "y"), rt.i(0)))):
            g.fragColor = rt.construct(4, rt.f(0.0))
            return
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        metric = rt.construct(1, _u_sobelMetric, base="int")
        offset = rt.component_wise("max", rt.i(1), rt.construct(1, rt.binary("*", _u_thickness, _u_renderScale, 1, "float"), base="int"), width=1)
        samples = rt.new_array(rt.i(9), 1)
        idx = rt.i(0)
        ky = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                ky = rt.binary("+", ky, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", ky, rt.i(1))):
                break
            kx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    kx = rt.binary("+", kx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", kx, rt.i(1))):
                    break
                sampleX = wrapCoord__int_int(rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", kx, offset, 1, "int"), 1, "int"), rt.swizzle(dimensions, "x"))
                sampleY = wrapCoord__int_int(rt.binary("+", rt.swizzle(coord, "y"), rt.binary("*", ky, offset, 1, "int"), 1, "int"), rt.swizzle(dimensions, "y"))
                samples[int(idx)] = rt.swizzle(rt.texel_fetch(_u_valueTexture, rt.construct(2, sampleX, sampleY, base="int"), rt.i(0)), "r")
                idx = rt.binary("+", idx, rt.i(1), 1, "int")
        gx = rt.binary("+", rt.binary("-", rt.binary("+", rt.binary("-", rt.binary("+", rt.unary("-", samples[int(rt.i(0))]), samples[int(rt.i(2))], 1, "float"), rt.binary("*", rt.f(2.0), samples[int(rt.i(3))], 1, "float"), 1, "float"), rt.binary("*", rt.f(2.0), samples[int(rt.i(5))], 1, "float"), 1, "float"), samples[int(rt.i(6))], 1, "float"), samples[int(rt.i(8))], 1, "float")
        gy = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("-", rt.binary("-", rt.unary("-", samples[int(rt.i(0))]), rt.binary("*", rt.f(2.0), samples[int(rt.i(1))], 1, "float"), 1, "float"), samples[int(rt.i(2))], 1, "float"), samples[int(rt.i(6))], 1, "float"), rt.binary("*", rt.f(2.0), samples[int(rt.i(7))], 1, "float"), 1, "float"), samples[int(rt.i(8))], 1, "float")
        magnitude = distanceMetric__float_float_int(gx, gy, metric)
        normalized = rt.component_wise("clamp", rt.binary("*", magnitude, rt.f(4.0), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        g.fragColor = rt.construct(4, normalized, normalized, normalized, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
