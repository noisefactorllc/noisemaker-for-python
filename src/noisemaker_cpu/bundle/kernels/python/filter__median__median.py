def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_RADIUS = U.get("RADIUS", 0)
    _u_inputTex = T["inputTex"]
    _u_threshold = U.get("threshold", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def lessRecord__uvec2_uint_uvec2_uint(a, blueA, b, blueB):
        a = rt.copy(a, "uint")
        b = rt.copy(b, "uint")
        if rt.binary("!=", rt.swizzle(a, "x"), rt.swizzle(b, "x")):
            return rt.binary("<", rt.swizzle(a, "x"), rt.swizzle(b, "x"))
        if rt.binary("!=", rt.swizzle(a, "y"), rt.swizzle(b, "y")):
            return rt.binary("<", rt.swizzle(a, "y"), rt.swizzle(b, "y"))
        return rt.binary("<", blueA, blueB)
    def packRecordMajor__vec4(sampleColor):
        sampleColor = rt.copy(sampleColor, "float")
        brightness = rt.dot(rt.swizzle(sampleColor, "rgb"), rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
        packedRg = rt.pack_half_2x16(rt.swizzle(sampleColor, "rg"))
        orderedRg = rt.binary("|", rt.binary("<<", rt.binary("&", packedRg, rt.i(65535), 1, "uint"), rt.i(16), 1, "uint"), rt.binary(">>", packedRg, rt.i(16), 1, "uint"), 1, "uint")
        return rt.construct(2, rt.float_bits_to_uint(brightness), orderedRg, base="uint")
    def packRecordBlue__vec4(sampleColor):
        sampleColor = rt.copy(sampleColor, "float")
        return rt.binary("&", rt.pack_half_2x16(rt.construct(2, rt.swizzle(sampleColor, "b"), rt.f(0.0))), rt.i(65535), 1, "uint")
    def unpackRecordRgb__uvec2_uint(major, blue):
        major = rt.copy(major, "uint")
        packedRg = rt.binary("|", rt.binary("<<", rt.swizzle(major, "y"), rt.i(16), 1, "uint"), rt.binary(">>", rt.swizzle(major, "y"), rt.i(16), 1, "uint"), 1, "uint")
        rg = rt.unpack_half_2x16(packedRg)
        b = rt.swizzle(rt.unpack_half_2x16(blue), "x")
        return rt.construct(3, rg, b)
    def readRecord__ivec2_ivec2_int_int(center, dimensions, x, y):
        center = rt.copy(center, "int")
        dimensions = rt.copy(dimensions, "int")
        coord = rt.component_wise("clamp", rt.binary("+", center, rt.construct(2, x, y, base="int"), 2, "int"), rt.construct(2, rt.i(0), base="int"), rt.binary("-", dimensions, rt.construct(2, rt.i(1), base="int"), 2, "int"), width=2)
        return rt.texel_fetch(_u_inputTex, coord, rt.i(0))
    def main__void():
        majorRecords = rt.new_array(rt.i(49), 2)
        blueRecords = rt.new_array(rt.i(49), 1)
        dimensions = rt.texture_size(_u_inputTex)
        center = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        originalRgb = rt.construct(3, rt.f(0.0))
        centerAlpha = rt.f(1.0)
        index = rt.i(0)
        y = rt.unary("-", _u_RADIUS)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                y = rt.binary("+", y, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", y, _u_RADIUS)):
                break
            x = rt.unary("-", _u_RADIUS)
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    x = rt.binary("+", x, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", x, _u_RADIUS)):
                    break
                sampleColor = readRecord__ivec2_ivec2_int_int(center, dimensions, x, y)
                majorRecords[int(index)] = packRecordMajor__vec4(sampleColor)
                blueRecords[int(index)] = packRecordBlue__vec4(sampleColor)
                if (bool(rt.binary("==", x, rt.i(0))) and bool(rt.binary("==", y, rt.i(0)))):
                    originalRgb = rt.swizzle(sampleColor, "rgb")
                    centerAlpha = rt.swizzle(sampleColor, "a")
                index = rt.binary("+", index, rt.i(1), 1, "int")
        medianIndex = rt.binary("/", rt.i(49), rt.i(2), 1, "int")
        left = rt.i(0)
        right = rt.binary("-", rt.i(49), rt.i(1), 1, "int")
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
                    if not (lessRecord__uvec2_uint_uvec2_uint(majorRecords[int(scanLeft)], blueRecords[int(scanLeft)], pivotMajor, pivotBlue)):
                        break
                    scanLeft = rt.binary("+", scanLeft, rt.i(1), 1, "int")
                for _wh5 in range(1048576):
                    if not (lessRecord__uvec2_uint_uvec2_uint(pivotMajor, pivotBlue, majorRecords[int(scanRight)], blueRecords[int(scanRight)])):
                        break
                    scanRight = rt.binary("-", scanRight, rt.i(1), 1, "int")
                if rt.binary("<=", scanLeft, scanRight):
                    temporaryMajor = majorRecords[int(scanLeft)]
                    majorRecords[int(scanLeft)] = majorRecords[int(scanRight)]
                    majorRecords[int(scanRight)] = temporaryMajor
                    temporaryBlue = blueRecords[int(scanLeft)]
                    blueRecords[int(scanLeft)] = blueRecords[int(scanRight)]
                    blueRecords[int(scanRight)] = temporaryBlue
                    scanLeft = rt.binary("+", scanLeft, rt.i(1), 1, "int")
                    scanRight = rt.binary("-", scanRight, rt.i(1), 1, "int")
            if rt.binary("<", scanRight, medianIndex):
                left = scanLeft
            if rt.binary("<", medianIndex, scanLeft):
                right = scanRight
        medianRgb = unpackRecordRgb__uvec2_uint(majorRecords[int(medianIndex)], blueRecords[int(medianIndex)])
        difference = rt.component_wise("abs", rt.binary("-", originalRgb, medianRgb, 3, "float"), width=3)
        maxDifference = rt.component_wise("max", rt.component_wise("max", rt.swizzle(difference, "r"), rt.swizzle(difference, "g"), width=1), rt.swizzle(difference, "b"), width=1)
        replaceCenter = (bool(rt.binary("<=", _u_threshold, rt.f(0.0))) or bool(rt.binary(">=", maxDifference, rt.binary("/", _u_threshold, rt.f(100.0), 1, "float"))))
        g.fragColor = rt.construct(4, (medianRgb if replaceCenter else originalRgb), centerAlpha)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
