def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_time = U.get("time", rt.f(0.0))
    _u_separation = U.get("separation", rt.f(0.0))
    _u_alignment = U.get("alignment", rt.f(0.0))
    _u_cohesion = U.get("cohesion", rt.f(0.0))
    _u_perceptionRadius = U.get("perceptionRadius", rt.f(0.0))
    _u_separationRadius = U.get("separationRadius", rt.f(0.0))
    _u_maxSpeed = U.get("maxSpeed", rt.f(0.0))
    _u_maxForce = U.get("maxForce", rt.f(0.0))
    _u_boundaryMode = U.get("boundaryMode", 0)
    _u_wallMargin = U.get("wallMargin", rt.f(0.0))
    _u_noiseWeight = U.get("noiseWeight", rt.f(0.0))
    _u_xyzTex = T["xyzTex"]
    _u_velTex = T["velTex"]
    _u_rgbaTex = T["rgbaTex"]
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    g.GRID_SIZE = rt.i(16)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def hash2__uint(seed):
        return rt.construct(2, hash__uint(seed), hash__uint(rt.binary("+", seed, rt.i(1), 1, "uint")))
    def hashFloat__float(n):
        return rt.binary("/", rt.construct(1, rt.hash_uint(rt.float_bits_to_uint(n))), rt.f(4294967295.0), 1, "float")
    def noise2D__vec2(p):
        p = rt.copy(p, "float")
        i = rt.component_wise("floor", p, width=2)
        f = rt.component_wise("fract", p, width=2)
        f[:] = rt.binary("*", rt.binary("*", f, f, 2, "float"), rt.binary("-", rt.f(3.0), rt.binary("*", rt.f(2.0), f, 2, "float"), 2, "float"), 2, "float")
        n = rt.binary("+", rt.swizzle(i, "x"), rt.binary("*", rt.swizzle(i, "y"), rt.f(57.0), 1, "float"), 1, "float")
        return rt.binary("-", rt.binary("*", rt.component_wise("mix", rt.component_wise("mix", hashFloat__float(n), hashFloat__float(rt.binary("+", n, rt.f(1.0), 1, "float")), rt.swizzle(f, "x"), width=1), rt.component_wise("mix", hashFloat__float(rt.binary("+", n, rt.f(57.0), 1, "float")), hashFloat__float(rt.binary("+", n, rt.f(58.0), 1, "float")), rt.swizzle(f, "x"), width=1), rt.swizzle(f, "y"), width=1), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")
    def wrapPosition__vec2_vec2(position, bounds):
        position = rt.copy(position, "float")
        bounds = rt.copy(bounds, "float")
        return rt.component_wise("mod", rt.binary("+", position, bounds, 2, "float"), bounds, width=2)
    def limitVec__vec2_float(v, maxLen):
        v = rt.copy(v, "float")
        len = rt.length(v)
        if (bool(rt.binary(">", len, maxLen)) and bool(rt.binary(">", len, rt.f(0.0)))):
            return rt.binary("*", v, rt.binary("/", maxLen, len, 1, "float"), 2, "float")
        return v
    def setMag__vec2_float(v, mag):
        v = rt.copy(v, "float")
        len = rt.length(v)
        if rt.binary(">", len, rt.f(0.0)):
            return rt.binary("*", v, rt.binary("/", mag, len, 1, "float"), 2, "float")
        return v
    def getGridCell__vec2_vec2(pos, res):
        pos = rt.copy(pos, "float")
        res = rt.copy(res, "float")
        cellSize = rt.binary("/", res, rt.construct(1, g.GRID_SIZE), 2, "float")
        return rt.construct(2, rt.component_wise("clamp", rt.binary("/", pos, cellSize, 2, "float"), rt.construct(2, rt.f(0.0)), rt.construct(2, rt.construct(1, rt.binary("-", g.GRID_SIZE, rt.i(1), 1, "int"))), width=2), base="int")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        stateSize = rt.texture_size(_u_xyzTex)
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        px = rt.swizzle(xyz, "x")
        py = rt.swizzle(xyz, "y")
        alive = rt.swizzle(xyz, "w")
        vx = rt.swizzle(vel, "x")
        vy = rt.swizzle(vel, "y")
        age = rt.swizzle(vel, "z")
        seed = rt.swizzle(vel, "w")
        boidId = rt.construct(1, rt.binary("+", rt.swizzle(coord, "x"), rt.binary("*", rt.swizzle(coord, "y"), rt.swizzle(stateSize, "x"), 1, "int"), 1, "int"), base="uint")
        pos = rt.binary("*", rt.construct(2, px, py), _u_resolution, 2, "float")
        velocity = rt.construct(2, vx, vy)
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        angle = rt.f(0.0)
        speed = rt.f(0.0)
        if (bool(rt.binary("==", rt.length(velocity), rt.f(0.0))) and bool(rt.binary("==", seed, rt.f(0.0)))):
            seed = hash__uint(rt.binary("+", boidId, rt.i(99999), 1, "uint"))
            angle = rt.binary("*", hash__uint(rt.binary("+", boidId, rt.i(12345), 1, "uint")), rt.f(6.28318530718), 1, "float")
            speed = rt.binary("+", rt.binary("*", rt.binary("*", hash__uint(rt.binary("+", boidId, rt.i(23456), 1, "uint")), _u_maxSpeed, 1, "float"), rt.f(0.5), 1, "float"), rt.binary("*", _u_maxSpeed, rt.f(0.25), 1, "float"), 1, "float")
            velocity[:] = rt.binary("*", rt.construct(2, rt.component_wise("cos", angle, width=1), rt.component_wise("sin", angle, width=1)), speed, 2, "float")
        separationForce = rt.construct(2, rt.f(0.0))
        alignmentSum = rt.construct(2, rt.f(0.0))
        cohesionSum = rt.construct(2, rt.f(0.0))
        separationCount = rt.i(0)
        alignmentCount = rt.i(0)
        cohesionCount = rt.i(0)
        myCell = getGridCell__vec2_vec2(pos, _u_resolution)
        perceptionSq = rt.binary("*", _u_perceptionRadius, _u_perceptionRadius, 1, "float")
        separationSq = rt.binary("*", _u_separationRadius, _u_separationRadius, 1, "float")
        totalBoids = rt.binary("*", rt.swizzle(stateSize, "x"), rt.swizzle(stateSize, "y"), 1, "int")
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
                if rt.binary("==", _u_boundaryMode, rt.i(0)):
                    checkCell[:] = rt.binary("%", rt.binary("+", checkCell, g.GRID_SIZE, 2, "int"), g.GRID_SIZE, 2, "int")
                else:
                    checkCell[:] = rt.component_wise("clamp", checkCell, rt.construct(2, rt.i(0), base="int"), rt.construct(2, rt.binary("-", g.GRID_SIZE, rt.i(1), 1, "int"), base="int"), width=2)
                cellSeed = rt.construct(1, rt.binary("+", rt.binary("*", rt.swizzle(checkCell, "y"), g.GRID_SIZE, 1, "int"), rt.swizzle(checkCell, "x"), 1, "int"), base="uint")
                s = rt.i(0)
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        s = rt.binary("+", s, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<", s, rt.i(8))):
                        break
                    sampleSeed = rt.binary("+", rt.binary("+", rt.binary("*", cellSeed, rt.i(31), 1, "uint"), rt.construct(1, s, base="uint"), 1, "uint"), rt.construct(1, rt.binary("*", _u_time, rt.f(10.0), 1, "float"), base="uint"), 1, "uint")
                    sampleIdx = rt.construct(1, rt.binary("%", rt.hash_uint(sampleSeed), rt.construct(1, totalBoids, base="uint"), 1, "uint"), base="int")
                    sx = rt.binary("%", sampleIdx, rt.swizzle(stateSize, "x"), 1, "int")
                    sy = rt.binary("/", sampleIdx, rt.swizzle(stateSize, "x"), 1, "int")
                    if (bool(rt.binary("==", sx, rt.swizzle(coord, "x"))) and bool(rt.binary("==", sy, rt.swizzle(coord, "y")))):
                        continue
                    otherXyz = rt.texel_fetch(_u_xyzTex, rt.construct(2, sx, sy, base="int"), rt.i(0))
                    otherVel = rt.texel_fetch(_u_velTex, rt.construct(2, sx, sy, base="int"), rt.i(0))
                    if rt.binary("<", rt.swizzle(otherXyz, "w"), rt.f(0.5)):
                        continue
                    otherPos = rt.binary("*", rt.swizzle(otherXyz, "xy"), _u_resolution, 2, "float")
                    otherVelocity = rt.swizzle(otherVel, "xy")
                    diff = rt.binary("-", otherPos, pos, 2, "float")
                    if rt.binary("==", _u_boundaryMode, rt.i(0)):
                        if rt.binary(">", rt.swizzle(diff, "x"), rt.binary("*", rt.swizzle(_u_resolution, "x"), rt.f(0.5), 1, "float")):
                            diff = rt.assign_swizzle(diff, "x", rt.binary("-", rt.swizzle(diff, "x"), rt.swizzle(_u_resolution, "x"), 1, "float"))
                        if rt.binary("<", rt.swizzle(diff, "x"), rt.binary("*", rt.unary("-", rt.swizzle(_u_resolution, "x")), rt.f(0.5), 1, "float")):
                            diff = rt.assign_swizzle(diff, "x", rt.binary("+", rt.swizzle(diff, "x"), rt.swizzle(_u_resolution, "x"), 1, "float"))
                        if rt.binary(">", rt.swizzle(diff, "y"), rt.binary("*", rt.swizzle(_u_resolution, "y"), rt.f(0.5), 1, "float")):
                            diff = rt.assign_swizzle(diff, "y", rt.binary("-", rt.swizzle(diff, "y"), rt.swizzle(_u_resolution, "y"), 1, "float"))
                        if rt.binary("<", rt.swizzle(diff, "y"), rt.binary("*", rt.unary("-", rt.swizzle(_u_resolution, "y")), rt.f(0.5), 1, "float")):
                            diff = rt.assign_swizzle(diff, "y", rt.binary("+", rt.swizzle(diff, "y"), rt.swizzle(_u_resolution, "y"), 1, "float"))
                    distSq = rt.dot(diff, diff)
                    away = rt.construct(2, 0.0)
                    dist = rt.f(0.0)
                    if (bool(rt.binary("<", distSq, separationSq)) and bool(rt.binary(">", distSq, rt.f(0.0)))):
                        away = rt.unary("-", diff)
                        dist = rt.component_wise("sqrt", distSq, width=1)
                        separationForce[:] = rt.binary("+", separationForce, rt.binary("/", away, dist, 2, "float"), 2, "float")
                        separationCount = rt.binary("+", separationCount, rt.i(1), 1, "int")
                    if (bool(rt.binary("<", distSq, perceptionSq)) and bool(rt.binary(">", distSq, rt.f(0.0)))):
                        alignmentSum[:] = rt.binary("+", alignmentSum, otherVelocity, 2, "float")
                        alignmentCount = rt.binary("+", alignmentCount, rt.i(1), 1, "int")
                        cohesionSum[:] = rt.binary("+", cohesionSum, otherPos, 2, "float")
                        cohesionCount = rt.binary("+", cohesionCount, rt.i(1), 1, "int")
        steer = rt.construct(2, rt.f(0.0))
        if rt.binary(">", separationCount, rt.i(0)):
            separationForce[:] = rt.binary("/", separationForce, rt.construct(1, separationCount), 2, "float")
            if rt.binary(">", rt.length(separationForce), rt.f(0.0)):
                separationForce[:] = setMag__vec2_float(separationForce, _u_maxSpeed)
                separationForce[:] = rt.binary("-", separationForce, velocity, 2, "float")
                separationForce[:] = limitVec__vec2_float(separationForce, _u_maxForce)
                steer[:] = rt.binary("+", steer, rt.binary("*", separationForce, _u_separation, 2, "float"), 2, "float")
        avgVel = rt.construct(2, 0.0)
        if rt.binary(">", alignmentCount, rt.i(0)):
            avgVel = rt.binary("/", alignmentSum, rt.construct(1, alignmentCount), 2, "float")
            alignSteer = rt.construct(2, 0.0)
            if rt.binary(">", rt.length(avgVel), rt.f(0.0)):
                avgVel[:] = setMag__vec2_float(avgVel, _u_maxSpeed)
                alignSteer = rt.binary("-", avgVel, velocity, 2, "float")
                alignSteer[:] = limitVec__vec2_float(alignSteer, _u_maxForce)
                steer[:] = rt.binary("+", steer, rt.binary("*", alignSteer, _u_alignment, 2, "float"), 2, "float")
        avgPos = rt.construct(2, 0.0)
        desired = rt.construct(2, 0.0)
        if rt.binary(">", cohesionCount, rt.i(0)):
            avgPos = rt.binary("/", cohesionSum, rt.construct(1, cohesionCount), 2, "float")
            desired = rt.binary("-", avgPos, pos, 2, "float")
            cohesionSteer = rt.construct(2, 0.0)
            if rt.binary(">", rt.length(desired), rt.f(0.0)):
                desired[:] = setMag__vec2_float(desired, _u_maxSpeed)
                cohesionSteer = rt.binary("-", desired, velocity, 2, "float")
                cohesionSteer[:] = limitVec__vec2_float(cohesionSteer, _u_maxForce)
                steer[:] = rt.binary("+", steer, rt.binary("*", cohesionSteer, _u_cohesion, 2, "float"), 2, "float")
        noiseScale = rt.f(0.0)
        nx = rt.f(0.0)
        ny = rt.f(0.0)
        noiseForce = rt.construct(2, 0.0)
        if rt.binary(">", _u_noiseWeight, rt.f(0.0)):
            noiseScale = rt.f(0.01)
            nx = noise2D__vec2(rt.binary("+", rt.binary("*", pos, noiseScale, 2, "float"), rt.binary("*", _u_time, rt.f(0.5), 1, "float"), 2, "float"))
            ny = noise2D__vec2(rt.binary("+", rt.binary("+", rt.binary("*", pos, noiseScale, 2, "float"), rt.construct(2, rt.f(100.0), rt.f(100.0)), 2, "float"), rt.binary("*", _u_time, rt.f(0.5), 1, "float"), 2, "float"))
            noiseForce = rt.binary("*", rt.binary("*", rt.construct(2, nx, ny), _u_maxForce, 2, "float"), _u_noiseWeight, 2, "float")
            steer[:] = rt.binary("+", steer, noiseForce, 2, "float")
        wallForce = rt.construct(2, 0.0)
        turnStrength = rt.f(0.0)
        if rt.binary("==", _u_boundaryMode, rt.i(1)):
            wallForce = rt.construct(2, rt.f(0.0))
            turnStrength = rt.binary("*", _u_maxForce, rt.f(2.0), 1, "float")
            if rt.binary("<", rt.swizzle(pos, "x"), _u_wallMargin):
                wallForce = rt.assign_swizzle(wallForce, "x", rt.binary("*", turnStrength, rt.binary("-", rt.f(1.0), rt.binary("/", rt.swizzle(pos, "x"), _u_wallMargin, 1, "float"), 1, "float"), 1, "float"))
            else:
                if rt.binary(">", rt.swizzle(pos, "x"), rt.binary("-", rt.swizzle(_u_resolution, "x"), _u_wallMargin, 1, "float")):
                    wallForce = rt.assign_swizzle(wallForce, "x", rt.binary("*", rt.unary("-", turnStrength), rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", rt.swizzle(_u_resolution, "x"), rt.swizzle(pos, "x"), 1, "float"), _u_wallMargin, 1, "float"), 1, "float"), 1, "float"))
            if rt.binary("<", rt.swizzle(pos, "y"), _u_wallMargin):
                wallForce = rt.assign_swizzle(wallForce, "y", rt.binary("*", turnStrength, rt.binary("-", rt.f(1.0), rt.binary("/", rt.swizzle(pos, "y"), _u_wallMargin, 1, "float"), 1, "float"), 1, "float"))
            else:
                if rt.binary(">", rt.swizzle(pos, "y"), rt.binary("-", rt.swizzle(_u_resolution, "y"), _u_wallMargin, 1, "float")):
                    wallForce = rt.assign_swizzle(wallForce, "y", rt.binary("*", rt.unary("-", turnStrength), rt.binary("-", rt.f(1.0), rt.binary("/", rt.binary("-", rt.swizzle(_u_resolution, "y"), rt.swizzle(pos, "y"), 1, "float"), _u_wallMargin, 1, "float"), 1, "float"), 1, "float"))
            steer[:] = rt.binary("+", steer, wallForce, 2, "float")
        velocity[:] = rt.binary("+", velocity, steer, 2, "float")
        velocity[:] = limitVec__vec2_float(velocity, _u_maxSpeed)
        pos[:] = rt.binary("+", pos, velocity, 2, "float")
        if rt.binary("==", _u_boundaryMode, rt.i(0)):
            pos[:] = wrapPosition__vec2_vec2(pos, _u_resolution)
        else:
            pos[:] = rt.component_wise("clamp", pos, rt.construct(2, rt.f(1.0)), rt.binary("-", _u_resolution, rt.construct(2, rt.f(1.0)), 2, "float"), width=2)
        age = rt.binary("+", age, rt.f(0.016), 1, "float")
        newPx = rt.binary("/", rt.swizzle(pos, "x"), rt.swizzle(_u_resolution, "x"), 1, "float")
        newPy = rt.binary("/", rt.swizzle(pos, "y"), rt.swizzle(_u_resolution, "y"), 1, "float")
        g.outXYZ[:] = rt.construct(4, newPx, newPy, rt.swizzle(xyz, "z"), rt.f(1.0))
        g.outVel[:] = rt.construct(4, velocity, age, seed)
        g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
