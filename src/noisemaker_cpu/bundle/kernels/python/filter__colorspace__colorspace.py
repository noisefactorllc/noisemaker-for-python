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
    _u_mode = U["mode"]
    g.TAU = rt.f(6.28318530718)
    g.fwdA = rt.construct(9, rt.f(1.0), rt.f(1.0), rt.f(1.0), rt.f(0.3963377774), rt.unary("-", rt.f(0.1055613458)), rt.unary("-", rt.f(0.0894841775)), rt.f(0.2158037573), rt.unary("-", rt.f(0.0638541728)), rt.unary("-", rt.f(1.2914855480)))
    g.fwdB = rt.construct(9, rt.f(4.0767245293), rt.unary("-", rt.f(1.2681437731)), rt.unary("-", rt.f(0.0041119885)), rt.unary("-", rt.f(3.3072168827)), rt.f(2.6093323231), rt.unary("-", rt.f(0.7034763098)), rt.f(0.2307590544), rt.unary("-", rt.f(0.3411344290)), rt.f(1.7068625689))
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
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
    def linear_srgb_from_oklab__vec3(c):
        c = rt.copy(c)
        lms = rt.binary("*", g.fwdA, c, 9)
        return rt.binary("*", g.fwdB, rt.binary("*", rt.binary("*", lms, lms, 3), lms, 3), 9)
    def linearToSrgb__vec3(linear):
        linear = rt.copy(linear)
        srgb = rt.construct(3, 0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                rt.unary("++", i)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            if rt.binary("<=", linear[int(i)], rt.f(0.0031308)):
                srgb[int(i)] = rt.binary("*", linear[int(i)], rt.f(12.92), 1)
            else:
                srgb[int(i)] = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear[int(i)], rt.binary("/", rt.f(1.0), rt.f(2.4), 1), width=1), 1), rt.f(0.055), 1)
        return srgb
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        color = rt.texture(_u_inputTex, uv)
        if rt.binary("==", _u_mode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(rt.swizzle(color, "rgb")))
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                color = rt.assign_swizzle(color, "g", rt.binary("+", rt.binary("*", rt.swizzle(color, "g"), rt.unary("-", rt.f(0.509)), 1), rt.f(0.276), 1))
                color = rt.assign_swizzle(color, "b", rt.binary("+", rt.binary("*", rt.swizzle(color, "b"), rt.unary("-", rt.f(0.509)), 1), rt.f(0.198), 1))
                color = rt.assign_swizzle(color, "rgb", linear_srgb_from_oklab__vec3(rt.swizzle(color, "rgb")))
                color = rt.assign_swizzle(color, "rgb", linearToSrgb__vec3(rt.swizzle(color, "rgb")))
            else:
                L = rt.swizzle(color, "r")
                C = rt.binary("*", rt.swizzle(color, "g"), rt.f(0.4), 1)
                H = rt.binary("*", rt.swizzle(color, "b"), g.TAU, 1)
                a = rt.binary("*", C, rt.component_wise("cos", H, width=1), 1)
                b = rt.binary("*", C, rt.component_wise("sin", H, width=1), 1)
                color = rt.assign_swizzle(color, "rgb", linear_srgb_from_oklab__vec3(rt.construct(3, L, a, b)))
                color = rt.assign_swizzle(color, "rgb", linearToSrgb__vec3(rt.swizzle(color, "rgb")))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
