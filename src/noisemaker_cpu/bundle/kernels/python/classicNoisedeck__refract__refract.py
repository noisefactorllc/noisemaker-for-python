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
    _u_mode = U.get("mode", 0)
    _u_amount = U.get("amount", rt.f(0.0))
    _u_direction = U.get("direction", rt.f(0.0))
    _u_blendMode = U.get("blendMode", 0)
    _u_mixAmt = U.get("mixAmt", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    g.fragColor = rt.construct(4, 0.0)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def convolve__vec2_float_bool(uv, kernel, divide):
        uv = rt.copy(uv, "float")
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        steps = rt.binary("/", rt.f(1.0), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        offset = rt.new_array(rt.i(9), 2)
        offset[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(2))] = rt.construct(2, rt.swizzle(steps, "x"), rt.unary("-", rt.swizzle(steps, "y")))
        offset[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.f(0.0))
        offset[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offset[int(rt.i(5))] = rt.construct(2, rt.swizzle(steps, "x"), rt.f(0.0))
        offset[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(steps, "x")), rt.swizzle(steps, "y"))
        offset[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(steps, "y"))
        offset[int(rt.i(8))] = rt.construct(2, rt.swizzle(steps, "x"), rt.swizzle(steps, "y"))
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
            color = rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", localUV, rt.binary("*", offset[int(i)], rt.component_wise("floor", map__float_float_float_float_float(_u_amount, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(20.0)), width=1), 2, "float"), 2, "float")), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", color, kernel[int(i)], 3, "float"), 3, "float")
            kernelWeight = rt.binary("+", kernelWeight, kernel[int(i)], 1, "float")
        if divide:
            conv = rt.assign_swizzle(conv, "rgb", rt.binary("/", rt.swizzle(conv, "rgb"), kernelWeight, 3, "float"))
        return rt.component_wise("clamp", rt.swizzle(conv, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
    def desaturate__vec3(color):
        color = rt.copy(color, "float")
        return rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
    def derivX__vec3_vec2_bool(color, uv, divide):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = rt.construct(3, desaturate__vec3(color))
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
        s1 = convolve__vec2_float_bool(uv, deriv_x, divide)
        return s1
    def derivY__vec3_vec2_bool(color, uv, divide):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        dcolor = rt.construct(3, desaturate__vec3(color))
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
        s2 = convolve__vec2_float_bool(uv, deriv_y, divide)
        return s2
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def blendOverlay__float_float(a, b):
        return (rt.binary("*", rt.binary("*", rt.f(2.0), a, 1, "float"), b, 1, "float") if rt.binary("<", a, rt.f(0.5)) else rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("*", rt.f(2.0), rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), rt.binary("-", rt.f(1.0), b, 1, "float"), 1, "float"), 1, "float"))
    def blendSoftLight__float_float(base, blend):
        return (rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), blend, 1, "float"), rt.binary("*", rt.binary("*", base, base, 1, "float"), rt.binary("-", rt.f(1.0), rt.binary("*", rt.f(2.0), blend, 1, "float"), 1, "float"), 1, "float"), 1, "float") if rt.binary("<", blend, rt.f(0.5)) else rt.binary("+", rt.binary("*", rt.component_wise("sqrt", base, width=1), rt.binary("-", rt.binary("*", rt.f(2.0), blend, 1, "float"), rt.f(1.0), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), base, 1, "float"), rt.binary("-", rt.f(1.0), blend, 1, "float"), 1, "float"), 1, "float"))
    def blend__vec4_vec4(color1, color2):
        color1 = rt.copy(color1, "float")
        color2 = rt.copy(color2, "float")
        color = rt.construct(4, 0.0)
        middle = rt.construct(4, 0.0)
        amt = map__float_float_float_float_float(_u_mixAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(1.0))
        if rt.binary("==", _u_blendMode, rt.i(0)):
            middle = rt.component_wise("min", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), width=4)
        else:
            if rt.binary("==", _u_blendMode, rt.i(2)):
                middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(0.0))) else rt.component_wise("max", rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", rt.f(1.0), color1, 4, "float"), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(0.0)), width=4))
            else:
                if rt.binary("==", _u_blendMode, rt.i(3)):
                    middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", color1, rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                else:
                    if rt.binary("==", _u_blendMode, rt.i(4)):
                        middle = rt.component_wise("min", color1, color2, width=4)
                    else:
                        if rt.binary("==", _u_blendMode, rt.i(5)):
                            middle = rt.component_wise("abs", rt.binary("-", color1, color2, 4, "float"), width=4)
                        else:
                            if rt.binary("==", _u_blendMode, rt.i(6)):
                                middle = rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.binary("*", rt.binary("*", rt.f(2.0), color1, 4, "float"), color2, 4, "float"), 4, "float")
                            else:
                                if rt.binary("==", _u_blendMode, rt.i(7)):
                                    middle = (color2 if rt.binary("==", color2, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color1, color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                else:
                                    if rt.binary("==", _u_blendMode, rt.i(8)):
                                        middle = rt.construct(4, blendOverlay__float_float(rt.swizzle(color2, "r"), rt.swizzle(color1, "r")), blendOverlay__float_float(rt.swizzle(color2, "g"), rt.swizzle(color1, "g")), blendOverlay__float_float(rt.swizzle(color2, "b"), rt.swizzle(color1, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                    else:
                                        if rt.binary("==", _u_blendMode, rt.i(9)):
                                            middle = rt.component_wise("max", color1, color2, width=4)
                                        else:
                                            if rt.binary("==", _u_blendMode, rt.i(10)):
                                                middle = rt.component_wise("mix", color1, color2, rt.f(0.5), width=4)
                                            else:
                                                if rt.binary("==", _u_blendMode, rt.i(11)):
                                                    middle = rt.binary("*", color1, color2, 4, "float")
                                                else:
                                                    if rt.binary("==", _u_blendMode, rt.i(12)):
                                                        middle = rt.binary("-", rt.construct(4, rt.f(1.0)), rt.component_wise("abs", rt.binary("-", rt.binary("-", rt.construct(4, rt.f(1.0)), color1, 4, "float"), color2, 4, "float"), width=4), 4, "float")
                                                    else:
                                                        if rt.binary("==", _u_blendMode, rt.i(13)):
                                                            middle = rt.construct(4, blendOverlay__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendOverlay__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendOverlay__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                                        else:
                                                            if rt.binary("==", _u_blendMode, rt.i(14)):
                                                                middle = rt.binary("+", rt.binary("-", rt.component_wise("min", color1, color2, width=4), rt.component_wise("max", color1, color2, width=4), 4, "float"), rt.construct(4, rt.f(1.0)), 4, "float")
                                                            else:
                                                                if rt.binary("==", _u_blendMode, rt.i(15)):
                                                                    middle = (color1 if rt.binary("==", color1, rt.construct(4, rt.f(1.0))) else rt.component_wise("min", rt.binary("/", rt.binary("*", color2, color2, 4, "float"), rt.binary("-", rt.f(1.0), color1, 4, "float"), 4, "float"), rt.construct(4, rt.f(1.0)), width=4))
                                                                else:
                                                                    if rt.binary("==", _u_blendMode, rt.i(16)):
                                                                        middle = rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), color1, 4, "float"), rt.binary("-", rt.f(1.0), color2, 4, "float"), 4, "float"), 4, "float")
                                                                    else:
                                                                        if rt.binary("==", _u_blendMode, rt.i(17)):
                                                                            middle = rt.construct(4, blendSoftLight__float_float(rt.swizzle(color1, "r"), rt.swizzle(color2, "r")), blendSoftLight__float_float(rt.swizzle(color1, "g"), rt.swizzle(color2, "g")), blendSoftLight__float_float(rt.swizzle(color1, "b"), rt.swizzle(color2, "b")), rt.component_wise("mix", rt.swizzle(color1, "a"), rt.swizzle(color2, "a"), rt.f(0.5), width=1))
                                                                        else:
                                                                            if rt.binary("==", _u_blendMode, rt.i(18)):
                                                                                middle = rt.component_wise("max", rt.binary("-", rt.binary("+", color1, color2, 4, "float"), rt.f(1.0), 4, "float"), rt.f(0.0), width=4)
        if rt.binary("==", amt, rt.f(0.5)):
            color = middle
        else:
            if rt.binary("<", amt, rt.f(0.5)):
                amt = map__float_float_float_float_float(amt, rt.f(0.0), rt.f(0.5), rt.f(0.0), rt.f(1.0))
                color = rt.component_wise("mix", color1, middle, amt, width=4)
            else:
                if rt.binary(">", amt, rt.f(0.5)):
                    amt = map__float_float_float_float_float(amt, rt.f(0.5), rt.f(1.0), rt.f(0.0), rt.f(1.0))
                    color = rt.component_wise("mix", middle, color2, amt, width=4)
        return rt.swizzle(color, "rgb")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        color = rt.construct(4, rt.f(0.0))
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        inputColor = rt.texture(_u_inputTex, localUV)
        brightness = rt.binary("+", desaturate__vec3(rt.swizzle(inputColor, "rgb")), rt.binary("/", _u_direction, rt.f(360.0), 1, "float"), 1, "float")
        displacement = rt.binary("*", _u_amount, rt.f(0.01), 1, "float")
        maxDisplacement = rt.f(0.0)
        if (bool(rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_resolution, "x"))) or bool(rt.binary(">", rt.swizzle(_u_fullResolution, "y"), rt.swizzle(_u_resolution, "y")))):
            maxDisplacement = rt.binary("/", rt.f(256.0), rt.component_wise("max", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), width=1), 1, "float")
            displacement = rt.component_wise("min", displacement, maxDisplacement, width=1)
        if rt.binary("==", _u_mode, rt.i(0)):
            uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", brightness, rt.f(6.28318530718), 1, "float"), width=1), displacement, 1, "float"), 1, "float"))
            uv = rt.assign_swizzle(uv, "y", rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", brightness, rt.f(6.28318530718), 1, "float"), width=1), displacement, 1, "float"), 1, "float"))
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                uv = rt.assign_swizzle(uv, "y", rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", desaturate__vec3(derivX__vec3_vec2_bool(rt.swizzle(inputColor, "rgb"), uv, False)), displacement, 1, "float"), 1, "float"))
                uv = rt.assign_swizzle(uv, "x", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", desaturate__vec3(derivY__vec3_vec2_bool(rt.swizzle(inputColor, "rgb"), uv, False)), displacement, 1, "float"), 1, "float"))
        if rt.binary("==", _u_wrap, rt.i(0)):
            uv = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", uv, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                uv = rt.component_wise("mod", uv, rt.f(1.0), width=2)
            else:
                if rt.binary("==", _u_wrap, rt.i(2)):
                    uv = rt.component_wise("clamp", uv, rt.f(0.0), rt.f(1.0), width=2)
        warpedLocalUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        color = rt.texture(_u_inputTex, warpedLocalUV)
        color = rt.assign_swizzle(color, "rgb", blend__vec4_vec4(inputColor, color))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
