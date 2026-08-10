def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_typeCount = U.get("typeCount", 0)
    _u_attractionScale = U.get("attractionScale", rt.f(0.0))
    _u_repulsionScale = U.get("repulsionScale", rt.f(0.0))
    _u_minRadius = U.get("minRadius", rt.f(0.0))
    _u_maxRadius = U.get("maxRadius", rt.f(0.0))
    _u_maxSpeed = U.get("maxSpeed", rt.f(0.0))
    _u_friction = U.get("friction", rt.f(0.0))
    _u_boundaryMode = U.get("boundaryMode", 0)
    _u_matrixSeed = U.get("matrixSeed", rt.f(0.0))
    _u_symmetricForces = U.get("symmetricForces", False)
    _u_useTypeColor = U.get("useTypeColor", False)
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    _u_dataTex = T["dataTex"]
    _u_forceMatrix = T["forceMatrix"]
    _u_inputTex = T["inputTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    g.outData = rt.construct(4, 0.0)
    g.GRID_SIZE = rt.i(16)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def hash2__uint(seed):
        return rt.construct(2, hash__uint(seed), hash__uint(rt.binary("+", seed, rt.i(1), 1, "uint")))
    def typeColor__int_int(typeId, totalTypes):
        hue = rt.binary("/", rt.construct(1, typeId), rt.construct(1, totalTypes), 1, "float")
        h = rt.binary("*", hue, rt.f(6.0), 1, "float")
        c = rt.f(1.0)
        x = rt.binary("*", c, rt.binary("-", rt.f(1.0), rt.component_wise("abs", rt.binary("-", rt.component_wise("mod", h, rt.f(2.0), width=1), rt.f(1.0), 1, "float"), width=1), 1, "float"), 1, "float")
        rgb = rt.construct(3, 0.0)
        if rt.binary("<", h, rt.f(1.0)):
            (rgb.__setitem__(0, c), rgb.__setitem__(1, x), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
        else:
            if rt.binary("<", h, rt.f(2.0)):
                (rgb.__setitem__(0, x), rgb.__setitem__(1, c), rgb.__setitem__(2, rt.f(0.0)), rgb)[-1]
            else:
                if rt.binary("<", h, rt.f(3.0)):
                    (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, c), rgb.__setitem__(2, x), rgb)[-1]
                else:
                    if rt.binary("<", h, rt.f(4.0)):
                        (rgb.__setitem__(0, rt.f(0.0)), rgb.__setitem__(1, x), rgb.__setitem__(2, c), rgb)[-1]
                    else:
                        if rt.binary("<", h, rt.f(5.0)):
                            (rgb.__setitem__(0, x), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, c), rgb)[-1]
                        else:
                            (rgb.__setitem__(0, c), rgb.__setitem__(1, rt.f(0.0)), rgb.__setitem__(2, x), rgb)[-1]
        return rgb
    def getGridCell__vec2(pos):
        pos = rt.copy(pos, "float")
        cellSize = rt.binary("/", rt.construct(2, rt.f(1.0)), rt.construct(1, g.GRID_SIZE), 2, "float")
        return rt.construct(2, rt.component_wise("clamp", rt.binary("/", pos, cellSize, 2, "float"), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.construct(1, rt.binary("-", g.GRID_SIZE, rt.i(1), 1, "int"))), width=2), base="int")
    def radialForce__float_float_float_float(dist, strength, prefDist, curveShape):
        normDist = rt.binary("/", rt.binary("-", dist, _u_minRadius, 1, "float"), rt.binary("-", _u_maxRadius, _u_minRadius, 1, "float"), 1, "float")
        forceScale = rt.binary("*", _u_maxSpeed, rt.f(10.0), 1, "float")
        if rt.binary("<", normDist, rt.f(0.0)):
            return rt.binary("*", rt.binary("*", rt.unary("-", _u_repulsionScale), rt.binary("-", rt.f(1.0), rt.binary("/", dist, _u_minRadius, 1, "float"), 1, "float"), 1, "float"), forceScale, 1, "float")
        if rt.binary(">", normDist, rt.f(1.0)):
            return rt.f(0.0)
        force = rt.f(0.0)
        if rt.binary("<", normDist, prefDist):
            force = rt.binary("*", strength, rt.binary("/", normDist, prefDist, 1, "float"), 1, "float")
        else:
            force = rt.binary("*", strength, rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", normDist, prefDist, 1, "float"), rt.binary("-", rt.f(1.0), prefDist, 1, "float"), 1, "float"), 1, "float"), 1, "float")
        shaped = rt.binary("*", rt.component_wise("sign", force, width=1), rt.component_wise("pow", rt.component_wise("abs", force, width=1), rt.binary("-", rt.f(1.0), rt.binary("*", curveShape, rt.f(0.5), 1, "float"), 1, "float"), width=1), 1, "float")
        if rt.binary(">", shaped, rt.f(0.0)):
            return rt.binary("*", rt.binary("*", shaped, _u_attractionScale, 1, "float"), forceScale, 1, "float")
        else:
            return rt.binary("*", rt.binary("*", shaped, _u_repulsionScale, 1, "float"), forceScale, 1, "float")
    def wrapPosition__vec2(pos):
        pos = rt.copy(pos, "float")
        return rt.component_wise("mod", rt.binary("+", pos, rt.f(1.0), 2, "float"), rt.f(1.0), width=2)
    def limitVec__vec2_float(v, maxLen):
        v = rt.copy(v, "float")
        len = rt.length(v)
        if (bool(rt.binary(">", len, maxLen)) and bool(rt.binary(">", len, rt.f(0.0)))):
            return rt.binary("*", v, rt.binary("/", maxLen, len, 1, "float"), 2, "float")
        return v
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateSize = rt.texture_size(_u_xyzTex)
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        data = rt.texel_fetch(_u_dataTex, coord, rt.i(0))
        px = rt.swizzle(xyz, "x")
        py = rt.swizzle(xyz, "y")
        alive = rt.swizzle(xyz, "w")
        vx = rt.swizzle(vel, "x")
        vy = rt.swizzle(vel, "y")
        age = rt.swizzle(vel, "z")
        seed = rt.swizzle(vel, "w")
        typeId = rt.swizzle(data, "x")
        mass = rt.swizzle(data, "y")
        particleId = rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(stateSize, "x"), 1, "int"), 1, "int"), base="uint")
        pos = rt.construct(2, px, py)
        velocity = rt.construct(2, vx, vy)
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            g.outData[:] = data
            return
        initSeed = 0
        if (bool(rt.binary("==", typeId, rt.f(0.0))) and bool(rt.binary("==", mass, rt.f(0.0)))):
            initSeed = rt.binary("+", particleId, rt.construct(1, rt.binary("*", _u_time, rt.f(1000.0), 1, "float"), base="uint"), 1, "uint")
            typeId = rt.component_wise("floor", rt.binary("*", hash__uint(rt.binary("+", initSeed, rt.i(4), 1, "uint")), rt.construct(1, _u_typeCount), 1, "float"), width=1)
            mass = rt.binary("+", rt.f(0.8), rt.binary("*", hash__uint(rt.binary("+", initSeed, rt.i(5), 1, "uint")), rt.f(0.4), 1, "float"), 1, "float")
            angle = rt.f(0.0)
            speed = rt.f(0.0)
            if rt.binary("==", rt.length(velocity), rt.f(0.0)):
                angle = rt.binary("*", hash__uint(rt.binary("+", initSeed, rt.i(2), 1, "uint")), rt.f(6.28318530718), 1, "float")
                speed = rt.binary("*", rt.binary("*", hash__uint(rt.binary("+", initSeed, rt.i(3), 1, "uint")), _u_maxSpeed, 1, "float"), rt.f(0.3), 1, "float")
                velocity[:] = rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), speed, 2, "float")
        mass = rt.component_wise("max", mass, rt.f(0.1), width=1)
        totalForce = rt.construct(2, rt.f(0.0))
        neighborCount = rt.i(0)
        myType = rt.construct(1, typeId, base="int")
        myCell = getGridCell__vec2(pos)
        totalParticles = rt.binary("*", rt.swizzle(stateSize, "x"), rt.swizzle(stateSize, "y"), 1, "int")
        dy = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dy, rt.i(1))):
                break
            dx = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", dx, rt.i(1))):
                    break
                checkCell = rt.binary("+", myCell, rt.construct(2, dx, dy, base="int"), 2, "int")
                checkCell[:] = rt.binary("%", rt.binary("+", checkCell, g.GRID_SIZE, 2, "int"), g.GRID_SIZE, 2, "int")
                cellSeed = rt.construct(1, rt.binary("+", rt.binary("*", rt.swizzle(checkCell, "y"), g.GRID_SIZE, 1, "int"), rt.swizzle(checkCell, "x"), 1, "int"), base="uint")
                s = rt.i(0)
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        s = rt.binary("+", s, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<", s, rt.i(12))):
                        break
                    sampleSeed = rt.binary("+", rt.binary("+", rt.binary("*", cellSeed, rt.i(31), 1, "uint"), rt.construct(1, s, base="uint"), 1, "uint"), rt.construct(1, rt.binary("*", _u_time, rt.f(7.0), 1, "float"), base="uint"), 1, "uint")
                    sampleIdx = rt.construct(1, rt.binary("%", rt.hash_uint(sampleSeed), rt.construct(1, totalParticles, base="uint"), 1, "uint"), base="int")
                    sx = rt.binary("%", sampleIdx, rt.swizzle(stateSize, "x"), 1, "int")
                    sy = rt.binary("/", sampleIdx, rt.swizzle(stateSize, "x"), 1, "int")
                    if (bool(rt.binary("==", sx, rt.swizzle(coord, "x"))) and bool(rt.binary("==", sy, rt.swizzle(coord, "y")))):
                        continue
                    otherXyz = rt.texel_fetch(_u_xyzTex, rt.construct(2, sx, sy, base="int"), rt.i(0))
                    otherData = rt.texel_fetch(_u_dataTex, rt.construct(2, sx, sy, base="int"), rt.i(0))
                    otherPos = rt.swizzle(otherXyz, "xy")
                    otherAlive = rt.swizzle(otherXyz, "w")
                    otherType = rt.construct(1, rt.swizzle(otherData, "x"), base="int")
                    if rt.binary("<", otherAlive, rt.f(0.5)):
                        continue
                    diff = rt.binary("-", otherPos, pos, 2, "float")
                    if rt.binary(">", rt.swizzle(diff, "x"), rt.f(0.5)):
                        diff = rt.assign_swizzle(diff, "x", rt.binary("-", rt.swizzle(diff, "x"), rt.f(1.0), 1, "float"))
                    if rt.binary("<", rt.swizzle(diff, "x"), rt.unary("-", rt.f(0.5))):
                        diff = rt.assign_swizzle(diff, "x", rt.binary("+", rt.swizzle(diff, "x"), rt.f(1.0), 1, "float"))
                    if rt.binary(">", rt.swizzle(diff, "y"), rt.f(0.5)):
                        diff = rt.assign_swizzle(diff, "y", rt.binary("-", rt.swizzle(diff, "y"), rt.f(1.0), 1, "float"))
                    if rt.binary("<", rt.swizzle(diff, "y"), rt.unary("-", rt.f(0.5))):
                        diff = rt.assign_swizzle(diff, "y", rt.binary("+", rt.swizzle(diff, "y"), rt.f(1.0), 1, "float"))
                    dist = rt.length(diff)
                    if (bool(rt.binary("<", dist, rt.f(0.0001))) or bool(rt.binary(">", dist, _u_maxRadius))):
                        continue
                    forceParams = rt.texel_fetch(_u_forceMatrix, rt.construct(2, myType, otherType, base="int"), rt.i(0))
                    strength = rt.swizzle(forceParams, "x")
                    prefDist = rt.swizzle(forceParams, "y")
                    curveShape = rt.swizzle(forceParams, "z")
                    forceMag = radialForce__float_float_float_float(dist, strength, prefDist, curveShape)
                    forceDir = rt.binary("/", diff, dist, 2, "float")
                    totalForce[:] = rt.binary("+", totalForce, rt.binary("*", forceDir, forceMag, 2, "float"), 2, "float")
                    neighborCount = rt.binary("+", neighborCount, rt.i(1), 1, "int")
        totalForce[:] = rt.binary("/", totalForce, mass, 2, "float")
        velocity[:] = rt.binary("+", velocity, totalForce, 2, "float")
        velocity[:] = rt.binary("*", velocity, rt.binary("-", rt.f(1.0), _u_friction, 1, "float"), 2, "float")
        velocity[:] = limitVec__vec2_float(velocity, _u_maxSpeed)
        pos[:] = rt.binary("+", pos, velocity, 2, "float")
        if rt.binary("==", _u_boundaryMode, rt.i(0)):
            pos[:] = wrapPosition__vec2(pos)
        else:
            if rt.binary("<", rt.swizzle(pos, "x"), rt.f(0.0)):
                pos = rt.assign_swizzle(pos, "x", rt.unary("-", rt.swizzle(pos, "x")))
                velocity = rt.assign_swizzle(velocity, "x", rt.unary("-", rt.swizzle(velocity, "x")))
            if rt.binary(">", rt.swizzle(pos, "x"), rt.f(1.0)):
                pos = rt.assign_swizzle(pos, "x", rt.binary("-", rt.f(2.0), rt.swizzle(pos, "x"), 1, "float"))
                velocity = rt.assign_swizzle(velocity, "x", rt.unary("-", rt.swizzle(velocity, "x")))
            if rt.binary("<", rt.swizzle(pos, "y"), rt.f(0.0)):
                pos = rt.assign_swizzle(pos, "y", rt.unary("-", rt.swizzle(pos, "y")))
                velocity = rt.assign_swizzle(velocity, "y", rt.unary("-", rt.swizzle(velocity, "y")))
            if rt.binary(">", rt.swizzle(pos, "y"), rt.f(1.0)):
                pos = rt.assign_swizzle(pos, "y", rt.binary("-", rt.f(2.0), rt.swizzle(pos, "y"), 1, "float"))
                velocity = rt.assign_swizzle(velocity, "y", rt.unary("-", rt.swizzle(velocity, "y")))
            pos[:] = rt.component_wise("clamp", pos, rt.construct(2, rt.f(0.001)), rt.construct(2, rt.f(0.999)), width=2)
        age = rt.binary("+", age, rt.f(0.016), 1, "float")
        g.outXYZ[:] = rt.construct(4, pos, rt.f(0.0), rt.f(1.0))
        g.outVel[:] = rt.construct(4, velocity, age, seed)
        if _u_useTypeColor:
            g.outRGBA[:] = rt.construct(4, typeColor__int_int(rt.construct(1, typeId, base="int"), _u_typeCount), rt.f(1.0))
        else:
            g.outRGBA[:] = rt.texture(_u_inputTex, pos)
        g.outData[:] = rt.construct(4, typeId, mass, rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
    _c = g.outData
    out[3][0] = rt.f32(_c[0]); out[3][1] = rt.f32(_c[1]); out[3][2] = rt.f32(_c[2]); out[3][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA', 'outData')
