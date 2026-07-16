def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_blendMode = U.get("blendMode", 0)
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    _u_refractAAmt = U.get("refractAAmt", rt.f(0.0))
    _u_refractBAmt = U.get("refractBAmt", rt.f(0.0))
    _u_refractADir = U.get("refractADir", rt.f(0.0))
    _u_refractBDir = U.get("refractBDir", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def blendOverlay__float_float(a, b):
        return (rt.binary("*", rt.binary("*", rt.f(2.0), a, 1, "float"), b, 1, "float") if rt.binary("<", a, rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), b, 1, "float"), 1, "float"), 1, "float"))
    def blendSoftLight__float_float(base, blend):
        return (rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), blend, 1, "float"), rt.binary("*", rt.binary("*", base, base, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), blend, 1, "float"), 1, "float"), 1, "float"), 1, "float") if rt.binary("<", blend, rt.f(0.5)) else rt.binary("+", rt.binary("*", rt.component_wise("sqrt", base, width=1), rt.binary("-", rt.binary("*", rt.f(2.0), blend, 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), rt.binary("-", rt.f(1.0), blend, 1, "float"), 1, "float"), 1, "float"))
    def cloak__vec2(st):
        st = rt.copy(st, "float")
        m = map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        ra = map__float_float_float_float_float(_u_refractAAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
        rb = map__float_float_float_float_float(_u_refractBAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
        leftColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        rightColor = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        leftUV = rt.construct(2, st)
        rightLen = rt.length(rt.swizzle(rightColor, "rgb"))
        leftUV = rt.assign_swizzle(leftUV, "x", rt.binary("+", rt.swizzle(leftUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
        leftUV = rt.assign_swizzle(leftUV, "y", rt.binary("+", rt.swizzle(leftUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
        leftLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", leftUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        leftRefracted = rt.texture(_u_inputTex, rt.component_wise("fract", leftLocalUV, width=2))
        rightUV = rt.construct(2, st)
        leftLen = rt.length(rt.swizzle(leftColor, "rgb"))
        rightUV = rt.assign_swizzle(rightUV, "x", rt.binary("+", rt.swizzle(rightUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
        rightUV = rt.assign_swizzle(rightUV, "y", rt.binary("+", rt.swizzle(rightUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
        rightLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", rightUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")
        rightRefracted = rt.texture(_u_tex, rt.component_wise("fract", rightLocalUV, width=2))
        leftReflected = rt.component_wise("min", rt.binary("/", rt.binary("*", rightRefracted, rightColor, 4, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", leftRefracted, leftColor, 4, "float"), 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        rightReflected = rt.component_wise("min", rt.binary("/", rt.binary("*", leftRefracted, leftColor, 4, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rightRefracted, rightColor, 4, "float"), 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        left = rt.construct(4, rt.f(1.0))
        right = rt.construct(4, rt.f(1.0))
        if rt.binary("<", _u_mixAmt, rt.f(0.0)):
            left = rt.component_wise("mix", leftRefracted, leftReflected, map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), width=4)
            right = rightReflected
        else:
            left = leftReflected
            right = rt.component_wise("mix", rightRefracted, rightRefracted, map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=4)
        return rt.component_wise("mix", left, right, m, width=4)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if (bool(rt.binary("<=", rt.f(0.0), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")))):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                rgb = rt.construct(3, c, rt.f(0.0), x)
                            else:
                                rgb = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3, "float")
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = rt.swizzle(rgb, "r")
        _g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        max = rt.component_wise("max", r, rt.component_wise("max", _g, b, width=1), width=1)
        min = rt.component_wise("min", r, rt.component_wise("min", _g, b, width=1), width=1)
        delta = rt.binary("-", max, min, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", _g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", max, _g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, _g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", max, rt.f(0.0)) else rt.binary("/", delta, max, 1, "float"))
        v = max
        return rt.construct(3, h, s, v)
    def blend__vec4_vec4_int_float(color1, color2, mode, factor):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        color = rt.construct(4, 0.0)
        middle = rt.construct(4, 0.0)
        amt = map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        a = rt.construct(4, rt.f(1.0))
        b = rt.construct(4, rt.f(1.0))
        if rt.binary(">=", mode, rt.i(1000)):
            a = rt.assign_swizzle(a, "rgb", rgb2hsv__vec3(rt.swizzle(color1, "rgb")))
            b = rt.assign_swizzle(b, "rgb", rgb2hsv__vec3(rt.swizzle(color2, "rgb")))
        if rt.binary("==", mode, rt.i(0)):
            middle = rt.component_wise("min", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), width=4)
        else:
            if rt.binary("==", mode, rt.i(1)):
                if rt.binary("<", _u_mixAmt, rt.f(0.0)):
                    return rt.swizzle(rt.component_wise("mix", color1, rt.binary("+", rt.binary("*", color2, rt.construct(4, rt.binary("-", rt.f(1.0), rt.swizzle(color1, "a"), 1, "float")), 4, "float"), rt.binary("*", color1, rt.construct(4, rt.swizzle(color1, "a")), 4, "float"), 4, "float"), map__float_float_float_float_float(_u_mixAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), width=4), "rgb")
                else:
                    return rt.swizzle(rt.component_wise("mix", rt.binary("+", rt.binary("*", color1, rt.construct(4, rt.binary("-", rt.f(1.0), rt.swizzle(color2, "a"), 1, "float")), 4, "float"), rt.binary("*", color2, rt.construct(4, rt.swizzle(color2, "a")), 4, "float"), 4, "float"), color2, map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=4), "rgb")
            else:
                if rt.binary("==", mode, rt.i(2)):
                    middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(0.0))) else rt.component_wise("max", rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", rt.f(1.0), color1, 4, "float"), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(0.0)), width=4))
                else:
                    if rt.binary("==", mode, rt.i(3)):
                        middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", color1, rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                    else:
                        if rt.binary("==", mode, rt.i(4)):
                            middle = rt.component_wise("min", color1, color2, width=4)
                        else:
                            if rt.binary("==", mode, rt.i(5)):
                                middle = rt.component_wise("abs", rt.binary("-", color1, color2, 4, "float"), width=4)
                            else:
                                if rt.binary("==", mode, rt.i(6)):
                                    middle = rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), color1, 4, "float"), color2, 4, "float"), 4, "float")
                                else:
                                    if rt.binary("==", mode, rt.i(7)):
                                        middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color1, color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                    else:
                                        if rt.binary("==", mode, rt.i(8)):
                                            middle = rt.construct(4, blendOverlay__float_float(rt.swizzle(color2, "r"), rt.swizzle(color1, "r")), blendOverlay__float_float(rt.swizzle(color2, "g"), rt.swizzle(color1, "g")), blendOverlay__float_float(rt.swizzle(color2, "b"), rt.swizzle(color1, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                        else:
                                            if rt.binary("==", mode, rt.i(9)):
                                                middle = rt.component_wise("max", color1, color2, width=4)
                                            else:
                                                if rt.binary("==", mode, rt.i(10)):
                                                    middle = rt.component_wise("mix", color1, color2, rt.f(0.5), width=4)
                                                else:
                                                    if rt.binary("==", mode, rt.i(11)):
                                                        middle = rt.binary("*", color1, color2, 4, "float")
                                                    else:
                                                        if rt.binary("==", mode, rt.i(12)):
                                                            middle = rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4, "float"), color2, 4, "float"), width=4), 4, "float")
                                                        else:
                                                            if rt.binary("==", mode, rt.i(13)):
                                                                middle = rt.construct(4, blendOverlay__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendOverlay__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendOverlay__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                                            else:
                                                                if rt.binary("==", mode, rt.i(14)):
                                                                    middle = rt.binary("+", rt.binary("-", rt.component_wise("min", color1, color2, width=4), rt.component_wise("max", color1, color2, width=4), 4, "float"), rt.construct(4, rt.f(1.0)), 4, "float")
                                                                else:
                                                                    if rt.binary("==", mode, rt.i(15)):
                                                                        middle = (color1 if rt.binary("==", color1, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color2, color2, 4, "float"), rt.binary("-", rt.f(1.0), color1, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                                                    else:
                                                                        if rt.binary("==", mode, rt.i(16)):
                                                                            middle = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), 4, "float")
                                                                        else:
                                                                            if rt.binary("==", mode, rt.i(17)):
                                                                                middle = rt.construct(4, blendSoftLight__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendSoftLight__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendSoftLight__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                                                            else:
                                                                                if rt.binary("==", mode, rt.i(18)):
                                                                                    middle = rt.component_wise("max", rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), 4, "float"), rt.f(0.0), width=4)
                                                                                else:
                                                                                    if rt.binary("==", mode, rt.i(1000)):
                                                                                        middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(b, "r"), rt.swizzle(a, "g"), rt.swizzle(a, "b"))))
                                                                                    else:
                                                                                        if rt.binary("==", mode, rt.i(1001)):
                                                                                            middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(a, "r"), rt.swizzle(b, "g"), rt.swizzle(b, "b"))))
                                                                                        else:
                                                                                            if rt.binary("==", mode, rt.i(1002)):
                                                                                                middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(a, "r"), rt.swizzle(b, "g"), rt.swizzle(a, "b"))))
                                                                                            else:
                                                                                                if rt.binary("==", mode, rt.i(1003)):
                                                                                                    middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(b, "r"), rt.swizzle(a, "g"), rt.swizzle(b, "b"))))
                                                                                                else:
                                                                                                    if rt.binary("==", mode, rt.i(1004)):
                                                                                                        middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(a, "r"), rt.swizzle(a, "g"), rt.swizzle(b, "b"))))
                                                                                                    else:
                                                                                                        if rt.binary("==", mode, rt.i(1005)):
                                                                                                            middle = rt.assign_swizzle(middle, "rgb", hsv2rgb__vec3(rt.construct(3, rt.swizzle(b, "r"), rt.swizzle(b, "g"), rt.swizzle(a, "b"))))
        if rt.binary(">=", mode, rt.i(1000)):
            middle = rt.assign_swizzle(middle, "a", rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
        if rt.binary("==", factor, rt.f(0.5)):
            color = middle
        else:
            if rt.binary("<", factor, rt.f(0.5)):
                factor = map__float_float_float_float_float(amt, rt.f(0.0), rt.f(0.5), rt.f(0.0), rt.f(1.0))
                color = rt.component_wise("mix", color1, middle, factor, width=4)
            else:
                if rt.binary(">", factor, rt.f(0.5)):
                    factor = map__float_float_float_float_float(amt, rt.f(0.5), rt.f(1.0), rt.f(0.0), rt.f(1.0))
                    color = rt.component_wise("mix", middle, color2, factor, width=4)
        return rt.swizzle(color, "rgb")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        if rt.binary("==", _u_blendMode, rt.i(100)):
            color = cloak__vec2(st)
        else:
            ra = map__float_float_float_float_float(_u_refractAAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
            rb = map__float_float_float_float_float(_u_refractBAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
            leftColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
            rightColor = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
            leftUV = rt.construct(2, st)
            rightLen = rt.binary("+", rt.length(rt.swizzle(rightColor, "rgb")), rt.binary("/", _u_refractADir, rt.f(360.0), 1, "float"), 1, "float")
            leftUV = rt.assign_swizzle(leftUV, "x", rt.binary("+", rt.swizzle(leftUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
            leftUV = rt.assign_swizzle(leftUV, "y", rt.binary("+", rt.swizzle(leftUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
            leftLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", leftUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
            color1 = rt.texture(_u_inputTex, rt.component_wise("fract", leftLocalUV, width=2))
            rightUV = rt.construct(2, st)
            leftLen = rt.binary("+", rt.length(rt.swizzle(leftColor, "rgb")), rt.binary("/", _u_refractBDir, rt.f(360.0), 1, "float"), 1, "float")
            rightUV = rt.assign_swizzle(rightUV, "x", rt.binary("+", rt.swizzle(rightUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
            rightUV = rt.assign_swizzle(rightUV, "y", rt.binary("+", rt.swizzle(rightUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
            rightLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", rightUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float")
            color2 = rt.texture(_u_tex, rt.component_wise("fract", rightLocalUV, width=2))
            color = rt.assign_swizzle(color, "rgb", blend__vec4_vec4_int_float(color1, color2, _u_blendMode, _u_mixAmt))
            color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
