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
    _u_inputColor = U.get("inputColor", rt.construct(3, 0.0))
    _u_blendMode = U.get("blendMode", 0)
    _u_range = U.get("range", rt.f(0.0))
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
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
    def desaturate__vec3(color):
        color = rt.copy(color, "float")
        c = rgb2hsv__vec3(color)
        c = rt.assign_swizzle(c, "g", rt.f(0.0))
        return hsv2rgb__vec3(c)
    def blend__vec3_vec3(color1, color2):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        color = rt.construct(3, rt.f(0.0))
        cut = rt.binary("*", _u_range, rt.f(0.01), 1, "float")
        if rt.binary("==", _u_blendMode, rt.i(0)):
            if rt.binary(">", rt.distance(_u_inputColor, color1), rt.binary("*", _u_range, rt.f(0.01), 1, "float")):
                color1 = desaturate__vec3(color1)
            if rt.binary(">", rt.distance(_u_inputColor, color2), rt.binary("*", _u_range, rt.f(0.01), 1, "float")):
                color2 = desaturate__vec3(color2)
            color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
        else:
            if rt.binary("==", _u_blendMode, rt.i(1)):
                if rt.binary("<=", rt.distance(_u_inputColor, color1), rt.binary("*", _u_range, rt.f(0.01), 1, "float")):
                    color = color2
                else:
                    color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
            else:
                if rt.binary("==", _u_blendMode, rt.i(2)):
                    if rt.binary("<=", rt.distance(_u_inputColor, color2), rt.binary("*", _u_range, rt.f(0.01), 1, "float")):
                        color = color1
                    else:
                        color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                else:
                    if rt.binary("==", _u_blendMode, rt.i(3)):
                        c = rt.binary("-", rt.f(1.0), rt.component_wise("step", cut, rt.swizzle(desaturate__vec3(color2), "r"), width=1), 1, "float")
                        color2 = rt.component_wise("mix", color1, rt.construct(3, rt.f(0.0)), c, width=3)
                        color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                    else:
                        if rt.binary("==", _u_blendMode, rt.i(4)):
                            c = rt.binary("-", rt.f(1.0), rt.component_wise("step", cut, color2, width=3), 3, "float")
                            color2 = rt.component_wise("mix", color1, rt.construct(3, rt.f(0.0)), c, width=3)
                            color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                        else:
                            if rt.binary("==", _u_blendMode, rt.i(5)):
                                c = rt.swizzle(rgb2hsv__vec3(color2), "r")
                                color2 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                            else:
                                if rt.binary("==", _u_blendMode, rt.i(6)):
                                    c = rt.swizzle(rgb2hsv__vec3(color2), "g")
                                    color2 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                    color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                else:
                                    if rt.binary("==", _u_blendMode, rt.i(7)):
                                        c = rt.swizzle(rgb2hsv__vec3(color2), "b")
                                        color2 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                        color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                    else:
                                        if rt.binary("==", _u_blendMode, rt.i(8)):
                                            c = rt.binary("-", rt.f(1.0), rt.component_wise("step", cut, rt.swizzle(desaturate__vec3(color1), "r"), width=1), 1, "float")
                                            color1 = rt.component_wise("mix", color2, rt.construct(3, rt.f(0.0)), c, width=3)
                                            color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                        else:
                                            if rt.binary("==", _u_blendMode, rt.i(9)):
                                                c = rt.binary("-", rt.f(1.0), rt.component_wise("step", cut, color1, width=3), 3, "float")
                                                color1 = rt.component_wise("mix", color2, rt.construct(3, rt.f(0.0)), c, width=3)
                                                color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                            else:
                                                if rt.binary("==", _u_blendMode, rt.i(10)):
                                                    c = rt.swizzle(rgb2hsv__vec3(color1), "r")
                                                    color1 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                                    color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                                else:
                                                    if rt.binary("==", _u_blendMode, rt.i(11)):
                                                        c = rt.swizzle(rgb2hsv__vec3(color1), "g")
                                                        color1 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                                        color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                                    else:
                                                        if rt.binary("==", _u_blendMode, rt.i(12)):
                                                            c = rt.swizzle(rgb2hsv__vec3(color1), "b")
                                                            color1 = rt.component_wise("mix", color1, color2, rt.binary("*", c, cut, 1, "float"), width=3)
                                                            color = rt.component_wise("mix", color2, color1, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                                        else:
                                                            if rt.binary("==", _u_blendMode, rt.i(13)):
                                                                color2 = rt.component_wise("mix", color1, color2, cut, width=3)
                                                                color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                                            else:
                                                                if rt.binary("==", _u_blendMode, rt.i(14)):
                                                                    c = rt.component_wise("step", cut, rt.component_wise("mix", color1, color2, rt.f(0.5), width=3), width=3)
                                                                    color2 = rt.component_wise("mix", color1, color2, c, width=3)
                                                                    color = rt.component_wise("mix", color1, color2, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
                                                                else:
                                                                    if rt.binary("==", _u_blendMode, rt.i(15)):
                                                                        c1 = rt.component_wise("smoothstep", color1, rt.construct(3, cut), color2, width=3)
                                                                        c2 = rt.component_wise("smoothstep", color2, rt.construct(3, cut), color1, width=3)
                                                                        color = rt.component_wise("mix", rt.swizzle(c1, "brg"), rt.swizzle(c2, "gbr"), rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=3)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color1 = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        color2 = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        color = rt.assign_swizzle(color, "rgb", blend__vec3_vec3(rt.swizzle(color1, "rgb"), rt.swizzle(color2, "rgb")))
        color = rt.assign_swizzle(color, "a", rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
