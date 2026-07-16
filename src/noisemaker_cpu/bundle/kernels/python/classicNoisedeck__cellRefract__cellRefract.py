def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_SHAPE = U.get("SHAPE", 0)
    _u_KERNEL = U.get("KERNEL", 0)
    _u_inputTex = T["inputTex"]
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_scale = U.get("scale", rt.f(0.0))
    _u_cellScale = U.get("cellScale", rt.f(0.0))
    _u_cellSmooth = U.get("cellSmooth", rt.f(0.0))
    _u_variation = U.get("variation", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_refractAmt = U.get("refractAmt", rt.f(0.0))
    _u_direction = U.get("direction", rt.f(0.0))
    _u_wrap = U.get("wrap", 0)
    _u_effectWidth = U.get("effectWidth", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.emboss = rt.new_array(rt.i(9), 1)
    g.sharpen = rt.new_array(rt.i(9), 1)
    g.blur = rt.new_array(rt.i(9), 1)
    g.edge = rt.new_array(rt.i(9), 1)
    g.edge2 = rt.new_array(rt.i(9), 1)
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
    def convolve__vec2_float_bool(localUV, kernel, divide):
        localUV = rt.copy(localUV, "float")
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        offset = rt.new_array(rt.i(9), 2)
        offset[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.unary("-", rt.swizzle(texelSize, "y")))
        offset[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(texelSize, "y")))
        offset[int(rt.i(2))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.unary("-", rt.swizzle(texelSize, "y")))
        offset[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.f(0.0))
        offset[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offset[int(rt.i(5))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.f(0.0))
        offset[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(texelSize, "x")), rt.swizzle(texelSize, "y"))
        offset[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(texelSize, "y"))
        offset[int(rt.i(8))] = rt.construct(2, rt.swizzle(texelSize, "x"), rt.swizzle(texelSize, "y"))
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
            color = rt.swizzle(rt.texture(_u_inputTex, rt.binary("+", localUV, rt.binary("*", offset[int(i)], _u_effectWidth, 2, "float"), 2, "float")), "rgb")
            conv = rt.binary("+", conv, rt.binary("*", color, kernel[int(i)], 3, "float"), 3, "float")
            kernelWeight = rt.binary("+", kernelWeight, kernel[int(i)], 1, "float")
        if divide:
            conv = rt.assign_swizzle(conv, "rgb", rt.binary("/", rt.swizzle(conv, "rgb"), kernelWeight, 3, "float"))
        return rt.component_wise("clamp", rt.swizzle(conv, "rgb"), rt.f(0.0), rt.f(1.0), width=3)
    def map__float_float_float_float_float(value, inMin, inMax, outMin, outMax):
        return rt.binary("+", outMin, rt.binary("/", rt.binary("*", rt.binary("-", outMax, outMin, 1, "float"), rt.binary("-", value, inMin, 1, "float"), 1, "float"), rt.binary("-", inMax, inMin, 1, "float"), 1, "float"), 1, "float")
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v = rt.binary("+", rt.binary("*", v, rt.construct(1, rt.i(1664525), base="uint"), 3, "uint"), rt.construct(1, rt.i(1013904223), base="uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.construct(1, rt.i(16), base="uint"), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.construct(1, rt.i(4294967295), base="uint")), 3, "float")
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
        avg = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.2126), rt.swizzle(color, "r"), 1, "float"), rt.binary("*", rt.f(0.7152), rt.swizzle(color, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0722), rt.swizzle(color, "b"), 1, "float"), 1, "float")
        return rt.construct(3, avg)
    def derivatives__vec3_vec2_bool(color, localUV, divide):
        color = rt.copy(color, "float")
        localUV = rt.copy(localUV, "float")
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
        s1 = convolve__vec2_float_bool(localUV, deriv_x, divide)
        s2 = convolve__vec2_float_bool(localUV, deriv_y, divide)
        dist = rt.distance(s1, s2)
        color = rt.binary("*", color, dist, 3, "float")
        return color
    def sobel__vec3_vec2(color, localUV):
        color = rt.copy(color, "float")
        localUV = rt.copy(localUV, "float")
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
        s1 = convolve__vec2_float_bool(localUV, sobel_x, False)
        s2 = convolve__vec2_float_bool(localUV, sobel_y, False)
        dist = rt.distance(s1, s2)
        color = rt.binary("*", color, dist, 3, "float")
        return color
    def shadow__vec3_vec2(color, localUV):
        color = rt.copy(color, "float")
        localUV = rt.copy(localUV, "float")
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
        color = rgb2hsv__vec3(color)
        x = convolve__vec2_float_bool(localUV, sobel_x, False)
        y = convolve__vec2_float_bool(localUV, sobel_y, False)
        shade = rt.distance(x, y)
        highlight = rt.binary("*", shade, shade, 1, "float")
        shade = rt.binary("*", rt.binary("-", rt.f(1.0), rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(color, "z"), 1, "float"), rt.binary("-", rt.f(1.0), highlight, 1, "float"), 1, "float"), 1, "float"), shade, 1, "float")
        alpha = rt.f(0.75)
        color = rt.construct(3, rt.swizzle(color, "x"), rt.swizzle(color, "y"), rt.component_wise("mix", rt.swizzle(color, "z"), shade, alpha, width=1))
        return hsv2rgb__vec3(color)
    def outline__vec3_vec2(color, localUV):
        color = rt.copy(color, "float")
        localUV = rt.copy(localUV, "float")
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
        s1 = convolve__vec2_float_bool(localUV, sobel_x, False)
        s2 = convolve__vec2_float_bool(localUV, sobel_y, False)
        dist = rt.distance(s1, s2)
        outcolor = rt.binary("-", color, dist, 3, "float")
        return rt.component_wise("max", outcolor, rt.f(0.0), width=3)
    def convolutionKernel__vec3_vec2(color, localUV):
        color = rt.copy(color, "float")
        localUV = rt.copy(localUV, "float")
        if rt.binary("==", _u_KERNEL, rt.i(1)):
            return convolve__vec2_float_bool(localUV, g.blur, True)
        else:
            if rt.binary("==", _u_KERNEL, rt.i(2)):
                return derivatives__vec3_vec2_bool(color, localUV, True)
            else:
                if rt.binary("==", _u_KERNEL, rt.i(120)):
                    return rt.component_wise("clamp", rt.binary("*", derivatives__vec3_vec2_bool(color, localUV, False), rt.f(2.5), 3, "float"), rt.f(0.0), rt.f(1.0), width=3)
                else:
                    if rt.binary("==", _u_KERNEL, rt.i(3)):
                        return rt.binary("*", color, convolve__vec2_float_bool(localUV, g.edge2, True), 3, "float")
                    else:
                        if rt.binary("==", _u_KERNEL, rt.i(4)):
                            return convolve__vec2_float_bool(localUV, g.emboss, False)
                        else:
                            if rt.binary("==", _u_KERNEL, rt.i(5)):
                                return outline__vec3_vec2(color, localUV)
                            else:
                                if rt.binary("==", _u_KERNEL, rt.i(6)):
                                    return shadow__vec3_vec2(color, localUV)
                                else:
                                    if rt.binary("==", _u_KERNEL, rt.i(7)):
                                        return convolve__vec2_float_bool(localUV, g.sharpen, False)
                                    else:
                                        if rt.binary("==", _u_KERNEL, rt.i(8)):
                                            return sobel__vec3_vec2(color, localUV)
                                        else:
                                            if rt.binary("==", _u_KERNEL, rt.i(9)):
                                                return rt.component_wise("max", color, convolve__vec2_float_bool(localUV, g.edge2, True), width=3)
                                            else:
                                                return color
    def periodicFunction__float(p):
        return map__float_float_float_float_float(rt.component_wise("sin", rt.binary("*", p, rt.f(6.28318530718), 1, "float"), width=1), rt.unary("-", rt.f(1.0)), rt.f(1.0), rt.f(0.0), rt.f(1.0))
    def polarShape__vec2_int(st, sides):
        st = rt.copy(st, "float")
        a = rt.binary("+", rt.component_wise("atan", rt.swizzle(st, "x"), rt.swizzle(st, "y"), width=1), rt.f(3.14159265359), 1, "float")
        r = rt.binary("/", rt.f(6.28318530718), rt.construct(1, sides), 1, "float")
        return rt.binary("*", rt.component_wise("cos", rt.binary("-", rt.binary("*", rt.component_wise("floor", rt.binary("+", rt.f(0.5), rt.binary("/", a, r, 1, "float"), 1, "float"), width=1), r, 1, "float"), a, 1, "float"), width=1), rt.length(st), 1, "float")
    def shapeDistance__vec2_vec2_float(st, offset, scale):
        st = rt.copy(st, "float")
        offset = rt.copy(offset, "float")
        st = rt.binary("+", st, offset, 2, "float")
        d = rt.f(1.0)
        if rt.binary("==", _u_SHAPE, rt.i(0)):
            d = rt.length(rt.binary("*", st, rt.f(1.2), 2, "float"))
        else:
            if rt.binary("==", _u_SHAPE, rt.i(2)):
                d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(6))
            else:
                if rt.binary("==", _u_SHAPE, rt.i(3)):
                    d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.2), 2, "float"), rt.i(8))
                else:
                    if rt.binary("==", _u_SHAPE, rt.i(4)):
                        d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(4))
                    else:
                        if rt.binary("==", _u_SHAPE, rt.i(6)):
                            st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.f(0.05), 1, "float"))
                            d = polarShape__vec2_int(rt.binary("*", st, rt.f(1.5), 2, "float"), rt.i(3))
        return rt.binary("*", d, scale, 1, "float")
    def wrapEdges__vec2_float(st, freq):
        st = rt.copy(st, "float")
        if rt.binary("<", rt.swizzle(st, "x"), rt.f(0.0)):
            st = rt.assign_swizzle(st, "x", rt.binary("-", freq, rt.f(1.0), 1, "float"))
        if rt.binary(">", rt.swizzle(st, "x"), rt.binary("/", rt.binary("*", freq, rt.swizzle(_u_fullResolution, "x"), 1, "float"), rt.swizzle(_u_fullResolution, "y"), 1, "float")):
            st = rt.assign_swizzle(st, "x", rt.f(0.0))
        if rt.binary("<", rt.swizzle(st, "y"), rt.f(0.0)):
            st = rt.assign_swizzle(st, "y", rt.binary("-", freq, rt.f(1.0), 1, "float"))
        if rt.binary(">", rt.swizzle(st, "y"), freq):
            st = rt.assign_swizzle(st, "y", rt.f(0.0))
        return st
    def smin__float_float_float(a, b, k):
        if rt.binary("==", k, rt.f(0.0)):
            return rt.component_wise("min", a, b, width=1)
        h = rt.binary("/", rt.component_wise("max", rt.binary("-", k, rt.component_wise("abs", rt.binary("-", a, b, 1, "float"), width=1), 1, "float"), rt.f(0.0), width=1), k, 1, "float")
        return rt.binary("-", rt.component_wise("min", a, b, width=1), rt.binary("*", rt.binary("*", rt.binary("*", h, h, 1, "float"), k, 1, "float"), rt.binary("/", rt.f(1.0), rt.f(4.0), 1, "float"), 1, "float"), 1, "float")
    def cells__vec2_float_float(st, freq, cellSize):
        st = rt.copy(st, "float")
        st = rt.binary("*", st, freq, 2, "float")
        st = rt.binary("+", st, rt.swizzle(prng__vec3(rt.construct(3, rt.construct(1, _u_seed))), "xy"), 2, "float")
        i = rt.component_wise("floor", st, width=2)
        f = rt.component_wise("fract", st, width=2)
        d = rt.f(1.0)
        y = rt.unary("-", rt.i(2))
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<=", y, rt.i(2))):
                break
            x = rt.unary("-", rt.i(2))
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<=", x, rt.i(2))):
                    break
                n = rt.construct(2, rt.construct(1, x), rt.construct(1, y))
                wrap = rt.binary("+", i, n, 2, "float")
                point = rt.swizzle(prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), "xy")
                r1 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, rt.construct(1, _u_seed), wrap)), rt.f(0.5), 3, "float"), rt.f(0.25), 3, "float")
                r2 = rt.binary("-", rt.binary("*", prng__vec3(rt.construct(3, wrap, rt.construct(1, _u_seed))), rt.f(2.0), 3, "float"), rt.f(1.0), 3, "float")
                spd = rt.component_wise("floor", _u_speed, width=1)
                point = rt.binary("+", point, rt.construct(2, rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "x"), 1, "float"), width=1), rt.swizzle(r1, "x"), 1, "float"), rt.binary("*", rt.component_wise("cos", rt.binary("+", rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float"), rt.swizzle(r2, "y"), 1, "float"), width=1), rt.swizzle(r1, "y"), 1, "float")), 2, "float")
                diff = rt.binary("-", rt.binary("+", n, point, 2, "float"), f, 2, "float")
                dist = rt.f(0.0)
                if rt.binary("==", _u_SHAPE, rt.i(1)):
                    dist = rt.binary("*", rt.binary("+", rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "x"), rt.swizzle(point, "x"), 1, "float"), rt.swizzle(f, "x"), 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", rt.binary("+", rt.swizzle(n, "y"), rt.swizzle(point, "y"), 1, "float"), rt.swizzle(f, "y"), 1, "float"), width=1), 1, "float"), cellSize, 1, "float")
                else:
                    dist = shapeDistance__vec2_vec2_float(rt.construct(2, rt.swizzle(diff, "x"), rt.unary("-", rt.swizzle(diff, "y"))), rt.construct(2, rt.f(0.0)), cellSize)
                dist = rt.binary("+", dist, rt.binary("*", rt.swizzle(r1, "z"), rt.binary("*", _u_variation, rt.f(0.01), 1, "float"), 1, "float"), 1, "float")
                d = smin__float_float_float(d, dist, rt.binary("*", _u_cellSmooth, rt.f(0.01), 1, "float"))
        return d
    def posterize__vec3_float(color, lev):
        color = rt.copy(color, "float")
        if rt.binary("==", lev, rt.f(0.0)):
            return color
        else:
            if rt.binary("==", lev, rt.f(1.0)):
                lev = rt.f(2.0)
        color = rt.component_wise("clamp", color, rt.f(0.0), rt.f(0.99), width=3)
        color = rt.binary("*", color, lev, 3, "float")
        color = rt.binary("+", rt.component_wise("floor", color, width=3), rt.f(0.5), 3, "float")
        color = rt.binary("/", color, lev, 3, "float")
        return color
    def pixellate__vec2_float(localUV, size):
        localUV = rt.copy(localUV, "float")
        if rt.binary("<=", size, rt.f(1.0)):
            return rt.swizzle(rt.texture(_u_inputTex, localUV), "rgb")
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        dx = rt.binary("*", size, rt.swizzle(texelSize, "x"), 1, "float")
        dy = rt.binary("*", size, rt.swizzle(texelSize, "y"), 1, "float")
        coord = rt.construct(2, rt.binary("*", dx, rt.component_wise("floor", rt.binary("/", rt.swizzle(localUV, "x"), dx, 1, "float"), width=1), 1, "float"), rt.binary("*", dy, rt.component_wise("floor", rt.binary("/", rt.swizzle(localUV, "y"), dy, 1, "float"), width=1), 1, "float"))
        return rt.swizzle(rt.texture(_u_inputTex, coord), "rgb")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        color = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(1.0), rt.f(1.0))
        st = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        loadKernels__void()
        blend = rt.f(1.0)
        freq = map__float_float_float_float_float(_u_scale, rt.f(1.0), rt.f(100.0), rt.f(20.0), rt.f(1.0))
        cellSize = map__float_float_float_float_float(_u_cellScale, rt.f(1.0), rt.f(100.0), rt.f(3.0), rt.f(0.75))
        d = cells__vec2_float_float(rt.binary("*", st, rt.construct(2, rt.binary("/", rt.swizzle(_u_fullResolution, "x"), rt.swizzle(_u_fullResolution, "y"), 1, "float"), rt.f(1.0)), 2, "float"), freq, cellSize)
        ref = map__float_float_float_float_float(_u_refractAmt, rt.f(0.0), rt.f(100.0), rt.f(0.0), rt.f(0.125))
        refLen = rt.binary("+", d, rt.binary("/", _u_direction, rt.f(360.0), 1, "float"), 1, "float")
        st = rt.assign_swizzle(st, "x", rt.binary("+", rt.swizzle(st, "x"), rt.binary("*", rt.component_wise("cos", rt.binary("*", refLen, rt.f(6.28318530718), 1, "float"), width=1), ref, 1, "float"), 1, "float"))
        st = rt.assign_swizzle(st, "y", rt.binary("+", rt.swizzle(st, "y"), rt.binary("*", rt.component_wise("sin", rt.binary("*", refLen, rt.f(6.28318530718), 1, "float"), width=1), ref, 1, "float"), 1, "float"))
        if rt.binary("==", _u_wrap, rt.i(0)):
            st = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", rt.binary("+", st, rt.f(1.0), 2, "float"), rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                st = rt.component_wise("fract", st, width=2)
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", st, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")
        color = rt.texture(_u_inputTex, localUV)
        if rt.binary("!=", _u_KERNEL, rt.i(0)):
            if rt.binary("!=", _u_effectWidth, rt.f(0.0)):
                if rt.binary("==", _u_KERNEL, rt.i(100)):
                    color = rt.assign_swizzle(color, "rgb", pixellate__vec2_float(localUV, rt.binary("*", _u_effectWidth, rt.f(4.0), 1, "float")))
                else:
                    if rt.binary("==", _u_KERNEL, rt.i(110)):
                        color = rt.assign_swizzle(color, "rgb", posterize__vec3_float(rt.swizzle(color, "rgb"), rt.component_wise("floor", map__float_float_float_float_float(_u_effectWidth, rt.f(0.0), rt.f(10.0), rt.f(0.0), rt.f(20.0)), width=1)))
                    else:
                        color = rt.assign_swizzle(color, "rgb", convolutionKernel__vec3_vec2(rt.swizzle(color, "rgb"), localUV))
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
