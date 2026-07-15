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
    _u_mode = U["mode"]
    _u_mapSource = U["mapSource"]
    _u_intensity = U["intensity"]
    _u_wrap = U["wrap"]
    _u_smoothing = U["smoothing"]
    _u_aberration = U["aberration"]
    _u_antialias = U["antialias"]
    def getLuminosity__vec3(color):
        color = rt.copy(color)
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def calculateNormal__vec2_vec2_sampler2D(uv, texelSize, mapTex):
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        sampleSize = rt.binary("*", texelSize, _u_smoothing, 2, "float")
        sobel_x = rt.new_array(rt.i(9), 1)
        sobel_x[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(1))] = rt.f(0.0)
        sobel_x[int(rt.i(2))] = rt.f(1.0)
        sobel_x[int(rt.i(3))] = rt.unary("-", rt.f(2.0))
        sobel_x[int(rt.i(4))] = rt.f(0.0)
        sobel_x[int(rt.i(5))] = rt.f(2.0)
        sobel_x[int(rt.i(6))] = rt.unary("-", rt.f(1.0))
        sobel_x[int(rt.i(7))] = rt.f(0.0)
        sobel_x[int(rt.i(8))] = rt.f(1.0)
        sobel_y = rt.new_array(rt.i(9), 1)
        sobel_y[int(rt.i(0))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(1))] = rt.unary("-", rt.f(2.0))
        sobel_y[int(rt.i(2))] = rt.unary("-", rt.f(1.0))
        sobel_y[int(rt.i(3))] = rt.f(0.0)
        sobel_y[int(rt.i(4))] = rt.f(0.0)
        sobel_y[int(rt.i(5))] = rt.f(0.0)
        sobel_y[int(rt.i(6))] = rt.f(1.0)
        sobel_y[int(rt.i(7))] = rt.f(2.0)
        sobel_y[int(rt.i(8))] = rt.f(1.0)
        offsets = rt.new_array(rt.i(9), 2)
        offsets[int(rt.i(0))] = rt.construct(2, rt.unary("-", rt.swizzle(sampleSize, "x")), rt.unary("-", rt.swizzle(sampleSize, "y")))
        offsets[int(rt.i(1))] = rt.construct(2, rt.f(0.0), rt.unary("-", rt.swizzle(sampleSize, "y")))
        offsets[int(rt.i(2))] = rt.construct(2, rt.swizzle(sampleSize, "x"), rt.unary("-", rt.swizzle(sampleSize, "y")))
        offsets[int(rt.i(3))] = rt.construct(2, rt.unary("-", rt.swizzle(sampleSize, "x")), rt.f(0.0))
        offsets[int(rt.i(4))] = rt.construct(2, rt.f(0.0), rt.f(0.0))
        offsets[int(rt.i(5))] = rt.construct(2, rt.swizzle(sampleSize, "x"), rt.f(0.0))
        offsets[int(rt.i(6))] = rt.construct(2, rt.unary("-", rt.swizzle(sampleSize, "x")), rt.swizzle(sampleSize, "y"))
        offsets[int(rt.i(7))] = rt.construct(2, rt.f(0.0), rt.swizzle(sampleSize, "y"))
        offsets[int(rt.i(8))] = rt.construct(2, rt.swizzle(sampleSize, "x"), rt.swizzle(sampleSize, "y"))
        dx = rt.f(0.0)
        dy = rt.f(0.0)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(9))):
                break
            texSample = rt.swizzle(rt.texture(mapTex, rt.binary("+", uv, offsets[int(i)], 2, "float")), "rgb")
            height = getLuminosity__vec3(texSample)
            dx = rt.binary("+", dx, rt.binary("*", height, sobel_x[int(i)], 1, "float"), 1, "float")
            dy = rt.binary("+", dy, rt.binary("*", height, sobel_y[int(i)], 1, "float"), 1, "float")
        normalStrength = rt.binary("*", _u_intensity, rt.f(0.1), 1, "float")
        dx = rt.binary("*", dx, normalStrength, 1, "float")
        dy = rt.binary("*", dy, normalStrength, 1, "float")
        normal = rt.normalize(rt.construct(3, rt.unary("-", dx), rt.unary("-", dy), rt.f(1.0)))
        return normal
    def wrapCoords__vec2(st):
        st = rt.copy(st)
        if rt.binary("==", _u_wrap, rt.i(0)):
            st = rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", st, rt.f(2.0), width=2), rt.f(1.0), 2, "float"), width=2)
            st = rt.binary("-", rt.f(1.0), st, 2, "float")
        else:
            if rt.binary("==", _u_wrap, rt.i(1)):
                st = rt.component_wise("fract", st, width=2)
            else:
                if rt.binary("==", _u_wrap, rt.i(2)):
                    st = rt.component_wise("clamp", st, rt.f(0.0), rt.f(1.0), width=2)
        return st
    def applyDisplacement__vec2_sampler2D_sampler2D(uv, mapTex, targetTex):
        uv = rt.copy(uv)
        mapColor = rt.texture(mapTex, uv)
        len = rt.length(rt.swizzle(mapColor, "rgb"))
        offset = rt.construct(2, 0.0)
        offset = rt.assign_swizzle(offset, "x", rt.binary("*", rt.component_wise("cos", rt.binary("*", len, rt.f(6.28318530718), 1, "float"), width=1), rt.binary("*", _u_intensity, rt.f(0.001), 1, "float"), 1, "float"))
        offset = rt.assign_swizzle(offset, "y", rt.binary("*", rt.component_wise("sin", rt.binary("*", len, rt.f(6.28318530718), 1, "float"), width=1), rt.binary("*", _u_intensity, rt.f(0.001), 1, "float"), 1, "float"))
        displacedUV = wrapCoords__vec2(rt.binary("+", uv, offset, 2, "float"))
        if _u_antialias:
            dx = rt.component_wise("dFdx", displacedUV, width=2)
            dy = rt.component_wise("dFdy", displacedUV, width=2)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", displacedUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", displacedUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", displacedUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", displacedUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            return rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            return rt.texture(targetTex, displacedUV)
    def applyRefraction__vec2_vec2_sampler2D_sampler2D(uv, texelSize, mapTex, targetTex):
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        normal = calculateNormal__vec2_vec2_sampler2D(uv, texelSize, mapTex)
        refractionOffset = rt.binary("*", rt.swizzle(normal, "xy"), rt.binary("*", _u_intensity, rt.f(0.0125), 1, "float"), 2, "float")
        refractedUV = wrapCoords__vec2(rt.binary("+", uv, refractionOffset, 2, "float"))
        if _u_antialias:
            dx = rt.component_wise("dFdx", refractedUV, width=2)
            dy = rt.component_wise("dFdy", refractedUV, width=2)
            col = rt.construct(4, rt.f(0.0))
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", refractedUV, rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", refractedUV, rt.binary("*", dx, rt.f(0.125), 2, "float"), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", refractedUV, rt.binary("*", dx, rt.f(0.375), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")), 4, "float")
            col = rt.binary("+", col, rt.texture(targetTex, rt.binary("+", rt.binary("+", refractedUV, rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")), 4, "float")
            return rt.binary("*", col, rt.f(0.25), 4, "float")
        else:
            return rt.texture(targetTex, refractedUV)
    def applyReflection__vec2_vec2_vec2_sampler2D_sampler2D(uv, globalUV, texelSize, mapTex, targetTex):
        uv = rt.copy(uv)
        globalUV = rt.copy(globalUV)
        texelSize = rt.copy(texelSize)
        normal = calculateNormal__vec2_vec2_sampler2D(uv, texelSize, mapTex)
        incident = rt.construct(3, rt.normalize(rt.binary("-", globalUV, rt.f(0.5), 2, "float")), rt.f(100.0))
        reflectionVec = rt.reflect(incident, normal)
        reflectionOffset = rt.binary("*", rt.swizzle(reflectionVec, "xy"), rt.binary("*", _u_intensity, rt.f(5e-05), 1, "float"), 2, "float")
        redOffset = rt.binary("*", reflectionOffset, rt.binary("+", rt.f(1.0), rt.binary("*", _u_aberration, rt.f(0.0075), 1, "float"), 1, "float"), 2, "float")
        greenOffset = reflectionOffset
        blueOffset = rt.binary("*", reflectionOffset, rt.binary("-", rt.f(1.0), rt.binary("*", _u_aberration, rt.f(0.0075), 1, "float"), 1, "float"), 2, "float")
        redUV = wrapCoords__vec2(rt.binary("+", uv, redOffset, 2, "float"))
        greenUV = wrapCoords__vec2(rt.binary("+", uv, greenOffset, 2, "float"))
        blueUV = wrapCoords__vec2(rt.binary("+", uv, blueOffset, 2, "float"))
        alphaUV = wrapCoords__vec2(rt.binary("+", uv, reflectionOffset, 2, "float"))
        if _u_antialias:
            dx = rt.component_wise("dFdx", greenUV, width=2)
            dy = rt.component_wise("dFdy", greenUV, width=2)
            r = rt.f(0.0)
            g = rt.f(0.0)
            b = rt.f(0.0)
            a = rt.f(0.0)
            o1 = rt.binary("+", rt.binary("*", dx, rt.unary("-", rt.f(0.375)), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.125)), 2, "float"), 2, "float")
            o2 = rt.binary("+", rt.binary("*", dx, rt.f(0.125), 2, "float"), rt.binary("*", dy, rt.unary("-", rt.f(0.375)), 2, "float"), 2, "float")
            o3 = rt.binary("+", rt.binary("*", dx, rt.f(0.375), 2, "float"), rt.binary("*", dy, rt.f(0.125), 2, "float"), 2, "float")
            o4 = rt.binary("+", rt.binary("*", dx, rt.unary("-", rt.f(0.125)), 2, "float"), rt.binary("*", dy, rt.f(0.375), 2, "float"), 2, "float")
            r = rt.binary("+", r, rt.swizzle(rt.texture(targetTex, rt.binary("+", redUV, o1, 2, "float")), "r"), 1, "float")
            r = rt.binary("+", r, rt.swizzle(rt.texture(targetTex, rt.binary("+", redUV, o2, 2, "float")), "r"), 1, "float")
            r = rt.binary("+", r, rt.swizzle(rt.texture(targetTex, rt.binary("+", redUV, o3, 2, "float")), "r"), 1, "float")
            r = rt.binary("+", r, rt.swizzle(rt.texture(targetTex, rt.binary("+", redUV, o4, 2, "float")), "r"), 1, "float")
            g = rt.binary("+", g, rt.swizzle(rt.texture(targetTex, rt.binary("+", greenUV, o1, 2, "float")), "g"), 1, "float")
            g = rt.binary("+", g, rt.swizzle(rt.texture(targetTex, rt.binary("+", greenUV, o2, 2, "float")), "g"), 1, "float")
            g = rt.binary("+", g, rt.swizzle(rt.texture(targetTex, rt.binary("+", greenUV, o3, 2, "float")), "g"), 1, "float")
            g = rt.binary("+", g, rt.swizzle(rt.texture(targetTex, rt.binary("+", greenUV, o4, 2, "float")), "g"), 1, "float")
            b = rt.binary("+", b, rt.swizzle(rt.texture(targetTex, rt.binary("+", blueUV, o1, 2, "float")), "b"), 1, "float")
            b = rt.binary("+", b, rt.swizzle(rt.texture(targetTex, rt.binary("+", blueUV, o2, 2, "float")), "b"), 1, "float")
            b = rt.binary("+", b, rt.swizzle(rt.texture(targetTex, rt.binary("+", blueUV, o3, 2, "float")), "b"), 1, "float")
            b = rt.binary("+", b, rt.swizzle(rt.texture(targetTex, rt.binary("+", blueUV, o4, 2, "float")), "b"), 1, "float")
            a = rt.binary("+", a, rt.swizzle(rt.texture(targetTex, rt.binary("+", alphaUV, o1, 2, "float")), "a"), 1, "float")
            a = rt.binary("+", a, rt.swizzle(rt.texture(targetTex, rt.binary("+", alphaUV, o2, 2, "float")), "a"), 1, "float")
            a = rt.binary("+", a, rt.swizzle(rt.texture(targetTex, rt.binary("+", alphaUV, o3, 2, "float")), "a"), 1, "float")
            a = rt.binary("+", a, rt.swizzle(rt.texture(targetTex, rt.binary("+", alphaUV, o4, 2, "float")), "a"), 1, "float")
            return rt.binary("*", rt.construct(4, r, g, b, a), rt.f(0.25), 4, "float")
        else:
            redChannel = rt.swizzle(rt.texture(targetTex, redUV), "r")
            greenChannel = rt.swizzle(rt.texture(targetTex, greenUV), "g")
            blueChannel = rt.swizzle(rt.texture(targetTex, blueUV), "b")
            alphaChannel = rt.swizzle(rt.texture(targetTex, alphaUV), "a")
            return rt.construct(4, redChannel, greenChannel, blueChannel, alphaChannel)
    def main__void():
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), _u_resolution, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), _u_resolution, 2, "float")
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else _u_resolution)
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        color = rt.construct(4, 0.0)
        if rt.binary("==", _u_mode, rt.i(0)):
            if rt.binary("==", _u_mapSource, rt.i(0)):
                color = applyDisplacement__vec2_sampler2D_sampler2D(uv, _u_inputTex, _u_tex)
            else:
                color = applyDisplacement__vec2_sampler2D_sampler2D(uv, _u_tex, _u_inputTex)
        else:
            if rt.binary("==", _u_mode, rt.i(1)):
                if rt.binary("==", _u_mapSource, rt.i(0)):
                    color = applyRefraction__vec2_vec2_sampler2D_sampler2D(uv, texelSize, _u_inputTex, _u_tex)
                else:
                    color = applyRefraction__vec2_vec2_sampler2D_sampler2D(uv, texelSize, _u_tex, _u_inputTex)
            else:
                if rt.binary("==", _u_mode, rt.i(2)):
                    if rt.binary("==", _u_mapSource, rt.i(0)):
                        color = applyReflection__vec2_vec2_vec2_sampler2D_sampler2D(uv, globalUV, texelSize, _u_inputTex, _u_tex)
                    else:
                        color = applyReflection__vec2_vec2_vec2_sampler2D_sampler2D(uv, globalUV, texelSize, _u_tex, _u_inputTex)
        g.fragColor = color
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
