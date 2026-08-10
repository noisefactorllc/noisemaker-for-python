def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_frame = U.get("frame", 0)
    _u_stride = U.get("stride", rt.f(0.0))
    _u_inputWeight = U.get("inputWeight", rt.f(0.0))
    _u_attrition = U.get("attrition", rt.f(0.0))
    _u_stateSize = U.get("stateSize", 0)
    _u_resetState = U.get("resetState", False)
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    _u_gridTex = T["gridTex"]
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
    def rand__float(seed):
        bits = rt.float_bits_to_uint(seed)
        bits = rt.hash_uint(bits)
        seed = rt.binary("-", rt.uint_bits_to_float(rt.binary("|", bits, rt.i(1065353216), 1, "uint")), rt.f(1.0), 1, "float")
        bits = rt.hash_uint(rt.binary("+", bits, rt.i(1), 1, "uint"))
        seed = rt.binary("-", rt.uint_bits_to_float(rt.binary("|", rt.binary("&", bits, rt.i(8388607), 1, "uint"), rt.i(1065353216), 1, "uint")), rt.f(1.0), 1, "float")
        return (seed, seed)
        return (None, seed)
    def randomDirection__float(seed):
        theta = rt.binary("*", (((_retc0 := rand__float(seed)), (seed := _retc0[1]), _retc0[0])[-1]), rt.f(6.28318530718), 1, "float")
        return (rt.construct(2, rt.component_wise("cos", theta, width=1), rt.component_wise("sin", theta, width=1)), seed)
        return (None, seed)
    def wrap01__vec2(v):
        v = rt.copy(v, "float")
        return rt.component_wise("fract", rt.component_wise("max", v, rt.f(0.0), width=2), width=2)
    def sampleGrid__vec2(uv):
        uv = rt.copy(uv, "float")
        dims = rt.texture_size(_u_gridTex)
        coord = rt.construct(2, rt.binary("*", wrap01__vec2(uv), rt.construct(2, dims), 2, "float"), base="int")
        return rt.swizzle(rt.texel_fetch(_u_gridTex, coord, rt.i(0)), "a")
    def neighborhood__vec2_float(uv, radius):
        uv = rt.copy(uv, "float")
        gridDims = rt.construct(2, rt.texture_size(_u_gridTex))
        texel = rt.binary("/", radius, gridDims, 2, "float")
        accum = rt.f(0.0)
        accum = rt.binary("+", accum, sampleGrid__vec2(uv), 1, "float")
        accum = rt.binary("+", accum, sampleGrid__vec2(rt.binary("+", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), 1, "float")
        accum = rt.binary("+", accum, sampleGrid__vec2(rt.binary("-", uv, rt.construct(2, rt.swizzle(texel, "x"), rt.f(0.0)), 2, "float")), 1, "float")
        accum = rt.binary("+", accum, sampleGrid__vec2(rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), 1, "float")
        accum = rt.binary("+", accum, sampleGrid__vec2(rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texel, "y")), 2, "float")), 1, "float")
        return rt.binary("*", accum, rt.f(0.2), 1, "float")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateDims = rt.texture_size(_u_xyzTex)
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        pos = rt.swizzle(xyz, "xy")
        alive = rt.swizzle(xyz, "w")
        seed = rt.swizzle(vel, "x")
        agentRand = rt.swizzle(vel, "w")
        agentId = rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(stateDims, "x"), 1, "int"), 1, "int"), base="uint")
        if rt.binary("<=", seed, rt.f(0.0)):
            seed = rt.binary("+", hash__uint(agentId), rt.f(0.001), 1, "float")
        frameSeed = rt.hash_uint(rt.binary("+", rt.binary("*", agentId, rt.i(31), 1, "uint"), rt.float_bits_to_uint(seed), 1, "uint"))
        seed = rt.binary("-", rt.uint_bits_to_float(rt.binary("|", rt.binary("&", frameSeed, rt.i(8388607), 1, "uint"), rt.i(1065353216), 1, "uint")), rt.f(1.0), 1, "float")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = rt.construct(4, seed, rt.f(0.0), rt.f(0.0), agentRand)
            g.outRGBA[:] = rgba
            return
        gridDims = rt.construct(2, rt.texture_size(_u_gridTex))
        texel = rt.binary("/", rt.f(1.0), rt.component_wise("max", rt.swizzle(gridDims, "x"), rt.swizzle(gridDims, "y"), width=1), 1, "float")
        local = neighborhood__vec2_float(pos, rt.f(2.0))
        proximity = rt.component_wise("smoothstep", rt.f(0.015), rt.f(0.12), local, width=1)
        randomDir = (((_retc1 := randomDirection__float(seed)), (seed := _retc1[1]), _retc1[0])[-1])
        inputW = rt.binary("/", _u_inputWeight, rt.f(100.0), 1, "float")
        stepDir = randomDir
        inputDims = rt.construct(2, 0.0, base="int")
        inputCoord = rt.construct(2, 0.0, base="int")
        inputVal = rt.construct(4, 0.0)
        inputDir = rt.construct(2, 0.0)
        if rt.binary(">", inputW, rt.f(0.0)):
            inputDims = rt.texture_size(_u_inputTex)
            inputCoord = rt.construct(2, rt.binary("*", wrap01__vec2(pos), rt.construct(2, inputDims), 2, "float"), base="int")
            inputVal = rt.texel_fetch(_u_inputTex, inputCoord, rt.i(0))
            inputDir = rt.binary("-", rt.binary("*", rt.swizzle(inputVal, "xy"), rt.f(2.0), 2, "float"), rt.f(1.0), 2, "float")
            if rt.binary(">", rt.length(inputDir), rt.f(0.01)):
                inputDir[:] = rt.normalize(inputDir)
                stepDir[:] = rt.normalize(rt.component_wise("mix", randomDir, inputDir, inputW, width=2))
        stepSize = rt.binary("*", rt.binary("*", rt.binary("/", _u_stride, rt.f(10.0), 1, "float"), texel, 1, "float"), rt.component_wise("mix", rt.f(3.0), rt.f(0.5), proximity, width=1), 1, "float")
        stepDir[:] = rt.binary("+", stepDir, rt.binary("*", (((_retc2 := randomDirection__float(seed)), (seed := _retc2[1]), _retc2[0])[-1]), rt.f(0.3), 2, "float"), 2, "float")
        stepDir[:] = rt.normalize(stepDir)
        candidate = wrap01__vec2(rt.binary("+", pos, rt.binary("*", stepDir, stepSize, 2, "float"), 2, "float"))
        here = sampleGrid__vec2(candidate)
        nearby = neighborhood__vec2_float(candidate, rt.f(1.0))
        stuck = (bool(rt.binary(">", nearby, rt.f(0.3))) and bool(rt.binary("<", here, rt.f(0.5))))
        needsRespawn = False
        attritionRate = rt.f(0.0)
        if rt.binary(">", _u_attrition, rt.f(0.0)):
            attritionRate = rt.binary("*", _u_attrition, rt.f(0.01), 1, "float")
            if rt.binary("<", (((_retc3 := rand__float(seed)), (seed := _retc3[1]), _retc3[0])[-1]), attritionRate):
                needsRespawn = True
        if stuck:
            g.outXYZ[:] = rt.construct(4, candidate, rt.f(0.0), rt.f(0.0))
            g.outVel[:] = rt.construct(4, seed, rt.f(1.0), rt.f(0.0), agentRand)
            g.outRGBA[:] = rgba
        else:
            if needsRespawn:
                g.outXYZ[:] = rt.construct(4, candidate, rt.f(0.0), rt.f(0.0))
                g.outVel[:] = rt.construct(4, seed, rt.f(0.0), rt.f(0.0), agentRand)
                g.outRGBA[:] = rgba
            else:
                g.outXYZ[:] = rt.construct(4, candidate, rt.f(0.0), rt.f(1.0))
                g.outVel[:] = rt.construct(4, seed, rt.f(0.0), rt.f(0.0), agentRand)
                g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
