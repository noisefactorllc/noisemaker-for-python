def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_aberrationAmt = U.get("aberrationAmt", rt.f(0.0))
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_hueRange = U.get("hueRange", rt.f(0.0))
    _u_modulate = U.get("modulate", False)
    _u_saturation = U.get("saturation", rt.f(0.0))
    _u_passthru = U.get("passthru", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
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
    def saturate__vec3(color):
        color = rt.copy(color, "float")
        sat = map__float_float_float_float_float(_u_saturation, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        avg = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(color, "r"), rt.swizzle(color, "g"), 1, "float"), rt.swizzle(color, "b"), 1, "float"), rt.f(3.0), 1, "float")
        color = rt.binary("-", color, rt.binary("*", rt.binary("-", avg, color, 3, "float"), sat, 3, "float"), 3, "float")
        return color
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        globalAspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        diff = rt.binary("-", rt.construct(2, rt.binary("*", rt.f(0.5), globalAspect, 1, "float"), rt.f(0.5)), rt.construct(2, rt.binary("*", rt.swizzle(globalUV, "x"), globalAspect, 1, "float"), rt.swizzle(globalUV, "y")), 2, "float")
        centerDist = rt.length(diff)
        lensedCoords = uv
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberrationAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.05)), centerDist, 1, "float"), rt.f(3.14159265359), 1, "float"), rt.f(0.5), 1, "float")
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), rt.swizzle(lensedCoords, "x"), width=1)
        redUV = rt.construct(2, redOffset, rt.swizzle(lensedCoords, "y"))
        redLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", redUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), texelSize, 2, "float")
        red = rt.texture(_u_inputTex, redLocalUV)
        greenLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", lensedCoords, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), texelSize, 2, "float")
        green = rt.texture(_u_inputTex, greenLocalUV)
        blueOffset = rt.component_wise("mix", rt.swizzle(lensedCoords, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), width=1)
        blueUV = rt.construct(2, blueOffset, rt.swizzle(lensedCoords, "y"))
        blueLocalUV = rt.binary("*", rt.binary("-", rt.binary("*", blueUV, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), texelSize, 2, "float")
        blue = rt.texture(_u_inputTex, blueLocalUV)
        hsv = rt.construct(3, rt.f(1.0))
        t = (_u_time if _u_modulate else rt.f(0.0))
        color = rt.binary("*", rt.construct(4, rt.length(rt.binary("-", rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(color, "a")), green, 4, "float"))), green, 4, "float")
        color = rt.assign_swizzle(color, "a", rt.swizzle(green, "a"))
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv[int(rt.i(0))] = rt.component_wise("fract", rt.binary("+", rt.binary("*", rt.binary("+", rt.binary("+", hsv[int(rt.i(0))], rt.f(0.125), 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"), rt.binary("+", rt.f(2.0), rt.binary("*", _u_hueRange, rt.f(0.05), 1, "float"), 1, "float"), 1, "float"), t, 1, "float"), width=1)
        hsv[int(rt.i(1))] = rt.f(1.0)
        green = rt.assign_swizzle(green, "rgb", rt.binary("*", saturate__vec3(rt.swizzle(green, "rgb")), map__float_float_float_float_float(_u_passthru, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0)), 3, "float"))
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("min", rt.binary("+", rt.swizzle(green, "rgb"), hsv2rgb__vec3(hsv), 3, "float"), rt.f(1.0), width=3))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
