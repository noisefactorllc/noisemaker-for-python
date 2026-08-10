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
    _u_attractor = U.get("attractor", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def lorenz__vec3(p):
        p = rt.copy(p, "float")
        sigma = rt.f(10.0)
        rho = rt.f(28.0)
        beta = rt.binary("/", rt.f(8.0), rt.f(3.0), 1, "float")
        return rt.construct(3, rt.binary("*", sigma, rt.binary("-", rt.swizzle(p, "y"), rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), rt.binary("-", rho, rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.swizzle(p, "y"), 1, "float"), rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.binary("*", beta, rt.swizzle(p, "z"), 1, "float"), 1, "float"))
    def rossler__vec3(p):
        p = rt.copy(p, "float")
        a = rt.f(0.2)
        b = rt.f(0.2)
        c = rt.f(5.7)
        return rt.construct(3, rt.binary("-", rt.unary("-", rt.swizzle(p, "y")), rt.swizzle(p, "z"), 1, "float"), rt.binary("+", rt.swizzle(p, "x"), rt.binary("*", a, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("+", b, rt.binary("*", rt.swizzle(p, "z"), rt.binary("-", rt.swizzle(p, "x"), c, 1, "float"), 1, "float"), 1, "float"))
    def aizawa__vec3(p):
        p = rt.copy(p, "float")
        a = rt.f(0.95)
        b = rt.f(0.7)
        c = rt.f(0.6)
        d = rt.f(3.5)
        e = rt.f(0.25)
        f = rt.f(0.1)
        return rt.construct(3, rt.binary("-", rt.binary("*", rt.binary("-", rt.swizzle(p, "z"), b, 1, "float"), rt.swizzle(p, "x"), 1, "float"), rt.binary("*", d, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("*", d, rt.swizzle(p, "x"), 1, "float"), rt.binary("*", rt.binary("-", rt.swizzle(p, "z"), b, 1, "float"), rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("-", rt.binary("+", c, rt.binary("*", a, rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("/", rt.binary("*", rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(p, "z"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), rt.f(3.0), 1, "float"), 1, "float"), rt.binary("*", rt.binary("+", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("+", rt.f(1.0), rt.binary("*", e, rt.swizzle(p, "z"), 1, "float"), 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("*", f, rt.swizzle(p, "z"), 1, "float"), rt.swizzle(p, "x"), 1, "float"), rt.swizzle(p, "x"), 1, "float"), rt.swizzle(p, "x"), 1, "float"), 1, "float"))
    def thomas__vec3(p):
        p = rt.copy(p, "float")
        b = rt.f(0.208186)
        return rt.construct(3, rt.binary("-", rt.component_wise("sin", rt.swizzle(p, "y"), width=1), rt.binary("*", b, rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("-", rt.component_wise("sin", rt.swizzle(p, "z"), width=1), rt.binary("*", b, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("-", rt.component_wise("sin", rt.swizzle(p, "x"), width=1), rt.binary("*", b, rt.swizzle(p, "z"), 1, "float"), 1, "float"))
    def halvorsen__vec3(p):
        p = rt.copy(p, "float")
        a = rt.f(1.89)
        return rt.construct(3, rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("*", rt.unary("-", a), rt.swizzle(p, "x"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(p, "y"), rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("*", rt.unary("-", a), rt.swizzle(p, "y"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(p, "z"), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("-", rt.binary("-", rt.binary("-", rt.binary("*", rt.unary("-", a), rt.swizzle(p, "z"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("*", rt.f(4.0), rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "x"), 1, "float"), 1, "float"))
    def chen__vec3(p):
        p = rt.copy(p, "float")
        a = rt.f(40.0)
        b = rt.f(3.0)
        c = rt.f(28.0)
        return rt.construct(3, rt.binary("*", a, rt.binary("-", rt.swizzle(p, "y"), rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("*", rt.binary("-", c, a, 1, "float"), rt.swizzle(p, "x"), 1, "float"), rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("*", c, rt.swizzle(p, "y"), 1, "float"), 1, "float"), rt.binary("-", rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.binary("*", b, rt.swizzle(p, "z"), 1, "float"), 1, "float"))
    def dadras__vec3(p):
        p = rt.copy(p, "float")
        a = rt.f(3.0)
        b = rt.f(2.7)
        c = rt.f(1.7)
        d = rt.f(2.0)
        e = rt.f(9.0)
        return rt.construct(3, rt.binary("+", rt.binary("-", rt.swizzle(p, "y"), rt.binary("*", a, rt.swizzle(p, "x"), 1, "float"), 1, "float"), rt.binary("*", rt.binary("*", b, rt.swizzle(p, "y"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.binary("+", rt.binary("-", rt.binary("*", c, rt.swizzle(p, "y"), 1, "float"), rt.binary("*", rt.swizzle(p, "x"), rt.swizzle(p, "z"), 1, "float"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), rt.binary("-", rt.binary("*", rt.binary("*", d, rt.swizzle(p, "x"), 1, "float"), rt.swizzle(p, "y"), 1, "float"), rt.binary("*", e, rt.swizzle(p, "z"), 1, "float"), 1, "float"))
    def stepAttractor__vec3_int_float(p, type, dt):
        p = rt.copy(p, "float")
        dp = rt.construct(3, 0.0)
        if rt.binary("==", type, rt.i(0)):
            dp[:] = lorenz__vec3(p)
        else:
            if rt.binary("==", type, rt.i(1)):
                dp[:] = rossler__vec3(p)
            else:
                if rt.binary("==", type, rt.i(2)):
                    dp[:] = aizawa__vec3(p)
                else:
                    if rt.binary("==", type, rt.i(3)):
                        dp[:] = thomas__vec3(p)
                    else:
                        if rt.binary("==", type, rt.i(4)):
                            dp[:] = halvorsen__vec3(p)
                        else:
                            if rt.binary("==", type, rt.i(5)):
                                dp[:] = chen__vec3(p)
                            else:
                                dp[:] = dadras__vec3(p)
        return rt.binary("+", p, rt.binary("*", dp, dt, 3, "float"), 3, "float")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        texSize = rt.texture_size(_u_xyzTex)
        stateSize = rt.swizzle(texSize, "x")
        pos = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        col = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        agentSeed = rt.binary("+", rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), stateSize, 1, "int"), 1, "int"), base="uint"), rt.construct(1, _u_seed, base="uint"), 1, "uint")
        needs3DInit = (bool((bool((bool((bool((bool(rt.binary(">=", rt.swizzle(pos, "w"), rt.f(0.5))) and bool(rt.binary("==", rt.swizzle(pos, "z"), rt.f(0.0))))) and bool(rt.binary(">=", rt.swizzle(pos, "x"), rt.f(0.0))))) and bool(rt.binary("<=", rt.swizzle(pos, "x"), rt.f(1.0))))) and bool(rt.binary(">=", rt.swizzle(pos, "y"), rt.f(0.0))))) and bool(rt.binary("<=", rt.swizzle(pos, "y"), rt.f(1.0))))
        initSeed = 0
        if needs3DInit:
            initSeed = rt.binary("+", agentSeed, rt.construct(1, rt.binary("*", _u_time, rt.f(1000.0), 1, "float"), base="uint"), 1, "uint")
            pos = rt.assign_swizzle(pos, "x", rt.binary("*", rt.binary("-", hash__uint(initSeed), rt.f(0.5), 1, "float"), rt.f(20.0), 1, "float"))
            pos = rt.assign_swizzle(pos, "y", rt.binary("*", rt.binary("-", hash__uint(rt.binary("+", initSeed, rt.i(1), 1, "uint")), rt.f(0.5), 1, "float"), rt.f(20.0), 1, "float"))
            pos = rt.assign_swizzle(pos, "z", rt.binary("+", rt.binary("*", hash__uint(rt.binary("+", initSeed, rt.i(2), 1, "uint")), rt.f(30.0), 1, "float"), rt.f(10.0), 1, "float"))
            g.outXYZ[:] = rt.construct(4, rt.swizzle(pos, "xyz"), rt.f(1.0))
            g.outVel[:] = vel
            g.outRGBA[:] = col
            return
        if rt.binary("<", rt.swizzle(pos, "w"), rt.f(0.5)):
            g.outXYZ[:] = pos
            g.outVel[:] = vel
            g.outRGBA[:] = col
            return
        dt = rt.binary("*", _u_speed, rt.f(0.01), 1, "float")
        newPos = stepAttractor__vec3_int_float(rt.swizzle(pos, "xyz"), _u_attractor, dt)
        respawnSeed = 0
        if (bool(rt.component_wise("any", rt.component_wise("isnan", newPos, width=3), width=3)) or bool(rt.binary(">", rt.length(newPos), rt.f(1000.0)))):
            respawnSeed = rt.binary("+", agentSeed, rt.construct(1, rt.binary("*", _u_time, rt.f(1000.0), 1, "float"), base="uint"), 1, "uint")
            newPos = rt.assign_swizzle(newPos, "x", rt.binary("*", rt.binary("-", hash__uint(respawnSeed), rt.f(0.5), 1, "float"), rt.f(20.0), 1, "float"))
            newPos = rt.assign_swizzle(newPos, "y", rt.binary("*", rt.binary("-", hash__uint(rt.binary("+", respawnSeed, rt.i(1), 1, "uint")), rt.f(0.5), 1, "float"), rt.f(20.0), 1, "float"))
            newPos = rt.assign_swizzle(newPos, "z", rt.binary("+", rt.binary("*", hash__uint(rt.binary("+", respawnSeed, rt.i(2), 1, "uint")), rt.f(30.0), 1, "float"), rt.f(10.0), 1, "float"))
        g.outXYZ[:] = rt.construct(4, newPos, rt.f(1.0))
        g.outVel[:] = vel
        g.outRGBA[:] = col
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
