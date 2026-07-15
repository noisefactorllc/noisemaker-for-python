def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_accumTex = T["accumTex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_alpha = U["alpha"]
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        src = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        accum = rt.texture(_u_accumTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_accumTex)), 2, "float"))
        sum = rt.f(0.0)
        count = rt.f(0.0)
        gy = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                gy = rt.binary("+", gy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", gy, rt.i(32))):
                break
            gx = rt.i(0)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    gx = rt.binary("+", gx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<", gx, rt.i(32))):
                    break
                sampleUV = rt.binary("/", rt.binary("+", rt.construct(2, rt.construct(1, gx), rt.construct(1, gy)), rt.f(0.5), 2, "float"), rt.f(32.0), 2, "float")
                s = rt.texture(_u_accumTex, sampleUV)
                v = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(s, "r"), rt.swizzle(s, "g"), 1, "float"), rt.swizzle(s, "b"), 1, "float"), rt.f(3.0), 1, "float")
                sum = rt.binary("+", sum, v, 1, "float")
                count = rt.binary("+", count, rt.f(1.0), 1, "float")
        mean = rt.binary("/", sum, count, 1, "float")
        normalized = rt.construct(3, 0.0)
        if rt.binary(">", mean, rt.f(0.0)):
            normalized = rt.component_wise("clamp", rt.binary("/", rt.swizzle(accum, "rgb"), rt.binary("*", mean, rt.f(4.0), 1, "float"), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
        else:
            normalized = rt.swizzle(accum, "rgb")
        sqrtVal = rt.component_wise("sqrt", normalized, width=3)
        g.fragColor = rt.construct(4, rt.component_wise("mix", rt.swizzle(src, "rgb"), sqrtVal, _u_alpha, width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
