def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_time = U.get("time", rt.f(0.0))
    _u_seed = U.get("seed", 0)
    _u_volumeSize = U.get("volumeSize", 0)
    _u_ruleIndex = U.get("ruleIndex", 0)
    _u_neighborMode = U.get("neighborMode", 0)
    _u_speed = U.get("speed", rt.f(0.0))
    _u_density = U.get("density", rt.f(0.0))
    _u_weight = U.get("weight", rt.f(0.0))
    _u_resetState = U.get("resetState", False)
    _u_stateTex = T["stateTex"]
    _u_seedTex = T["seedTex"]
    g.fragColor = rt.construct(4, 0.0)
    def hash3__vec3(p):
        p = rt.copy(p, "float")
        p[:] = rt.binary("+", p, rt.binary("*", rt.construct(1, _u_seed), rt.f(0.1), 1, "float"), 3, "float")
        p[:] = rt.component_wise("fract", rt.binary("*", p, rt.construct(3, rt.f(0.1031), rt.f(0.103), rt.f(0.0973)), 3, "float"), width=3)
        p[:] = rt.binary("+", p, rt.dot(p, rt.binary("+", rt.swizzle(p, "yxz"), rt.f(33.33), 3, "float")), 3, "float")
        return rt.component_wise("fract", rt.binary("*", rt.binary("+", rt.swizzle(p, "x"), rt.swizzle(p, "y"), 1, "float"), rt.swizzle(p, "z"), 1, "float"), width=1)
    def atlasTexel__ivec3_int(p, volSize):
        p = rt.copy(p, "int")
        wrapped = rt.construct(3, rt.binary("%", rt.binary("+", rt.swizzle(p, "x"), volSize, 1, "int"), volSize, 1, "int"), rt.binary("%", rt.binary("+", rt.swizzle(p, "y"), volSize, 1, "int"), volSize, 1, "int"), rt.binary("%", rt.binary("+", rt.swizzle(p, "z"), volSize, 1, "int"), volSize, 1, "int"), base="int")
        return rt.construct(2, rt.swizzle(wrapped, "x"), rt.binary("+", rt.swizzle(wrapped, "y"), rt.binary("*", rt.swizzle(wrapped, "z"), volSize, 1, "int"), 1, "int"), base="int")
    def sampleState__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        return rt.texel_fetch(_u_stateTex, atlasTexel__ivec3_int(voxel, volSize), rt.i(0))
    def sampleSeed__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        return rt.texel_fetch(_u_seedTex, atlasTexel__ivec3_int(voxel, volSize), rt.i(0))
    def countMooreNeighbors__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        count = rt.i(0)
        dz = rt.unary("-", rt.i(1))
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                dz = rt.binary("+", dz, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<=", dz, rt.i(1))):
                break
            dy = rt.unary("-", rt.i(1))
            _for1_first = True
            for _for1 in range(1048576):
                if not _for1_first:
                    dy = rt.binary("+", dy, rt.i(1), 1, "int")
                _for1_first = False
                if not (rt.binary("<=", dy, rt.i(1))):
                    break
                dx = rt.unary("-", rt.i(1))
                _for2_first = True
                for _for2 in range(1048576):
                    if not _for2_first:
                        dx = rt.binary("+", dx, rt.i(1), 1, "int")
                    _for2_first = False
                    if not (rt.binary("<=", dx, rt.i(1))):
                        break
                    if (bool((bool(rt.binary("==", dx, rt.i(0))) and bool(rt.binary("==", dy, rt.i(0))))) and bool(rt.binary("==", dz, rt.i(0)))):
                        continue
                    neighbor = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, dx, dy, dz, base="int"), 3, "int"), volSize)
                    if rt.binary(">", rt.swizzle(neighbor, "r"), rt.f(0.5)):
                        count = rt.binary("+", count, rt.i(1), 1, "int")
        return count
    def countVonNeumannNeighbors__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        count = rt.i(0)
        xp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(1), rt.i(0), rt.i(0), base="int"), 3, "int"), volSize)
        xn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.unary("-", rt.i(1)), rt.i(0), rt.i(0), base="int"), 3, "int"), volSize)
        yp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(1), rt.i(0), base="int"), 3, "int"), volSize)
        yn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.unary("-", rt.i(1)), rt.i(0), base="int"), 3, "int"), volSize)
        zp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(0), rt.i(1), base="int"), 3, "int"), volSize)
        zn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(0), rt.unary("-", rt.i(1)), base="int"), 3, "int"), volSize)
        if rt.binary(">", rt.swizzle(xp, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        if rt.binary(">", rt.swizzle(xn, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        if rt.binary(">", rt.swizzle(yp, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        if rt.binary(">", rt.swizzle(yn, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        if rt.binary(">", rt.swizzle(zp, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        if rt.binary(">", rt.swizzle(zn, "r"), rt.f(0.5)):
            count = rt.binary("+", count, rt.i(1), 1, "int")
        return count
    def shouldBeBorn__int_int(n, rule):
        if rt.binary("==", rule, rt.i(0)):
            return rt.binary("==", n, rt.i(4))
        if rt.binary("==", rule, rt.i(1)):
            return (bool(rt.binary(">=", n, rt.i(6))) and bool(rt.binary("<=", n, rt.i(8))))
        if rt.binary("==", rule, rt.i(2)):
            return rt.binary(">=", n, rt.i(9))
        if rt.binary("==", rule, rt.i(3)):
            return (bool((bool((bool(rt.binary("==", n, rt.i(4))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(8))))) or bool(rt.binary("==", n, rt.i(9))))
        if rt.binary("==", rule, rt.i(4)):
            return rt.binary("==", n, rt.i(3))
        if rt.binary("==", rule, rt.i(5)):
            return rt.binary(">=", n, rt.i(13))
        if rt.binary("==", rule, rt.i(6)):
            return (bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(3))))
        if rt.binary("==", rule, rt.i(7)):
            return (bool((bool(rt.binary(">=", n, rt.i(5))) and bool(rt.binary("<=", n, rt.i(7))))) or bool(rt.binary("==", n, rt.i(12))))
        if rt.binary("==", rule, rt.i(8)):
            return (bool(rt.binary(">=", n, rt.i(4))) and bool(rt.binary("<=", n, rt.i(7))))
        if rt.binary("==", rule, rt.i(9)):
            return rt.binary("==", n, rt.i(4))
        if rt.binary("==", rule, rt.i(10)):
            return (bool(rt.binary(">=", n, rt.i(5))) and bool(rt.binary("<=", n, rt.i(8))))
        return False
    def shouldSurvive__int_int(n, rule):
        if rt.binary("==", rule, rt.i(0)):
            return rt.binary("==", n, rt.i(4))
        if rt.binary("==", rule, rt.i(1)):
            return (bool(rt.binary(">=", n, rt.i(6))) and bool(rt.binary("<=", n, rt.i(8))))
        if rt.binary("==", rule, rt.i(2)):
            return (bool((bool((bool((bool(rt.binary(">=", n, rt.i(5))) and bool(rt.binary("<=", n, rt.i(7))))) or bool(rt.binary("==", n, rt.i(12))))) or bool(rt.binary("==", n, rt.i(13))))) or bool(rt.binary("==", n, rt.i(15))))
        if rt.binary("==", rule, rt.i(3)):
            return (bool((bool(rt.binary(">=", n, rt.i(3))) and bool(rt.binary("<=", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(9))))
        if rt.binary("==", rule, rt.i(4)):
            return (bool(rt.binary("==", n, rt.i(2))) or bool(rt.binary("==", n, rt.i(3))))
        if rt.binary("==", rule, rt.i(5)):
            return rt.binary(">=", n, rt.i(13))
        if rt.binary("==", rule, rt.i(6)):
            return (bool((bool(rt.binary("==", n, rt.i(1))) or bool(rt.binary("==", n, rt.i(2))))) or bool(rt.binary("==", n, rt.i(4))))
        if rt.binary("==", rule, rt.i(7)):
            return (bool(rt.binary(">=", n, rt.i(5))) and bool(rt.binary("<=", n, rt.i(8))))
        if rt.binary("==", rule, rt.i(8)):
            return (bool(rt.binary(">=", n, rt.i(6))) and bool(rt.binary("<=", n, rt.i(8))))
        if rt.binary("==", rule, rt.i(9)):
            return (bool(rt.binary("==", n, rt.i(3))) or bool(rt.binary("==", n, rt.i(4))))
        if rt.binary("==", rule, rt.i(10)):
            return (bool((bool(rt.binary("==", n, rt.i(5))) or bool(rt.binary("==", n, rt.i(6))))) or bool(rt.binary("==", n, rt.i(9))))
        return False
    def main__void():
        volSize = _u_volumeSize
        volSizeF = rt.construct(1, volSize)
        pixelCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        x = rt.swizzle(pixelCoord, "x")
        y = rt.binary("%", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        z = rt.binary("/", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        voxel = rt.construct(3, x, y, z, base="int")
        if (bool((bool(rt.binary(">=", x, volSize)) or bool(rt.binary(">=", y, volSize)))) or bool(rt.binary(">=", z, volSize))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        state = sampleState__ivec3_int(voxel, volSize)
        alive = rt.swizzle(state, "r")
        age = rt.swizzle(state, "g")
        bufferIsEmpty = (bool((bool((bool(rt.binary("==", rt.swizzle(state, "r"), rt.f(0.0))) and bool(rt.binary("==", rt.swizzle(state, "g"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(state, "b"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(state, "a"), rt.f(0.0))))
        seedVal = rt.construct(4, 0.0)
        hasSeedInput = False
        if (bool(bufferIsEmpty) or bool(_u_resetState)):
            seedVal = sampleSeed__ivec3_int(voxel, volSize)
            hasSeedInput = (bool((bool(rt.binary(">", rt.swizzle(seedVal, "r"), rt.f(0.0))) or bool(rt.binary(">", rt.swizzle(seedVal, "g"), rt.f(0.0))))) or bool(rt.binary(">", rt.swizzle(seedVal, "b"), rt.f(0.0))))
            lum = rt.f(0.0)
            p = rt.construct(3, 0.0)
            h = rt.f(0.0)
            threshold = rt.f(0.0)
            center = rt.construct(3, 0.0)
            dist = rt.f(0.0)
            radius = rt.f(0.0)
            if hasSeedInput:
                lum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.299), rt.swizzle(seedVal, "r"), 1, "float"), rt.binary("*", rt.f(0.587), rt.swizzle(seedVal, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.114), rt.swizzle(seedVal, "b"), 1, "float"), 1, "float")
                alive = (rt.f(1.0) if rt.binary(">", lum, rt.f(0.5)) else rt.f(0.0))
                age = rt.f(0.0)
            else:
                p = rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z))
                h = hash3__vec3(p)
                threshold = rt.binary("*", _u_density, rt.f(0.01), 1, "float")
                center = rt.construct(3, rt.binary("*", volSizeF, rt.f(0.5), 1, "float"))
                dist = rt.length(rt.binary("-", p, center, 3, "float"))
                radius = rt.binary("*", volSizeF, rt.f(0.15), 1, "float")
                if (bool(rt.binary("<", h, threshold)) or bool(rt.binary("<", dist, radius))):
                    alive = rt.f(1.0)
                    age = rt.f(0.0)
                else:
                    alive = rt.f(0.0)
                    age = rt.f(0.0)
            g.fragColor[:] = rt.construct(4, alive, alive, alive, rt.f(1.0))
            return
        neighbors = 0
        if rt.binary("==", _u_neighborMode, rt.i(0)):
            neighbors = countMooreNeighbors__ivec3_int(voxel, volSize)
        else:
            neighbors = countVonNeumannNeighbors__ivec3_int(voxel, volSize)
        newAlive = rt.f(0.0)
        newAge = age
        if rt.binary(">", alive, rt.f(0.5)):
            if shouldSurvive__int_int(neighbors, _u_ruleIndex):
                newAlive = rt.f(1.0)
                newAge = rt.component_wise("min", rt.binary("+", age, rt.f(0.01), 1, "float"), rt.f(1.0), width=1)
            else:
                newAlive = rt.f(0.0)
                newAge = rt.f(0.0)
        else:
            if shouldBeBorn__int_int(neighbors, _u_ruleIndex):
                newAlive = rt.f(1.0)
                newAge = rt.f(0.0)
            else:
                newAlive = rt.f(0.0)
                newAge = rt.f(0.0)
        animSpeed = rt.binary("*", _u_speed, rt.f(0.01), 1, "float")
        finalAlive = rt.component_wise("mix", alive, newAlive, animSpeed, width=1)
        finalAge = rt.component_wise("mix", age, newAge, animSpeed, width=1)
        seedLum = rt.f(0.0)
        if rt.binary(">", _u_weight, rt.f(0.0)):
            seedVal = sampleSeed__ivec3_int(voxel, volSize)
            seedLum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.299), rt.swizzle(seedVal, "r"), 1, "float"), rt.binary("*", rt.f(0.587), rt.swizzle(seedVal, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.114), rt.swizzle(seedVal, "b"), 1, "float"), 1, "float")
            finalAlive = rt.component_wise("mix", finalAlive, seedLum, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
        g.fragColor[:] = rt.construct(4, finalAlive, finalAlive, finalAlive, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
