def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_rows = U.get("rows", 0)
    _u_seed = U.get("seed", 0)
    g.fragColor = rt.construct(4, 0.0)
    g.GLYPHS = rt.array([rt.i(60), rt.i(66), rt.i(66), rt.i(66), rt.i(66), rt.i(66), rt.i(60), rt.i(0), rt.i(24), rt.i(8), rt.i(8), rt.i(8), rt.i(28), rt.i(28), rt.i(28), rt.i(0), rt.i(28), rt.i(4), rt.i(4), rt.i(28), rt.i(16), rt.i(16), rt.i(28), rt.i(0), rt.i(28), rt.i(4), rt.i(4), rt.i(28), rt.i(6), rt.i(6), rt.i(30), rt.i(0), rt.i(96), rt.i(96), rt.i(96), rt.i(96), rt.i(102), rt.i(126), rt.i(6), rt.i(0), rt.i(60), rt.i(32), rt.i(32), rt.i(60), rt.i(4), rt.i(4), rt.i(60), rt.i(0), rt.i(120), rt.i(72), rt.i(64), rt.i(64), rt.i(126), rt.i(66), rt.i(126), rt.i(0), rt.i(60), rt.i(36), rt.i(4), rt.i(12), rt.i(8), rt.i(8), rt.i(8), rt.i(0), rt.i(60), rt.i(36), rt.i(36), rt.i(126), rt.i(102), rt.i(102), rt.i(126), rt.i(0), rt.i(62), rt.i(34), rt.i(34), rt.i(62), rt.i(6), rt.i(6), rt.i(6), rt.i(0)])
    g.GLYPH_W = rt.i(7)
    g.GLYPH_H = rt.i(8)
    g.BASE_SCALE = rt.i(3)
    g.BASE_ROW_GAP = rt.i(4)
    def hash_mix__uint(v):
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 1, "uint"), 1, "uint")
        v = rt.binary("*", v, rt.i(2146121005), 1, "uint")
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(15), 1, "uint"), 1, "uint")
        v = rt.binary("*", v, rt.i(2221713035), 1, "uint")
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 1, "uint"), 1, "uint")
        return v
    def sample_glyph__int_int_int_int(digit, localX, localY, iScale):
        gx = rt.binary("/", localX, iScale, 1, "int")
        gy = rt.binary("/", localY, iScale, 1, "int")
        if (bool((bool((bool(rt.binary("<", gx, rt.i(0))) or bool(rt.binary(">=", gx, g.GLYPH_W)))) or bool(rt.binary("<", gy, rt.i(0))))) or bool(rt.binary(">=", gy, g.GLYPH_H))):
            return rt.f(0.0)
        row = g.GLYPHS[int(rt.binary("+", rt.binary("*", digit, rt.i(8), 1, "int"), gy, 1, "int"))]
        return rt.construct(1, rt.binary("&", rt.binary(">>", row, rt.binary("-", rt.i(6), gx, 1, "int"), 1, "int"), rt.i(1), 1, "int"))
    def ticker_row_mask__int_int_int_float_int_int(pixelX, pixelY, rowSeed, t, CELL_W, iScale):
        scrollSpeed = rt.binary("+", rt.f(0.5), rt.binary("*", rt.binary("/", rt.construct(1, rt.binary("&", hash_mix__uint(rt.binary("^", rt.construct(1, rowSeed, base="uint"), rt.i(17), 1, "uint")), rt.i(65535), 1, "uint")), rt.f(65535.0), 1, "float"), rt.f(1.5), 1, "float"), 1, "float")
        offset = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.binary("*", t, scrollSpeed, 1, "float"), rt.f(120.0), 1, "float"), width=1), base="int")
        sx = rt.binary("+", pixelX, offset, 1, "int")
        cellX = (rt.binary("/", sx, CELL_W, 1, "int") if rt.binary(">=", sx, rt.i(0)) else rt.binary("/", rt.binary("+", rt.binary("-", sx, CELL_W, 1, "int"), rt.i(1), 1, "int"), CELL_W, 1, "int"))
        localX = rt.binary("-", sx, rt.binary("*", cellX, CELL_W, 1, "int"), 1, "int")
        h = hash_mix__uint(rt.binary("^", rt.construct(1, cellX, base="uint"), rt.binary("*", rt.construct(1, rowSeed, base="uint"), rt.i(997), 1, "uint"), 1, "uint"))
        digit = rt.construct(1, rt.binary("%", h, rt.i(10), 1, "uint"), base="int")
        return sample_glyph__int_int_int_int(digit, localX, pixelY, iScale)
    def main__void():
        iScale = rt.component_wise("max", rt.construct(1, rt.binary("*", rt.construct(1, g.BASE_SCALE), _u_renderScale, 1, "float"), base="int"), rt.i(1), width=1)
        CELL_W = rt.binary("*", g.GLYPH_W, iScale, 1, "int")
        CELL_H = rt.binary("*", g.GLYPH_H, iScale, 1, "int")
        ROW_GAP = rt.component_wise("max", rt.construct(1, rt.binary("*", rt.construct(1, g.BASE_ROW_GAP), _u_renderScale, 1, "float"), base="int"), rt.i(1), width=1)
        dims = rt.construct(2, rt.texture_size(_u_inputTex))
        src = rt.texture(_u_inputTex, ctx.uv)
        t = rt.binary("*", _u_time, _u_speed, 1, "float")
        baseSeed = hash_mix__uint(rt.binary("*", rt.construct(1, _u_seed, base="uint"), rt.i(7919), 1, "uint"))
        totalH = rt.binary("*", _u_rows, rt.binary("+", CELL_H, ROW_GAP, 1, "int"), 1, "int")
        px = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.swizzle(ctx.uv, "x"), rt.swizzle(dims, "x"), 1, "float"), width=1), base="int")
        pyFromBottom = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(ctx.uv, "y"), 1, "float"), rt.swizzle(dims, "y"), 1, "float"), width=1), base="int")
        if rt.binary(">=", pyFromBottom, totalH):
            g.fragColor[:] = src
            return
        rowStride = rt.binary("+", CELL_H, ROW_GAP, 1, "int")
        rowIdx = rt.binary("/", pyFromBottom, rowStride, 1, "int")
        localY = rt.binary("-", pyFromBottom, rt.binary("*", rowIdx, rowStride, 1, "int"), 1, "int")
        if (bool(rt.binary(">=", rowIdx, _u_rows)) or bool(rt.binary(">=", localY, CELL_H))):
            g.fragColor[:] = src
            return
        rowSeed = rt.construct(1, hash_mix__uint(rt.binary("+", rt.construct(1, rowIdx, base="uint"), baseSeed, 1, "uint")), base="int")
        mask = ticker_row_mask__int_int_int_float_int_int(px, localY, rowSeed, t, CELL_W, iScale)
        shadow = rt.f(0.0)
        shadowOff = rt.component_wise("max", rt.construct(1, rt.binary("*", rt.f(2.0), _u_renderScale, 1, "float"), base="int"), rt.i(1), width=1)
        shadowLocalY = rt.binary("+", localY, shadowOff, 1, "int")
        if rt.binary("<", shadowLocalY, CELL_H):
            shadow = ticker_row_mask__int_int_int_float_int_int(rt.binary("+", px, shadowOff, 1, "int"), shadowLocalY, rowSeed, t, CELL_W, iScale)
        result = rt.swizzle(src, "rgb")
        result[:] = rt.binary("*", result, rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", shadow, rt.f(0.4), 1, "float"), _u_alpha, 1, "float"), 1, "float"), 3, "float")
        result[:] = rt.component_wise("max", result, rt.binary("*", rt.construct(3, mask), _u_alpha, 3, "float"), width=3)
        g.fragColor[:] = rt.construct(4, rt.component_wise("clamp", result, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(src, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
