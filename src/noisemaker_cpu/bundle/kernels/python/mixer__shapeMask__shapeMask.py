def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tex = T["tex"]
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_shape = U["shape"]
    _u_radius = U["radius"]
    _u_edgeSmooth = U["edgeSmooth"]
    _u_rotation = U["rotation"]
    _u_posX = U["posX"]
    _u_posY = U["posY"]
    _u_invert = U["invert"]
    _u_speed = U["speed"]
    _u_time = U["time"]
    def rotate2D__vec2_float(p, angle):
        p = rt.copy(p)
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        return rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), c, 1), rt.binary("*", rt.swizzle(p, "y"), s, 1), 1), rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), s, 1), rt.binary("*", rt.swizzle(p, "y"), c, 1), 1))
    def sdfCircle__vec2_float(p, r):
        p = rt.copy(p)
        return rt.binary("-", rt.length(p), r, 1)
    def sdfPolygon__vec2_float_float(p, r, sides):
        p = rt.copy(p)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(p, "x"), rt.swizzle(p, "y"), width=1), rt.f(3.14159265359), 1)
        seg = rt.binary("/", rt.f(6.28318530718), sides, 1)
        return rt.binary("-", rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, seg, 1), 1), width=1), seg, 1), a, 1), width=1), rt.length(p), 1), r, 1)
    def sdfTriangle__vec2_float(p, r):
        p = rt.copy(p)
        k = rt.f(1.732050808)
        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.component_wise("abs", rt.swizzle(p, "x"), width=1), r, 1))
        p = rt.assign_swizzle(p, "y", rt.binary("+", rt.swizzle(p, "y"), rt.binary("/", r, k, 1), 1))
        if rt.binary(">", rt.binary("+", rt.swizzle(p, "x"), rt.binary("*", k, rt.swizzle(p, "y"), 1), 1), rt.f(0.0)):
            p = rt.binary("/", rt.construct(2, rt.binary("-", rt.swizzle(p, "x"), rt.binary("*", k, rt.swizzle(p, "y"), 1), 1), rt.binary("-", rt.binary("*", rt.unary("-", k), rt.swizzle(p, "x"), 1), rt.swizzle(p, "y"), 1)), rt.f(2.0), 2)
        p = rt.assign_swizzle(p, "x", rt.binary("-", rt.swizzle(p, "x"), rt.component_wise("clamp", rt.swizzle(p, "x"), rt.binary("*", rt.unary("-", rt.f(2.0)), r, 1), rt.f(0.0), width=1), 1))
        return rt.binary("*", rt.unary("-", rt.length(p)), rt.component_wise("sign", rt.swizzle(p, "y"), width=1), 1)
    def sdfFlower__vec2_float(p, r):
        p = rt.copy(p)
        outerR = r
        innerR = rt.binary("*", r, rt.f(0.45), 1)
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(p, "x"), rt.swizzle(p, "y"), width=1), rt.f(3.14159265359), 1)
        seg = rt.binary("/", rt.f(6.28318530718), rt.f(5.0), 1)
        halfSeg = rt.binary("*", seg, rt.f(0.5), 1)
        segAngle = rt.component_wise("mod", a, seg, width=1)
        t = rt.binary("/", rt.component_wise("abs", rt.binary("-", segAngle, halfSeg, 1), width=1), halfSeg, 1)
        starR = rt.component_wise("mix", innerR, outerR, t, width=1)
        return rt.binary("-", rt.length(p), starR, 1)
    def sdfStar5__vec2_float(p, r):
        p = rt.copy(p)
        rf = rt.f(0.4)
        k1 = rt.construct(2, rt.f(0.809016994375), rt.unary("-", rt.f(0.587785252292)))
        k2 = rt.construct(2, rt.unary("-", rt.swizzle(k1, "x")), rt.swizzle(k1, "y"))
        p = rt.assign_swizzle(p, "x", rt.component_wise("abs", rt.swizzle(p, "x"), width=1))
        p = rt.binary("-", p, rt.binary("*", rt.binary("*", rt.f(2.0), rt.component_wise("max", rt.dot(k1, p), rt.f(0.0), width=1), 1), k1, 2), 2)
        p = rt.binary("-", p, rt.binary("*", rt.binary("*", rt.f(2.0), rt.component_wise("max", rt.dot(k2, p), rt.f(0.0), width=1), 1), k2, 2), 2)
        p = rt.assign_swizzle(p, "x", rt.component_wise("abs", rt.swizzle(p, "x"), width=1))
        p = rt.assign_swizzle(p, "y", rt.binary("-", rt.swizzle(p, "y"), r, 1))
        ba = rt.binary("-", rt.binary("*", rf, rt.construct(2, rt.unary("-", rt.swizzle(k1, "y")), rt.swizzle(k1, "x")), 2), rt.construct(2, rt.f(0.0), rt.f(1.0)), 2)
        h = rt.component_wise("clamp", rt.binary("/", rt.dot(p, ba), rt.dot(ba, ba), 1), rt.f(0.0), r, width=1)
        return rt.binary("*", rt.length(rt.binary("-", p, rt.binary("*", ba, h, 2), 2)), rt.component_wise("sign", rt.binary("-", rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(ba, "x"), 1), rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(ba, "y"), 1), 1), width=1), 1)
    def sdfRing__vec2_float(p, r):
        p = rt.copy(p)
        ringWidth = rt.binary("*", r, rt.f(0.15), 1)
        return rt.binary("-", rt.component_wise("abs", rt.binary("-", rt.length(p), r, 1), width=1), ringWidth, 1)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        st = rt.binary("/", globalCoord, _u_fullResolution, 2)
        colorA = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2))
        colorB = rt.texture(_u_tex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_tex)), 2))
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        aspect = rt.binary("/", rt.swizzle(fullRes, "x"), rt.swizzle(fullRes, "y"), 1)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2), fullRes, 2)
        p = rt.binary("*", rt.binary("-", globalUV, rt.f(0.5), 2), rt.f(2.0), 2)
        p = rt.assign_swizzle(p, "x", rt.binary("*", rt.swizzle(p, "x"), aspect, 1))
        p = rt.binary("-", p, rt.construct(2, rt.binary("*", _u_posX, aspect, 1), rt.unary("-", _u_posY)), 2)
        rad = rt.binary("/", rt.binary("*", _u_rotation, rt.f(3.14159265359), 1), rt.f(180.0), 1)
        p = rotate2D__vec2_float(p, rad)
        r = _u_radius
        if rt.binary(">", _u_speed, rt.i(0)):
            r = rt.binary("+", rt.binary("*", _u_radius, rt.f(0.5), 1), rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), _u_speed, 1), width=1), _u_radius, 1), rt.f(0.5), 1), 1)
        d = rt.f(0.0)
        if rt.binary("==", _u_shape, rt.i(0)):
            d = sdfCircle__vec2_float(p, r)
        else:
            if rt.binary("==", _u_shape, rt.i(1)):
                d = sdfTriangle__vec2_float(p, r)
            else:
                if rt.binary("==", _u_shape, rt.i(2)):
                    d = sdfPolygon__vec2_float_float(p, r, rt.f(4.0))
                else:
                    if rt.binary("==", _u_shape, rt.i(3)):
                        d = sdfPolygon__vec2_float_float(p, r, rt.f(5.0))
                    else:
                        if rt.binary("==", _u_shape, rt.i(4)):
                            d = sdfPolygon__vec2_float_float(p, r, rt.f(6.0))
                        else:
                            if rt.binary("==", _u_shape, rt.i(5)):
                                d = sdfFlower__vec2_float(p, r)
                            else:
                                if rt.binary("==", _u_shape, rt.i(6)):
                                    d = sdfRing__vec2_float(p, r)
                                else:
                                    if rt.binary("==", _u_shape, rt.i(7)):
                                        d = sdfStar5__vec2_float(p, r)
        mask = rt.component_wise("smoothstep", rt.unary("-", _u_edgeSmooth), _u_edgeSmooth, d, width=1)
        if rt.binary("==", _u_invert, rt.i(1)):
            mask = rt.binary("-", rt.f(1.0), mask, 1)
        color = rt.component_wise("mix", colorA, colorB, mask, width=4)
        color = rt.assign_swizzle(color, "a", rt.component_wise("max", rt.swizzle(colorA, "a"), rt.swizzle(colorB, "a"), width=1))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
