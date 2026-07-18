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
    _u_patternType = U.get("patternType", 0)
    _u_scale = U.get("scale", rt.f(0.0))
    _u_thickness = U.get("thickness", rt.f(0.0))
    _u_smoothness = U.get("smoothness", rt.f(0.0))
    _u_rotation = U.get("rotation", rt.f(0.0))
    _u_invert = U.get("invert", 0)
    g.fragColor = rt.construct(4, 0.0)
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(p, "y"), c, 1, "float"), 1, "float"))
    def stripes__vec2_float(p, t):
        p = rt.copy(p, "float")
        stripe = rt.component_wise("fract", rt.swizzle(p, "x"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), stripe, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), stripe, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def checkerboard__vec2_float(p, sm):
        p = rt.copy(p, "float")
        f = rt.component_wise("fract", p, width=2)
        d = rt.component_wise("min", rt.component_wise("min", rt.swizzle(f, "x"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), width=1), rt.component_wise("min", rt.swizzle(f, "y"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "y"), 1, "float"), width=1), width=1)
        cell = rt.component_wise("floor", p, width=2)
        check = rt.component_wise("mod", rt.binary("+", rt.swizzle(cell, "x"), rt.swizzle(cell, "y"), 1, "float"), rt.f(2.0), width=1)
        edge = rt.component_wise("smoothstep", rt.f(0.0), rt.binary("*", sm, rt.f(0.5), 1, "float"), d, width=1)
        return rt.component_wise("mix", rt.binary("-", rt.f(1.0), check, 1, "float"), check, edge, width=1)
    def grid__vec2_float(p, t):
        p = rt.copy(p, "float")
        f = rt.component_wise("fract", p, width=2)
        lineX = rt.component_wise("smoothstep", rt.binary("-", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.component_wise("abs", rt.binary("-", rt.swizzle(f, "x"), rt.f(0.5), 1, "float"), width=1), width=1)
        lineY = rt.component_wise("smoothstep", rt.binary("-", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("*", t, rt.f(0.5), 1, "float"), _u_smoothness, 1, "float"), rt.component_wise("abs", rt.binary("-", rt.swizzle(f, "y"), rt.f(0.5), 1, "float"), width=1), width=1)
        return rt.binary("-", rt.f(1.0), rt.component_wise("min", lineX, lineY, width=1), 1, "float")
    def dots__vec2_float(p, t):
        p = rt.copy(p, "float")
        f = rt.binary("-", rt.component_wise("fract", p, width=2), rt.f(0.5), 2, "float")
        d = rt.length(f)
        radius = rt.binary("*", t, rt.f(0.5), 1, "float")
        return rt.binary("-", rt.f(1.0), rt.component_wise("smoothstep", rt.binary("-", radius, _u_smoothness, 1, "float"), rt.binary("+", radius, _u_smoothness, 1, "float"), d, width=1), 1, "float")
    def hexDist__vec2(p):
        p = rt.copy(p, "float")
        p[:] = rt.component_wise("abs", p, width=2)
        return rt.component_wise("max", rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.f(0.5), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.binary("/", rt.f(1.7320508075688772), rt.f(2.0), 1, "float"), 1, "float"), 1, "float"), rt.swizzle(p, "x"), width=1)
    def hexagons__vec2_float(p, t):
        p = rt.copy(p, "float")
        s = rt.construct(2, rt.f(1.0), rt.f(1.7320508075688772))
        h = rt.binary("*", s, rt.f(0.5), 2, "float")
        a = rt.binary("-", rt.component_wise("mod", p, s, width=2), h, 2, "float")
        b = rt.binary("-", rt.component_wise("mod", rt.binary("+", p, h, 2, "float"), s, width=2), h, 2, "float")
        _g = (a if rt.binary("<", rt.length(a), rt.length(b)) else b)
        d = hexDist__vec2(_g)
        edge = rt.binary("*", rt.f(0.5), t, 1, "float")
        return rt.component_wise("smoothstep", rt.binary("+", edge, _u_smoothness, 1, "float"), rt.binary("-", edge, _u_smoothness, 1, "float"), d, width=1)
    def concentricRings__vec2_float(p, t):
        p = rt.copy(p, "float")
        d = rt.component_wise("fract", rt.length(p), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def radialLines__vec2_float(p, t):
        p = rt.copy(p, "float")
        lineCount = rt.component_wise("max", rt.f(1.0), rt.component_wise("floor", rt.binary("*", rt.f(20.0), t, 1, "float"), width=1), width=1)
        angle = rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1)
        d = rt.component_wise("fract", rt.binary("*", rt.binary("/", angle, rt.f(6.28318530718), 1, "float"), lineCount, 1, "float"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.f(0.25), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.f(0.25), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.f(0.25), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.f(0.25), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def triangularGrid__vec2_float(p, t):
        p = rt.copy(p, "float")
        skewed = rt.construct(2, rt.binary("-", rt.swizzle(p, "x"), rt.binary("/", rt.swizzle(p, "y"), rt.f(1.7320508075688772), 1, "float"), 1, "float"), rt.binary("/", rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float"), rt.f(1.7320508075688772), 1, "float"))
        cell = rt.component_wise("floor", skewed, width=2)
        f = rt.component_wise("fract", skewed, width=2)
        d = rt.f(0.0)
        if rt.binary("<", rt.binary("+", rt.swizzle(f, "x"), rt.swizzle(f, "y"), 1, "float"), rt.f(1.0)):
            d = rt.component_wise("min", rt.component_wise("min", rt.swizzle(f, "x"), rt.swizzle(f, "y"), width=1), rt.binary("-", rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), rt.swizzle(f, "y"), 1, "float"), width=1)
        else:
            d = rt.component_wise("min", rt.component_wise("min", rt.binary("-", rt.f(1.0), rt.swizzle(f, "x"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(f, "y"), 1, "float"), width=1), rt.binary("-", rt.binary("+", rt.swizzle(f, "x"), rt.swizzle(f, "y"), 1, "float"), rt.f(1.0), 1, "float"), width=1)
        edge = rt.binary("*", rt.binary("-", rt.f(1.0), t, 1, "float"), rt.f(0.4), 1, "float")
        return rt.component_wise("smoothstep", rt.binary("-", edge, _u_smoothness, 1, "float"), rt.binary("+", edge, _u_smoothness, 1, "float"), d, width=1)
    def spiralPattern__vec2_float(p, t):
        p = rt.copy(p, "float")
        dist = rt.length(p)
        angle = rt.component_wise("atan", rt.swizzle(p, "y"), rt.swizzle(p, "x"), width=1)
        d = rt.component_wise("fract", rt.binary("+", rt.binary("/", angle, rt.f(6.28318530718), 1, "float"), dist, 1, "float"), width=1)
        edge1 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("-", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        edge2 = rt.component_wise("smoothstep", rt.binary("-", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), rt.binary("+", rt.binary("+", rt.f(0.5), rt.binary("*", t, rt.f(0.5), 1, "float"), 1, "float"), _u_smoothness, 1, "float"), d, width=1)
        return rt.binary("-", edge1, edge2, 1, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2, "float"))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        p = rt.binary("*", rt.binary("-", globalUV, rt.f(0.5), 2, "float"), rt.f(2.0), 2, "float")
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspect, 1, "float"))
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1, "float"), rt.f(180.0), 1, "float")
        p[:] = rotate2D__vec2_float(p, rad)
        p[:] = rt.binary("*", p, rt.binary("-", rt.f(21.0), _u_scale, 1, "float"), 2, "float")
        m = rt.f(0.0)
        if rt.binary("==", _u_patternType, rt.i(0)):
            m = checkerboard__vec2_float(p, _u_smoothness)
        else:
            if rt.binary("==", _u_patternType, rt.i(1)):
                m = concentricRings__vec2_float(p, _u_thickness)
            else:
                if rt.binary("==", _u_patternType, rt.i(2)):
                    m = dots__vec2_float(p, _u_thickness)
                else:
                    if rt.binary("==", _u_patternType, rt.i(3)):
                        m = grid__vec2_float(p, _u_thickness)
                    else:
                        if rt.binary("==", _u_patternType, rt.i(4)):
                            m = hexagons__vec2_float(p, _u_thickness)
                        else:
                            if rt.binary("==", _u_patternType, rt.i(5)):
                                m = radialLines__vec2_float(p, _u_thickness)
                            else:
                                if rt.binary("==", _u_patternType, rt.i(6)):
                                    m = spiralPattern__vec2_float(p, _u_thickness)
                                else:
                                    if rt.binary("==", _u_patternType, rt.i(7)):
                                        m = stripes__vec2_float(p, _u_thickness)
                                    else:
                                        if rt.binary("==", _u_patternType, rt.i(8)):
                                            m = triangularGrid__vec2_float(p, _u_thickness)
        if rt.binary("==", _u_invert, rt.i(1)):
            m = rt.binary("-", rt.f(1.0), m, 1, "float")
        color = rt.component_wise("mix", colorA, colorB, m, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), width=1))
        g.fragColor[:] = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
