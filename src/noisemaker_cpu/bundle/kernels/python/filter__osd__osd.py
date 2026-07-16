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
    _u_renderScale = U["renderScale"]
    _u_alpha = U["alpha"]
    _u_seed = U["seed"]
    _u_speed = U["speed"]
    _u_time = U["time"]
    _u_corner = U["corner"]
    g.fragColor = rt.construct(4, 0.0)
    g.GLYPHS = rt.array([rt.i(60), rt.i(66), rt.i(66), rt.i(66), rt.i(66), rt.i(66), rt.i(60), rt.i(0), rt.i(24), rt.i(8), rt.i(8), rt.i(8), rt.i(28), rt.i(28), rt.i(28), rt.i(0), rt.i(28), rt.i(4), rt.i(4), rt.i(28), rt.i(16), rt.i(16), rt.i(28), rt.i(0), rt.i(28), rt.i(4), rt.i(4), rt.i(28), rt.i(6), rt.i(6), rt.i(30), rt.i(0), rt.i(96), rt.i(96), rt.i(96), rt.i(96), rt.i(102), rt.i(126), rt.i(6), rt.i(0), rt.i(60), rt.i(32), rt.i(32), rt.i(60), rt.i(4), rt.i(4), rt.i(60), rt.i(0), rt.i(120), rt.i(72), rt.i(64), rt.i(64), rt.i(126), rt.i(66), rt.i(126), rt.i(0), rt.i(60), rt.i(36), rt.i(4), rt.i(12), rt.i(8), rt.i(8), rt.i(8), rt.i(0), rt.i(60), rt.i(36), rt.i(36), rt.i(126), rt.i(102), rt.i(102), rt.i(126), rt.i(0), rt.i(62), rt.i(34), rt.i(34), rt.i(62), rt.i(6), rt.i(6), rt.i(6), rt.i(0)])
    g.GLYPH_W = rt.i(7)
    g.GLYPH_H = rt.i(8)
    g.BASE_SCALE = rt.i(3)
    g.BASE_PADDING = rt.i(25)
    def pcg__uint(v_in):
        state = rt.binary("+", rt.binary("*", v_in, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash2__uint_uint(a, b):
        return pcg__uint(rt.binary("^", a, rt.binary("+", rt.binary("*", b, rt.i(2654435769), 1, "uint"), rt.i(1663821211), 1, "uint"), 1, "uint"))
    def hash3__uint_uint_uint(a, b, c):
        return pcg__uint(rt.binary("^", hash2__uint_uint(a, b), rt.binary("+", rt.binary("*", c, rt.i(2496678331), 1, "uint"), rt.i(1542469173), 1, "uint"), 1, "uint"))
    def sample_glyph__int_int_int_int(digit, localX, localY, iScale):
        gx = rt.binary("/", localX, iScale, 1, "int")
        gy = rt.binary("/", localY, iScale, 1, "int")
        if (bool((bool((bool(rt.binary("<", gx, rt.i(0))) or bool(rt.binary(">=", gx, g.GLYPH_W)))) or bool(rt.binary("<", gy, rt.i(0))))) or bool(rt.binary(">=", gy, g.GLYPH_H))):
            return rt.f(0.0)
        row = g.GLYPHS[int(rt.binary("+", rt.binary("*", digit, rt.i(8), 1, "int"), gy, 1, "int"))]
        return rt.construct(1, rt.binary("&", rt.binary(">>", row, rt.binary("-", rt.i(6), gx, 1, "int"), 1, "int"), rt.i(1), 1, "int"))
    def main__void():
        iScale = rt.component_wise("max", rt.construct(1, rt.binary("*", rt.construct(1, g.BASE_SCALE), _u_renderScale, 1, "float"), base="int"), rt.i(1), width=1)
        CELL_W = rt.binary("*", g.GLYPH_W, iScale, 1, "int")
        CELL_H = rt.binary("*", g.GLYPH_H, iScale, 1, "int")
        GAP = iScale
        PADDING = rt.construct(1, rt.binary("*", rt.construct(1, g.BASE_PADDING), _u_renderScale, 1, "float"), base="int")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        texDims = rt.texture_size(_u_inputTex)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, texDims))
        width = rt.component_wise("max", rt.construct(1, rt.swizzle(fullRes, "x"), base="int"), rt.i(1), width=1)
        height = rt.component_wise("max", rt.construct(1, rt.swizzle(fullRes, "y"), base="int"), rt.i(1), width=1)
        globalCoord = rt.binary("+", coord, rt.construct(2, _u_tileOffset, base="int"), 2, "int")
        texel = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        blend_alpha = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        scanlineStep = rt.component_wise("max", rt.binary("/", iScale, g.BASE_SCALE, 1, "int"), rt.i(1), width=1)
        scanline = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(0.03), blend_alpha, 1, "float"), rt.construct(1, rt.binary("&", rt.binary("/", rt.swizzle(globalCoord, "y"), scanlineStep, 1, "int"), rt.i(1), 1, "int")), 1, "float"), 1, "float")
        base_rgb = rt.binary("*", rt.swizzle(texel, "rgb"), scanline, 3, "float")
        if rt.binary("<=", blend_alpha, rt.f(0.0)):
            g.fragColor = rt.construct(4, base_rgb, rt.swizzle(texel, "a"))
            return
        base_seed = rt.construct(1, rt.component_wise("max", _u_seed, rt.f(1.0), width=1), base="uint")
        glyph_count = rt.binary("+", rt.i(3), rt.construct(1, rt.binary("%", hash2__uint_uint(base_seed, rt.i(42)), rt.i(4), 1, "uint"), base="int"), 1, "int")
        overlay_w = rt.binary("+", rt.binary("*", glyph_count, CELL_W, 1, "int"), rt.binary("*", rt.binary("-", glyph_count, rt.i(1), 1, "int"), GAP, 1, "int"), 1, "int")
        overlay_h = CELL_H
        origin_x = 0
        origin_y = 0
        if rt.binary("==", _u_corner, rt.i(0)):
            origin_x = PADDING
            origin_y = rt.binary("-", rt.binary("-", height, overlay_h, 1, "int"), PADDING, 1, "int")
        else:
            if rt.binary("==", _u_corner, rt.i(1)):
                origin_x = rt.binary("-", rt.binary("-", width, overlay_w, 1, "int"), PADDING, 1, "int")
                origin_y = rt.binary("-", rt.binary("-", height, overlay_h, 1, "int"), PADDING, 1, "int")
            else:
                if rt.binary("==", _u_corner, rt.i(2)):
                    origin_x = PADDING
                    origin_y = PADDING
                else:
                    origin_x = rt.binary("-", rt.binary("-", width, overlay_w, 1, "int"), PADDING, 1, "int")
                    origin_y = PADDING
        if rt.binary("<", origin_x, rt.i(0)):
            origin_x = rt.i(0)
        if rt.binary("<", origin_y, rt.i(0)):
            origin_y = rt.i(0)
        panel_pad = rt.binary("*", GAP, rt.i(2), 1, "int")
        panel_x0 = rt.binary("-", origin_x, panel_pad, 1, "int")
        panel_y0 = rt.binary("-", origin_y, panel_pad, 1, "int")
        panel_x1 = rt.binary("+", rt.binary("+", origin_x, overlay_w, 1, "int"), panel_pad, 1, "int")
        panel_y1 = rt.binary("+", rt.binary("+", origin_y, overlay_h, 1, "int"), panel_pad, 1, "int")
        if (bool((bool((bool(rt.binary("<", rt.swizzle(globalCoord, "x"), panel_x0)) or bool(rt.binary(">=", rt.swizzle(globalCoord, "x"), panel_x1)))) or bool(rt.binary("<", rt.swizzle(globalCoord, "y"), panel_y0)))) or bool(rt.binary(">=", rt.swizzle(globalCoord, "y"), panel_y1))):
            g.fragColor = rt.construct(4, base_rgb, rt.swizzle(texel, "a"))
            return
        lx = rt.binary("-", rt.swizzle(globalCoord, "x"), origin_x, 1, "int")
        ly = rt.binary("-", rt.swizzle(globalCoord, "y"), origin_y, 1, "int")
        mask = rt.f(0.0)
        if (bool((bool((bool(rt.binary(">=", lx, rt.i(0))) and bool(rt.binary("<", lx, overlay_w)))) and bool(rt.binary(">=", ly, rt.i(0))))) and bool(rt.binary("<", ly, overlay_h))):
            cell_stride = rt.binary("+", CELL_W, GAP, 1, "int")
            glyph_idx = rt.binary("/", lx, cell_stride, 1, "int")
            within_glyph_x = rt.binary("-", lx, rt.binary("*", glyph_idx, cell_stride, 1, "int"), 1, "int")
            if (bool(rt.binary("<", within_glyph_x, CELL_W)) and bool(rt.binary("<", glyph_idx, glyph_count))):
                local_y = rt.binary("-", rt.binary("-", CELL_H, rt.i(1), 1, "int"), ly, 1, "int")
                time_cell = rt.construct(1, rt.component_wise("floor", rt.binary("*", _u_time, rt.component_wise("max", _u_speed, rt.f(0.001), width=1), 1, "float"), width=1), base="int")
                digit_hash = hash3__uint_uint_uint(base_seed, rt.construct(1, glyph_idx, base="uint"), rt.construct(1, time_cell, base="uint"))
                digit = rt.construct(1, rt.binary("%", digit_hash, rt.i(10), 1, "uint"), base="int")
                mask = sample_glyph__int_int_int_int(digit, within_glyph_x, local_y, iScale)
        panel_bg = rt.binary("*", base_rgb, rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(0.5), blend_alpha, 1, "float"), 1, "float"), 3, "float")
        if rt.binary("<", mask, rt.f(0.5)):
            g.fragColor = rt.construct(4, rt.component_wise("clamp", panel_bg, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(texel, "a"))
            return
        osd_color = rt.construct(3, rt.f(0.7), rt.f(1.0), rt.f(0.75))
        highlight = rt.component_wise("max", panel_bg, rt.binary("*", osd_color, mask, 3, "float"), width=3)
        blended = rt.component_wise("mix", panel_bg, highlight, blend_alpha, width=3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", blended, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
