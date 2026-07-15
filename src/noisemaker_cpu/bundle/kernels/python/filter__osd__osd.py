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
    g.GLYPH_W = rt.i(7)
    g.GLYPH_H = rt.i(8)
    g.BASE_SCALE = rt.i(3)
    g.BASE_PADDING = rt.i(25)
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_umul__int_int(left, right):
        return rt.binary("*", left, right, 1)
    def pcg__int(v_in):
        state = rt.binary("+", cpu_umul__int_int(v_in, rt.i(747796405)), rt.i(2891336453), 1)
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1), rt.i(4), 1), 1), state, 1), rt.i(277803737), 1)
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1), word, 1)
    def hash2__int_int(a, b):
        return pcg__int(rt.binary("^", a, rt.binary("+", cpu_umul__int_int(b, rt.f(0x9e3779b9)), rt.f(0x632be59b), 1), 1))
    def hash3__int_int_int(a, b, c):
        return pcg__int(rt.binary("^", hash2__int_int(a, b), rt.binary("+", cpu_umul__int_int(c, rt.i(0x94d049bb)), rt.i(0x5bf03635), 1), 1))
    def sample_glyph__int_int_int_int(digit, localX, localY, iScale):
        gx = rt.binary("/", localX, iScale, 1)
        gy = rt.binary("/", localY, iScale, 1)
        if rt.binary("||", rt.binary("<", gx, rt.i(0)), rt.binary("||", rt.binary(">=", gx, g.GLYPH_W), rt.binary("||", rt.binary("<", gy, rt.i(0)), rt.binary(">=", gy, g.GLYPH_H)))):
            return rt.f(0.0)
        row = g.GLYPHS[int(rt.binary("+", rt.binary("*", digit, rt.i(8), 1), gy, 1))]
        return rt.construct(1, rt.binary("&", rt.binary(">>", row, rt.binary("-", rt.i(6), gx, 1), 1), rt.i(1), 1))
    def main__void():
        iScale = rt.component_wise("max", rt.construct(1, rt.binary("*", g.BASE_SCALE, _u_renderScale, 1)), rt.i(1), width=1)
        CELL_W = rt.binary("*", g.GLYPH_W, iScale, 1)
        CELL_H = rt.binary("*", g.GLYPH_H, iScale, 1)
        GAP = iScale
        PADDING = rt.construct(1, rt.binary("*", g.BASE_PADDING, _u_renderScale, 1))
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        texDims = rt.texture_size(_u_inputTex)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else rt.construct(2, texDims))
        width = rt.component_wise("max", rt.construct(1, rt.swizzle(fullRes, "x")), rt.i(1), width=1)
        height = rt.component_wise("max", rt.construct(1, rt.swizzle(fullRes, "y")), rt.i(1), width=1)
        globalCoord = rt.binary("+", coord, cpu_ivec2__vec2(_u_tileOffset), 2)
        texel = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        blend_alpha = rt.component_wise("clamp", _u_alpha, rt.f(0.0), rt.f(1.0), width=1)
        scanlineStep = rt.component_wise("max", rt.binary("/", iScale, g.BASE_SCALE, 1), rt.i(1), width=1)
        scanline = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(0.03), blend_alpha, 1), rt.construct(1, rt.binary("&", rt.binary("/", rt.swizzle(globalCoord, "y"), scanlineStep, 1), rt.i(1), 1)), 1), 1)
        base_rgb = rt.binary("*", rt.swizzle(texel, "rgb"), scanline, 3)
        if rt.binary("<=", blend_alpha, rt.f(0.0)):
            g.fragColor = rt.construct(4, base_rgb, rt.swizzle(texel, "a"))
            return
        base_seed = rt.construct(1, rt.component_wise("max", _u_seed, rt.f(1.0), width=1))
        glyph_count = rt.binary("+", rt.i(3), rt.construct(1, rt.binary("%", hash2__int_int(base_seed, rt.i(42)), rt.i(4), 1)), 1)
        overlay_w = rt.binary("+", rt.binary("*", glyph_count, CELL_W, 1), rt.binary("*", rt.binary("-", glyph_count, rt.i(1), 1), GAP, 1), 1)
        overlay_h = CELL_H
        origin_x = 0
        origin_y = 0
        if rt.binary("==", _u_corner, rt.i(0)):
            origin_x = PADDING
            origin_y = rt.binary("-", rt.binary("-", height, overlay_h, 1), PADDING, 1)
        else:
            if rt.binary("==", _u_corner, rt.i(1)):
                origin_x = rt.binary("-", rt.binary("-", width, overlay_w, 1), PADDING, 1)
                origin_y = rt.binary("-", rt.binary("-", height, overlay_h, 1), PADDING, 1)
            else:
                if rt.binary("==", _u_corner, rt.i(2)):
                    origin_x = PADDING
                    origin_y = PADDING
                else:
                    origin_x = rt.binary("-", rt.binary("-", width, overlay_w, 1), PADDING, 1)
                    origin_y = PADDING
        if rt.binary("<", origin_x, rt.i(0)):
            origin_x = rt.i(0)
        if rt.binary("<", origin_y, rt.i(0)):
            origin_y = rt.i(0)
        panel_pad = rt.binary("*", GAP, rt.i(2), 1)
        panel_x0 = rt.binary("-", origin_x, panel_pad, 1)
        panel_y0 = rt.binary("-", origin_y, panel_pad, 1)
        panel_x1 = rt.binary("+", rt.binary("+", origin_x, overlay_w, 1), panel_pad, 1)
        panel_y1 = rt.binary("+", rt.binary("+", origin_y, overlay_h, 1), panel_pad, 1)
        if rt.binary("||", rt.binary("<", rt.swizzle(globalCoord, "x"), panel_x0), rt.binary("||", rt.binary(">=", rt.swizzle(globalCoord, "x"), panel_x1), rt.binary("||", rt.binary("<", rt.swizzle(globalCoord, "y"), panel_y0), rt.binary(">=", rt.swizzle(globalCoord, "y"), panel_y1)))):
            g.fragColor = rt.construct(4, base_rgb, rt.swizzle(texel, "a"))
            return
        lx = rt.binary("-", rt.swizzle(globalCoord, "x"), origin_x, 1)
        ly = rt.binary("-", rt.swizzle(globalCoord, "y"), origin_y, 1)
        mask = rt.f(0.0)
        if rt.binary("&&", rt.binary(">=", lx, rt.i(0)), rt.binary("&&", rt.binary("<", lx, overlay_w), rt.binary("&&", rt.binary(">=", ly, rt.i(0)), rt.binary("<", ly, overlay_h)))):
            cell_stride = rt.binary("+", CELL_W, GAP, 1)
            glyph_idx = rt.binary("/", lx, cell_stride, 1)
            within_glyph_x = rt.binary("-", lx, rt.binary("*", glyph_idx, cell_stride, 1), 1)
            if rt.binary("&&", rt.binary("<", within_glyph_x, CELL_W), rt.binary("<", glyph_idx, glyph_count)):
                local_y = rt.binary("-", rt.binary("-", CELL_H, rt.i(1), 1), ly, 1)
                time_cell = rt.construct(1, rt.component_wise("floor", rt.binary("*", _u_time, rt.component_wise("max", _u_speed, rt.f(0.001), width=1), 1), width=1))
                digit_hash = hash3__int_int_int(base_seed, rt.construct(1, glyph_idx), rt.construct(1, time_cell))
                digit = rt.construct(1, rt.binary("%", digit_hash, rt.i(10), 1))
                mask = sample_glyph__int_int_int_int(digit, within_glyph_x, local_y, iScale)
        panel_bg = rt.binary("*", base_rgb, rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(0.5), blend_alpha, 1), 1), 3)
        if rt.binary("<", mask, rt.f(0.5)):
            g.fragColor = rt.construct(4, rt.component_wise("clamp", panel_bg, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(texel, "a"))
            return
        osd_color = rt.construct(3, rt.f(0.7), rt.f(1.0), rt.f(0.75))
        highlight = rt.component_wise("max", panel_bg, rt.binary("*", osd_color, mask, 3), width=3)
        blended = rt.component_wise("mix", panel_bg, highlight, blend_alpha, width=3)
        g.fragColor = rt.construct(4, rt.component_wise("clamp", blended, rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(texel, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
