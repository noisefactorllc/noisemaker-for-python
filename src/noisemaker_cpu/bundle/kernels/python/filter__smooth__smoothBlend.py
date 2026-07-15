def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_inputTex = T["inputTex"]
    _u_edgeTex = T["edgeTex"]
    _u_smoothType = U["smoothType"]
    _u_strength = U["strength"]
    _u_threshold = U["threshold"]
    _u_radius = U["radius"]
    _u_samples = U["samples"]
    _u_searchSteps = U["searchSteps"]
    g.LUMA_WEIGHTS = rt.construct(3, rt.f(0.299), rt.f(0.587), rt.f(0.114))
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def luminance__vec3(rgb):
        rgb = rt.copy(rgb)
        return rt.dot(rgb, g.LUMA_WEIGHTS)
    def sampleBilinear__vec2_ivec2(uv, texSize):
        uv = rt.copy(uv)
        texSize = rt.copy(texSize)
        texCoord = rt.binary("-", rt.binary("*", uv, rt.construct(2, texSize), 2), rt.f(0.5), 2)
        base = cpu_ivec2__vec2(rt.component_wise("floor", texCoord, width=2))
        f = rt.binary("-", texCoord, rt.construct(2, base), 2)
        maxC = rt.binary("-", texSize, rt.i(1), 2)
        tl = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", base, cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
        tr = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
        bl = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
        br = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", base, cpu_ivec2__float_float(rt.i(1), rt.i(1)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
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
        uv = rt.copy(uv)
        texelSize = rt.copy(texelSize)
        texSize = rt.copy(texSize)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        maxC = rt.binary("-", texSize, rt.i(1), 2)
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        L = luminance__vec3(rt.swizzle(center, "rgb"))
        Ln = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(0), rt.unary("-", rt.i(1))), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0)), "rgb"))
        Ls = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0)), "rgb"))
        Lw = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0)), "rgb"))
        Le = luminance__vec3(rt.swizzle(rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0)), "rgb"))
        maxDiff = rt.component_wise("max", rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Ln, 1), width=1), rt.component_wise("abs", rt.binary("-", L, Ls, 1), width=1), width=1), rt.component_wise("max", rt.component_wise("abs", rt.binary("-", L, Lw, 1), width=1), rt.component_wise("abs", rt.binary("-", L, Le, 1), width=1), width=1), width=1)
        if rt.binary("<", maxDiff, _u_threshold):
            return center
        sum = rt.construct(4, rt.f(0.0))
        count = _u_samples
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<", i, rt.i(8))):
                break
            if rt.binary(">=", i, count):
                break
            offset = rt.binary("*", getSampleOffset__int_int(i, count), _u_radius, 2)
            sum = rt.binary("+", sum, sampleBilinear__vec2_ivec2(rt.binary("+", uv, rt.binary("*", offset, texelSize, 2), 2), texSize), 4)
        return rt.binary("/", sum, count, 4)
    def searchEdge__ivec2_ivec2_ivec2_int(coord, dir, maxC, component):
        coord = rt.copy(coord)
        dir = rt.copy(dir)
        maxC = rt.copy(maxC)
        i = rt.i(1)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1)
            _for1_first = False
            if not (rt.binary("<=", i, rt.i(32))):
                break
            if rt.binary(">", i, _u_searchSteps):
                break
            sampleCoord = rt.component_wise("clamp", rt.binary("+", coord, rt.binary("*", dir, i, 2), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2)
            edge = (rt.swizzle(rt.texel_fetch(_u_edgeTex, sampleCoord, rt.i(0)), "r") if rt.binary("==", component, rt.i(0)) else rt.swizzle(rt.texel_fetch(_u_edgeTex, sampleCoord, rt.i(0)), "g"))
            if rt.binary("<", edge, rt.f(0.5)):
                return rt.construct(1, rt.binary("-", i, rt.i(1), 1))
        return _u_searchSteps
    def smaaBlend__ivec2(texSize):
        texSize = rt.copy(texSize)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        maxC = rt.binary("-", texSize, rt.i(1), 2)
        edges = rt.texel_fetch(_u_edgeTex, coord, rt.i(0))
        edgeH = rt.swizzle(edges, "r")
        edgeV = rt.swizzle(edges, "g")
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if rt.binary("&&", rt.binary("<", edgeH, rt.f(0.5)), rt.binary("<", edgeV, rt.f(0.5))):
            return center
        blended = center
        if rt.binary(">", edgeH, rt.f(0.5)):
            distLeft = searchEdge__ivec2_ivec2_ivec2_int(coord, cpu_ivec2__float_float(rt.unary("-", rt.i(1)), rt.i(0)), maxC, rt.i(0))
            distRight = searchEdge__ivec2_ivec2_ivec2_int(coord, cpu_ivec2__float_float(rt.i(1), rt.i(0)), maxC, rt.i(0))
            edgeLength = rt.binary("+", rt.binary("+", distLeft, distRight, 1), rt.f(1.0), 1)
            weight = rt.component_wise("clamp", rt.binary("/", rt.binary("*", _u_radius, rt.f(0.5), 1), rt.component_wise("sqrt", edgeLength, width=1), 1), rt.f(0.0), rt.f(0.5), width=1)
            neighbor = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(0), rt.i(1)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
            blended = rt.component_wise("mix", blended, neighbor, weight, width=4)
        if rt.binary(">", edgeV, rt.f(0.5)):
            distUp = searchEdge__ivec2_ivec2_ivec2_int(coord, cpu_ivec2__float_float(rt.i(0), rt.unary("-", rt.i(1))), maxC, rt.i(1))
            distDown = searchEdge__ivec2_ivec2_ivec2_int(coord, cpu_ivec2__float_float(rt.i(0), rt.i(1)), maxC, rt.i(1))
            edgeLength = rt.binary("+", rt.binary("+", distUp, distDown, 1), rt.f(1.0), 1)
            weight = rt.component_wise("clamp", rt.binary("/", rt.binary("*", _u_radius, rt.f(0.5), 1), rt.component_wise("sqrt", edgeLength, width=1), 1), rt.f(0.0), rt.f(0.5), width=1)
            neighbor = rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(rt.i(1), rt.i(0)), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0))
            blended = rt.component_wise("mix", blended, neighbor, weight, width=4)
        return blended
    def edgeBlur__ivec2(texSize):
        texSize = rt.copy(texSize)
        coord = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        maxC = rt.binary("-", texSize, rt.i(1), 2)
        edges = rt.texel_fetch(_u_edgeTex, coord, rt.i(0))
        center = rt.texel_fetch(_u_inputTex, coord, rt.i(0))
        if rt.binary("&&", rt.binary("<", rt.swizzle(edges, "r"), rt.f(0.5)), rt.binary("<", rt.swizzle(edges, "g"), rt.f(0.5))):
            return center
        r = rt.construct(1, rt.component_wise("ceil", _u_radius, width=1))
        sigma = rt.binary("*", _u_radius, rt.f(0.5), 1)
        sigma2 = rt.binary("*", rt.binary("*", rt.f(2.0), sigma, 1), sigma, 1)
        sum = center
        totalWeight = rt.f(1.0)
        dy = rt.unary("-", rt.i(4))
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                dy = rt.binary("+", dy, rt.i(1), 1)
            _for2_first = False
            if not (rt.binary("<=", dy, rt.i(4))):
                break
            dx = rt.unary("-", rt.i(4))
            _for3_first = True
            for _for3 in range(1048576):
                if not _for3_first:
                    dx = rt.binary("+", dx, rt.i(1), 1)
                _for3_first = False
                if not (rt.binary("<=", dx, rt.i(4))):
                    break
                if rt.binary("&&", rt.binary("==", dx, rt.i(0)), rt.binary("==", dy, rt.i(0))):
                    continue
                if rt.binary("||", rt.binary(">", rt.component_wise("abs", dx, width=1), r), rt.binary(">", rt.component_wise("abs", dy, width=1), r)):
                    continue
                d = rt.construct(1, rt.binary("+", rt.binary("*", dx, dx, 1), rt.binary("*", dy, dy, 1), 1))
                w = rt.component_wise("exp", rt.binary("/", rt.unary("-", d), sigma2, 1), width=1)
                sum = rt.binary("+", sum, rt.binary("*", rt.texel_fetch(_u_inputTex, rt.component_wise("clamp", rt.binary("+", coord, cpu_ivec2__float_float(dx, dy), 2), cpu_ivec2__float(rt.i(0)), maxC, width=2), rt.i(0)), w, 4), 4)
                totalWeight = rt.binary("+", totalWeight, w, 1)
        return rt.binary("/", sum, totalWeight, 4)
    def main__void():
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        texSize = rt.texture_size(_u_inputTex)
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(2, texSize), 2)
        texelSize = rt.binary("/", rt.f(1.0), rt.construct(2, texSize), 2)
        original = rt.texel_fetch(_u_inputTex, cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy")), rt.i(0))
        result = rt.construct(4, 0.0)
        if rt.binary("==", _u_smoothType, rt.i(0)):
            result = msaaBlend__vec2_vec2_ivec2(uv, texelSize, texSize)
        else:
            if rt.binary("==", _u_smoothType, rt.i(1)):
                result = smaaBlend__ivec2(texSize)
            else:
                result = edgeBlur__ivec2(texSize)
        g.fragColor = rt.component_wise("mix", original, result, _u_strength, width=4)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
