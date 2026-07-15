def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_heightMap = T["heightMap"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_diffuseColor = U["diffuseColor"]
    _u_specularColor = U["specularColor"]
    _u_specularIntensity = U["specularIntensity"]
    _u_shininess = U["shininess"]
    _u_ambientColor = U["ambientColor"]
    _u_lightDirection = U["lightDirection"]
    _u_normalStrength = U["normalStrength"]
    _u_smoothing = U["smoothing"]
    _u_renderScale = U["renderScale"]
    _u_reflection = U["reflection"]
    _u_refraction = U["refraction"]
    _u_aberration = U["aberration"]
    def getLuminosity__vec3(color):
        color = rt.copy(color)
        return rt.dot(color, rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114)))
    def getHeight__vec2(uv):
        uv = rt.copy(uv)
        mapSize = rt.construct(2, rt.texture_size(_u_heightMap))
        localUV = rt.binary("/", rt.binary("-", rt.binary("*", uv, _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), mapSize, 2, "float")
        return getLuminosity__vec3(rt.swizzle(rt.texture(_u_heightMap, localUV), "rgb"))
    def calculateNormal__vec2_vec2(uv, texelSize):
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        sampleSize = rt.binary("*", rt.binary("*", texelSize, _u_smoothing, 2, "float"), _u_renderScale, 2, "float")
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
            height = getHeight__vec2(rt.binary("+", uv, offsets[int(i)], 2, "float"))
            dx = rt.binary("+", dx, rt.binary("*", height, sobel_x[int(i)], 1, "float"), 1, "float")
            dy = rt.binary("+", dy, rt.binary("*", height, sobel_y[int(i)], 1, "float"), 1, "float")
        dx = rt.binary("*", dx, _u_normalStrength, 1, "float")
        dy = rt.binary("*", dy, _u_normalStrength, 1, "float")
        normal = rt.normalize(rt.construct(3, rt.unary("-", dx), rt.unary("-", dy), rt.f(1.0)))
        return normal
    def applyRefraction__vec2_vec3(uv, normal):
        uv = rt.copy(uv)
        normal = rt.copy(normal)
        refractionOffset = rt.binary("*", rt.swizzle(normal, "xy"), rt.binary("*", _u_refraction, rt.f(0.0125), 1, "float"), 2, "float")
        return rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, refractionOffset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
    def applyReflection__vec2_vec2_vec3(uv, globalUV, normal):
        uv = rt.copy(uv)
        globalUV = rt.copy(globalUV)
        normal = rt.copy(normal)
        incident = rt.construct(3, rt.normalize(rt.binary("-", globalUV, rt.f(0.5), 2, "float")), rt.f(100.0))
        reflectionVec = rt.reflect(incident, normal)
        reflectionOffset = rt.binary("*", rt.swizzle(reflectionVec, "xy"), rt.binary("*", _u_reflection, rt.f(5e-05), 1, "float"), 2, "float")
        redOffset = rt.binary("*", reflectionOffset, rt.binary("+", rt.f(1.0), rt.binary("*", _u_aberration, rt.f(0.0075), 1, "float"), 1, "float"), 2, "float")
        greenOffset = reflectionOffset
        blueOffset = rt.binary("*", reflectionOffset, rt.binary("-", rt.f(1.0), rt.binary("*", _u_aberration, rt.f(0.0075), 1, "float"), 1, "float"), 2, "float")
        redChannel = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, redOffset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "r")
        greenChannel = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, greenOffset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "g")
        blueChannel = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, blueOffset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "b")
        alphaChannel = rt.swizzle(rt.texture(_u_inputTex, rt.binary("/", rt.binary("-", rt.binary("*", rt.binary("+", uv, reflectionOffset, 2, "float"), _u_fullResolution, 2, "float"), _u_tileOffset, 2, "float"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float")), "a")
        return rt.construct(4, redChannel, greenChannel, blueChannel, alphaChannel)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        resolution = rt.construct(2, texSize)
        fullRes = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else resolution)
        uv = rt.binary("/", globalCoord, _u_fullResolution, 2, "float")
        globalUV = rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float"), fullRes, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), resolution, 2, "float")
        origColor = rt.texture(_u_inputTex, rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, rt.texture_size(_u_inputTex)), 2, "float"))
        normal = calculateNormal__vec2_vec2(uv, texelSize)
        lightDir = rt.normalize(_u_lightDirection)
        viewDir = rt.construct(3, rt.f(0.0), rt.f(0.0), rt.f(1.0))
        ambient = rt.binary("*", _u_ambientColor, rt.swizzle(origColor, "rgb"), 3, "float")
        diffuseFactor = rt.component_wise("max", rt.dot(normal, lightDir), rt.f(0.0), width=1)
        diffuse = rt.binary("*", rt.binary("*", _u_diffuseColor, diffuseFactor, 3, "float"), rt.swizzle(origColor, "rgb"), 3, "float")
        halfDir = rt.normalize(rt.binary("+", lightDir, viewDir, 3, "float"))
        specAngle = rt.component_wise("max", rt.dot(halfDir, normal), rt.f(0.0), width=1)
        specularFactor = rt.component_wise("pow", specAngle, _u_shininess, width=1)
        specular = rt.binary("*", rt.binary("*", _u_specularColor, specularFactor, 3, "float"), _u_specularIntensity, 3, "float")
        litColor = rt.binary("+", rt.binary("+", ambient, diffuse, 3, "float"), specular, 3, "float")
        workingColor = rt.construct(4, litColor, rt.swizzle(origColor, "a"))
        if rt.binary(">", _u_refraction, rt.f(0.0)):
            refractedColor = applyRefraction__vec2_vec3(uv, normal)
            workingColor = rt.component_wise("mix", workingColor, refractedColor, rt.binary("/", _u_refraction, rt.f(100.0), 1, "float"), width=4)
        if (bool(rt.binary(">", _u_reflection, rt.f(0.0))) or bool(rt.binary(">", _u_aberration, rt.f(0.0)))):
            reflectedColor = applyReflection__vec2_vec2_vec3(uv, globalUV, normal)
            workingColor = rt.component_wise("mix", workingColor, reflectedColor, rt.binary("/", _u_reflection, rt.f(100.0), 1, "float"), width=4)
        g.fragColor = workingColor
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
