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
    _u_paletteIndex = U["paletteIndex"]
    _u_rotation = U["rotation"]
    _u_offset = U["offset"]
    _u_repeat = U["repeat"]
    _u_alpha = U["alpha"]
    _u_time = U["time"]
    g.MODE_RGB = rt.i(0)
    g.MODE_HSV = rt.i(1)
    g.MODE_OKLAB = rt.i(2)
    g.PALETTE_COUNT = rt.i(55)
    g.TAU = rt.f(6.283185307179586)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv)
        h = rt.swizzle(hsv, "x")
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1)
        hp = rt.binary("*", h, rt.f(6.0), 1)
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", hp, rt.f(2.0), width=1), rt.f(1.0), 1), width=1), 1), 1)
        m = rt.binary("-", v, c, 1)
        rgb = rt.construct(3, 0.0)
        if rt.binary("<", hp, rt.f(1.0)):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("<", hp, rt.f(2.0)):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("<", hp, rt.f(3.0)):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("<", hp, rt.f(4.0)):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("<", hp, rt.f(5.0)):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            rgb = rt.construct(3, c, rt.f(0.0), x)
        return rt.binary("+", rgb, rt.construct(3, m), 3)
    def oklab2linear__vec3(lab):
        lab = rt.copy(lab)
        L = rt.swizzle(lab, "x")
        a = rt.swizzle(lab, "y")
        b = rt.swizzle(lab, "z")
        l_ = rt.binary("+", rt.binary("+", L, rt.binary("*", rt.f(0.3963377774), a, 1), 1), rt.binary("*", rt.f(0.2158037573), b, 1), 1)
        m_ = rt.binary("-", rt.binary("-", L, rt.binary("*", rt.f(0.1055613458), a, 1), 1), rt.binary("*", rt.f(0.0638541728), b, 1), 1)
        s_ = rt.binary("-", rt.binary("-", L, rt.binary("*", rt.f(0.0894841775), a, 1), 1), rt.binary("*", rt.f(1.2914855480), b, 1), 1)
        l = rt.binary("*", rt.binary("*", l_, l_, 1), l_, 1)
        m = rt.binary("*", rt.binary("*", m_, m_, 1), m_, 1)
        s = rt.binary("*", rt.binary("*", s_, s_, 1), s_, 1)
        return rt.construct(3, rt.binary("+", rt.binary("-", rt.binary("*", rt.f(4.0767416621), l, 1), rt.binary("*", rt.f(3.3077115913), m, 1), 1), rt.binary("*", rt.f(0.2309699292), s, 1), 1), rt.binary("-", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(1.2684380046)), l, 1), rt.binary("*", rt.f(2.6097574011), m, 1), 1), rt.binary("*", rt.f(0.3413193965), s, 1), 1), rt.binary("+", rt.binary("-", rt.binary("*", rt.unary("-", rt.f(0.0041960863)), l, 1), rt.binary("*", rt.f(0.7034186147), m, 1), 1), rt.binary("*", rt.f(1.7076147010), s, 1), 1))
    def linear2srgb__vec3(linear):
        linear = rt.copy(linear)
        low = rt.binary("*", linear, rt.f(12.92), 3)
        high = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", linear, rt.construct(3, rt.binary("/", rt.f(1.0), rt.f(2.4), 1)), width=3), 3), rt.f(0.055), 3)
        return rt.component_wise("mix", high, low, rt.component_wise("step", linear, rt.construct(3, rt.f(0.0031308)), width=3), width=3)
    def oklab2rgb__vec3(lab):
        lab = rt.copy(lab)
        lab = rt.assign_swizzle(lab, "g", rt.binary("+", rt.binary("*", rt.swizzle(lab, "g"), rt.unary("-", rt.f(0.509)), 1), rt.f(0.276), 1))
        lab = rt.assign_swizzle(lab, "b", rt.binary("+", rt.binary("*", rt.swizzle(lab, "b"), rt.unary("-", rt.f(0.509)), 1), rt.f(0.198), 1))
        linear_rgb = oklab2linear__vec3(lab)
        return rt.component_wise("clamp", linear2srgb__vec3(linear_rgb), rt.f(0.0), rt.f(1.0), width=3)
    def cosinePalette__float_vec3_vec3_vec3_vec3(t, amp, freq, offset, phase):
        amp = rt.copy(amp)
        freq = rt.copy(freq)
        offset = rt.copy(offset)
        phase = rt.copy(phase)
        return rt.component_wise("clamp", rt.binary("+", offset, rt.binary("*", amp, rt.component_wise("cos", rt.binary("*", g.TAU, rt.binary("+", rt.binary("*", freq, t, 3), phase, 3), 3), width=3), 3), 3), rt.f(0.0), rt.f(1.0), width=3)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2)
        inputColor = rt.texture(_u_inputTex, uv)
        if rt.binary("||", rt.binary("<=", _u_paletteIndex, rt.i(0)), rt.binary(">", _u_paletteIndex, g.PALETTE_COUNT)):
            g.fragColor = inputColor
            return
        lum = rt.dot(rt.swizzle(inputColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        t = rt.binary("+", rt.binary("*", lum, _u_repeat, 1), rt.binary("*", _u_offset, rt.f(0.01), 1), 1)
        if rt.binary("==", _u_rotation, rt.unary("-", rt.i(1))):
            t = rt.binary("+", t, _u_time, 1)
        else:
            if rt.binary("==", _u_rotation, rt.i(1)):
                t = rt.binary("-", t, _u_time, 1)
        entry = g.PALETTES[int(rt.binary("-", _u_paletteIndex, rt.i(1), 1))]
        mode = rt.construct(1, rt.swizzle(rt.swizzle(entry, "amp"), "w"))
        paletteColor = cosinePalette__float_vec3_vec3_vec3_vec3(t, rt.swizzle(rt.swizzle(entry, "amp"), "xyz"), rt.swizzle(rt.swizzle(entry, "freq"), "xyz"), rt.swizzle(rt.swizzle(entry, "offset"), "xyz"), rt.swizzle(rt.swizzle(entry, "phase"), "xyz"))
        finalColor = rt.construct(3, 0.0)
        if rt.binary("==", mode, g.MODE_HSV):
            finalColor = hsv2rgb__vec3(paletteColor)
        else:
            if rt.binary("==", mode, g.MODE_OKLAB):
                finalColor = oklab2rgb__vec3(paletteColor)
            else:
                finalColor = paletteColor
        blendedColor = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), finalColor, _u_alpha, width=3)
        g.fragColor = rt.construct(4, blendedColor, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
