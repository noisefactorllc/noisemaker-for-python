def run_pixel(ctx, out):
    rt = ctx.rt
    U = ctx.uniforms
    T = ctx.textures
    class _G:
        pass
    g = _G()
    _u_densityTex = T["densityTex"]
    _u_resolution = U.get("resolution", rt.construct(2, 0.0))
    _u_muK = U.get("muK", rt.f(0.0))
    _u_sigmaK = U.get("sigmaK", rt.f(0.0))
    _u_searchRadius = U.get("searchRadius", rt.f(0.0))
    g.fragColor = rt.construct(4, 0.0)
    g.EPSILON = rt.f(0.0001)
    g.PI = rt.f(3.14159265359)
    def kernel__float_float_float(r, mu, sigma):
        x = rt.binary("/", rt.binary("-", r, mu, 1, "float"), sigma, 1, "float")
        return rt.component_wise("exp", rt.binary("*", rt.unary("-", x), x, 1, "float"), width=1)
    def main__void():
        densitySize = rt.construct(2, rt.texture_size(_u_densityTex))
        uv = rt.binary("/", rt.swizzle(ctx.frag_coord, "xy"), densitySize, 2, "float")
        texelSize = rt.binary("/", rt.f(1.0), densitySize, 2, "float")
        wK = rt.f(0.0)
        numSamples = rt.i(64)
        dr = rt.binary("/", _u_searchRadius, rt.construct(1, numSamples), 1, "float")
        i = rt.i(0)
        _for0_first = True
        for _for0 in range(1048576):
            if not _for0_first:
                i = rt.binary("+", i, rt.i(1), 1, "int")
            _for0_first = False
            if not (rt.binary("<", i, numSamples)):
                break
            r = rt.binary("*", rt.binary("+", rt.construct(1, i), rt.f(0.5), 1, "float"), dr, 1, "float")
            wK = rt.binary("+", wK, rt.binary("*", rt.binary("*", kernel__float_float_float(r, _u_muK, _u_sigmaK), r, 1, "float"), dr, 1, "float"), 1, "float")
        wK = rt.binary("/", rt.f(1.0), rt.component_wise("max", rt.binary("*", rt.binary("*", wK, rt.f(2.0), 1, "float"), g.PI, 1, "float"), g.EPSILON, width=1), 1, "float")
        _U = rt.f(0.0)
        iRadius = rt.construct(1, rt.component_wise("ceil", _u_searchRadius, width=1), base="int")
        dy = rt.unary("-", iRadius)
        _for1_first = True
        for _for1 in range(1048576):
            if not _for1_first:
                dy = rt.binary("+", dy, rt.i(1), 1, "int")
            _for1_first = False
            if not (rt.binary("<=", dy, iRadius)):
                break
            dx = rt.unary("-", iRadius)
            _for2_first = True
            for _for2 in range(1048576):
                if not _for2_first:
                    dx = rt.binary("+", dx, rt.i(1), 1, "int")
                _for2_first = False
                if not (rt.binary("<=", dx, iRadius)):
                    break
                r = rt.length(rt.construct(2, rt.construct(1, dx), rt.construct(1, dy)))
                if rt.binary(">", r, _u_searchRadius):
                    continue
                sampleUV = rt.component_wise("fract", rt.binary("+", uv, rt.binary("*", rt.construct(2, rt.construct(1, dx), rt.construct(1, dy)), texelSize, 2, "float"), 2, "float"), width=2)
                density = rt.swizzle(rt.texture(_u_densityTex, sampleUV), "r")
                kVal = rt.binary("*", kernel__float_float_float(r, _u_muK, _u_sigmaK), wK, 1, "float")
                _U = rt.binary("+", _U, rt.binary("*", density, kVal, 1, "float"), 1, "float")
        g.fragColor[:] = rt.construct(4, _U, rt.f(0.0), rt.f(0.0), rt.f(1.0))
    main__void()
    _c = g.fragColor
    out[0] = rt.f32(_c[0]); out[1] = rt.f32(_c[1]); out[2] = rt.f32(_c[2]); out[3] = rt.f32(_c[3])
run_pixel.output_names = ('fragColor',)
