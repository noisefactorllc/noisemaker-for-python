def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_typeCount = U.get("typeCount", 0)
    _u_matrixSeed = U.get("matrixSeed", rt.f(0.0))
    _u_symmetricForces = U.get("symmetricForces", False)
    g.fragColor = rt.construct(4, 0.0)
    def hash_uint__uint(seed):
        state = rt.binary("+", rt.binary("*", seed, rt.i(747796405), 1, "uint"), rt.i(2891336453), 1, "uint")
        word = rt.binary("*", rt.binary("^", rt.binary(">>", state, rt.binary("+", rt.binary(">>", state, rt.i(28), 1, "uint"), rt.i(4), 1, "uint"), 1, "uint"), state, 1, "uint"), rt.i(277803737), 1, "uint")
        return rt.binary("^", rt.binary(">>", word, rt.i(22), 1, "uint"), word, 1, "uint")
    def hash__uint(seed):
        return rt.binary("/", rt.construct(1, rt.hash_uint(seed)), rt.f(4294967295.0), 1, "float")
    def main__void():
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        typeA = rt.swizzle(coord, "x")
        typeB = rt.swizzle(coord, "y")
        if (bool(rt.binary(">=", typeA, _u_typeCount)) or bool(rt.binary(">=", typeB, _u_typeCount))):
            g.fragColor[:] = rt.construct(4, rt.f(0.0))
            return
        seed = rt.binary("+", rt.construct(1, rt.binary("*", _u_matrixSeed, rt.f(1000.0), 1, "float"), base="uint"), rt.construct(1, rt.binary("+", rt.binary("*", typeA, rt.i(31), 1, "int"), rt.binary("*", typeB, rt.i(17), 1, "int"), 1, "int"), base="uint"), 1, "uint")
        if (bool(_u_symmetricForces) and bool(rt.binary("<", typeB, typeA))):
            seed = rt.binary("+", rt.construct(1, rt.binary("*", _u_matrixSeed, rt.f(1000.0), 1, "float"), base="uint"), rt.construct(1, rt.binary("+", rt.binary("*", typeB, rt.i(31), 1, "int"), rt.binary("*", typeA, rt.i(17), 1, "int"), 1, "int"), base="uint"), 1, "uint")
        strength = rt.f(0.0)
        if rt.binary("==", typeA, typeB):
            strength = rt.binary("-", rt.unary("-", rt.f(0.3)), rt.binary("*", hash__uint(seed), rt.f(0.4), 1, "float"), 1, "float")
        else:
            strength = rt.binary("-", rt.binary("*", hash__uint(seed), rt.f(2.0), 1, "float"), rt.f(1.0), 1, "float")
        prefDist = rt.binary("+", rt.f(0.3), rt.binary("*", hash__uint(rt.binary("+", seed, rt.i(1), 1, "uint")), rt.f(0.5), 1, "float"), 1, "float")
        curveShape = hash__uint(rt.binary("+", seed, rt.i(2), 1, "uint"))
        g.fragColor[:] = rt.construct(4, strength, prefDist, curveShape, rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
