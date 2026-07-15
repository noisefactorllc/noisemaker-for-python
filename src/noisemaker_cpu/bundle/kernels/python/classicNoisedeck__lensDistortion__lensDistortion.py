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
    _u_aspectLens = U["aspectLens"]
    _u_shape = U["shape"]
    _u_tint = U["tint"]
    _u_alpha = U["alpha"]
    _u_vignetteAmt = U["vignetteAmt"]
    _u_distortion = U["distortion"]
    _u_speed = U["speed"]
    _u_loopScale = U["loopScale"]
    _u_aberration = U["aberration"]
    _u_hueRotation = U["hueRotation"]
    _u_hueRange = U["hueRange"]
    _u_mode = U["mode"]
    _u_modulate = U["modulate"]
    _u_blendMode = U["blendMode"]
    _u_saturation = U["saturation"]
    _u_passthru = U["passthru"]
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv)
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
        rgb = rt.copy(rgb)
        r = rt.swizzle(rgb, "r")
        g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        max = rt.component_wise("max", r, rt.component_wise("max", g, b, width=1), width=1)
        min = rt.component_wise("min", r, rt.component_wise("min", g, b, width=1), width=1)
        delta = rt.binary("-", max, min, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", max, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", max, g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", max, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", max, rt.f(0.0)) else rt.binary("/", delta, max, 1, "float"))
        v = max
        return rt.construct(3, h, s, v)
    def hsv2rgb2__vec3(hsv):
        hsv = rt.copy(hsv)
        rgb = rt.construct(3, rt.f(0.0))
        c = rt.binary("*", rt.swizzle(hsv, "z"), rt.swizzle(hsv, "y"), 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", rt.swizzle(hsv, "x"), rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", rt.swizzle(hsv, "z"), c, 1, "float")
        if rt.binary("<", rt.swizzle(hsv, "x"), rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float")):
            rgb = rt.construct(3, c, x, rt.f(0.0))
        else:
            if rt.binary("<", rt.swizzle(hsv, "x"), rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")):
                rgb = rt.construct(3, x, c, rt.f(0.0))
            else:
                if rt.binary("<", rt.swizzle(hsv, "x"), rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")):
                    rgb = rt.construct(3, rt.f(0.0), c, x)
                else:
                    if rt.binary("<", rt.swizzle(hsv, "x"), rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")):
                        rgb = rt.construct(3, rt.f(0.0), x, c)
                    else:
                        if rt.binary("<", rt.swizzle(hsv, "x"), rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")):
                            rgb = rt.construct(3, x, rt.f(0.0), c)
                        else:
                            rgb = rt.construct(3, c, rt.f(0.0), x)
        rgb = rt.binary("+", rgb, m, 3, "float")
        return rgb
    def rgb2hsv2__vec3(rgb):
        rgb = rt.copy(rgb)
        hsv = rt.construct(3, rt.f(0.0))
        maxC = rt.component_wise("max", rt.component_wise("max", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        minC = rt.component_wise("min", rt.component_wise("min", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), width=1), rt.swizzle(rgb, "b"), width=1)
        diff = rt.binary("-", maxC, minC, 1, "float")
        if rt.binary("==", rt.swizzle(rgb, "r"), maxC):
            hsv = rt.assign_swizzle(hsv, "x", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "g"), rt.swizzle(rgb, "b"), 1, "float"), diff, 1, "float"))
        else:
            if rt.binary("==", rt.swizzle(rgb, "g"), maxC):
                hsv = rt.assign_swizzle(hsv, "x", rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "b"), rt.swizzle(rgb, "r"), 1, "float"), diff, 1, "float"), rt.f(2.0), 1, "float"))
            else:
                hsv = rt.assign_swizzle(hsv, "x", rt.binary("+", rt.binary("/", rt.binary("-", rt.swizzle(rgb, "r"), rt.swizzle(rgb, "g"), 1, "float"), diff, 1, "float"), rt.f(4.0), 1, "float"))
        hsv = rt.assign_swizzle(hsv, "x", rt.binary("/", rt.component_wise("mod", rt.swizzle(hsv, "x"), rt.f(6.0), width=1), rt.f(6.0), 1, "float"))
        hsv = rt.assign_swizzle(hsv, "y", rt.component_wise("max", rt.f(0.0), rt.binary("/", diff, maxC, 1, "float"), width=1))
        hsv = rt.assign_swizzle(hsv, "z", maxC)
        return hsv
    def saturate__vec3(color):
        color = rt.copy(color)
        sat = map__float_float_float_float_float(_u_saturation, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        avg = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(color, "r"), rt.swizzle(color, "g"), 1, "float"), rt.swizzle(color, "b"), 1, "float"), rt.f(3.0), 1, "float")
        color = rt.binary("-", color, rt.binary("*", rt.binary("-", avg, color, 3, "float"), sat, 3, "float"), 3, "float")
        return color
    def _distance__vec2_vec2(diff, uv):
        diff = rt.copy(diff)
        uv = rt.copy(uv)
        uv = rt.assign_swizzle(uv, "x", rt.binary("*", rt.swizzle(uv, "x"), rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"))
        dist = rt.f(1.0)
        if rt.binary("==", _u_shape, rt.i(0)):
            dist = rt.length(diff)
        else:
            if rt.binary("==", _u_shape, rt.i(1)):
                dist = rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), width=1), 1, "float")
            else:
                if rt.binary("==", _u_shape, rt.i(2)):
                    dist = rt.component_wise("max", rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.unary("-", rt.f(0.5)), 1, "float"), 1, "float"), rt.binary("*", rt.unary("-", rt.f(1.0)), rt.swizzle(diff, "y"), 1, "float"), width=1), rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.f(0.5), 1, "float"), 1, "float"), rt.binary("*", rt.f(1.0), rt.swizzle(diff, "y"), 1, "float"), width=1), width=1)
                else:
                    if rt.binary("==", _u_shape, rt.i(3)):
                        dist = rt.component_wise("max", rt.binary("/", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), width=1), 1, "float"), rt.component_wise("sqrt", rt.f(2.0), width=1), 1, "float"), rt.component_wise("max", rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), width=1), width=1), width=1)
                    else:
                        if rt.binary("==", _u_shape, rt.i(4)):
                            dist = rt.component_wise("max", rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "x"), rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.swizzle(uv, "y"), rt.f(0.5), 1, "float"), width=1), width=1)
                        else:
                            if rt.binary("==", _u_shape, rt.i(6)):
                                dist = rt.component_wise("max", rt.binary("-", rt.component_wise("abs", rt.swizzle(diff, "x"), width=1), rt.binary("*", rt.swizzle(diff, "y"), rt.unary("-", rt.f(0.5)), 1, "float"), 1, "float"), rt.binary("*", rt.unary("-", rt.f(1.0)), rt.swizzle(diff, "y"), 1, "float"), width=1)
                            else:
                                if rt.binary("==", _u_shape, rt.i(10)):
                                    dist = rt.binary("-", rt.f(1.0), rt.length(rt.construct(2, rt.binary("*", rt.binary("+", rt.component_wise("cos", rt.binary("*", rt.swizzle(diff, "x"), rt.f(6.28318530718), 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float"), rt.binary("*", rt.binary("+", rt.component_wise("cos", rt.binary("*", rt.swizzle(diff, "y"), rt.f(6.28318530718), 1, "float"), width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float"))), 1, "float")
        lf = map__float_float_float_float_float(_u_loopScale, rt.f(1.0), rt.f(100.0), rt.f(6.0), rt.f(1.0))
        t = rt.f(1.0)
        if rt.binary("<", _u_speed, rt.f(0.0)):
            t = rt.binary("+", rt.binary("*", dist, lf, 1, "float"), _u_time, 1, "float")
        else:
            t = rt.binary("-", rt.binary("*", dist, lf, 1, "float"), _u_time, 1, "float")
        return rt.component_wise("mix", dist, rt.binary("*", rt.binary("*", rt.binary("+", rt.component_wise("sin", rt.binary("*", t, rt.f(6.28318530718), 1, "float"), width=1), rt.binary("*", rt.f(1.0), rt.f(0.5), 1, "float"), 1, "float"), rt.component_wise("abs", _u_speed, width=1), 1, "float"), rt.f(0.005), 1, "float"), rt.binary("*", rt.component_wise("abs", _u_speed, width=1), rt.f(0.01), 1, "float"), width=1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0))
        diff = rt.binary("-", rt.f(0.5), uv, 2, "float")
        if _u_aspectLens:
            diff = rt.binary("-", rt.construct(2, rt.binary("/", rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(0.5)), rt.construct(2, rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.swizzle(uv, "y")), 2, "float")
        centerDist = _distance__vec2_vec2(diff, uv)
        distort = rt.f(0.0)
        zoom = rt.f(1.0)
        if rt.binary("<", _u_distortion, rt.f(0.0)):
            distort = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.unary("-", rt.f(2.0)), rt.f(0.0))
            zoom = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.04), rt.f(0.0))
        else:
            distort = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0))
            zoom = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.unary("-", rt.f(1.0)))
        lensedCoords = rt.component_wise("fract", rt.binary("-", rt.binary("-", uv, rt.binary("*", diff, zoom, 2, "float"), 2, "float"), rt.binary("*", rt.binary("*", rt.binary("*", diff, centerDist, 2, "float"), centerDist, 2, "float"), distort, 2, "float"), 2, "float"), width=2)
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberration, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.05)), centerDist, 1, "float"), rt.f(3.14159265359), 1, "float"), rt.f(0.5), 1, "float")
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), rt.swizzle(lensedCoords, "x"), width=1)
        red = rt.texture(_u_inputTex, rt.construct(2, redOffset, rt.swizzle(lensedCoords, "y")))
        green = rt.texture(_u_inputTex, lensedCoords)
        blueOffset = rt.component_wise("mix", rt.swizzle(lensedCoords, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(lensedCoords, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(lensedCoords, "x"), width=1)
        blue = rt.texture(_u_inputTex, rt.construct(2, blueOffset, rt.swizzle(lensedCoords, "y")))
        hsv = rt.construct(3, rt.f(1.0))
        t = (_u_time if _u_modulate else rt.f(0.0))
        if rt.binary("==", _u_mode, rt.i(0)):
            color = rt.binary("-", rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(color, "a")), green, 4, "float")
            color = rt.assign_swizzle(color, "a", rt.swizzle(green, "a"))
            hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
            hsv[int(rt.i(0))] = rt.component_wise("fract", rt.binary("+", rt.binary("+", rt.binary("+", hsv[int(rt.i(0))], rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", hsv[int(rt.i(0))], _u_hueRange, 1, "float"), rt.f(0.01), 1, "float"), 1, "float"), t, 1, "float"), width=1)
            hsv[int(rt.i(1))] = rt.f(1.0)
        else:
            color = rt.binary("*", rt.construct(4, rt.length(rt.binary("-", rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.swizzle(color, "a")), green, 4, "float"))), green, 4, "float")
            color = rt.assign_swizzle(color, "a", rt.swizzle(green, "a"))
            hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
            hsv[int(rt.i(0))] = rt.component_wise("fract", rt.binary("+", rt.binary("*", rt.binary("+", rt.binary("+", hsv[int(rt.i(0))], rt.f(0.125), 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("/", _u_hueRotation, rt.f(360.0), 1, "float"), 1, "float"), 1, "float"), rt.binary("+", rt.f(2.0), rt.binary("*", _u_hueRange, rt.f(0.05), 1, "float"), 1, "float"), 1, "float"), t, 1, "float"), width=1)
            hsv[int(rt.i(1))] = rt.f(1.0)
        green = rt.assign_swizzle(green, "rgb", rt.binary("*", saturate__vec3(rt.swizzle(green, "rgb")), map__float_float_float_float_float(_u_passthru, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0)), 3, "float"))
        if rt.binary("==", _u_blendMode, rt.i(0)):
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("min", rt.binary("+", rt.swizzle(green, "rgb"), hsv2rgb__vec3(hsv), 3, "float"), rt.f(1.0), width=3))
        else:
            if rt.binary("==", _u_blendMode, rt.i(1)):
                color = rt.assign_swizzle(color, "rgb", rt.component_wise("min", rt.binary("+", rt.component_wise("max", rt.binary("-", rt.swizzle(green, "rgb"), rt.construct(3, hsv[int(rt.i(2))]), 3, "float"), rt.f(0.0), width=3), hsv2rgb__vec3(hsv), 3, "float"), rt.f(1.0), width=3))
        color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), (rt.swizzle(color, "rgb") if rt.binary("==", rt.swizzle(color, "rgb"), rt.construct(3, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", _u_tint, _u_tint, 3, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(color, "rgb"), 3, "float"), 3, "float"), rt.construct(3, rt.f(1.0)), width=3)), rt.binary("*", _u_alpha, rt.f(0.01), 1, "float"), width=3))
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color, "a"), rt.binary("*", _u_alpha, rt.f(0.01), 1, "float"), width=1))
        if rt.binary("<", _u_vignetteAmt, rt.f(0.0)):
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.binary("-", rt.binary("*", rt.swizzle(color, "rgb"), rt.f(1.0), 3, "float"), rt.component_wise("pow", rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), rt.f(1.125), 1, "float"), rt.f(2.0), width=1), 3, "float"), rt.swizzle(color, "rgb"), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.0), rt.f(1.0)), width=3))
            color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color, "a"), rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(1.0), rt.f(0.0)), 1, "float"), width=1))
        else:
            color = rt.assign_swizzle(color, "rgb", rt.component_wise("mix", rt.swizzle(color, "rgb"), rt.binary("-", rt.f(1.0), rt.binary("-", rt.binary("-", rt.f(1.0), rt.binary("*", rt.swizzle(color, "rgb"), rt.f(1.0), 3, "float"), 3, "float"), rt.component_wise("pow", rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), rt.f(1.125), 1, "float"), rt.f(2.0), width=1), 3, "float"), 3, "float"), map__float_float_float_float_float(_u_vignetteAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=3))
            color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(color, "a"), rt.binary("*", rt.length(rt.binary("-", rt.f(0.5), uv, 2, "float")), map__float_float_float_float_float(_u_vignetteAmt, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(1.0), rt.f(0.0)), 1, "float"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
