def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_maxIter = U.get("maxIter", 0)
    _u_minIter = U.get("minIter", 0)
    _u_mode = U.get("mode", 0)
    _u_centerX = U.get("centerX", rt.f(0.0))
    _u_centerY = U.get("centerY", rt.f(0.0))
    _u_zoom = U.get("zoom", rt.f(0.0))
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    def hash_uint__uint(s):
        state = rt.binary("+", rt.binary("*", s, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(s):
        return rt.binary("/", rt.construct(1, rt.hash_uint(s)), rt.f(4294967295.0), 1, "float")
    def complexToScreen__vec2(z):
        z = rt.copy(z, "float")
        return rt.construct(2, rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", rt.swizzle(z, "y"), _u_centerY, 1, "float"), _u_zoom, 1, "float"), _u_zoom, 1, "float"), rt.f(0.2), 1, "float"), rt.f(0.5), 1, "float"), rt.binary("+", rt.binary("*", rt.binary("*", rt.binary("*", rt.binary("-", _u_centerX, rt.swizzle(z, "x"), 1, "float"), _u_zoom, 1, "float"), _u_zoom, 1, "float"), rt.f(0.2), 1, "float"), rt.f(0.5), 1, "float"))
    def inMandelbrotInterior__float_float(cRe, cIm):
        y2 = rt.binary("*", cIm, cIm, 1, "float")
        q = rt.binary("+", rt.binary("*", rt.binary("-", cRe, rt.f(0.25), 1, "float"), rt.binary("-", cRe, rt.f(0.25), 1, "float"), 1, "float"), y2, 1, "float")
        if rt.binary("<=", rt.binary("*", q, rt.binary("+", q, rt.binary("-", cRe, rt.f(0.25), 1, "float"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.25), y2, 1, "float")):
            return True
        xp1 = rt.binary("+", cRe, rt.f(1.0), 1, "float")
        return rt.binary("<=", rt.binary("+", rt.binary("*", xp1, xp1, 1, "float"), y2, 1, "float"), rt.f(0.0625))
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        texSize = rt.texture_size(_u_xyzTex)
        stateSize = rt.swizzle(texSize, "x")
        pos = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        col = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        if rt.binary("<", rt.swizzle(pos, "w"), rt.f(0.5)):
            g.outXYZ[:] = pos
            g.outVel[:] = vel
            g.outRGBA[:] = col
            return
        agentSeed = rt.binary("^", rt.binary("^", rt.hash_uint(rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), stateSize, 1, "int"), 1, "int"), base="uint")), rt.construct(1, rt.binary("*", _u_time, rt.f(65536.0), 1, "float"), base="uint"), 1, "uint"), rt.construct(1, rt.binary("*", rt.swizzle(vel, "z"), rt.f(137.0), 1, "float"), base="uint"), 1, "uint")
        needsInit = rt.binary("<", rt.swizzle(pos, "z"), rt.f(0.25))
        cRe = rt.f(0.0)
        cIm = rt.f(0.0)
        z = rt.construct(2, 0.0)
        escapeAt = 0
        iterCap = 0
        escaped = False
        escapeStep = rt.f(0.0)
        brightness = rt.f(0.0)
        screen = rt.construct(2, 0.0)
        if needsInit:
            cRe = rt.binary("-", rt.binary("*", hash__uint(agentSeed), rt.f(3.5), 1, "float"), rt.f(2.5), 1, "float")
            cIm = rt.binary("-", rt.binary("*", hash__uint(rt.binary("+", agentSeed, rt.i(1), 1, "uint")), rt.f(3.0), 1, "float"), rt.f(1.5), 1, "float")
            if (bool(rt.binary("==", _u_mode, rt.i(0))) and bool(inMandelbrotInterior__float_float(cRe, cIm))):
                g.outXYZ[:] = rt.construct(4, rt.swizzle(pos, "xy"), rt.f(0.0), rt.f(0.0))
                g.outVel[:] = vel
                g.outRGBA[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0))
                return
            z = rt.construct(2, rt.f(0.0))
            escapeAt = rt.i(0)
            iterCap = rt.component_wise("min", _u_maxIter, rt.i(2048), width=1)
            i = rt.i(0)
            _for0_first = True
            for _for0 in range(1048576):
                if not _for0_first:
                    i = rt.binary("+", i, rt.i(1), 1, "int")
                _for0_first = False
                if not (rt.binary("<", i, rt.i(2048))):
                    break
                if rt.binary(">=", i, iterCap):
                    break
                zr = rt.binary("+", rt.binary("-", rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), cRe, 1, "float")
                zi = rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(z, "x"), 1, "float"), rt.swizzle(z, "y"), 1, "float"), cIm, 1, "float")
                (z.__setitem__(0, zr), z.__setitem__(1, zi), z)[-1]
                if rt.binary(">", rt.dot(z, z), rt.f(4.0)):
                    escapeAt = rt.binary("+", i, rt.i(1), 1, "int")
                    break
            escaped = rt.binary(">", escapeAt, rt.i(0))
            escapeStep = rt.f(0.0)
            brightness = rt.f(0.0)
            if rt.binary("==", _u_mode, rt.i(0)):
                if (bool(escaped) and bool(rt.binary(">=", escapeAt, _u_minIter))):
                    escapeStep = rt.construct(1, escapeAt)
                    brightness = rt.f(0.03)
            else:
                if (not (escaped)):
                    escapeStep = rt.construct(1, iterCap)
                    brightness = rt.f(0.03)
            if rt.binary("==", brightness, rt.f(0.0)):
                g.outXYZ[:] = rt.construct(4, rt.swizzle(pos, "xy"), rt.f(0.0), rt.f(0.0))
                g.outVel[:] = vel
                g.outRGBA[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0))
                return
            screen = complexToScreen__vec2(rt.construct(2, cRe, cIm))
            g.outXYZ[:] = rt.construct(4, screen, rt.f(0.5), rt.f(1.0))
            g.outVel[:] = rt.construct(4, cRe, cIm, rt.f(1.0), escapeStep)
            g.outRGBA[:] = rt.construct(4, brightness, brightness, brightness, rt.f(1.0))
            return
        cRe = rt.swizzle(vel, "x")
        cIm = rt.swizzle(vel, "y")
        step = rt.swizzle(vel, "z")
        escapeStep = rt.swizzle(vel, "w")
        z = rt.construct(2, rt.f(0.0))
        currentStep = rt.construct(1, step, base="int")
        i = rt.i(0)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<", i, rt.i(2048))):
                break
            if rt.binary(">=", i, currentStep):
                break
            zr = rt.binary("+", rt.binary("-", rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), cRe, 1, "float")
            zi = rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(z, "x"), 1, "float"), rt.swizzle(z, "y"), 1, "float"), cIm, 1, "float")
            (z.__setitem__(0, zr), z.__setitem__(1, zi), z)[-1]
        s = rt.i(0)
        _for2_first = True
        for _for2 in range(1048576):
            if not _for2_first:
                s = rt.binary("+", s, rt.i(1), 1, "int")
            _for2_first = False
            if not (rt.binary("<", s, rt.i(8))):
                break
            step = rt.binary("+", step, rt.f(1.0), 1, "float")
            if rt.binary(">=", step, escapeStep):
                g.outXYZ[:] = rt.construct(4, rt.swizzle(pos, "xy"), rt.f(0.0), rt.f(0.0))
                g.outVel[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), step, rt.f(0.0))
                g.outRGBA[:] = rt.construct(4, rt.f(0.0), rt.f(0.0), rt.f(0.0), rt.f(0.0))
                return
            zr = rt.binary("+", rt.binary("-", rt.binary("*", rt.swizzle(z, "x"), rt.swizzle(z, "x"), 1, "float"), rt.binary("*", rt.swizzle(z, "y"), rt.swizzle(z, "y"), 1, "float"), 1, "float"), cRe, 1, "float")
            zi = rt.binary("+", rt.binary("*", rt.binary("*", rt.f(2.0), rt.swizzle(z, "x"), 1, "float"), rt.swizzle(z, "y"), 1, "float"), cIm, 1, "float")
            (z.__setitem__(0, zr), z.__setitem__(1, zi), z)[-1]
        screen = complexToScreen__vec2(z)
        g.outXYZ[:] = rt.construct(4, screen, rt.f(0.5), rt.f(1.0))
        g.outVel[:] = rt.construct(4, cRe, cIm, step, escapeStep)
        g.outRGBA[:] = col
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
