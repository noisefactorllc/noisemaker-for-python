def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_color = U["color"]
    _u_alpha = U["alpha"]
    _u_mode = U["mode"]
    _u_inputTex = T["inputTex"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def rgb_to_hsv__vec3(rgb):
        rgb = rt.copy(rgb)
        r = rt.swizzle(rgb, "x")
        g = rt.swizzle(rgb, "y")
        b = rt.swizzle(rgb, "z")
        max_c = rt.component_wise("max", rt.component_wise("max", r, g, width=1), b, width=1)
        min_c = rt.component_wise("min", rt.component_wise("min", r, g, width=1), b, width=1)
        delta = rt.binary("-", max_c, min_c, 1)
        hue = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", max_c, r):
                raw = rt.binary("/", rt.binary("-", g, b, 1), delta, 1)
                raw = rt.binary("-", raw, rt.binary("*", rt.component_wise("floor", rt.binary("/", raw, rt.f(6.0), 1), width=1), rt.f(6.0), 1), 1)
                if rt.binary("<", raw, rt.f(0.0)):
                    raw = rt.binary("+", raw, rt.f(6.0), 1)
                hue = raw
            else:
                if rt.binary("==", max_c, g):
                    hue = rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1), delta, 1), rt.f(2.0), 1)
                else:
                    hue = rt.binary("+", rt.binary("/", rt.binary("-", r, g, 1), delta, 1), rt.f(4.0), 1)
        hue = rt.binary("/", hue, rt.f(6.0), 1)
        if rt.binary("<", hue, rt.f(0.0)):
            hue = rt.binary("+", hue, rt.f(1.0), 1)
        sat = (rt.binary("/", delta, max_c, 1) if rt.binary("!=", max_c, rt.f(0.0)) else rt.f(0.0))
        return rt.construct(3, hue, sat, max_c)
    def hsv_to_rgb__vec3(hsv):
        hsv = rt.copy(hsv)
        h = rt.swizzle(hsv, "x")
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        dh = rt.binary("*", h, rt.f(6.0), 1)
        dr = rt.component_wise("clamp", rt.binary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(3.0), 1), width=1), rt.f(1.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        dg = rt.component_wise("clamp", rt.binary("+", rt.unary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(2.0), 1), width=1)), rt.f(2.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        db = rt.component_wise("clamp", rt.binary("+", rt.unary("-", rt.component_wise("abs", rt.binary("-", dh, rt.f(4.0), 1), width=1)), rt.f(2.0), 1), rt.f(0.0), rt.f(1.0), width=1)
        oms = rt.binary("-", rt.f(1.0), s, 1)
        return rt.construct(3, rt.binary("*", rt.binary("+", oms, rt.binary("*", s, dr, 1), 1), v, 1), rt.binary("*", rt.binary("+", oms, rt.binary("*", s, dg, 1), 1), v, 1), rt.binary("*", rt.binary("+", oms, rt.binary("*", s, db, 1), 1), v, 1))
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.component_wise("max", rt.texture_size(_u_inputTex), cpu_ivec2__float(rt.i(1)), width=2)), 2)
        base = rt.texture(_u_inputTex, st)
        base_rgb = rt.component_wise("clamp", rt.swizzle(base, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
        m = rt.construct(1, _u_mode)
        tinted = rt.construct(3, 0.0)
        if rt.binary("==", m, rt.i(1)):
            tinted = rt.binary("*", base_rgb, _u_color, 3)
        else:
            if rt.binary("==", m, rt.i(2)):
                tintHue = rt.swizzle(rgb_to_hsv__vec3(_u_color), "x")
                base_hsv = rgb_to_hsv__vec3(base_rgb)
                tinted = rt.component_wise("clamp", hsv_to_rgb__vec3(rt.construct(3, tintHue, rt.component_wise("clamp", rt.swizzle(base_rgb, "y"), rt.f(0.0), rt.f(1.0), width=1), rt.component_wise("clamp", rt.swizzle(base_hsv, "z"), rt.f(0.0), rt.f(1.0), width=1))), rt.f(0.0), rt.f(1.0), width=3)
            else:
                tinted = _u_color
        rgb = rt.component_wise("mix", base_rgb, tinted, _u_alpha, width=3)
        g.fragColor = rt.construct(4, rgb, rt.swizzle(base, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
