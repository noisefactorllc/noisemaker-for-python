def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_selfTex = T["selfTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_scaleAmt = U.get("scaleAmt", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_blendMode = U.get("blendMode", 0)
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    _u_hueRotation = U.get("hueRotation", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_distortion = U.get("distortion", rt.f(0.0))
    _u_aberration = U.get("aberration", rt.f(0.0))
    _u_refractAAmt = U.get("refractAAmt", rt.f(0.0))
    _u_refractBAmt = U.get("refractBAmt", rt.f(0.0))
    _u_refractADir = U.get("refractADir", rt.f(0.0))
    _u_refractBDir = U.get("refractBDir", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def blendOverlay__float_float(a, b):
        return (rt.binary("*", rt.binary("*", rt.f(2.0), a, 1, "float"), b, 1, "float") if rt.binary("<", a, rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), b, 1, "float"), 1, "float"), 1, "float"))
    def blendSoftLight__float_float(base, blend):
        return (rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), blend, 1, "float"), rt.binary("*", rt.binary("*", base, base, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), blend, 1, "float"), 1, "float"), 1, "float"), 1, "float") if rt.binary("<", blend, rt.f(0.5)) else rt.binary("+", rt.binary("*", rt.component_wise("sqrt", base, width=1), rt.binary("-", rt.binary("*", rt.f(2.0), blend, 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), rt.binary("-", rt.f(1.0), blend, 1, "float"), 1, "float"), 1, "float"))
    def cloak__vec2(st):
        st = rt.copy(st, "float")
        m = map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        ra = map__float_float_float_float_float(_u_refractAAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
        rb = map__float_float_float_float_float(_u_refractBAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
        leftColor = rt.texture(_u_inputTex, st)
        rightColor = rt.texture(_u_selfTex, st)
        leftUV = rt.construct(2, st)
        rightLen = rt.length(rt.swizzle(rightColor, "rgb"))
        leftUV = rt.assign_swizzle(leftUV, "x", rt.binary("+", rt.swizzle(leftUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
        leftUV = rt.assign_swizzle(leftUV, "y", rt.binary("+", rt.swizzle(leftUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
        leftRefracted = rt.texture(_u_inputTex, rt.component_wise("fract", leftUV, width=2))
        rightUV = rt.construct(2, st)
        leftLen = rt.length(rt.swizzle(leftColor, "rgb"))
        rightUV = rt.assign_swizzle(rightUV, "x", rt.binary("+", rt.swizzle(rightUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
        rightUV = rt.assign_swizzle(rightUV, "y", rt.binary("+", rt.swizzle(rightUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
        rightRefracted = rt.texture(_u_selfTex, rt.component_wise("fract", rightUV, width=2))
        leftReflected = rt.component_wise("min", rt.binary("/", rt.binary("*", rightRefracted, rightColor, 4, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", leftRefracted, leftColor, 4, "float"), 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        rightReflected = rt.component_wise("min", rt.binary("/", rt.binary("*", leftRefracted, leftColor, 4, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rightRefracted, rightColor, 4, "float"), 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4)
        left = rt.construct(4, rt.f(1.0))
        right = rt.construct(4, rt.f(1.0))
        if rt.binary("<", _u_mixAmt, rt.f(50.0)):
            left[:] = rt.component_wise("mix", leftRefracted, leftReflected, map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(50.0), rt.f(0.0), rt.f(1.0)), width=4)
            right[:] = rightReflected
        else:
            left[:] = leftReflected
            right[:] = rt.component_wise("mix", rightReflected, rightRefracted, map__float_float_float_float_float(_u_mixAmt, rt.f(50.0), rt.f(100.0), rt.f(0.0), rt.f(1.0)), width=4)
        return rt.component_wise("mix", left, right, m, width=4)
    def blend__vec4_vec4_int_float(color1, color2, mode, factor):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        color = rt.construct(4, 0.0)
        middle = rt.construct(4, 0.0)
        amt = map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        if rt.binary("==", mode, rt.i(0)):
            middle[:] = rt.component_wise("min", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), width=4)
        else:
            if rt.binary("==", mode, rt.i(2)):
                middle[:] = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(0.0))) else rt.component_wise("max", rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", rt.f(1.0), color1, 4, "float"), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(0.0)), width=4))
            else:
                if rt.binary("==", mode, rt.i(3)):
                    middle[:] = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", color1, rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                else:
                    if rt.binary("==", mode, rt.i(4)):
                        middle[:] = rt.component_wise("min", color1, color2, width=4)
                    else:
                        if rt.binary("==", mode, rt.i(5)):
                            middle[:] = rt.component_wise("abs", rt.binary("-", color1, color2, 4, "float"), width=4)
                            middle = rt.assign_swizzle(middle, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
                        else:
                            if rt.binary("==", mode, rt.i(6)):
                                middle[:] = rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), color1, 4, "float"), color2, 4, "float"), 4, "float")
                                middle = rt.assign_swizzle(middle, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
                            else:
                                if rt.binary("==", mode, rt.i(7)):
                                    middle[:] = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color1, color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                else:
                                    if rt.binary("==", mode, rt.i(8)):
                                        (middle.__setitem__(0, blendOverlay__float_float(rt.swizzle(color2, "r"), rt.swizzle(color1, "r"))), middle.__setitem__(1, blendOverlay__float_float(rt.swizzle(color2, "g"), rt.swizzle(color1, "g"))), middle.__setitem__(2, blendOverlay__float_float(rt.swizzle(color2, "b"), rt.swizzle(color1, "b"))), middle.__setitem__(3, rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1)), middle)[-1]
                                    else:
                                        if rt.binary("==", mode, rt.i(9)):
                                            middle[:] = rt.component_wise("max", color1, color2, width=4)
                                        else:
                                            if rt.binary("==", mode, rt.i(10)):
                                                middle[:] = rt.component_wise("mix", color1, color2, rt.f(0.5), width=4)
                                            else:
                                                if rt.binary("==", mode, rt.i(11)):
                                                    middle[:] = rt.binary("*", color1, color2, 4, "float")
                                                else:
                                                    if rt.binary("==", mode, rt.i(12)):
                                                        middle[:] = rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4, "float"), color2, 4, "float"), width=4), 4, "float")
                                                        middle = rt.assign_swizzle(middle, "a", rt.component_wise("max", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), width=1))
                                                    else:
                                                        if rt.binary("==", mode, rt.i(13)):
                                                            (middle.__setitem__(0, blendOverlay__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r"))), middle.__setitem__(1, blendOverlay__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g"))), middle.__setitem__(2, blendOverlay__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b"))), middle.__setitem__(3, rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1)), middle)[-1]
                                                        else:
                                                            if rt.binary("==", mode, rt.i(14)):
                                                                middle[:] = rt.binary("+", rt.binary("-", rt.component_wise("min", color1, color2, width=4), rt.component_wise("max", color1, color2, width=4), 4, "float"), rt.construct(4, rt.f(1.0)), 4, "float")
                                                            else:
                                                                if rt.binary("==", mode, rt.i(15)):
                                                                    middle[:] = (color1 if rt.binary("==", color1, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color2, color2, 4, "float"), rt.binary("-", rt.f(1.0), color1, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                                                else:
                                                                    if rt.binary("==", mode, rt.i(16)):
                                                                        middle[:] = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), 4, "float")
                                                                    else:
                                                                        if rt.binary("==", mode, rt.i(17)):
                                                                            (middle.__setitem__(0, blendSoftLight__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r"))), middle.__setitem__(1, blendSoftLight__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g"))), middle.__setitem__(2, blendSoftLight__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b"))), middle.__setitem__(3, rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1)), middle)[-1]
                                                                        else:
                                                                            if rt.binary("==", mode, rt.i(18)):
                                                                                middle[:] = rt.component_wise("max", rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), 4, "float"), rt.f(0.0), width=4)
                                                                            else:
                                                                                middle[:] = rt.component_wise("mix", color1, color2, rt.f(0.5), width=4)
        if rt.binary("==", factor, rt.f(0.5)):
            color[:] = middle
        else:
            if rt.binary("<", factor, rt.f(0.5)):
                factor = map__float_float_float_float_float(amt, rt.f(0.0), rt.f(0.5), rt.f(0.0), rt.f(1.0))
                color[:] = rt.component_wise("mix", color1, middle, factor, width=4)
            else:
                if rt.binary(">", factor, rt.f(0.5)):
                    factor = map__float_float_float_float_float(amt, rt.f(0.5), rt.f(1.0), rt.f(0.0), rt.f(1.0))
                    color[:] = rt.component_wise("mix", middle, color2, factor, width=4)
        return color
    def brightnessContrast__vec3(color):
        color = rt.copy(color, "float")
        bright = map__float_float_float_float_float(rt.binary("*", _u_intensity, rt.f(0.1), 1, "float"), rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.5)), rt.f(0.5))
        cont = map__float_float_float_float_float(rt.binary("*", _u_intensity, rt.f(0.1), 1, "float"), rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.f(0.5), rt.f(1.5))
        color[:] = rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", color, rt.f(0.5), 3, "float"), cont, 3, "float"), rt.f(0.5), 3, "float"), bright, 3, "float")
        return color
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), 1, "float"), 1, "float"))
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(2.0))
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        st[:] = rt.binary("-", st, rt.construct(2, rt.binary("*", rt.f(0.5), rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), 1, "float"), 1, "float"), rt.f(0.5)), 2, "float")
        st[:] = rt.matrix_mult(rt.construct(4, rt.component_wise("cos", angle, width=1), rt.unary("-", rt.component_wise("sin", angle, width=1)), rt.component_wise("sin", angle, width=1), rt.component_wise("cos", angle, width=1)), st, 2)
        st[:] = rt.binary("+", st, rt.construct(2, rt.binary("*", rt.f(0.5), rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), 1, "float"), 1, "float"), rt.f(0.5)), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("/", rt.swizzle(st, "x"), rt.binary("/", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), 1, "float"), 1, "float"))
        return st
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
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if (bool(rt.binary("<=", rt.binary("/", rt.f(1.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float")))):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if (bool(rt.binary("<=", rt.binary("/", rt.f(2.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float")))):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if (bool(rt.binary("<=", rt.binary("/", rt.f(3.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float")))):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if (bool(rt.binary("<=", rt.binary("/", rt.f(4.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float")))):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            if (bool(rt.binary("<=", rt.binary("/", rt.f(5.0), rt.f(6.0), 1, "float"), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
                            else:
                                (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        return rt.binary("+", rgb, rt.construct(3, m, m, m), 3, "float")
    def rgb2hsv__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r = rt.swizzle(rgb, "r")
        _g = rt.swizzle(rgb, "g")
        b = rt.swizzle(rgb, "b")
        maxC = rt.component_wise("max", r, rt.component_wise("max", _g, b, width=1), width=1)
        minC = rt.component_wise("min", r, rt.component_wise("min", _g, b, width=1), width=1)
        delta = rt.binary("-", maxC, minC, 1, "float")
        h = rt.f(0.0)
        if rt.binary("!=", delta, rt.f(0.0)):
            if rt.binary("==", maxC, r):
                h = rt.binary("/", rt.component_wise("mod", rt.binary("/", rt.binary("-", _g, b, 1, "float"), delta, 1, "float"), rt.f(6.0), width=1), rt.f(6.0), 1, "float")
            else:
                if rt.binary("==", maxC, _g):
                    h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", b, r, 1, "float"), delta, 1, "float"), rt.f(2.0), 1, "float"), rt.f(6.0), 1, "float")
                else:
                    if rt.binary("==", maxC, b):
                        h = rt.binary("/", rt.binary("+", rt.binary("/", rt.binary("-", r, _g, 1, "float"), delta, 1, "float"), rt.f(4.0), 1, "float"), rt.f(6.0), 1, "float")
        s = (rt.f(0.0) if rt.binary("==", maxC, rt.f(0.0)) else rt.binary("/", delta, maxC, 1, "float"))
        v = maxC
        return rt.construct(3, h, s, v)
    def getImage__vec2(st):
        st = rt.copy(st, "float")
        st[:] = rotate2D__vec2_float(st, _u_rotation)
        diff = rt.binary("-", rt.f(0.5), st, 2, "float")
        centerDist = rt.length(diff)
        distort = rt.f(0.0)
        zoom = rt.f(0.0)
        if rt.binary("<", _u_distortion, rt.f(0.0)):
            distort = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.unary("-", rt.f(2.0)), rt.f(0.0))
            zoom = map__float_float_float_float_float(_u_distortion, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.04), rt.f(0.0))
        else:
            distort = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(2.0))
            zoom = map__float_float_float_float_float(_u_distortion, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.unary("-", rt.f(1.0)))
        st[:] = rt.binary("-", rt.binary("-", st, rt.binary("*", diff, zoom, 2, "float"), 2, "float"), rt.binary("*", rt.binary("*", rt.binary("*", diff, centerDist, 2, "float"), centerDist, 2, "float"), distort, 2, "float"), 2, "float")
        scale = rt.binary("/", rt.f(100.0), _u_scaleAmt, 1, "float")
        if rt.binary("==", scale, rt.f(0.0)):
            scale = rt.f(1.0)
        st[:] = rt.binary("*", st, scale, 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("-", rt.swizzle(st, "x"), rt.binary("-", rt.binary("*", scale, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(_u_resolution, "x"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("-", rt.binary("+", rt.binary("*", scale, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.binary("/", rt.f(1.0), rt.swizzle(_u_resolution, "y"), 1, "float"), scale, 1, "float"), 1, "float"), 1, "float"), scale, 1, "float"), 1, "float"))
        st[:] = rt.binary("+", st, rt.binary("/", rt.f(1.0), _u_resolution, 2, "float"), 2, "float")
        st[:] = rt.component_wise("fract", st, width=2)
        aberrationOffset = rt.binary("*", rt.binary("*", rt.binary("*", map__float_float_float_float_float(_u_aberration, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.1)), centerDist, 1, "float"), rt.f(3.14159265359), 1, "float"), rt.f(0.5), 1, "float")
        redOffset = rt.component_wise("mix", rt.component_wise("clamp", rt.binary("+", rt.swizzle(st, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(st, "x"), rt.swizzle(st, "x"), width=1)
        red = rt.texture(_u_selfTex, rt.construct(2, redOffset, rt.swizzle(st, "y")))
        green = rt.texture(_u_selfTex, st)
        blueOffset = rt.component_wise("mix", rt.swizzle(st, "x"), rt.component_wise("clamp", rt.binary("-", rt.swizzle(st, "x"), aberrationOffset, 1, "float"), rt.f(0.0), rt.f(1.0), width=1), rt.swizzle(st, "x"), width=1)
        blue = rt.texture(_u_selfTex, rt.construct(2, blueOffset, rt.swizzle(st, "y")))
        tex = rt.construct(4, rt.swizzle(red, "r"), rt.swizzle(green, "g"), rt.swizzle(blue, "b"), rt.f(1.0))
        tex = rt.assign_swizzle(tex, "rgb", rt.binary("*", rt.swizzle(tex, "rgb"), rt.swizzle(tex, "a"), 3, "float"))
        return tex
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        if _u_resetState:
            g.fragColor[:] = rt.texture(_u_inputTex, uv)
            return
        color = rt.construct(4, rt.f(0.0))
        ra = rt.f(0.0)
        rb = rt.f(0.0)
        leftColor = rt.construct(4, 0.0)
        rightColor = rt.construct(4, 0.0)
        leftUV = rt.construct(2, 0.0)
        rightLen = rt.f(0.0)
        rightUV = rt.construct(2, 0.0)
        leftLen = rt.f(0.0)
        if rt.binary("==", _u_blendMode, rt.i(100)):
            color[:] = cloak__vec2(uv)
        else:
            ra = map__float_float_float_float_float(_u_refractAAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
            rb = map__float_float_float_float_float(_u_refractBAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
            leftColor = rt.texture(_u_inputTex, uv)
            rightColor = rt.texture(_u_selfTex, uv)
            leftUV = rt.construct(2, uv)
            rightLen = rt.binary("+", rt.length(rt.swizzle(rightColor, "rgb")), rt.binary("/", _u_refractADir, rt.f(360.0), 1, "float"), 1, "float")
            leftUV = rt.assign_swizzle(leftUV, "x", rt.binary("+", rt.swizzle(leftUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
            leftUV = rt.assign_swizzle(leftUV, "y", rt.binary("+", rt.swizzle(leftUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", rightLen, rt.f(6.28318530718), 1, "float"), width=1), ra, 1, "float"), 1, "float"))
            rightUV = rt.construct(2, uv)
            leftLen = rt.binary("+", rt.length(rt.swizzle(leftColor, "rgb")), rt.binary("/", _u_refractBDir, rt.f(360.0), 1, "float"), 1, "float")
            rightUV = rt.assign_swizzle(rightUV, "x", rt.binary("+", rt.swizzle(rightUV, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
            rightUV = rt.assign_swizzle(rightUV, "y", rt.binary("+", rt.swizzle(rightUV, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", leftLen, rt.f(6.28318530718), 1, "float"), width=1), rb, 1, "float"), 1, "float"))
            color[:] = blend__vec4_vec4_int_float(rt.texture(_u_inputTex, leftUV), getImage__vec2(rightUV), _u_blendMode, rt.binary("*", _u_mixAmt, rt.f(0.01), 1, "float"))
        hsv = rgb2hsv__vec3(rt.swizzle(color, "rgb"))
        hsv[int(rt.i(0))] = rt.component_wise("mod", rt.binary("+", hsv[int(rt.i(0))], map__float_float_float_float_float(_u_hueRotation, rt.unary("-", rt.f(180.0)), rt.f(180.0), rt.unary("-", rt.f(0.05)), rt.f(0.05)), 1, "float"), rt.f(1.0), width=1)
        color = rt.assign_swizzle(color, "rgb", hsv2rgb__vec3(hsv))
        color = rt.assign_swizzle(color, "rgb", brightnessContrast__vec3(rt.swizzle(color, "rgb")))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
