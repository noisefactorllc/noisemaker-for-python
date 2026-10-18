def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_EFFECT = U.get("EFFECT", 0)
    _u_FLIP = U.get("FLIP", 0)
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_invFullResolution = U.get("invFullResolution", rt.construct(2, 0.0))
    _u_aspectInv = U.get("aspectInv", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_effectAmt = U.get("effectAmt", rt.f(0.0))
    _u_scaleAmt = U.get("scaleAmt", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_offsetX = U.get("offsetX", rt.f(0.0))
    _u_offsetY = U.get("offsetY", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_saturation = U.get("saturation", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.emboss = rt.new_array(rt.i(9), 1)
    g.sharpen = rt.new_array(rt.i(9), 1)
    g.blur = rt.new_array(rt.i(9), 1)
    g.edge = rt.new_array(rt.i(9), 1)
    g.edge2 = rt.new_array(rt.i(9), 1)
    g.edge3 = rt.new_array(rt.i(9), 1)
    g.sharpenBlur = rt.new_array(rt.i(9), 1)
    def loadKernels__void():
        g.emboss[int(rt.i(0))] = rt.unary("-", rt.f(2.0))
        g.emboss[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        g.emboss[int(rt.i(2))] = rt.f(0.0)
        g.emboss[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        g.emboss[int(rt.i(4))] = rt.f(1.0)
        g.emboss[int(rt.i(5))] = rt.f(1.0)
        g.emboss[int(rt.i(6))] = rt.f(0.0)
        g.emboss[int(rt.i(7))] = rt.f(1.0)
        g.emboss[int(rt.i(8))] = rt.f(2.0)
        g.sharpen[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(1))] = rt.f(0.0)
        g.sharpen[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(3))] = rt.f(0.0)
        g.sharpen[int(rt.i(4))] = rt.f(5.0)
        g.sharpen[int(rt.i(5))] = rt.f(0.0)
        g.sharpen[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.sharpen[int(rt.i(7))] = rt.f(0.0)
        g.sharpen[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        g.blur[int(rt.i(0))] = rt.f(1.0)
        g.blur[int(rt.i(1))] = rt.f(2.0)
        g.blur[int(rt.i(2))] = rt.f(1.0)
        g.blur[int(rt.i(3))] = rt.f(2.0)
        g.blur[int(rt.i(4))] = rt.f(4.0)
        g.blur[int(rt.i(5))] = rt.f(2.0)
        g.blur[int(rt.i(6))] = rt.f(1.0)
        g.blur[int(rt.i(7))] = rt.f(2.0)
        g.blur[int(rt.i(8))] = rt.f(1.0)
        g.edge[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(1))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(3))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(4))] = rt.f(8.0)
        g.edge[int(rt.i(5))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(7))] = rt.unary("-", rt.f(1.0))
        g.edge[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(1))] = rt.f(0.0)
        g.edge2[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(3))] = rt.f(0.0)
        g.edge2[int(rt.i(4))] = rt.f(4.0)
        g.edge2[int(rt.i(5))] = rt.f(0.0)
        g.edge2[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        g.edge2[int(rt.i(7))] = rt.f(0.0)
        g.edge2[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        g.edge3[int(rt.i(0))] = rt.unary("-", rt.f(0.875))
        g.edge3[int(rt.i(1))] = rt.unary("-", rt.f(0.75))
        g.edge3[int(rt.i(2))] = rt.unary("-", rt.f(0.875))
        g.edge3[int(rt.i(3))] = rt.unary("-", rt.f(0.75))
        g.edge3[int(rt.i(4))] = rt.f(5.0)
        g.edge3[int(rt.i(5))] = rt.unary("-", rt.f(0.75))
        g.edge3[int(rt.i(6))] = rt.unary("-", rt.f(0.875))
        g.edge3[int(rt.i(7))] = rt.unary("-", rt.f(0.75))
        g.edge3[int(rt.i(8))] = rt.unary("-", rt.f(0.875))
        g.sharpenBlur[int(rt.i(0))] = rt.unary("-", rt.f(2.0))
        g.sharpenBlur[int(rt.i(1))] = rt.f(2.0)
        g.sharpenBlur[int(rt.i(2))] = rt.unary("-", rt.f(2.0))
        g.sharpenBlur[int(rt.i(3))] = rt.f(2.0)
        g.sharpenBlur[int(rt.i(4))] = rt.f(1.0)
        g.sharpenBlur[int(rt.i(5))] = rt.f(2.0)
        g.sharpenBlur[int(rt.i(6))] = rt.unary("-", rt.f(2.0))
        g.sharpenBlur[int(rt.i(7))] = rt.f(2.0)
        g.sharpenBlur[int(rt.i(8))] = rt.unary("-", rt.f(2.0))
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        (v.__setitem__(0, rt.binary("+", rt.binary("*", rt.swizzle(v, "x"), rt.construct(1, rt.i(1664525), base="uint"), 1, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 1, "uint")), v.__setitem__(1, rt.binary("+", rt.binary("*", rt.swizzle(v, "y"), rt.construct(1, rt.i(1664525), base="uint"), 1, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 1, "uint")), v.__setitem__(2, rt.binary("+", rt.binary("*", rt.swizzle(v, "z"), rt.construct(1, rt.i(1664525), base="uint"), 1, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 1, "uint")), v)[-1]
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        (v.__setitem__(0, rt.binary("^", rt.swizzle(v, "x"), rt.binary(">>", rt.swizzle(v, "x"), rt.construct(1, rt.i(16), base="uint"), 1, "uint"), 1, "uint")), v.__setitem__(1, rt.binary("^", rt.swizzle(v, "y"), rt.binary(">>", rt.swizzle(v, "y"), rt.construct(1, rt.i(16), base="uint"), 1, "uint"), 1, "uint")), v.__setitem__(2, rt.binary("^", rt.swizzle(v, "z"), rt.binary(">>", rt.swizzle(v, "z"), rt.construct(1, rt.i(16), base="uint"), 1, "uint"), 1, "uint")), v)[-1]
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        return rt.construct(3, rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, 'float'))
    def random__vec2(p):
        p = rt.copy(p, "float")
        p2 = rt.construct(3, p, rt.f(0.0))
        return rt.binary("/", rt.construct(1, rt.swizzle(pcg__uvec3(rt.construct(3, p2, base="uint")), "x")), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 1, "float")
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        span = rt.binary("-", inMax, inMin, 1, "float")
        rmul = rt.binary("/", rt.f(1.0), span, 1, "float")
        mc = rt.component_wise("min", rt.component_wise("max", rt.binary("*", span, rmul, 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        return rt.binary("+", outMin, rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("*", rt.binary("-", value, inMin, 1, "float"), rt.binary("*", rmul, rt.binary("-", rt.f(2.0), mc, 1, "float"), 1, "float"), 1, "float"), 1, "float"), 1, "float")
    def rotate2D__vec2_float(st, rot):
        st = rt.copy(st, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), rt.fdiv(rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1), 1, "float"))
        st = rt.assign_swizzle(st, "x", rt.component_wise("min", rt.component_wise("max", rt.swizzle(st, "x"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1))
        rot = map__float_float_float_float_float(rot, rt.f(0.0), rt.f(360.0), rt.f(0.0), rt.f(2.0))
        angle = rt.binary("*", rot, rt.f(3.14159265359), 1, "float")
        ox = rt.component_wise("min", rt.component_wise("max", rt.fdiv(rt.binary("*", rt.f(0.5), rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        st[:] = rt.binary("-", st, rt.construct(2, ox, rt.f(0.5)), 2, "float")
        ca = rt.component_wise("cos", angle, width=1)
        sa = rt.component_wise("sin", angle, width=1)
        px = rt.component_wise("min", rt.component_wise("max", rt.binary("*", ca, rt.swizzle(st, "x"), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        py = rt.component_wise("min", rt.component_wise("max", rt.binary("*", sa, rt.swizzle(st, "y"), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        qx = rt.component_wise("min", rt.component_wise("max", rt.binary("*", rt.unary("-", sa), rt.swizzle(st, "x"), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        qy = rt.component_wise("min", rt.component_wise("max", rt.binary("*", ca, rt.swizzle(st, "y"), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        (st.__setitem__(0, rt.binary("+", px, py, 1, "float")), st.__setitem__(1, rt.binary("+", qx, qy, 1, "float")), st)[-1]
        st[:] = rt.binary("+", st, rt.construct(2, ox, rt.f(0.5)), 2, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("*", rt.swizzle(st, "x"), _u_aspectInv, 1, "float"))
        st[:] = rt.component_wise("min", rt.component_wise("max", st, rt.construct(2, rt.unary("-", rt.f(1e+38))), width=2), rt.construct(2, rt.f(1e+38)), width=2)
        return st
    def brightnessContrast__vec3(color):
        color = rt.copy(color, "float")
        bright = map__float_float_float_float_float(_u_intensity, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(0.4)), rt.f(0.4))
        cont = rt.f(1.0)
        if rt.binary("<", _u_intensity, rt.f(0.0)):
            cont = map__float_float_float_float_float(_u_intensity, rt.unary("-", rt.f(100.0)), rt.f(0.0), rt.f(0.5), rt.f(1.0))
        else:
            cont = map__float_float_float_float_float(_u_intensity, rt.f(0.0), rt.f(100.0), rt.f(1.0), rt.f(1.5))
        (color.__setitem__(0, rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(color, "x"), rt.f(0.5), 1, "float"), cont, 1, "float"), rt.f(0.5), 1, "float"), bright, 1, "float")), color.__setitem__(1, rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(color, "y"), rt.f(0.5), 1, "float"), cont, 1, "float"), rt.f(0.5), 1, "float"), bright, 1, "float")), color.__setitem__(2, rt.binary("+", rt.binary("+", rt.binary("*", rt.binary("-", rt.swizzle(color, "z"), rt.f(0.5), 1, "float"), cont, 1, "float"), rt.f(0.5), 1, "float"), bright, 1, "float")), color)[-1]
        return color
    def saturate__vec3(color):
        color = rt.copy(color, "float")
        sat = map__float_float_float_float_float(_u_saturation, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        avg = rt.binary("/", rt.binary("+", rt.binary("+", rt.swizzle(color, "r"), rt.swizzle(color, "g"), 1, "float"), rt.swizzle(color, "b"), 1, "float"), rt.f(3.0), 1, "float")
        (color.__setitem__(0, rt.binary("-", rt.swizzle(color, "x"), rt.binary("*", rt.binary("-", avg, rt.swizzle(color, "x"), 1, "float"), sat, 1, "float"), 1, "float")), color.__setitem__(1, rt.binary("-", rt.swizzle(color, "y"), rt.binary("*", rt.binary("-", avg, rt.swizzle(color, "y"), 1, "float"), sat, 1, "float"), 1, "float")), color.__setitem__(2, rt.binary("-", rt.swizzle(color, "z"), rt.binary("*", rt.binary("-", avg, rt.swizzle(color, "z"), 1, "float"), sat, 1, "float"), 1, "float")), color)[-1]
        return color
    def hsv2rgb__vec3(hsv):
        hsv = rt.copy(hsv, "float")
        h = rt.component_wise("fract", rt.swizzle(hsv, "x"), width=1)
        s = rt.swizzle(hsv, "y")
        v = rt.swizzle(hsv, "z")
        c = rt.binary("*", v, s, 1, "float")
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("*", h, rt.f(6.0), 1, "float"), rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        m = rt.binary("-", v, c, 1, "float")
        rgb = rt.construct(3, 0.0)
        if (bool(rt.binary("<=", rt.f(0.0), h)) and bool(rt.binary("<", h, rt.f(0.16666666666666666)))):
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if (bool(rt.binary("<=", rt.f(0.16666666666666666), h)) and bool(rt.binary("<", h, rt.f(0.3333333333333333)))):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if (bool(rt.binary("<=", rt.f(0.3333333333333333), h)) and bool(rt.binary("<", h, rt.f(0.5)))):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if (bool(rt.binary("<=", rt.f(0.5), h)) and bool(rt.binary("<", h, rt.f(0.6666666666666666)))):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if (bool(rt.binary("<=", rt.f(0.6666666666666666), h)) and bool(rt.binary("<", h, rt.f(0.8333333333333334)))):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            if (bool(rt.binary("<=", rt.f(0.8333333333333334), h)) and bool(rt.binary("<", h, rt.f(1.0)))):
                                (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
                            else:
                                (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        return rt.construct(3, rt.binary("+", rgb, rt.construct_raw(3, m, m, m), 3, 'float'))
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
    def posterize__vec3_float(color, lev):
        color = rt.copy(color, "float")
        if rt.binary("==", lev, rt.f(0.0)):
            return color
        else:
            if rt.binary("==", lev, rt.f(1.0)):
                return rt.component_wise("step", rt.f(0.5), color, width=3)
        gamma = rt.f(0.65)
        color[:] = rt.component_wise("pow", color, rt.construct(3, gamma), width=3)
        ((_vector_write_0_0 := rt.binary("/", rt.swizzle(rt.component_wise("floor", rt.binary("*", color, lev, 3, 'float'), width=3), "x"), lev, 1, "float")), (_vector_write_0_1 := rt.binary("/", rt.swizzle(rt.component_wise("floor", rt.binary("*", color, lev, 3, 'float'), width=3), "y"), lev, 1, "float")), (_vector_write_0_2 := rt.binary("/", rt.swizzle(rt.component_wise("floor", rt.binary("*", color, lev, 3, 'float'), width=3), "z"), lev, 1, "float")), color.__setitem__(0, _vector_write_0_0), color.__setitem__(1, _vector_write_0_1), color.__setitem__(2, _vector_write_0_2), color)[-1]
        color[:] = rt.component_wise("pow", color, rt.construct(3, rt.binary("/", rt.f(1.0), gamma, 1, "float")), width=3)
        return color
    def pixellate__vec2_float(uv, size):
        uv = rt.copy(uv, "float")
        if rt.binary("<", size, rt.f(1.0)):
            return rt.swizzle(rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))), "rgb")
        size = rt.binary("*", size, rt.f(4.0), 1, "float")
        dx = rt.binary("*", size, rt.fdiv(rt.f(1.0), rt.swizzle(_u_fullResolution, "x"), 1), 1, "float")
        dy = rt.binary("*", size, rt.fdiv(rt.f(1.0), rt.swizzle(_u_fullResolution, "y"), 1), 1, "float")
        uv[:] = rt.binary("-", uv, rt.f(0.5), 2, "float")
        coord = rt.construct(2, rt.binary("*", dx, rt.component_wise("floor", rt.binary("/", rt.swizzle(uv, "x"), dx, 1, "float"), width=1), 1, "float"), rt.binary("*", dy, rt.component_wise("floor", rt.binary("/", rt.swizzle(uv, "y"), dy, 1, "float"), width=1), 1, "float"))
        coord[:] = rt.binary("+", coord, rt.f(0.5), 2, "float")
        return rt.swizzle(rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", coord, _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))), "rgb")
    def desaturate__vec3(color):
        color = rt.copy(color, "float")
        avg = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
        return rt.construct(3, avg)
    def convolve__vec2_float_bool(uv, kernel, divide):
        uv = rt.copy(uv, "float")
        steps = rt.construct(2, rt.fdiv(rt.f(1.0), _u_fullResolution, 2))
        offset = rt.new_array(rt.i(9), 2)
        offset[int(rt.i(0))] = rt.construct(2, rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.unary("-", rt.swizzle(steps, "y"))))
        offset[int(rt.i(1))] = rt.construct(2, rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(steps, "y"))))
        offset[int(rt.i(2))] = rt.construct(2, rt.construct(2, rt.swizzle(steps, "x"), rt.unary("-", rt.swizzle(steps, "y"))))
        offset[int(rt.i(3))] = rt.construct(2, rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.f(0.0)))
        offset[int(rt.i(4))] = rt.construct(2, rt.construct(2, rt.f(0.0), rt.f(0.0)))
        offset[int(rt.i(5))] = rt.construct(2, rt.construct(2, rt.swizzle(steps, "x"), rt.f(0.0)))
        offset[int(rt.i(6))] = rt.construct(2, rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.swizzle(steps, "y")))
        offset[int(rt.i(7))] = rt.construct(2, rt.construct(2, rt.f(0.0), rt.swizzle(steps, "y")))
        offset[int(rt.i(8))] = rt.construct(2, rt.construct(2, rt.swizzle(steps, "x"), rt.swizzle(steps, "y")))
        kernelWeight = rt.f(0.0)
        conv = rt.construct(3, rt.f(0.0))
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            color = rt.swizzle(rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", rt.binary("+", uv, rt.binary("*", offset[int(i)], _u_effectAmt, 2, 'float'), 2, 'float'), _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))), "rgb")
            conv[:] = rt.binary("+", conv, rt.binary("*", color, kernel[int(i)], 3, 'float'), 3, "float")
            kernelWeight = rt.binary("+", kernelWeight, kernel[int(i)], 1, "float")
        if divide:
            conv = rt.assign_swizzle(conv, "rgb", rt.binary("/", rt.swizzle(conv, "rgb"), kernelWeight, 3, "float"))
        return rt.component_wise("clamp", rt.swizzle(conv, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
    def derivatives__vec3_vec2_bool(color, uv, divide):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        deriv_x = rt.new_array(rt.i(9), 1)
        deriv_x[int(rt.i(0))] = rt.f(0.0)
        deriv_x[int(rt.i(1))] = rt.f(0.0)
        deriv_x[int(rt.i(2))] = rt.f(0.0)
        deriv_x[int(rt.i(3))] = rt.f(0.0)
        deriv_x[int(rt.i(4))] = rt.f(1.0)
        deriv_x[int(rt.i(5))] = rt.unary("-", rt.f(1.0))
        deriv_x[int(rt.i(6))] = rt.f(0.0)
        deriv_x[int(rt.i(7))] = rt.f(0.0)
        deriv_x[int(rt.i(8))] = rt.f(0.0)
        deriv_y = rt.new_array(rt.i(9), 1)
        deriv_y[int(rt.i(0))] = rt.f(0.0)
        deriv_y[int(rt.i(1))] = rt.f(0.0)
        deriv_y[int(rt.i(2))] = rt.f(0.0)
        deriv_y[int(rt.i(3))] = rt.f(0.0)
        deriv_y[int(rt.i(4))] = rt.f(1.0)
        deriv_y[int(rt.i(5))] = rt.f(0.0)
        deriv_y[int(rt.i(6))] = rt.f(0.0)
        deriv_y[int(rt.i(7))] = rt.unary("-", rt.f(1.0))
        deriv_y[int(rt.i(8))] = rt.f(0.0)
        s1 = convolve__vec2_float_bool(uv, deriv_x, divide)
        s2 = convolve__vec2_float_bool(uv, deriv_y, divide)
        dist = rt.distance(s1, s2)
        color[:] = rt.binary("*", color, dist, 3, "float")
        return color
    def sobel__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        s1 = convolve__vec2_float_bool(uv, sobel_x, False)
        s2 = convolve__vec2_float_bool(uv, sobel_y, False)
        dist = rt.distance(s1, s2)
        color[:] = rt.binary("*", color, dist, 3, "float")
        return color
    def outline__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = desaturate__vec3(color)
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        s1 = convolve__vec2_float_bool(uv, sobel_x, False)
        s2 = convolve__vec2_float_bool(uv, sobel_y, False)
        dist = rt.distance(s1, s2)
        outcolor = rt.construct(3, rt.binary("-", color, dist, 3, 'float'))
        return rt.component_wise("max", outcolor, rt.f(0.0), width=3)
    def shadow__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.f(1.0)
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(3))] = rt.f(2.0)
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(6))] = rt.f(1.0)
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.f(1.0)
        sobel_y[int(rt.i(1))] = rt.f(2.0)
        sobel_y[int(rt.i(2))] = rt.f(1.0)
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(7))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(8))] = rt.unary("-", rt.f(1.0))
        color[:] = rgb2hsv__vec3(color)
        x = convolve__vec2_float_bool(uv, sobel_x, False)
        y = convolve__vec2_float_bool(uv, sobel_y, False)
        shade = rt.distance(x, y)
        highlight = rt.binary("*", shade, shade, 1, "float")
        shade = rt.binary("*", rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(color, "z"), 1, "float"), rt.binary("-", rt.f(1.0), highlight, 1, "float"), 1, "float"), 1, "float"), shade, 1, "float")
        alpha = rt.f(0.75)
        cpu_vector_assignment_0 = rt.construct(3, rt.swizzle(color, "x"), rt.swizzle(color, "y"), rt.component_wise("mix", rt.swizzle(color, "z"), shade, alpha, width=1))
        color[:] = cpu_vector_assignment_0
        return hsv2rgb__vec3(color)
    def convolutionEffect__vec3_vec2(color, uv):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        if rt.binary("==", _u_EFFECT, rt.i(1)):
            return convolve__vec2_float_bool(uv, g.blur, True)
        else:
            if rt.binary("==", _u_EFFECT, rt.i(2)):
                return derivatives__vec3_vec2_bool(color, uv, True)
            else:
                if rt.binary("==", _u_EFFECT, rt.i(120)):
                    return rt.component_wise("clamp", rt.construct(3, rt.binary("*", derivatives__vec3_vec2_bool(color, uv, False), rt.f(2.5), 3, 'float')), rt.f(0.0), rt.f(1.0), width=3)
                else:
                    if rt.binary("==", _u_EFFECT, rt.i(3)):
                        return rt.construct(3, rt.binary("*", color, convolve__vec2_float_bool(uv, g.edge2, True), 3, 'float'))
                    else:
                        if rt.binary("==", _u_EFFECT, rt.i(4)):
                            return convolve__vec2_float_bool(uv, g.emboss, False)
                        else:
                            if rt.binary("==", _u_EFFECT, rt.i(5)):
                                return outline__vec3_vec2(color, uv)
                            else:
                                if rt.binary("==", _u_EFFECT, rt.i(6)):
                                    return shadow__vec3_vec2(color, uv)
                                else:
                                    if rt.binary("==", _u_EFFECT, rt.i(7)):
                                        return convolve__vec2_float_bool(uv, g.sharpen, False)
                                    else:
                                        if rt.binary("==", _u_EFFECT, rt.i(8)):
                                            return sobel__vec3_vec2(color, uv)
                                        else:
                                            if rt.binary("==", _u_EFFECT, rt.i(9)):
                                                return rt.component_wise("max", color, convolve__vec2_float_bool(uv, g.edge2, True), width=3)
                                            else:
                                                if rt.binary("==", _u_EFFECT, rt.i(300)):
                                                    return convolve__vec2_float_bool(uv, g.sharpenBlur, True)
                                                else:
                                                    if rt.binary("==", _u_EFFECT, rt.i(301)):
                                                        return convolve__vec2_float_bool(uv, g.edge3, True)
                                                    else:
                                                        return color
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def f__vec2(st):
        st = rt.copy(st, "float")
        return random__vec2(rt.component_wise("floor", st, width=2))
    def bicubic__vec2(p):
        p = rt.copy(p, "float")
        x = rt.swizzle(p, "x")
        y = rt.swizzle(p, "y")
        x1 = rt.component_wise("floor", x, width=1)
        y1 = rt.component_wise("floor", y, width=1)
        x2 = rt.binary("+", x1, rt.f(1.0), 1, "float")
        y2 = rt.binary("+", y1, rt.f(1.0), 1, "float")
        f11 = f__vec2(rt.construct(2, x1, y1))
        f12 = f__vec2(rt.construct(2, x1, y2))
        f21 = f__vec2(rt.construct(2, x2, y1))
        f22 = f__vec2(rt.construct(2, x2, y2))
        f11x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), y1)), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), y1)), 1, "float"), rt.f(2.0), 1, "float")
        f12x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), y2)), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), y2)), 1, "float"), rt.f(2.0), 1, "float")
        f21x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), y1)), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), y1)), 1, "float"), rt.f(2.0), 1, "float")
        f22x = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), y2)), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), y2)), 1, "float"), rt.f(2.0), 1, "float")
        f11y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x1, rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x1, rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f12y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x1, rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x1, rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f21y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x2, rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x2, rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f22y = rt.binary("/", rt.binary("-", f__vec2(rt.construct(2, x2, rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, x2, rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(2.0), 1, "float")
        f11xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f12xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x1, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x1, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f21xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("+", y1, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("-", y1, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        f22xy = rt.binary("/", rt.binary("+", rt.binary("-", rt.binary("-", f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), f__vec2(rt.construct(2, rt.binary("+", x2, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("+", y2, rt.f(1.0), 1, "float"))), 1, "float"), f__vec2(rt.construct(2, rt.binary("-", x2, rt.f(1.0), 1, "float"), rt.binary("-", y2, rt.f(1.0), 1, "float"))), 1, "float"), rt.f(4.0), 1, "float")
        Q = rt.construct(16, f11, f21, f11x, f21x, f12, f22, f12x, f22x, f11y, f21y, f11xy, f21xy, f12y, f22y, f12xy, f22xy)
        S = rt.construct(16, rt.f(1.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(3.0)), rt.f(3.0), rt.unary("-", rt.f(2.0)), rt.unary("-", rt.f(1.0)), rt.f(2.0), rt.unary("-", rt.f(2.0)), rt.f(1.0), rt.f(1.0))
        _T = rt.construct(16, rt.f(1.0), rt.f(0.0), rt.unary("-", rt.f(3.0)), rt.f(2.0), rt.f(0.0), rt.f(0.0), rt.f(3.0), rt.unary("-", rt.f(2.0)), rt.f(0.0), rt.f(1.0), rt.unary("-", rt.f(2.0)), rt.f(1.0), rt.f(0.0), rt.f(0.0), rt.unary("-", rt.f(1.0)), rt.f(1.0))
        A = rt.matrix_mult(rt.matrix_mult(_T, Q, 4), S, 4)
        t = rt.component_wise("fract", rt.swizzle(p, "x"), width=1)
        u = rt.component_wise("fract", rt.swizzle(p, "y"), width=1)
        tv = rt.construct(4, rt.f(1.0), t, rt.binary("*", t, t, 1, "float"), rt.binary("*", rt.binary("*", t, t, 1, "float"), t, 1, "float"))
        uv = rt.construct(4, rt.f(1.0), u, rt.binary("*", u, u, 1, "float"), rt.binary("*", rt.binary("*", u, u, 1, "float"), u, 1, "float"))
        return rt.dot(rt.matrix_mult(tv, A, 4), uv)
    def cga__vec4_vec2(color, st):
        color = rt.copy(color, "float")
        st = rt.copy(st, "float")
        amt = map__float_float_float_float_float(_u_effectAmt, rt.f(0.0), rt.f(20.0), rt.f(0.0), rt.f(5.0))
        if rt.binary("<", amt, rt.f(0.01)):
            return rt.swizzle(color, "rgb")
        pixelDensity = rt.binary("*", amt, _u_renderScale, 1, "float")
        size = rt.binary("*", rt.f(2.0), pixelDensity, 1, "float")
        dSize = rt.binary("*", rt.f(2.0), size, 1, "float")
        amount = rt.binary("/", rt.swizzle(_u_fullResolution, "x"), size, 1, "float")
        d = rt.binary("/", rt.f(1.0), amount, 1, "float")
        ar = rt.fdiv(rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1)
        sx = rt.binary("*", rt.component_wise("floor", rt.binary("/", rt.swizzle(st, "x"), d, 1, "float"), width=1), d, 1, "float")
        d = rt.binary("/", ar, amount, 1, "float")
        sy = rt.binary("*", rt.component_wise("floor", rt.binary("/", rt.swizzle(st, "y"), d, 1, "float"), width=1), d, 1, "float")
        base = rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", rt.construct_raw(2, sx, sy), _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2)))
        lum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(base, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(base, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(base, "b"), 1, "float"), 1, "float")
        o = rt.component_wise("floor", rt.binary("*", rt.f(6.0), lum, 1, "float"), width=1)
        c1 = rt.construct(3, 0.0)
        c2 = rt.construct(3, 0.0)
        black = rt.construct(3, rt.f(0.0))
        light = rt.construct(3, rt.binary("/", rt.construct_raw(3, rt.f(85.0), rt.f(255.0), rt.f(255.0)), rt.f(255.0), 3, 'float'))
        dark = rt.construct(3, rt.binary("/", rt.construct_raw(3, rt.f(254.0), rt.f(84.0), rt.f(255.0)), rt.f(255.0), 3, 'float'))
        white = rt.construct(3, rt.f(1.0))
        if rt.binary("==", o, rt.f(0.0)):
            c1[:] = black
            c2[:] = c1
        if rt.binary("==", o, rt.f(1.0)):
            c1[:] = black
            c2[:] = dark
        if rt.binary("==", o, rt.f(2.0)):
            c1[:] = dark
            c2[:] = c1
        if rt.binary("==", o, rt.f(3.0)):
            c1[:] = dark
            c2[:] = light
        if rt.binary("==", o, rt.f(4.0)):
            c1[:] = light
            c2[:] = c1
        if rt.binary("==", o, rt.f(5.0)):
            c1[:] = light
            c2[:] = white
        if rt.binary("==", o, rt.f(6.0)):
            c1[:] = white
            c2[:] = c1
        if rt.binary(">", rt.component_wise("mod", rt.binary("+", rt.swizzle(ctx.frag_coord, "x"), rt.swizzle(_u_tileOffset, "x"), 1, "float"), dSize, width=1), size):
            if rt.binary(">", rt.component_wise("mod", rt.binary("+", rt.swizzle(ctx.frag_coord, "y"), rt.swizzle(_u_tileOffset, "y"), 1, "float"), dSize, width=1), size):
                base = rt.assign_swizzle(base, "rgb", c1)
            else:
                base = rt.assign_swizzle(base, "rgb", c2)
        else:
            if rt.binary(">", rt.component_wise("mod", rt.binary("+", rt.swizzle(ctx.frag_coord, "y"), rt.swizzle(_u_tileOffset, "y"), 1, "float"), dSize, width=1), size):
                base = rt.assign_swizzle(base, "rgb", c2)
            else:
                base = rt.assign_swizzle(base, "rgb", c1)
        return rt.swizzle(base, "rgb")
    def subpixel__vec2_float(st, scale):
        st = rt.copy(st, "float")
        scale = rt.binary("*", map__float_float_float_float_float(scale, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(10.0)), _u_renderScale, 1, "float")
        orig = pixellate__vec2_float(st, rt.binary("*", rt.f(4.0), scale, 1, "float"))
        color = rt.copy_decl(orig, "float")
        st[:] = rt.binary("*", st, _u_fullResolution, 2, "float")
        st[:] = rt.component_wise("floor", st, width=2)
        m = rt.component_wise("mod", rt.swizzle(st, "x"), rt.binary("*", rt.f(4.0), scale, 1, "float"), width=1)
        if rt.binary("<=", rt.component_wise("mod", rt.swizzle(st, "y"), rt.binary("*", rt.f(4.0), scale, 1, "float"), width=1), rt.binary("*", rt.f(1.0), scale, 1, "float")):
            color[:] = rt.binary("*", color, rt.construct(3, rt.f(0.0)), 3, "float")
        else:
            if rt.binary("<=", m, rt.binary("*", rt.f(1.0), scale, 1, "float")):
                color[:] = rt.binary("*", color, rt.construct(3, rt.f(1.0), rt.f(0.0), rt.f(0.0)), 3, "float")
            else:
                if rt.binary("<=", m, rt.binary("*", rt.f(2.0), scale, 1, "float")):
                    color[:] = rt.binary("*", color, rt.construct(3, rt.f(0.0), rt.f(1.0), rt.f(0.0)), 3, "float")
                else:
                    if rt.binary("<=", m, rt.binary("*", rt.f(3.0), scale, 1, "float")):
                        color[:] = rt.binary("*", color, rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0)), 3, "float")
                    else:
                        color[:] = rt.binary("*", color, rt.construct(3, rt.f(0.0)), 3, "float")
        factor = rt.component_wise("clamp", rt.binary("*", scale, rt.f(0.25), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.component_wise("mix", orig, color, factor, width=3)
    def bloom__vec2(st):
        st = rt.copy(st, "float")
        sum = rt.construct(3, rt.f(0.0))
        color = rt.construct(3, rt.f(0.0))
        orig = rt.swizzle(rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", st, _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))), "rgb")
        strength = map__float_float_float_float_float(_u_effectAmt, rt.f(0.0), rt.f(20.0), rt.f(0.0), rt.f(0.25))
        i = rt.unary("-", rt.i(4))
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, rt.i(4))):
                break
            j = rt.unary("-", rt.i(3))
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    j = rt.binary("+", j, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<", j, rt.i(3))):
                    break
                sum[:] = rt.binary("+", sum, rt.construct(3, rt.binary("*", rt.swizzle(rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", rt.binary("+", st, rt.binary("*", rt.construct_raw(2, rt.construct(1, j), rt.construct(1, i)), rt.f(0.004), 2, 'float'), 2, 'float'), _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2))), "rgb"), strength, 3, 'float')), 3, "float")
        if rt.binary("<", rt.swizzle(orig, "r"), rt.f(0.3)):
            color[:] = rt.binary("+", rt.binary("*", rt.binary("*", sum, sum, 3, 'float'), rt.f(0.012), 3, 'float'), orig, 3, 'float')
        else:
            if rt.binary("<", rt.swizzle(orig, "r"), rt.f(0.5)):
                color[:] = rt.binary("+", rt.binary("*", rt.binary("*", sum, sum, 3, 'float'), rt.f(0.009), 3, 'float'), orig, 3, 'float')
            else:
                color[:] = rt.binary("+", rt.binary("*", rt.binary("*", sum, sum, 3, 'float'), rt.f(0.0075), 3, 'float'), orig, 3, 'float')
        color[:] = rt.component_wise("clamp", color, rt.f(0.0), rt.f(1.0), width=3)
        return color
    def zoomBlur__vec2(st):
        st = rt.copy(st, "float")
        color = rt.construct(3, rt.f(0.0))
        total = rt.f(0.0)
        toCenter = rt.construct(2, rt.binary("-", st, rt.f(0.5), 2, 'float'))
        offset = rt.swizzle(prng__vec3(rt.construct(3, rt.f(12.9898), rt.f(78.233), rt.f(151.7182))), "x")
        products = rt.new_array(rt.i(41), 3)
        t = rt.f(0.0)
        _for3_first = True
        for _for3 in range(1048576):
            if not _for3_first:
                t = rt.binary("+", t, rt.i(1), 1, "float")
            _for3_first = False
            if not (rt.binary("<=", t, rt.f(40.0))):
                break
            percent = rt.binary("/", rt.binary("+", t, offset, 1, "float"), rt.f(40.0), 1, "float")
            percentSq = rt.component_wise("min", rt.component_wise("max", rt.binary("*", percent, percent, 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
            weight = rt.binary("*", rt.f(4.0), rt.binary("-", percent, percentSq, 1, "float"), 1, "float")
            strength = map__float_float_float_float_float(_u_effectAmt, rt.f(0.0), rt.f(20.0), rt.f(0.0), rt.f(1.0))
            tapA = rt.construct(2, rt.binary("*", toCenter, percent, 2, 'float'))
            tap = rt.construct(2, rt.binary("*", rt.component_wise("min", rt.component_wise("max", tapA, rt.construct(2, rt.unary("-", rt.f(1e+38))), width=2), rt.construct(2, rt.f(1e+38)), width=2), strength, 2, 'float'))
            tapB = rt.component_wise("min", rt.component_wise("max", tap, rt.construct(2, rt.unary("-", rt.f(1e+38))), width=2), rt.construct(2, rt.f(1e+38)), width=2)
            tapBudget = rt.construct(2, 0.0)
            if (bool(rt.binary("!=", rt.swizzle(_u_tileOffset, "x"), rt.f(0.0))) or bool(rt.binary("!=", rt.swizzle(_u_tileOffset, "y"), rt.f(0.0)))):
                tapBudget = rt.construct(2, rt.binary("*", rt.construct_raw(2, rt.f(256.0)), _u_invFullResolution, 2, 'float'))
                tapB[:] = rt.component_wise("min", rt.component_wise("max", tapB, rt.unary("-", tapBudget), width=2), tapBudget, width=2)
            tex = rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", rt.binary("+", st, tapB, 2, 'float'), _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2)))
            products[int(rt.construct(1, t, base="int"))] = rt.construct(3, rt.component_wise("min", rt.component_wise("max", rt.binary("*", rt.swizzle(tex, "rgb"), weight, 3, 'float'), rt.construct(3, rt.unary("-", rt.f(1e+38))), width=3), rt.construct(3, rt.f(1e+38)), width=3))
            total = rt.binary("+", total, rt.component_wise("min", rt.component_wise("max", weight, rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1), 1, "float")
        i = rt.i(0)
        _for4_first = True
        for _for4 in range(1048576):
            if not _for4_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for4_first = False
            if not (rt.binary("<", i, rt.i(41))):
                break
            color[:] = rt.binary("+", color, products[int(i)], 3, "float")
        r = rt.binary("/", rt.f(1.0), total, 1, "float")
        tr = rt.component_wise("min", rt.component_wise("max", rt.binary("*", total, r, 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        r = rt.binary("*", r, rt.binary("-", rt.f(2.0), tr, 1, "float"), 1, "float")
        color[:] = rt.binary("*", color, r, 3, "float")
        return color
    def offsets__vec2(st):
        st = rt.copy(st, "float")
        return rt.distance(st, rt.construct(2, rt.f(0.5)))
    def main__void():
        globalCoord = rt.construct(2, rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, 'float'))
        uv = rt.construct(2, rt.binary("*", globalCoord, _u_invFullResolution, 2, 'float'))
        color = rt.construct(4, rt.f(0.0))
        sR = rt.fdiv(rt.f(1.0), _u_scaleAmt, 1)
        sC = rt.component_wise("min", rt.component_wise("max", rt.binary("*", _u_scaleAmt, sR, 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        scale = rt.binary("*", rt.f(100.0), rt.binary("*", sR, rt.binary("-", rt.f(2.0), sC, 1, "float"), 1, "float"), 1, "float")
        if rt.binary("==", scale, rt.f(0.0)):
            scale = rt.f(1.0)
        uv[:] = rotate2D__vec2_float(uv, _u_rotation)
        uv[:] = rt.binary("-", uv, rt.f(0.5), 2, "float")
        uv[:] = rt.binary("*", uv, scale, 2, "float")
        uv[:] = rt.component_wise("min", rt.component_wise("max", uv, rt.construct(2, rt.unary("-", rt.f(1e+38))), width=2), rt.construct(2, rt.f(1e+38)), width=2)
        uv[:] = rt.binary("+", uv, rt.f(0.5), 2, "float")
        imageSize = rt.copy_decl(_u_fullResolution, "float")
        uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.swizzle(uv, "x"), rt.component_wise("ceil", rt.binary("-", rt.binary("*", scale, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.fdiv(rt.f(1.0), rt.swizzle(imageSize, "x"), 1), scale, 1, "float"), 1, "float"), 1, "float"), width=1), 1, "float"))
        uv = rt.assign_swizzle(uv, "y", rt.binary("+", rt.swizzle(uv, "y"), rt.component_wise("ceil", rt.binary("-", rt.binary("+", rt.binary("*", scale, rt.f(0.5), 1, "float"), rt.binary("-", rt.f(0.5), rt.binary("*", rt.fdiv(rt.f(1.0), rt.swizzle(imageSize, "y"), 1), scale, 1, "float"), 1, "float"), 1, "float"), scale, 1, "float"), width=1), 1, "float"))
        shiftXv = rt.component_wise("min", rt.component_wise("max", rt.binary("*", map__float_float_float_float_float(_u_offsetX, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", scale), scale), rt.f(1.5), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        shiftYv = rt.component_wise("min", rt.component_wise("max", rt.binary("*", map__float_float_float_float_float(_u_offsetY, rt.unary("-", rt.f(100.0)), rt.f(100.0), rt.unary("-", scale), scale), rt.f(1.5), 1, "float"), rt.unary("-", rt.f(1e+38)), width=1), rt.f(1e+38), width=1)
        uv[:] = rt.binary("-", uv, rt.construct(2, shiftXv, shiftYv), 2, "float")
        uv[:] = rt.component_wise("fract", uv, width=2)
        if rt.binary("==", _u_FLIP, rt.i(1)):
            uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
            uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
        else:
            if rt.binary("==", _u_FLIP, rt.i(2)):
                uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
            else:
                if rt.binary("==", _u_FLIP, rt.i(3)):
                    uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                else:
                    if rt.binary("==", _u_FLIP, rt.i(11)):
                        if rt.binary(">", rt.swizzle(uv, "x"), rt.f(0.5)):
                            uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                    else:
                        if rt.binary("==", _u_FLIP, rt.i(12)):
                            if rt.binary("<", rt.swizzle(uv, "x"), rt.f(0.5)):
                                uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                        else:
                            if rt.binary("==", _u_FLIP, rt.i(13)):
                                if rt.binary("<", rt.swizzle(uv, "y"), rt.f(0.5)):
                                    uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                            else:
                                if rt.binary("==", _u_FLIP, rt.i(14)):
                                    if rt.binary(">", rt.swizzle(uv, "y"), rt.f(0.5)):
                                        uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                                else:
                                    if rt.binary("==", _u_FLIP, rt.i(15)):
                                        if rt.binary(">", rt.swizzle(uv, "x"), rt.f(0.5)):
                                            uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                                        if rt.binary("<", rt.swizzle(uv, "y"), rt.f(0.5)):
                                            uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                                    else:
                                        if rt.binary("==", _u_FLIP, rt.i(16)):
                                            if rt.binary(">", rt.swizzle(uv, "x"), rt.f(0.5)):
                                                uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                                            if rt.binary(">", rt.swizzle(uv, "y"), rt.f(0.5)):
                                                uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                                        else:
                                            if rt.binary("==", _u_FLIP, rt.i(17)):
                                                if rt.binary("<", rt.swizzle(uv, "x"), rt.f(0.5)):
                                                    uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                                                if rt.binary("<", rt.swizzle(uv, "y"), rt.f(0.5)):
                                                    uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
                                            else:
                                                if rt.binary("==", _u_FLIP, rt.i(18)):
                                                    if rt.binary("<", rt.swizzle(uv, "x"), rt.f(0.5)):
                                                        uv = rt.assign_swizzle(uv, "x", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "x"), 1, "float"))
                                                    if rt.binary(">", rt.swizzle(uv, "y"), rt.f(0.5)):
                                                        uv = rt.assign_swizzle(uv, "y", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"))
        loadKernels__void()
        blendy = periodicFunction__float(rt.binary("-", _u_time, offsets__vec2(uv), 1, "float"))
        origUV = rt.copy_decl(uv, "float")
        origcolor = rt.texture(_u_inputTex, rt.construct(2, rt.fdiv(rt.construct(2, rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, 'float'), _u_tileOffset, 2, 'float')), rt.construct(2, rt.texture_size(_u_inputTex)), 2)))
        color[:] = origcolor
        if rt.binary("!=", _u_EFFECT, rt.i(0)):
            if rt.binary("!=", _u_effectAmt, rt.f(0.0)):
                if rt.binary("==", _u_EFFECT, rt.i(100)):
                    color = rt.assign_swizzle(color, "rgb", pixellate__vec2_float(uv, _u_effectAmt))
                else:
                    if rt.binary("==", _u_EFFECT, rt.i(110)):
                        color = rt.assign_swizzle(color, "rgb", posterize__vec3_float(rt.swizzle(color, "rgb"), _u_effectAmt))
                    else:
                        if rt.binary("==", _u_EFFECT, rt.i(200)):
                            color = rt.assign_swizzle(color, "rgb", cga__vec4_vec2(color, uv))
                        else:
                            if rt.binary("==", _u_EFFECT, rt.i(210)):
                                color = rt.assign_swizzle(color, "rgb", subpixel__vec2_float(uv, _u_effectAmt))
                            else:
                                if rt.binary("==", _u_EFFECT, rt.i(220)):
                                    color = rt.assign_swizzle(color, "rgb", bloom__vec2(uv))
                                else:
                                    if rt.binary("==", _u_EFFECT, rt.i(230)):
                                        color = rt.assign_swizzle(color, "rgb", zoomBlur__vec2(uv))
                                    else:
                                        color = rt.assign_swizzle(color, "rgb", convolutionEffect__vec3_vec2(rt.swizzle(color, "rgb"), uv))
        color = rt.assign_swizzle(color, "rgb", brightnessContrast__vec3(rt.swizzle(color, "rgb")))
        color = rt.assign_swizzle(color, "rgb", saturate__vec3(rt.swizzle(color, "rgb")))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
