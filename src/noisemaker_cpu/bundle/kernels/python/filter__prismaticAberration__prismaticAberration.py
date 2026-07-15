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
    _u_time = U["time"]
    _u_aberrationAmt = U["aberrationAmt"]
    _u_hueRotation = U["hueRotation"]
    _u_hueRange = U["hueRange"]
    _u_modulate = U["modulate"]
    _u_saturation = U["saturation"]
    _u_passthru = U["passthru"]
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1), rt.binary("-", value, inMin, 1), 1), rt.binary("-", inMax, inMin, 1), 1), 1)
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv)
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1)
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1), rt.f(2.0), width=1), rt.f(1.0), 1), width=1), 1), 1)
        m = rt.binary("-", v, c, 1)
        rgb = rt.construct(3, 0.0)
        if rt.binary("&&", rt.binary("<=", rt.f(0.0), h), rt.binary("<", h, rt.binary("/", rt.f(1.0), rt.f(6.0), 1))):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1), h), rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1))):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1), h), rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1))):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1), h), rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1))):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1), h), rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1))):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            if rt.binary("&&", rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1), h), rt.binary("<", h, rt.f(1.0))):
                                rgb = rt.construct(3, c, rt.f(0.0), x)
                            else:
                                rgb = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(0.0))
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3)
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb)
        r = rt.swizzle(rgb, "r")
        g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        _max = rt.component_wise("max", r, rt.component_wise("max", g, b, width=1), width=1)
        _min = rt.component_wise("min", r, rt.component_wise("min", g, b, width=1), width=1)
        delta = rt.binary("-", _max, _min, 1)
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", _max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", g, b, 1), delta, 1), rt.f(6.0), width=1), rt.f(6.0), 1)
            else:
                if rt.binary("==", _max, g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1), delta, 1), rt.f(2.0), 1), rt.f(6.0), 1)
                else:
                    if rt.binary("==", _max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, g, 1), delta, 1), rt.f(4.0), 1), rt.f(6.0), 1)
        s = (rt.f(0.0) if rt.binary("==", _max, rt.f(0.0)) else rt.binary("/", delta, _max, 1))
        v = _max
        return rt.construct(3, h, s, v)
    def saturate__vec3(color):
        color = rt.copy(color)
        sat = map__float_float_float_float_float(_u_saturation, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        avg = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(color, "r"), rt.swizzle(color, "g"), 1), rt.swizzle(color, "b"), 1), rt.f(3.0), 1)
        color = rt.binary("-", color, rt.binary("*", rt.binary("-", avg, color, 3), sat, 3), 3)
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        globalAspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        diff = rt.binary("-", rt.construct(2, rt.binary("*", rt.f(0.5), globalAspect, 1), rt.f(0.5)), rt.construct(2, rt.binary("*", rt.swizzle(globalUV, "x"), globalAspect, 1), rt.swizzle(globalUV, "y")), 2)
        centerDist = rt.length(diff)
        lensedCoords = uv
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberrationAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.05)), centerDist, 1), rt.f(3.14159265359), 1), rt.f(0.5), 1)
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, rt.texture_size(_u_inputTex)), 2)
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), rt.swizzle(lensedCoords, "x"), width=1)
        redUV = rt.construct(2, redOffset, rt.swizzle(lensedCoords, "y"))
        redLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", redUV, _u_fullResolution, 2), _u_tileOffset, 2), texelSize, 2)
        red = rt.texture(_u_inputTex, redLocalUV)
        greenLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", lensedCoords, _u_fullResolution, 2), _u_tileOffset, 2), texelSize, 2)
        green = rt.texture(_u_inputTex, greenLocalUV)
        blueOffset = rt.component_wise("mix", rt.swizzle(lensedCoords, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), width=1)
        blueUV = rt.construct(2, blueOffset, rt.swizzle(lensedCoords, "y"))
        blueLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", blueUV, _u_fullResolution, 2), _u_tileOffset, 2), texelSize, 2)
        blue = rt.texture(_u_inputTex, blueLocalUV)
        hsv = rt.construct(3, rt.f(1.0))
        t = (_u_time if _u_modulate else rt.f(0.0))
        color = rt.binary("*", rt.construct(4, rt.length(rt.binary("-", rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(color, "a")), green, 4))), green, 4)
        color = rt.assign_swizzle(color, "a", rt.swizzle(green, "a"))
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv[int(rt.i(0))] = rt.component_wise("fract", rt.binary("+", rt.binary("*", rt.binary("+", rt.binary("+", hsv[int(rt.i(0))], rt.f(0.125), 1), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1), 1), 1), rt.binary("+", rt.f(2.0), rt.binary("*", _u_hueRange, rt.f(0.05), 1), 1), 1), t, 1), width=1)
        hsv[int(rt.i(1))] = rt.f(1.0)
        green = rt.assign_swizzle(green, "rgb", rt.binary("*", saturate__vec3(rt.swizzle(green, "rgb")), map__float_float_float_float_float(_u_passthru, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0)), 3))
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("min", rt.binary("+", rt.swizzle(green, "rgb"), hsv2rgb__vec3(hsv), 3), rt.f(1.0), width=3))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
