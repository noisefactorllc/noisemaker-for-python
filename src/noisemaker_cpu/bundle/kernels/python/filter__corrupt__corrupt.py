def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_inputTex = T["inputTex"]
    _u_tileOffset = U["tileOffset"]
    _u_fullResolution = U["fullResolution"]
    _u_time = U["time"]
    _u_seed = U["seed"]
    _u_intensity = U["intensity"]
    _u_sort = U["sort"]
    _u_shift = U["shift"]
    _u_bits = U["bits"]
    _u_channelShift = U["channelShift"]
    _u_speed = U["speed"]
    _u_melt = U["melt"]
    _u_scatter = U["scatter"]
    _u_bandHeight = U["bandHeight"]
    _u_renderScale = U["renderScale"]
    def cpu_uvec3__float(value):
        return rt.construct(3, value)
    def cpu_uvec3__vec3(value):
        value = rt.copy(value)
        return value
    def cpu_uvec3__float_float_float(v0, v1, v2):
        return rt.construct(3, v0, v1, v2)
    def pcg__vec3(v):
        v = rt.copy(v)
        v = rt.binary("+", rt.binary("*", v, rt.i(1664525), 3), rt.i(1013904223), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        v = rt.binary("^", v, rt.binary(">>", v, rt.i(16), 3), 3)
        v = rt.assign_swizzle(v, "x", rt.binary("+", rt.swizzle(v, "x"), rt.binary("*", rt.swizzle(v, "y"), rt.swizzle(v, "z"), 1), 1))
        v = rt.assign_swizzle(v, "y", rt.binary("+", rt.swizzle(v, "y"), rt.binary("*", rt.swizzle(v, "z"), rt.swizzle(v, "x"), 1), 1))
        v = rt.assign_swizzle(v, "z", rt.binary("+", rt.swizzle(v, "z"), rt.binary("*", rt.swizzle(v, "x"), rt.swizzle(v, "y"), 1), 1))
        return v
    def prng__vec3(p):
        p = rt.copy(p)
        p = rt.assign_swizzle(p, "x", (rt.binary("*", rt.swizzle(p, "x"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "x"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "x")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "y", (rt.binary("*", rt.swizzle(p, "y"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "y"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "y")), rt.f(2.0), 1), rt.f(1.0), 1)))
        p = rt.assign_swizzle(p, "z", (rt.binary("*", rt.swizzle(p, "z"), rt.f(2.0), 1) if rt.binary(">=", rt.swizzle(p, "z"), rt.f(0.0)) else rt.binary("+", rt.binary("*", rt.unary("-", rt.swizzle(p, "z")), rt.f(2.0), 1), rt.f(1.0), 1)))
        return rt.binary("/", rt.construct(3, pcg__vec3(cpu_uvec3__vec3(p))), rt.f(4294967295.0), 3)
    def rowTime__float_float(row, t):
        phase = rt.swizzle(prng__vec3(rt.construct(3, row, rt.binary("+", _u_seed, rt.f(777.0), 1), rt.f(0.0))), "x")
        return rt.component_wise("floor", rt.binary("*", rt.binary("+", t, phase, 1), rt.f(8.0), 1), width=1)
    def lineHash__float_float(line, rt):
        return prng__vec3(rt.construct(3, line, _u_seed, rt))
    def pixelSort__vec2_float_float_float_float(uv, row, sortAmt, rt, resX):
        uv = rt.copy(uv)
        rh = lineHash__float_float(row, rt)
        threshold = rt.component_wise("mix", rt.f(0.8), rt.f(0.2), sortAmt, width=1)
        regionSize = rt.binary("+", rt.f(3.0), rt.binary("*", rt.swizzle(rh, "y"), rt.f(20.0), 1), 1)
        region = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1), regionSize, 1), width=1)
        regionHash = prng__vec3(rt.construct(3, region, row, rt.binary("+", _u_seed, rt, 1)))
        regionPos = rt.component_wise("fract", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1), regionSize, 1), width=1)
        sortShift = rt.binary("*", rt.binary("*", rt.binary("*", regionPos, rt.swizzle(regionHash, "x"), 1), sortAmt, 1), rt.f(0.15), 1)
        if rt.binary(">", rt.swizzle(regionHash, "y"), threshold):
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), sortShift, 1), width=1))
        return uv
    def byteShift__vec2_float_float_float_float(uv, row, shiftAmt, rt, resX):
        uv = rt.copy(uv)
        rh = lineHash__float_float(row, rt)
        chunkWidth = rt.binary("+", rt.f(8.0), rt.binary("*", rt.swizzle(rh, "x"), rt.f(80.0), 1), 1)
        chunk = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1), chunkWidth, 1), width=1)
        ch = prng__vec3(rt.construct(3, chunk, rt.binary("+", row, rt.f(200.0), 1), rt.binary("+", _u_seed, rt, 1)))
        shiftPx = rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(ch, "x"), rt.f(0.5), 1), rt.f(2.0), 1), shiftAmt, 1), resX, 1), rt.f(0.15), 1)
        sparsity = rt.component_wise("mix", rt.f(0.85), rt.f(0.3), shiftAmt, width=1)
        if rt.binary(">", rt.swizzle(ch, "y"), sparsity):
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("/", shiftPx, resX, 1), 1), width=1))
        return uv
    def bitCorrupt__vec3_vec2_float_float_float_float(color, uv, row, bitAmt, rt, resX):
        color = rt.copy(color)
        uv = rt.copy(uv)
        bh = lineHash__float_float(rt.binary("+", row, rt.f(400.0), 1), rt)
        levels = rt.component_wise("mix", rt.f(256.0), rt.f(2.0), rt.binary("*", bitAmt, bitAmt, 1), width=1)
        color = rt.binary("/", rt.component_wise("floor", rt.binary("+", rt.binary("*", color, levels, 3), rt.f(0.5), 3), width=3), levels, 3)
        if rt.binary(">", bitAmt, rt.f(0.3)):
            xorStrength = rt.binary("/", rt.binary("-", bitAmt, rt.f(0.3), 1), rt.f(0.7), 1)
            px = rt.component_wise("floor", rt.binary("*", rt.swizzle(uv, "x"), resX, 1), width=1)
            xorHash = prng__vec3(rt.construct(3, px, row, rt.binary("+", rt.binary("+", _u_seed, rt, 1), rt.f(500.0), 1)))
            mask = rt.component_wise("step", rt.construct(3, rt.binary("-", rt.f(1.0), rt.binary("*", xorStrength, rt.f(0.5), 1), 1)), xorHash, width=3)
            color = rt.component_wise("mix", color, rt.binary("-", rt.f(1.0), color, 3), mask, width=3)
        if rt.binary(">", bitAmt, rt.f(0.6)):
            shiftStr = rt.binary("/", rt.binary("-", bitAmt, rt.f(0.6), 1), rt.f(0.4), 1)
            bitShift = rt.binary("+", rt.component_wise("floor", rt.binary("*", rt.swizzle(bh, "x"), rt.f(4.0), 1), width=1), rt.f(1.0), 1)
            scale = rt.component_wise("pow", rt.f(2.0), bitShift, width=1)
            color = rt.component_wise("fract", rt.binary("*", color, rt.component_wise("mix", rt.f(1.0), scale, shiftStr, width=1), 3), width=3)
        return color
    def meltDisplace__vec2_float_float_float_float(uv, meltAmt, t, resX, rs):
        uv = rt.copy(uv)
        col = rt.component_wise("floor", rt.binary("/", rt.binary("*", rt.swizzle(uv, "x"), resX, 1), rt.f(3.0), 1), width=1)
        colPhase = rt.swizzle(prng__vec3(rt.construct(3, col, rt.binary("+", _u_seed, rt.f(601.0), 1), rt.f(0.0))), "x")
        dripHash = prng__vec3(rt.construct(3, col, rt.binary("+", _u_seed, rt.f(600.0), 1), rt.component_wise("floor", rt.binary("*", rt.binary("+", t, colPhase, 1), rt.f(8.0), 1), width=1)))
        gravity = rt.binary("*", rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1), rt.binary("-", rt.f(1.0), rt.swizzle(uv, "y"), 1), 1)
        dripAmt = rt.binary("*", rt.binary("*", rt.binary("*", rt.swizzle(dripHash, "x"), meltAmt, 1), gravity, 1), rt.f(0.4), 1)
        dripProb = rt.component_wise("mix", rt.f(0.9), rt.f(0.2), meltAmt, width=1)
        if rt.binary(">", rt.swizzle(dripHash, "y"), dripProb):
            wobble = rt.binary("*", rt.binary("*", rt.component_wise("sin", rt.binary("+", rt.binary("+", rt.binary("*", rt.swizzle(uv, "y"), rt.f(20.0), 1), rt.binary("*", rt.swizzle(dripHash, "z"), rt.f(6.28318530718), 1), 1), t, 1), width=1), meltAmt, 1), rt.f(0.02), 1)
            uv = rt.assign_swizzle(uv, "y", rt.component_wise("clamp", rt.binary("+", rt.swizzle(uv, "y"), dripAmt, 1), rt.f(0.0), rt.f(1.0), width=1))
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), wobble, 1), width=1))
        return uv
    def scatterDisplace__vec2_float_float_float_vec2(uv, scatterAmt, t, rs, tileOff):
        uv = rt.copy(uv)
        tileOff = rt.copy(tileOff)
        scaledCoord = rt.component_wise("floor", rt.binary("/", rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), tileOff, 2), rs, 2), width=2)
        phaseHash = prng__vec3(rt.construct(3, scaledCoord, rt.binary("+", _u_seed, rt.f(700.0), 1)))
        pixTime = rt.component_wise("floor", rt.binary("*", rt.binary("+", t, rt.swizzle(phaseHash, "x"), 1), rt.f(8.0), 1), width=1)
        pixHash = prng__vec3(rt.construct(3, scaledCoord, rt.binary("+", pixTime, _u_seed, 1)))
        threshold = rt.component_wise("mix", rt.f(0.98), rt.f(0.1), rt.binary("*", scatterAmt, scatterAmt, 1), width=1)
        if rt.binary(">", rt.swizzle(pixHash, "x"), threshold):
            dirHash = prng__vec3(rt.construct(3, rt.binary("+", scaledCoord, rt.f(1000.0), 2), rt.binary("+", pixTime, _u_seed, 1)))
            dist = rt.binary("*", rt.binary("*", scatterAmt, rt.f(0.15), 1), rt.binary("+", rt.f(0.5), rt.binary("*", rt.swizzle(pixHash, "y"), rt.f(0.5), 1), 1), 1)
            uv = rt.assign_swizzle(uv, "x", rt.component_wise("fract", rt.binary("+", rt.swizzle(uv, "x"), rt.binary("*", rt.binary("-", rt.swizzle(dirHash, "x"), rt.f(0.5), 1), dist, 1), 1), width=1))
            uv = rt.assign_swizzle(uv, "y", rt.component_wise("clamp", rt.binary("+", rt.swizzle(uv, "y"), rt.binary("*", rt.binary("-", rt.swizzle(dirHash, "y"), rt.f(0.5), 1), dist, 1), 1), rt.f(0.0), rt.f(1.0), width=1))
        return uv
    def main__void():
        tileDims = rt.construct(2, rt.texture_size(_u_inputTex))
        resolution = (_u_fullResolution if rt.binary(">", rt.swizzle(_u_fullResolution, "x"), rt.f(0.0)) else tileDims)
        globalCoord = rt.binary("+", rt.swizzle(ctx.frag_coord, "xy"), _u_tileOffset, 2)
        uv = rt.binary("/", globalCoord, resolution, 2)
        rs = rt.component_wise("max", _u_renderScale, rt.f(1.0), width=1)
        resX = rt.binary("/", rt.swizzle(resolution, "x"), rs, 1)
        spd = rt.component_wise("floor", _u_speed, width=1)
        t = rt.binary("*", rt.binary("*", _u_time, rt.f(6.28318530718), 1), spd, 1)
        rawRow = rt.binary("/", rt.swizzle(globalCoord, "y"), rs, 1)
        bh = rt.component_wise("max", rt.f(1.0), rt.component_wise("floor", rt.binary("*", _u_bandHeight, rt.f(0.32), 1), width=1), width=1)
        row = rt.component_wise("floor", rt.binary("/", rawRow, bh, 1), width=1)
        rt = rowTime__float_float(row, t)
        rowHash = lineHash__float_float(row, rt)
        prob = rt.binary("/", _u_intensity, rt.f(100.0), 1)
        isCorrupt = rt.binary("<", rt.swizzle(rowHash, "x"), prob)
        sampleUv = uv
        meltAmt = rt.binary("/", _u_melt, rt.f(100.0), 1)
        if rt.binary(">", meltAmt, rt.f(0.0)):
            sampleUv = meltDisplace__vec2_float_float_float_float(sampleUv, meltAmt, t, resX, rs)
        scatterAmt = rt.binary("/", _u_scatter, rt.f(100.0), 1)
        if rt.binary(">", scatterAmt, rt.f(0.0)):
            sampleUv = scatterDisplace__vec2_float_float_float_vec2(sampleUv, scatterAmt, t, rs, _u_tileOffset)
        if isCorrupt:
            sortAmt = rt.binary("/", _u_sort, rt.f(100.0), 1)
            shiftAmt = rt.binary("/", _u_shift, rt.f(100.0), 1)
            if rt.binary(">", sortAmt, rt.f(0.0)):
                sampleUv = pixelSort__vec2_float_float_float_float(sampleUv, row, sortAmt, rt, resX)
            if rt.binary(">", shiftAmt, rt.f(0.0)):
                sampleUv = byteShift__vec2_float_float_float_float(sampleUv, row, shiftAmt, rt, resX)
        color = rt.swizzle(rt.texture(_u_inputTex, sampleUv), "rgb")
        if rt.binary("&&", rt.binary(">", _u_channelShift, rt.f(0.0)), isCorrupt):
            chAmt = rt.binary("/", _u_channelShift, rt.f(100.0), 1)
            chHash = lineHash__float_float(rt.binary("+", row, rt.f(300.0), 1), rt)
            rShift = rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(chHash, "x"), rt.f(0.5), 1), chAmt, 1), rt.f(0.08), 1)
            bShift = rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(chHash, "y"), rt.f(0.5), 1), chAmt, 1), rt.f(0.08), 1)
            rUv = rt.construct(2, rt.component_wise("fract", rt.binary("+", rt.swizzle(sampleUv, "x"), rShift, 1), width=1), rt.swizzle(sampleUv, "y"))
            bUv = rt.construct(2, rt.component_wise("fract", rt.binary("+", rt.swizzle(sampleUv, "x"), bShift, 1), width=1), rt.swizzle(sampleUv, "y"))
            color = rt.assign_swizzle(color, "r", rt.swizzle(rt.texture(_u_inputTex, rUv), "r"))
            color = rt.assign_swizzle(color, "b", rt.swizzle(rt.texture(_u_inputTex, bUv), "b"))
        if rt.binary("&&", rt.binary(">", _u_bits, rt.f(0.0)), isCorrupt):
            color = bitCorrupt__vec3_vec2_float_float_float_float(color, uv, row, rt.binary("/", _u_bits, rt.f(100.0), 1), rt, resX)
        g.fragColor = rt.construct(4, color, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
