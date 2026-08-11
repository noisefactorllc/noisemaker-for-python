def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_BEHAVIOR = U.get("BEHAVIOR", 0)
    _u_stateTex1 = T["stateTex1"]
    _u_stateTex2 = T["stateTex2"]
    _u_stateTex3 = T["stateTex3"]
    _u_mixerTex = T["mixerTex"]
    _u_stride = U.get("stride", rt.f(0.0))
    _u_strideDeviation = U.get("strideDeviation", rt.f(0.0))
    _u_kink = U.get("kink", rt.f(0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_lifetime = U.get("lifetime", rt.f(0.0))
    _u_density = U.get("density", rt.f(0.0))
    _u_volumeSize = U.get("volumeSize", 0)
    g.outState1 = rt.construct(4, 0.0)
    g.outState2 = rt.construct(4, 0.0)
    g.outState3 = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    g.PI = rt.f(3.141592653589793)
    g.RIGHT_ANGLE = rt.f(1.5707963267948966)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def hash3__uint(seed):
        return rt.construct(3, hash__uint(seed), hash__uint(rt.binary("+", seed, rt.i(1), 1, "uint")), hash__uint(rt.binary("+", seed, rt.i(2), 1, "uint")))
    def wrap_float__float_float(value, size):
        if rt.binary("<=", size, rt.f(0.0)):
            return rt.f(0.0)
        scaled = rt.component_wise("floor", rt.binary("/", value, size, 1, "float"), width=1)
        wrapped = rt.binary("-", value, rt.binary("*", scaled, size, 1, "float"), 1, "float")
        if rt.binary("<", wrapped, rt.f(0.0)):
            wrapped = rt.binary("+", wrapped, size, 1, "float")
        return wrapped
    def wrap_int__int_int(value, size):
        if rt.binary("<=", size, rt.i(0)):
            return rt.i(0)
        result = rt.binary("%", value, size, 1, "int")
        if rt.binary("<", result, rt.i(0)):
            result = rt.binary("+", result, size, 1, "int")
        return result
    def atlasTexel__ivec3_int(p, volSize):
        p = rt.copy(p, "int")
        clamped = rt.component_wise("clamp", p, rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", volSize, rt.i(1), 1, "int"), base="int"), width=3)
        return rt.construct(2, rt.swizzle(clamped, "x"), rt.binary("+", rt.swizzle(clamped, "y"), rt.binary("*", rt.swizzle(clamped, "z"), volSize, 1, "int"), 1, "int"), base="int")
    def sampleVoxel__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        clamped = rt.component_wise("clamp", voxel, rt.construct(3, rt.i(0), base="int"), rt.construct(3, rt.binary("-", volSize, rt.i(1), 1, "int"), base="int"), width=3)
        return rt.texel_fetch(_u_mixerTex, atlasTexel__ivec3_int(clamped, volSize), rt.i(0))
    def srgb_to_linear__float(value):
        if rt.binary("<=", value, rt.f(0.04045)):
            return rt.binary("/", value, rt.f(12.92), 1, "float")
        return rt.component_wise("pow", rt.binary("/", rt.binary("+", value, rt.f(0.055), 1, "float"), rt.f(1.055), 1, "float"), rt.f(2.4), width=1)
    def cube_root__float(value):
        if rt.binary("==", value, rt.f(0.0)):
            return rt.f(0.0)
        sign_value = (rt.f(1.0) if rt.binary(">=", value, rt.f(0.0)) else rt.unary("-", rt.f(1.0)))
        return rt.binary("*", sign_value, rt.component_wise("pow", rt.component_wise("abs", value, width=1), rt.binary("/", rt.f(1.0), rt.f(3.0), 1, "float"), width=1), 1, "float")
    def oklab_l__vec3(rgb):
        rgb = rt.copy(rgb, "float")
        r_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "x"), rt.f(0.0), rt.f(1.0), width=1))
        g_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "y"), rt.f(0.0), rt.f(1.0), width=1))
        b_lin = srgb_to_linear__float(rt.component_wise("clamp", rt.swizzle(rgb, "z"), rt.f(0.0), rt.f(1.0), width=1))
        l = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.412165612), r_lin, 1, "float"), rt.binary("*", rt.f(0.536275208), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0514575653), b_lin, 1, "float"), 1, "float")
        m = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.211859107), r_lin, 1, "float"), rt.binary("*", rt.f(0.6807189584), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.107406579), b_lin, 1, "float"), 1, "float")
        s = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.0883097947), r_lin, 1, "float"), rt.binary("*", rt.f(0.2818474174), g_lin, 1, "float"), 1, "float"), rt.binary("*", rt.f(0.6302613616), b_lin, 1, "float"), 1, "float")
        return rt.binary("-", rt.binary("+", rt.binary("*", rt.f(0.2104542553), cube_root__float(l), 1, "float"), rt.binary("*", rt.f(0.793617785), cube_root__float(m), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.0040720468), cube_root__float(s), 1, "float"), 1, "float")
    def normalized_sine__float(value):
        return rt.binary("*", rt.binary("+", rt.component_wise("sin", value, width=1), rt.f(1.0), 1, "float"), rt.f(0.5), 1, "float")
    def computeRotationBias__float_float_float_int_int(baseHeading, baseRotRand, time, agentIndex, totalAgents):
        quarterSize = 0
        band = 0
        if rt.binary("<=", _u_BEHAVIOR, rt.i(0)):
            return rt.f(0.0)
        else:
            if rt.binary("==", _u_BEHAVIOR, rt.i(1)):
                return baseHeading
            else:
                if rt.binary("==", _u_BEHAVIOR, rt.i(2)):
                    return rt.binary("+", baseHeading, rt.binary("*", rt.component_wise("floor", rt.binary("*", baseRotRand, rt.f(4.0), 1, "float"), width=1), g.RIGHT_ANGLE, 1, "float"), 1, "float")
                else:
                    if rt.binary("==", _u_BEHAVIOR, rt.i(3)):
                        return rt.binary("+", baseHeading, rt.binary("*", rt.binary("-", baseRotRand, rt.f(0.5), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
                    else:
                        if rt.binary("==", _u_BEHAVIOR, rt.i(4)):
                            return rt.binary("*", baseRotRand, g.TAU, 1, "float")
                        else:
                            if rt.binary("==", _u_BEHAVIOR, rt.i(5)):
                                quarterSize = rt.component_wise("max", rt.i(1), rt.binary("/", totalAgents, rt.i(4), 1, "int"), width=1)
                                band = rt.binary("/", agentIndex, quarterSize, 1, "int")
                                if rt.binary("<=", band, rt.i(0)):
                                    return baseHeading
                                else:
                                    if rt.binary("==", band, rt.i(1)):
                                        return rt.binary("+", baseHeading, rt.binary("*", rt.component_wise("floor", rt.binary("*", baseRotRand, rt.f(4.0), 1, "float"), width=1), g.RIGHT_ANGLE, 1, "float"), 1, "float")
                                    else:
                                        if rt.binary("==", band, rt.i(2)):
                                            return rt.binary("+", baseHeading, rt.binary("*", rt.binary("-", baseRotRand, rt.f(0.5), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
                                        else:
                                            return rt.binary("*", baseRotRand, g.TAU, 1, "float")
                            else:
                                if rt.binary("==", _u_BEHAVIOR, rt.i(10)):
                                    return normalized_sine__float(rt.binary("*", rt.binary("-", time, baseRotRand, 1, "float"), g.TAU, 1, "float"))
                                else:
                                    return rt.binary("*", baseRotRand, g.TAU, 1, "float")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateTexSize = rt.texture_size(_u_stateTex1)
        width = rt.swizzle(stateTexSize, "x")
        height = rt.swizzle(stateTexSize, "y")
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        state1 = rt.texel_fetch(_u_stateTex1, coord, rt.i(0))
        state2 = rt.texel_fetch(_u_stateTex2, coord, rt.i(0))
        state3 = rt.texel_fetch(_u_stateTex3, coord, rt.i(0))
        flow_x = rt.swizzle(state1, "x")
        flow_y = rt.swizzle(state1, "y")
        flow_z = rt.swizzle(state1, "z")
        rotRand = rt.swizzle(state1, "w")
        cr = rt.swizzle(state2, "x")
        cg = rt.swizzle(state2, "y")
        cb = rt.swizzle(state2, "z")
        seed_f = rt.swizzle(state2, "w")
        age = rt.swizzle(state3, "x")
        initialized = rt.swizzle(state3, "y")
        strideRand = rt.swizzle(state3, "z")
        agentSeed = rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), width, 1, "int"), 1, "int"), base="uint")
        baseSeed = rt.binary("+", agentSeed, rt.construct(1, rt.binary("*", _u_time, rt.f(1000.0), 1, "float"), base="uint"), 1, "uint")
        totalAgents = rt.binary("*", width, height, 1, "int")
        agentIndex = rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), width, 1, "int"), 1, "int")
        pos = rt.construct(3, 0.0)
        xi = 0
        yi = 0
        zi = 0
        inputColor = rt.construct(4, 0.0)
        if rt.binary("<", initialized, rt.f(0.5)):
            pos = hash3__uint(agentSeed)
            flow_x = rt.binary("*", rt.swizzle(pos, "x"), volSizeF, 1, "float")
            flow_y = rt.binary("*", rt.swizzle(pos, "y"), volSizeF, 1, "float")
            flow_z = rt.binary("*", rt.swizzle(pos, "z"), volSizeF, 1, "float")
            rotRand = hash__uint(rt.binary("+", agentSeed, rt.i(200), 1, "uint"))
            strideRand = rt.binary("-", hash__uint(rt.binary("+", agentSeed, rt.i(300), 1, "uint")), rt.f(0.5), 1, "float")
            xi = wrap_int__int_int(rt.construct(1, flow_x, base="int"), volSize)
            yi = wrap_int__int_int(rt.construct(1, flow_y, base="int"), volSize)
            zi = wrap_int__int_int(rt.construct(1, flow_z, base="int"), volSize)
            inputColor = sampleVoxel__ivec3_int(rt.construct(3, xi, yi, zi, base="int"), volSize)
            cr = rt.swizzle(inputColor, "r")
            cg = rt.swizzle(inputColor, "g")
            cb = rt.swizzle(inputColor, "b")
            seed_f = rt.construct(1, agentSeed)
            age = rt.f(0.0)
            initialized = rt.f(1.0)
        agentPhase = rt.binary("/", rt.construct(1, agentIndex), rt.construct(1, rt.component_wise("max", totalAgents, rt.i(1), width=1)), 1, "float")
        staggeredAge = rt.binary("+", age, rt.binary("*", agentPhase, _u_lifetime, 1, "float"), 1, "float")
        shouldRespawn = (bool(rt.binary(">", _u_lifetime, rt.f(0.0))) and bool(rt.binary(">=", staggeredAge, _u_lifetime)))
        if shouldRespawn:
            pos = hash3__uint(baseSeed)
            flow_x = rt.binary("*", rt.swizzle(pos, "x"), volSizeF, 1, "float")
            flow_y = rt.binary("*", rt.swizzle(pos, "y"), volSizeF, 1, "float")
            flow_z = rt.binary("*", rt.swizzle(pos, "z"), volSizeF, 1, "float")
            rotRand = hash__uint(rt.binary("+", baseSeed, rt.i(200), 1, "uint"))
            xi = wrap_int__int_int(rt.construct(1, flow_x, base="int"), volSize)
            yi = wrap_int__int_int(rt.construct(1, flow_y, base="int"), volSize)
            zi = wrap_int__int_int(rt.construct(1, flow_z, base="int"), volSize)
            inputColor = sampleVoxel__ivec3_int(rt.construct(3, xi, yi, zi, base="int"), volSize)
            cr = rt.swizzle(inputColor, "r")
            cg = rt.swizzle(inputColor, "g")
            cb = rt.swizzle(inputColor, "b")
            age = rt.f(0.0)
        xi = wrap_int__int_int(rt.construct(1, flow_x, base="int"), volSize)
        yi = wrap_int__int_int(rt.construct(1, flow_y, base="int"), volSize)
        zi = wrap_int__int_int(rt.construct(1, flow_z, base="int"), volSize)
        texel = sampleVoxel__ivec3_int(rt.construct(3, xi, yi, zi, base="int"), volSize)
        indexValue = oklab_l__vec3(rt.swizzle(texel, "rgb"))
        baseHeading = rt.binary("*", hash__uint(rt.i(0)), g.TAU, 1, "float")
        rotationBias = computeRotationBias__float_float_float_int_int(baseHeading, rotRand, _u_time, agentIndex, totalAgents)
        azimuth = rt.binary("+", rt.binary("*", rt.binary("*", indexValue, g.TAU, 1, "float"), _u_kink, 1, "float"), rotationBias, 1, "float")
        elevation = rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", indexValue, rt.f(0.5), 1, "float"), g.PI, 1, "float"), _u_kink, 1, "float"), rt.f(0.5), 1, "float")
        scale = rt.component_wise("max", rt.binary("/", volSizeF, rt.f(64.0), 1, "float"), rt.f(1.0), width=1)
        devFactor = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", strideRand, rt.f(2.0), 1, "float"), _u_strideDeviation, 1, "float"), 1, "float")
        actualStride = rt.component_wise("max", rt.f(0.1), rt.binary("*", rt.binary("*", _u_stride, scale, 1, "float"), devFactor, 1, "float"), width=1)
        cosElev = rt.component_wise("cos", elevation, width=1)
        newX = rt.binary("+", flow_x, rt.binary("*", rt.binary("*", rt.component_wise("sin", azimuth, width=1), cosElev, 1, "float"), actualStride, 1, "float"), 1, "float")
        newY = rt.binary("+", flow_y, rt.binary("*", rt.binary("*", rt.component_wise("cos", azimuth, width=1), cosElev, 1, "float"), actualStride, 1, "float"), 1, "float")
        newZ = rt.binary("+", flow_z, rt.binary("*", rt.component_wise("sin", elevation, width=1), actualStride, 1, "float"), 1, "float")
        newX = wrap_float__float_float(newX, volSizeF)
        newY = wrap_float__float_float(newY, volSizeF)
        newZ = wrap_float__float_float(newZ, volSizeF)
        age = rt.binary("+", age, rt.f(0.016), 1, "float")
        g.outState1[:] = rt.construct(4, newX, newY, newZ, rotRand)
        g.outState2[:] = rt.construct(4, cr, cg, cb, seed_f)
        g.outState3[:] = rt.construct(4, age, initialized, strideRand, rt.f(0.0))
    main__void()
    _c = g.outState1
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outState2
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outState3
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outState1', 'outState2', 'outState3')
