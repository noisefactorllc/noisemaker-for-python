def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    _u_trailTex = T["trailTex"]
    _u_inputTex = T["inputTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_moveSpeed = U.get("moveSpeed", rt.f(0.0))
    _u_turnSpeed = U.get("turnSpeed", rt.f(0.0))
    _u_sensorAngle = U.get("sensorAngle", rt.f(0.0))
    _u_sensorDistance = U.get("sensorDistance", rt.f(0.0))
    _u_inputWeight = U.get("inputWeight", rt.f(0.0))
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    g.TAU = rt.f(6.28318530718)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def hash_f__float(n):
        return rt.binary("/", rt.construct(1, rt.hash_uint(rt.float_bits_to_uint(n))), rt.f(4294967295.0), 1, "float")
    def wrapPosition__vec2(pos):
        pos = rt.copy(pos, "float")
        return rt.component_wise("fract", rt.binary("+", pos, rt.f(1.0), 2, "float"), width=2)
    def luminance__vec3(color):
        color = rt.copy(color, "float")
        return rt.dot(color, rt.construct(3, rt.f(0.2126), rt.f(0.7152), rt.f(0.0722)))
    def sampleTrail__vec2(uv):
        uv = rt.copy(uv, "float")
        return luminance__vec3(rt.swizzle(rt.texture(_u_trailTex, uv), "rgb"))
    def sampleExternalField__vec2_float(uv, weight):
        uv = rt.copy(uv, "float")
        if rt.binary("<=", weight, rt.f(0.0)):
            return rt.f(0.0)
        blend = rt.component_wise("clamp", rt.binary("*", weight, rt.f(0.01), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        return rt.binary("*", rt.binary("*", luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, uv), "rgb")), blend, 1, "float"), rt.f(0.05), 1, "float")
    def main__void():
        stateSize = rt.texture_size(_u_xyzTex)
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        pos = rt.swizzle(xyz, "xy")
        heading = rt.swizzle(xyz, "z")
        alive = rt.swizzle(xyz, "w")
        age = rt.swizzle(vel, "z")
        seed = rt.swizzle(vel, "w")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = rt.construct(4, pos, rt.binary("*", hash__uint(rt.construct(1, rt.binary("*", seed, rt.f(1000.0), 1, "float"), base="uint")), g.TAU, 1, "float"), rt.f(0.0))
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        forwardDir = rt.construct(2, rt.component_wise("cos", heading, width=1), rt.component_wise("sin", heading, width=1))
        leftDir = rt.construct(2, rt.component_wise("cos", rt.binary("-", heading, _u_sensorAngle, 1, "float"), width=1), rt.component_wise("sin", rt.binary("-", heading, _u_sensorAngle, 1, "float"), width=1))
        rightDir = rt.construct(2, rt.component_wise("cos", rt.binary("+", heading, _u_sensorAngle, 1, "float"), width=1), rt.component_wise("sin", rt.binary("+", heading, _u_sensorAngle, 1, "float"), width=1))
        sensorPosF = wrapPosition__vec2(rt.binary("+", pos, rt.binary("*", forwardDir, _u_sensorDistance, 2, "float"), 2, "float"))
        sensorPosL = wrapPosition__vec2(rt.binary("+", pos, rt.binary("*", leftDir, _u_sensorDistance, 2, "float"), 2, "float"))
        sensorPosR = wrapPosition__vec2(rt.binary("+", pos, rt.binary("*", rightDir, _u_sensorDistance, 2, "float"), 2, "float"))
        valF = rt.binary("+", sampleTrail__vec2(sensorPosF), sampleExternalField__vec2_float(sensorPosF, _u_inputWeight), 1, "float")
        valL = rt.binary("+", sampleTrail__vec2(sensorPosL), sampleExternalField__vec2_float(sensorPosL, _u_inputWeight), 1, "float")
        valR = rt.binary("+", sampleTrail__vec2(sensorPosR), sampleExternalField__vec2_float(sensorPosR, _u_inputWeight), 1, "float")
        newHeading = heading
        if (bool(rt.binary(">", valF, valL)) and bool(rt.binary(">", valF, valR))):
            pass
        else:
            if (bool(rt.binary("<", valF, valL)) and bool(rt.binary("<", valF, valR))):
                newHeading = rt.binary("+", newHeading, rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", hash_f__float(rt.binary("+", _u_time, rt.swizzle(pos, "x"), 1, "float")), rt.f(0.5), 1, "float"), rt.f(2.0), 1, "float"), _u_turnSpeed, 1, "float"), _u_moveSpeed, 1, "float"), 1, "float")
            else:
                if rt.binary(">", valL, valR):
                    newHeading = rt.binary("-", newHeading, rt.binary("*", _u_turnSpeed, _u_moveSpeed, 1, "float"), 1, "float")
                else:
                    if rt.binary(">", valR, valL):
                        newHeading = rt.binary("+", newHeading, rt.binary("*", _u_turnSpeed, _u_moveSpeed, 1, "float"), 1, "float")
        moveDir = rt.construct(2, rt.component_wise("cos", newHeading, width=1), rt.component_wise("sin", newHeading, width=1))
        speedScale = rt.f(1.0)
        blend = rt.component_wise("clamp", rt.binary("*", _u_inputWeight, rt.f(0.01), 1, "float"), rt.f(0.0), rt.f(1.0), width=1)
        localInput = rt.f(0.0)
        if rt.binary(">", blend, rt.f(0.0)):
            localInput = luminance__vec3(rt.swizzle(rt.texture(_u_inputTex, pos), "rgb"))
            speedScale = rt.component_wise("mix", rt.f(1.0), rt.component_wise("mix", rt.f(1.8), rt.f(0.35), localInput, width=1), blend, width=1)
        normalizedSpeed = rt.binary("*", rt.binary("*", _u_moveSpeed, rt.f(0.001), 1, "float"), speedScale, 1, "float")
        newPos = wrapPosition__vec2(rt.binary("+", pos, rt.binary("*", moveDir, normalizedSpeed, 2, "float"), 2, "float"))
        newAge = rt.binary("+", age, rt.f(0.016), 1, "float")
        g.outXYZ[:] = rt.construct(4, newPos, newHeading, rt.f(1.0))
        g.outVel[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), newAge, seed)
        g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
