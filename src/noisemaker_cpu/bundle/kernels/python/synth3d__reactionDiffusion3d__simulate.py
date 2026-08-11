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
    _u_feed = U.get("feed", rt.f(0.0))
    _u_kill = U.get("kill", rt.f(0.0))
    _u_rate1 = U.get("rate1", rt.f(0.0))
    _u_rate2 = U.get("rate2", rt.f(0.0))
    _u_speed = U.get("speed", rt.f(0.0))
    _u_iterations = U.get("iterations", 0)
    _u_colorMode = U.get("colorMode", 0)
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
    def laplacian3D__ivec3_int(voxel, volSize):
        voxel = rt.copy(voxel, "int")
        center = sampleState__ivec3_int(voxel, volSize)
        xp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(1), rt.i(0), rt.i(0), base="int"), 3, "int"), volSize)
        xn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.unary("-", rt.i(1)), rt.i(0), rt.i(0), base="int"), 3, "int"), volSize)
        yp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(1), rt.i(0), base="int"), 3, "int"), volSize)
        yn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.unary("-", rt.i(1)), rt.i(0), base="int"), 3, "int"), volSize)
        zp = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(0), rt.i(1), base="int"), 3, "int"), volSize)
        zn = sampleState__ivec3_int(rt.binary("+", voxel, rt.construct(3, rt.i(0), rt.i(0), rt.unary("-", rt.i(1)), base="int"), 3, "int"), volSize)
        neighborSum = rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", rt.binary("+", rt.swizzle(xp, "ra"), rt.swizzle(xn, "ra"), 2, "float"), rt.swizzle(yp, "ra"), 2, "float"), rt.swizzle(yn, "ra"), 2, "float"), rt.swizzle(zp, "ra"), 2, "float"), rt.swizzle(zn, "ra"), 2, "float")
        lap = rt.binary("-", neighborSum, rt.binary("*", rt.f(6.0), rt.swizzle(center, "ra"), 2, "float"), 2, "float")
        return lap
    def main__void():
        volSize = _u_volumeSize
        pixelCoord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        x = rt.swizzle(pixelCoord, "x")
        y = rt.binary("%", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        z = rt.binary("/", rt.swizzle(pixelCoord, "y"), volSize, 1, "int")
        voxel = rt.construct(3, x, y, z, base="int")
        if (bool((bool(rt.binary(">=", x, volSize)) or bool(rt.binary(">=", y, volSize)))) or bool(rt.binary(">=", z, volSize))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        state = sampleState__ivec3_int(voxel, volSize)
        b = rt.swizzle(state, "r")
        a = rt.swizzle(state, "a")
        bufferIsEmpty = (bool((bool((bool(rt.binary("==", rt.swizzle(state, "r"), rt.f(0.0))) and bool(rt.binary("==", rt.swizzle(state, "g"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(state, "b"), rt.f(0.0))))) and bool(rt.binary("==", rt.swizzle(state, "a"), rt.f(0.0))))
        if (bool(bufferIsEmpty) or bool(_u_resetState)):
            a = rt.f(1.0)
            b = rt.f(0.0)
            start = 0
            end = 0
            inCenterCube = False
            seedVal = rt.construct(4, 0.0)
            hasSeedInput = False
            if _u_resetState:
                start = rt.component_wise("max", rt.i(0), rt.binary("-", rt.binary("/", volSize, rt.i(2), 1, "int"), rt.i(2), 1, "int"), width=1)
                end = rt.component_wise("min", rt.binary("-", volSize, rt.i(1), 1, "int"), rt.binary("+", start, rt.i(3), 1, "int"), width=1)
                inCenterCube = (bool((bool((bool((bool((bool(rt.binary(">=", x, start)) and bool(rt.binary("<=", x, end)))) and bool(rt.binary(">=", y, start)))) and bool(rt.binary("<=", y, end)))) and bool(rt.binary(">=", z, start)))) and bool(rt.binary("<=", z, end)))
                b = (rt.f(1.0) if inCenterCube else rt.f(0.0))
            else:
                seedVal = sampleSeed__ivec3_int(voxel, volSize)
                hasSeedInput = (bool((bool(rt.binary(">", rt.swizzle(seedVal, "r"), rt.f(0.0))) or bool(rt.binary(">", rt.swizzle(seedVal, "g"), rt.f(0.0))))) or bool(rt.binary(">", rt.swizzle(seedVal, "b"), rt.f(0.0))))
                lum = rt.f(0.0)
                p = rt.construct(3, 0.0)
                if hasSeedInput:
                    lum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.299), rt.swizzle(seedVal, "r"), 1, "float"), rt.binary("*", rt.f(0.587), rt.swizzle(seedVal, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.114), rt.swizzle(seedVal, "b"), 1, "float"), 1, "float")
                    b = (rt.f(1.0) if rt.binary(">", lum, rt.f(0.5)) else rt.f(0.0))
                else:
                    p = rt.construct(3, rt.construct(1, x), rt.construct(1, y), rt.construct(1, z))
                    if rt.binary(">", hash3__vec3(p), rt.f(0.97)):
                        b = rt.f(1.0)
            g.fragColor[:] = rt.construct(4, b, b, b, a)
            return
        lap = laplacian3D__ivec3_int(voxel, volSize)
        f = rt.binary("*", _u_feed, rt.f(0.001), 1, "float")
        k = rt.binary("*", _u_kill, rt.f(0.001), 1, "float")
        r1 = rt.binary("/", rt.binary("*", _u_rate1, rt.f(0.01), 1, "float"), rt.f(6.0), 1, "float")
        r2 = rt.binary("/", rt.binary("*", _u_rate2, rt.f(0.01), 1, "float"), rt.f(6.0), 1, "float")
        iterF = rt.component_wise("max", rt.f(1.0), rt.construct(1, _u_iterations), width=1)
        s = rt.binary("/", rt.binary("*", _u_speed, rt.f(0.01), 1, "float"), iterF, 1, "float")
        newA = rt.binary("+", a, rt.binary("*", rt.binary("+", rt.binary("-", rt.binary("*", r1, rt.swizzle(lap, "y"), 1, "float"), rt.binary("*", rt.binary("*", a, b, 1, "float"), b, 1, "float"), 1, "float"), rt.binary("*", f, rt.binary("-", rt.f(1.0), a, 1, "float"), 1, "float"), 1, "float"), s, 1, "float"), 1, "float")
        newB = rt.binary("+", b, rt.binary("*", rt.binary("-", rt.binary("+", rt.binary("*", r2, rt.swizzle(lap, "x"), 1, "float"), rt.binary("*", rt.binary("*", a, b, 1, "float"), b, 1, "float"), 1, "float"), rt.binary("*", rt.binary("+", k, f, 1, "float"), b, 1, "float"), 1, "float"), s, 1, "float"), 1, "float")
        seedVal = rt.construct(4, 0.0)
        seedLum = rt.f(0.0)
        if rt.binary(">", _u_weight, rt.f(0.0)):
            seedVal = sampleSeed__ivec3_int(voxel, volSize)
            seedLum = rt.binary("+", rt.binary("+", rt.binary("*", rt.f(0.299), rt.swizzle(seedVal, "r"), 1, "float"), rt.binary("*", rt.f(0.587), rt.swizzle(seedVal, "g"), 1, "float"), 1, "float"), rt.binary("*", rt.f(0.114), rt.swizzle(seedVal, "b"), 1, "float"), 1, "float")
            newB = rt.component_wise("mix", newB, seedLum, rt.binary("*", _u_weight, rt.f(0.01), 1, "float"), width=1)
        newA = rt.component_wise("clamp", newA, rt.f(0.0), rt.f(1.0), width=1)
        newB = rt.component_wise("clamp", newB, rt.f(0.0), rt.f(1.0), width=1)
        density = newB
        outRgb = rt.construct(3, 0.0)
        if rt.binary("==", _u_colorMode, rt.i(0)):
            outRgb[:] = rt.construct(3, density)
        else:
            (outRgb.__setitem__(0, density), outRgb.__setitem__(1, newA), outRgb.__setitem__(2, rt.binary("-", rt.f(1.0), density, 1, "float")), outRgb)[-1]
        g.fragColor[:] = rt.construct(4, outRgb, newA)
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
