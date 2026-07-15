def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_rotation = U["rotation"]
    _u_hueRange = U["hueRange"]
    _u_saturation = U["saturation"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb)
        r = rt.swizzle(rgb, "r")
        g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        maxC = rt.component_wise("max", r, rt.component_wise("max", g, b, width=1), width=1)
        minC = rt.component_wise("min", r, rt.component_wise("min", g, b, width=1), width=1)
        delta = rt.binary("-", maxC, minC, 1)
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", maxC, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", g, b, 1), delta, 1), rt.f(6.0), width=1), rt.f(6.0), 1)
            else:
                if rt.binary("==", maxC, g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1), delta, 1), rt.f(2.0), 1), rt.f(6.0), 1)
                else:
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, g, 1), delta, 1), rt.f(4.0), 1), rt.f(6.0), 1)
        s = (rt.f(0.0) if rt.binary("==", maxC, rt.f(0.0)) else rt.binary("/", delta, maxC, 1))
        return rt.construct(3, h, s, maxC)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv)
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1)
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1), rt.f(2.0), width=1), rt.f(1.0), 1), width=1), 1), 1)
        m = rt.binary("-", v, c, 1)
        rgb = rt.construct(3, 0.0)
        if rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1)):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1)):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1)):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1)):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1)):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            rgb = rt.construct(3, c, rt.f(0.0), x)
        return rt.binary("+", rgb, m, 3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        color = rt.texture(_u_inputTex, uv)
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv = rt.assign_swizzle(hsv, "x", rt.component_wise("fract", rt.binary("+", rt.binary("*", rt.swizzle(hsv, "x"), map__float_float_float_float_float(_u_hueRange, rt.f(0.0), rt.f(200.0), rt.f(0.0), rt.f(2.0)), 1), rt.binary("/", _u_rotation, rt.f(360.0), 1), 1), width=1))
        hsv = rt.assign_swizzle(hsv, "y", rt.binary("*", rt.swizzle(hsv, "y"), _u_saturation, 1))
        color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(hsv))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
