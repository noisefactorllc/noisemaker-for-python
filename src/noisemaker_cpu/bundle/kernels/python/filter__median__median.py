def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_RADIUS = U["RADIUS"]
    _u_inputTex = T["inputTex"]
    _u_threshold = U["threshold"]
    def cpu_ivec2__float(value):
        return rt.construct(2, value)
    def cpu_ivec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_ivec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def cpu_uvec2__float(value):
        return rt.construct(2, value)
    def cpu_uvec2__vec2(value):
        value = rt.copy(value)
        return value
    def cpu_uvec2__float_float(v0, v1):
        return rt.construct(2, v0, v1)
    def lessRecord__vec2_int_vec2_int(a, blueA, b, blueB):
        a = rt.copy(a)
        b = rt.copy(b)
        if rt.binary("!=", rt.swizzle(a, "x"), rt.swizzle(b, "x")):
            return rt.binary("<", rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        if rt.binary("!=", rt.swizzle(a, "y"), rt.swizzle(b, "y")):
            return rt.binary("<", rt.swizzle(a, "y"), rt.swizzle(b, "y"))
        return rt.binary("<", blueA, blueB)
    def packRecordMajor__vec4(sampleColor):
        sampleColor = rt.copy(sampleColor)
        brightness = rt.dot(rt.swizzle(sampleColor, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        packedRg = rt.component_wise("packHalf2x16", rt.swizzle(sampleColor, "rg"), width=2)
        orderedRg = rt.binary("|", rt.binary("<<", rt.binary("&", packedRg, rt.i(0xfff), 1), rt.i(16), 1), rt.binary(">>", packedRg, rt.i(16), 1), 1)
        return cpu_uvec2__float_float(rt.component_wise("floatBitsToUint", brightness, width=1), orderedRg)
    def packRecordBlue__vec4(sampleColor):
        sampleColor = rt.copy(sampleColor)
        return rt.binary("&", rt.component_wise("packHalf2x16", rt.construct(2, rt.swizzle(sampleColor, "b"), rt.f(0.0)), width=2), rt.i(0xfff), 2)
    def unpackRecordRgb__vec2_int(major, blue):
        major = rt.copy(major)
        packedRg = rt.binary("|", rt.binary("<<", rt.swizzle(major, "y"), rt.i(16), 1), rt.binary(">>", rt.swizzle(major, "y"), rt.i(16), 1), 1)
        rg = rt.component_wise("unpackHalf2x16", packedRg, width=1)
        b = rt.swizzle(rt.component_wise("unpackHalf2x16", blue, width=1), "x")
        return rt.construct(3, rg, b)
    def readRecord__ivec2_ivec2_int_int(center, dimensions, x, y):
        center = rt.copy(center)
        dimensions = rt.copy(dimensions)
        coord = rt.component_wise("clamp", rt.binary("+", center, cpu_ivec2__float_float(x, y), 2), cpu_ivec2__float(rt.i(0)), rt.binary("-", dimensions, cpu_ivec2__float(rt.i(1)), 2), width=2)
        return rt.texel_fetch(_u_inputTex, coord, rt.i(0))
    def main__void():
        majorRecords = rt.construct(2, 0.0)
        blueRecords = 0
        dimensions = rt.texture_size(_u_inputTex)
        center = cpu_ivec2__vec2(rt.swizzle(ctx.frag_coord, "xy"))
        originalRgb = rt.construct(3, rt.f(0.0))
        centerAlpha = rt.f(1.0)
        index = rt.i(0)
        y = rt.unary("-", _u_RADIUS)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1)
            _for0_first = False
            if not (rt.binary("<=", y, _u_RADIUS)):
                break
            x = rt.unary("-", _u_RADIUS)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1)
                _for1_first = False
                if not (rt.binary("<=", x, _u_RADIUS)):
                    break
                sampleColor = readRecord__ivec2_ivec2_int_int(center, dimensions, x, y)
                majorRecords[int(index)] = packRecordMajor__vec4(sampleColor)
                blueRecords[int(index)] = packRecordBlue__vec4(sampleColor)
                if rt.binary("&&", rt.binary("==", x, rt.i(0)), rt.binary("==", y, rt.i(0))):
                    originalRgb = rt.swizzle(sampleColor, "rgb")
                    centerAlpha = rt.swizzle(sampleColor, "a")
                index = rt.binary("+", index, rt.i(1), 1)
        medianIndex = rt.binary("/", rt.i(49), rt.i(2), 1)
        left = rt.i(0)
        right = rt.binary("-", rt.i(49), rt.i(1), 1)
        for _wh2 in range(1048576):
            if not (rt.binary("<", left, right)):
                break
            pivotMajor = majorRecords[int(medianIndex)]
            pivotBlue = blueRecords[int(medianIndex)]
            scanLeft = left
            scanRight = right
            for _wh3 in range(1048576):
                if not (rt.binary("<=", scanLeft, scanRight)):
                    break
                for _wh4 in range(1048576):
                    if not (lessRecord__vec2_int_vec2_int(majorRecords[int(scanLeft)], blueRecords[int(scanLeft)], pivotMajor, pivotBlue)):
                        break
                    scanLeft = rt.binary("+", scanLeft, rt.i(1), 1)
                for _wh5 in range(1048576):
                    if not (lessRecord__vec2_int_vec2_int(pivotMajor, pivotBlue, majorRecords[int(scanRight)], blueRecords[int(scanRight)])):
                        break
                    scanRight = rt.binary("-", scanRight, rt.i(1), 1)
                if rt.binary("<=", scanLeft, scanRight):
                    temporaryMajor = majorRecords[int(scanLeft)]
                    majorRecords[int(scanLeft)] = majorRecords[int(scanRight)]
                    majorRecords[int(scanRight)] = temporaryMajor
                    temporaryBlue = blueRecords[int(scanLeft)]
                    blueRecords[int(scanLeft)] = blueRecords[int(scanRight)]
                    blueRecords[int(scanRight)] = temporaryBlue
                    scanLeft = rt.binary("+", scanLeft, rt.i(1), 1)
                    scanRight = rt.binary("-", scanRight, rt.i(1), 1)
            if rt.binary("<", scanRight, medianIndex):
                left = scanLeft
            if rt.binary("<", medianIndex, scanLeft):
                right = scanRight
        medianRgb = unpackRecordRgb__vec2_int(majorRecords[int(medianIndex)], blueRecords[int(medianIndex)])
        difference = rt.component_wise("abs", rt.binary("-", originalRgb, medianRgb, 3), width=3)
        maxDifference = rt.component_wise("max", rt.component_wise("max", rt.swizzle(difference, "r"), rt.swizzle(difference, "g"), width=1), rt.swizzle(difference, "b"), width=1)
        replaceCenter = rt.binary("||", rt.binary("<=", _u_threshold, rt.f(0.0)), rt.binary(">=", maxDifference, rt.binary("/", _u_threshold, rt.f(100.0), 1)))
        g.fragColor = rt.construct(4, (medianRgb if replaceCenter else originalRgb), centerAlpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
