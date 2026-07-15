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
    _u_smoothness = U["smoothness"]
    _u_rotation = U["rotation"]
    _u_offset = U["offset"]
    _u_repeat = U["repeat"]
    _u_alpha = U["alpha"]
    _u_time = U["time"]
    g.PALETTE_COUNT = rt.i(21)
    def sampleHistoricPalette__float_float_float(pal, lum, smoothAmount):
        t1 = rt.f(0.2)
        t2 = rt.f(0.4)
        t3 = rt.f(0.6)
        t4 = rt.f(0.8)
        blendWidth = rt.binary("*", smoothAmount, rt.f(0.1), 1)
        b1 = rt.component_wise("smoothstep", rt.binary("-", t1, blendWidth, 1), rt.binary("+", t1, blendWidth, 1), lum, width=1)
        b2 = rt.component_wise("smoothstep", rt.binary("-", t2, blendWidth, 1), rt.binary("+", t2, blendWidth, 1), lum, width=1)
        b3 = rt.component_wise("smoothstep", rt.binary("-", t3, blendWidth, 1), rt.binary("+", t3, blendWidth, 1), lum, width=1)
        b4 = rt.component_wise("smoothstep", rt.binary("-", t4, blendWidth, 1), rt.binary("+", t4, blendWidth, 1), lum, width=1)
        result = rt.component_wise("mix", rt.swizzle(pal, "color1"), rt.swizzle(pal, "color2"), b1, width=6)
        result = rt.component_wise("mix", result, rt.swizzle(pal, "color3"), b2, width=6)
        result = rt.component_wise("mix", result, rt.swizzle(pal, "color4"), b3, width=6)
        result = rt.component_wise("mix", result, rt.swizzle(pal, "color5"), b4, width=6)
        if rt.binary(">", blendWidth, rt.f(0.0)):
            d = (rt.binary("-", lum, rt.f(1.0), 1) if rt.binary(">", lum, rt.f(0.5)) else lum)
            wrapFactor = rt.component_wise("smoothstep", rt.unary("-", blendWidth), blendWidth, d, width=1)
            wrapColor = rt.component_wise("mix", rt.swizzle(pal, "color5"), rt.swizzle(pal, "color1"), wrapFactor, width=6)
            wrapMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), blendWidth, rt.component_wise("abs", d, width=1), width=1), 1)
            result = rt.component_wise("mix", result, wrapColor, wrapMask, width=3)
        return result
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2)
        inputColor = rt.texture(_u_inputTex, uv)
        idx = rt.component_wise("clamp", _u_paletteIndex, rt.i(0), rt.binary("-", g.PALETTE_COUNT, rt.i(1), 1), width=1)
        lum = rt.dot(rt.swizzle(inputColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        t = rt.binary("+", rt.binary("*", rt.binary("*", lum, rt.binary("-", rt.f(1.0), rt.f(1e-4), 1), 1), _u_repeat, 1), rt.binary("*", _u_offset, rt.f(0.01), 1), 1)
        if rt.binary("==", _u_rotation, rt.unary("-", rt.i(1))):
            t = rt.binary("+", t, _u_time, 1)
        else:
            if rt.binary("==", _u_rotation, rt.i(1)):
                t = rt.binary("-", t, _u_time, 1)
        t = rt.component_wise("fract", t, width=1)
        pal = g.PALETTES[int(idx)]
        paletteColor = sampleHistoricPalette__float_float_float(pal, t, _u_smoothness)
        blendedColor = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), paletteColor, _u_alpha, width=3)
        g.fragColor = rt.construct(4, blendedColor, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
