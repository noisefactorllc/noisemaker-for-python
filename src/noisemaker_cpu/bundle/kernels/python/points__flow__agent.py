def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_stride = U.get("stride", rt.f(0.0))
    _u_strideDeviation = U.get("strideDeviation", rt.f(0.0))
    _u_kink = U.get("kink", rt.f(0.0))
    _u_quantize = U.get("quantize", rt.f(0.0))
    _u_inputWeight = U.get("inputWeight", rt.f(0.0))
    _u_behavior = U.get("behavior", rt.f(0.0))
    _u_inputTex = T["inputTex"]
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    g.TAU = rt.f(6.283185307179586)
    g.RIGHT_ANGLE = rt.f(1.5707963267948966)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
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
    def computeRotationBias__int_float_float_float_int_int(behaviorMode, baseHeading, rotRand, time, agentIndex, totalAgents):
        quarterSize = 0
        band = 0
        if rt.binary("<=", behaviorMode, rt.i(0)):
            return rt.f(0.0)
        else:
            if rt.binary("==", behaviorMode, rt.i(1)):
                return baseHeading
            else:
                if rt.binary("==", behaviorMode, rt.i(2)):
                    return rt.binary("+", baseHeading, rt.binary("*", rt.component_wise("floor", rt.binary("*", rotRand, rt.f(4.0), 1, "float"), width=1), g.RIGHT_ANGLE, 1, "float"), 1, "float")
                else:
                    if rt.binary("==", behaviorMode, rt.i(3)):
                        return rt.binary("+", baseHeading, rt.binary("*", rt.binary("-", rotRand, rt.f(0.5), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
                    else:
                        if rt.binary("==", behaviorMode, rt.i(4)):
                            return rt.binary("*", rotRand, g.TAU, 1, "float")
                        else:
                            if rt.binary("==", behaviorMode, rt.i(5)):
                                quarterSize = rt.component_wise("max", rt.i(1), rt.binary("/", totalAgents, rt.i(4), 1, "int"), width=1)
                                band = rt.binary("/", agentIndex, quarterSize, 1, "int")
                                if rt.binary("<=", band, rt.i(0)):
                                    return baseHeading
                                else:
                                    if rt.binary("==", band, rt.i(1)):
                                        return rt.binary("+", baseHeading, rt.binary("*", rt.component_wise("floor", rt.binary("*", rotRand, rt.f(4.0), 1, "float"), width=1), g.RIGHT_ANGLE, 1, "float"), 1, "float")
                                    else:
                                        if rt.binary("==", band, rt.i(2)):
                                            return rt.binary("+", baseHeading, rt.binary("*", rt.binary("-", rotRand, rt.f(0.5), 1, "float"), rt.f(0.25), 1, "float"), 1, "float")
                                        else:
                                            return rt.binary("*", rotRand, g.TAU, 1, "float")
                            else:
                                if rt.binary("==", behaviorMode, rt.i(10)):
                                    return normalized_sine__float(rt.binary("*", rt.binary("-", time, rotRand, 1, "float"), g.TAU, 1, "float"))
                                else:
                                    return rt.binary("*", rotRand, g.TAU, 1, "float")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateSize = rt.texture_size(_u_xyzTex)
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        px = rt.swizzle(xyz, "x")
        py = rt.swizzle(xyz, "y")
        pz = rt.swizzle(xyz, "z")
        alive = rt.swizzle(xyz, "w")
        rotRand = rt.swizzle(vel, "z")
        strideRand = rt.swizzle(vel, "w")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        texSize = rt.texture_size(_u_inputTex)
        texCoord = rt.construct(2, rt.binary("*", px, rt.construct(1, rt.swizzle(texSize, "x")), 1, "float"), rt.binary("*", py, rt.construct(1, rt.swizzle(texSize, "y")), 1, "float"), base="int")
        texCoord[:] = rt.component_wise("clamp", texCoord, rt.construct(2, rt.i(0), base="int"), rt.binary("-", texSize, rt.i(1), 2, "int"), width=2)
        texel = rt.texel_fetch(_u_inputTex, texCoord, rt.i(0))
        inputLuma = oklab_l__vec3(rt.swizzle(texel, "rgb"))
        weightBlend = rt.component_wise("clamp", rt.binary("*", _u_inputWeight, rt.f(0.01), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        indexValue = rt.component_wise("mix", rt.f(0.5), inputLuma, weightBlend, width=1)
        baseHeading = rt.binary("*", hash__uint(rt.i(0)), g.TAU, 1, "float")
        behaviorMode = rt.construct(1, _u_behavior, base="int")
        totalAgents = rt.binary("*", rt.swizzle(stateSize, "x"), rt.swizzle(stateSize, "y"), 1, "int")
        agentIndex = rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(stateSize, "x"), 1, "int"), 1, "int")
        rotationBias = computeRotationBias__int_float_float_float_int_int(behaviorMode, baseHeading, rotRand, _u_time, agentIndex, totalAgents)
        finalAngle = rt.binary("+", rt.binary("*", rt.binary("*", indexValue, g.TAU, 1, "float"), _u_kink, 1, "float"), rotationBias, 1, "float")
        if rt.binary(">", _u_quantize, rt.f(0.5)):
            finalAngle = rt.component_wise("round", finalAngle, width=1)
        scale = rt.component_wise("max", rt.binary("/", rt.component_wise("max", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), width=1), rt.f(1024.0), 1, "float"), rt.f(1.0), width=1)
        devFactor = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", strideRand, rt.f(2.0), 1, "float"), _u_strideDeviation, 1, "float"), 1, "float")
        actualStride = rt.component_wise("max", rt.f(0.0001), rt.binary("/", rt.binary("*", rt.binary("*", rt.binary("*", _u_stride, rt.f(0.1), 1, "float"), scale, 1, "float"), devFactor, 1, "float"), rt.component_wise("max", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), width=1), 1, "float"), width=1)
        newX = rt.binary("+", px, rt.binary("*", rt.component_wise("sin", finalAngle, width=1), actualStride, 1, "float"), 1, "float")
        newY = rt.binary("+", py, rt.binary("*", rt.component_wise("cos", finalAngle, width=1), actualStride, 1, "float"), 1, "float")
        newX = rt.component_wise("fract", newX, width=1)
        newY = rt.component_wise("fract", newY, width=1)
        g.outXYZ[:] = rt.construct(4, newX, newY, pz, rt.f(1.0))
        g.outVel[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rotRand, strideRand)
        g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
