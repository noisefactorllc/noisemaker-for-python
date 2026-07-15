def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U["resolution"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_renderScale = U["renderScale"]
    _u_time = U["time"]
    _u_operation = U["operation"]
    _u_scale = U["scale"]
    _u_offsetX = U["offsetX"]
    _u_offsetY = U["offsetY"]
    _u_mask = U["mask"]
    _u_seed = U["seed"]
    _u_colorMode = U["colorMode"]
    _u_speed = U["speed"]
    _u_rotation = U["rotation"]
    _u_colorOffset = U["colorOffset"]
    g.PI = rt.f(3.14159265358979)
    def hsv2rgb__vec3(c):
        c = rt.copy(c)
        p = rt.component_wise("abs", rt.binary("-", rt.binary("*", rt.component_wise("fract", rt.binary("+", rt.swizzle(c, "xxx"), rt.construct(3, rt.f(1.0), rt.binary("/", rt.f(2.0), rt.f(3.0), 1, "float"), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float")), 3, "float"), width=3), rt.f(6.0), 3, "float"), rt.f(3.0), 3, "float"), width=3)
        return rt.binary("*", rt.swizzle(c, "z"), rt.component_wise("mix", rt.construct(3, rt.f(1.0)), rt.component_wise("clamp", rt.binary("-", p, rt.f(1.0), 3, "float"), rt.f(0.0), rt.f(1.0), width=3), rt.swizzle(c, "y"), width=3), 3, "float")
    def bitOp__int_int_int_int(a, b, op, m):
        r = rt.i(0)
        if rt.binary("==", op, rt.i(0)):
            r = rt.binary("^", a, b, 1, "int")
        else:
            if rt.binary("==", op, rt.i(1)):
                r = rt.binary("&", a, b, 1, "int")
            else:
                if rt.binary("==", op, rt.i(2)):
                    r = rt.binary("|", a, b, 1, "int")
                else:
                    if rt.binary("==", op, rt.i(3)):
                        r = rt.bit_not(rt.binary("&", a, b, 1, "int"))
                    else:
                        if rt.binary("==", op, rt.i(4)):
                            r = rt.bit_not(rt.binary("^", a, b, 1, "int"))
                        else:
                            if rt.binary("==", op, rt.i(5)):
                                r = rt.binary("*", a, b, 1, "int")
                            else:
                                if rt.binary("==", op, rt.i(6)):
                                    r = rt.binary("+", a, b, 1, "int")
                                else:
                                    r = rt.binary("-", a, b, 1, "int")
        r = rt.binary("&", r, m, 1, "int")
        return rt.binary("/", rt.construct(1, r), rt.construct(1, m), 1, "float")
    def main__void():
        pixelScale = rt.binary("*", rt.binary("*", _u_scale, rt.f(0.1), 1, "float"), _u_renderScale, 1, "float")
        angle = rt.binary("/", rt.binary("*", _u_rotation, g.PI, 1, "float"), rt.f(180.0), 1, "float")
        c = rt.component_wise("cos", angle, width=1)
        s = rt.component_wise("sin", angle, width=1)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        centered = rt.binary("-", globalCoord, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2, "float")
        rotated = rt.construct(2, rt.binary("-", rt.binary("*", rt.swizzle(centered, "x"), c, 1, "float"), rt.binary("*", rt.swizzle(centered, "y"), s, 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", rt.swizzle(centered, "x"), s, 1, "float"), rt.binary("*", rt.swizzle(centered, "y"), c, 1, "float"), 1, "float"))
        coord = rt.binary("+", rotated, rt.binary("*", _u_fullResolution, rt.f(0.5), 2, "float"), 2, "float")
        animOffset = rt.construct(1, rt.component_wise("floor", rt.binary("*", rt.binary("*", _u_time, rt.construct(1, rt.construct(1, rt.unary("-", _u_speed), base="int")), 1, "float"), rt.f(256.0), 1, "float"), width=1), base="int")
        x = rt.binary("+", rt.binary("+", rt.construct(1, rt.component_wise("floor", rt.binary("/", rt.swizzle(coord, "x"), pixelScale, 1, "float"), width=1), base="int"), _u_offsetX, 1, "int"), animOffset, 1, "int")
        y = rt.binary("+", rt.construct(1, rt.component_wise("floor", rt.binary("/", rt.swizzle(coord, "y"), pixelScale, 1, "float"), width=1), base="int"), _u_offsetY, 1, "int")
        x = rt.binary("^", x, _u_seed, 1, "int")
        y = rt.binary("^", y, rt.binary("*", _u_seed, rt.i(3), 1, "int"), 1, "int")
        v = rt.f(0.0)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            v = bitOp__int_int_int_int(x, y, _u_operation, _u_mask)
            g.fragColor = rt.construct(4, v, v, v, rt.f(1.0))
        else:
            if rt.binary("==", _u_colorMode, rt.i(1)):
                r = bitOp__int_int_int_int(x, y, _u_operation, _u_mask)
                g = bitOp__int_int_int_int(rt.binary("+", x, _u_colorOffset, 1, "int"), y, _u_operation, _u_mask)
                b = bitOp__int_int_int_int(x, rt.binary("+", y, _u_colorOffset, 1, "int"), _u_operation, _u_mask)
                g.fragColor = rt.construct(4, r, g, b, rt.f(1.0))
            else:
                v = bitOp__int_int_int_int(x, y, _u_operation, _u_mask)
                hueScale = rt.binary("/", rt.construct(1, _u_mask), rt.construct(1, rt.binary("+", _u_mask, rt.i(1), 1, "int")), 1, "float")
                g.fragColor = rt.construct(4, hsv2rgb__vec3(rt.construct(3, rt.binary("*", v, hueScale, 1, "float"), rt.f(1.0), rt.f(1.0))), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
