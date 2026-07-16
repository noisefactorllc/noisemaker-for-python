def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U.get("tileOffset", rt.construct(2, 0.0))
    _u_fullResolution = U.get("fullResolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", rt.f(0.0))
    _u_intensity = U.get("intensity", rt.f(0.0))
    _u_sort = U.get("sort", rt.f(0.0))
    _u_shift = U.get("shift", rt.f(0.0))
    _u_bits = U.get("bits", rt.f(0.0))
    _u_channelShift = U.get("channelShift", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_melt = U.get("melt", rt.f(0.0))
    _u_scatter = U.get("scatter", rt.f(0.0))
    _u_bandHeight = U.get("bandHeight", rt.f(0.0))
    _u_renderScale = U.get("renderScale", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    def pcg__uvec3(v):
        v = rt.copy(v, "uint")
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3, "uint"), rt.i(1013904223), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3, "uint"), 3, "uint")
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1, "uint"), 1, "uint"))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1, "uint"), 1, "uint"))
        return v
    def prng__vec3(p):
        p = rt.copy(p, "float")
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1, "float") if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")))
        return rt.binary("/", rt.construct(3, pcg__uvec3(rt.construct(3, p, base="uint"))), rt.construct(1, rt.i(4294967295)), 3, "float")
    def rowTime__float_float(row, t):
        phase = rt.swizzle(prng__vec3(rt.construct(3, row, rt.binary("+", _u_seed, rt.f(777.0), 1, "float"), rt.f(0.0))), "x")
        return rt.component_wise("floor", rt.binary("*", rt.binary("+", t, phase, 1, "float"), rt.f(8.0), 1, "float"), width=1)
    def lineHash__float_float(line, _rt):
        return prng__vec3(rt.construct(3, line, _u_seed, _rt))
    def pixelSort__vec2_float_float_float_float(uv, row, sortAmt, _rt, resX):
        uv = rt.copy(uv, "float")
        rh = lineHash__float_float(row, _rt)
        threshold = rt.component_wise("mix", rt.f(0.8), rt.f(0.2), sortAmt, width=1)
        regionSize = rt.binary("+", rt.f(3.0), rt.binary("*", rt.swizzle(rh, "y"), rt.f(20.0), 1, "float"), 1, "float")
        region = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1, "float"), regionSize, 1, "float"), width=1)
        regionHash = prng__vec3(rt.construct(3, region, row, rt.binary("+", _u_seed, _rt, 1, "float")))
        regionPos = rt.component_wise("fract", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1, "float"), regionSize, 1, "float"), width=1)
        sortShift = rt.binary("*", rt.binary("*", rt.binary("*", regionPos, rt.swizzle(regionHash, "x"), 1, "float"), sortAmt, 1, "float"), rt.f(0.15), 1, "float")
        if rt.binary(">", rt.swizzle(regionHash, "y"), threshold):
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), sortShift, 1, "float"), width=1))
        return uv
    def byteShift__vec2_float_float_float_float(uv, row, shiftAmt, _rt, resX):
        uv = rt.copy(uv, "float")
        rh = lineHash__float_float(row, _rt)
        chunkWidth = rt.binary("+", rt.f(8.0), rt.binary("*", rt.swizzle(rh, "x"), rt.f(80.0), 1, "float"), 1, "float")
        chunk = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1, "float"), chunkWidth, 1, "float"), width=1)
        ch = prng__vec3(rt.construct(3, chunk, rt.binary("+", row, rt.f(200.0), 1, "float"), rt.binary("+", _u_seed, _rt, 1, "float")))
        shiftPx = rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(ch, "x"), rt.f(0.5), 1, "float"), rt.f(2.0), 1, "float"), shiftAmt, 1, "float"), resX, 1, "float"), rt.f(0.15), 1, "float")
        sparsity = rt.component_wise("mix", rt.f(0.85), rt.f(0.3), shiftAmt, width=1)
        if rt.binary(">", rt.swizzle(ch, "y"), sparsity):
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("/", shiftPx, resX, 1, "float"), 1, "float"), width=1))
        return uv
    def bitCorrupt__vec3_vec2_float_float_float_float(color, uv, row, bitAmt, _rt, resX):
        color = rt.copy(color, "float")
        uv = rt.copy(uv, "float")
        bh = lineHash__float_float(rt.binary("+", row, rt.f(400.0), 1, "float"), _rt)
        levels = rt.component_wise("mix", rt.f(256.0), rt.f(2.0), rt.binary("*", bitAmt, bitAmt, 1, "float"), width=1)
        color = rt.binary("/", rt.component_wise("floor", rt.binary("+", rt.binary("*", color, levels, 3, "float"), rt.f(0.5), 3, "float"), width=3), levels, 3, "float")
        xorStrength = rt.f(0.0)
        px = rt.f(0.0)
        xorHash = rt.construct(3, 0.0)
        mask = rt.construct(3, 0.0)
        if rt.binary(">", bitAmt, rt.f(0.3)):
            xorStrength = rt.binary("/", rt.binary("-", bitAmt, rt.f(0.3), 1, "float"), rt.f(0.7), 1, "float")
            px = rt.component_wise("floor", rt.binary("*", rt.swizzle(uv, "x"), resX, 1, "float"), width=1)
            xorHash = prng__vec3(rt.construct(3, px, row, rt.binary("+", rt.binary("+", _u_seed, _rt, 1, "float"), rt.f(500.0), 1, "float")))
            mask = rt.component_wise("step", rt.construct(3, rt.binary("-", rt.f(1.0), rt.binary("*", xorStrength, rt.f(0.5), 1, "float"), 1, "float")), xorHash, width=3)
            color = rt.component_wise("mix", color, rt.binary("-", rt.f(1.0), color, 3, "float"), mask, width=3)
        shiftStr = rt.f(0.0)
        bitShift = rt.f(0.0)
        scale = rt.f(0.0)
        if rt.binary(">", bitAmt, rt.f(0.6)):
            shiftStr = rt.binary("/", rt.binary("-", bitAmt, rt.f(0.6), 1, "float"), rt.f(0.4), 1, "float")
            bitShift = rt.binary("+", rt.component_wise("floor", rt.binary("*", rt.swizzle(bh, "x"), rt.f(4.0), 1, "float"), width=1), rt.f(1.0), 1, "float")
            scale = rt.component_wise("pow", rt.f(2.0), bitShift, width=1)
            color = rt.component_wise("fract", rt.binary("*", color, rt.component_wise("mix", rt.f(1.0), scale, shiftStr, width=1), 3, "float"), width=3)
        return color
    def meltDisplace__vec2_float_float_float_float(uv, meltAmt, t, resX, rs):
        uv = rt.copy(uv, "float")
        col = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1, "float"), rt.f(3.0), 1, "float"), width=1)
        colPhase = rt.swizzle(prng__vec3(rt.construct(3, col, rt.binary("+", _u_seed, rt.f(601.0), 1, "float"), rt.f(0.0))), "x")
        dripHash = prng__vec3(rt.construct(3, col, rt.binary("+", _u_seed, rt.f(600.0), 1, "float"), rt.component_wise("floor", rt.binary("*", rt.binary("+", t, colPhase, 1, "float"), rt.f(8.0), 1, "float"), width=1)))
        gravity = rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"), rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1, "float"), 1, "float")
        dripAmt = rt.binary("*", rt.binary("*", rt.binary("*", rt.swizzle(dripHash, "x"), meltAmt, 1, "float"), gravity, 1, "float"), rt.f(0.4), 1, "float")
        dripProb = rt.component_wise("mix", rt.f(0.9), rt.f(0.2), meltAmt, width=1)
        wobble = rt.f(0.0)
        if rt.binary(">", rt.swizzle(dripHash, "y"), dripProb):
            wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(uv, "y"), rt.f(20.0), 1, "float"), rt.binary("*", rt.swizzle(dripHash, "z"), rt.f(6.28318530718), 1, "float"), 1, "float"), t, 1, "float"), width=1), meltAmt, 1, "float"), rt.f(0.02), 1, "float")
            uv = rt.assign_swizzle(uv, "y", rt.component_wise("clamp", rt.binary("+", rt.swizzle(uv, "y"), dripAmt, 1, "float"), rt.f(0.0), rt.f(1.0), width=1))
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), wobble, 1, "float"), width=1))
        return uv
    def scatterDisplace__vec2_float_float_float_vec2(uv, scatterAmt, t, rs, tileOff):
        uv = rt.copy(uv, "float")
        tileOff = rt.copy(tileOff, "float")
        scaledCoord = rt.component_wise("floor", rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), tileOff, 2, "float"), rs, 2, "float"), width=2)
        phaseHash = prng__vec3(rt.construct(3, scaledCoord, rt.binary("+", _u_seed, rt.f(700.0), 1, "float")))
        pixTime = rt.component_wise("floor", rt.binary("*", rt.binary("+", t, rt.swizzle(phaseHash, "x"), 1, "float"), rt.f(8.0), 1, "float"), width=1)
        pixHash = prng__vec3(rt.construct(3, scaledCoord, rt.binary("+", pixTime, _u_seed, 1, "float")))
        threshold = rt.component_wise("mix", rt.f(0.98), rt.f(0.1), rt.binary("*", scatterAmt, scatterAmt, 1, "float"), width=1)
        dirHash = rt.construct(3, 0.0)
        dist = rt.f(0.0)
        if rt.binary(">", rt.swizzle(pixHash, "x"), threshold):
            dirHash = prng__vec3(rt.construct(3, rt.binary("+", scaledCoord, rt.f(1000.0), 2, "float"), rt.binary("+", pixTime, _u_seed, 1, "float")))
            dist = rt.binary("*", rt.binary("*", scatterAmt, rt.f(0.15), 1, "float"), rt.binary("+", rt.f(0.5), rt.binary("*", rt.swizzle(pixHash, "y"), rt.f(0.5), 1, "float"), 1, "float"), 1, "float")
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", rt.binary("-", rt.swizzle(dirHash, "x"), rt.f(0.5), 1, "float"), dist, 1, "float"), 1, "float"), width=1))
            uv = rt.assign_swizzle(uv, "y", rt.component_wise("clamp", rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", rt.binary("-", rt.swizzle(dirHash, "y"), rt.f(0.5), 1, "float"), dist, 1, "float"), 1, "float"), rt.f(0.0), rt.f(1.0), width=1))
        return uv
    def main__void():
        tileDims = rt.construct(2, rt.texture_size(_u_inputTex))
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2, "float")
        uv = rt.binary("/", globalCoord, resolution, 2, "float")
        rs = rt.component_wise("max", _u_renderScale, rt.f(1.0), width=1)
        resX = rt.binary("/", rt.swizzle(resolution, "x"), rs, 1, "float")
        spd = rt.component_wise("floor", _u_speed, width=1)
        t = rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1, "float"), spd, 1, "float")
        rawRow = rt.binary("/", rt.swizzle(globalCoord, "y"), rs, 1, "float")
        bh = rt.component_wise("max", rt.f(1.0), rt.component_wise("floor", rt.binary("*", _u_bandHeight, rt.f(0.32), 1, "float"), width=1), width=1)
        row = rt.component_wise("floor", rt.binary("/", rawRow, bh, 1, "float"), width=1)
        _rt = rowTime__float_float(row, t)
        rowHash = lineHash__float_float(row, _rt)
        prob = rt.binary("/", _u_intensity, rt.f(100.0), 1, "float")
        isCorrupt = rt.binary("<", rt.swizzle(rowHash, "x"), prob)
        sampleUv = uv
        meltAmt = rt.binary("/", _u_melt, rt.f(100.0), 1, "float")
        if rt.binary(">", meltAmt, rt.f(0.0)):
            sampleUv = meltDisplace__vec2_float_float_float_float(sampleUv, meltAmt, t, resX, rs)
        scatterAmt = rt.binary("/", _u_scatter, rt.f(100.0), 1, "float")
        if rt.binary(">", scatterAmt, rt.f(0.0)):
            sampleUv = scatterDisplace__vec2_float_float_float_vec2(sampleUv, scatterAmt, t, rs, _u_tileOffset)
        sortAmt = rt.f(0.0)
        shiftAmt = rt.f(0.0)
        if isCorrupt:
            sortAmt = rt.binary("/", _u_sort, rt.f(100.0), 1, "float")
            shiftAmt = rt.binary("/", _u_shift, rt.f(100.0), 1, "float")
            if rt.binary(">", sortAmt, rt.f(0.0)):
                sampleUv = pixelSort__vec2_float_float_float_float(sampleUv, row, sortAmt, _rt, resX)
            if rt.binary(">", shiftAmt, rt.f(0.0)):
                sampleUv = byteShift__vec2_float_float_float_float(sampleUv, row, shiftAmt, _rt, resX)
        color = rt.swizzle(rt.texture(_u_inputTex, sampleUv), "rgb")
        chAmt = rt.f(0.0)
        chHash = rt.construct(3, 0.0)
        rShift = rt.f(0.0)
        bShift = rt.f(0.0)
        rUv = rt.construct(2, 0.0)
        bUv = rt.construct(2, 0.0)
        if (bool(rt.binary(">", _u_channelShift, rt.f(0.0))) and bool(isCorrupt)):
            chAmt = rt.binary("/", _u_channelShift, rt.f(100.0), 1, "float")
            chHash = lineHash__float_float(rt.binary("+", row, rt.f(300.0), 1, "float"), _rt)
            rShift = rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(chHash, "x"), rt.f(0.5), 1, "float"), chAmt, 1, "float"), rt.f(0.08), 1, "float")
            bShift = rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(chHash, "y"), rt.f(0.5), 1, "float"), chAmt, 1, "float"), rt.f(0.08), 1, "float")
            rUv = rt.construct(2, rt.component_wise("fract", rt.binary("+", rt.swizzle(sampleUv, "x"), rShift, 1, "float"), width=1), rt.swizzle(sampleUv, "y"))
            bUv = rt.construct(2, rt.component_wise("fract", rt.binary("+", rt.swizzle(sampleUv, "x"), bShift, 1, "float"), width=1), rt.swizzle(sampleUv, "y"))
            color = rt.assign_swizzle(color, "r", rt.swizzle(rt.texture(_u_inputTex, rUv), "r"))
            color = rt.assign_swizzle(color, "b", rt.swizzle(rt.texture(_u_inputTex, bUv), "b"))
        if (bool(rt.binary(">", _u_bits, rt.f(0.0))) and bool(isCorrupt)):
            color = bitCorrupt__vec3_vec2_float_float_float_float(color, uv, row, rt.binary("/", _u_bits, rt.f(100.0), 1, "float"), _rt, resX)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
