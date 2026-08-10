def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_gravity = U.get("gravity", rt.f(0.0))
    _u_wind = U.get("wind", rt.f(0.0))
    _u_energy = U.get("energy", rt.f(0.0))
    _u_drag = U.get("drag", rt.f(0.0))
    _u_deviation = U.get("deviation", rt.f(0.0))
    _u_wander = U.get("wander", rt.f(0.0))
    _u_inputTex = T["inputTex"]
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
    def noise2D__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        f[:] = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        n = rt.binary("+", rt.construct(1, rt.swizzle(i, "x"), base="uint"), rt.binary("*", rt.construct(1, rt.swizzle(i, "y"), base="uint"), rt.i(57), 1, "uint"), 1, "uint")
        a = hash__uint(n)
        b = hash__uint(rt.binary("+", n, rt.i(1), 1, "uint"))
        c = hash__uint(rt.binary("+", n, rt.i(57), 1, "uint"))
        d = hash__uint(rt.binary("+", n, rt.i(58), 1, "uint"))
        return rt.component_wise("mix", rt.component_wise("mix", a, b, rt.swizzle(f, "x"), width=1), rt.component_wise("mix", c, d, rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1)
    def fbm__vec2(p):
        p = rt.copy(p, "float")
        v = rt.f(0.0)
        a = rt.f(0.5)
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, rt.i(3))):
                break
            v = rt.binary("+", v, rt.binary("*", a, noise2D__vec2(p), 1, "float"), 1, "float")
            p[:] = rt.binary("*", p, rt.f(2.0), 2, "float")
            a = rt.binary("*", a, rt.f(0.5), 1, "float")
        return v
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
        vx = rt.swizzle(vel, "x")
        vy = rt.swizzle(vel, "y")
        vz = rt.swizzle(vel, "z")
        seed_f = rt.swizzle(vel, "w")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        deviationMultiplier = rt.binary("+", rt.f(1.0), rt.binary("*", rt.binary("*", rt.binary("-", seed_f, rt.f(0.5), 1, "float"), _u_deviation, 1, "float"), rt.f(2.0), 1, "float"), 1, "float")
        noiseScale = rt.f(2.0)
        wanderAngle = rt.binary("*", rt.binary("*", fbm__vec2(rt.binary("+", rt.binary("*", rt.construct(2, px, py), noiseScale, 2, "float"), rt.binary("*", _u_time, rt.f(0.5), 1, "float"), 2, "float")), rt.f(6.283185), 1, "float"), rt.f(2.0), 1, "float")
        wanderStrength = rt.binary("*", _u_wander, rt.f(0.002), 1, "float")
        wanderX = rt.binary("*", rt.component_wise("cos", wanderAngle, width=1), wanderStrength, 1, "float")
        wanderY = rt.binary("*", rt.component_wise("sin", wanderAngle, width=1), wanderStrength, 1, "float")
        ax = rt.binary("*", rt.binary("+", rt.binary("*", _u_wind, rt.f(0.01), 1, "float"), wanderX, 1, "float"), _u_energy, 1, "float")
        ay = rt.binary("*", rt.binary("+", rt.binary("*", rt.unary("-", _u_gravity), rt.f(0.01), 1, "float"), wanderY, 1, "float"), _u_energy, 1, "float")
        vx = rt.binary("+", vx, rt.binary("*", ax, deviationMultiplier, 1, "float"), 1, "float")
        vy = rt.binary("+", vy, rt.binary("*", ay, deviationMultiplier, 1, "float"), 1, "float")
        dragFactor = rt.binary("-", rt.f(1.0), _u_drag, 1, "float")
        vx = rt.binary("*", vx, dragFactor, 1, "float")
        vy = rt.binary("*", vy, dragFactor, 1, "float")
        px = rt.binary("+", px, vx, 1, "float")
        py = rt.binary("+", py, vy, 1, "float")
        needsRespawn = False
        if (bool((bool((bool(rt.binary("<", px, rt.f(0.0))) or bool(rt.binary(">", px, rt.f(1.0))))) or bool(rt.binary("<", py, rt.f(0.0))))) or bool(rt.binary(">", py, rt.f(1.0)))):
            needsRespawn = True
        if needsRespawn:
            g.outXYZ[:] = rt.construct(4, px, py, pz, rt.f(0.0))
            g.outVel[:] = rt.construct(4, vx, vy, vz, seed_f)
            g.outRGBA[:] = rgba
        else:
            g.outXYZ[:] = rt.construct(4, px, py, pz, rt.f(1.0))
            g.outVel[:] = rt.construct(4, vx, vy, vz, seed_f)
            g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
