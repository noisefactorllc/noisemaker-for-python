def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_renderScale = U["renderScale"]
    _u_time = U["time"]
    _u_speed = U["speed"]
    _u_alpha = U["alpha"]
    _u_rows = U["rows"]
    _u_seed = U["seed"]
    g.GLYPH_W = rt.i(7)
    g.GLYPH_H = rt.i(8)
    g.BASE_SCALE = rt.i(3)
    g.BASE_ROW_GAP = rt.i(4)
    def cpu_umul__int_int(left, right):
        return rt.binary("*", left, right, 1)
    def hash_mix__int(v):
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 1), 1)
        v = cpu_umul__int_int(v, rt.f(0x7feb352d))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(15), 1), 1)
        v = cpu_umul__int_int(v, rt.i(0x846ca68b))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 1), 1)
        return v
    def sample_glyph__int_int_int_int(digit, localX, localY, iScale):
        gx = rt.binary("/", localX, iScale, 1)
        gy = rt.binary("/", localY, iScale, 1)
        if rt.binary("||", rt.binary("<", gx, rt.i(0)), rt.binary("||", rt.binary(">=", gx, g.GLYPH_W), rt.binary("||", rt.binary("<", gy, rt.i(0)), rt.binary(">=", gy, g.GLYPH_H)))):
            return rt.f(0.0)
        row = g.GLYPHS[int(rt.binary("+", rt.binary("*", digit, rt.i(8), 1), gy, 1))]
        return rt.construct(1, rt.binary("&", rt.binary(">>", row, rt.binary("-", rt.i(6), gx, 1), 1), rt.i(1), 1))
    def ticker_row_mask__int_int_int_float_int_int(pixelX, pixelY, rowSeed, t, CELL_W, iScale):
        scrollSpeed = rt.binary("+", rt.f(0.5), rt.binary("*", rt.binary("/", rt.construct(1, rt.binary("&", hash_mix__int(rt.binary("^", rt.construct(1, rowSeed), rt.i(17), 1)), rt.i(0xFFF), 1)), rt.f(65535.0), 1), rt.f(1.5), 1), 1)
        offset = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.binary("*", t, scrollSpeed, 1), rt.f(120.0), 1), width=1))
        sx = rt.binary("+", pixelX, offset, 1)
        cellX = (rt.binary("/", sx, CELL_W, 1) if rt.binary(">=", sx, rt.i(0)) else rt.binary("/", rt.binary("+", rt.binary("-", sx, CELL_W, 1), rt.i(1), 1), CELL_W, 1))
        localX = rt.binary("-", sx, rt.binary("*", cellX, CELL_W, 1), 1)
        h = hash_mix__int(rt.binary("^", rt.construct(1, cellX), rt.binary("*", rt.construct(1, rowSeed), rt.i(997), 1), 1))
        digit = rt.construct(1, rt.binary("%", h, rt.i(10), 1))
        return sample_glyph__int_int_int_int(digit, localX, pixelY, iScale)
    def main__void():
        iScale = rt.component_wise("max", rt.construct(1, rt.binary("*", g.BASE_SCALE, _u_renderScale, 1)), rt.i(1), width=1)
        CELL_W = rt.binary("*", g.GLYPH_W, iScale, 1)
        CELL_H = rt.binary("*", g.GLYPH_H, iScale, 1)
        ROW_GAP = rt.component_wise("max", rt.construct(1, rt.binary("*", g.BASE_ROW_GAP, _u_renderScale, 1)), rt.i(1), width=1)
        dims = rt.construct(2, rt.texture_size(_u_inputTex))
        src = rt.texture(_u_inputTex, g.v_texCoord)
        t = rt.binary("*", _u_time, _u_speed, 1)
        baseSeed = hash_mix__int(rt.binary("*", rt.construct(1, _u_seed), rt.i(7919), 1))
        totalH = rt.binary("*", _u_rows, rt.binary("+", CELL_H, ROW_GAP, 1), 1)
        px = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(g.v_texCoord, "x"), rt.swizzle(dims, "x"), 1), width=1))
        pyFromBottom = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(g.v_texCoord, "y"), 1), rt.swizzle(dims, "y"), 1), width=1))
        if rt.binary(">=", pyFromBottom, totalH):
            g.fragColor = src
            return
        rowStride = rt.binary("+", CELL_H, ROW_GAP, 1)
        rowIdx = rt.binary("/", pyFromBottom, rowStride, 1)
        localY = rt.binary("-", pyFromBottom, rt.binary("*", rowIdx, rowStride, 1), 1)
        if rt.binary("||", rt.binary(">=", rowIdx, _u_rows), rt.binary(">=", localY, CELL_H)):
            g.fragColor = src
            return
        rowSeed = rt.construct(1, hash_mix__int(rt.binary("+", rt.construct(1, rowIdx), baseSeed, 1)))
        mask = ticker_row_mask__int_int_int_float_int_int(px, localY, rowSeed, t, CELL_W, iScale)
        shadow = rt.f(0.0)
        shadowOff = rt.component_wise("max", rt.construct(1, rt.binary("*", rt.f(2.0), _u_renderScale, 1)), rt.i(1), width=1)
        shadowLocalY = rt.binary("+", localY, shadowOff, 1)
        if rt.binary("<", shadowLocalY, CELL_H):
            shadow = ticker_row_mask__int_int_int_float_int_int(rt.binary("+", px, shadowOff, 1), shadowLocalY, rowSeed, t, CELL_W, iScale)
        result = rt.swizzle(src, "rgb")
        result = rt.binary("*", result, rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", shadow, rt.f(0.4), 1), _u_alpha, 1), 1), 3)
        result = rt.component_wise("max", result, rt.binary("*", rt.construct(3, mask), _u_alpha, 3), width=3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
