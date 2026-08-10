def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_colorMode = U.get("colorMode", 0)
    _u_colorCount = U.get("colorCount", 0)
    _u_positionMode = U.get("positionMode", 0)
    _u_color0 = U.get("color0", rt.construct(3, 0.0))
    _u_color1 = U.get("color1", rt.construct(3, 0.0))
    _u_color2 = U.get("color2", rt.construct(3, 0.0))
    _u_color3 = U.get("color3", rt.construct(3, 0.0))
    _u_color4 = U.get("color4", rt.construct(3, 0.0))
    _u_color5 = U.get("color5", rt.construct(3, 0.0))
    _u_color6 = U.get("color6", rt.construct(3, 0.0))
    _u_color7 = U.get("color7", rt.construct(3, 0.0))
    _u_pos0 = U.get("pos0", rt.f(0.0))
    _u_pos1 = U.get("pos1", rt.f(0.0))
    _u_pos2 = U.get("pos2", rt.f(0.0))
    _u_pos3 = U.get("pos3", rt.f(0.0))
    _u_pos4 = U.get("pos4", rt.f(0.0))
    _u_pos5 = U.get("pos5", rt.f(0.0))
    _u_pos6 = U.get("pos6", rt.f(0.0))
    _u_pos7 = U.get("pos7", rt.f(0.0))
    _u_repeat = U.get("repeat", rt.f(0.0))
    _u_offset = U.get("offset", rt.f(0.0))
    _u_smoothness = U.get("smoothness", rt.f(0.0))
    _u_alpha = U.get("alpha", rt.f(0.0))
    _u_rotation = U.get("rotation", 0)
    _u_time = U.get("time", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.swizzle(hsv, "x")
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        hp = rt.binary("*", h, rt.f(6.0), 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", hp, rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if rt.binary("<", hp, rt.f(1.0)):
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if rt.binary("<", hp, rt.f(2.0)):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if rt.binary("<", hp, rt.f(3.0)):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if rt.binary("<", hp, rt.f(4.0)):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if rt.binary("<", hp, rt.f(5.0)):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
        return rt.binary("+", rgb, rt.construct(3, m), 3, "float")
    def rgb2hsv__vec3(c):
        c = rt.copy(c, "float")
        cmax = rt.component_wise("max", rt.swizzle(c, "r"), rt.component_wise("max", rt.swizzle(c, "g"), rt.swizzle(c, "b"), width=1), width=1)
        cmin = rt.component_wise("min", rt.swizzle(c, "r"), rt.component_wise("min", rt.swizzle(c, "g"), rt.swizzle(c, "b"), width=1), width=1)
        delta = rt.binary("-", cmax, cmin, 1, "float")
        h = rt.f(0.0)
        if rt.binary(">", delta, rt.f(0.0)):
            if rt.binary("==", cmax, rt.swizzle(c, "r")):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", rt.swizzle(c, "g"), rt.swizzle(c, "b"), 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", cmax, rt.swizzle(c, "g")):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(c, "b"), rt.swizzle(c, "r"), 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(c, "r"), rt.swizzle(c, "g"), 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.binary("/", delta, cmax, 1, "float") if rt.binary(">", cmax, rt.f(0.0)) else rt.f(0.0))
        return rt.construct(3, h, s, cmax)
    def linear2srgb__vec3(lin):
        lin = rt.copy(lin, "float")
        low = rt.binary("*", lin, rt.f(12.92), 3, "float")
        high = rt.binary("-", rt.binary("*", rt.f(1.055), rt.component_wise("pow", rt.component_wise("max", lin, rt.construct(3, rt.f(0.0)), width=3), rt.construct(3, rt.binary("/", rt.f(1.0), rt.f(2.4), 1, "float")), width=3), 3, "float"), rt.f(0.055), 3, "float")
        return rt.component_wise("mix", high, low, rt.component_wise("step", lin, rt.construct(3, rt.f(0.0031308)), width=3), width=3)
    def srgb2linear__vec3(c):
        c = rt.copy(c, "float")
        low = rt.binary("/", c, rt.f(12.92), 3, "float")
        high = rt.component_wise("pow", rt.binary("/", rt.binary("+", c, rt.f(0.055), 3, "float"), rt.f(1.055), 3, "float"), rt.construct(3, rt.f(2.4)), width=3)
        return rt.component_wise("mix", high, low, rt.component_wise("step", c, rt.construct(3, rt.f(0.04045)), width=3), width=3)
    def oklab2linear__vec3(lab):
        lab = rt.copy(lab, "float")
        l_ = rt.binary("+", rt.binary("+", rt.swizzle(lab, "x"), rt.binary("*", rt.f(0.3963377774), rt.swizzle(lab, "y"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.2158037573), rt.swizzle(lab, "z"), 1, "float"), 1, "float")
        m_ = rt.binary("-", rt.binary("-", rt.swizzle(lab, "x"), rt.binary("*", rt.f(0.1055613458), rt.swizzle(lab, "y"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0638541728), rt.swizzle(lab, "z"), 1, "float"), 1, "float")
        s_ = rt.binary("-", rt.binary("-", rt.swizzle(lab, "x"), rt.binary("*", rt.f(0.0894841775), rt.swizzle(lab, "y"), 1, "float"), 1, "float"), rt.binary("*", rt.f(1.291485548), rt.swizzle(lab, "z"), 1, "float"), 1, "float")
        l = rt.binary("*", rt.binary("*", l_, l_, 1, "float"), l_, 1, "float")
        m = rt.binary("*", rt.binary("*", m_, m_, 1, "float"), m_, 1, "float")
        s = rt.binary("*", rt.binary("*", s_, s_, 1, "float"), s_, 1, "float")
        return rt.construct(3, rt.binary("+", rt.binary("-", rt.binary("*", rt.f(4.0767416621), l, 1, "float"), rt.binary("*", rt.f(3.3077115913), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.2309699292), s, 1, "float"), 1, "float"), rt.binary("-", rt.binary("+", rt.binary("*", rt.unary("-", rt.f(1.2684380046)), l, 1, "float"), rt.binary("*", rt.f(2.6097574011), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.3413193965), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("*", rt.unary("-", rt.f(0.0041960863)), l, 1, "float"), rt.binary("*", rt.f(0.7034186147), m, 1, "float"), 1, "float"), rt.binary("*", rt.f(1.707614701), s, 1, "float"), 1, "float"))
    def linear2oklab__vec3(lin):
        lin = rt.copy(lin, "float")
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.4122214708), rt.swizzle(lin, "r"), 1, "float"), rt.binary("*", rt.f(0.5363325363), rt.swizzle(lin, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0514459929), rt.swizzle(lin, "b"), 1, "float"), 1, "float")
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2119034982), rt.swizzle(lin, "r"), 1, "float"), rt.binary("*", rt.f(0.6806995451), rt.swizzle(lin, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.1073969566), rt.swizzle(lin, "b"), 1, "float"), 1, "float")
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883024619), rt.swizzle(lin, "r"), 1, "float"), rt.binary("*", rt.f(0.2817188376), rt.swizzle(lin, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.6299787005), rt.swizzle(lin, "b"), 1, "float"), 1, "float")
        l_ = rt.component_wise("pow", rt.component_wise("max", l, rt.f(0.0), width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1)
        m_ = rt.component_wise("pow", rt.component_wise("max", m, rt.f(0.0), width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1)
        s_ = rt.component_wise("pow", rt.component_wise("max", s, rt.f(0.0), width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1)
        return rt.construct(3, rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), l_, 1, "float"), rt.binary("*", rt.f(0.793617785), m_, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0040720468), s_, 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("*", rt.f(1.9779984951), l_, 1, "float"), rt.binary("*", rt.f(2.428592205), m_, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.4505937099), s_, 1, "float"), 1, "float"), rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.0259040371), l_, 1, "float"), rt.binary("*", rt.f(0.7827717662), m_, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.808675766), s_, 1, "float"), 1, "float"))
    def oklab2rgb__vec3(lab):
        lab = rt.copy(lab, "float")
        return rt.component_wise("clamp", linear2srgb__vec3(oklab2linear__vec3(lab)), rt.f(0.0), rt.f(1.0), width=3)
    def rgb2oklab__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        return linear2oklab__vec3(srgb2linear__vec3(rgb))
    def oklch2rgb__vec3(lch):
        lch = rt.copy(lch, "float")
        a = rt.binary("*", rt.swizzle(lch, "y"), rt.component_wise("cos", rt.binary("*", rt.swizzle(lch, "z"), g.TAU, 1, "float"), width=1), 1, "float")
        b = rt.binary("*", rt.swizzle(lch, "y"), rt.component_wise("sin", rt.binary("*", rt.swizzle(lch, "z"), g.TAU, 1, "float"), width=1), 1, "float")
        return rt.component_wise("clamp", linear2srgb__vec3(oklab2linear__vec3(rt.construct(3, rt.swizzle(lch, "x"), a, b))), rt.f(0.0), rt.f(1.0), width=3)
    def rgb2oklch__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        lab = rgb2oklab__vec3(rgb)
        C = rt.length(rt.swizzle(lab, "yz"))
        h = rt.component_wise("atan", rt.swizzle(lab, "z"), rt.swizzle(lab, "y"), width=1)
        return rt.construct(3, rt.swizzle(lab, "x"), C, rt.component_wise("fract", rt.binary("/", h, g.TAU, 1, "float"), width=1))
    def rgbToColorSpace__vec3_int(rgb, mode):
        rgb = rt.copy(rgb, "float")
        if rt.binary("==", mode, rt.i(1)):
            return rgb2hsv__vec3(rgb)
        if rt.binary("==", mode, rt.i(2)):
            return rgb2oklab__vec3(rgb)
        if rt.binary("==", mode, rt.i(3)):
            return rgb2oklch__vec3(rgb)
        return rgb
    def colorSpaceToRgb__vec3_int(color, mode):
        color = rt.copy(color, "float")
        if rt.binary("==", mode, rt.i(1)):
            return hsv2rgb__vec3(color)
        if rt.binary("==", mode, rt.i(2)):
            return oklab2rgb__vec3(color)
        if rt.binary("==", mode, rt.i(3)):
            return oklch2rgb__vec3(color)
        return color
    def getColor__int(index):
        if rt.binary("==", index, rt.i(0)):
            return _u_color0
        if rt.binary("==", index, rt.i(1)):
            return _u_color1
        if rt.binary("==", index, rt.i(2)):
            return _u_color2
        if rt.binary("==", index, rt.i(3)):
            return _u_color3
        if rt.binary("==", index, rt.i(4)):
            return _u_color4
        if rt.binary("==", index, rt.i(5)):
            return _u_color5
        if rt.binary("==", index, rt.i(6)):
            return _u_color6
        return _u_color7
    def getPosition__int_int(index, count):
        if rt.binary("==", _u_positionMode, rt.i(0)):
            return rt.binary("/", rt.construct(1, index), rt.construct(1, rt.binary("-", count, rt.i(1), 1, "int")), 1, "float")
        if rt.binary("==", index, rt.i(0)):
            return _u_pos0
        if rt.binary("==", index, rt.i(1)):
            return _u_pos1
        if rt.binary("==", index, rt.i(2)):
            return _u_pos2
        if rt.binary("==", index, rt.i(3)):
            return _u_pos3
        if rt.binary("==", index, rt.i(4)):
            return _u_pos4
        if rt.binary("==", index, rt.i(5)):
            return _u_pos5
        if rt.binary("==", index, rt.i(6)):
            return _u_pos6
        return _u_pos7
    def mixInColorSpace__vec3_vec3_float_int(a, b, f, mode):
        a = rt.copy(a, "float")
        b = rt.copy(b, "float")
        dh = rt.f(0.0)
        if rt.binary("==", mode, rt.i(1)):
            dh = rt.binary("-", rt.swizzle(b, "x"), rt.swizzle(a, "x"), 1, "float")
            if rt.binary(">", dh, rt.f(0.5)):
                dh = rt.binary("-", dh, rt.f(1.0), 1, "float")
            if rt.binary("<", dh, rt.unary("-", rt.f(0.5))):
                dh = rt.binary("+", dh, rt.f(1.0), 1, "float")
            return rt.construct(3, rt.component_wise("fract", rt.binary("+", rt.swizzle(a, "x"), rt.binary("*", dh, f, 1, "float"), 1, "float"), width=1), rt.component_wise("mix", rt.swizzle(a, "y"), rt.swizzle(b, "y"), f, width=1), rt.component_wise("mix", rt.swizzle(a, "z"), rt.swizzle(b, "z"), f, width=1))
        else:
            if rt.binary("==", mode, rt.i(3)):
                dh = rt.binary("-", rt.swizzle(b, "z"), rt.swizzle(a, "z"), 1, "float")
                if rt.binary(">", dh, rt.f(0.5)):
                    dh = rt.binary("-", dh, rt.f(1.0), 1, "float")
                if rt.binary("<", dh, rt.unary("-", rt.f(0.5))):
                    dh = rt.binary("+", dh, rt.f(1.0), 1, "float")
                return rt.construct(3, rt.component_wise("mix", rt.swizzle(a, "x"), rt.swizzle(b, "x"), f, width=1), rt.component_wise("mix", rt.swizzle(a, "y"), rt.swizzle(b, "y"), f, width=1), rt.component_wise("fract", rt.binary("+", rt.swizzle(a, "z"), rt.binary("*", dh, f, 1, "float"), 1, "float"), width=1))
        return rt.component_wise("mix", a, b, f, width=3)
    def sampleColorArray__float_int_float(t, count, smoothAmount):
        t = rt.component_wise("clamp", t, rt.f(0.0), rt.f(1.0), width=1)
        mode = _u_colorMode
        result = rgbToColorSpace__vec3_int(getColor__int(rt.i(0)), mode)
        i = rt.i(1)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, count)):
                break
            boundary = rt.f(0.0)
            bw = rt.f(0.0)
            pPrev = rt.f(0.0)
            pCurr = rt.f(0.0)
            if rt.binary("==", _u_positionMode, rt.i(0)):
                boundary = rt.binary("/", rt.construct(1, i), rt.construct(1, count), 1, "float")
                bw = rt.binary("/", rt.binary("*", smoothAmount, rt.f(0.5), 1, "float"), rt.construct(1, count), 1, "float")
            else:
                pPrev = getPosition__int_int(rt.binary("-", i, rt.i(1), 1, "int"), count)
                pCurr = getPosition__int_int(i, count)
                boundary = rt.binary("*", rt.binary("+", pPrev, pCurr, 1, "float"), rt.f(0.5), 1, "float")
                bw = rt.binary("*", rt.binary("*", smoothAmount, rt.binary("-", pCurr, pPrev, 1, "float"), 1, "float"), rt.f(0.25), 1, "float")
            blend = rt.component_wise("smoothstep", rt.binary("-", boundary, bw, 1, "float"), rt.binary("+", boundary, bw, 1, "float"), t, width=1)
            nextColor = rgbToColorSpace__vec3_int(getColor__int(i), mode)
            result[:] = mixInColorSpace__vec3_vec3_float_int(result, nextColor, blend, mode)
        bw = rt.f(0.0)
        if rt.binary(">", smoothAmount, rt.f(0.0)):
            bw = rt.f(0.0)
            pLast = rt.f(0.0)
            pFirst = rt.f(0.0)
            gap = rt.f(0.0)
            if rt.binary("==", _u_positionMode, rt.i(0)):
                bw = rt.binary("/", rt.binary("*", smoothAmount, rt.f(0.5), 1, "float"), rt.construct(1, count), 1, "float")
            else:
                pLast = getPosition__int_int(rt.binary("-", count, rt.i(1), 1, "int"), count)
                pFirst = getPosition__int_int(rt.i(0), count)
                gap = rt.binary("+", rt.binary("-", rt.f(1.0), pLast, 1, "float"), pFirst, 1, "float")
                bw = rt.binary("*", rt.binary("*", smoothAmount, gap, 1, "float"), rt.f(0.25), 1, "float")
            d = rt.f(0.0)
            wrapFactor = rt.f(0.0)
            lastColor = rt.construct(3, 0.0)
            firstColor = rt.construct(3, 0.0)
            wrapColor = rt.construct(3, 0.0)
            wrapMask = rt.f(0.0)
            if rt.binary(">", bw, rt.f(0.0)):
                d = (rt.binary("-", t, rt.f(1.0), 1, "float") if rt.binary(">", t, rt.f(0.5)) else t)
                wrapFactor = rt.component_wise("smoothstep", rt.unary("-", bw), bw, d, width=1)
                lastColor = rgbToColorSpace__vec3_int(getColor__int(rt.binary("-", count, rt.i(1), 1, "int")), mode)
                firstColor = rgbToColorSpace__vec3_int(getColor__int(rt.i(0)), mode)
                wrapColor = mixInColorSpace__vec3_vec3_float_int(lastColor, firstColor, wrapFactor, mode)
                wrapMask = rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.f(0.0), bw, rt.component_wise("abs", d, width=1), width=1), 1, "float")
                result[:] = mixInColorSpace__vec3_vec3_float_int(result, wrapColor, wrapMask, mode)
        return colorSpaceToRgb__vec3_int(result, mode)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.construct(2, rt.texture_size(_u_inputTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), texSize, 2, "float")
        inputColor = rt.texture(_u_inputTex, uv)
        lum = rt.dot(rt.swizzle(inputColor, "rgb"), rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
        t = rt.binary("+", rt.binary("*", rt.binary("*", lum, rt.binary("-", rt.f(1.0), rt.f(0.0001), 1, "float"), 1, "float"), _u_repeat, 1, "float"), _u_offset, 1, "float")
        if rt.binary("==", _u_rotation, rt.unary("-", rt.i(1))):
            t = rt.binary("+", t, _u_time, 1, "float")
        else:
            if rt.binary("==", _u_rotation, rt.i(1)):
                t = rt.binary("-", t, _u_time, 1, "float")
        t = rt.component_wise("fract", t, width=1)
        gradientColor = sampleColorArray__float_int_float(t, _u_colorCount, _u_smoothness)
        blendedColor = rt.component_wise("mix", rt.swizzle(inputColor, "rgb"), gradientColor, _u_alpha, width=3)
        g.fragColor[:] = rt.construct(4, blendedColor, rt.swizzle(inputColor, "a"))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
