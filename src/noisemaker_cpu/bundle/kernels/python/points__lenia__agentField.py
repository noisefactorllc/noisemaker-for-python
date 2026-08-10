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
    _u_fieldTex = T["fieldTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_muG = U.get("muG", rt.f(0.0))
    _u_sigmaG = U.get("sigmaG", rt.f(0.0))
    _u_repulsion = U.get("repulsion", rt.f(0.0))
    _u_dt = U.get("dt", rt.f(0.0))
    g.outXYZ = rt.construct(4, 0.0)
    g.outVel = rt.construct(4, 0.0)
    g.outRGBA = rt.construct(4, 0.0)
    g.EPSILON = rt.f(0.0001)
    def growth__float_float_float(u, mu, sigma):
        x = rt.binary("/", rt.binary("-", u, mu, 1, "float"), sigma, 1, "float")
        return rt.component_wise("exp", rt.binary("*", rt.unary("-", x), x, 1, "float"), width=1)
    def growthDerivative__float_float_float(u, mu, sigma):
        G = growth__float_float_float(u, mu, sigma)
        return rt.binary("/", rt.binary("*", G, rt.binary("*", rt.unary("-", rt.f(2.0)), rt.binary("-", u, mu, 1, "float"), 1, "float"), 1, "float"), rt.binary("*", sigma, sigma, 1, "float"), 1, "float")
    def main__void():
        stateSize = rt.texture_size(_u_xyzTex)
        coord = rt.construct(2, rt.swizzle(ctx.frag_coord, "xy"), base="int")
        xyz = rt.texel_fetch(_u_xyzTex, coord, rt.i(0))
        vel = rt.texel_fetch(_u_velTex, coord, rt.i(0))
        rgba = rt.texel_fetch(_u_rgbaTex, coord, rt.i(0))
        alive = rt.swizzle(xyz, "w")
        if rt.binary("<", alive, rt.f(0.5)):
            g.outXYZ[:] = xyz
            g.outVel[:] = vel
            g.outRGBA[:] = rgba
            return
        uv = rt.swizzle(xyz, "xy")
        _U = rt.swizzle(rt.texture(_u_fieldTex, uv), "r")
        fieldSize = rt.construct(2, rt.texture_size(_u_fieldTex))
        texelSize = rt.binary("/", rt.f(1.0), fieldSize, 2, "float")
        Ux_plus = rt.swizzle(rt.texture(_u_fieldTex, rt.component_wise("fract", rt.binary("+", uv, rt.construct(2, rt.swizzle(texelSize, "x"), rt.f(0.0)), 2, "float"), width=2)), "r")
        Ux_minus = rt.swizzle(rt.texture(_u_fieldTex, rt.component_wise("fract", rt.binary("-", uv, rt.construct(2, rt.swizzle(texelSize, "x"), rt.f(0.0)), 2, "float"), width=2)), "r")
        Uy_plus = rt.swizzle(rt.texture(_u_fieldTex, rt.component_wise("fract", rt.binary("+", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texelSize, "y")), 2, "float"), width=2)), "r")
        Uy_minus = rt.swizzle(rt.texture(_u_fieldTex, rt.component_wise("fract", rt.binary("-", uv, rt.construct(2, rt.f(0.0), rt.swizzle(texelSize, "y")), 2, "float"), width=2)), "r")
        gradU = rt.construct(2, rt.binary("/", rt.binary("-", Ux_plus, Ux_minus, 1, "float"), rt.binary("*", rt.f(2.0), rt.swizzle(texelSize, "x"), 1, "float"), 1, "float"), rt.binary("/", rt.binary("-", Uy_plus, Uy_minus, 1, "float"), rt.binary("*", rt.f(2.0), rt.swizzle(texelSize, "y"), 1, "float"), 1, "float"))
        worldScale = rt.binary("*", rt.component_wise("min", rt.swizzle(_u_resolution, "x"), rt.swizzle(_u_resolution, "y"), width=1), rt.f(0.05), 1, "float")
        gradU[:] = rt.binary("/", gradU, worldScale, 2, "float")
        dGdU = growthDerivative__float_float_float(_U, _u_muG, _u_sigmaG)
        gradG = rt.binary("*", dGdU, gradU, 2, "float")
        gradR = rt.binary("*", _u_repulsion, gradU, 2, "float")
        force = rt.binary("-", gradG, gradR, 2, "float")
        forceMag = rt.length(force)
        if rt.binary(">", forceMag, rt.f(10.0)):
            force[:] = rt.binary("*", rt.binary("/", force, forceMag, 2, "float"), rt.f(10.0), 2, "float")
        newPos = rt.binary("+", uv, rt.binary("*", rt.binary("*", force, _u_dt, 2, "float"), rt.f(0.01), 2, "float"), 2, "float")
        newPos[:] = rt.component_wise("fract", rt.binary("+", newPos, rt.f(1.0), 2, "float"), width=2)
        velocity = rt.binary("*", rt.binary("*", force, _u_dt, 2, "float"), rt.f(0.01), 2, "float")
        age = rt.binary("+", rt.swizzle(vel, "z"), rt.f(0.016), 1, "float")
        g.outXYZ[:] = rt.construct(4, newPos, rt.swizzle(xyz, "z"), rt.f(1.0))
        g.outVel[:] = rt.construct(4, velocity, age, rt.swizzle(vel, "w"))
        g.outRGBA[:] = rgba
    main__void()
    _c = g.outXYZ
    out[0][0] = rt.f32(_c[0]); out[0][1] = rt.f32(_c[1]); out[0][2] = rt.f32(_c[2]); out[0][3] = rt.f32(_c[3])
    _c = g.outVel
    out[1][0] = rt.f32(_c[0]); out[1][1] = rt.f32(_c[1]); out[1][2] = rt.f32(_c[2]); out[1][3] = rt.f32(_c[3])
    _c = g.outRGBA
    out[2][0] = rt.f32(_c[0]); out[2][1] = rt.f32(_c[1]); out[2][2] = rt.f32(_c[2]); out[2][3] = rt.f32(_c[3])
run_pixel.output_names = ('outXYZ', 'outVel', 'outRGBA')
