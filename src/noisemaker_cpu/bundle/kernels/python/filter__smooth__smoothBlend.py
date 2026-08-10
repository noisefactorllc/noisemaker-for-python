def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_inputTex = T["inputTex"]
    _u_edgeTex = T["edgeTex"]
    _u_smoothType = U.get("smoothType", 0)
    _u_strength = U.get("strength", rt.f(0.0))
    _u_threshold = U.get("threshold", rt.f(0.0))
    _u_radius = U.get("radius", rt.f(0.0))
    _u_samples = U.get("samples", 0)
    _u_searchSteps = U.get("searchSteps", 0)
    g.fragColor = rt.construct(4, 0.0)
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114))
    def luminance__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        return rt.dot(rgb, g.LUMA_WEIGHTS)
    def sampleBilinear__vec2_ivec2(uv, texSize):
        uv = rt.copy(uv, "float")
        texSize = rt.copy(texSize, "int")
        texCoord = rt.binary("-", rt.binary("*", uv, rt.construct(2, texSize), 2, "float"), rt.f(0.5), 2, "float")
        base = rt.construct(2, rt.component_wise("floor", texCoord, width=2), base="int")
        f = rt.binary("-", texCoord, rt.construct(2, base), 2, "float")
        maxC = rt.binary("-", texSize, rt.i(1), 2, "int")
        tl = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", base, rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
        tr = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
        bl = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
        br = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, rt.construct(2, rt.i(1), rt.i(1), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
        return rt.component_wise("mix", rt.component_wise("mix", tl, tr, rt.swizzle(f, "x"), width=4), rt.component_wise("mix", bl, br, rt.swizzle(f, "x"), width=4), rt.swizzle(f, "y"), width=4)
    def sampleOffset2x__int(i):
        if rt.binary("==", i, rt.i(0)):
            return rt.construct(2, rt.unary("-", rt.f(0.25)), rt.f(0.25))
        return rt.construct(2, rt.f(0.25), rt.unary("-", rt.f(0.25)))
    def sampleOffset4x__int(i):
        if rt.binary("==", i, rt.i(0)):
            return rt.construct(2, rt.unary("-", rt.f(0.125)), rt.unary("-", rt.f(0.375)))
        if rt.binary("==", i, rt.i(1)):
            return rt.construct(2, rt.f(0.375), rt.unary("-", rt.f(0.125)))
        if rt.binary("==", i, rt.i(2)):
            return rt.construct(2, rt.unary("-", rt.f(0.375)), rt.f(0.125))
        return rt.construct(2, rt.f(0.125), rt.f(0.375))
    def sampleOffset8x__int(i):
        if rt.binary("==", i, rt.i(0)):
            return rt.construct(2, rt.unary("-", rt.f(0.375)), rt.unary("-", rt.f(0.375)))
        if rt.binary("==", i, rt.i(1)):
            return rt.construct(2, rt.f(0.125), rt.unary("-", rt.f(0.375)))
        if rt.binary("==", i, rt.i(2)):
            return rt.construct(2, rt.unary("-", rt.f(0.125)), rt.unary("-", rt.f(0.125)))
        if rt.binary("==", i, rt.i(3)):
            return rt.construct(2, rt.f(0.375), rt.unary("-", rt.f(0.125)))
        if rt.binary("==", i, rt.i(4)):
            return rt.construct(2, rt.unary("-", rt.f(0.375)), rt.f(0.125))
        if rt.binary("==", i, rt.i(5)):
            return rt.construct(2, rt.f(0.125), rt.f(0.125))
        if rt.binary("==", i, rt.i(6)):
            return rt.construct(2, rt.unary("-", rt.f(0.125)), rt.f(0.375))
        return rt.construct(2, rt.f(0.375), rt.f(0.375))
    def getSampleOffset__int_int(i, count):
        if rt.binary("<=", count, rt.i(2)):
            return sampleOffset2x__int(i)
        if rt.binary("<=", count, rt.i(4)):
            return sampleOffset4x__int(i)
        return sampleOffset8x__int(i)
    def msaaBlend__vec2_vec2_ivec2(uv, texelSize, texSize):
        uv = rt.copy(uv, "float")
        texelSize = rt.copy(texelSize, "float")
        texSize = rt.copy(texSize, "int")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        maxC = rt.binary("-", texSize, rt.i(1), 2, "int")
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        L = luminance__vec3(rt.swizzle(center, "rgb"))
        Ln = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0)), "rgb"))
        Ls = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0)), "rgb"))
        Lw = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0)), "rgb"))
        Le = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0)), "rgb"))
        maxDiff = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Ln, 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", L, Ls, 1, "float"), width=1), width=1), rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Lw, 1, "float"), width=1), rt.component_wise("abs", rt.binary("-", L, Le, 1, "float"), width=1), width=1), width=1)
        if rt.binary("<", maxDiff, _u_threshold):
            return center
        sum = rt.construct(4, rt.f(0.0))
        count = _u_samples
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(8))):
                break
            if rt.binary(">=", i, count):
                break
            offset = rt.binary("*", getSampleOffset__int_int(i, count), _u_radius, 2, "float")
            sum[:] = rt.binary("+", sum, sampleBilinear__vec2_ivec2(rt.binary("+", uv, rt.binary("*", offset, texelSize, 2, "float"), 2, "float"), texSize), 4, "float")
        return rt.binary("/", sum, rt.construct(1, count), 4, "float")
    def searchEdge__ivec2_ivec2_ivec2_int(coord, dir, maxC, component):
        coord = rt.copy(coord, "int")
        dir = rt.copy(dir, "int")
        maxC = rt.copy(maxC, "int")
        i = rt.i(1)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<=", i, rt.i(32))):
                break
            if rt.binary(">", i, _u_searchSteps):
                break
            sampleCoord = rt.component_wise("clamp", rt.binary("+", coord, rt.binary("*", dir, i, 2, "int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2)
            edge = (rt.swizzle(rt.texel_fetch(_u_edgeTex, sampleCoord, rt.i(0)), "r") if rt.binary("==", component, rt.i(0)) else rt.swizzle(rt.texel_fetch(_u_edgeTex, sampleCoord, rt.i(0)), "g"))
            if rt.binary("<", edge, rt.f(0.5)):
                return rt.construct(1, rt.binary("-", i, rt.i(1), 1, "int"))
        return rt.construct(1, _u_searchSteps)
    def smaaBlend__ivec2(texSize):
        texSize = rt.copy(texSize, "int")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        maxC = rt.binary("-", texSize, rt.i(1), 2, "int")
        edges = rt.texel_fetch(_u_edgeTex, coord, rt.i(0))
        edgeH = rt.swizzle(edges, "r")
        edgeV = rt.swizzle(edges, "g")
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if (bool(rt.binary("<", edgeH, rt.f(0.5))) and bool(rt.binary("<", edgeV, rt.f(0.5)))):
            return center
        blended = center
        distLeft = rt.f(0.0)
        distRight = rt.f(0.0)
        edgeLength = rt.f(0.0)
        weight = rt.f(0.0)
        neighbor = rt.construct(4, 0.0)
        if rt.binary(">", edgeH, rt.f(0.5)):
            distLeft = searchEdge__ivec2_ivec2_ivec2_int(coord, rt.construct(2, rt.unary("-", rt.i(1)), rt.i(0), base="int"), maxC, rt.i(0))
            distRight = searchEdge__ivec2_ivec2_ivec2_int(coord, rt.construct(2, rt.i(1), rt.i(0), base="int"), maxC, rt.i(0))
            edgeLength = rt.binary("+", rt.binary("+", distLeft, distRight, 1, "float"), rt.f(1.0), 1, "float")
            weight = rt.component_wise("clamp", rt.binary("/", rt.binary("*", _u_radius, rt.f(0.5), 1, "float"), rt.component_wise("sqrt", edgeLength, width=1), 1, "float"), rt.f(0.0), rt.f(0.5), width=1)
            neighbor = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.i(0), rt.i(1), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
            blended[:] = rt.component_wise("mix", blended, neighbor, weight, width=4)
        distUp = rt.f(0.0)
        distDown = rt.f(0.0)
        if rt.binary(">", edgeV, rt.f(0.5)):
            distUp = searchEdge__ivec2_ivec2_ivec2_int(coord, rt.construct(2, rt.i(0), rt.unary("-", rt.i(1)), base="int"), maxC, rt.i(1))
            distDown = searchEdge__ivec2_ivec2_ivec2_int(coord, rt.construct(2, rt.i(0), rt.i(1), base="int"), maxC, rt.i(1))
            edgeLength = rt.binary("+", rt.binary("+", distUp, distDown, 1, "float"), rt.f(1.0), 1, "float")
            weight = rt.component_wise("clamp", rt.binary("/", rt.binary("*", _u_radius, rt.f(0.5), 1, "float"), rt.component_wise("sqrt", edgeLength, width=1), 1, "float"), rt.f(0.0), rt.f(0.5), width=1)
            neighbor = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, rt.i(1), rt.i(0), base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0))
            blended[:] = rt.component_wise("mix", blended, neighbor, weight, width=4)
        return blended
    def edgeBlur__ivec2(texSize):
        texSize = rt.copy(texSize, "int")
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        maxC = rt.binary("-", texSize, rt.i(1), 2, "int")
        edges = rt.texel_fetch(_u_edgeTex, coord, rt.i(0))
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if (bool(rt.binary("<", rt.swizzle(edges, "r"), rt.f(0.5))) and bool(rt.binary("<", rt.swizzle(edges, "g"), rt.f(0.5)))):
            return center
        r = rt.construct(1, rt.component_wise("ceil", _u_radius, width=1), base="int")
        sigma = rt.binary("*", _u_radius, rt.f(0.5), 1, "float")
        sigma2 = rt.binary("*", rt.binary("*", rt.f(2.0), sigma, 1, "float"), sigma, 1, "float")
        sum = center
        totalWeight = rt.f(1.0)
        dy = rt.unary("-", rt.i(4))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<=", dy, rt.i(4))):
                break
            dx = rt.unary("-", rt.i(4))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for3_first = False
                if not (rt.binary("<=", dx, rt.i(4))):
                    break
                if (bool(rt.binary("==", dx, rt.i(0))) and bool(rt.binary("==", dy, rt.i(0)))):
                    continue
                if (bool(rt.binary(">", rt.component_wise("abs", dx, width=1), r)) or bool(rt.binary(">", rt.component_wise("abs", dy, width=1), r))):
                    continue
                d = rt.construct(1, rt.binary("+", rt.binary("*", dx, dx, 1, "int"), rt.binary("*", dy, dy, 1, "int"), 1, "int"))
                w = rt.component_wise("exp", rt.binary("/", rt.unary("-", d), sigma2, 1, "float"), width=1)
                sum[:] = rt.binary("+", sum, rt.binary("*", rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, rt.construct(2, dx, dy, base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), maxC, width=2), rt.i(0)), w, 4, "float"), 4, "float")
                totalWeight = rt.binary("+", totalWeight, w, 1, "float")
        return rt.binary("/", sum, totalWeight, 4, "float")
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2, "float")
        original = rt.texel_fetch(_u_inputTex, rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int"), rt.i(0))
        result = rt.construct(4, 0.0)
        if rt.binary("==", _u_smoothType, rt.i(0)):
            result[:] = msaaBlend__vec2_vec2_ivec2(uv, texelSize, texSize)
        else:
            if rt.binary("==", _u_smoothType, rt.i(1)):
                result[:] = smaaBlend__ivec2(texSize)
            else:
                result[:] = edgeBlur__ivec2(texSize)
        g.fragColor[:] = rt.component_wise("mix", original, result, _u_strength, width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
