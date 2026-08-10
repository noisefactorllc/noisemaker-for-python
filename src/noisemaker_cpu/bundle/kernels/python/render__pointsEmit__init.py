def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_seed = U.get("seed", 0)
    _u_stateSize = U.get("stateSize", 0)
    _u_layoutMode = U.get("layoutMode", 0)
    _u_attrition = U.get("attrition", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    _u_inputTex = T["inputTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def hash2__uint(seed):
        return rt.construct(2, hash__uint(seed), hash__uint(rt.binary("+", seed, rt.i(1), 1, "uint")))
    def main__void():
        stateCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), rt.construct(1, _u_stateSize), 2, "float")
        agentSeed = rt.binary("+", rt.construct(1, rt.binary("+", rt.swizzle(stateCoord, "x"), rt.binary("*", rt.swizzle(stateCoord, "y"), _u_stateSize, 1, "int"), 1, "int"), base="uint"), rt.construct(1, _u_seed, base="uint"), 1, "uint")
        pPos = rt.texel_fetch(_u_xyzTex, stateCoord, rt.i(0))
        pVel = rt.texel_fetch(_u_velTex, stateCoord, rt.i(0))
        pCol = rt.texel_fetch(_u_rgbaTex, stateCoord, rt.i(0))
        needsRespawn = (bool((bool(_u_resetState) or bool(rt.binary("<", rt.swizzle(pPos, "w"), rt.f(0.5))))) or bool((bool(rt.binary("<", _u_time, rt.f(0.01))) and bool(rt.binary("==", rt.swizzle(pPos, "w"), rt.f(0.0))))))
        timeBits = 0
        check_seed = 0
        respawnRand = rt.f(0.0)
        attritionRate = rt.f(0.0)
        if (bool((not (needsRespawn))) and bool(rt.binary(">", _u_attrition, rt.f(0.0)))):
            timeBits = rt.float_bits_to_uint(_u_time)
            check_seed = rt.binary("+", rt.binary("*", agentSeed, rt.i(1664525), 1, "uint"), timeBits, 1, "uint")
            check_seed = rt.hash_uint(check_seed)
            respawnRand = rt.binary("/", rt.construct(1, check_seed), rt.f(4294967295.0), 1, "float")
            attritionRate = rt.binary("*", _u_attrition, rt.f(0.01), 1, "float")
            if rt.binary("<", respawnRand, attritionRate):
                needsRespawn = True
        rnd = hash2__uint(agentSeed)
        newPos = rt.construct(3, rt.f(0.0))
        angle = rt.f(0.0)
        radius = rt.f(0.0)
        clusterSeed = 0
        clusterId = rt.f(0.0)
        centerSeed = 0
        center = rt.construct(2, 0.0)
        r = rt.f(0.0)
        a = rt.f(0.0)
        t = rt.f(0.0)
        if rt.binary("==", _u_layoutMode, rt.i(0)):
            newPos[:] = rt.construct(3, rnd, rt.f(0.0))
        else:
            if rt.binary("==", _u_layoutMode, rt.i(1)):
                newPos[:] = rt.construct(3, uv, rt.f(0.0))
            else:
                if rt.binary("==", _u_layoutMode, rt.i(2)):
                    newPos[:] = rt.construct(3, rt.binary("+", rt.f(0.5), rt.binary("*", rt.binary("-", rnd, rt.f(0.5), 2, "float"), rt.f(0.1), 2, "float"), 2, "float"), rt.f(0.0))
                else:
                    if rt.binary("==", _u_layoutMode, rt.i(3)):
                        angle = rt.binary("*", rt.swizzle(rnd, "x"), rt.f(6.28318), 1, "float")
                        radius = rt.binary("+", rt.f(0.3), rt.binary("*", rt.swizzle(rnd, "y"), rt.f(0.1), 1, "float"), 1, "float")
                        newPos[:] = rt.construct(3, rt.binary("+", rt.f(0.5), rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), radius, 2, "float"), 2, "float"), rt.f(0.0))
                    else:
                        if rt.binary("==", _u_layoutMode, rt.i(4)):
                            clusterSeed = rt.binary("*", rt.construct(1, _u_seed, base="uint"), rt.i(12345), 1, "uint")
                            clusterId = rt.component_wise("floor", rt.binary("*", rt.swizzle(rnd, "x"), rt.f(5.0), 1, "float"), width=1)
                            centerSeed = rt.binary("+", clusterSeed, rt.binary("*", rt.construct(1, clusterId, base="uint"), rt.i(31), 1, "uint"), 1, "uint")
                            center = rt.construct(2, hash__uint(centerSeed), hash__uint(rt.binary("+", centerSeed, rt.i(17), 1, "uint")))
                            r = rt.binary("*", hash__uint(rt.binary("+", agentSeed, rt.i(2), 1, "uint")), rt.f(0.15), 1, "float")
                            a = rt.binary("*", hash__uint(rt.binary("+", agentSeed, rt.i(3), 1, "uint")), rt.f(6.28318), 1, "float")
                            newPos[:] = rt.construct(3, rt.binary("+", center, rt.binary("*", rt.construct(2, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1)), r, 2, "float"), 2, "float"), rt.f(0.0))
                            newPos = rt.assign_swizzle(newPos, "xy", rt.component_wise("fract", rt.swizzle(newPos, "xy"), width=2))
                        else:
                            if rt.binary("==", _u_layoutMode, rt.i(5)):
                                t = rt.binary("*", rt.swizzle(rnd, "x"), rt.f(20.0), 1, "float")
                                r = rt.binary("*", t, rt.f(0.02), 1, "float")
                                a = rt.binary("*", t, rt.f(6.28318), 1, "float")
                                newPos[:] = rt.construct(3, rt.binary("+", rt.f(0.5), rt.binary("*", rt.construct(2, rt.component_wise("cos", a, width=1), rt.component_wise("sin", a, width=1)), r, 2, "float"), 2, "float"), rt.f(0.0))
                                newPos = rt.assign_swizzle(newPos, "xy", rt.component_wise("clamp", rt.swizzle(newPos, "xy"), rt.f(0.0), rt.f(1.0), width=2))
        texDims = rt.texture_size(_u_inputTex)
        texCoord = rt.construct(2, rt.binary("*", rt.swizzle(newPos, "xy"), rt.construct(2, texDims), 2, "float"), base="int")
        sampledCol = rt.texel_fetch(_u_inputTex, texCoord, rt.i(0))
        newCol = (sampledCol if rt.binary(">", rt.swizzle(sampledCol, "a"), rt.f(0.0)) else rt.construct(4, rt.f(1.0)))
        rotRand = rt.f(0.0)
        strideRand = rt.f(0.0)
        if needsRespawn:
            rotRand = hash__uint(rt.binary("+", agentSeed, rt.i(100), 1, "uint"))
            strideRand = rt.binary("-", hash__uint(rt.binary("+", agentSeed, rt.i(101), 1, "uint")), rt.f(0.5), 1, "float")
            g.outXYZ[:] = rt.construct(4, newPos, rt.f(1.0))
            g.outVel[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rotRand, strideRand)
            g.outRGBA[:] = newCol
        else:
            g.outXYZ[:] = pPos
            g.outVel[:] = pVel
            g.outRGBA[:] = pCol
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
